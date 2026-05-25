import pygame

from settings import BASE_SPEED, GREEN, TILE_SIZE


class Player(pygame.sprite.Sprite):
	def __init__(self, x: float, y: float) -> None:
		super().__init__()
		self.image = pygame.Surface((TILE_SIZE, TILE_SIZE))
		self.image.fill(GREEN)
		self.rect = self.image.get_rect(center=(x, y))

		self.pos = pygame.math.Vector2(x, y)
		self.velocity = pygame.math.Vector2(0.0, 0.0)
		self.direction = pygame.math.Vector2(0.0, 0.0)

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

		if self.direction.length_squared() > 0.0:
			self.direction = self.direction.normalize()

	def update(self, dt: float) -> None:
		self.input()
		self.velocity = self.direction * BASE_SPEED
		self.pos += self.velocity * dt
		self.rect.center = (round(self.pos.x), round(self.pos.y))
