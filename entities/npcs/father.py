import pygame

from entities.npc import NPC
from settings import TILE_SIZE


class Father(NPC):
    """
    O Pai — aggressive, fast, unpredictable.
    Narrower FOV than the Manager but moves much faster.
    On contact applies knockback toward the room interior (RF003 AoE Noise on fall).
    """

    fov_range = 170.0
    fov_angle = 80.0
    speed = 115.0
    color = (150, 70, 35)

    KNOCKBACK_FORCE = 500.0
    CONTACT_RADIUS = TILE_SIZE

    def __init__(self, waypoints: list[tuple[float, float]],
                 room_center: tuple[float, float] = (0.0, 0.0)) -> None:
        super().__init__(waypoints)
        self._room_center = pygame.math.Vector2(room_center)

    def try_knockback(self, player) -> bool:
        """
        If player is within CONTACT_RADIUS, push them away from Father
        (which is toward the room interior in Phase 1).
        Returns True if knockback was applied.
        """
        diff = player.pos - self.pos
        dist = diff.length()
        if dist > self.CONTACT_RADIUS or dist == 0:
            return False
        push_dir = diff.normalize()
        player.receive_knockback(push_dir, self.KNOCKBACK_FORCE)
        return True
