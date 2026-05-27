"""
RF011 — Hitboxes de lixo com tosse.

TrashZone  : rect de lixo; player parado/movendo dentro por 1.5s → tosse.
DustParticle: partícula de poeira visual, gerada ao atravessar lixo.
"""

import math
import random

import pygame

from settings import TILE_SIZE, TRASH_COUGH_DELAY


class TrashZone:
    COUGH_COOLDOWN = 4.0  # segundos antes de poder tossir de novo na mesma zona

    def __init__(self, rect: pygame.Rect | tuple, label: str = "") -> None:
        self.rect = pygame.Rect(rect)
        self.label = label
        self._timer: float = 0.0
        self._cooldown: float = 0.0

    def update(self, dt: float, hitbox: pygame.Rect,
               player_moving: bool) -> bool:
        """
        Returns True exactly once when the cough should trigger.
        Timer only advances while the player is moving (rubbing against trash).
        """
        if self._cooldown > 0:
            self._cooldown -= dt
            self._timer = 0.0
            return False

        if not self.rect.colliderect(hitbox):
            self._timer = 0.0
            return False

        if player_moving:
            self._timer += dt
        else:
            # Still decays slowly when idle — discourages sneaking too
            self._timer = max(0.0, self._timer - dt * 0.4)

        if self._timer >= TRASH_COUGH_DELAY:
            self._timer = 0.0
            self._cooldown = self.COUGH_COOLDOWN
            return True

        return False

    @property
    def timer_ratio(self) -> float:
        return min(1.0, self._timer / TRASH_COUGH_DELAY)

    def draw_debug(self, surface: pygame.Surface,
                   camera_offset: pygame.math.Vector2) -> None:
        ox, oy = int(camera_offset.x), int(camera_offset.y)
        sr = self.rect.move(ox, oy)
        dbg = pygame.Surface((sr.width, sr.height), pygame.SRCALPHA)
        fill_a = int(40 + 60 * self.timer_ratio)
        dbg.fill((160, 100, 40, fill_a))
        pygame.draw.rect(dbg, (200, 140, 60, 140), dbg.get_rect(), 1)
        surface.blit(dbg, sr.topleft)
        font = pygame.font.SysFont("monospace", 9)
        lbl = font.render(f"lixo:{self.label}", True, (200, 150, 80))
        surface.blit(lbl, (sr.x + 2, sr.y + 2))


class DustParticle:
    def __init__(self, x: float, y: float) -> None:
        self.pos = pygame.math.Vector2(x, y)
        spread = random.uniform(-18, 18)
        self.vel = pygame.math.Vector2(spread, random.uniform(-45, -20))
        self.lifetime = random.uniform(0.35, 0.75)
        self._elapsed: float = 0.0
        self.radius = random.randint(2, 4)
        shade = random.randint(140, 190)
        self._color = (shade, shade - 20, shade - 40)

    @property
    def alive(self) -> bool:
        return self._elapsed < self.lifetime

    def update(self, dt: float) -> None:
        self._elapsed += dt
        self.pos += self.vel * dt
        self.vel.x *= (1 - 2.0 * dt)   # horizontal drag
        self.vel.y += 15.0 * dt          # slight gravity

    def draw(self, surface: pygame.Surface,
             camera_offset: pygame.math.Vector2) -> None:
        if not self.alive:
            return
        ratio = self._elapsed / self.lifetime
        alpha = int(160 * (1 - ratio))
        sp = self.pos + camera_offset
        sz = self.radius * 2
        psurf = pygame.Surface((sz, sz), pygame.SRCALPHA)
        pygame.draw.circle(psurf, (*self._color, alpha),
                           (self.radius, self.radius), self.radius)
        surface.blit(psurf, (int(sp.x) - self.radius, int(sp.y) - self.radius))


# ---------------------------------------------------------------------------
# Phase 3 trash zones — alinhadas com phase3_room() em map/layouts.py
# ---------------------------------------------------------------------------
def build_phase3_trash_zones(tile_size: int = TILE_SIZE) -> list[TrashZone]:
    ts = tile_size
    return [
        TrashZone(pygame.Rect( 5*ts, 5*ts, 3*ts, 2*ts), label="caixotes-esq"),
        TrashZone(pygame.Rect(14*ts, 5*ts, 3*ts, 2*ts), label="caixotes-centro"),
        TrashZone(pygame.Rect(28*ts, 5*ts, 3*ts, 2*ts), label="caixotes-dir"),
        TrashZone(pygame.Rect( 5*ts,10*ts, 3*ts, 2*ts), label="guarda-roupa-resto"),
        TrashZone(pygame.Rect(20*ts,10*ts, 3*ts, 2*ts), label="escrivaninha-resto"),
        TrashZone(pygame.Rect(10*ts,16*ts, 3*ts, 2*ts), label="entulho-esq"),
        TrashZone(pygame.Rect(26*ts,16*ts, 3*ts, 2*ts), label="entulho-dir"),
    ]


# ---------------------------------------------------------------------------
# Phase 4 trash zones — labirinto denso, mesma lógica
# ---------------------------------------------------------------------------
def build_phase4_trash_zones(tile_size: int = TILE_SIZE) -> list[TrashZone]:
    ts = tile_size
    return [
        TrashZone(pygame.Rect( 5*ts, 5*ts, 4*ts, 2*ts), label="p4-topo-esq"),
        TrashZone(pygame.Rect(13*ts, 5*ts, 4*ts, 2*ts), label="p4-topo-centro"),
        TrashZone(pygame.Rect(23*ts, 5*ts, 4*ts, 2*ts), label="p4-topo-dir"),
        TrashZone(pygame.Rect( 9*ts,10*ts, 4*ts, 2*ts), label="p4-meio-esq"),
        TrashZone(pygame.Rect(19*ts,10*ts, 4*ts, 2*ts), label="p4-meio-centro"),
        TrashZone(pygame.Rect(29*ts,10*ts, 4*ts, 2*ts), label="p4-meio-dir"),
        TrashZone(pygame.Rect( 6*ts,15*ts, 4*ts, 2*ts), label="p4-baixo-esq"),
        TrashZone(pygame.Rect(16*ts,15*ts, 4*ts, 2*ts), label="p4-baixo-centro"),
        TrashZone(pygame.Rect(26*ts,15*ts, 4*ts, 2*ts), label="p4-baixo-dir"),
    ]
