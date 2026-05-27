import pygame

from scene.base_scene import BaseScene
from settings import DARK_GRAY, RED, SCREEN_HEIGHT, SCREEN_WIDTH, WHITE

# Used when reaching Game Over before Phase 4 (e.g., early exits / debug)
_LINES = [
    ("Grete",  '"Não posso pronunciar o nome do meu irmão na frente desse monstro."'),
    ("",        ""),
    ("",        "Nós tentamos cuidar. Tentamos suportar."),
    ("",        "Mas precisamos nos livrar dele."),
    ("",        ""),
    ("Gregor",  '"Ela tem razão. Minhas dores estão passando…"'),
    ("Gregor",  '"Que a escuridão leve tudo logo…"'),
    ("",        ""),
    ("",        "— FIM —"),
]

_REVEAL_INTERVAL = 0.9   # seconds between lines


class GameOverScene(BaseScene):
    def __init__(self, game) -> None:
        super().__init__(game)
        self._serif  = pygame.font.SysFont("serif", 22)
        self._mono   = pygame.font.SysFont("monospace", 13)
        self._hint   = pygame.font.SysFont("monospace", 14)
        self._timer  = 0.0
        self._revealed = 0
        self._done = False

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type != pygame.KEYDOWN:
            return
        if self._done:
            if event.key == pygame.K_r:
                self.transition_to("phase1")
            elif event.key == pygame.K_ESCAPE:
                self.transition_to("menu")
        else:
            # Skip to full reveal
            self._revealed = len(_LINES)
            self._done = True

    def update(self, dt: float) -> None:
        if self._done:
            return
        self._timer += dt
        if self._timer >= _REVEAL_INTERVAL and self._revealed < len(_LINES):
            self._timer = 0.0
            self._revealed += 1
            if self._revealed >= len(_LINES):
                self._done = True

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill(DARK_GRAY)

        line_h = 36
        total_h = len(_LINES) * line_h
        start_y = SCREEN_HEIGHT // 2 - total_h // 2

        for i, (speaker, text) in enumerate(_LINES[:self._revealed]):
            y = start_y + i * line_h
            if speaker == "Grete":
                color = RED
                rendered = self._serif.render(text, True, color)
            elif speaker == "Gregor":
                color = (180, 200, 240)
                rendered = self._serif.render(text, True, color)
            else:
                rendered = self._serif.render(text, True, (90, 90, 90))
            surface.blit(rendered, rendered.get_rect(
                centerx=SCREEN_WIDTH // 2, centery=y))

            if speaker and speaker not in ("",):
                lbl = self._mono.render(speaker.upper(), True, (60, 60, 60))
                surface.blit(lbl, lbl.get_rect(
                    centerx=SCREEN_WIDTH // 2, centery=y - 14))

        if self._done:
            hint = self._hint.render(
                "R — Reiniciar   ESC — Menu", True, (60, 60, 60))
            surface.blit(hint, hint.get_rect(
                centerx=SCREEN_WIDTH // 2, centery=SCREEN_HEIGHT - 35))
