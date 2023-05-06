import json
import pytest
from unittest.mock import AsyncMock, MagicMock, call

from websockets.exceptions import ConnectionClosed
from demo.connectivity.common.websocket_feed import WebSocketFeed, WEBSOCKET_TRANSIENT_ERRORS
import demo.connectivity.common.exceptions as exceptions

@pytest.fixture
def websocket_feed():
    return WebSocketFeed("wss://test.example.com")

@pytest.fixture
def mock_websockets_connect(monkeypatch):
    async def _mock_connect(uri):
        mock_socket = MagicMock()
        mock_socket.close = AsyncMock()
        return mock_socket
    
    monkeypatch.setattr("demo.connectivity.common.websocket_feed.websockets.connect", _mock_connect)
    return _mock_connect

@pytest.mark.asyncio
async def test_connect(websocket_feed, mock_websockets_connect):
    await websocket_feed.connect()
    assert websocket_feed._socket is not None

@pytest.mark.asyncio
async def test_close(websocket_feed, mock_websockets_connect):
    await websocket_feed.connect()
    await websocket_feed.close()
    assert websocket_feed._socket is None

@pytest.mark.asyncio
async def test_send_message(websocket_feed, mock_websockets_connect):
    await websocket_feed.connect()
    websocket_feed._socket.send = AsyncMock()
    await websocket_feed.send_message("test message")
    websocket_feed._socket.send.assert_called_once_with("test message")

@pytest.mark.asyncio
async def test_stream_recover_from_out_of_sequence_error(websocket_feed, mock_websockets_connect):
    handle_event_async = AsyncMock()

    async def mock_stream_init_func_async():
        pass

    await websocket_feed.connect()

    websocket_feed._socket.recv = AsyncMock(side_effect=["{\"message\": \"message1\"}", "{\"message\": \"message2\"}", exceptions.OutOfSequenceError(), "{\"message\": \"message3\"}", "{\"message\": \"message4\"}"])
    websocket_feed._reconnect = AsyncMock()

    with pytest.raises(StopAsyncIteration):
        await websocket_feed.stream(handle_event_async, mock_stream_init_func_async)

    handle_event_async.assert_has_calls([call(json.loads("{\"message\": \"message1\"}")), call(json.loads("{\"message\": \"message2\"}")), call(json.loads("{\"message\": \"message3\"}")), call(json.loads("{\"message\": \"message4\"}"))])
    websocket_feed._reconnect.assert_called_once()

@pytest.mark.asyncio
async def test_transform(websocket_feed):
    data = '{"key": "value"}'
    transformed_data = websocket_feed.transform(data)
    assert transformed_data == json.loads(data)