import math

import pygame

from settings import TILE_SIZE
from systems.fov import draw_fov_cone, is_in_fov
from systems.stealth import AlertState, AlertStateMachine


class NPC(pygame.sprite.Sprite):
    """
    Base top-down NPC with waypoint patrol and FOV-based stealth detection.

    Subclasses override:
        fov_range, fov_angle, speed, color
    """

    fov_range: float = 180.0
    fov_angle: float = 90.0
    speed: float = 70.0
    color: tuple[int, int, int] = (180, 120, 60)

    def __init__(self, waypoints: list[tuple[float, float]]) -> None:
        super().__init__()
        assert waypoints, "NPC needs at least one waypoint"

        self.image = pygame.Surface((TILE_SIZE - 8, TILE_SIZE - 8), pygame.SRCALPHA)
        self._redraw_sprite()
        start = waypoints[0]
        self.rect = self.image.get_rect(center=start)

        self.pos = pygame.math.Vector2(start)
        self.velocity = pygame.math.Vector2(0.0, 0.0)
        self.facing_angle: float = 0.0  # degrees, 0 = right

        self.waypoints = [pygame.math.Vector2(w) for w in waypoints]
        self._wp_index: int = 0
        self._wait_timer: float = 0.0
        self._wait_at_wp: float = 1.2  # seconds to pause at each waypoint

        self.alert = AlertStateMachine()
        self.debug_fov: bool = False

    def _redraw_sprite(self) -> None:
        self.image.fill((0, 0, 0, 0))
        size = self.image.get_width()
        pygame.draw.circle(self.image, self.color, (size // 2, size // 2), size // 2)
        pygame.draw.circle(self.image, (255, 255, 255),
                           (size // 2, size // 4), 3)

    # -------------------------------------------------------------------------
    # Update
    # -------------------------------------------------------------------------

    def update(self, dt: float, tilemap, player) -> None:
        sees = is_in_fov(self.pos, self.facing_angle, self.fov_angle,
                         self.fov_range, player.pos, tilemap)
        hears, source = player._last_heard_source if hasattr(player, '_last_heard_source') else (False, None)

        prev_state = self.alert.state
        new_state = self.alert.tick(
            dt,
            sees_player=sees and not player.hidden,
            hears_player=False,
            player_pos=(player.pos.x, player.pos.y),
        )

        if new_state in (AlertState.PATROL, AlertState.SUSPICIOUS):
            self._patrol(dt, tilemap)
        elif new_state == AlertState.ALERT:
            self._chase(dt, player.pos, tilemap)
        elif new_state == AlertState.SEARCH:
            self._search(dt, tilemap)

        self.rect.center = (round(self.pos.x), round(self.pos.y))
        self._redraw_sprite()
        # Draw alert color dot
        dot_color = self.alert.color
        pygame.draw.circle(self.image,
                           dot_color,
                           (self.image.get_width() // 2, 4), 3)

    # -------------------------------------------------------------------------
    # Patrol
    # -------------------------------------------------------------------------

    def _patrol(self, dt: float, tilemap) -> None:
        target = self.waypoints[self._wp_index]
        diff = target - self.pos
        dist = diff.length()

        if dist < 4.0:
            self._wait_timer += dt
            if self._wait_timer >= self._wait_at_wp:
                self._wait_timer = 0.0
                self._wp_index = (self._wp_index + 1) % len(self.waypoints)
            return

        direction = diff.normalize()
        self.facing_angle = math.degrees(math.atan2(direction.y, direction.x))
        self.pos += direction * self.speed * dt

    # -------------------------------------------------------------------------
    # Chase
    # -------------------------------------------------------------------------

    def _chase(self, dt: float, player_pos: pygame.math.Vector2, tilemap) -> None:
        diff = player_pos - self.pos
        dist = diff.length()
        if dist < 2.0:
            return
        direction = diff.normalize()
        self.facing_angle = math.degrees(math.atan2(direction.y, direction.x))
        self.pos += direction * self.speed * 1.6 * dt

    # -------------------------------------------------------------------------
    # Search
    # -------------------------------------------------------------------------

    def _search(self, dt: float, tilemap) -> None:
        if self.alert.last_known_pos is None:
            return
        target = pygame.math.Vector2(self.alert.last_known_pos)
        diff = target - self.pos
        dist = diff.length()
        if dist < 4.0:
            return
        direction = diff.normalize()
        self.facing_angle = math.degrees(math.atan2(direction.y, direction.x))
        self.pos += direction * self.speed * 0.8 * dt

    # -------------------------------------------------------------------------
    # Draw
    # -------------------------------------------------------------------------

    def draw_fov(self, surface: pygame.Surface,
                 camera_offset: pygame.math.Vector2) -> None:
        color = {
            AlertState.PATROL:     (255, 220, 50),
            AlertState.SUSPICIOUS: (255, 160, 0),
            AlertState.ALERT:      (220, 40, 40),
            AlertState.SEARCH:     (200, 100, 0),
        }[self.alert.state]

        alpha = 55 if self.debug_fov else 35
        draw_fov_cone(
            surface, self.pos, self.facing_angle,
            self.fov_angle, self.fov_range,
            camera_offset, color=color, alpha=alpha,
        )

    def draw_alert_bar(self, surface: pygame.Surface,
                       camera_offset: pygame.math.Vector2) -> None:
        if self.alert.suspicion < 1.0:
            return
        screen_pos = self.pos + camera_offset
        bar_w, bar_h = 32, 4
        x = int(screen_pos.x) - bar_w // 2
        y = int(screen_pos.y) - self.image.get_height() // 2 - 8
        pygame.draw.rect(surface, (40, 40, 40), (x, y, bar_w, bar_h))
        fill_w = int(bar_w * self.alert.suspicion_ratio)
        pygame.draw.rect(surface, self.alert.color, (x, y, fill_w, bar_h))
        pygame.draw.rect(surface, (200, 200, 200), (x, y, bar_w, bar_h), 1)
