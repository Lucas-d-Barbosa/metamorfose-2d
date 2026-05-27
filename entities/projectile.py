"""
Sistema de projéteis top-down.

Projectile  : base class — posição, velocidade, raio de colisão, lifetime.
AppleProjectile : RF013 — a maçã crítica arremessada pelo Pai.
"""

import math

import pygame

from settings import TILE_SIZE


class Projectile:
    RADIUS = 6.0
    SPEED = 320.0
    LIFETIME = 3.0
    COLOR = (180, 80, 40)

    def __init__(self, origin: pygame.math.Vector2,
                 target: pygame.math.Vector2) -> None:
        self.pos = pygame.math.Vector2(origin)
        diff = target - origin
        if diff.length_squared() > 0:
            self.velocity = diff.normalize() * self.SPEED
        else:
            self.velocity = pygame.math.Vector2(self.SPEED, 0)
        self._elapsed = 0.0
        self.alive = True
        self.hit = False

    def update(self, dt: float, tilemap) -> None:
        if not self.alive:
            return
        self._elapsed += dt
        if self._elapsed >= self.LIFETIME:
            self.alive = False
            return
        self.pos += self.velocity * dt
        if tilemap.is_solid_at(self.pos.x, self.pos.y):
            self.alive = False

    def check_hit(self, player_pos: pygame.math.Vector2,
                  player_radius: float = 10.0) -> bool:
        if not self.alive:
            return False
        dist = (self.pos - player_pos).length()
        if dist <= self.RADIUS + player_radius:
            self.alive = False
            self.hit = True
            return True
        return False

    def draw(self, surface: pygame.Surface,
             camera_offset: pygame.math.Vector2) -> None:
        if not self.alive:
            return
        sp = self.pos + camera_offset
        # Wobble radius for visual interest
        wobble = math.sin(self._elapsed * 18.0) * 1.5
        pygame.draw.circle(surface, self.COLOR,
                           (int(sp.x), int(sp.y)),
                           int(self.RADIUS + wobble))
        pygame.draw.circle(surface, (230, 120, 60),
                           (int(sp.x), int(sp.y)),
                           int(self.RADIUS + wobble), 1)


class AppleProjectile(Projectile):
    """RF013 — a maçã crítica. Ao acertar aplica debuff permanente."""
    RADIUS = 7.0
    SPEED = 280.0
    LIFETIME = 2.5
    COLOR = (200, 55, 30)
    IS_APPLE = True
