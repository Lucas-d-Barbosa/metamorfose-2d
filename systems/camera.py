import pygame

from settings import SCREEN_HEIGHT, SCREEN_WIDTH


class Camera:
    """Smooth-follow camera that clamps to world bounds."""

    LERP_SPEED = 0.12

    def __init__(self, world_width: int, world_height: int) -> None:
        self.offset = pygame.math.Vector2(0.0, 0.0)
        self.world_width = world_width
        self.world_height = world_height

    def update(self, target: pygame.math.Vector2) -> None:
        target_x = SCREEN_WIDTH / 2 - target.x
        target_y = SCREEN_HEIGHT / 2 - target.y
        self.offset.x += (target_x - self.offset.x) * self.LERP_SPEED
        self.offset.y += (target_y - self.offset.y) * self.LERP_SPEED
        # Clamp so we never show beyond world edges
        max_x = min(0.0, SCREEN_WIDTH - self.world_width)
        max_y = min(0.0, SCREEN_HEIGHT - self.world_height)
        self.offset.x = max(max_x, min(0.0, self.offset.x))
        self.offset.y = max(max_y, min(0.0, self.offset.y))

    # ---- Coordinate helpers -------------------------------------------------

    def apply_rect(self, rect: pygame.Rect) -> pygame.Rect:
        return rect.move(int(self.offset.x), int(self.offset.y))

    def apply_vec(self, world_pos: pygame.math.Vector2) -> pygame.math.Vector2:
        return world_pos + self.offset

    def screen_to_world(self, screen_pos: pygame.math.Vector2) -> pygame.math.Vector2:
        return screen_pos - self.offset


class CameraGroup(pygame.sprite.Group):
    """Sprite group that draws each sprite offset by the camera."""

    def __init__(self, camera: Camera) -> None:
        super().__init__()
        self.camera = camera

    def draw(self, surface: pygame.Surface) -> list[pygame.Rect]:  # type: ignore[override]
        drawn = []
        for sprite in self.sprites():
            screen_rect = self.camera.apply_rect(sprite.rect)
            surface.blit(sprite.image, screen_rect)
            drawn.append(screen_rect)
        return drawn
