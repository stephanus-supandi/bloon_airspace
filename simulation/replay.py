"""
REPLAY SYSTEM
-------------
Records every frame. Plays it back. Rewinds. Fast-forwards.
Time is a flat circle. BLOON approves.
"""
from dataclasses import dataclass, field
from typing import List, Tuple


@dataclass
class Snapshot:
    time: float
    aircraft_id: str
    x: float
    y: float
    altitude: float
    heading: float
    speed: float
    waypoint_name: str = ""


class ReplayRecorder:
    """Records snapshots every tick."""

    def __init__(self):
        self._snapshots: List[Snapshot] = []
        self._recording = True

    def record(self, snapshot: Snapshot) -> None:
        if self._recording:
            self._snapshots.append(snapshot)

    def clear(self) -> None:
        self._snapshots.clear()

    @property
    def snapshots(self) -> List[Snapshot]:
        return self._snapshots

    def __len__(self) -> int:
        return len(self._snapshots)


class ReplayPlayer:
    """
    Plays back a recorded list of snapshots.
    Supports play/pause/rewind/fast-forward.
    """

    def __init__(self, snapshots: List[Snapshot]):
        self._all = snapshots
        self._index = 0
        self._playing = False
        self._speed = 1.0  # 1.0 = normal, 2.0 = 2x, -1.0 = rewind

    @property
    def playing(self) -> bool:
        return self._playing

    @property
    def speed(self) -> float:
        return self._speed

    @property
    def index(self) -> int:
        return self._index

    @property
    def total(self) -> int:
        return len(self._all)

    def play(self) -> None:
        self._playing = True
        if self._speed == 0:
            self._speed = 1.0

    def pause(self) -> None:
        self._playing = False

    def rewind(self) -> None:
        self._playing = True
        self._speed = -1.0

    def fast_forward(self) -> None:
        self._playing = True
        self._speed = 4.0

    def normal_speed(self) -> None:
        self._speed = 1.0
        self._playing = True

    def current_frame(self) -> Snapshot:
        if not self._all:
            raise IndexError("No snapshots to play. BLOON has nothing to show.")
        idx = max(0, min(self._index, len(self._all) - 1))
        return self._all[idx]

    def advance(self) -> None:
        """Advance one tick based on current speed."""
        if not self._playing:
            return
        step = int(self._speed) if self._speed != 0 else 0
        self._index += step
        if self._index >= len(self._all):
            self._index = len(self._all) - 1
            self._playing = False
        elif self._index < 0:
            self._index = 0
            self._playing = False

    def seek(self, index: int) -> None:
        self._index = max(0, min(index, len(self._all) - 1))