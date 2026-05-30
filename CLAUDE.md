# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Metamorfose 2D** is a top-down 2D stealth game in Python/Pygame adapting Kafka's *A Metamorfose*. The player controls Gregor Samsa (an insect) across 4 phases, each implementing specific GDD mechanics (stealth, fog of war, apple debuff, violin audio, etc.). The canonical design spec is `GDD.MD`; all acceptance criteria live in `GDD.MD §7`.

## Commands

```bash
# Run the game
python main.py

# Run all QA tests (headless, no window required)
python -m pytest tests/test_qa.py -v

# Run a single test class
python -m pytest tests/test_qa.py::TestAppleDebuffPersistence -v

# Run tests directly (alternative)
python tests/test_qa.py
```

**Dependencies:** `pip install pygame==2.6.1` (single dependency).

**Debug mode:** `systems/debug_overlay.py` — toggle in-game to see FPS, NPC FOV cones, noise radii, and fog ratios. Check this first when validating GDD §7 acceptance criteria.

## Architecture

### Scene State Machine (`game.py`)
`Game` owns a `_SCENE_REGISTRY` dict and swaps the `current_scene` each frame when `scene.next_scene` is set. Scenes call `self.transition_to("phase2")` to advance. All scenes inherit `BaseScene` (abstract: `handle_event`, `update`, `draw`).

Scene flow: `menu → phase1 → phase2 → phase3 → phase4 → epilogue` (or `→ game_over`).

### Player (`entities/player.py`)
Top-down movement with `z_level: "floor" | "ceiling"`. Key properties:
- `apple_debuff` — permanent debuff applied by `apply_apple_debuff()`, persists across saves via OR logic in `save_manager`
- `effective_speed` — returns `BASE_SPEED * APPLE_SPEED_PENALTY` if debuffed
- Stamina decay is halved on ceiling (`CEILING_STAMINA_MODIFIER = 0.5`)
- `noise_radius` — set each frame; read by `sound_propagation` to emit `NoiseEvent`

### NPC & Stealth (`systems/stealth.py`, `entities/npc.py`)
`AlertStateMachine` drives PATROL → SUSPICIOUS → ALERT → SEARCH → PATROL. Each NPC owns one instance. NPCs have `fov_angle`, `fov_range`, and `sprite_key` class-level constants. `NPC.update(dt, tilemap, player, sound_system=None)` — pass `self.sound` from the scene so NPCs hear player noise events. `TenantGroup` syncs suspicion across all three Tenants via `_sync_alert()`.

### Save System (`data/save_manager.py`, `data/event_flags.py`)
Single-slot JSON (`save.json` in project root). `EventFlags` is a `@dataclass` with all persistent state. Critical invariant: `apple_debuff` uses OR logic on write — once `True` it never reverts. `apply_to_player()` restores stats without re-applying multipliers (avoid double-apply).

### Systems
| File | Responsibility |
|------|---------------|
| `systems/collision.py` | AABB push-out, shared by all 4 phase scenes |
| `systems/fog_of_war.py` | Radial alpha mask; skipped in phases 1–2, 60% in phase 3, 40% in phase 4 |
| `systems/fov.py` | 2D DDA raycasting for NPC cone-of-vision |
| `systems/sound_propagation.py` | Circular `NoiseEvent` with LOS check against walls |
| `systems/violin.py` | Directional audio panning/volume by player↔source distance |
| `systems/spatial_hash.py` | Acceleration structure for `tilemap.walls_near()` |
| `systems/camera.py` | Smooth-scroll camera + `CameraGroup` |
| `systems/sprite_generator.py` | Generates pixel-art sprites for all characters (GBA Pokémon top-down style); `get_npc_sprite(key)` and `get_gregor_sprite()` |
| `systems/tile_renderer.py` | Generates GBA-style textured tile surfaces (floor/wall/furniture/door/ceiling); cached by `(tile_id, tile_size)` |
| `systems/sprite_loader.py` | Loads `assets/sprites/gregor.png` as fallback; `get_player_sprite()` now delegates to `sprite_generator.get_gregor_sprite()` |
| `systems/debug_overlay.py` | In-game debug visualization |

### Map (`map/`)
`TileMap` built from code via `map/layouts.py` (`phase1_room()`, `phase2_room()`, etc.) until Tiled `.tmx` maps are ready. `map/trash.py` — `TrashZone` accumulates time inside zone and fires cough event after `TRASH_COUGH_DELAY = 1.5s`. `map/triggers.py` — `TriggerZone`/`ListeningZone` for scripted events and listening zones.

### UI (`ui/`)
- `ui/hud.py` — stamina/hunger bars + alert meter; rendered **above** fog-of-war layer
- `ui/dialogue.py` — thought bubbles (fade, colored border) + subtitle system
- `ui/minigame_door.py` — bouncing-cursor timing bar for door unlock (Phase 1)

### Constants (`settings.py`)
All gameplay tuning lives here. Never hardcode values in scenes/entities — always import from `settings`. Fog radii per phase: `FOG_RADIUS_BY_PHASE = {1: 1.0, 2: 1.0, 3: 0.6, 4: 0.4}`.

## Key GDD Constraints to Preserve

- **Apple debuff is permanent**: persists through death, phase restart, and save reload. The OR logic in `save_manager.save()` enforces this.
- **Janitor never triggers game over**: `Janitor.try_sweep()` applies knockback only — must not call `transition_to` or reference `game_over`.
- **Fog of War renders above world, below HUD**: layer order matters.
- **Tenant FOV = Manager FOV × 1.3**: enforced by test `TestTenantFOV`.
- **Cough noise radius = 2× footstep radius**: `COUGH_NOISE_RADIUS = FOOTSTEP_NOISE_RADIUS * 2.0`.

## Agent

`.github/agents/gamesson.agent.md` defines a pygame-expert agent for game feature implementation. Invoke it for new gameplay mechanics.
