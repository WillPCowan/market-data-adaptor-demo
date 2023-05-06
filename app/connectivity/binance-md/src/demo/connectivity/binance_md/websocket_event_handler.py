
import decimal
from enum import Enum
from typing import Any, Dict
import logging

import demo.connectivity.binance_md.order_book_sequencer as order_book_sequencer

logger = logging.getLogger(__name__)

class WebSocketEventHandler:

    def __init__(self, order_book_sequencer: order_book_sequencer.BinanceOrderBookSequencer):
        self.order_book_sequencer = order_book_sequencer

    def handle_event(self, event: Dict[str, Any]):

        event_type = event.get("e", None)
        if event_type == "depthUpdate":
            self._handle_order_book_update(event)
        
        elif "result" in event and event["result"] == None:
            logger.info("Subscription request acknowledged")
        
        else:
            raise ValueError(f"Unknown event type: {event}")
        

    def _handle_order_book_update(self, update: Dict[str, Any]):
        self.order_book_sequencer.sequence_update(update)
        
