import asyncio
import signal
import sys
from types import FrameType
from typing import Optional, Union
import yaml
import httpx
import logging

import demo.connectivity.common.json as json
import demo.connectivity.common.order_book_l2 as order_book_l2
import demo.connectivity.common.websocket_feed as websocket_feed

import demo.connectivity.binance_md.utils as utils
import demo.connectivity.binance_md.response as response
import demo.connectivity.binance_md.config as config
import demo.connectivity.binance_md.order_book_sequencer as order_book_sequencer


logger = logging.getLogger(__name__)

async def main_async():
    
    with open("config.yaml", 'r') as file:
        try:
            config_data = yaml.safe_load(file)
            app_config = config.BinanceMdConfig(config_data)
        except yaml.YAMLError as e:
            logger.error(f"Error parsing config file: {e}")
            raise

    http = httpx.AsyncClient()

    order_book = order_book_l2.OrderBookL2()
    order_book_print_interval = 2

    # TODO: improve design by having ResponseHandler > {Sequencer, ...} > BookDataMapper
    # so that filtering and asimilation of events occurs in ResponseHandler, 

    # TODO: implement hibernation mode for when binance servers irresponsive

    response_handler = response.ResponseHandler(
        symbol=app_config.symbol,
        order_book=order_book,
    )

    ob_sequencer = order_book_sequencer.BinanceOrderBookSequencer(
        handle_snapshot=response_handler.handle_order_book_snapshot,
        handle_update=response_handler.handle_order_book_update,
    )

    async with websocket_feed.WebSocketFeed(uri=app_config.ws_uri) as wsf:

        async def stream_init_func():
            logger.info("Sending order book subscription request")
            await wsf.send_message(utils.make_order_book_subscription_payload(app_config.symbol))

        async def on_stream_start():
            # TODO: use more robust method to wait for streaming to start (e.g. asyncio event)
            # Wait for connection to establish before requesting snapshot
            await asyncio.sleep(2) 
            snapshot_res = await http.get(app_config.http_uri + '/depth', params={"symbol": app_config.symbol, "limit": app_config.depth})
            snapshot = json.loads(snapshot_res.text) # NOTE: prefer custom parsing to in-built .json() method (avoid floats)
            ob_sequencer.sequence_snapshot_and_queued_updates(snapshot)

        try:
            group = asyncio.gather(
                wsf.stream(
                    handle_event_async=ob_sequencer.sequence_update,
                    stream_init_func_async=stream_init_func,
                ),
                on_stream_start(),
                order_book.print_regularly(period=order_book_print_interval),
            )
            await group
        except Exception as e:
            logger.error(f"Error streaming market data: {e}")
            group.cancel()

    logger.info("Finished.")


def main():
    loop = asyncio.get_event_loop()
    main_task = loop.create_task(main_async())

    logging.basicConfig(
        level=logging.INFO,
        format='[%(asctime)s][%(levelname)s] %(message)s',
        handlers=[logging.StreamHandler(sys.stdout)]
    )

    def handle_shutdown_signals(signum: Union[int, signal.Signals], frame: Optional[Union[int, FrameType]]) -> None:
        logger.info("Received shutdown signal. Triggering application shutdown.")
        main_task.cancel()
    
    for sig in [signal.SIGINT, signal.SIGTERM]:
        signal.signal(sig, handle_shutdown_signals)
    
    try:
        loop.run_until_complete(main_task)
    except asyncio.exceptions.CancelledError:
        if not main_task.cancelled():
            logger.info("Application shutdown complete.")


if __name__ == "__main__":
    main()