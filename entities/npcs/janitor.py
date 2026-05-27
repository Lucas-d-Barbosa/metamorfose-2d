"""
RF014 — A Faxineira.

Patrulha caótica. Ao colidir com o jogador aplica knockback — nunca causa
Game Over nem eleva o estado de alerta global da casa.
"""

import pygame

from entities.npc import NPC
from settings import TILE_SIZE


class Janitor(NPC):
    fov_range = 100.0
    fov_angle = 80.0
    speed = 58.0
    color = (160, 155, 120)

    CONTACT_RADIUS = TILE_SIZE * 1.2
    KNOCKBACK_FORCE = 380.0

    def try_sweep(self, player) -> bool:
        """
        Push the player away with the broom if within contact range.
        Returns True when knockback was applied.
        Unlike Father, this never changes alert state or triggers game over.
        """
        diff = player.pos - self.pos
        dist = diff.length()
        if dist > self.CONTACT_RADIUS or dist == 0:
            return False
        player.receive_knockback(diff.normalize(), self.KNOCKBACK_FORCE)
        return True
