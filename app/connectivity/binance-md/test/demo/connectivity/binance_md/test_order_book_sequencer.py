from unittest.mock import Mock

import pytest
from demo.connectivity.common.exceptions import OutOfSequenceError

from demo.connectivity.binance_md.order_book_sequencer import (
    BinanceOrderBookSequencer,
)


def test_sequence_update_func__init():
    snapshot_handler = Mock()
    update_handler = Mock()

    sequencer = BinanceOrderBookSequencer(snapshot_handler, update_handler)

    data = {"e": "depthUpdate", "U": 1, "u": 2}
    sequencer.sequence_update_func(data)

    assert len(sequencer._update_queue) == 1
    assert sequencer._update_queue[0] == data

def test_sequence_update_func__main_in_sequence():
    snapshot_handler = Mock()
    update_handler = Mock()

    sequencer = BinanceOrderBookSequencer(snapshot_handler, update_handler)
    sequencer._last_seqnum = 1
    sequencer._last_message = {"e": "depthUpdate", "U": 1, "u": 2}
    sequencer.sequence_update_func = sequencer._sequence_update_func__main

    data = {"e": "depthUpdate", "U": 2, "u": 3}
    sequencer.sequence_update_func(data)

    assert sequencer._last_message == data
    assert sequencer._last_seqnum == 3
    update_handler.assert_called_once_with(data)

def test_sequence_update_func__main_out_of_sequence():
    snapshot_handler = Mock()
    update_handler = Mock()

    sequencer = BinanceOrderBookSequencer(snapshot_handler, update_handler)
    sequencer._last_seqnum = 1
    sequencer._last_message = {"e": "depthUpdate", "U": 1, "u": 2}
    sequencer.sequence_update_func = sequencer._sequence_update_func__main

    data = {"e": "depthUpdate", "U": 3, "u": 4}

    with pytest.raises(OutOfSequenceError):
        sequencer.sequence_update_func(data)

def test_sequence_update_func__first_update():
    snapshot_handler = Mock()
    update_handler = Mock()

    sequencer = BinanceOrderBookSequencer(snapshot_handler, update_handler)
    sequencer._last_seqnum = 1
    sequencer._last_message = {"e": "depthUpdate", "U": 1, "u": 2}
    sequencer.sequence_update_func = sequencer._sequence_update_func__first_update

    data = {"e": "depthUpdate", "U": 2, "u": 3}
    sequencer.sequence_update_func(data)

    assert sequencer._last_message == data
    assert sequencer._last_seqnum == 3
    update_handler.assert_called_once_with(data)
    assert sequencer.sequence_update_func == sequencer._sequence_update_func__main

def test_sequence_snapshot_and_queued_updates():
    snapshot_handler = Mock()
    update_handler = Mock()

    sequencer = BinanceOrderBookSequencer(snapshot_handler, update_handler)
    sequencer._update_queue.append({"e": "depthUpdate", "U": 2, "u": 3})

    data = {"e": "depthUpdate", "lastUpdateId": 1}
    sequencer.sequence_snapshot_and_queued_updates(data)

    assert sequencer._last_seqnum == 3
    snapshot_handler.assert_called_once_with(data)
    update_handler.assert_called_once_with(data)