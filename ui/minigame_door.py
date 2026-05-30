"""
Minigame: Destrancar a porta com a boca.

Timing bar with a bouncing cursor. Player presses E when the cursor
is inside the green zone. Needs SUCCESSES_NEEDED hits to unlock.
Cursor speeds up with each attempt (represents increasing desperation).
"""

import math

import pygame

from settings import SCREEN_HEIGHT, SCREEN_WIDTH


class DoorMinigame:
    BAR_W = 320
    BAR_H = 32
    BASE_SPEED = 110.0       # slow cursor — easy to time
    SPEED_RAMP = 5.0         # barely speeds up between attempts
    GREEN_ZONE_W = 130       # ~40 % of the bar — hard to miss
    SUCCESSES_NEEDED = 2     # only 2 hits needed
    MAX_MISSES = 8           # very forgiving

    def __init__(self) -> None:
        self.active = False
        self.result: str | None = None  # None | "success" | "fail"
        self.successes = 0
        self._misses = 0
        self._total_attempts = 0
        self._cursor = 0.0
        self._dir = 1
        self._green_x = (self.BAR_W - self.GREEN_ZONE_W) // 2
        self._miss_shake = 0.0
        self._hit_flash = 0.0

    # -------------------------------------------------------------------------

    def start(self) -> None:
        self.__init__()
        self.active = True

    def update(self, dt: float) -> None:
        if not self.active:
            return
        speed = self.BASE_SPEED + self._total_attempts * self.SPEED_RAMP
        self._cursor += self._dir * speed * dt
        if self._cursor >= self.BAR_W:
            self._cursor = self.BAR_W
            self._dir = -1
        elif self._cursor <= 0:
            self._cursor = 0
            self._dir = 1
        self._miss_shake = max(0.0, self._miss_shake - dt * 4)
        self._hit_flash = max(0.0, self._hit_flash - dt * 3)

    def attempt(self) -> str:
        """
        Returns: 'hit' | 'miss' | 'unlock' | 'exhausted'
        """
        if not self.active or self.result:
            return ""
        self._total_attempts += 1
        in_green = self._green_x <= self._cursor <= self._green_x + self.GREEN_ZONE_W

        if in_green:
            self.successes += 1
            self._hit_flash = 1.0
            if self.successes >= self.SUCCESSES_NEEDED:
                self.result = "success"
                self.active = False
                return "unlock"
            return "hit"
        else:
            self._misses += 1
            self._miss_shake = 1.0
            if self._misses >= self.MAX_MISSES:
                self.result = "fail"
                self.active = False
                return "exhausted"
            return "miss"

    def cancel(self) -> None:
        self.active = False
        self.result = "cancelled"

    # -------------------------------------------------------------------------

    def draw(self, surface: pygame.Surface) -> None:
        W, H = SCREEN_WIDTH, SCREEN_HEIGHT
        cx, cy = W // 2, H // 2

        # Semi-transparent backdrop
        overlay = pygame.Surface((W, H), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 170))
        surface.blit(overlay, (0, 0))

        shake = int(math.sin(self._miss_shake * 60) * 5 * self._miss_shake)

        # ---- Title ----
        title_font = pygame.font.SysFont("serif", 26)
        title = title_font.render("DESTRANCAR A PORTA", True, (200, 155, 70))
        surface.blit(title, title.get_rect(centerx=cx + shake, centery=cy - 90))

        # ---- Thought ----
        thought_font = pygame.font.SysFont("serif", 15)
        thought = thought_font.render(
            '"Preciso me virar… tentar girar com a boca…"',
            True, (150, 150, 195),
        )
        surface.blit(thought, thought.get_rect(centerx=cx, centery=cy - 58))

        # ---- Success dots ----
        dot_r = 10
        total_w = self.SUCCESSES_NEEDED * (dot_r * 2 + 8)
        for i in range(self.SUCCESSES_NEEDED):
            dot_x = cx - total_w // 2 + i * (dot_r * 2 + 8) + dot_r + shake
            dot_y = cy - 30
            filled = i < self.successes
            color = (70, 215, 100) if filled else (45, 45, 45)
            pygame.draw.circle(surface, color, (dot_x, dot_y), dot_r)
            pygame.draw.circle(surface, (190, 190, 190), (dot_x, dot_y), dot_r, 1)

        # ---- Bar ----
        bx = cx - self.BAR_W // 2 + shake
        by = cy

        pygame.draw.rect(surface, (35, 35, 35), (bx, by, self.BAR_W, self.BAR_H))

        # Green zone
        green_r = min(255, int(60 + 190 * self._hit_flash))
        green_g = min(255, int(185 + 70 * self._hit_flash))
        green_b = min(255, int(80 + 170 * self._hit_flash))
        pygame.draw.rect(surface, (green_r, green_g, green_b),
                         (bx + self._green_x, by, self.GREEN_ZONE_W, self.BAR_H))

        # Cursor
        cur_x = bx + int(self._cursor)
        cur_col = (255, 70, 70) if self._miss_shake > 0.1 else (240, 240, 240)
        pygame.draw.rect(surface, cur_col, (cur_x - 3, by - 4, 6, self.BAR_H + 8))

        # Bar border
        pygame.draw.rect(surface, (160, 160, 160), (bx, by, self.BAR_W, self.BAR_H), 1)

        # ---- Hint ----
        hint_font = pygame.font.SysFont("monospace", 11)
        hint = hint_font.render(
            "[ E ] Tentar quando estiver no verde     [ ESC ] Desistir",
            True, (90, 90, 90),
        )
        surface.blit(hint, hint.get_rect(centerx=cx, centery=by + self.BAR_H + 18))

        # ---- Miss feedback ----
        if self._miss_shake > 0.5:
            miss_surf = hint_font.render("Errou!", True, (220, 80, 60))
            surface.blit(miss_surf, miss_surf.get_rect(centerx=cx, centery=by - 14))
