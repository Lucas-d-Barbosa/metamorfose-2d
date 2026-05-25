from typing import Final, Tuple

Color = Tuple[int, int, int]

SCREEN_WIDTH: Final[int] = 1280
SCREEN_HEIGHT: Final[int] = 720
FPS: Final[int] = 60
TILE_SIZE: Final[int] = 64

BLACK: Final[Color] = (0, 0, 0)
WHITE: Final[Color] = (255, 255, 255)
RED: Final[Color] = (255, 0, 0)
GREEN: Final[Color] = (0, 255, 0)
BLUE: Final[Color] = (0, 0, 255)
GRAY: Final[Color] = (128, 128, 128)

BASE_SPEED: Final[float] = 220.0
GRAVITY: Final[float] = 1800.0
CEILING_STAMINA_MODIFIER: Final[float] = 0.5
