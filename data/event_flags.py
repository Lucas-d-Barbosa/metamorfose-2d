"""
Persistent game state flags — serialized to/from save.json.
All fields default to "new game" values.
"""

from dataclasses import asdict, dataclass, field


@dataclass
class EventFlags:
    # Progress
    phase: int = 1
    phase1_complete: bool = False
    phase2_complete: bool = False
    phase3_complete: bool = False

    # Narrative flags
    saved_picture: bool = False       # Missão do Quadro (Fase 2)
    apple_debuff: bool = False        # Maçã Crítica (Fase 3)
    door_unlocked_phase1: bool = False

    # Player persistent stats (modified by debuffs)
    max_stamina: float = 100.0
    current_stamina: float = 100.0
    max_hunger: float = 100.0
    current_hunger: float = 100.0

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "EventFlags":
        valid = {k: v for k, v in data.items()
                 if k in cls.__dataclass_fields__}
        return cls(**valid)
