import pygame

from scene.base_scene import BaseScene
from settings import AMBER, BLACK, DARK_GRAY, SCREEN_HEIGHT, SCREEN_WIDTH, WHITE


class MenuScene(BaseScene):
    def __init__(self, game) -> None:
        super().__init__(game)
        self._title_font = pygame.font.SysFont("serif", 52)
        self._subtitle_font = pygame.font.SysFont("monospace", 18)
        self._hint_font = pygame.font.SysFont("monospace", 14)
        self._blink_timer = 0.0
        self._blink_visible = True

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                self.transition_to("profile_select")
            elif event.key == pygame.K_ESCAPE:
                self.game.running = False

    def update(self, dt: float) -> None:
        self._blink_timer += dt
        if self._blink_timer >= 0.6:
            self._blink_timer = 0.0
            self._blink_visible = not self._blink_visible

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill(DARK_GRAY)

        # Title
        title = self._title_font.render("Metamorfose", True, AMBER)
        sub = self._subtitle_font.render("Uma adaptação de A Metamorfose, de Franz Kafka", True, (160, 140, 100))
        surface.blit(title, title.get_rect(centerx=SCREEN_WIDTH // 2, centery=SCREEN_HEIGHT // 2 - 60))
        surface.blit(sub, sub.get_rect(centerx=SCREEN_WIDTH // 2, centery=SCREEN_HEIGHT // 2))

        if self._blink_visible:
            hint = self._hint_font.render("Pressione ENTER para começar", True, WHITE)
            surface.blit(hint, hint.get_rect(centerx=SCREEN_WIDTH // 2, centery=SCREEN_HEIGHT // 2 + 60))

        esc = self._hint_font.render("ESC — Sair", True, (100, 100, 100))
        surface.blit(esc, (20, SCREEN_HEIGHT - 30))
