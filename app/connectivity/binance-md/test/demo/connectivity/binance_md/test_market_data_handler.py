import decimal
from typing import List
from unittest.mock import Mock

import pytest
from demo.connectivity.common.order_book_l2 import Order, OrderBookL2

from demo.connectivity.binance_md.market_data_handler import MarketDataHandler


class SnapshotTestCase:
    def __init__(self, snapshot, expected_bids, expected_asks):
        self.snapshot = snapshot
        self.expected_bids = expected_bids
        self.expected_asks = expected_asks

class UpdateTestCase:
    def __init__(self, update, expected_bids, expected_asks):
        self.update = update
        self.expected_bids = expected_bids
        self.expected_asks = expected_asks


@pytest.fixture
def order_book():
    return OrderBookL2()


@pytest.fixture
def market_data_handler(order_book):
    return MarketDataHandler("BNBBTC", order_book)


def _make_order_book_snapshot_test_cases() -> List[SnapshotTestCase]:
    return [
        SnapshotTestCase(
            snapshot={
                "lastUpdateId": 2731179239,
                "bids": [
                    ["0.01379900", "3.43200000"],
                    ["0.01379800", "3.24300000"],
                ],
                "asks": [
                    ["0.01380000", "5.91700000"],
                    ["0.01380100", "6.01400000"],
                ],
            },
            expected_bids=[
                Order(decimal.Decimal("0.01379900"), decimal.Decimal("3.43200000")),
                Order(decimal.Decimal("0.01379800"), decimal.Decimal("3.24300000")),
            ],
            expected_asks=[
                Order(decimal.Decimal("0.01380000"), decimal.Decimal("5.91700000")),
                Order(decimal.Decimal("0.01380100"), decimal.Decimal("6.01400000")),
            ],
        )
    ]

def _make_order_book_update_test_cases() -> List[UpdateTestCase]:
    return [
        UpdateTestCase(
            update={
                "e": "depthUpdate",
                "E": 123456789,
                "s": "BNBBTC",
                "U": 157,
                "u": 160,
                "b": [
                    ["0.01379900", "10"]
                ],
                "a": [
                    ["0.01380000", "100"]
                ],
            },
            expected_bids=[
                Order(decimal.Decimal("0.01379900"), decimal.Decimal("10")),
                Order(decimal.Decimal("0.01379800"), decimal.Decimal("3.24300000")),
            ],
            expected_asks=[
                Order(decimal.Decimal("0.01380000"), decimal.Decimal("100")),
                Order(decimal.Decimal("0.01380100"), decimal.Decimal("6.01400000")),
            ],
        )
    ]


@pytest.mark.parametrize("test_case", _make_order_book_snapshot_test_cases())
def test_handle_snapshot(test_case, market_data_handler, order_book):
    market_data_handler.handle_snapshot(test_case.snapshot)

    assert order_book._bids == test_case.expected_bids
    assert order_book._asks == test_case.expected_asks


@pytest.mark.parametrize("test_case", _make_order_book_update_test_cases())
def test_handle_update(test_case, market_data_handler, order_book):
    snapshot = {
        "lastUpdateId": 2731179239,
        "bids": [
            ["0.01379900", "3.43200000"],
            ["0.01379800", "3.24300000"],
        ],
        "asks": [
            ["0.01380000", "5.91700000"],
            ["0.01380100", "6.01400000"],
        ],
    }

    market_data_handler.handle_snapshot(snapshot)

    market_data_handler.handle_update(test_case.update)

    assert order_book._bids == test_case.expected_bids
    assert order_book._asks == test_case.expected_asks