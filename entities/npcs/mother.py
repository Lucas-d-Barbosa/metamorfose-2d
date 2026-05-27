"""
NPC Mãe — patrulha lenta, FOV amplo.
Durante a Missão do Quadro ela é "detectable": se Gregor entrar no seu FOV
o evento falha.
"""

from entities.npc import NPC


class Mother(NPC):
    fov_range = 160.0
    fov_angle = 90.0
    speed = 50.0
    color = (180, 140, 160)
