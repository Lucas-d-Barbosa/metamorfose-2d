"""
RF008 — Zonas de Escuta e sistema geral de triggers.

TriggerZone  : base class, rect + one-shot flag.
ListeningZone: inactivity trigger; player must stand still for `required_still`
               seconds inside the zone to fire the dialogue queue.
"""

import pygame


class TriggerZone:
    def __init__(self, rect: pygame.Rect | tuple,
                 label: str = "", one_shot: bool = True) -> None:
        self.rect = pygame.Rect(rect)
        self.label = label
        self.one_shot = one_shot
        self.activated = False

    def is_inside(self, hitbox: pygame.Rect) -> bool:
        return self.rect.colliderect(hitbox)

    def reset(self) -> None:
        self.activated = False

    def draw_debug(self, surface: pygame.Surface,
                   camera_offset: pygame.math.Vector2) -> None:
        ox, oy = int(camera_offset.x), int(camera_offset.y)
        sr = self.rect.move(ox, oy)
        dbg = pygame.Surface((sr.width, sr.height), pygame.SRCALPHA)
        dbg.fill((80, 180, 255, 30))
        pygame.draw.rect(dbg, (80, 180, 255, 120), dbg.get_rect(), 1)
        surface.blit(dbg, sr.topleft)
        font = pygame.font.SysFont("monospace", 9)
        lbl = font.render(f"trg:{self.label}", True, (80, 180, 255))
        surface.blit(lbl, (sr.x + 2, sr.y + 2))


class ListeningZone(TriggerZone):
    """
    RF008 — Player must remain still inside the zone for `required_still`
    seconds. On activation, the dialogue queue is returned once and the zone
    is marked done (one_shot=True by default).

    Usage in scene.update(dt):
        fired = zone.update(dt, player.hitbox, player.velocity)
        if fired:
            for speaker, text in fired:
                dialogue.show_dialogue(speaker, text)
    """

    IDLE_THRESHOLD = 8.0   # px/s — below this counts as "still"

    def __init__(self, rect: pygame.Rect | tuple,
                 dialogues: list[tuple[str, str]],
                 required_still: float = 2.0,
                 label: str = "") -> None:
        super().__init__(rect, label=label, one_shot=True)
        self.dialogues = dialogues
        self.required_still = required_still
        self._still_timer: float = 0.0

    def update(self, dt: float, hitbox: pygame.Rect,
               velocity: pygame.math.Vector2) -> list[tuple[str, str]] | None:
        if self.activated:
            return None

        if not self.is_inside(hitbox):
            self._still_timer = 0.0
            return None

        moving = velocity.length() > self.IDLE_THRESHOLD
        if moving:
            self._still_timer = 0.0
            return None

        self._still_timer += dt
        if self._still_timer >= self.required_still:
            self.activated = True
            return self.dialogues

        return None

    @property
    def listen_progress(self) -> float:
        """0.0–1.0 fill ratio for optional HUD indicator."""
        return min(1.0, self._still_timer / self.required_still)
