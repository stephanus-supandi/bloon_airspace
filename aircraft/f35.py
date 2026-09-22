"""
F-35 LIGHTNING II (sort of)
----------------------------
Confused. Consistently.
"""
from aircraft import Aircraft
from simulation.flight import FlightModel


class F35(Aircraft):
    def __init__(self, aircraft_id: str = "F-35", initial_position=(750.0, 350.0)):
        super().__init__(
            aircraft_id=aircraft_id,
            aircraft_type="F-35",
            initial_position=initial_position,
            initial_heading=180.0,
            initial_altitude=32000.0,
            initial_speed=340.0,
            color=(255, 180, 80),   # warm orange
        )
        self.flight_model = FlightModel(
            max_speed=440.0,
            min_speed=130.0,
            max_turn_rate=45.0,
            max_climb_rate=3000.0,
        )

    def quip(self) -> str:
        import random
        lines = [
            "Gue juga nggak tahu kita ke mana.",
            "Apakah ini Papua? Kayaknya Papua.",
            "F-22, lo tau kita ngapain nggak?",
            "Gue forgot where I was going. Again.",
            "BLOON said turn left. So I turned left.",
        ]
        return random.choice(lines)