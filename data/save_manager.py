"""
Multi-slot save system.

Each player has an isolated save identified by a nickname.
Files live at  saves/<nickname>.json  (relative to the project root).

Public API
----------
list_saves()                      -> list[str]   sorted nicknames with existing saves
save(flags, player, nickname)     -> None
load(nickname)                    -> EventFlags
apply_to_player(flags, player)    -> None
has_save(nickname)                -> bool
delete_save(nickname)             -> None
"""

import json
import re
from pathlib import Path

from data.event_flags import EventFlags

_SAVES_DIR = Path("saves")


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _sanitize(nickname: str) -> str:
    """Map a nickname to a safe filename (no slashes, dots, etc.)."""
    return re.sub(r"[^\w\- ]", "_", nickname.strip())


def _path(nickname: str) -> Path:
    return _SAVES_DIR / f"{_sanitize(nickname)}.json"


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def list_saves() -> list[str]:
    """Return alphabetically sorted list of existing nicknames."""
    if not _SAVES_DIR.exists():
        return []
    return sorted(f.stem for f in _SAVES_DIR.glob("*.json"))


def save(flags: EventFlags, player, nickname: str) -> None:
    _SAVES_DIR.mkdir(exist_ok=True)
    data = flags.to_dict()
    if player is not None:
        data["max_stamina"]     = player.max_stamina
        data["current_stamina"] = player.current_stamina
        data["max_hunger"]      = player.max_hunger
        data["current_hunger"]  = player.current_hunger
        # apple_debuff is permanent — True once set, never reverted (GDD §7)
        data["apple_debuff"] = flags.apple_debuff or player.apple_debuff
    _path(nickname).write_text(json.dumps(data, indent=2, ensure_ascii=False))


def load(nickname: str) -> EventFlags:
    p = _path(nickname)
    if not p.exists():
        return EventFlags()
    try:
        data = json.loads(p.read_text())
        return EventFlags.from_dict(data)
    except (json.JSONDecodeError, TypeError):
        return EventFlags()


def apply_to_player(flags: EventFlags, player) -> None:
    """Restore persisted stats and debuffs onto a freshly created Player."""
    player.max_stamina     = flags.max_stamina
    player.current_stamina = min(flags.current_stamina, flags.max_stamina)
    player.max_hunger      = flags.max_hunger
    player.current_hunger  = min(flags.current_hunger, flags.max_hunger)
    if flags.apple_debuff:
        # stats already restored from save — don't re-apply multipliers
        player.apple_debuff = True


def has_save(nickname: str) -> bool:
    return _path(nickname).exists()


def delete_save(nickname: str) -> None:
    _path(nickname).unlink(missing_ok=True)
