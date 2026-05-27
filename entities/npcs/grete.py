"""
NPC Grete — mais rápida que a Mãe, FOV estreito (olha para frente).
"""

from entities.npc import NPC


class Grete(NPC):
    fov_range = 130.0
    fov_angle = 70.0
    speed = 65.0
    color = (130, 160, 180)
