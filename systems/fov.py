"""
2D top-down raycasting FOV for NPCs.

check_los  — returns True if two world points have clear line of sight.
is_in_fov  — returns True if a target is inside an NPC's vision cone.
draw_fov   — renders the vision cone to a surface (screen space).
"""

import math

import pygame

from settings import TILE_SIZE


def check_los(start: pygame.math.Vector2,
              end: pygame.math.Vector2,
              tilemap) -> bool:
    """
    DDA-style LOS check between two world points.
    Returns True if no solid tile blocks the path.
    """
    diff = end - start
    distance = diff.length()
    if distance == 0:
        return True

    direction = diff.normalize()
    step_size = TILE_SIZE // 2  # sample every half-tile
    steps = int(distance / step_size)

    for i in range(1, steps + 1):
        sample = start + direction * (i * step_size)
        if tilemap.is_solid_at(sample.x, sample.y):
            return False

    # Final check at exact end point
    if tilemap.is_solid_at(end.x, end.y):
        return False

    return True


def is_in_fov(npc_pos: pygame.math.Vector2,
              npc_angle_deg: float,
              fov_deg: float,
              fov_range: float,
              target_pos: pygame.math.Vector2,
              tilemap) -> bool:
    """
    Returns True if target_pos is inside the NPC's vision cone
    AND has clear line of sight.
    """
    diff = target_pos - npc_pos
    distance = diff.length()
    if distance > fov_range or distance == 0:
        return False

    target_angle = math.degrees(math.atan2(diff.y, diff.x))
    angle_diff = (target_angle - npc_angle_deg + 180) % 360 - 180
    if abs(angle_diff) > fov_deg / 2:
        return False

    return check_los(npc_pos, target_pos, tilemap)


def draw_fov_cone(surface: pygame.Surface,
                  npc_world_pos: pygame.math.Vector2,
                  npc_angle_deg: float,
                  fov_deg: float,
                  fov_range: float,
                  camera_offset: pygame.math.Vector2,
                  color: tuple = (255, 220, 50),
                  alpha: int = 45,
                  ray_count: int = 24) -> None:
    """
    Draws a filled, semi-transparent vision cone in screen space.
    Used in debug mode and as a subtle visual cue.
    """
    cone_surf = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
    screen_pos = npc_world_pos + camera_offset

    half_fov = fov_deg / 2
    angle_step = fov_deg / ray_count

    points = [screen_pos]
    for i in range(ray_count + 1):
        ray_angle = math.radians(npc_angle_deg - half_fov + i * angle_step)
        tip = pygame.math.Vector2(
            screen_pos.x + math.cos(ray_angle) * fov_range,
            screen_pos.y + math.sin(ray_angle) * fov_range,
        )
        points.append(tip)

    if len(points) >= 3:
        pygame.draw.polygon(cone_surf, (*color, alpha), [(p.x, p.y) for p in points])
        pygame.draw.polygon(cone_surf, (*color, alpha + 40),
                            [(p.x, p.y) for p in points], 1)

    surface.blit(cone_surf, (0, 0))
