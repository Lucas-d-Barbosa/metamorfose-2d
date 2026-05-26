import pygame

from settings import AMBER, SCREEN_HEIGHT, SCREEN_WIDTH, WHITE


class _Balloon:
    def __init__(self, text: str, duration: float, color: tuple) -> None:
        self.text = text
        self.duration = duration
        self.elapsed = 0.0
        self.color = color

    @property
    def alive(self) -> bool:
        return self.elapsed < self.duration

    @property
    def alpha(self) -> int:
        fade_start = self.duration * 0.75
        if self.elapsed < fade_start:
            return 255
        progress = (self.elapsed - fade_start) / (self.duration - fade_start)
        return max(0, int(255 * (1 - progress)))


class DialogueSystem:
    """Handles Gregor's thought balloons and NPC dialogue captions."""

    _THOUGHT_FONT: pygame.font.Font | None = None
    _DIALOGUE_FONT: pygame.font.Font | None = None

    def __init__(self) -> None:
        self._thought: _Balloon | None = None
        self._dialogue_queue: list[_Balloon] = []

    @classmethod
    def _get_fonts(cls) -> tuple[pygame.font.Font, pygame.font.Font]:
        if cls._THOUGHT_FONT is None:
            cls._THOUGHT_FONT = pygame.font.SysFont("serif", 20)
            cls._DIALOGUE_FONT = pygame.font.SysFont("monospace", 16)
        return cls._THOUGHT_FONT, cls._DIALOGUE_FONT  # type: ignore[return-value]

    # -------------------------------------------------------------------------

    def show_thought(self, text: str, duration: float = 4.0,
                     color: tuple = AMBER) -> None:
        self._thought = _Balloon(text, duration, color)

    def show_dialogue(self, speaker: str, text: str, duration: float = 4.0) -> None:
        full = f"{speaker}: {text}" if speaker else text
        self._dialogue_queue.append(_Balloon(full, duration, WHITE))

    def handle_event(self, event: pygame.event.Event) -> None:
        pass  # reserved for skip-dialogue key

    def update(self, dt: float) -> None:
        if self._thought:
            self._thought.elapsed += dt
            if not self._thought.alive:
                self._thought = None

        if self._dialogue_queue:
            self._dialogue_queue[0].elapsed += dt
            if not self._dialogue_queue[0].alive:
                self._dialogue_queue.pop(0)

    # -------------------------------------------------------------------------

    def draw(self, surface: pygame.Surface) -> None:
        thought_font, dialogue_font = self._get_fonts()

        # Thought balloon — top of screen, centered, serifed
        if self._thought:
            self._draw_balloon(
                surface, self._thought, thought_font,
                y=18, italic=True,
            )

        # Dialogue caption — bottom of screen
        if self._dialogue_queue:
            balloon = self._dialogue_queue[0]
            self._draw_balloon(
                surface, balloon, dialogue_font,
                y=SCREEN_HEIGHT - 60, italic=False,
            )

    def _draw_balloon(self, surface: pygame.Surface, balloon: _Balloon,
                      font: pygame.font.Font, y: int, italic: bool) -> None:
        text_surf = font.render(balloon.text, True, balloon.color)
        text_surf.set_alpha(balloon.alpha)

        pad = 12
        bg_rect = pygame.Rect(
            SCREEN_WIDTH // 2 - text_surf.get_width() // 2 - pad,
            y - pad // 2,
            text_surf.get_width() + pad * 2,
            text_surf.get_height() + pad,
        )

        bg = pygame.Surface((bg_rect.width, bg_rect.height), pygame.SRCALPHA)
        bg.fill((0, 0, 0, int(balloon.alpha * 0.55)))
        surface.blit(bg, bg_rect.topleft)
        pygame.draw.rect(surface, (*balloon.color, balloon.alpha), bg_rect, 1)
        surface.blit(text_surf, (bg_rect.x + pad, bg_rect.y + pad // 2))
