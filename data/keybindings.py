"""
Remapeamento de teclas — carrega data/keybindings.json se existir,
senão usa os defaults. Todas as cenas devem ler daqui ao invés de
pygame.K_* hardcoded, exceto o setup inicial.

Uso:
    from data.keybindings import KB
    if event.key == KB.INTERACT: ...
    keys = pygame.key.get_pressed()
    if keys[KB.MOVE_UP]: ...
"""

import json
from pathlib import Path

import pygame

_PATH = Path("data/keybindings.json")

_DEFAULTS: dict[str, int] = {
    "MOVE_UP":    pygame.K_w,
    "MOVE_DOWN":  pygame.K_s,
    "MOVE_LEFT":  pygame.K_a,
    "MOVE_RIGHT": pygame.K_d,
    "INTERACT":   pygame.K_e,
    "SPEAK":      pygame.K_f,
    "THOUGHT":    pygame.K_t,
    "Z_LEVEL":    pygame.K_c,
    "DEBUG":      pygame.K_F3,
    "PAUSE":      pygame.K_ESCAPE,
    "CONFIRM":    pygame.K_RETURN,
    "SKIP":       pygame.K_SPACE,
}


class _KeyBindings:
    def __init__(self) -> None:
        self._bindings: dict[str, int] = dict(_DEFAULTS)
        self._load()

    def _load(self) -> None:
        if not _PATH.exists():
            return
        try:
            raw = json.loads(_PATH.read_text())
            for name, key_str in raw.items():
                if name in self._bindings:
                    # Accept either pygame constant name ("K_w") or int
                    if isinstance(key_str, int):
                        self._bindings[name] = key_str
                    elif isinstance(key_str, str):
                        val = getattr(pygame, key_str, None)
                        if val is not None:
                            self._bindings[name] = val
        except (json.JSONDecodeError, TypeError):
            pass

    def save(self) -> None:
        """Write current bindings to JSON (pygame constant names for readability)."""
        out = {}
        for name, key in self._bindings.items():
            key_name = pygame.key.name(key)
            out[name] = key_name
        _PATH.write_text(json.dumps(out, indent=2, ensure_ascii=False))

    def get(self, name: str) -> int:
        return self._bindings.get(name, _DEFAULTS.get(name, pygame.K_UNKNOWN))

    def set(self, name: str, key: int) -> None:
        if name in _DEFAULTS:
            self._bindings[name] = key

    # Convenience attributes (matches _DEFAULTS keys)
    def __getattr__(self, name: str) -> int:
        if name.startswith("_"):
            raise AttributeError(name)
        return self._bindings.get(name, _DEFAULTS.get(name, pygame.K_UNKNOWN))


KB = _KeyBindings()
