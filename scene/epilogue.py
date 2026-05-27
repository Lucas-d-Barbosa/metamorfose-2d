"""
Epílogo — O Dia Depois.

Sequência de telas claras (dia ensolarado) com os diálogos finais da família.
Transita para o menu ao fim.
"""

import pygame

from scene.base_scene import BaseScene
from settings import SCREEN_HEIGHT, SCREEN_WIDTH

_SCREENS = [
    # (background_color, lines)
    (
        (245, 235, 200),
        [
            ("", "— Manhã de primavera. O sol entra pela janela. —"),
            ("Pai",   "Foi um dia difícil, mas vejam como o sol está lindo hoje."),
        ],
    ),
    (
        (240, 232, 210),
        [
            ("Mãe",  "Sim. Acho que podemos nos mudar para um apartamento menor,"),
            ("Mãe",  "mais barato e mais ensolarado agora."),
        ],
    ),
    (
        (235, 228, 215),
        [
            ("Pai",  "E olhem para a nossa Grete. Apesar de tudo…"),
            ("Pai",  "nossa filha desabrochou e se tornou uma bela mulher."),
            ("Pai",  "Logo teremos que arranjar um bom marido para ela."),
        ],
    ),
    (
        (20, 20, 20),
        [
            ("", "FIM."),
        ],
    ),
]

_LINE_INTERVAL = 3.5   # seconds between lines within a screen
_SCREEN_HOLD   = 1.2   # extra seconds after last line before auto-advance


class EpilogueScene(BaseScene):
    def __init__(self, game) -> None:
        super().__init__(game)
        self._screen_idx = 0
        self._line_idx = 0
        self._line_timer = 0.0
        self._hold_timer = 0.0
        self._all_lines_shown = False
        self._done = False

        self._serif = pygame.font.SysFont("serif", 22)
        self._small = pygame.font.SysFont("monospace", 12)
        self._label = pygame.font.SysFont("monospace", 13)
        self._lines_rendered: list[tuple[str, str]] = []

    # ------------------------------------------------------------------

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type != pygame.KEYDOWN:
            return
        if self._done:
            if event.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_ESCAPE):
                self.transition_to("menu")
            return
        # Skip current screen
        if event.key in (pygame.K_RETURN, pygame.K_SPACE):
            self._advance_screen()

    def _advance_screen(self) -> None:
        self._screen_idx += 1
        if self._screen_idx >= len(_SCREENS):
            self._done = True
            return
        self._line_idx = 0
        self._line_timer = 0.0
        self._hold_timer = 0.0
        self._all_lines_shown = False
        self._lines_rendered = []

    def update(self, dt: float) -> None:
        if self._done:
            return

        _, lines = _SCREENS[self._screen_idx]

        if self._all_lines_shown:
            self._hold_timer += dt
            if self._hold_timer >= _SCREEN_HOLD:
                self._advance_screen()
            return

        self._line_timer += dt
        if self._line_timer >= _LINE_INTERVAL:
            self._line_timer = 0.0
            if self._line_idx < len(lines):
                self._lines_rendered.append(lines[self._line_idx])
                self._line_idx += 1
                if self._line_idx >= len(lines):
                    self._all_lines_shown = True

    def draw(self, surface: pygame.Surface) -> None:
        if self._done:
            surface.fill((10, 10, 10))
            hint = self._small.render("[ ENTER ] Voltar ao Menu", True, (60, 60, 60))
            surface.blit(hint, hint.get_rect(
                centerx=SCREEN_WIDTH // 2, centery=SCREEN_HEIGHT // 2))
            return

        bg_color, _ = _SCREENS[self._screen_idx]
        surface.fill(bg_color)

        # Determine text color from background brightness
        brightness = sum(bg_color) / 3
        text_color = (30, 25, 20) if brightness > 128 else (220, 215, 200)
        label_color = (80, 60, 40) if brightness > 128 else (160, 140, 120)

        cx = SCREEN_WIDTH // 2
        start_y = SCREEN_HEIGHT // 2 - len(self._lines_rendered) * 22

        for i, (speaker, text) in enumerate(self._lines_rendered):
            y = start_y + i * 44
            if speaker:
                lbl = self._label.render(speaker.upper(), True, label_color)
                surface.blit(lbl, lbl.get_rect(centerx=cx, centery=y - 12))
            surf = self._serif.render(text, True, text_color)
            surface.blit(surf, surf.get_rect(centerx=cx, centery=y + 10))

        # Screen counter
        ctr = self._small.render(
            f"{self._screen_idx + 1}/{len(_SCREENS)}", True,
            (100, 90, 70) if brightness > 128 else (60, 60, 60))
        surface.blit(ctr, (SCREEN_WIDTH - 50, SCREEN_HEIGHT - 20))

        # Skip hint
        hint = self._small.render(
            "[ ENTER ] Avançar", True,
            (120, 110, 90) if brightness > 128 else (60, 60, 60))
        surface.blit(hint, hint.get_rect(
            centerx=cx, centery=SCREEN_HEIGHT - 25))
