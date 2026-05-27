"""
Os Três Inquilinos — patrulha sincronizada, alerta compartilhado.

GDD §7: FOV dos Inquilinos deve ser 30% maior que o da família.
Referência: Manager (fov_angle=100°, fov_range=220) × 1.3 = 130° / 286.

Alerta compartilhado: quando qualquer Inquilino entra em ALERT, todos os
outros têm sua suspicion elevada a 100 imediatamente.
"""

import pygame

from entities.npc import NPC
from systems.stealth import AlertState


class Tenant(NPC):
    fov_range = 286.0   # Manager 220 × 1.3
    fov_angle = 130.0   # Manager 100 × 1.3
    speed = 72.0
    color = (95, 85, 125)   # cinza-arroxeado


class TenantGroup:
    """
    Wraps three Tenant NPCs with:
    - Independent waypoint patrols
    - Synchronized alert: one sees → all know
    """

    def __init__(self, waypoint_sets: list[list[tuple[float, float]]]) -> None:
        assert len(waypoint_sets) == 3, "TenantGroup expects exactly 3 waypoint lists"
        self.tenants = [Tenant(wps) for wps in waypoint_sets]

        # Stagger starting waypoint index so they spread across the room
        for i, t in enumerate(self.tenants):
            t._wp_index = i % max(1, len(waypoint_sets[i]))

    # ------------------------------------------------------------------

    def update(self, dt: float, tilemap, player) -> None:
        for t in self.tenants:
            t.update(dt, tilemap, player)
        self._sync_alert()

    def _sync_alert(self) -> None:
        alerted = any(t.alert.state == AlertState.ALERT for t in self.tenants)
        if not alerted:
            return
        # Broadcast: push all non-alerted tenants to ALERT instantly
        for t in self.tenants:
            if t.alert.state != AlertState.ALERT:
                t.alert.suspicion = 100.0

    # ------------------------------------------------------------------
    # Proxy helpers so the scene can treat the group like a list

    def __iter__(self):
        return iter(self.tenants)

    def __len__(self) -> int:
        return len(self.tenants)

    @property
    def alert_states(self) -> list[AlertState]:
        return [t.alert.state for t in self.tenants]

    def any_alerted(self) -> bool:
        return any(t.alert.state == AlertState.ALERT for t in self.tenants)

    def draw_fov_all(self, surface: pygame.Surface,
                     camera_offset: pygame.math.Vector2) -> None:
        for t in self.tenants:
            t.draw_fov(surface, camera_offset)

    def draw_sprites_all(self, surface: pygame.Surface,
                         camera: "Camera") -> None:
        for t in self.tenants:
            surface.blit(t.image, camera.apply_rect(t.rect))
            t.draw_alert_bar(surface, camera.offset)
