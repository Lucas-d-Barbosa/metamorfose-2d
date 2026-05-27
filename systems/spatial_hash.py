"""
systems/spatial_hash.py

General-purpose spatial hash for pygame.Rect objects.
Useful for broad-phase collision queries on large tilemaps.
"""

from __future__ import annotations

import pygame


class SpatialHash:
    """Partition space into equal-sized cells for fast rectangle lookups.

    Usage::

        sh = SpatialHash(cell_size=64)
        sh.build(tilemap.wall_rects)           # rebuild every time the map changes
        nearby = sh.query(player.hitbox)       # only rects that truly intersect
    """

    def __init__(self, cell_size: int = 64) -> None:
        self.cell_size = cell_size
        self._cells: dict[tuple[int, int], list[pygame.Rect]] = {}

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _cell_coords(self, rect: pygame.Rect) -> list[tuple[int, int]]:
        """Return all cell coordinates that *rect* overlaps."""
        cs = self.cell_size
        x0 = rect.left   // cs
        y0 = rect.top    // cs
        x1 = rect.right  // cs
        y1 = rect.bottom // cs
        coords = []
        for cx in range(x0, x1 + 1):
            for cy in range(y0, y1 + 1):
                coords.append((cx, cy))
        return coords

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def insert(self, rect: pygame.Rect) -> None:
        """Add a single rect to the hash."""
        for key in self._cell_coords(rect):
            if key not in self._cells:
                self._cells[key] = []
            self._cells[key].append(rect)

    def build(self, rects: list[pygame.Rect]) -> None:
        """Clear the hash and bulk-insert all rects."""
        self._cells = {}
        for rect in rects:
            self.insert(rect)

    def query(self, rect: pygame.Rect) -> list[pygame.Rect]:
        """Return all rects that actually intersect *rect* (de-duplicated)."""
        seen: set[int] = set()
        result: list[pygame.Rect] = []
        for key in self._cell_coords(rect):
            for candidate in self._cells.get(key, ()):
                rid = id(candidate)
                if rid not in seen:
                    seen.add(rid)
                    if rect.colliderect(candidate):
                        result.append(candidate)
        return result
