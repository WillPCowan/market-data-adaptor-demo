
import collections
import logging
from typing import Any, Callable, Dict, Optional

from demo.connectivity.common.exceptions import OutOfSequenceError

logger = logging.getLogger(__name__)

class BinanceEventKeyError(Exception):
    pass

# TODO: Create abstract class for sequencer, for exchange sequencers to inherit from
class BinanceOrderBookSequencer():
    """Validates sequence of order book updates and raises when sequence is broken."""

    def __init__(
        self,
        handle_snapshot: Callable[[Dict[str, Any]], None],
        handle_update: Callable[[Dict[str, Any]], None],
    ) -> None:

        self.sequence_update_func = self._sequence_update_func__init

        self._handle_snapshot = handle_snapshot
        self._handle_update = handle_update

        self._last_message: Optional[Dict[str, Any]] = None
        self._last_seqnum: Optional[int] = None

        self._update_queue: collections.deque[Dict[str, Any]] = collections.deque()

    def sequence_update(self, data: Dict[str, Any]) -> None:
        if self._filter_out_event(data):
            return
        self.sequence_update_func(data)

    def sequence_snapshot_and_queued_updates(self, data: Dict[str, Any]) -> None:
        logger.info("Sequencing snapshot and replaying queued updates")

        self._handle_snapshot(data)
        self._last_message = data
        self._last_seqnum = self._seqnum_from_snapshot(data)

        # Replay queued updates
        newest_seqnum = self._last_seqnum
        newest_message = self._last_message
        while len(self._update_queue) > 0:
            replay_data = self._update_queue.popleft()
            replay_seqnum = self._seqnum_from_update(replay_data)

            # Only process updates that are newer than the snapshot
            if replay_seqnum > self._last_seqnum:
                newest_message = replay_data
                newest_seqnum = replay_seqnum
                self._last_message_was_snapshot = False
                self._handle_update(data)

        if newest_seqnum > self._last_seqnum:
            self._last_message = newest_message
            self._last_seqnum = newest_seqnum
            self.sequence_update_func = self._sequence_update_func__main
        else:
            self.sequence_update_func = self._sequence_update_func__first_update


    def _filter_out_event(self, data: Dict[str, Any]) -> bool:
        if data.get("e") == "depthUpdate":
            return False
        
        # Filter out subscription confirmation messages
        return True 

    def _seqnum_from_update(self, data: str) -> int:
        try:
            return int(data["u"]) # Final update ID
        except KeyError:
            # Create an error noting the key expected key and the event
            raise BinanceEventKeyError(f"Key 'U' not found in event: {data}")
    
    def _seqnum_from_snapshot(self, data: str) -> int:
        return int(data["lastUpdateId"])

    def _reset_sequencer(self):
        self._last_message = None
        self._last_seqnum = None
        self._sequence_update = self._sequence_update_func__init

    def _process_update(self, data: Dict[str, Any]) -> None:
        self._last_message = data
        self._last_seqnum = int(data["u"])
        self._handle_update(data)
    
    def _sequence_update_func__init(self, data: Dict[str, Any]) -> None:
        self._update_queue.append(data)

    def _sequence_update_func__first_update(self, data: Dict[str, Any]) -> None:
        if int(data["U"]) <= self._last_seqnum + 1: 
            if int(data["u"]) >= self._last_seqnum + 1:
                # Switch to main sequencing logic
                self.sequence_update_func = self._sequence_update_func__main 
                self._process_update(data)
            else:
                # NOTE: stale message can be ignored
                return 
        else:
            errMsg = f"Sequence broken (last={self._last_message['u']} vs new={self._last_message['U']}). The first processed update event is out of sequence {data} relative to the snapshot {self._last_message}"
            self._reset_sequencer()
            raise OutOfSequenceError(errMsg)

    def _sequence_update_func__main(self, data: Dict[str, Any]) -> None:
        if data["U"] == self._last_seqnum + 1:
            self._process_update(data)
        else:
            errMsg = f"Sequence broken (last={self._last_message['u']} vs new={self._last_message['U']}). The first processed update event is out of sequence {data} relative to the snapshot {self._last_message}"
            self._reset_sequencer()
            raise OutOfSequenceError(errMsg)
