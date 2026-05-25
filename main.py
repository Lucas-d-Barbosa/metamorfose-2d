import pygame

from settings import BLACK, FPS, SCREEN_HEIGHT, SCREEN_WIDTH


class Game:
	def __init__(self) -> None:
		pygame.init()
		self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
		pygame.display.set_caption("Metamorfose 2D")
		self.clock = pygame.time.Clock()
		self.running = True

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
		_ = dt

	def draw(self) -> None:
		self.screen.fill(BLACK)
		pygame.display.flip()


if __name__ == "__main__":
	Game().run()
