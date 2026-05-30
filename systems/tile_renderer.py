"""
GBA Pokémon-style tile surface generation and caching.
All tile textures drawn with pygame.draw — no external images needed.

Public API
----------
get_tile_surface(tile_id: int, tile_size: int = 32) -> pygame.Surface
"""

from __future__ import annotations

import pygame

# Cache: (tile_id, tile_size) -> Surface
_CACHE: dict[tuple, pygame.Surface] = {}

# ---------------------------------------------------------------------------
# Public
# ---------------------------------------------------------------------------

def get_tile_surface(tile_id: int, tile_size: int = 32) -> pygame.Surface:
    key = (tile_id, tile_size)
    if key not in _CACHE:
        _CACHE[key] = _make_tile(tile_id, tile_size)
    return _CACHE[key]

# ---------------------------------------------------------------------------
# Tile factory
# ---------------------------------------------------------------------------

def _make_tile(tile_id: int, ts: int) -> pygame.Surface:
    # Import tile IDs lazily to avoid circular imports at module load time
    from map.tilemap import FLOOR, WALL, FURNITURE, DOOR_OPEN, CEILING_ACCESS

    surf = pygame.Surface((ts, ts))  # no alpha — always fully opaque tiles
    {
        FLOOR:          _draw_floor,
        WALL:           _draw_wall,
        FURNITURE:      _draw_furniture,
        DOOR_OPEN:      _draw_door,
        CEILING_ACCESS: _draw_ceiling_access,
    }.get(tile_id, _draw_unknown)(surf, ts)
    return surf

# ---------------------------------------------------------------------------
# Individual tile renderers
# ---------------------------------------------------------------------------

def _draw_floor(surf: pygame.Surface, ts: int) -> None:
    """Warm wood planks — visible horizontal grain, small knot."""
    BASE   = (155, 120, 72)
    GRAIN  = (128,  98, 55)
    KNOT   = (112,  85, 45)
    BORDER = (120,  92, 50)

    surf.fill(BASE)

    # Horizontal grain lines at ~30%, 60%, 90% of tile height
    for frac in (0.30, 0.60, 0.90):
        y = int(ts * frac)
        pygame.draw.line(surf, GRAIN, (0, y), (ts - 1, y), 1)

    # Wood knot (small ellipse, upper-right quadrant)
    kx, ky = ts * 3 // 4, ts // 4
    pygame.draw.ellipse(surf, KNOT, (kx - 3, ky - 2, 6, 4))

    # 1-px border
    pygame.draw.rect(surf, BORDER, (0, 0, ts, ts), 1)


def _draw_wall(surf: pygame.Surface, ts: int) -> None:
    """Plaster/stone wall surface — darker top shadow, subtle crack."""
    BASE   = (102,  90, 76)
    TOP    = ( 78,  68, 56)
    LEFT   = ( 90,  80, 66)
    BOTTOM = (118, 106, 90)
    BORDER = ( 72,  62, 50)
    CRACK  = ( 85,  75, 62)

    surf.fill(BASE)

    # Top shadow (2 px)
    pygame.draw.rect(surf, TOP, (0, 0, ts, 3))
    # Left edge (2 px)
    pygame.draw.rect(surf, LEFT, (0, 0, 2, ts))
    # Bottom highlight (2 px)
    pygame.draw.rect(surf, BOTTOM, (0, ts - 2, ts, 2))

    # Faint vertical crack at ~2/3 of width
    cx = ts * 2 // 3
    pygame.draw.line(surf, CRACK, (cx, 4), (cx + 1, ts - 4), 1)

    # Border
    pygame.draw.rect(surf, BORDER, (0, 0, ts, ts), 1)


def _draw_furniture(surf: pygame.Surface, ts: int) -> None:
    """Top-down view of dark polished wood — bevelled edges."""
    BASE   = ( 80,  56,  28)
    HILIT  = (112,  82,  45)
    SHADOW = ( 52,  35,  15)
    GRAIN  = ( 65,  44,  20)
    BORDER = ( 52,  35,  15)

    surf.fill(BASE)

    # Top-left highlight L-shape
    pygame.draw.line(surf, HILIT, (2, 2), (ts - 4, 2), 2)   # top edge
    pygame.draw.line(surf, HILIT, (2, 2), (2, ts - 4), 2)   # left edge

    # Bottom-right shadow L-shape
    pygame.draw.line(surf, SHADOW, (2, ts - 3), (ts - 2, ts - 3), 2)   # bottom
    pygame.draw.line(surf, SHADOW, (ts - 3, 2), (ts - 3, ts - 2), 2)   # right

    # Centre horizontal grain line
    mid = ts // 2
    pygame.draw.line(surf, GRAIN, (6, mid), (ts - 6, mid), 1)

    # Border
    pygame.draw.rect(surf, BORDER, (0, 0, ts, ts), 1)


def _draw_door(surf: pygame.Surface, ts: int) -> None:
    """Closed/locked door — dark wood panel with frame, inset, and brass knob."""
    FRAME  = (165, 128,  72)   # warm wood frame
    PANEL  = ( 52,  36,  18)   # dark door panel
    INSET  = ( 64,  46,  24)   # raised inset panel
    HILIT  = (200, 160,  88)   # frame top/left highlight
    KNOB   = (210, 170,  60)   # brass doorknob
    BORDER = (120,  92,  48)

    surf.fill(PANEL)

    # Thick frame on all sides
    pygame.draw.rect(surf, FRAME, (0, 0, ts, 5))          # top
    pygame.draw.rect(surf, FRAME, (0, ts - 4, ts, 4))     # bottom
    pygame.draw.rect(surf, FRAME, (0, 0, 5, ts))          # left
    pygame.draw.rect(surf, FRAME, (ts - 5, 0, 5, ts))     # right

    # Frame highlight (top-left bevel)
    pygame.draw.line(surf, HILIT, (1, 1), (ts - 2, 1), 1)
    pygame.draw.line(surf, HILIT, (1, 1), (1, ts - 2), 1)

    # Inset panel (top half)
    inset_margin = 7
    panel_h = ts // 2 - inset_margin
    pygame.draw.rect(surf, INSET,
                     (inset_margin, inset_margin,
                      ts - inset_margin * 2, panel_h))

    # Inset panel (bottom half)
    panel_y2 = ts // 2 + 2
    panel_h2 = ts - panel_y2 - inset_margin
    pygame.draw.rect(surf, INSET,
                     (inset_margin, panel_y2,
                      ts - inset_margin * 2, panel_h2))

    # Brass knob (right side, vertical centre)
    kx = ts - 9
    ky = ts // 2
    pygame.draw.circle(surf, KNOB, (kx, ky), 3)
    pygame.draw.circle(surf, (140, 108, 38), (kx, ky), 3, 1)  # dark rim

    pygame.draw.rect(surf, BORDER, (0, 0, ts, ts), 1)


def _draw_ceiling_access(surf: pygame.Surface, ts: int) -> None:
    """Ceiling tile — cool blue-grey with climb-cross marks and corner cobwebs."""
    BASE   = (132, 138, 152)
    MARK   = (108, 114, 128)
    DOT    = (100, 106, 120)
    BORDER = ( 98, 104, 118)

    surf.fill(BASE)

    # Cross marks at centre
    mid = ts // 2
    pygame.draw.line(surf, MARK, (mid - 4, mid), (mid + 4, mid), 2)
    pygame.draw.line(surf, MARK, (mid, mid - 4), (mid, mid + 4), 2)

    # Corner cobweb dots
    for cx, cy in [(4, 4), (ts - 4, 4), (4, ts - 4), (ts - 4, ts - 4)]:
        pygame.draw.circle(surf, DOT, (cx, cy), 2)

    pygame.draw.rect(surf, BORDER, (0, 0, ts, ts), 1)


def _draw_unknown(surf: pygame.Surface, ts: int) -> None:
    surf.fill((75, 75, 75))
    pygame.draw.rect(surf, (55, 55, 55), (0, 0, ts, ts), 1)
