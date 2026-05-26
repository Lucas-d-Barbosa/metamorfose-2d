from typing import Final, Tuple

Color = Tuple[int, int, int]

SCREEN_WIDTH: Final[int] = 1280
SCREEN_HEIGHT: Final[int] = 720
FPS: Final[int] = 60
TILE_SIZE: Final[int] = 32

BLACK: Final[Color] = (0, 0, 0)
WHITE: Final[Color] = (255, 255, 255)
RED: Final[Color] = (220, 50, 50)
GREEN: Final[Color] = (50, 200, 50)
BLUE: Final[Color] = (50, 100, 220)
GRAY: Final[Color] = (30, 30, 30)
DARK_GRAY: Final[Color] = (15, 15, 15)
AMBER: Final[Color] = (180, 120, 40)

# Player
BASE_SPEED: Final[float] = 160.0
ACCELERATION: Final[float] = 1200.0
FRICTION: Final[float] = 10.0

# Stamina
STAMINA_DECAY_RATE: Final[float] = 12.0
CEILING_STAMINA_MODIFIER: Final[float] = 0.5
HUNGER_DECAY_RATE: Final[float] = 4.0

# Sound propagation
FOOTSTEP_NOISE_RADIUS: Final[float] = 120.0
VOICE_NOISE_RADIUS: Final[float] = 200.0
COUGH_NOISE_RADIUS: Final[float] = FOOTSTEP_NOISE_RADIUS * 2.0
VOICE_ALERT_MULTIPLIER: Final[float] = 0.5

# Trash
TRASH_COUGH_DELAY: Final[float] = 1.5

# Apple debuff
APPLE_STAMINA_PENALTY: Final[float] = 0.5
APPLE_SPEED_PENALTY: Final[float] = 0.7

# Fog of War radius per phase (fraction of screen diagonal)
FOG_RADIUS_BY_PHASE: Final[dict[int, float]] = {1: 1.0, 2: 1.0, 3: 0.6, 4: 0.4}
