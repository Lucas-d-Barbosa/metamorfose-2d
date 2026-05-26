from typing import Literal

import pygame

from settings import (
    ACCELERATION,
    APPLE_SPEED_PENALTY,
    APPLE_STAMINA_PENALTY,
    BASE_SPEED,
    BLUE,
    CEILING_STAMINA_MODIFIER,
    FRICTION,
    GREEN,
    HUNGER_DECAY_RATE,
    RED,
    STAMINA_DECAY_RATE,
    TILE_SIZE,
    WHITE,
)

ZLevel = Literal["floor", "ceiling"]


class Player(pygame.sprite.Sprite):
    def __init__(self, x: float, y: float) -> None:
        super().__init__()

        self.image = pygame.Surface((TILE_SIZE - 4, TILE_SIZE - 4), pygame.SRCALPHA)
        self._build_sprite()
        self.rect = self.image.get_rect(center=(x, y))
        self.hitbox = self.rect.inflate(-8, -8)

        self.pos = pygame.math.Vector2(x, y)
        self.velocity = pygame.math.Vector2(0.0, 0.0)
        self.direction = pygame.math.Vector2(0.0, 0.0)

        self.z_level: ZLevel = "floor"
        self.hidden: bool = False
        self.facing_angle: float = 0.0  # degrees, 0 = right

        # Stats
        self.max_stamina: float = 100.0
        self.current_stamina: float = 100.0
        self.max_hunger: float = 100.0
        self.current_hunger: float = 100.0

        # Debuffs (loaded from save)
        self.apple_debuff: bool = False

        # Noise emission (read by sound propagation system)
        self.noise_radius: float = 0.0

    # -------------------------------------------------------------------------
    # Setup
    # -------------------------------------------------------------------------

    def _build_sprite(self) -> None:
        self.image.fill((0, 0, 0, 0))
        size = self.image.get_width()
        pygame.draw.circle(self.image, GREEN, (size // 2, size // 2), size // 2)
        # direction indicator (small dot in front)
        pygame.draw.circle(self.image, WHITE, (size // 2, size // 4), 3)

    def apply_apple_debuff(self) -> None:
        if self.apple_debuff:
            return
        self.apple_debuff = True
        self.max_stamina *= APPLE_STAMINA_PENALTY
        self.current_stamina = min(self.current_stamina, self.max_stamina)

    # -------------------------------------------------------------------------
    # Z-level (floor ↔ ceiling)
    # -------------------------------------------------------------------------

    def go_to_ceiling(self) -> None:
        if self.z_level != "ceiling":
            self.z_level = "ceiling"

    def go_to_floor(self) -> None:
        if self.z_level != "floor":
            self.z_level = "floor"

    @property
    def effective_speed(self) -> float:
        speed = BASE_SPEED
        if self.apple_debuff:
            speed *= APPLE_SPEED_PENALTY
        return speed

    # -------------------------------------------------------------------------
    # Input
    # -------------------------------------------------------------------------

    def _read_input(self) -> None:
        keys = pygame.key.get_pressed()
        self.direction.x = 0.0
        self.direction.y = 0.0
        if keys[pygame.K_a]:
            self.direction.x -= 1.0
        if keys[pygame.K_d]:
            self.direction.x += 1.0
        if keys[pygame.K_w]:
            self.direction.y -= 1.0
        if keys[pygame.K_s]:
            self.direction.y += 1.0
        if self.direction.length_squared() > 0:
            self.direction = self.direction.normalize()

    # -------------------------------------------------------------------------
    # Update
    # -------------------------------------------------------------------------

    def update(self, dt: float) -> None:
        self._read_input()
        self._move(dt)
        self._update_stats(dt)
        self._update_facing()

    def _move(self, dt: float) -> None:
        target_velocity = self.direction * self.effective_speed
        self.velocity = self.velocity.lerp(target_velocity, min(1.0, FRICTION * dt))
        self.pos += self.velocity * dt
        self.rect.center = (round(self.pos.x), round(self.pos.y))
        self.hitbox.center = self.rect.center

    def _update_stats(self, dt: float) -> None:
        moving = self.direction.length_squared() > 0

        stamina_decay = STAMINA_DECAY_RATE * (1.0 if moving else 0.2)
        if self.z_level == "ceiling":
            stamina_decay *= CEILING_STAMINA_MODIFIER
        self.current_stamina = max(0.0, self.current_stamina - stamina_decay * dt)

        hunger_decay = HUNGER_DECAY_RATE * (1.0 if moving else 0.3)
        self.current_hunger = max(0.0, self.current_hunger - hunger_decay * dt)

        self.noise_radius = 0.0
        if moving and not self.hidden:
            from settings import FOOTSTEP_NOISE_RADIUS
            self.noise_radius = FOOTSTEP_NOISE_RADIUS

    def _update_facing(self) -> None:
        if self.direction.length_squared() > 0:
            import math
            self.facing_angle = math.degrees(math.atan2(self.direction.y, self.direction.x))

    def receive_knockback(self, direction: pygame.math.Vector2,
                          force: float) -> None:
        if direction.length_squared() > 0:
            self.velocity += direction.normalize() * force

    # -------------------------------------------------------------------------
    # Collision helpers (called by scene after movement)
    # -------------------------------------------------------------------------

    def move_x(self, dx: float) -> None:
        self.pos.x += dx
        self.rect.centerx = round(self.pos.x)
        self.hitbox.centerx = self.rect.centerx

    def move_y(self, dy: float) -> None:
        self.pos.y += dy
        self.rect.centery = round(self.pos.y)
        self.hitbox.centery = self.rect.centery

    # -------------------------------------------------------------------------
    # Draw HUD (called by scene after main draw)
    # -------------------------------------------------------------------------

    def draw_hud(self, surface: pygame.Surface) -> None:
        bar_w, bar_h, pad, gap = 180, 12, 10, 5

        # Stamina
        self._draw_bar(surface, pad, pad, bar_w, bar_h,
                       self.current_stamina, self.max_stamina, RED, "STA")
        # Hunger
        self._draw_bar(surface, pad, pad + bar_h + gap, bar_w, bar_h,
                       self.current_hunger, self.max_hunger, BLUE, "FOM")

        # Z-level indicator
        label = "TETO" if self.z_level == "ceiling" else "CHÃO"
        color = (180, 220, 255) if self.z_level == "ceiling" else (200, 180, 120)
        font = pygame.font.SysFont("monospace", 11)
        surf = font.render(label, True, color)
        surface.blit(surf, (pad, pad + (bar_h + gap) * 2 + 4))

    def _draw_bar(self, surface: pygame.Surface, x: int, y: int,
                  w: int, h: int, current: float, maximum: float,
                  color: tuple, label: str) -> None:
        ratio = 0.0 if maximum <= 0 else current / maximum
        pygame.draw.rect(surface, (50, 50, 50), (x, y, w, h))
        pygame.draw.rect(surface, color, (x, y, int(w * ratio), h))
        pygame.draw.rect(surface, WHITE, (x, y, w, h), 1)
        font = pygame.font.SysFont("monospace", 10)
        text = font.render(f"{label} {int(current)}/{int(maximum)}", True, WHITE)
        surface.blit(text, (x + 3, y + 1))
