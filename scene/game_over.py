import pygame

from scene.base_scene import BaseScene
from settings import DARK_GRAY, RED, SCREEN_HEIGHT, SCREEN_WIDTH, WHITE

# Grete's sentence — the narrative game over
_SENTENCE = [
    '"Não posso pronunciar o nome do meu irmão',
    ' na frente desse monstro."',
    "",
    "Nós tentamos cuidar. Tentamos suportar.",
    "Mas precisamos nos livrar dele.",
    "",
    "— Grete Samsa",
]


class GameOverScene(BaseScene):
    def __init__(self, game) -> None:
        super().__init__(game)
        self._font = pygame.font.SysFont("serif", 22)
        self._hint_font = pygame.font.SysFont("monospace", 14)
        self._reveal_timer = 0.0
        self._lines_revealed = 0
        self._done = False

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN:
            if self._done:
                if event.key == pygame.K_r:
                    self.transition_to("phase1")
                elif event.key == pygame.K_ESCAPE:
                    self.transition_to("menu")
            else:
                # Skip to full reveal
                self._lines_revealed = len(_SENTENCE)
                self._done = True

    def update(self, dt: float) -> None:
        if self._done:
            return
        self._reveal_timer += dt
        if self._reveal_timer >= 0.8 and self._lines_revealed < len(_SENTENCE):
            self._reveal_timer = 0.0
            self._lines_revealed += 1
            if self._lines_revealed == len(_SENTENCE):
                self._done = True

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill(DARK_GRAY)

        start_y = SCREEN_HEIGHT // 2 - len(_SENTENCE) * 16
        for i, line in enumerate(_SENTENCE[:self._lines_revealed]):
            color = RED if i == 0 else WHITE
            rendered = self._font.render(line, True, color)
            surface.blit(rendered, rendered.get_rect(centerx=SCREEN_WIDTH // 2, y=start_y + i * 34))

        if self._done:
            hint = self._hint_font.render("R — Reiniciar   ESC — Menu", True, (80, 80, 80))
            surface.blit(hint, hint.get_rect(centerx=SCREEN_WIDTH // 2, y=SCREEN_HEIGHT - 40))
