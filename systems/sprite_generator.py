"""
systems/sprite_generator.py

Generates top-down pixel-art sprites for every character in Metamorfose 2D
using only pygame.draw calls.

Public API
----------
get_npc_sprite(sprite_key, alert_dot_color=None) -> pygame.Surface  (32×32)
get_gregor_sprite(apple_debuff, z_level)          -> pygame.Surface  (40×40)
"""

from __future__ import annotations

from typing import Optional, Tuple

import pygame

# ---------------------------------------------------------------------------
# Sizes
# ---------------------------------------------------------------------------

_NPC_SIZE    = 32   # was 24
_GREGOR_SIZE = 40   # was 28

# ---------------------------------------------------------------------------
# Shared palette
# ---------------------------------------------------------------------------

_OUTLINE: Tuple[int, int, int]      = (18, 12, 6)
_SKIN:    Tuple[int, int, int]      = (215, 168, 128)
_SHOES:   Tuple[int, int, int]      = (30, 22, 12)
_SHADOW:  Tuple[int, int, int, int] = (0, 0, 0, 55)

# ---------------------------------------------------------------------------
# Caches
# ---------------------------------------------------------------------------

_npc_cache:    dict[str, pygame.Surface] = {}
_gregor_cache: dict[tuple, pygame.Surface] = {}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _new_surf(w: int, h: int) -> pygame.Surface:
    s = pygame.Surface((w, h), pygame.SRCALPHA)
    s.fill((0, 0, 0, 0))
    return s


def _draw_npc_base(surf: pygame.Surface, hair: tuple, shirt: tuple,
                   pants: tuple | None = None, wide: bool = False) -> None:
    """
    Top-down humanoid on a 32×32 canvas.

    Structure (top = north, character faces south):
      - Ground shadow
      - Legs / shoes at bottom
      - Torso rectangle
      - Head circle at top-centre
      - Hair cap on head
      - Small face strip (skin)
    """
    W = H = _NPC_SIZE
    cx = W // 2
    if pants is None:
        pants = shirt

    # Ground shadow
    sh = _new_surf(W, H)
    pygame.draw.ellipse(sh, _SHADOW, (5, H - 7, W - 10, 7))
    surf.blit(sh, (0, 0))

    # Shoes
    pygame.draw.rect(surf, _SHOES, (cx - 8,  H - 5, 6, 4))
    pygame.draw.rect(surf, _SHOES, (cx + 2,  H - 5, 6, 4))

    # Legs
    pygame.draw.rect(surf, pants, (cx - 7, H - 11, 5, 6))
    pygame.draw.rect(surf, pants, (cx + 2, H - 11, 5, 6))

    # Torso
    tw = 18 if wide else 14
    tx = cx - tw // 2
    pygame.draw.rect(surf, _OUTLINE, (tx - 1, 13, tw + 2, 10))
    pygame.draw.rect(surf, shirt,    (tx,     14, tw,      9))

    # Head outline + fill
    pygame.draw.circle(surf, _OUTLINE, (cx, 10), 9)
    pygame.draw.circle(surf, hair,     (cx, 10), 8)

    # Face (skin band across lower half of head)
    pygame.draw.rect(surf, _SKIN, (cx - 5, 10, 10, 5))

    # Eyes (two tiny dark dots)
    pygame.draw.circle(surf, (40, 28, 18), (cx - 2, 11), 1)
    pygame.draw.circle(surf, (40, 28, 18), (cx + 2, 11), 1)


# ---------------------------------------------------------------------------
# Per-character builders
# ---------------------------------------------------------------------------

def _make_manager() -> pygame.Surface:
    surf = _new_surf(_NPC_SIZE, _NPC_SIZE)
    _draw_npc_base(surf, hair=(72, 48, 22), shirt=(52, 78, 148), pants=(38, 58, 108))
    cx = _NPC_SIZE // 2
    # White shirt collar
    pygame.draw.rect(surf, (235, 230, 218), (cx - 2, 14, 4, 3))
    # Briefcase (right side of torso)
    pygame.draw.rect(surf, (28, 18, 8), (cx + 8, 15, 5, 4))
    pygame.draw.rect(surf, (28, 18, 8), (cx + 9, 14, 3, 2))
    return surf


def _make_father() -> pygame.Surface:
    surf = _new_surf(_NPC_SIZE, _NPC_SIZE)
    _draw_npc_base(surf, hair=(155, 148, 138), shirt=(68, 56, 80), pants=(52, 42, 62))
    cx = _NPC_SIZE // 2
    # Cane
    pygame.draw.line(surf, (110, 85, 50), (cx + 7, 18), (cx + 11, 28), 2)
    # Military medal
    pygame.draw.circle(surf, (190, 158, 60), (cx - 4, 16), 2)
    return surf


def _make_mother() -> pygame.Surface:
    surf = _new_surf(_NPC_SIZE, _NPC_SIZE)
    _draw_npc_base(surf, hair=(195, 185, 172), shirt=(188, 138, 158),
                   pants=(175, 120, 140), wide=True)
    cx = _NPC_SIZE // 2
    # Hair bun on side
    pygame.draw.circle(surf, (195, 185, 172), (cx + 8, 6), 4)
    return surf


def _make_grete() -> pygame.Surface:
    surf = _new_surf(_NPC_SIZE, _NPC_SIZE)
    _draw_npc_base(surf, hair=(48, 32, 14), shirt=(88, 138, 195), pants=(68, 108, 158))
    cx = _NPC_SIZE // 2
    # Hair flows down both sides
    pygame.draw.ellipse(surf, (48, 32, 14), (cx - 11, 5, 6, 12))
    pygame.draw.ellipse(surf, (48, 32, 14), (cx + 5,  5, 6, 12))
    return surf


def _make_janitor() -> pygame.Surface:
    surf = _new_surf(_NPC_SIZE, _NPC_SIZE)
    _draw_npc_base(surf, hair=(88, 58, 28), shirt=(128, 122, 98), pants=(108, 102, 80))
    cx = _NPC_SIZE // 2
    # Apron
    pygame.draw.rect(surf, (155, 148, 120), (cx - 4, 14, 8, 9))
    # Broom handle + head
    pygame.draw.line(surf, (100, 82, 52), (cx - 7, 18), (cx - 11, 30), 2)
    pygame.draw.rect(surf, (90, 72, 45), (cx - 14, 28, 8, 3))
    return surf


def _make_tenant() -> pygame.Surface:
    surf = _new_surf(_NPC_SIZE, _NPC_SIZE)
    _draw_npc_base(surf, hair=(30, 24, 16), shirt=(58, 52, 70), pants=(44, 38, 55))
    cx = _NPC_SIZE // 2
    # Thin mustache
    pygame.draw.rect(surf, (22, 16, 8), (cx - 4, 13, 3, 1))
    pygame.draw.rect(surf, (22, 16, 8), (cx + 1, 13, 3, 1))
    # Pocket square
    pygame.draw.rect(surf, (210, 205, 192), (cx + 4, 14, 3, 2))
    return surf


def _make_fallback() -> pygame.Surface:
    surf = _new_surf(_NPC_SIZE, _NPC_SIZE)
    pygame.draw.circle(surf, (200, 0, 200), (_NPC_SIZE // 2, _NPC_SIZE // 2),
                       _NPC_SIZE // 2 - 2)
    return surf


_NPC_BUILDERS = {
    "manager": _make_manager,
    "father":  _make_father,
    "mother":  _make_mother,
    "grete":   _make_grete,
    "janitor": _make_janitor,
    "tenant":  _make_tenant,
}


# ---------------------------------------------------------------------------
# Gregor builder
# ---------------------------------------------------------------------------

def _build_gregor_base(apple_debuff: bool, ceiling: bool) -> pygame.Surface:
    W = H = _GREGOR_SIZE
    surf = _new_surf(W, H)
    cx = W // 2

    if ceiling:
        CARAPACE  = (48, 62, 105)
        HEAD_C    = (58, 75, 128)
        HILIT     = (80, 105, 165)
        LEG_C     = (32, 44, 78)
    else:
        CARAPACE  = (62, 48, 22)
        HEAD_C    = (76, 58, 28)
        HILIT     = (102, 80, 42)
        LEG_C     = (42, 30, 12)

    WOUND   = (188, 42, 42)
    OUTLINE = (12, 8, 4)

    # Ground shadow
    sh = _new_surf(W, H)
    pygame.draw.ellipse(sh, (0, 0, 0, 45), (cx - 12, H - 7, 24, 6))
    surf.blit(sh, (0, 0))

    # Antennae
    pygame.draw.line(surf, LEG_C, (cx - 2, 6), (cx - 8, 1), 1)
    pygame.draw.line(surf, LEG_C, (cx + 2, 6), (cx + 8, 1), 1)

    # Head
    pygame.draw.ellipse(surf, OUTLINE, (cx - 6, 3, 12, 9))
    pygame.draw.ellipse(surf, HEAD_C,  (cx - 5, 4, 10, 8))
    # Eyes
    pygame.draw.circle(surf, (200, 220, 255), (cx - 2, 7), 1)
    pygame.draw.circle(surf, (200, 220, 255), (cx + 2, 7), 1)

    # Body (large oval)
    pygame.draw.ellipse(surf, OUTLINE, (cx - 10, 10, 20, 26))
    pygame.draw.ellipse(surf, CARAPACE, (cx - 9, 11, 18, 24))

    # Centre stripe
    pygame.draw.line(surf, HILIT, (cx, 12), (cx, 33), 3)

    # Body segment line
    pygame.draw.line(surf, OUTLINE, (cx - 8, 22), (cx + 8, 22), 1)

    # Legs — 3 per side
    left_pts  = [(cx - 9, 14), (cx - 9, 21), (cx - 9, 28)]
    right_pts = [(cx + 9, 14), (cx + 9, 21), (cx + 9, 28)]
    left_ends  = [(-10,  4), (-10, 0), (-10, -4)]
    right_ends = [( 10,  4), ( 10, 0), ( 10, -4)]
    for (ox, oy), (dx, dy) in zip(left_pts, left_ends):
        pygame.draw.line(surf, LEG_C, (ox, oy), (ox + dx, oy + dy), 1)
    for (ox, oy), (dx, dy) in zip(right_pts, right_ends):
        pygame.draw.line(surf, LEG_C, (ox, oy), (ox + dx, oy + dy), 1)

    # Apple wound
    if apple_debuff and not ceiling:
        pygame.draw.ellipse(surf, WOUND, (cx - 5, 17, 10, 6))
        pygame.draw.line(surf, (220, 90, 90), (cx - 3, 19), (cx + 3, 20), 1)

    return surf


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def get_npc_sprite(
    sprite_key: str,
    alert_dot_color: Optional[Tuple[int, int, int]] = None,
) -> pygame.Surface:
    if sprite_key not in _npc_cache:
        fn = _NPC_BUILDERS.get(sprite_key, _make_fallback)
        _npc_cache[sprite_key] = fn()

    copy = _npc_cache[sprite_key].copy()

    if alert_dot_color is not None:
        pygame.draw.circle(copy, alert_dot_color, (_NPC_SIZE // 2, 4), 4)

    return copy


def get_gregor_sprite(
    apple_debuff: bool = False,
    z_level: str = "floor",
) -> pygame.Surface:
    ceiling   = (z_level == "ceiling")
    cache_key = (apple_debuff, ceiling)

    if cache_key not in _gregor_cache:
        _gregor_cache[cache_key] = _build_gregor_base(apple_debuff, ceiling)

    return _gregor_cache[cache_key].copy()
