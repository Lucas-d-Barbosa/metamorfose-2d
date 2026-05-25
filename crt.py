import pygame


class CRT:
    def __init__(self, screen: pygame.Surface) -> None:
        self.screen = screen
        self.width = screen.get_width()
        self.height = screen.get_height()

        self.scanlines = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.scanlines.fill((0, 0, 0, 0))
        for y in range(0, self.height, 2):
            pygame.draw.line(self.scanlines, (0, 0, 0, 255), (0, y), (self.width, y))
        self.scanlines.set_alpha(35)

        self.vignette = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.vignette.fill((0, 0, 0, 0))
        border = max(24, min(self.width, self.height) // 12)
        pygame.draw.rect(
            self.vignette,
            (0, 0, 0, 255),
            (0, 0, self.width, self.height),
            border,
        )
        self.vignette.set_alpha(70)

    def draw(self) -> None:
        self.screen.blit(self.scanlines, (0, 0))
        self.screen.blit(self.vignette, (0, 0))
