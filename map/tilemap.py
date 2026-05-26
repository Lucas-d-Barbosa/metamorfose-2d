import pygame

from settings import TILE_SIZE

# Tile IDs
FLOOR = 0
WALL = 1
FURNITURE = 2      # solid, different visual
DOOR_OPEN = 3      # walkable gap in wall
CEILING_ACCESS = 4 # floor tile where player can climb to ceiling


_TILE_COLORS: dict[int, tuple[int, int, int]] = {
    FLOOR:          (52, 42, 32),
    WALL:           (75, 62, 48),
    FURNITURE:      (90, 65, 40),
    DOOR_OPEN:      (40, 32, 24),
    CEILING_ACCESS: (52, 52, 70),
}
_TILE_BORDER: dict[int, tuple[int, int, int]] = {
    FLOOR:          (30, 24, 18),
    WALL:           (45, 35, 25),
    FURNITURE:      (60, 42, 24),
    DOOR_OPEN:      (25, 20, 15),
    CEILING_ACCESS: (30, 30, 50),
}

_SOLID = {WALL, FURNITURE}


class TileMap:
    """
    Tile-based map. Layout is a 2D list of tile IDs.
    Coordinates are in world-space pixels (origin top-left).
    """

    def __init__(self, layout: list[list[int]], tile_size: int = TILE_SIZE) -> None:
        self.layout = layout
        self.tile_size = tile_size
        self.rows = len(layout)
        self.cols = len(layout[0]) if layout else 0
        self.width = self.cols * tile_size
        self.height = self.rows * tile_size
        self.wall_rects = self._build_walls()

    def _build_walls(self) -> list[pygame.Rect]:
        walls = []
        ts = self.tile_size
        for r, row in enumerate(self.layout):
            for c, tile in enumerate(row):
                if tile in _SOLID:
                    walls.append(pygame.Rect(c * ts, r * ts, ts, ts))
        return walls

    def is_solid_at(self, world_x: float, world_y: float) -> bool:
        c = int(world_x // self.tile_size)
        r = int(world_y // self.tile_size)
        if not (0 <= r < self.rows and 0 <= c < self.cols):
            return True  # out of bounds → treat as solid
        return self.layout[r][c] in _SOLID

    def tile_at(self, world_x: float, world_y: float) -> int:
        c = int(world_x // self.tile_size)
        r = int(world_y // self.tile_size)
        if not (0 <= r < self.rows and 0 <= c < self.cols):
            return WALL
        return self.layout[r][c]

    def draw(self, surface: pygame.Surface,
             camera_offset: pygame.math.Vector2) -> None:
        ts = self.tile_size
        ox, oy = int(camera_offset.x), int(camera_offset.y)

        screen_w = surface.get_width()
        screen_h = surface.get_height()

        # Only draw tiles visible on screen
        col_start = max(0, -ox // ts)
        col_end = min(self.cols, (-ox + screen_w) // ts + 2)
        row_start = max(0, -oy // ts)
        row_end = min(self.rows, (-oy + screen_h) // ts + 2)

        for r in range(row_start, row_end):
            for c in range(col_start, col_end):
                tile = self.layout[r][c]
                color = _TILE_COLORS.get(tile, (80, 80, 80))
                border = _TILE_BORDER.get(tile, (50, 50, 50))
                rect = pygame.Rect(c * ts + ox, r * ts + oy, ts, ts)
                pygame.draw.rect(surface, color, rect)
                pygame.draw.rect(surface, border, rect, 1)
