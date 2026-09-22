"""
FLIGHT MODEL
------------
Aerodynamically questionable. Visually adequate.

We do NOT simulate:
  - lift, drag, thrust vectors
  - stall, spin, g-loading
  - anything the FAA would care about

We DO simulate:
  - position moves in heading direction at given speed
  - heading turns toward a target at a turn_rate
  - altitude changes linearly
  - speed changes linearly

That's it. That's the simulation.
"""
import math
from typing import Tuple


def normalize_angle(angle_deg: float) -> float:
    """Wrap angle to [0, 360)."""
    return angle_deg % 360.0


def shortest_turn(from_deg: float, to_deg: float) -> float:
    """Signed shortest angular difference in degrees."""
    diff = (to_deg - from_deg + 540.0) % 360.0 - 180.0
    return diff


def bearing(from_pos: Tuple[float, float], to_pos: Tuple[float, float]) -> float:
    """Bearing in degrees (0=north/+y, clockwise)."""
    dx = to_pos[0] - from_pos[0]
    dy = to_pos[1] - from_pos[1]
    # atan2(dx, dy) gives angle from +y axis, clockwise.
    ang = math.degrees(math.atan2(dx, dy))
    return normalize_angle(ang)


class FlightModel:
    """
    Pure-function flight update. No state. Just math.

    Given current state + target + dt, return new state.
    """

    def __init__(
        self,
        max_speed: float = 420.0,      # world units / second (abstract)
        min_speed: float = 120.0,
        max_turn_rate: float = 45.0,   # deg / second
        max_climb_rate: float = 3000.0,# altitude units / second
        max_altitude: float = 50000.0,
        min_altitude: float = 5000.0,
    ):
        self.max_speed = max_speed
        self.min_speed = min_speed
        self.max_turn_rate = max_turn_rate
        self.max_climb_rate = max_climb_rate
        self.max_altitude = max_altitude
        self.min_altitude = min_altitude

    def update(
        self,
        position: Tuple[float, float],
        heading: float,
        altitude: float,
        speed: float,
        target_heading: float,
        target_altitude: float,
        target_speed: float,
        dt: float,
    ) -> Tuple[Tuple[float, float], float, float, float]:
        """
        Returns (new_position, new_heading, new_altitude, new_speed).
        """
        # --- Heading: turn toward target at limited rate ---
        turn_needed = shortest_turn(heading, target_heading)
        max_turn = self.max_turn_rate * dt
        if abs(turn_needed) <= max_turn:
            new_heading = normalize_angle(target_heading)
        else:
            new_heading = normalize_angle(heading + max_turn * (1 if turn_needed >= 0 else -1))

        # --- Speed: linearly approach target ---
        speed_diff = target_speed - speed
        max_speed_change = 80.0 * dt  # abstract acceleration
        if abs(speed_diff) <= max_speed_change:
            new_speed = target_speed
        else:
            new_speed = speed + max_speed_change * (1 if speed_diff >= 0 else -1)
        new_speed = max(self.min_speed, min(self.max_speed, new_speed))

        # --- Altitude: linearly approach target ---
        alt_diff = target_altitude - altitude
        max_alt_change = self.max_climb_rate * dt
        if abs(alt_diff) <= max_alt_change:
            new_altitude = target_altitude
        else:
            new_altitude = altitude + max_alt_change * (1 if alt_diff >= 0 else -1)
        new_altitude = max(self.min_altitude, min(self.max_altitude, new_altitude))

        # --- Position: move in heading direction ---
        # heading 0 = +y (north), 90 = +x (east)
        rad = math.radians(new_heading)
        dx = math.sin(rad) * new_speed * dt
        dy = math.cos(rad) * new_speed * dt
        new_position = (position[0] + dx, position[1] + dy)

        return new_position, new_heading, new_altitude, new_speed