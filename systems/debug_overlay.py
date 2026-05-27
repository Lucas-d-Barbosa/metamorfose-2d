"""
Modo debug (F3) — overlay centralizado usado por todas as cenas.

Mostra: FPS, player stats, NPCs com FOV info, sound radius, fog radius.
Verifica os critérios de aceitação do GDD §7 em tempo real.
"""

import math

import pygame

from settings import (
    CEILING_STAMINA_MODIFIER,
    COUGH_NOISE_RADIUS,
    FOOTSTEP_NOISE_RADIUS,
    FOG_RADIUS_BY_PHASE,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    TILE_SIZE,
)


def _font(size: int = 11) -> pygame.font.Font:
    return pygame.font.SysFont("monospace", size)


class DebugOverlay:
    """
    Instantiate once per scene. Call draw() after the world and before HUD.
    """

    BG_COLOR  = (0, 0, 0, 160)
    OK_COLOR  = (80, 220, 100)
    ERR_COLOR = (220, 80, 60)
    DIM_COLOR = (140, 140, 140)
    HI_COLOR  = (220, 220, 100)

    def __init__(self, phase: int) -> None:
        self.phase = phase
        self._clock_ref: pygame.time.Clock | None = None

    def set_clock(self, clock: pygame.time.Clock) -> None:
        self._clock_ref = clock

    # ------------------------------------------------------------------

    def draw(self, surface: pygame.Surface, player, npcs: list,
             tilemap=None, sound_system=None) -> None:
        lines: list[tuple[str, tuple]] = []

        # --- FPS ---
        fps = self._clock_ref.get_fps() if self._clock_ref else 0.0
        fps_color = self.OK_COLOR if fps >= 55 else (self.ERR_COLOR if fps < 40 else self.HI_COLOR)
        lines.append((f"FPS {fps:.0f}", fps_color))
        lines.append(("", self.DIM_COLOR))

        # --- Player ---
        lines.append(("─ PLAYER ─", self.DIM_COLOR))
        lines.append((f"pos  ({player.pos.x:.0f}, {player.pos.y:.0f})", self.DIM_COLOR))
        lines.append((f"z    {player.z_level.upper()}", self.HI_COLOR))
        lines.append((f"STA  {player.current_stamina:.0f}/{player.max_stamina:.0f}", self.DIM_COLOR))
        lines.append((f"FAM  {player.current_hunger:.0f}/{player.max_hunger:.0f}", self.DIM_COLOR))
        lines.append((f"SPD  {player.effective_speed:.0f}", self.DIM_COLOR))
        lines.append((f"hidden {player.hidden}", self.OK_COLOR if player.hidden else self.DIM_COLOR))

        if player.apple_debuff:
            lines.append(("apple_debuff ON", self.ERR_COLOR))

        # GDD §7 — ceiling stamina = 50%
        if player.z_level == "ceiling":
            expected = CEILING_STAMINA_MODIFIER
            ok = abs(expected - 0.5) < 0.001
            col = self.OK_COLOR if ok else self.ERR_COLOR
            lines.append((f"  ✓ teto stamina×{CEILING_STAMINA_MODIFIER}", col))

        lines.append(("", self.DIM_COLOR))

        # --- NPCs ---
        if npcs:
            lines.append(("─ NPCS ─", self.DIM_COLOR))
            manager_fov = None
            for npc in npcs:
                name = type(npc).__name__
                state = npc.alert.state.name
                sus = f"{npc.alert.suspicion:.0f}"
                fov_a = getattr(npc, "fov_angle", 0)
                fov_r = getattr(npc, "fov_range", 0)
                lines.append((f"{name:12s} {state:10s} sus={sus}", self.DIM_COLOR))
                lines.append((f"  FOV {fov_a:.0f}° / {fov_r:.0f}px", self.DIM_COLOR))

                if name == "Manager":
                    manager_fov = (fov_a, fov_r)
                if name == "Tenant" and manager_fov:
                    # GDD §7 — Tenant FOV 30% maior que Manager
                    expected_a = round(manager_fov[0] * 1.3, 1)
                    expected_r = round(manager_fov[1] * 1.3, 1)
                    ok = abs(fov_a - expected_a) < 2.0 and abs(fov_r - expected_r) < 3.0
                    col = self.OK_COLOR if ok else self.ERR_COLOR
                    lines.append((f"  ✓ FOV×1.3 expect {expected_a}°/{expected_r}px", col))

        lines.append(("", self.DIM_COLOR))

        # --- Sound ---
        lines.append(("─ SOUND RADII ─", self.DIM_COLOR))
        lines.append((f"footstep  {FOOTSTEP_NOISE_RADIUS:.0f}px", self.DIM_COLOR))
        cough_ok = abs(COUGH_NOISE_RADIUS - FOOTSTEP_NOISE_RADIUS * 2.0) < 0.1
        col = self.OK_COLOR if cough_ok else self.ERR_COLOR
        lines.append((f"cough     {COUGH_NOISE_RADIUS:.0f}px  ✓×2 = {col is self.OK_COLOR}", col))
        lines.append((f"noise_now {player.noise_radius:.0f}px", self.DIM_COLOR))

        # --- Fog ---
        lines.append(("", self.DIM_COLOR))
        lines.append(("─ FOG OF WAR ─", self.DIM_COLOR))
        for ph, ratio in FOG_RADIUS_BY_PHASE.items():
            active = "◄" if ph == self.phase else " "
            lines.append((f"phase {ph}: {int(ratio*100)}%  {active}", self.DIM_COLOR))

        # --- Tile info ---
        if tilemap:
            mx, my = pygame.mouse.get_pos()
            lines.append(("", self.DIM_COLOR))
            lines.append(("─ TILE AT MOUSE ─", self.DIM_COLOR))
            # approximate: no camera offset available here
            lines.append((f"screen ({mx},{my})", self.DIM_COLOR))

        self._render(surface, lines)

    # ------------------------------------------------------------------

    def _render(self, surface: pygame.Surface,
                lines: list[tuple[str, tuple]]) -> None:
        f = _font(10)
        line_h = 13
        pad = 6
        max_w = max((f.size(text)[0] for text, _ in lines if text), default=0) + pad * 2
        panel_h = len(lines) * line_h + pad * 2

        panel = pygame.Surface((max_w, panel_h), pygame.SRCALPHA)
        panel.fill(self.BG_COLOR)
        surface.blit(panel, (SCREEN_WIDTH - max_w - 4, 4))

        for i, (text, color) in enumerate(lines):
            if not text:
                continue
            rendered = f.render(text, True, color)
            surface.blit(rendered,
                         (SCREEN_WIDTH - max_w - 4 + pad,
                          4 + pad + i * line_h))
