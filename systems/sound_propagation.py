"""
Circular noise propagation.

A NoiseEvent is created when the player (or any entity) makes a sound.
Each NPC queries the system to know if it's within range.
Walls with the 'sound_isolating' flag block propagation.
"""

import math

import pygame


class NoiseEvent:
    def __init__(self, pos: pygame.math.Vector2, radius: float,
                 lifetime: float = 0.25) -> None:
        self.pos = pygame.math.Vector2(pos)
        self.radius = radius
        self.lifetime = lifetime
        self._elapsed = 0.0

    @property
    def alive(self) -> bool:
        return self._elapsed < self.lifetime

    def tick(self, dt: float) -> None:
        self._elapsed += dt


class SoundPropagationSystem:
    """
    Collects noise events each frame and lets NPCs query whether they
    can hear anything.
    """

    def __init__(self) -> None:
        self._events: list[NoiseEvent] = []

    def emit(self, pos: pygame.math.Vector2, radius: float,
             lifetime: float = 0.25) -> None:
        self._events.append(NoiseEvent(pos, radius, lifetime))

    def update(self, dt: float) -> None:
        for event in self._events:
            event.tick(dt)
        self._events = [e for e in self._events if e.alive]

    def heard_at(self, listener_pos: pygame.math.Vector2,
                 tilemap) -> tuple[bool, pygame.math.Vector2 | None]:
        """
        Returns (heard: bool, approximate_source: Vector2 | None).
        Does a basic wall check: if any wall tile sits between the
        listener and the source the sound is blocked.
        """
        from systems.fov import check_los

        for event in self._events:
            dist = (listener_pos - event.pos).length()
            if dist <= event.radius:
                if check_los(listener_pos, event.pos, tilemap):
                    return True, event.pos
        return False, None

    def draw_debug(self, surface: pygame.Surface,
                   camera_offset: pygame.math.Vector2) -> None:
        debug_surf = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        for event in self._events:
            screen_pos = event.pos + camera_offset
            ratio = event._elapsed / event.lifetime
            alpha = int(80 * (1 - ratio))
            pygame.draw.circle(
                debug_surf,
                (200, 200, 255, alpha),
                (int(screen_pos.x), int(screen_pos.y)),
                int(event.radius),
                2,
            )
        surface.blit(debug_surf, (0, 0))
