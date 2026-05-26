"""
Code-defined map layouts. Replace with pytmx loader when Tiled maps are ready.

Tile IDs: 0=floor, 1=wall, 2=furniture(solid), 3=door_open, 4=ceiling_access
"""

from map.tilemap import CEILING_ACCESS, DOOR_OPEN, FLOOR, FURNITURE, WALL


def _empty(rows: int, cols: int) -> list[list[int]]:
    return [[FLOOR] * cols for _ in range(rows)]


def _border(layout: list[list[int]]) -> None:
    rows, cols = len(layout), len(layout[0])
    for c in range(cols):
        layout[0][c] = WALL
        layout[rows - 1][c] = WALL
    for r in range(rows):
        layout[r][0] = WALL
        layout[r][cols - 1] = WALL


def _fill_rect(layout: list[list[int]], r1: int, c1: int,
               r2: int, c2: int, tile: int) -> None:
    for r in range(r1, r2 + 1):
        for c in range(c1, c2 + 1):
            layout[r][c] = tile


# ---------------------------------------------------------------------------
# Phase 1 — Gregor's Bedroom (42 cols × 24 rows = 1344 × 768 pixels @ 32px)
# ---------------------------------------------------------------------------
def phase1_room() -> list[list[int]]:
    COLS, ROWS = 42, 24
    layout = _empty(ROWS, COLS)
    _border(layout)

    # Door gap in bottom wall (cols 19–20)
    layout[ROWS - 1][19] = DOOR_OPEN
    layout[ROWS - 1][20] = DOOR_OPEN

    # Wardrobe — top-left area (cols 2–3, rows 2–5)
    _fill_rect(layout, 2, 2, 5, 3, FURNITURE)

    # Bed — center-left (cols 7–10, rows 9–11)
    _fill_rect(layout, 9, 7, 11, 10, FURNITURE)
    # Crevice under bed: mark floor tiles adjacent to bed bottom as ceiling_access
    for c in range(7, 11):
        layout[12][c] = CEILING_ACCESS

    # Picture frame on wall (col 0, rows 6–7) — not solid, just visual marker
    # Represented as a ceiling_access tile (player can press against it)
    layout[6][1] = CEILING_ACCESS
    layout[7][1] = CEILING_ACCESS

    # Desk — right side (cols 37–39, rows 3–5)
    _fill_rect(layout, 3, 37, 5, 39, FURNITURE)

    # Scattered items table (cols 25–27, rows 14–15)
    _fill_rect(layout, 14, 25, 15, 27, FURNITURE)

    return layout
