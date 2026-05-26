"""
JSON save/load. One slot only — save.json in the project root.
The apple_debuff flag is permanent across deaths and reloads (GDD §7).
"""

import json
from pathlib import Path

from data.event_flags import EventFlags

_SAVE_PATH = Path("save.json")


def save(flags: EventFlags, player=None) -> None:
    data = flags.to_dict()
    if player is not None:
        # Persist live player stats so they survive reload
        data["max_stamina"] = player.max_stamina
        data["current_stamina"] = player.current_stamina
        data["max_hunger"] = player.max_hunger
        data["current_hunger"] = player.current_hunger
        # apple_debuff is permanent — True once set, never reverted
        data["apple_debuff"] = flags.apple_debuff or player.apple_debuff
    _SAVE_PATH.write_text(json.dumps(data, indent=2, ensure_ascii=False))


def load() -> EventFlags:
    if not _SAVE_PATH.exists():
        return EventFlags()
    try:
        data = json.loads(_SAVE_PATH.read_text())
        return EventFlags.from_dict(data)
    except (json.JSONDecodeError, TypeError):
        return EventFlags()


def apply_to_player(flags: EventFlags, player) -> None:
    """Restore persisted stats and debuffs onto a freshly created Player."""
    player.max_stamina = flags.max_stamina
    player.current_stamina = min(flags.current_stamina, flags.max_stamina)
    player.max_hunger = flags.max_hunger
    player.current_hunger = min(flags.current_hunger, flags.max_hunger)
    if flags.apple_debuff and not player.apple_debuff:
        player.apply_apple_debuff()


def has_save() -> bool:
    return _SAVE_PATH.exists()


def delete_save() -> None:
    _SAVE_PATH.unlink(missing_ok=True)
