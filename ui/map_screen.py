"""
MAP SCREEN
----------
Renders the world: ocean, islands, trails, aircraft.
"""
import math
import pygame
from typing import Tuple, List

from world import IndonesiaMap
from aircraft import Aircraft


class MapScreen:
    """Transforms world coords -> screen coords and draws everything."""

    def __init__(
        self,
        screen: pygame.Surface,
        world_size: Tuple[float, float] = (2000.0, 1000.0),
    ):
        self.screen = screen
        self.world_size = world_size
        self._compute_transform()
        self.map = IndonesiaMap()

    def _compute_transform(self) -> None:
        sw, sh = self.screen.get_size()
        # Reserve bottom 160px for HUD, top 60 for title
        usable_h = sh - 220
        usable_w = sw - 40
        sx = usable_w / self.world_size[0]
        sy = usable_h / self.world_size[1]
        self.scale = min(sx, sy)
        # Center the world in the usable area
        drawn_w = self.world_size[0] * self.scale
        drawn_h = self.world_size[1] * self.scale
        self.offset_x = (sw - drawn_w) / 2
        self.offset_y = 60 + (usable_h - drawn_h) / 2

    def world_to_screen(self, pos: Tuple[float, float]) -> Tuple[int, int]:
        x = self.offset_x + pos[0] * self.scale
        # Flip y so north is up
        y = self.offset_y + (self.world_size[1] - pos[1]) * self.scale
        return int(x), int(y)

    def draw_background(self) -> None:
        # Deep ocean gradient (flat)
        self.screen.fill((14, 22, 40))

        # Subtle grid
        grid_color = (28, 38, 60)
        step = 100  # world units
        for wx in range(0, int(self.world_size[0]) + 1, step):
            x1, y1 = self.world_to_screen((wx, 0))
            x2, y2 = self.world_to_screen((wx, self.world_size[1]))
            pygame.draw.line(self.screen, grid_color, (x1, y1), (x2, y2), 1)
        for wy in range(0, int(self.world_size[1]) + 1, step):
            x1, y1 = self.world_to_screen((0, wy))
            x2, y2 = self.world_to_screen((self.world_size[0], wy))
            pygame.draw.line(self.screen, grid_color, (x1, y1), (x2, y2), 1)

    def draw_islands(self) -> None:
        for name, poly in self.map.all_polygons():
            pts = [self.world_to_screen(p) for p in poly]
            if len(pts) >= 3:
                # Fill
                pygame.draw.polygon(self.screen, (52, 90, 60), pts)
                # Outline
                pygame.draw.polygon(self.screen, (90, 140, 95), pts, 2)

                # Island label (only for big ones)
                if name in ("Sumatra", "Java", "Kalimantan", "Sulawesi", "Papua"):
                    cx = sum(p[0] for p in pts) / len(pts)
                    cy = sum(p[1] for p in pts) / len(pts)
                    font = pygame.font.SysFont("consolas", 12)
                    lbl = font.render(name.upper(), True, (170, 200, 170))
                    r = lbl.get_rect(center=(int(cx), int(cy)))
                    self.screen.blit(lbl, r)

    def draw_trail(self, aircraft: Aircraft, visible: bool) -> None:
        if not visible:
            return
        trail = aircraft.trail
        if len(trail) < 2:
            return
        # Draw as fading segments
        n = len(trail)
        for i in range(1, n):
            alpha = int(255 * (i / n))
            color = (
                min(255, aircraft.color[0]),
                min(255, aircraft.color[1]),
                min(255, aircraft.color[2]),
            )
            # pygame.draw.line doesn't do alpha on the main surface easily,
            # so we modulate brightness instead.
            factor = alpha / 255.0
            c = (int(color[0] * factor), int(color[1] * factor), int(color[2] * factor))
            p1 = self.world_to_screen(trail[i - 1])
            p2 = self.world_to_screen(trail[i])
            pygame.draw.line(self.screen, c, p1, p2, 2)

    def draw_aircraft(self, aircraft: Aircraft, selected: bool) -> None:
        sx, sy = self.world_to_screen(aircraft.state.position)
        heading_rad = math.radians(aircraft.state.heading)

        # Triangle pointing in heading direction (north = up = -y on screen)
        size = 12 if not selected else 14
        # Tip (forward)
        tip_dx = math.sin(heading_rad) * size
        tip_dy = -math.cos(heading_rad) * size  # screen y flipped
        tip = (sx + tip_dx, sy + tip_dy)

        # Left wing
        left_ang = heading_rad + math.radians(140)
        left_dx = math.sin(left_ang) * size * 0.8
        left_dy = -math.cos(left_ang) * size * 0.8
        left = (sx + left_dx, sy + left_dy)

        # Right wing
        right_ang = heading_rad - math.radians(140)
        right_dx = math.sin(right_ang) * size * 0.8
        right_dy = -math.cos(right_ang) * size * 0.8
        right = (sx + right_dx, sy + right_dy)

        # Selection ring
        if selected:
            pygame.draw.circle(self.screen, (255, 255, 255), (sx, sy), size + 6, 2)

        # Aircraft body
        pygame.draw.polygon(self.screen, aircraft.color, [tip, left, right])
        pygame.draw.polygon(self.screen, (255, 255, 255), [tip, left, right], 1)

        # ID label
        font = pygame.font.SysFont("consolas", 12, bold=True)
        lbl = font.render(aircraft.state.aircraft_id, True, aircraft.color)
        self.screen.blit(lbl, (sx + 14, sy - 8))