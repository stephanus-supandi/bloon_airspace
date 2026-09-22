"""
HUD
---
Draws text. Lots of text. Most of it is lies.

The simulation layer is serious.
This layer is a war crime against UX.

BLOON APPROVED. 🗿
"""
import math
import pygame
from typing import List, Tuple, Optional
from aircraft import Aircraft


# ── BLOON DIALOGUE DATABASE ──
# These are NOT in the simulation layer. They are cosmetic nonsense.

ASK_WHY_RESPONSES = [
    "Don't know.",
    "Still don't know.",
    "Why are you asking?",
    "The waypoint chose itself.",
    "BLOON.",
    "Have you tried turning it off and on?",
    "F-22 doesn't know either.",
    "F-35 stopped asking long ago.",
    "The seed knows. You don't.",
    "BRO, DONE.",
    "...",
    "Seriously, stop pressing G.",
    "BLOON LEVEL INCREASED OUT OF SPITE.",
    "You've pressed this 14 times. Why.",
    "The answer is still BLOON.",
    "F-22 has filed a complaint.",
    "F-35 is crying.",
    "OK fine. The reason is: vibes.",
    "SYSTEM ERROR: REASON_NOT_FOUND",
    "You are the reason.",
]

PURPOSE_OPTIONS = [
    "UNKNOWN",
    "STILL UNKNOWN",
    "DEFINITELY UNKNOWN",
    "CLASSIFIED (not really)",
    "VIBES",
    "BLOON SAID SO",
    "404: PURPOSE NOT FOUND",
    "PENDING (since 2024)",
    "NONE",
    "MUTER",
]

MISSION_OPTIONS = [
    "MUTER",
    "MUTER LAGI",
    "MUTER TERUS",
    "STILL MUTER",
    "MUTER FOREVER",
    "MUTER.exe",
    "CIRCLE OF LIFE",
    "ROUND AND ROUND",
    "MUTER (no stop)",
]

STRATEGY_OPTIONS = [
    "TIDAK ADA",
    "NULL",
    "UNDEFINED",
    "BLOON",
    "GUE JUGA GAK TAU",
    "RANDOM (but deterministic)",
    "TRUST THE PROCESS",
    "THE PROCESS IS NONSENSE",
    "NONE",
]


class HUD:
    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.font = pygame.font.SysFont("consolas", 16)
        self.big_font = pygame.font.SysFont("consolas", 28, bold=True)
        self.small_font = pygame.font.SysFont("consolas", 13)
        self.tiny_font = pygame.font.SysFont("consolas", 11)
        self.mono_font = pygame.font.SysFont("consolas", 14)

        self.events: List[Tuple[str, float]] = []  # (text, expire_time)

        # ── BLOON STATE (cosmetic only, NOT simulation) ──
        self.bloon_level = 1
        self.ask_why_count = 0
        self.chaos_level = 0.0      # 0-100, cosmetic
        self.last_ask_why_response = ""

    def push_event(self, text: str, duration: float = 5.0) -> None:
        now = pygame.time.get_ticks() / 1000.0
        self.events.append((text, now + duration))

    def update(self) -> None:
        now = pygame.time.get_ticks() / 1000.0
        self.events = [(t, e) for t, e in self.events if e > now]

    # ── BLOON COSMETIC CALCULATIONS ──
    # These use math.sin/cos on sim_time for fluctuation.
    # They are PURELY VISUAL. They do NOT affect aircraft state.

    def _f22_brain(self, sim_time: float) -> int:
        """F-22 brain percentage. Starts ~72%, degrades with bloon_level."""
        base = max(5, 72 - self.bloon_level * 2)
        fluctuation = math.sin(sim_time * 0.7) * 5
        return max(1, min(100, int(base + fluctuation)))

    def _f35_brain(self, sim_time: float) -> int:
        """F-35 brain percentage. Starts ~31%, barely functional."""
        base = max(3, 31 - self.bloon_level * 1)
        fluctuation = math.cos(sim_time * 0.5) * 3
        return max(1, min(100, int(base + fluctuation)))

    def _system_intelligence(self) -> int:
        """Always 100%. The ENGINE is serious. The HUD is not."""
        return 100

    def _chaos_display(self, sim_time: float) -> int:
        """Cosmetic chaos percentage."""
        base = min(99, self.chaos_level + self.bloon_level * 3)
        fluctuation = math.sin(sim_time * 1.3) * 4
        return max(0, min(99, int(base + fluctuation)))

    # ── DRAWING ──

    def draw(
        self,
        f22: Aircraft,
        f35: Aircraft,
        mode: str,
        selected: str,
        show_trail: bool,
        sim_time: float,
        seed: int,
        replay_speed: float = 1.0,
        replay_playing: bool = False,
        replay_index: int = 0,
        replay_total: int = 0,
    ) -> None:
        w, h = self.screen.get_size()

        # ═══════════════════════════════════════════
        # TOP TITLE BAR
        # ═══════════════════════════════════════════
        title = self.big_font.render("BLOON AIRSPACE", True, (255, 255, 255))
        self.screen.blit(title, (20, 8))
        sub = self.tiny_font.render(
            "A Completely Unnecessary Aircraft Simulation by Solitude Labs",
            True, (140, 145, 165),
        )
        self.screen.blit(sub, (20, 40))

        # BLOON LEVEL badge (top center)
        bloon_txt = self.font.render(
            f"BLOON LEVEL: {self.bloon_level}", True, (255, 100, 100)
        )
        self.screen.blit(bloon_txt, (w // 2 - bloon_txt.get_width() // 2, 12))

        # Mode badge (top right area, above brain panel)
        mode_colors = {
            "FREE": (120, 220, 120),
            "AUTO": (120, 180, 255),
            "CHAOS": (255, 80, 80),
            "REPLAY": (220, 180, 255),
        }
        color = mode_colors.get(mode, (200, 200, 200))
        mode_text = self.font.render(f"MODE: {mode}", True, color)
        self.screen.blit(mode_text, (w - 220, 12))

        # Seed display
        seed_txt = self.tiny_font.render(f"SEED: {seed}", True, (100, 110, 130))
        self.screen.blit(seed_txt, (w - 220, 34))

        # ═══════════════════════════════════════════
        # BRAIN STATUS PANEL (top-right overlay)
        # ═══════════════════════════════════════════
        self._draw_brain_panel(w, sim_time)

        # ═══════════════════════════════════════════
        # PURPOSE / MISSION / STRATEGY (left side)
        # ═══════════════════════════════════════════
        self._draw_status_oneliners(sim_time)

        # ═══════════════════════════════════════════
        # BOTTOM INFO PANEL
        # ═══════════════════════════════════════════
        panel_y = h - 190
        pygame.draw.rect(self.screen, (16, 20, 32), (0, panel_y, w, 190))
        pygame.draw.line(self.screen, (60, 70, 90), (0, panel_y), (w, panel_y), 2)

        self._draw_aircraft_info(f22, 20, panel_y + 8, selected == "F-22", sim_time)
        self._draw_aircraft_info(f35, w // 2 + 20, panel_y + 8, selected == "F-35", sim_time)

        # ── Waypoint Reason (bottom center) ──
        self._draw_waypoint_reason(w // 2 - 120, panel_y + 90)

        # ── Controls hint ──
        hints = [
            "[1] FREE  [2] AUTO  [3] CHAOS  [4] REPLAY  [R] RESET",
            "[T] TRAIL  [C] CLEAR  [Q/E] SELECT  [G] ASK WHY  [M] MAKE IT WORSE  [ESC] REPORT",
        ]
        for i, line in enumerate(hints):
            t = self.tiny_font.render(line, True, (110, 120, 140))
            self.screen.blit(t, (20, panel_y + 148 + i * 14))

        # ── ASK WHY response ──
        if self.last_ask_why_response:
            ask_surf = self.font.render(
                f"SYSTEM: {self.last_ask_why_response}", True, (255, 200, 100)
            )
            self.screen.blit(ask_surf, (20, panel_y + 120))

        # ═══════════════════════════════════════════
        # REPLAY BAR
        # ═══════════════════════════════════════════
        if mode == "REPLAY" and replay_total > 0:
            bar_y = panel_y - 30
            pygame.draw.rect(self.screen, (40, 45, 60), (20, bar_y, w - 40, 14))
            frac = replay_index / max(1, replay_total - 1)
            pygame.draw.rect(
                self.screen, (180, 140, 255), (20, bar_y, int((w - 40) * frac), 14)
            )
            state = "PLAYING" if replay_playing else "PAUSED"
            lbl = self.tiny_font.render(
                f"REPLAY: {state}  x{replay_speed:.1f}   {replay_index}/{replay_total}",
                True, (200, 180, 240),
            )
            self.screen.blit(lbl, (20, bar_y - 16))

        # ═══════════════════════════════════════════
        # BLOON EVENT LOG (right side, stacked)
        # ═══════════════════════════════════════════
        ex = w - 420
        ey = 170
        for text, _ in self.events[-8:]:
            surf = self.small_font.render(text, True, (255, 230, 140))
            self.screen.blit(surf, (ex, ey))
            ey += 17

        # ── Trail indicator ──
        trail_txt = self.tiny_font.render(
            f"TRAIL: {'ON' if show_trail else 'OFF'}", True, (150, 170, 150)
        )
        self.screen.blit(trail_txt, (w - 220, 50))

    # ── SUB-DRAW METHODS ──

    def _draw_brain_panel(self, w: int, sim_time: float) -> None:
        """The most important panel in the entire application."""
        px = w - 260
        py = 68
        pw = 245
        ph = 120

        # Background
        pygame.draw.rect(self.screen, (20, 24, 38), (px, py, pw, ph))
        pygame.draw.rect(self.screen, (70, 80, 100), (px, py, pw, ph), 1)

        # Title
        title = self.small_font.render("🧠 BRAIN STATUS", True, (255, 220, 140))
        self.screen.blit(title, (px + 8, py + 4))

        # F-22 brain bar
        f22_brain = self._f22_brain(sim_time)
        self._draw_progress_bar(
            px + 8, py + 24, pw - 16, 14,
            f22_brain, (80, 180, 255),
            f"F-22   {f22_brain}%"
        )

        # F-35 brain bar
        f35_brain = self._f35_brain(sim_time)
        self._draw_progress_bar(
            px + 8, py + 44, pw - 16, 14,
            f35_brain, (255, 160, 80),
            f"F-35   {f35_brain}%"
        )

        # System intelligence (always 100%)
        sys_int = self._system_intelligence()
        self._draw_progress_bar(
            px + 8, py + 68, pw - 16, 14,
            sys_int, (120, 255, 120),
            f"SYSTEM {sys_int}%"
        )

        # Result
        result = self.tiny_font.render(
            "RESULT: TIDAK MEMBANTU", True, (255, 100, 100)
        )
        self.screen.blit(result, (px + 8, py + 92))

        # Chaos level
        chaos = self._chaos_display(sim_time)
        chaos_txt = self.tiny_font.render(
            f"CHAOS LEVEL: {chaos}%", True, (255, 140, 140)
        )
        self.screen.blit(chaos_txt, (px + 8, py + 106))

    def _draw_progress_bar(
        self, x: int, y: int, w: int, h: int,
        percent: int, color: Tuple[int, int, int], label: str
    ) -> None:
        """Draw a filled progress bar with label."""
        # Background
        pygame.draw.rect(self.screen, (40, 45, 60), (x, y, w, h))
        # Fill
        fill_w = int(w * max(0, min(100, percent)) / 100)
        pygame.draw.rect(self.screen, color, (x, y, fill_w, h))
        # Border
        pygame.draw.rect(self.screen, (80, 90, 110), (x, y, w, h), 1)
        # Label
        lbl = self.tiny_font.render(label, True, (255, 255, 255))
        self.screen.blit(lbl, (x + 4, y + 1))

    def _draw_status_oneliners(self, sim_time: float) -> None:
        """Left-side status: PURPOSE, MISSION, STRATEGY, BRAIN."""
        x = 20
        y = 68

        # Cycle through options based on sim_time (deterministic-ish)
        p_idx = int(sim_time * 0.1) % len(PURPOSE_OPTIONS)
        m_idx = int(sim_time * 0.08) % len(MISSION_OPTIONS)
        s_idx = int(sim_time * 0.06) % len(STRATEGY_OPTIONS)

        lines = [
            ("PURPOSE:", PURPOSE_OPTIONS[p_idx], (255, 180, 100)),
            ("MISSION:", MISSION_OPTIONS[m_idx], (180, 200, 255)),
            ("STRATEGY:", STRATEGY_OPTIONS[s_idx], (255, 140, 140)),
            ("BRAIN:", "OPTIONAL", (200, 200, 200)),
            ("OTAK PILOT:", "LOADING...", (180, 180, 100)),
        ]

        for label, value, color in lines:
            lbl_surf = self.tiny_font.render(label, True, (140, 150, 170))
            val_surf = self.tiny_font.render(f" {value}", True, color)
            self.screen.blit(lbl_surf, (x, y))
            self.screen.blit(val_surf, (x + lbl_surf.get_width(), y))
            y += 16

    def _draw_waypoint_reason(self, x: int, y: int) -> None:
        """Checkbox list for why the waypoint was selected."""
        title = self.tiny_font.render("REASON FOR WAYPOINT:", True, (160, 170, 190))
        self.screen.blit(title, (x, y))

        reasons = [
            ("Strategic", False),
            ("Scientific", False),
            ("Navigation", False),
            ("BLOON", True),  # Always BLOON.
        ]

        for i, (reason, checked) in enumerate(reasons):
            ry = y + 16 + i * 14
            box = "[x]" if checked else "[ ]"
            color = (255, 220, 100) if checked else (100, 110, 130)
            txt = self.tiny_font.render(f"{box} {reason}", True, color)
            self.screen.blit(txt, (x + 4, ry))

    def _draw_aircraft_info(
        self, ac: Aircraft, x: int, y: int, selected: bool, sim_time: float
    ) -> None:
        """Aircraft info panel with BLOON additions."""
        color = ac.color if selected else (160, 160, 160)
        header = self.font.render(
            f"{'▶ ' if selected else '  '}{ac.state.aircraft_id}  ({ac.state.aircraft_type})",
            True, color,
        )
        self.screen.blit(header, (x, y))

        s = ac.state
        wp_name = s.current_waypoint.name if s.current_waypoint else "---"
        dist = f"{ac.distance_to_waypoint():.0f}" if s.current_waypoint else "---"

        # Brain status for this aircraft
        if ac.state.aircraft_id == "F-22":
            brain = self._f22_brain(sim_time)
        else:
            brain = self._f35_brain(sim_time)

        lines = [
            f"ALT: {s.altitude:,.0f}     SPEED: {s.speed:.0f}     HDG: {s.heading:03.0f}°",
            f"WAYPOINT: {wp_name:<12}   DIST: {dist}",
            f"DIST: {s.distance_traveled:,.0f}   VISITED: {s.waypoints_visited}   BRAIN: {brain}%",
        ]

        # BLOON STATUS line
        if brain > 50:
            bloon_status = "MASIH MUTER (aware)"
        elif brain > 20:
            bloon_status = "MASIH MUTER (confused)"
        else:
            bloon_status = "MASIH MUTER (unconscious)"

        lines.append(f"BLOON STATUS: {bloon_status}")

        for i, line in enumerate(lines):
            t = self.tiny_font.render(line, True, (200, 205, 215))
            self.screen.blit(t, (x + 4, y + 22 + i * 14))