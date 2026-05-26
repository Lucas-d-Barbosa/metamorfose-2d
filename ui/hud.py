"""
HUD overlay drawn in screen-space (above camera, above fog of war).

Draws:
  - Stamina bar
  - Hunger bar
  - Global alert level (highest suspicion among all NPCs)
  - Z-level indicator (CHÃO / TETO)
  - Phase label
"""

import pygame

from settings import BLUE, RED, SCREEN_HEIGHT, SCREEN_WIDTH, WHITE
from systems.stealth import AlertState

_FONT_CACHE: dict[tuple, pygame.font.Font] = {}


def _font(name: str, size: int) -> pygame.font.Font:
    key = (name, size)
    if key not in _FONT_CACHE:
        _FONT_CACHE[key] = pygame.font.SysFont(name, size)
    return _FONT_CACHE[key]


class HUD:
    PAD = 10
    BAR_W = 180
    BAR_H = 12
    GAP = 5

    def __init__(self, phase: int = 1) -> None:
        self.phase = phase

    def draw(self, surface: pygame.Surface, player, npcs: list) -> None:
        self._draw_player_bars(surface, player)
        self._draw_alert_meter(surface, npcs)
        self._draw_z_level(surface, player)
        self._draw_hidden_indicator(surface, player)
        self._draw_phase_label(surface)

    # -------------------------------------------------------------------------

    def _draw_player_bars(self, surface: pygame.Surface, player) -> None:
        p = self.PAD
        self._bar(surface, p, p,
                  self.BAR_W, self.BAR_H,
                  player.current_stamina, player.max_stamina,
                  RED, "STA")
        self._bar(surface, p, p + self.BAR_H + self.GAP,
                  self.BAR_W, self.BAR_H,
                  player.current_hunger, player.max_hunger,
                  BLUE, "FAM")

    def _draw_alert_meter(self, surface: pygame.Surface, npcs: list) -> None:
        if not npcs:
            return
        max_suspicion = max(npc.alert.suspicion for npc in npcs)
        if max_suspicion < 1.0:
            return

        # Pick color from highest-alert NPC
        top_npc = max(npcs, key=lambda n: n.alert.suspicion)
        color = top_npc.alert.color

        p = self.PAD
        y = p + (self.BAR_H + self.GAP) * 2 + 4

        font = _font("monospace", 10)
        label_surf = font.render("ALERTA", True, color)
        surface.blit(label_surf, (p, y))
        y += 13

        self._bar(surface, p, y, self.BAR_W, self.BAR_H,
                  max_suspicion, 100.0, color, "")

        # State label
        state_name = top_npc.alert.state.name
        state_surf = font.render(state_name, True, color)
        surface.blit(state_surf, (p + self.BAR_W + 6, y))

    def _draw_z_level(self, surface: pygame.Surface, player) -> None:
        label = "[ TETO ]" if player.z_level == "ceiling" else "[ CHÃO ]"
        color = (160, 210, 255) if player.z_level == "ceiling" else (210, 180, 120)
        font = _font("monospace", 11)
        surf = font.render(label, True, color)
        p = self.PAD
        y = p + (self.BAR_H + self.GAP) * 2 + 4 + 13 + self.BAR_H + 8
        surface.blit(surf, (p, y))

    def _draw_hidden_indicator(self, surface: pygame.Surface, player) -> None:
        if not player.hidden:
            return
        font = _font("monospace", 12)
        surf = font.render("[ OCULTO ]", True, (80, 220, 140))
        surface.blit(surf, (SCREEN_WIDTH // 2 - surf.get_width() // 2,
                            SCREEN_HEIGHT - 28))

    def _draw_phase_label(self, surface: pygame.Surface) -> None:
        font = _font("monospace", 11)
        text = f"FASE {self.phase}"
        surf = font.render(text, True, (80, 80, 80))
        surface.blit(surf, (SCREEN_WIDTH - surf.get_width() - self.PAD,
                            SCREEN_HEIGHT - surf.get_height() - self.PAD))

    # -------------------------------------------------------------------------

    @staticmethod
    def _bar(surface: pygame.Surface, x: int, y: int,
             w: int, h: int, current: float, maximum: float,
             color: tuple, label: str) -> None:
        ratio = 0.0 if maximum <= 0 else current / maximum
        pygame.draw.rect(surface, (40, 40, 40), (x, y, w, h))
        pygame.draw.rect(surface, color, (x, y, int(w * ratio), h))
        pygame.draw.rect(surface, WHITE, (x, y, w, h), 1)
        if label:
            font = _font("monospace", 9)
            text = font.render(f"{label} {int(current)}/{int(maximum)}", True, WHITE)
            surface.blit(text, (x + 3, y + 1))
