import pygame

from crt import CRT
from player import Player
from settings import FPS, GRAY, SCREEN_HEIGHT, SCREEN_WIDTH


class Game:
	def __init__(self) -> None:
		pygame.init()
		self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
		pygame.display.set_caption("Metamorfose 2D")
		self.clock = pygame.time.Clock()
		self.running = True
		self.crt = CRT(self.screen)

		self.all_sprites = pygame.sprite.Group()
		self.player = Player(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
		self.all_sprites.add(self.player)

	def run(self) -> None:
		while self.running:
			dt = self.clock.tick(FPS) / 1000.0
			self.events()
			self.update(dt)
			self.draw()

		pygame.quit()

	def events(self) -> None:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				self.running = False

	def update(self, dt: float) -> None:
		self.all_sprites.update(dt)

	def draw(self) -> None:
		self.screen.fill(GRAY)
		self.all_sprites.draw(self.screen)
		self.crt.draw()
		pygame.display.flip()


if __name__ == "__main__":
	Game().run()
