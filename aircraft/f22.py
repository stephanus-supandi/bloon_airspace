"""
F-22 RAPTORIZER (™ BLOON)
--------------------------
Turns good. Thinks less.
"""
from aircraft import Aircraft
from simulation.flight import FlightModel


class F22(Aircraft):
    def __init__(self, aircraft_id: str = "F-22", initial_position=(300.0, 450.0)):
        super().__init__(
            aircraft_id=aircraft_id,
            aircraft_type="F-22",
            initial_position=initial_position,
            initial_heading=90.0,
            initial_altitude=35000.0,
            initial_speed=380.0,
            color=(80, 180, 255),   # icy blue
        )
        self.flight_model = FlightModel(
            max_speed=480.0,
            min_speed=140.0,
            max_turn_rate=55.0,     # F-22 turns better (in this fiction)
            max_climb_rate=3500.0,
        )

    def quip(self) -> str:
        import random
        lines = [
            "Bro, kita muter lagi?",
            "Gue kayaknya udah liat Java tiga kali.",
            "Kenapa waypoint-nya di Sulawesi lagi?",
            "Ini F-22, bukan F-uber.",
            "Autopilot, tolong. Tolong.",
        ]
        return random.choice(lines)