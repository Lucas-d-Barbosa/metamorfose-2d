import pygame

from crt import CRT
from scene.base_scene import BaseScene
from scene.game_over import GameOverScene
from scene.menu import MenuScene
from scene.phase1 import Phase1Scene
from settings import FPS, SCREEN_HEIGHT, SCREEN_WIDTH


_SCENE_REGISTRY: dict[str, type[BaseScene]] = {
    "menu": MenuScene,
    "phase1": Phase1Scene,
    "game_over": GameOverScene,
}


class Game:
    def __init__(self) -> None:
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Metamorfose 2D")
        self.clock = pygame.time.Clock()
        self.running = True
        self.crt = CRT(self.screen)
        self.current_scene: BaseScene = MenuScene(self)

    # -------------------------------------------------------------------------

    def run(self) -> None:
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0
            self._handle_events()
            self._update(dt)
            self._draw()
        pygame.quit()

    def _handle_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            self.current_scene.handle_event(event)

    def _update(self, dt: float) -> None:
        self.current_scene.update(dt)
        if self.current_scene.next_scene:
            self._transition(self.current_scene.next_scene)

    def _draw(self) -> None:
        self.current_scene.draw(self.screen)
        self.crt.draw()
        pygame.display.flip()

    def _transition(self, scene_name: str) -> None:
        scene_class = _SCENE_REGISTRY.get(scene_name)
        if scene_class is None:
            raise ValueError(f"Unknown scene: '{scene_name}'")
        self.current_scene = scene_class(self)

    # -------------------------------------------------------------------------

    def register_scene(self, name: str, scene_class: type[BaseScene]) -> None:
        """Allows phases to register themselves without editing this file."""
        _SCENE_REGISTRY[name] = scene_class
