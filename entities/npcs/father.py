import pygame

from entities.npc import NPC
from settings import TILE_SIZE

THROW_COOLDOWN = 4.5    # seconds between apple throws (Phase 3)
THROW_RANGE   = 280.0   # max distance to throw at player


class Father(NPC):
    """
    O Pai — aggressive, fast, unpredictable.
    Narrower FOV than the Manager but moves much faster.
    On contact applies knockback toward the room interior.
    In Phase 3: also throws AppleProjectiles periodically (RF013).
    """

    fov_range = 170.0
    fov_angle = 80.0
    speed = 115.0
    color = (150, 70, 35)
    sprite_key = "father"

    KNOCKBACK_FORCE = 500.0
    CONTACT_RADIUS = TILE_SIZE

    def __init__(self, waypoints: list[tuple[float, float]],
                 room_center: tuple[float, float] = (0.0, 0.0),
                 throws_apples: bool = False) -> None:
        super().__init__(waypoints)
        self._room_center = pygame.math.Vector2(room_center)
        self._throws_apples = throws_apples
        self._throw_timer: float = THROW_COOLDOWN * 0.5  # first throw sooner

    def try_knockback(self, player) -> bool:
        diff = player.pos - self.pos
        dist = diff.length()
        if dist > self.CONTACT_RADIUS or dist == 0:
            return False
        push_dir = diff.normalize()
        player.receive_knockback(push_dir, self.KNOCKBACK_FORCE)
        return True

    def try_throw(self, dt: float,
                  player_pos: pygame.math.Vector2) -> "AppleProjectile | None":
        """
        RF013 — Returns an AppleProjectile aimed at the player if the cooldown
        has elapsed and the player is within range. Returns None otherwise.
        Only active when throws_apples=True (Phase 3).
        """
        if not self._throws_apples:
            return None
        self._throw_timer += dt
        if self._throw_timer < THROW_COOLDOWN:
            return None
        dist = (player_pos - self.pos).length()
        if dist > THROW_RANGE:
            return None
        self._throw_timer = 0.0
        from entities.projectile import AppleProjectile
        return AppleProjectile(pygame.math.Vector2(self.pos),
                               pygame.math.Vector2(player_pos))
