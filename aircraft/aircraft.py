"""
AIRCRAFT BASE
-------------
Abstract aircraft. Has state. Has a trail. Has dreams.
"""
from dataclasses import dataclass, field
from typing import List, Tuple, Optional
from simulation.waypoint import Waypoint


@dataclass
class AircraftState:
    aircraft_id: str
    aircraft_type: str
    position: Tuple[float, float]
    heading: float          # degrees, 0 = north
    altitude: float         # abstract altitude units
    speed: float            # abstract speed units
    target_heading: float
    target_altitude: float
    target_speed: float
    current_waypoint: Optional[Waypoint] = None
    waypoint_index: int = 0
    distance_traveled: float = 0.0
    waypoints_visited: int = 0


class Aircraft:
    """Base class. Subclasses add personality."""

    def __init__(
        self,
        aircraft_id: str,
        aircraft_type: str,
        initial_position: Tuple[float, float],
        initial_heading: float = 0.0,
        initial_altitude: float = 30000.0,
        initial_speed: float = 300.0,
        color: Tuple[int, int, int] = (255, 255, 255),
    ):
        self.state = AircraftState(
            aircraft_id=aircraft_id,
            aircraft_type=aircraft_type,
            position=initial_position,
            heading=initial_heading,
            altitude=initial_altitude,
            speed=initial_speed,
            target_heading=initial_heading,
            target_altitude=initial_altitude,
            target_speed=initial_speed,
        )
        self.color = color
        self._trail: List[Tuple[float, float]] = [initial_position]
        self._max_trail = 600
        self._trail_sample_counter = 0

    @property
    def trail(self) -> List[Tuple[float, float]]:
        return self._trail

    def append_trail(self, position: Tuple[float, float]) -> None:
        self._trail_sample_counter += 1
        if self._trail_sample_counter % 2 == 0:  # sample every 2 frames
            self._trail.append(position)
            if len(self._trail) > self._max_trail:
                self._trail.pop(0)

    def clear_trail(self) -> None:
        self._trail = [self.state.position]

    def set_waypoint(self, wp: Waypoint) -> None:
        self.state.current_waypoint = wp
        self.state.target_heading = self._bearing_to(wp.position)

    def _bearing_to(self, target: Tuple[float, float]) -> float:
        import math
        dx = target[0] - self.state.position[0]
        dy = target[1] - self.state.position[1]
        ang = math.degrees(math.atan2(dx, dy))
        return ang % 360.0

    def distance_to_waypoint(self) -> float:
        if self.state.current_waypoint is None:
            return float("inf")
        return self.state.current_waypoint.distance_to(self.state.position)

    def reset(self, initial_position: Tuple[float, float], initial_heading: float = 0.0) -> None:
        self.state.position = initial_position
        self.state.heading = initial_heading
        self.state.target_heading = initial_heading
        self.state.distance_traveled = 0.0
        self.state.waypoints_visited = 0
        self.state.waypoint_index = 0
        self.state.current_waypoint = None
        self._trail = [initial_position]