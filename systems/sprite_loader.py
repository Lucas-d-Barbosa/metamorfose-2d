"""
systems/sprite_loader.py

Loads and caches the Gregor sprite sheet (assets/sprites/gregor.png).
Exposes get_player_sprite() for use by any scene or entity that needs
a ready-to-render player surface.
"""

from __future__ import annotations

import os
from typing import Optional

import pygame

from settings import TILE_SIZE

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_SPRITE_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "assets", "sprites", "gregor.png",
)

_BG_COLOR = (143, 143, 141)
_SPRITE_SIZE = TILE_SIZE - 4  # 28 × 28

# ---------------------------------------------------------------------------
# Module-level cache
# ---------------------------------------------------------------------------

_base_sprite: Optional[pygame.Surface] = None  # loaded once, 28×28 SRCALPHA


def _load_base_sprite() -> pygame.Surface:
    """Load gregor.png, strip background, crop tight bbox, scale to 28×28."""
    raw = pygame.image.load(_SPRITE_PATH)
    raw.set_colorkey(_BG_COLOR)
    raw = raw.convert(32, pygame.SRCALPHA)  # apply colorkey → alpha channel

    # --- tight bounding box (sample every 2 px) ---
    w, h = raw.get_size()
    min_x, min_y = w, h
    max_x, max_y = 0, 0
    found_any = False

    for y in range(0, h, 2):
        for x in range(0, w, 2):
            _, _, _, a = raw.get_at((x, y))
            if a > 0:
                if x < min_x:
                    min_x = x
                if x > max_x:
                    max_x = x
                if y < min_y:
                    min_y = y
                if y > max_y:
                    max_y = y
                found_any = True

    if not found_any:
        # Whole image is transparent — fall back to full size
        min_x, min_y, max_x, max_y = 0, 0, w - 1, h - 1

    bbox = pygame.Rect(min_x, min_y, max_x - min_x + 1, max_y - min_y + 1)
    cropped = raw.subsurface(bbox).copy()

    # Scale to 28×28
    scaled = pygame.transform.smoothscale(cropped, (_SPRITE_SIZE, _SPRITE_SIZE))
    return scaled


def _get_base() -> pygame.Surface:
    """Return (and populate) the module-level cached base sprite."""
    global _base_sprite
    if _base_sprite is None:
        if not os.path.exists(_SPRITE_PATH):
            _base_sprite = _make_fallback()
        else:
            try:
                _base_sprite = _load_base_sprite()
            except Exception:
                _base_sprite = _make_fallback()
    return _base_sprite


def _make_fallback() -> pygame.Surface:
    """Plain green circle fallback when gregor.png is unavailable."""
    surf = pygame.Surface((_SPRITE_SIZE, _SPRITE_SIZE), pygame.SRCALPHA)
    pygame.draw.circle(surf, (50, 200, 50), (_SPRITE_SIZE // 2, _SPRITE_SIZE // 2),
                       _SPRITE_SIZE // 2)
    return surf


def _tint(surface: pygame.Surface, r_mult: float, g_mult: float, b_mult: float) -> pygame.Surface:
    """Return a copy of *surface* with each channel multiplied by the given factors."""
    result = surface.copy()
    # pygame.surfarray requires numpy; use pixel-by-pixel via PixelArray instead
    pa = pygame.PixelArray(result)
    fmt = result.get_masks()  # not used directly — use map/unmap
    for x in range(result.get_width()):
        for y in range(result.get_height()):
            r, g, b, a = result.unmap_rgb(pa[x, y])
            if a > 0:
                nr = min(255, int(r * r_mult))
                ng = min(255, int(g * g_mult))
                nb = min(255, int(b * b_mult))
                pa[x, y] = result.map_rgb(nr, ng, nb)
    del pa
    return result


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def get_player_sprite(
    apple_debuff: bool = False,
    z_level: str = "floor",
    facing_left: bool = False,
) -> pygame.Surface:
    """Return a 28×28 SRCALPHA surface for the player.

    Parameters
    ----------
    apple_debuff:
        When True and z_level is not "ceiling", applies a reddish tint
        (RGB × 1.0, 0.7, 0.7).
    z_level:
        "ceiling" applies a bluish tint (RGB × 0.7, 0.8, 1.0).
        "floor" uses the natural colours (subject to apple_debuff).
    facing_left:
        When True the sprite is flipped horizontally.
    """
    base = _get_base()

    # Work on a copy so we never mutate the cache
    surf = base.copy()

    if z_level == "ceiling":
        surf = _tint(surf, 0.7, 0.8, 1.0)
    elif apple_debuff:
        surf = _tint(surf, 1.0, 0.7, 0.7)

    if facing_left:
        surf = pygame.transform.flip(surf, True, False)

    return surf
