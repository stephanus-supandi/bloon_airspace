"""
BLOON AIRSPACE v2
-----------------
main.py — where the nonsense becomes executable.

v2 CHANGELOG:
  - Added BLOON LAYER (cosmetic stupidity)
  - Added [G] ASK WHY (useless button)
  - Added [M] MAKE IT WORSE (mandatory)
  - Added Brain Status panel
  - Added Waypoint Reason checkboxes
  - Added PURPOSE / MISSION / STRATEGY one-liners
  - Simulation layer: UNTOUCHED. Still deterministic. Still serious.

Two aircraft. One map. Zero reasons.

Solitude Labs™ — Engineering More, Flying Nowhere.
"""
import os
import sys
import pygame

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from simulation.rng import BloonRNG
from simulation.waypoint import WaypointManager
from simulation.replay import ReplayRecorder, ReplayPlayer, Snapshot
from aircraft import F22, F35
from ui import MapScreen, HUD, Controls


SEED = 1337
SCREEN_W, SCREEN_H = 1280, 820
WAYPOINT_ARRIVAL_RADIUS = 60.0


# ── BLOON EVENT DATABASES ──
# These are COSMETIC. They do not affect simulation state.

BLOON_EVENTS_AUTO = [
    "Waypoint recalculated.",
    "F-35 forgot where it was going.",
    "F-22 discovered Java.",
    "Both aircraft are currently doing absolutely nothing.",
    "Waypoint selected by highly sophisticated BLOON AI.",
    "BLOON.",
    "F-22: Bro, kita muter lagi?",
    "F-35: Kayaknya iya.",
    "SYSTEM: Affirmative. Muter lagi.",
    "F-35: Is this Sumatra or Sulawesi?",
    "SYSTEM: Yes.",
    "F-22: Kenapa waypoint-nya di sini?",
    "SYSTEM: Karena BLOON.",
    "F-35: Gue udah lupa tujuan awal.",
    "SYSTEM: Tidak ada tujuan awal.",
]

BLOON_EVENTS_CHAOS = [
    "CHAOS MODE: ON",
    "F-22: Kenapa gue ke Papua?",
    "F-35: Kenapa gue ke Sumatra?",
    "SYSTEM: Karena seed.",
    "F-22: Seed siapa?",
    "SYSTEM: 1337.",
    "F-35: ...",
    "SYSTEM: BLOON.",
    "Waypoint changed. No reason.",
    "F-22: Wait, we were just there.",
    "F-35: And now we're going back.",
    "BLOON AI: Trust the process.",
    "The process is nonsense.",
    "F-22: I have questions.",
    "SYSTEM: No you don't.",
    "F-35: Gue mau pulang.",
    "SYSTEM: Rumah lo di mana?",
    "F-35: ...BLOON?",
    "SYSTEM: Correct.",
]

MAKE_WORSE_EVENTS = [
    "BLOON LEVEL INCREASED. Nothing changed in the simulation.",
    "The simulation is still deterministic. The HUD is not.",
    "F-22 brain cells: declining.",
    "F-35 has accepted its fate.",
    "SYSTEM: Why are you doing this?",
    "BLOON LEVEL UP. Purpose: still unknown.",
    "The aircraft don't care. They never did.",
    "F-35: Gue udah pasrah.",
    "F-22: Ini bukan simulator, ini therapy.",
    "SYSTEM: BLOON LEVEL {level}. Simulation integrity: 100%.",
    "You pressed M again. The simulation remains perfect.",
    "The contrast IS the joke.",
    "F-22: Bro, HUD-nya kenapa makin aneh?",
    "SYSTEM: Because you pressed M.",
    "F-35: Gue gak mau liat lagi.",
]


class GameMode:
    FREE = "FREE"
    AUTO = "AUTO"
    CHAOS = "CHAOS"
    REPLAY = "REPLAY"


class BloonAirspace:
    def __init__(self, seed: int = SEED):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
        pygame.display.set_caption("BLOON AIRSPACE v2 — Solitude Labs")
        self.clock = pygame.time.Clock()

        # ── SIMULATION STATE (serious, deterministic) ──
        self.seed = seed
        self.rng = BloonRNG(seed)

        self.f22 = F22()
        self.f35 = F35()
        self._initial_f22_pos = self.f22.state.position
        self._initial_f35_pos = self.f35.state.position
        self._initial_f22_hdg = self.f22.state.heading
        self._initial_f35_hdg = self.f35.state.heading

        self.wp_manager = WaypointManager()
        self.recorder = ReplayRecorder()
        self.replay_player: ReplayPlayer = None

        self.mode = GameMode.AUTO
        self.selected = "F-22"
        self.show_trail = True

        self.map_screen = MapScreen(self.screen)
        self.hud = HUD(self.screen)
        self.controls = Controls()

        self.sim_time = 0.0
        self._chaos_timer = 0.0
        self._event_timer = 0.0
        self._show_report = False
        self._running = True

        # ── BLOON LAYER STATE (cosmetic, NOT simulation) ──
        # These variables do NOT affect flight model, waypoints, or RNG.
        self.bloon_level = 1
        self.ask_why_count = 0
        self.chaos_level = 0.0

        self._assign_initial_auto_waypoints()

    # ── Setup ──

    def _assign_initial_auto_waypoints(self) -> None:
        self.f22.set_waypoint(self.wp_manager.waypoints[1])
        self.f22.state.waypoint_index = 1
        self.f35.set_waypoint(self.wp_manager.waypoints[4])
        self.f35.state.waypoint_index = 4

    def _reset(self) -> None:
        # ── Reset simulation (serious) ──
        self.rng.reset()
        self.f22.reset(self._initial_f22_pos, self._initial_f22_hdg)
        self.f22.state.target_altitude = 35000.0
        self.f22.state.target_speed = 380.0
        self.f22.state.altitude = 35000.0
        self.f22.state.speed = 380.0

        self.f35.reset(self._initial_f35_pos, self._initial_f35_hdg)
        self.f35.state.target_altitude = 32000.0
        self.f35.state.target_speed = 340.0
        self.f35.state.altitude = 32000.0
        self.f35.state.speed = 340.0

        self.recorder.clear()
        self.replay_player = None
        self.sim_time = 0.0
        self._chaos_timer = 0.0
        self._event_timer = 0.0
        self._show_report = False
        self.hud.events.clear()

        # ── Reset BLOON layer (cosmetic) ──
        self.bloon_level = 1
        self.ask_why_count = 0
        self.chaos_level = 0.0
        self.hud.bloon_level = 1
        self.hud.ask_why_count = 0
        self.hud.chaos_level = 0.0
        self.hud.last_ask_why_response = ""

        self._assign_initial_auto_waypoints()
        self.hud.push_event("RESET. BLOON APPROVES. 🗿")

    # ── Input ──

    def _handle_input(self) -> None:
        self.controls.poll()
        c = self.controls

        if c.quit_requested:
            self._running = False
            return

        if c.reset_requested:
            self._reset()
            return

        if c.show_report:
            self._show_report = True
            return

        if c.mode_free:
            self.mode = GameMode.FREE
            self.hud.push_event("MODE: FREE FLIGHT")
        if c.mode_auto:
            self.mode = GameMode.AUTO
            self.chaos_level = 0.0
            self.hud.chaos_level = 0.0
            self.hud.push_event("MODE: AUTO PILOT")
        if c.mode_chaos:
            self.mode = GameMode.CHAOS
            self.chaos_level = 50.0
            self.hud.chaos_level = 50.0
            self.hud.push_event("CHAOS MODE: ON 🤣")
        if c.mode_replay:
            self._enter_replay_mode()

        if c.toggle_trail:
            self.show_trail = not self.show_trail
        if c.clear_trail:
            self.f22.clear_trail()
            self.f35.clear_trail()
            self.hud.push_event("Trails cleared. History erased.")

        if c.select_f22:
            self.selected = "F-22"
        if c.select_f35:
            self.selected = "F-35"

        # Replay controls
        if self.mode == GameMode.REPLAY and self.replay_player:
            if c.replay_play:
                self.replay_player.play()
            if c.replay_pause:
                self.replay_player.pause()
            if c.replay_rewind:
                self.replay_player.rewind()
            if c.replay_ff:
                self.replay_player.fast_forward()

        # ── BLOON LAYER INPUT ──
        if c.ask_why:
            self._handle_ask_why()
        if c.make_worse:
            self._handle_make_worse()

    def _handle_ask_why(self) -> None:
        """[G] ASK WHY — the most useless button in aviation history."""
        self.ask_why_count += 1
        idx = min(self.ask_why_count - 1, len(ASK_WHY_RESPONSES) - 1)
        response = ASK_WHY_RESPONSES[idx]
        self.hud.last_ask_why_response = response
        self.hud.push_event(f"YOU: Why?")
        self.hud.push_event(f"SYSTEM: {response}")

        # After 10 presses, escalate
        if self.ask_why_count == 10:
            self.hud.push_event("SYSTEM: BRO, DONE.")
        if self.ask_why_count >= 15:
            self.hud.push_event("SYSTEM: You're still pressing G?")

    def _handle_make_worse(self) -> None:
        """[M] MAKE IT WORSE — mandatory BLOON feature."""
        self.bloon_level += 1
        self.hud.bloon_level = self.bloon_level

        # Pick a response (deterministic based on level)
        event_idx = (self.bloon_level - 2) % len(MAKE_WORSE_EVENTS)
        event = MAKE_WORSE_EVENTS[event_idx]
        event = event.replace("{level}", str(self.bloon_level))
        self.hud.push_event(f"[M] BLOON LEVEL: {self.bloon_level}")
        self.hud.push_event(event)

        # Increase chaos level cosmetically
        self.chaos_level = min(99.0, self.chaos_level + 5.0)
        self.hud.chaos_level = self.chaos_level

        # At certain thresholds, special events
        if self.bloon_level == 10:
            self.hud.push_event("SYSTEM: BLOON LEVEL 10. Simulation still perfect.")
        if self.bloon_level == 50:
            self.hud.push_event("SYSTEM: BLOON LEVEL 50. F-35 has given up.")
        if self.bloon_level == 100:
            self.hud.push_event("SYSTEM: BLOON LEVEL 100. Achievement: WHY.")
        if self.bloon_level == 999:
            self.hud.push_event("SYSTEM: BLOON LEVEL 999. You win. There is no prize.")

    def _enter_replay_mode(self) -> None:
        if len(self.recorder) < 2:
            self.hud.push_event("Not enough data to replay. Fly a bit first.")
            return
        self.replay_player = ReplayPlayer(self.recorder.snapshots)
        self.replay_player.play()
        self.mode = GameMode.REPLAY
        self.hud.push_event("MODE: REPLAY")

    # ── Simulation (UNTOUCHED from v1 — still serious, still deterministic) ──

    def _selected_aircraft(self):
        return self.f22 if self.selected == "F-22" else self.f35

    def _update_free_flight(self, dt: float) -> None:
        ac = self._selected_aircraft()
        c = self.controls
        turn = 60.0 * dt
        if c.turn_left:
            ac.state.target_heading = (ac.state.target_heading - turn) % 360.0
        if c.turn_right:
            ac.state.target_heading = (ac.state.target_heading + turn) % 360.0
        speed_step = 120.0 * dt
        if c.speed_up:
            ac.state.target_speed = min(
                ac.flight_model.max_speed, ac.state.target_speed + speed_step
            )
        if c.speed_down:
            ac.state.target_speed = max(
                ac.flight_model.min_speed, ac.state.target_speed - speed_step
            )
        alt_step = 5000.0 * dt
        if c.climb:
            ac.state.target_altitude = min(
                ac.flight_model.max_altitude, ac.state.target_altitude + alt_step
            )
        if c.descend:
            ac.state.target_altitude = max(
                ac.flight_model.min_altitude, ac.state.target_altitude - alt_step
            )

    def _update_auto_pilot(self, dt: float) -> None:
        for ac in (self.f22, self.f35):
            if ac.state.current_waypoint is None:
                continue
            if ac.distance_to_waypoint() < WAYPOINT_ARRIVAL_RADIUS:
                ac.state.waypoints_visited += 1
                ac.state.waypoint_index = self.wp_manager.next_in_sequence(
                    ac.state.waypoint_index
                )
                new_wp = self.wp_manager.waypoints[ac.state.waypoint_index]
                ac.set_waypoint(new_wp)
                self.hud.push_event(
                    f"{ac.state.aircraft_id}: BRO, KITA SUDAH SAMPAI. Next: {new_wp.name}"
                )

    def _update_chaos_mode(self, dt: float) -> None:
        self._chaos_timer += dt
        if self._chaos_timer >= 5.0:
            self._chaos_timer = 0.0
            for ac in (self.f22, self.f35):
                new_wp = self.rng.choice(self.wp_manager.waypoints)
                ac.set_waypoint(new_wp)
            self.hud.push_event(self.rng.choice(BLOON_EVENTS_CHAOS))

    def _update_events(self, dt: float) -> None:
        self._event_timer += dt
        if self._event_timer >= 7.0:
            self._event_timer = 0.0
            if self.mode == GameMode.AUTO:
                self.hud.push_event(self.rng.choice(BLOON_EVENTS_AUTO))
            elif self.mode == GameMode.CHAOS:
                self.hud.push_event(self.rng.choice(BLOON_EVENTS_CHAOS))

    def _step_aircraft(self, ac, dt: float) -> None:
        old_pos = ac.state.position
        new_pos, new_hdg, new_alt, new_spd = ac.flight_model.update(
            position=ac.state.position,
            heading=ac.state.heading,
            altitude=ac.state.altitude,
            speed=ac.state.speed,
            target_heading=ac.state.target_heading,
            target_altitude=ac.state.target_altitude,
            target_speed=ac.state.target_speed,
            dt=dt,
        )
        dx = new_pos[0] - old_pos[0]
        dy = new_pos[1] - old_pos[1]
        ac.state.distance_traveled += (dx * dx + dy * dy) ** 0.5

        ac.state.position = new_pos
        ac.state.heading = new_hdg
        ac.state.altitude = new_alt
        ac.state.speed = new_spd

        if ac.state.current_waypoint is not None:
            ac.state.target_heading = ac._bearing_to(
                ac.state.current_waypoint.position
            )

        ac.append_trail(new_pos)

    def _record_snapshot(self) -> None:
        for ac in (self.f22, self.f35):
            self.recorder.record(
                Snapshot(
                    time=self.sim_time,
                    aircraft_id=ac.state.aircraft_id,
                    x=ac.state.position[0],
                    y=ac.state.position[1],
                    altitude=ac.state.altitude,
                    heading=ac.state.heading,
                    speed=ac.state.speed,
                    waypoint_name=(
                        ac.state.current_waypoint.name
                        if ac.state.current_waypoint
                        else ""
                    ),
                )
            )

    def _apply_replay_frame(self) -> None:
        if not self.replay_player:
            return
        idx = self.replay_player.index
        base = (idx // 2) * 2
        for ac, offset in ((self.f22, 0), (self.f35, 1)):
            snap_idx = base + offset
            if snap_idx < len(self.recorder.snapshots):
                snap = self.recorder.snapshots[snap_idx]
                ac.state.position = (snap.x, snap.y)
                ac.state.altitude = snap.altitude
                ac.state.heading = snap.heading
                ac.state.speed = snap.speed

    def _simulate(self, dt: float) -> None:
        if self.mode == GameMode.FREE:
            self._update_free_flight(dt)
            self._step_aircraft(self.f22, dt)
            self._step_aircraft(self.f35, dt)
            self._lazy_circle(self.f35, dt)
        elif self.mode == GameMode.AUTO:
            self._update_auto_pilot(dt)
            self._step_aircraft(self.f22, dt)
            self._step_aircraft(self.f35, dt)
        elif self.mode == GameMode.CHAOS:
            self._update_chaos_mode(dt)
            self._step_aircraft(self.f22, dt)
            self._step_aircraft(self.f35, dt)
        elif self.mode == GameMode.REPLAY:
            if self.replay_player and self.replay_player.playing:
                steps = max(1, int(abs(self.replay_player.speed)))
                for _ in range(steps):
                    self.replay_player.advance()
                self._apply_replay_frame()

        self._update_events(dt)
        self.hud.update()

        if self.mode != GameMode.REPLAY:
            self.sim_time += dt
            self._record_snapshot()

    def _lazy_circle(self, ac, dt: float) -> None:
        ac.state.target_heading = (ac.state.target_heading + 8.0 * dt) % 360.0
        ac.state.target_speed = 260.0
        ac.state.target_altitude = 28000.0

    # ── Render ──

    def _render(self) -> None:
        self.map_screen.draw_background()
        self.map_screen.draw_islands()

        self.map_screen.draw_trail(self.f22, self.show_trail)
        self.map_screen.draw_trail(self.f35, self.show_trail)

        self.map_screen.draw_aircraft(self.f22, self.selected == "F-22")
        self.map_screen.draw_aircraft(self.f35, self.selected == "F-35")

        rp = self.replay_player
        self.hud.draw(
            f22=self.f22,
            f35=self.f35,
            mode=self.mode,
            selected=self.selected,
            show_trail=self.show_trail,
            sim_time=self.sim_time,
            seed=self.seed,
            replay_speed=rp.speed if rp else 1.0,
            replay_playing=rp.playing if rp else False,
            replay_index=rp.index if rp else 0,
            replay_total=rp.total if rp else 0,
        )

        pygame.display.flip()

    # ── Report Screen (now stupider) ──

    def _draw_report(self) -> None:
        self.screen.fill((10, 14, 24))
        font_big = pygame.font.SysFont("consolas", 32, bold=True)
        font = pygame.font.SysFont("consolas", 18)
        font_small = pygame.font.SysFont("consolas", 14)
        font_tiny = pygame.font.SysFont("consolas", 12)

        title = font_big.render("BLOON AIRSPACE REPORT", True, (255, 230, 140))
        self.screen.blit(title, (SCREEN_W // 2 - title.get_width() // 2, 60))

        pygame.draw.line(
            self.screen, (80, 90, 110), (100, 105), (SCREEN_W - 100, 105), 2
        )

        total_wp = self.f22.state.waypoints_visited + self.f35.state.waypoints_visited

        lines = [
            f"F-22 distance: {self.f22.state.distance_traveled:,.0f} km (abstract)",
            f"F-35 distance: {self.f35.state.distance_traveled:,.0f} km (abstract)",
            f"Waypoints visited: {total_wp}",
            f"Collisions: 0",
            f"Missiles fired: 0",
            f"Actual purpose: UNKNOWN",
            f"Actual strategy: TIDAK ADA",
            f"Brain cells remaining: DEBATABLE",
            "",
            f"Simulation time: {self.sim_time:.1f} s",
            f"Seed: {self.seed}",
            f"Replay frames: {len(self.recorder)}",
            f"BLOON LEVEL achieved: {self.bloon_level}",
            f"Times you pressed [G]: {self.ask_why_count}",
            f"Times you pressed [M]: {max(0, self.bloon_level - 1)}",
            f"Simulation integrity: 100% (always)",
            f"HUD integrity: {max(1, 100 - self.bloon_level * 3)}% (declining)",
        ]

        y = 130
        for line in lines:
            surf = font.render(line, True, (220, 225, 235))
            self.screen.blit(surf, (140, y))
            y += 26

        pygame.draw.line(
            self.screen, (80, 90, 110), (100, y + 10), (SCREEN_W - 100, y + 10), 2
        )

        mission = font_big.render(
            "BLOON MISSION COMPLETE", True, (180, 220, 255)
        )
        self.screen.blit(
            mission, (SCREEN_W // 2 - mission.get_width() // 2, y + 30)
        )

        # Footer
        footers = [
            "Two aircraft. One map. Zero reasons.",
            "Solitude Labs™ — Engineering More, Flying Nowhere.",
            f"The simulation was deterministic. The pilot was not.",
        ]
        fy = y + 80
        for f_text in footers:
            surf = font_tiny.render(f_text, True, (140, 150, 170))
            self.screen.blit(
                surf, (SCREEN_W // 2 - surf.get_width() // 2, fy)
            )
            fy += 18

        hint = font_tiny.render(
            "[ESC] return   [R] reset   [Q] quit",
            True, (100, 110, 130),
        )
        self.screen.blit(
            hint, (SCREEN_W // 2 - hint.get_width() // 2, SCREEN_H - 30)
        )

        pygame.display.flip()

    def _handle_report_input(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self._running = False
                return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self._show_report = False
                elif event.key == pygame.K_r:
                    self._reset()
                    self._show_report = False
                elif event.key == pygame.K_q:
                    self._running = False

    # ── Main Loop ──

    def run(self) -> None:
        self.hud.push_event("BLOON AIRSPACE v2 ONLINE.")
        self.hud.push_event("Two aircraft. Zero reasons.")
        self.hud.push_event("Press [M] to make it worse.")
        self.hud.push_event("Press [G] to ask why (pointless).")

        while self._running:
            dt = self.clock.tick(60) / 1000.0
            dt = min(dt, 0.05)

            if self._show_report:
                self._handle_report_input()
                self._draw_report()
                continue

            self._handle_input()
            if not self._running:
                break
            self._simulate(dt)
            self._render()

        pygame.quit()


def main():
    seed = SEED
    env_seed = os.environ.get("BLOON_SEED")
    if env_seed:
        try:
            seed = int(env_seed)
        except ValueError:
            pass
    game = BloonAirspace(seed=seed)
    game.run()


if __name__ == "__main__":
    main()