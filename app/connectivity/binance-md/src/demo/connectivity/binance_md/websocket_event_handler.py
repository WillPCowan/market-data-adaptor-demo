
import decimal
from enum import Enum
from typing import Any, Dict

import demo.connectivity.common.order_book_l2 as order_book_l2

class Side(Enum):
    BID = 0
    ASK = 1

ZERO_DECIMAL = decimal.Decimal(0)

class WebSocketEventHandler:

    def __init__(self, symbol: str, order_book: order_book_l2.OrderBookL2):
        self.symbol = symbol
        self.order_book = order_book

    # TODO: error handling
    def handle_order_book_snapshot(self, snapshot: Dict[str, Any]):

        # Clear book
        self.order_book.clear()
        
        # Add orders
        for bid in snapshot["bids"]:
            price, size = decimal.Decimal(bid[0]), decimal.Decimal(bid[1])
            self.order_book.add_bid(
                price=price,
                size=size,
            )
        for ask in snapshot["asks"]:
            price, size = decimal.Decimal(ask[0]), decimal.Decimal(ask[1])
            self.order_book.add_ask(
                price=price,
                size=size,
            )

    # TODO: error handling
    def handle_order_book_update(self, update: Dict[str, Any]):

        for bid in update["b"]:
            price, size = decimal.Decimal(bid[0]), decimal.Decimal(bid[1])
            if size == ZERO_DECIMAL:
                self.order_book.remove_bid(price=price)
            else:
                self.order_book.add_bid(
                    price=price,
                    size=size,
                )
        for ask in update["a"]:
            price, size = decimal.Decimal(ask[0]), decimal.Decimal(ask[1])
            if size == ZERO_DECIMAL:
                self.order_book.remove_ask(price=price)
            else:
                self.order_book.add_ask(
                    price=price,
                    size=size,
                )
        
