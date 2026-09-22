"""
CONTROLS
--------
Keyboard input. Translates to intent.
Now includes two buttons that do absolutely nothing useful.
"""
import pygame


class Controls:
    """Maps pygame events to game intents."""

    def __init__(self):
        self.quit_requested = False
        self.speed_up = False
        self.speed_down = False
        self.turn_left = False
        self.turn_right = False
        self.climb = False
        self.descend = False

        self.mode_free = False
        self.mode_auto = False
        self.mode_chaos = False
        self.mode_replay = False
        self.reset_requested = False

        self.toggle_trail = False
        self.clear_trail = False

        self.replay_play = False
        self.replay_pause = False
        self.replay_rewind = False
        self.replay_ff = False

        self.select_f22 = False
        self.select_f35 = False

        self.show_report = False

        # ── BLOON LAYER ──
        self.ask_why = False        # [G]
        self.make_worse = False     # [M]

    def poll(self) -> None:
        """Reset per-frame intents."""
        self.quit_requested = False
        self.speed_up = False
        self.speed_down = False
        self.turn_left = False
        self.turn_right = False
        self.climb = False
        self.descend = False

        self.mode_free = False
        self.mode_auto = False
        self.mode_chaos = False
        self.mode_replay = False
        self.reset_requested = False

        self.toggle_trail = False
        self.clear_trail = False

        self.replay_play = False
        self.replay_pause = False
        self.replay_rewind = False
        self.replay_ff = False

        self.select_f22 = False
        self.select_f35 = False

        self.show_report = False

        # ── BLOON LAYER ──
        self.ask_why = False
        self.make_worse = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit_requested = True
            elif event.type == pygame.KEYDOWN:
                self._handle_key(event.key)

    def _handle_key(self, key: int) -> None:
        # Movement
        if key == pygame.K_UP:     self.speed_up = True
        if key == pygame.K_DOWN:   self.speed_down = True
        if key == pygame.K_LEFT:   self.turn_left = True
        if key == pygame.K_RIGHT:  self.turn_right = True
        if key == pygame.K_w:      self.climb = True
        if key == pygame.K_s:      self.descend = True

        # Modes
        if key == pygame.K_1:      self.mode_free = True
        if key == pygame.K_2:      self.mode_auto = True
        if key == pygame.K_3:      self.mode_chaos = True
        if key == pygame.K_4:      self.mode_replay = True
        if key == pygame.K_r:      self.reset_requested = True

        # Trails
        if key == pygame.K_t:      self.toggle_trail = True
        if key == pygame.K_c:      self.clear_trail = True

        # Replay
        if key == pygame.K_SPACE:  self.replay_play = True
        if key == pygame.K_p:      self.replay_pause = True
        if key == pygame.K_b:      self.replay_rewind = True
        if key == pygame.K_f:      self.replay_ff = True

        # Selection
        if key == pygame.K_q:      self.select_f22 = True
        if key == pygame.K_e:      self.select_f35 = True

        # Report
        if key == pygame.K_ESCAPE: self.show_report = True

        # ── BLOON LAYER ──
        if key == pygame.K_g:      self.ask_why = True
        if key == pygame.K_m:      self.make_worse = True