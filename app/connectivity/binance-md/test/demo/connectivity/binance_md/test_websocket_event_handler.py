import pytest
from unittest.mock import Mock
from demo.connectivity.binance_md import order_book_sequencer
from demo.connectivity.binance_md.websocket_event_handler import WebSocketEventHandler

@pytest.fixture
def mock_order_book_sequencer():
    return Mock(spec=order_book_sequencer.BinanceOrderBookSequencer)

@pytest.fixture
def ws_event_handler(mock_order_book_sequencer):
    return WebSocketEventHandler(mock_order_book_sequencer)

def test_handle_event_subscription_acknowledged(ws_event_handler):
    event = {"result": None}
    ws_event_handler.handle_event(event)
    ws_event_handler.order_book_sequencer.sequence_update.assert_not_called()

def test_handle_event_order_book_update(ws_event_handler, mock_order_book_sequencer):
    event = {
        "e": "depthUpdate",
        "E": 123456789,
        "s": "BNBBTC",
        "U": 157,
        "u": 160,
        "b": [["0.01379900", "10"]],
        "a": [["0.01380000", "100"]],
    }
    ws_event_handler.handle_event(event)
    mock_order_book_sequencer.sequence_update.assert_called_once_with(event)

def test_handle_event_unknown_event_type(ws_event_handler):
    event = {"e": "unknownEventType"}
    with pytest.raises(ValueError, match="Unknown event type"):
        ws_event_handler.handle_event(event)
    ws_event_handler.order_book_sequencer.sequence_update.assert_not_called()