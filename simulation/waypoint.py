"""
WAYPOINT SYSTEM
---------------
Just coordinates with names. No military significance.
These are just... places. Vaguely.
"""
from dataclasses import dataclass
from typing import List, Tuple


@dataclass(frozen=True)
class Waypoint:
    name: str
    position: Tuple[float, float]  # world coords (x, y)

    def distance_to(self, other_pos: Tuple[float, float]) -> float:
        dx = other_pos[0] - self.position[0]
        dy = other_pos[1] - self.position[1]
        return (dx * dx + dy * dy) ** 0.5


# Canonical Indonesian waypoint set.
# Coordinates are fictional but maintain relative geography.
# (We promise this is not operational data. It's vibes.)
INDONESIA_WAYPOINTS: List[Waypoint] = [
    Waypoint("SUMATRA",      (300.0, 450.0)),
    Waypoint("JAVA",         (680.0, 720.0)),
    Waypoint("BALI",         (820.0, 730.0)),
    Waypoint("LOMBOK",       (880.0, 735.0)),
    Waypoint("KALIMANTAN",   (750.0, 350.0)),
    Waypoint("SULAWESI",     (1050.0, 420.0)),
    Waypoint("MALUKU",       (1280.0, 500.0)),
    Waypoint("PAPUA",        (1600.0, 450.0)),
]


class WaypointManager:
    """Manages waypoint sequences for aircraft."""

    def __init__(self, waypoints: List[Waypoint] = None):
        self._waypoints = waypoints if waypoints is not None else list(INDONESIA_WAYPOINTS)

    @property
    def waypoints(self) -> List[Waypoint]:
        return self._waypoints

    def get_by_name(self, name: str) -> Waypoint:
        for w in self._waypoints:
            if w.name == name:
                return w
        raise KeyError(f"Waypoint '{name}' not found. BLOON is confused.")

    def next_in_sequence(self, current_index: int) -> int:
        return (current_index + 1) % len(self._waypoints)