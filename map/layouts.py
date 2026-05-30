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
# Phase 1 — Gregor's Bedroom (24 cols × 16 rows = 768 × 512 pixels @ 32px)
# Fits entirely on a 1280×720 screen — the full room is visible at once.
# ---------------------------------------------------------------------------
def phase1_room() -> list[list[int]]:
    COLS, ROWS = 24, 16
    layout = _empty(ROWS, COLS)
    _border(layout)

    # Door gap in bottom wall — centre (cols 11–12)
    layout[ROWS - 1][11] = DOOR_OPEN
    layout[ROWS - 1][12] = DOOR_OPEN

    # Wardrobe — left wall (cols 1–2, rows 9–11)
    _fill_rect(layout, 9, 1, 11, 2, FURNITURE)

    # Bed — top-left (cols 2–4, rows 4–6)
    _fill_rect(layout, 4, 2, 6, 4, FURNITURE)
    # Ceiling access under bed
    for c in range(2, 5):
        layout[7][c] = CEILING_ACCESS

    # Picture frame (ceiling access) — left wall, rows 4–5
    layout[4][1] = CEILING_ACCESS
    layout[5][1] = CEILING_ACCESS

    # Desk — top-right (cols 19–22, rows 3–5)
    _fill_rect(layout, 3, 19, 5, 22, FURNITURE)

    # Scattered items table — mid-right (cols 15–17, rows 9–11)
    _fill_rect(layout, 9, 15, 11, 17, FURNITURE)

    return layout


# ---------------------------------------------------------------------------
# Phase 2 — Gregor's Bedroom (emptied version, same dimensions)
# Only the picture frame and door remain; furniture was removed by Mãe/Grete.
# ---------------------------------------------------------------------------
def phase2_room() -> list[list[int]]:
    COLS, ROWS = 42, 24
    layout = _empty(ROWS, COLS)
    _border(layout)

    # Same door gap
    layout[ROWS - 1][19] = DOOR_OPEN
    layout[ROWS - 1][20] = DOOR_OPEN

    # Picture frame still on wall — player's objective
    layout[6][1] = CEILING_ACCESS
    layout[7][1] = CEILING_ACCESS

    # Scratch marks on ceiling (Gregor's crawling marks — ceiling_access tiles)
    for c in range(5, 38, 6):
        layout[1][c] = CEILING_ACCESS

    return layout


# ---------------------------------------------------------------------------
# Phase 3 — Gregor's Bedroom turned storage room (junk maze)
# Crates and debris block paths; Father patrols aggressively.
# ---------------------------------------------------------------------------
def phase3_room() -> list[list[int]]:
    COLS, ROWS = 42, 24
    layout = _empty(ROWS, COLS)
    _border(layout)

    layout[ROWS - 1][19] = DOOR_OPEN
    layout[ROWS - 1][20] = DOOR_OPEN

    # Junk piles — broken furniture, crates (FURNITURE = solid)
    _fill_rect(layout, 3,  5,  4,  7, FURNITURE)   # crate stack left
    _fill_rect(layout, 3, 14,  4, 16, FURNITURE)   # crate center
    _fill_rect(layout, 3, 28,  4, 30, FURNITURE)   # crate right
    _fill_rect(layout, 8,  2,  9,  4, FURNITURE)   # broken wardrobe remnant
    _fill_rect(layout, 8, 20,  9, 22, FURNITURE)   # old desk
    _fill_rect(layout, 8, 33,  9, 35, FURNITURE)   # stacked boxes
    _fill_rect(layout, 14, 8, 15, 10, FURNITURE)   # debris mid-left
    _fill_rect(layout, 14,26, 15, 28, FURNITURE)   # debris mid-right
    _fill_rect(layout, 18, 5, 19,  7, FURNITURE)   # bottom-left pile
    _fill_rect(layout, 18,34, 19, 36, FURNITURE)   # bottom-right pile

    # Ceiling access strips (wall-crawl routes)
    for c in range(2, 40, 5):
        layout[1][c] = CEILING_ACCESS
    for c in range(4, 38, 7):
        layout[ROWS - 2][c] = CEILING_ACCESS

    return layout


# ---------------------------------------------------------------------------
# Phase 4 — The Dump / The Music
# Even more junk. Sala passage on the right wall (rows 10–13, col 41).
# Tenants patrol cols 30–41; janitor roams the full room.
# ---------------------------------------------------------------------------
def phase4_room() -> list[list[int]]:
    COLS, ROWS = 42, 24
    layout = _empty(ROWS, COLS)
    _border(layout)

    # Bottom door (quarto ↔ corridor, kept for continuity)
    layout[ROWS - 1][19] = DOOR_OPEN
    layout[ROWS - 1][20] = DOOR_OPEN

    # Sala passage — right wall gap (rows 10–13)
    for r in range(10, 14):
        layout[r][COLS - 1] = DOOR_OPEN

    # Dense junk labyrinth
    _fill_rect(layout, 2,  2,  4,  4, FURNITURE)   # left-top pile
    _fill_rect(layout, 2, 10,  4, 12, FURNITURE)   # center-top crates
    _fill_rect(layout, 2, 20,  4, 22, FURNITURE)   # center-top right
    _fill_rect(layout, 2, 30,  4, 32, FURNITURE)   # right-top pile
    _fill_rect(layout, 7,  6,  9,  8, FURNITURE)   # mid-left debris
    _fill_rect(layout, 7, 16,  9, 18, FURNITURE)   # mid-center debris
    _fill_rect(layout, 7, 26,  9, 28, FURNITURE)   # mid-right debris
    _fill_rect(layout, 12, 2, 14,  5, FURNITURE)   # heavy left pile
    _fill_rect(layout, 12,12, 14, 15, FURNITURE)   # heavy center pile
    _fill_rect(layout, 12,22, 14, 25, FURNITURE)   # heavy right pile
    _fill_rect(layout, 17, 7, 19,  9, FURNITURE)   # bottom-left junk
    _fill_rect(layout, 17,17, 19, 19, FURNITURE)   # bottom-center junk
    _fill_rect(layout, 17,28, 19, 30, FURNITURE)   # bottom-right junk

    # Ceiling crawl routes (thick strip near top and alongside right wall)
    for c in range(2, 40, 4):
        layout[1][c] = CEILING_ACCESS
    for r in range(2, ROWS - 2):
        if layout[r][COLS - 2] == FLOOR:
            layout[r][COLS - 2] = CEILING_ACCESS

    return layout
