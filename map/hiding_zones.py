"""
RF004 — Hiding zones (frestas e debaixo de móveis).

When the player's hitbox overlaps a HidingZone, player.hidden is set True.
NPCs already check player.hidden before reporting a detection.
"""

import pygame


class HidingZone:
    def __init__(self, rect: tuple | pygame.Rect, label: str = "") -> None:
        self.rect = pygame.Rect(rect)
        self.label = label

    def contains(self, hitbox: pygame.Rect) -> bool:
        return self.rect.colliderect(hitbox)

    def draw_debug(self, surface: pygame.Surface,
                   camera_offset: pygame.math.Vector2) -> None:
        ox, oy = int(camera_offset.x), int(camera_offset.y)
        screen_rect = self.rect.move(ox, oy)
        dbg = pygame.Surface((screen_rect.width, screen_rect.height), pygame.SRCALPHA)
        dbg.fill((0, 255, 120, 35))
        pygame.draw.rect(dbg, (0, 255, 120, 130), dbg.get_rect(), 1)
        surface.blit(dbg, screen_rect.topleft)
        # Label
        font = pygame.font.SysFont("monospace", 9)
        lbl = font.render(f"hide:{self.label}", True, (0, 220, 100))
        surface.blit(lbl, (screen_rect.x + 2, screen_rect.y + 2))


def build_phase1_hiding_zones(tile_size: int = 32) -> list[HidingZone]:
    """
    Returns hiding zones for Phase 1's room layout.

    Positions match map/layouts.py phase1_room():
      - Bed at rows 9–11, cols 7–10
      - Wardrobe at rows 2–5, cols 2–3
      - Desk at rows 3–5, cols 37–39
    """
    ts = tile_size
    return [
        # Under the bed (CEILING_ACCESS row below furniture)
        HidingZone(pygame.Rect(7 * ts, 12 * ts, 4 * ts, ts), label="cama"),
        # Beside the wardrobe (narrow gap)
        HidingZone(pygame.Rect(4 * ts, 3 * ts, ts, 3 * ts), label="guarda-roupa"),
        # Under the desk (south side)
        HidingZone(pygame.Rect(37 * ts, 6 * ts, 3 * ts, ts), label="escrivaninha"),
    ]
