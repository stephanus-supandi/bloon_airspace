"""
TESTS
-----
Verifies BLOON REPRODUCIBILITY LAW:
  same seed + same initial state = same trajectory.

Run:  python -m pytest tests/ -v
Or:   python tests/test_determinism.py
"""
import os
import sys
import math

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from simulation.rng import BloonRNG
from simulation.waypoint import WaypointManager
from simulation.flight import FlightModel
from simulation.replay import ReplayRecorder, Snapshot
from aircraft import F22, F35


def test_rng_deterministic():
    a = BloonRNG(1337)
    b = BloonRNG(1337)
    seq_a = [a.uniform(0, 1) for _ in range(50)]
    seq_b = [b.uniform(0, 1) for _ in range(50)]
    assert seq_a == seq_b, "RNG not deterministic across instances with same seed"


def test_rng_reset():
    r = BloonRNG(42)
    first = [r.uniform(0, 1) for _ in range(20)]
    r.reset()
    second = [r.uniform(0, 1) for _ in range(20)]
    assert first == second, "RNG reset did not reproduce sequence"


def test_flight_model_deterministic():
    fm = FlightModel()
    state = ((300.0, 450.0), 90.0, 35000.0, 380.0)
    out_a = fm.update(*state, target_heading=180.0, target_altitude=35000.0,
                      target_speed=380.0, dt=0.1)
    out_b = fm.update(*state, target_heading=180.0, target_altitude=35000.0,
                      target_speed=380.0, dt=0.1)
    assert out_a == out_b, "Flight model not deterministic"


def test_aircraft_trajectory_deterministic():
    """Run 100 ticks of AUTO-like flight. Must match exactly."""
    def run():
        f22 = F22()
        f35 = F35()
        rng = BloonRNG(1337)
        wm = WaypointManager()
        fm22 = f22.flight_model
        fm35 = f35.flight_model

        f22.set_waypoint(wm.waypoints[1])
        f35.set_waypoint(wm.waypoints[4])

        positions = []
        for i in range(100):
            # Chaos-style random waypoint reassignment (uses local RNG)
            if i % 20 == 0 and i > 0:
                f22.set_waypoint(rng.choice(wm.waypoints))
                f35.set_waypoint(rng.choice(wm.waypoints))

            for ac, fm in ((f22, fm22), (f35, fm35)):
                if ac.state.current_waypoint:
                    ac.state.target_heading = ac._bearing_to(ac.state.current_waypoint.position)
                new_pos, new_hdg, new_alt, new_spd = fm.update(
                    ac.state.position, ac.state.heading, ac.state.altitude, ac.state.speed,
                    ac.state.target_heading, ac.state.target_altitude, ac.state.target_speed,
                    dt=0.1,
                )
                ac.state.position = new_pos
                ac.state.heading = new_hdg
                ac.state.altitude = new_alt
                ac.state.speed = new_spd
            positions.append((f22.state.position, f35.state.position))
        return positions

    run_a = run()
    run_b = run()
    assert run_a == run_b, "Trajectories diverged across runs with same seed"


def test_waypoint_approach():
    """Aircraft should eventually get closer to its waypoint."""
    f22 = F22(initial_position=(300.0, 450.0))
    wm = WaypointManager()
    target = wm.get_by_name("JAVA")
    f22.set_waypoint(target)

    initial_dist = f22.distance_to_waypoint()
    fm = f22.flight_model

    for _ in range(200):
        f22.state.target_heading = f22._bearing_to(target.position)
        new_pos, new_hdg, new_alt, new_spd = fm.update(
            f22.state.position, f22.state.heading, f22.state.altitude, f22.state.speed,
            f22.state.target_heading, f22.state.target_altitude, f22.state.target_speed,
            dt=0.1,
        )
        f22.state.position = new_pos
        f22.state.heading = new_hdg

    final_dist = f22.distance_to_waypoint()
    assert final_dist < initial_dist, (
        f"Aircraft did not approach waypoint: {initial_dist:.1f} -> {final_dist:.1f}"
    )


def test_replay_record_and_playback():
    rec = ReplayRecorder()
    for i in range(10):
        rec.record(Snapshot(
            time=float(i), aircraft_id="F-22",
            x=float(i), y=float(i * 2),
            altitude=35000.0, heading=90.0, speed=300.0,
        ))
    from simulation.replay import ReplayPlayer
    player = ReplayPlayer(rec.snapshots)
    player.play()
    frames_seen = []
    while player.index < player.total - 1:
        frames_seen.append(player.current_frame())
        player.advance()
    frames_seen.append(player.current_frame())
    assert len(frames_seen) == 10, f"Expected 10 frames, got {len(frames_seen)}"
    assert frames_seen[0].time == 0.0
    assert frames_seen[-1].time == 9.0


def test_reset_returns_initial_state():
    f22 = F22()
    original_pos = f22.state.position
    original_hdg = f22.state.heading
    # Perturb
    f22.state.position = (999.0, 999.0)
    f22.state.heading = 277.0
    f22.state.distance_traveled = 5000.0
    # Reset
    f22.reset(original_pos, original_hdg)
    assert f22.state.position == original_pos
    assert f22.state.heading == original_hdg
    assert f22.state.distance_traveled == 0.0


if __name__ == "__main__":
    test_rng_deterministic()
    test_rng_reset()
    test_flight_model_deterministic()
    test_aircraft_trajectory_deterministic()
    test_waypoint_approach()
    test_replay_record_and_playback()
    test_reset_returns_initial_state()
    print("All BLOON tests passed. Reproducibility law intact. 🗿")