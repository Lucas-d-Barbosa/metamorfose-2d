"""
RF007 — Miopia Progressiva (Fog of War).

Renderiza uma Surface escura sobre o mundo com um "furo" circular ao redor
do jogador. O raio encolhe por fase:
  Fase 1-2: 100% (sem neblina visível)
  Fase 3:    60%
  Fase 4:    40%

A Surface é desenhada ACIMA dos tiles e NPCs mas ABAIXO do HUD e diálogos.
"""

import math

import pygame

from settings import FOG_RADIUS_BY_PHASE, SCREEN_HEIGHT, SCREEN_WIDTH

_DIAG = math.sqrt(SCREEN_WIDTH**2 + SCREEN_HEIGHT**2)

# Phases 1-2 have full visibility — skip fog drawing entirely
_SKIP_PHASES = {1, 2}

_BASE_ALPHA = 220   # darkness outside the vision circle


class FogOfWar:
    def __init__(self, phase: int) -> None:
        self.phase = phase
        ratio = FOG_RADIUS_BY_PHASE.get(phase, 1.0)
        self.radius = int(_DIAG * ratio * 0.5)
        self._surf: pygame.Surface | None = None
        self._last_center: tuple[int, int] | None = None

    # ------------------------------------------------------------------

    def draw(self, surface: pygame.Surface,
             player_screen_pos: pygame.math.Vector2) -> None:
        if self.phase in _SKIP_PHASES:
            return

        center = (int(player_screen_pos.x), int(player_screen_pos.y))

        # Rebuild surface only when player has moved at least 2px
        if self._surf is None or self._last_center != center:
            self._surf = self._build(center)
            self._last_center = center

        surface.blit(self._surf, (0, 0))

    # ------------------------------------------------------------------

    def _build(self, center: tuple[int, int]) -> pygame.Surface:
        surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        surf.fill((0, 0, 0, _BASE_ALPHA))

        r = self.radius
        # Gradient: draw concentric circles from edge inward, each with
        # decreasing alpha, carving out a visible region at center.
        steps = max(1, r // 3)
        for i in range(steps, -1, -1):
            frac = i / steps            # 1.0 at outer ring → 0.0 at center
            a = int(_BASE_ALPHA * (frac ** 1.6))
            step_r = int(r * frac)
            pygame.draw.circle(surf, (0, 0, 0, a), center, step_r)

        return surf

    # ------------------------------------------------------------------

    def update_phase(self, phase: int) -> None:
        """Call when transitioning to a new phase mid-session."""
        self.phase = phase
        ratio = FOG_RADIUS_BY_PHASE.get(phase, 1.0)
        self.radius = int(_DIAG * ratio * 0.5)
        self._surf = None
        self._last_center = None
