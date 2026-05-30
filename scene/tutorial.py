"""
scene/tutorial.py

Tutorial de controles e mecânicas — exibido antes da Fase 1.
3 páginas: Controles  /  Stealth  /  Objetivos por fase.

Fluxo: intro_cutscene → tutorial → phase1
"""

import pygame

from scene.base_scene import BaseScene
from settings import SCREEN_HEIGHT, SCREEN_WIDTH

_BG = (5, 5, 8)

# Cada página: (título, [(tecla, descrição), ...])
_PAGES: list[tuple[str, list[tuple[str, str]]]] = [
    (
        "CONTROLES",
        [
            ("WASD",       "Mover Gregor pelo apartamento"),
            ("C",          "Alternar entre chão e teto"),
            ("E",          "Interagir — comer alimentos / destrancar portas"),
            ("F",          "Falar (emite barulho — NPCs podem ouvir)"),
            ("ESC",        "Salvar e voltar ao menu"),
            ("F3",         "Debug — exibe cones de visão e raios de som"),
        ],
    ),
    (
        "MECÂNICAS DE STEALTH",
        [
            ("CAMPO DE VISÃO", "NPCs têm cones coloridos — fique fora deles"),
            ("BARULHO",        "Movimentos emitem som — corra menos"),
            ("ESCONDERIJOS",   "Zonas escuras ocultam Gregor completamente"),
            ("TETO",           "Teto esconde, mas consome stamina mais rápido"),
            ("ALERTA",         "Barra vermelha acima do NPC = ele te viu"),
            ("MAÇÃ",           "Ser acertado pela maçã do Pai é permanente"),
        ],
    ),
    (
        "OBJETIVOS",
        [
            ("FASE 1", "Saia do quarto sem ser visto pelo Gerente"),
            ("FASE 2", "Busque comida pela casa durante a noite"),
            ("FASE 3", "Sobreviva enquanto o apartamento se deteriora"),
            ("FASE 4", "Ouça o violino de Grete pela última vez"),
            ("",       ""),
            ("ENTER",  "Começar o jogo — boa sorte, Gregor."),
        ],
    ),
]

_TITLE_COLOR  = (175, 138, 55)
_KEY_COLOR    = (160, 128, 68)
_DESC_COLOR   = (200, 194, 178)
_HINT_COLOR   = (55, 52, 44)
_LAST_COLOR   = (120, 108, 78)
_LINE_COLOR   = (58, 48, 32)


class TutorialScene(BaseScene):
    def __init__(self, game) -> None:
        super().__init__(game)
        self._page = 0
        self._title_font = pygame.font.SysFont("serif", 30)
        self._key_font   = pygame.font.SysFont("monospace", 13)
        self._desc_font  = pygame.font.SysFont("serif", 18)
        self._hint_font  = pygame.font.SysFont("monospace", 11)

    # ------------------------------------------------------------------

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type != pygame.KEYDOWN:
            return
        if event.key in (pygame.K_RETURN, pygame.K_SPACE):
            self._page += 1
            if self._page >= len(_PAGES):
                self.transition_to("phase1")
        elif event.key == pygame.K_ESCAPE:
            self.transition_to("phase1")

    def update(self, dt: float) -> None:
        pass

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill(_BG)
        title_text, items = _PAGES[self._page]
        cx = SCREEN_WIDTH // 2

        # Title
        ts = self._title_font.render(title_text, True, _TITLE_COLOR)
        surface.blit(ts, ts.get_rect(centerx=cx, centery=78))
        pygame.draw.line(surface, _LINE_COLOR,
                         (cx - 210, 106), (cx + 210, 106), 1)

        # Items
        start_y = 148
        row_h   = 50
        for i, (key, desc) in enumerate(items):
            y = start_y + i * row_h
            if key:
                ks = self._key_font.render(f"[ {key} ]", True, _KEY_COLOR)
                surface.blit(ks, ks.get_rect(right=cx - 18, centery=y))
            if desc:
                ds = self._desc_font.render(desc, True, _DESC_COLOR)
                surface.blit(ds, ds.get_rect(left=cx + 18, centery=y))

        # Navigation hint
        is_last = self._page == len(_PAGES) - 1
        if is_last:
            hint = self._hint_font.render(
                "[ ENTER ] Começar a jogar!", True, _LAST_COLOR)
        else:
            hint = self._hint_font.render(
                f"[ ENTER ] Próximo  |  [ ESC ] Pular  "
                f"({self._page + 1}/{len(_PAGES)})",
                True, _HINT_COLOR)
        surface.blit(hint, hint.get_rect(centerx=cx, centery=SCREEN_HEIGHT - 28))
