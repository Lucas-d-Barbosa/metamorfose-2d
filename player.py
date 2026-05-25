from typing import Literal

import pygame

from settings import BASE_SPEED, CEILING_STAMINA_MODIFIER, GRAVITY, GREEN, RED, TILE_SIZE, WHITE, BLUE

State = Literal["floor", "wall_left", "wall_right", "ceiling"]
VALID_STATES: tuple[State, ...] = ("floor", "wall_left", "wall_right", "ceiling")


class Player(pygame.sprite.Sprite):
	def __init__(self, x: float, y: float) -> None:
		super().__init__()
		self.image = pygame.Surface((TILE_SIZE, TILE_SIZE))
		self.image.fill(GREEN)
		self.rect = self.image.get_rect(center=(x, y))

		self.pos = pygame.math.Vector2(x, y)
		self.velocity = pygame.math.Vector2(0.0, 0.0)
		self.direction = pygame.math.Vector2(0.0, 0.0)
		self.state: State = "floor"

		self.max_stamina = 100.0
		self.current_stamina = 100.0
		self.max_hunger = 100.0
		self.current_hunger = 100.0
		self.stamina_decay_rate = 12.0
		self.hunger_decay_rate = 6.0

	def set_state(self, new_state: State) -> None:
		if new_state not in VALID_STATES:
			return
		if new_state != self.state:
			print(f"Player state: {self.state} -> {new_state}")
			self.state = new_state

	def input(self) -> None:
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

	def update(self, dt: float) -> None:
		self.input()
		move_dir = pygame.math.Vector2(0.0, 0.0)
		gravity_dir = pygame.math.Vector2(0.0, 0.0)

		if self.state == "floor":
			move_dir.x = self.direction.x
			gravity_dir.y = 1.0
		elif self.state == "ceiling":
			move_dir.x = -self.direction.x
			gravity_dir.y = -1.0
		elif self.state == "wall_left":
			move_dir.y = self.direction.y
			gravity_dir.x = -1.0
		elif self.state == "wall_right":
			move_dir.y = self.direction.y
			gravity_dir.x = 1.0

		if move_dir.length_squared() > 0.0:
			move_dir = move_dir.normalize()

		if self.state in ("floor", "ceiling"):
			self.velocity.x = move_dir.x * BASE_SPEED
			self.velocity.y += gravity_dir.y * GRAVITY * dt
		else:
			self.velocity.y = move_dir.y * BASE_SPEED
			self.velocity.x += gravity_dir.x * GRAVITY * dt

		self.pos += self.velocity * dt
		self.rect.center = (round(self.pos.x), round(self.pos.y))

		move_strength = min(1.0, self.direction.length())
		stamina_decay = self.stamina_decay_rate * move_strength
		if self.state == "ceiling":
			stamina_decay *= CEILING_STAMINA_MODIFIER
		self.current_stamina = max(0.0, self.current_stamina - stamina_decay * dt)
		self.current_hunger = max(0.0, self.current_hunger - self.hunger_decay_rate * move_strength * dt)

	def draw_ui(self, surface: pygame.Surface) -> None:
		bar_width = 200
		bar_height = 16
		padding = 10

		stamina_ratio = 0.0 if self.max_stamina <= 0.0 else self.current_stamina / self.max_stamina
		hunger_ratio = 0.0 if self.max_hunger <= 0.0 else self.current_hunger / self.max_hunger

		stamina_rect = pygame.Rect(padding, padding, int(bar_width * stamina_ratio), bar_height)
		stamina_bg = pygame.Rect(padding, padding, bar_width, bar_height)
		pygame.draw.rect(surface, WHITE, stamina_bg, 2)
		pygame.draw.rect(surface, RED, stamina_rect)

		hunger_rect = pygame.Rect(padding, padding + bar_height + 6, int(bar_width * hunger_ratio), bar_height)
		hunger_bg = pygame.Rect(padding, padding + bar_height + 6, bar_width, bar_height)
		pygame.draw.rect(surface, WHITE, hunger_bg, 2)
		pygame.draw.rect(surface, BLUE, hunger_rect)
