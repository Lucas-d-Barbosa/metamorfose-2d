"""
systems/collision.py

Shared AABB push-out collision resolution for the player against wall rects.
Extracted from the identical _resolve_collisions() methods in all four phase
scenes so each scene can simply call::

    resolve_wall_collisions(self.player, self.tilemap.walls_near(self.player.hitbox))
"""

from __future__ import annotations

import pygame


def resolve_wall_collisions(
    player,
    wall_rects: list[pygame.Rect],
) -> None:
    """Push *player* out of every overlapping wall rect.

    Uses minimum-overlap AABB push-out: for each colliding wall the axis with
    the smallest penetration depth is corrected and the corresponding velocity
    component is zeroed.

    Parameters
    ----------
    player:
        A ``Player`` instance exposing ``hitbox``, ``velocity``,
        ``move_x(dx)`` and ``move_y(dy)``.
    wall_rects:
        Sequence of ``pygame.Rect`` objects to test against.  Typically
        obtained via ``tilemap.walls_near(player.hitbox)`` (or the full
        ``tilemap.wall_rects`` list when no spatial hash is available).
    """
    for wall in wall_rects:
        if not player.hitbox.colliderect(wall):
            continue

        overlap_left  = player.hitbox.right  - wall.left
        overlap_right = wall.right           - player.hitbox.left
        overlap_top   = player.hitbox.bottom - wall.top
        overlap_bot   = wall.bottom          - player.hitbox.top

        minimum = min(overlap_left, overlap_right, overlap_top, overlap_bot)

        if minimum == overlap_left:
            player.move_x(-overlap_left)
            player.velocity.x = 0
        elif minimum == overlap_right:
            player.move_x(overlap_right)
            player.velocity.x = 0
        elif minimum == overlap_top:
            player.move_y(-overlap_top)
            player.velocity.y = 0
        else:
            player.move_y(overlap_bot)
            player.velocity.y = 0
