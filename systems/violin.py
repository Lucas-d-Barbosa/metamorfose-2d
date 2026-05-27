"""
RF015 — Sistema de Áudio Posicional do Violino.

Calcula volume e panning L/R com base na distância/ângulo do jogador
em relação à porta da sala. Se o arquivo de áudio existir, usa
pygame.mixer.Channel.set_volume(left, right). Caso contrário, opera
em modo visual (guia de direção no HUD).

Para ativar o áudio: coloque assets/audio/violin.ogg no projeto.
"""

import math
from pathlib import Path

import pygame

_AUDIO_PATH = Path("assets/audio/violin.ogg")
_MAX_DIST = 900.0    # distância máxima de audibilidade
_CHANNEL_ID = 1      # reserva o canal 1 para o violino


class ViolinSystem:
    """
    Instanciar uma vez na Phase4Scene. Chamar update() a cada frame.
    A porta da sala (world pos) é passada no __init__.
    """

    def __init__(self, sala_door_pos: pygame.math.Vector2) -> None:
        self.source = pygame.math.Vector2(sala_door_pos)

        self.volume: float = 0.0       # 0.0–1.0
        self.pan_left: float = 0.5
        self.pan_right: float = 0.5
        self.direction = pygame.math.Vector2(0.0, 0.0)  # normalized, toward source

        self._channel: pygame.mixer.Channel | None = None
        self._sound: pygame.mixer.Sound | None = None
        self._init_audio()

    # ------------------------------------------------------------------

    def _init_audio(self) -> None:
        if not pygame.mixer.get_init():
            return
        if not _AUDIO_PATH.exists():
            return
        try:
            self._sound = pygame.mixer.Sound(str(_AUDIO_PATH))
            self._channel = pygame.mixer.Channel(_CHANNEL_ID)
            self._channel.play(self._sound, loops=-1)
            self._channel.set_volume(0.0, 0.0)
        except Exception:
            self._channel = None
            self._sound = None

    def start(self) -> None:
        """Call when the violin sequence begins."""
        if self._channel and self._sound and not self._channel.get_busy():
            self._channel.play(self._sound, loops=-1)

    def stop(self) -> None:
        if self._channel:
            self._channel.stop()

    # ------------------------------------------------------------------

    def update(self, player_pos: pygame.math.Vector2) -> None:
        diff = self.source - player_pos
        dist = diff.length()

        self.volume = max(0.0, 1.0 - dist / _MAX_DIST)

        if dist > 0:
            self.direction = diff.normalize()
            # Pan: source to the right of player → more right channel
            norm_x = diff.x / _MAX_DIST
            self.pan_right = max(0.0, min(1.0, 0.5 + norm_x * 0.5))
            self.pan_left = max(0.0, min(1.0, 1.0 - self.pan_right))
        else:
            self.direction = pygame.math.Vector2(0.0, 0.0)
            self.pan_left = self.pan_right = 0.5

        if self._channel:
            l = self.pan_left * self.volume
            r = self.pan_right * self.volume
            self._channel.set_volume(l, r)

    # ------------------------------------------------------------------

    def draw_hud(self, surface: pygame.Surface,
                 cx: int = 640, cy: int = 50) -> None:
        """
        Draws a visual guide: a pulsing note icon + directional arrow.
        Visible once volume > 0.05.
        """
        if self.volume < 0.05:
            return

        import time
        pulse = 0.7 + 0.3 * math.sin(time.time() * 4.0)
        alpha = int(200 * self.volume * pulse)

        guide = pygame.Surface((200, 28), pygame.SRCALPHA)
        # ♪ label
        font = pygame.font.SysFont("serif", 18)
        note = font.render("♪", True, (220, 200, 120, alpha))
        guide.blit(note, (4, 4))

        # Volume bar
        bar_w = int(120 * self.volume)
        pygame.draw.rect(guide, (100, 80, 40, alpha // 2), (24, 10, 120, 8))
        pygame.draw.rect(guide, (220, 200, 120, alpha), (24, 10, bar_w, 8))
        pygame.draw.rect(guide, (180, 160, 80, alpha), (24, 10, 120, 8), 1)

        # Directional arrow
        if self.direction.length_squared() > 0:
            ax, ay = 160, 14
            dx, dy = int(self.direction.x * 12), int(self.direction.y * 12)
            pygame.draw.line(guide, (220, 200, 120, alpha),
                             (ax, ay), (ax + dx, ay + dy), 2)
            # Arrowhead
            perp = pygame.math.Vector2(-self.direction.y, self.direction.x) * 4
            tip = pygame.math.Vector2(ax + dx, ay + dy)
            pygame.draw.polygon(guide, (220, 200, 120, alpha), [
                (int(tip.x), int(tip.y)),
                (int(tip.x - dx * 0.4 + perp.x), int(tip.y - dy * 0.4 + perp.y)),
                (int(tip.x - dx * 0.4 - perp.x), int(tip.y - dy * 0.4 - perp.y)),
            ])

        surface.blit(guide, guide.get_rect(centerx=cx, centery=cy))
