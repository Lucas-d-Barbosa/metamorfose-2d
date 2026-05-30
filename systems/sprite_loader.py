"""
systems/sprite_loader.py

Loads and animates the Gregor sprite sheet (assets/sprites/gregor.png).
Provides get_player_sprite() for static use and get_animation_frame() for animation.
"""

from __future__ import annotations

import os
from typing import Dict, List, Optional, Tuple

import pygame

from settings import TILE_SIZE

# ---------------------------------------------------------------------------
# Paths & sizes
# ---------------------------------------------------------------------------

_SPRITE_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "assets", "sprites", "gregor.png",
)

_CANVAS = 44  # fixed square canvas (px) shared by EVERY frame

# ---------------------------------------------------------------------------
# Frame definitions: {anim_name: [(sheet_x, sheet_y, sheet_w, sheet_h), ...]}
# ---------------------------------------------------------------------------

ANIM_FRAMES: Dict[str, List[Tuple[int, int, int, int]]] = {
    "idle": [
        (151, 55, 52, 70),
        (233, 56, 52, 69),
        (310, 56, 52, 69),
        (385, 56, 52, 69),
        (458, 56, 52, 69),
        (537, 56, 52, 69),
    ],
    "walk_right": [
        (146, 218, 88, 48),
        (247, 218, 100, 48),
        (327, 219, 105, 49),
        (417, 218, 89, 49),
        (528, 218, 83, 48),
        (631, 218, 86, 48),
    ],
    "walk_left": [
        (134, 288, 100, 48),
        (213, 288, 105, 49),
        (295, 288, 105, 47),
        (381, 288, 92, 48),
        (507, 288, 92, 48),
        (616, 288, 86, 47),
    ],
    "stealth_right": [
        (142, 360, 91, 44),
        (251, 360, 90, 44),
        (357, 360, 100, 44),
        (439, 362, 87, 41),
        (550, 365, 88, 38),
    ],
    "stealth_left": [
        (140, 423, 93, 59),
        (273, 422, 92, 60),
        (397, 424, 87, 41),
        (513, 429, 88, 36),
    ],
}

# ---------------------------------------------------------------------------
# Sheet cache
# ---------------------------------------------------------------------------

_sheet: Optional[pygame.Surface] = None   # preprocessed RGBA sheet
_frame_cache: Dict[tuple, pygame.Surface] = {}


def _load_sheet() -> pygame.Surface:
    """Load gregor.png and return an RGBA surface.

    The PNG is expected to already have a transparent background (processed
    offline).  If it still has an opaque background (alpha at corner = 255),
    fall back to a colorkey-based removal for all sampled corner shades.
    """
    surf = pygame.image.load(_SPRITE_PATH).convert_alpha()
    if surf.get_at((0, 0))[3] == 0:
        return surf  # alpha channel already baked in

    # Fallback for unprocessed sheet: use pygame.transform.threshold to
    # remove each sampled background shade in-place.
    w, h = surf.get_size()
    sample_pts = [(0, 0), (1, 0), (0, 1), (1, 1),
                  (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
    bg_shades = list({surf.get_at(pt)[:3] for pt in sample_pts})
    for r, g, b in bg_shades:
        pygame.transform.threshold(
            surf, surf,
            search_color=(r, g, b, 255),
            threshold=(25, 25, 25, 0),
            set_color=(0, 0, 0, 0),
            set_behavior=1,
        )
    return surf


def _get_sheet() -> Optional[pygame.Surface]:
    global _sheet
    if _sheet is None:
        if os.path.exists(_SPRITE_PATH):
            try:
                _sheet = _load_sheet()
            except Exception:
                _sheet = None
    return _sheet


# ---------------------------------------------------------------------------
# Frame extraction helpers
# ---------------------------------------------------------------------------

def _extract_frame(
    sx: int, sy: int, sw: int, sh: int,
    apple_debuff: bool,
    ceiling: bool,
    anim: str = "",
) -> pygame.Surface:
    """Extract one frame from the sheet, scale to _TARGET_H, return RGBA."""
    sheet = _get_sheet()
    if sheet is None:
        return _fallback_surface()

    # Crop
    crop = sheet.subsurface(pygame.Rect(sx, sy, sw, sh)).copy()

    # Normalise by the LARGEST dimension so every frame's longest extent maps
    # to _CANVAS.  This keeps the beetle the same apparent size regardless of
    # the crop's aspect ratio (idle is tall/narrow, walk is wide/short), which
    # is what caused the sprite to "change size" between idle and walking.
    scale = _CANVAS / max(sw, sh)
    tw = max(1, round(sw * scale))
    th = max(1, round(sh * scale))
    scaled = pygame.transform.smoothscale(crop, (tw, th))

    # Centre every frame in one fixed square canvas so the sprite rect never
    # resizes when switching animations.
    canvas = pygame.Surface((_CANVAS, _CANVAS), pygame.SRCALPHA)
    canvas.fill((0, 0, 0, 0))
    canvas.blit(scaled, ((_CANVAS - tw) // 2, (_CANVAS - th) // 2))

    if ceiling:
        _apply_tint(canvas, 0.7, 0.8, 1.0)
    elif apple_debuff:
        _apply_tint(canvas, 1.0, 0.75, 0.75)

    return canvas


def _apply_tint(
    surf: pygame.Surface, rm: float, gm: float, bm: float
) -> None:
    """Tint surface in-place using PixelArray."""
    pa = pygame.PixelArray(surf)
    for x in range(surf.get_width()):
        for y in range(surf.get_height()):
            r, g, b, a = surf.unmap_rgb(pa[x, y])
            if a > 0:
                pa[x, y] = surf.map_rgb(
                    min(255, int(r * rm)),
                    min(255, int(g * gm)),
                    min(255, int(b * bm)),
                )
    del pa


def _fallback_surface() -> pygame.Surface:
    s = pygame.Surface((_CANVAS, _CANVAS), pygame.SRCALPHA)
    pygame.draw.circle(s, (50, 200, 50), (_CANVAS // 2, _CANVAS // 2), _CANVAS // 2)
    return s


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def get_animation_frame(
    anim: str,
    frame_idx: int,
    apple_debuff: bool = False,
    z_level: str = "floor",
) -> pygame.Surface:
    """Return a cached, preprocessed surface for one animation frame.

    Falls back to sprite_generator if the sheet is unavailable.
    """
    frames = ANIM_FRAMES.get(anim)
    if not frames:
        return get_player_sprite(apple_debuff=apple_debuff, z_level=z_level)

    frame_idx = frame_idx % len(frames)
    ceiling = z_level == "ceiling"
    key = (anim, frame_idx, apple_debuff, ceiling)

    if key not in _frame_cache:
        sx, sy, sw, sh = frames[frame_idx]
        _frame_cache[key] = _extract_frame(sx, sy, sw, sh, apple_debuff, ceiling, anim=anim)

    return _frame_cache[key]


def frame_count(anim: str) -> int:
    """Number of frames for a given animation name."""
    return len(ANIM_FRAMES.get(anim, []))


def get_player_sprite(
    apple_debuff: bool = False,
    z_level: str = "floor",
) -> pygame.Surface:
    """Return a static sprite for the player (idle frame 0).

    Kept for backward compatibility; delegates to get_animation_frame.
    """
    if _get_sheet() is not None:
        return get_animation_frame("idle", 0, apple_debuff=apple_debuff, z_level=z_level)

    # Fallback to procedural generator
    try:
        from systems.sprite_generator import get_gregor_sprite  # type: ignore
        return get_gregor_sprite(apple_debuff=apple_debuff, z_level=z_level)
    except Exception:
        return _fallback_surface()
