import pygame
from abc import ABC, abstractmethod


class BaseScene(ABC):
    """Abstract base for all game scenes/phases."""

    def __init__(self, game: "Game") -> None:  # type: ignore[name-defined]
        self.game = game
        self.next_scene: str | None = None

    @abstractmethod
    def handle_event(self, event: pygame.event.Event) -> None: ...

    @abstractmethod
    def update(self, dt: float) -> None: ...

    @abstractmethod
    def draw(self, surface: pygame.Surface) -> None: ...

    def transition_to(self, scene_name: str) -> None:
        self.next_scene = scene_name
