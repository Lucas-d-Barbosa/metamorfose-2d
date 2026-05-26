"""
RF010 — Food items: fresh (repulse/damage) vs rotten (restore 20-30% stamina).
"""

import math
import random
from enum import Enum, auto

import pygame

from settings import AMBER, TILE_SIZE

_FRESH_THOUGHTS = [
    "Era minha bebida favorita… mas o cheiro… me dá nojo agora.",
    "Não consigo… o leite fresco me dá ânsia. Por quê?",
]
_ROTTEN_THOUGHTS = [
    "Um pedaço de queijo velho e um repolho murcho… Perfeito.",
    "Que cheiro forte… azedo… maravilhoso. Nunca pensei que lixo me daria tanta água na boca.",
]

_FRESH_LABELS = {
    "milk": "Leite fresco",
    "apple": "Maçã",
    "bread": "Pão fresco",
}
_ROTTEN_LABELS = {
    "cheese": "Queijo velho",
    "scraps": "Restos podres",
    "vegetables": "Legumes murchos",
}

_INTERACTION_RANGE = 48.0
_SIZE = 16


class FoodType(Enum):
    FRESH = auto()
    ROTTEN = auto()


class FoodItem(pygame.sprite.Sprite):
    def __init__(self, x: float, y: float,
                 food_type: FoodType, variant: str = "") -> None:
        super().__init__()
        self.food_type = food_type
        self.variant = variant
        self.consumed = False

        self._elapsed = 0.0
        self._base_y = float(y)

        self.pos = pygame.math.Vector2(x, y)
        self.image = self._make_image()
        self.rect = self.image.get_rect(center=(round(x), round(y)))

    # -------------------------------------------------------------------------

    def _make_image(self) -> pygame.Surface:
        surf = pygame.Surface((_SIZE, _SIZE), pygame.SRCALPHA)
        r = _SIZE // 2
        if self.food_type == FoodType.FRESH:
            outer = (210, 230, 255)
            inner = (255, 255, 255)
            glow = (180, 210, 255, 60)
        else:
            outer = (105, 80, 42)
            inner = (75, 55, 28)
            glow = (60, 80, 30, 60)

        # Glow ring
        pygame.draw.circle(surf, glow, (r, r), r)
        # Main body
        pygame.draw.circle(surf, outer, (r, r), r - 2)
        # Highlight
        pygame.draw.circle(surf, inner, (r - 2, r - 3), max(2, r // 3))
        # Spoilage dots for rotten
        if self.food_type == FoodType.ROTTEN:
            for dx, dy in ((-3, 2), (2, -3), (3, 3)):
                pygame.draw.circle(surf, (50, 90, 20),
                                   (r + dx, r + dy), 2)
        return surf

    # -------------------------------------------------------------------------

    def update(self, dt: float) -> None:
        if self.consumed:
            return
        self._elapsed += dt
        bob = math.sin(self._elapsed * 2.8) * 2.0
        self.rect.centery = round(self._base_y + bob)

    def is_near(self, player_pos: pygame.math.Vector2) -> bool:
        return self.pos.distance_to(player_pos) <= _INTERACTION_RANGE and not self.consumed

    def consume(self, player, dialogue) -> str:
        """
        Apply food effect. Returns 'repulse' or 'restore'.
        Kills the sprite.
        """
        if self.consumed:
            return ""
        self.consumed = True
        self.kill()

        if self.food_type == FoodType.FRESH:
            damage = player.max_stamina * 0.25
            player.current_stamina = max(0.0, player.current_stamina - damage)
            dialogue.show_thought(random.choice(_FRESH_THOUGHTS),
                                  duration=4.5, color=(220, 100, 80))
            return "repulse"
        else:
            restore = random.uniform(0.20, 0.30) * player.max_stamina
            player.current_stamina = min(player.max_stamina,
                                         player.current_stamina + restore)
            dialogue.show_thought(random.choice(_ROTTEN_THOUGHTS),
                                  duration=4.5, color=(140, 210, 90))
            return "restore"

    def draw_prompt(self, surface: pygame.Surface,
                    camera_offset: pygame.math.Vector2) -> None:
        sp = self.pos + camera_offset
        font = pygame.font.SysFont("monospace", 10)
        text = "[ E ] Comer"
        color = (210, 230, 255) if self.food_type == FoodType.FRESH else (180, 160, 90)
        rendered = font.render(text, True, color)
        x = int(sp.x) - rendered.get_width() // 2
        y = int(sp.y) - _SIZE - 14
        # Background pill
        bg = pygame.Surface((rendered.get_width() + 8, rendered.get_height() + 4),
                            pygame.SRCALPHA)
        bg.fill((0, 0, 0, 140))
        surface.blit(bg, (x - 4, y - 2))
        surface.blit(rendered, (x, y))
