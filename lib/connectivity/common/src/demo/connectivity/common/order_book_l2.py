
import asyncio
from dataclasses import dataclass
import decimal
import logging
from typing import List

logger = logging.getLogger(__name__)

@dataclass
class OrderBookSymbol:
    base: str
    quote: str
    name: str

@dataclass
class Order:
    # trader_id: str
    price: decimal.Decimal
    size: decimal.Decimal

@dataclass
class TopOfBookPair:
    bid: Order
    ask: Order

# TODO: smarter book implementation
class OrderBookL2:

    def __init__(self):
        self._bids: List[Order] = []
        self._asks: List[Order] = []

    def add_bid(self, price: decimal.Decimal, size: decimal.Decimal):
        for i in range(len(self._bids)):
            if self._bids[i].price == price:
                self._bids[i].size = size
                return
        self._bids.append(Order(price, size))
        self._bids.sort(key=lambda x: x.price, reverse=True)

    def add_ask(self, price: decimal.Decimal, size: decimal.Decimal):
        for i in range(len(self._asks)):
            if self._asks[i].price == price:
                self._asks[i].size = size
                return
        self._asks.append(Order(price, size))
        self._asks.sort(key=lambda x: x.price)

    def remove_bid(self, price: decimal.Decimal):
        for i in range(len(self._bids)):
            if self._bids[i].price == price:
                # print(f"removing bid index={i} price={price}")
                del self._bids[i]
                break

    def remove_ask(self, price: decimal.Decimal):
        for i in range(len(self._asks)):
            if self._asks[i].price == price:
                del self._asks[i]
                break

    def clear(self):
        self._bids = []
        self._asks = []

    def get_top_pair(self) -> TopOfBookPair:
        top_bid = self._bids[0] if self._bids else None
        top_ask = self._asks[0] if self._asks else None
        return TopOfBookPair(top_bid, top_ask)

    async def print_regularly(self, period: int):
        while True:
            top_pair = self.get_top_pair()
            bid_price = top_pair.bid.price if top_pair.bid else None
            bid_size = top_pair.bid.size if top_pair.bid else None
            ask_price = top_pair.ask.price if top_pair.ask else None
            ask_size = top_pair.ask.size if top_pair.ask else None
            logger.info(f"Top bid (price={bid_price} size={bid_size}), Top ask (price={ask_price}, size={ask_size})")
            await asyncio.sleep(period)