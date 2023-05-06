from __future__ import annotations
import json
import traceback
from typing import Any, Callable, Optional, Tuple, Type
import logging
import asyncio
import demo.connectivity.common.exceptions as exceptions
import websockets.exceptions

logger = logging.getLogger(__name__)

WEBSOCKET_TRANSIENT_ERRORS: Tuple[Type[Exception]] = (
    TimeoutError,
    asyncio.exceptions.TimeoutError,
    websockets.exceptions.ConnectionClosed,
    websockets.exceptions.ConnectionClosedOK,
    websockets.exceptions.InvalidStatusCode,
    exceptions.OutOfSequenceError,
)

class WebSocketFeed:

    def __init__(self, uri: str) -> None:
        self._uri = uri
        self._socket = None

    async def __aenter__(self) -> WebSocketFeed:
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc, tb) -> None:
        await self.close()

    async def connect(self) -> None:
        logger.info(f"Connecting to websocket server at {self._uri}")
        # TODO: retry functionality to go in decorator
        while True:
            try:
                self._socket = await websockets.connect(self._uri)
                logger.info(f"Connected to websocket server at {self._uri}")
                return
            except WEBSOCKET_TRANSIENT_ERRORS as e:
                logger.info(
                    f"Failed to connect to websocket. This is not fatal, so connection will be retried. Error: {e}"
                )
                continue
            except Exception as e:
                logger.error(
                    f"Failed to connect to websocket. This is fatal, so connection will not be retried. Error: {e}"
                )
                break
        
    async def _reconnect(self) -> None:
        try:
            if self._socket is not None:
                await self._socket.close()
        except Exception as e:
            logger.info(
                "Failed to closing existing websocket. This is not fatal, so connection will be retried. Error: {}".format(e)
            )
        self._socket = await websockets.connect(self._uri)

    async def close(self) -> None:
        if self._socket is not None:
            await self._socket.close()
        self._socket = None

    async def send_message(self, message: str) -> None:
        await self._socket.send(message)

    async def stream(self, handle_event_async: Callable[[str], None], stream_init_func_async: Optional[Callable[[str], None]] = None):
        # TODO: retry functionality to go in decorator
        logger.info(f"Starting websocket stream for {self._uri}")
        while True:
            try:
                if stream_init_func_async is not None:
                    await stream_init_func_async()

                logger.info("Starting websocket stream")
                while True:
                    message = await self._socket.recv()
                    await handle_event_async(self.transform(message))
            except WEBSOCKET_TRANSIENT_ERRORS as e:
                logger.info(
                    f"Websocket connection failed. This is not fatal, so connection will be retried. Error: {e} {traceback.print_exc()}"
                )
                await self._reconnect()
                continue
            except Exception as e:
                raise e

    def transform(self, data: Any) -> Any:
        # WebSocketFeed can be inherited and 'transform' can be overridden for custom data transformations
        # # TODO: make this return 'data' only, and each exchange adaptor should have its own feed and override this method
        return json.loads(data)