from entities.npc import NPC


class Manager(NPC):
    """O Gerente — fast, wide FOV, patrols near the door."""

    fov_range = 220.0
    fov_angle = 100.0
    speed = 85.0
    color = (140, 100, 60)
