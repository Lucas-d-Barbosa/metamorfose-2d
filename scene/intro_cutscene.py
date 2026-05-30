"""
scene/intro_cutscene.py

Cutscene de abertura — prólogo narrativo exibido após o menu,
antes do tutorial e da Fase 1.

Fluxo: menu → intro_cutscene → tutorial → phase1
"""

import pygame

from scene.base_scene import BaseScene
from settings import SCREEN_HEIGHT, SCREEN_WIDTH

_BG    = (4, 3, 6)
_SPEED = 36.0   # chars/sec

# speaker == "" → narrador (sem rótulo, cor mais suave)
_LINES: list[tuple[str, str]] = [
    ("", "Praga, início do século XX."),
    ("", "Ao acordar certa manhã depois de sonhos agitados,"),
    ("", "Gregor Samsa encontrou-se metamorfoseado num inseto monstruoso."),
    ("", "— Franz Kafka, A Metamorfose —"),
    ("Gregor", "O que aconteceu comigo? Não é um sonho…"),
    ("Gregor", "Preciso chegar ao trabalho. O trem das cinco…"),
    ("", "Mas as pernas não obedecem mais. São muitas. E estranhas."),
    ("", "O apartamento está silencioso. Por enquanto."),
]


class IntroCutsceneScene(BaseScene):
    def __init__(self, game) -> None:
        super().__init__(game)
        self._line:    int   = 0
        self._chars:   float = 0.0
        self._waiting: bool  = False

    # ------------------------------------------------------------------

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type != pygame.KEYDOWN:
            return
        if event.key in (pygame.K_RETURN, pygame.K_SPACE):
            if self._waiting:
                self._next_line()
            else:
                self._chars = float(len(_LINES[self._line][1]) + 1)
        elif event.key == pygame.K_ESCAPE:
            self.transition_to("tutorial")

    def update(self, dt: float) -> None:
        if self._waiting or self._line >= len(_LINES):
            return
        self._chars += _SPEED * dt
        full = len(_LINES[self._line][1])
        if self._chars >= full:
            self._chars   = float(full)
            self._waiting = True

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill(_BG)
        if self._line >= len(_LINES):
            return

        speaker, full = _LINES[self._line]
        visible = full[:int(self._chars)]
        cx = SCREEN_WIDTH  // 2
        cy = SCREEN_HEIGHT // 2

        if speaker:
            sf = pygame.font.SysFont("monospace", 13)
            sl = sf.render(speaker.upper(), True, (140, 120, 80))
            surface.blit(sl, sl.get_rect(centerx=cx, centery=cy - 30))
            tf = pygame.font.SysFont("serif", 22)
            ts = tf.render(visible, True, (210, 200, 180))
            surface.blit(ts, ts.get_rect(centerx=cx, centery=cy))
        else:
            nf = pygame.font.SysFont("serif", 20)
            ns = nf.render(visible, True, (130, 120, 100))
            surface.blit(ns, ns.get_rect(centerx=cx, centery=cy))

        if self._waiting:
            pf = pygame.font.SysFont("monospace", 11)
            ps = pf.render("[ ENTER ] Continuar  |  [ ESC ] Pular", True, (60, 58, 50))
            surface.blit(ps, ps.get_rect(centerx=cx, centery=SCREEN_HEIGHT - 28))

        cf = pygame.font.SysFont("monospace", 10)
        cs = cf.render(f"{self._line + 1}/{len(_LINES)}", True, (45, 42, 36))
        surface.blit(cs, (SCREEN_WIDTH - 44, SCREEN_HEIGHT - 18))

    # ------------------------------------------------------------------

    def _next_line(self) -> None:
        self._line  += 1
        self._chars  = 0.0
        self._waiting = False
        if self._line >= len(_LINES):
            self.transition_to("tutorial")
