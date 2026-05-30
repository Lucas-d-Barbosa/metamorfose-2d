"""
Fase 1 — O Despertar e o Pânico.

States: cutscene → gameplay → door_minigame → phase_end
"""

import pygame

import data.save_manager as save_mgr
from data.event_flags import EventFlags
from entities.food import FoodItem, FoodType
from entities.npcs.father import Father
from entities.npcs.manager import Manager
from entities.player import Player
from map.hiding_zones import build_phase1_hiding_zones
from map.layouts import phase1_room
from map.tilemap import TileMap
from scene.base_scene import BaseScene
from settings import (
    DARK_GRAY,
    FOOTSTEP_NOISE_RADIUS,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    TILE_SIZE,
    VOICE_NOISE_RADIUS,
)
from systems.camera import Camera
from systems.sound_propagation import SoundPropagationSystem
from ui.dialogue import DialogueSystem
from ui.hud import HUD
from ui.minigame_door import DoorMinigame

# ---------------------------------------------------------------------------
# Narrative data
# ---------------------------------------------------------------------------

_CUTSCENE = [
    ("Gregor", "O que aconteceu comigo? Não é um sonho…"),
    ("Gregor", "Eu devia ter pegado o trem das cinco. O despertador não tocou?"),
]

_INTRO_DIALOGUES = [
    (3.0,  "Mãe",    "Gregor? São quase sete horas. Você não ia viajar?"),
    (7.0,  "Pai",    "Gregor! Gregor! O que está acontecendo aí?"),
    (12.0, "Grete",  "Gregor… você está se sentindo mal?"),
    (18.0, "Gerente","Bom dia, Sr. e Sra. Samsa. O chefe me mandou vir pessoalmente."),
    (23.0, "Pai",    "Ele não está bem, senhor Gerente. Por que mais perderia um dia?"),
]

_THOUGHTS = [
    "Que profissão cansativa eu escolhi…",
    "O trem das cinco. Perdi. O chefe vai gritar tanto…",
    "Por que meu corpo não obedece?",
    "Seis e meia! Se eu perder o trem das sete…",
    "Ele veio pessoalmente. Não têm confiança nenhuma em mim.",
]

_DOOR_APPROACH_THOUGHT = "A porta… preciso destrancar. O Gerente está esperando."

_PHASE_END_LINES = [
    ("Gerente", "Aaaah! O que é isso?! Meu Deus!"),
    ("Mãe",     "(som de desmaio)"),
    ("Pai",     "Volte para lá! Volte agora, seu monstro!"),
]


def _ts(col: int, row: int) -> tuple[float, float]:
    return col * TILE_SIZE + TILE_SIZE / 2, row * TILE_SIZE + TILE_SIZE / 2


# ---------------------------------------------------------------------------
# Scene
# ---------------------------------------------------------------------------

class Phase1Scene(BaseScene):
    PHASE = 1
    DEBUG = False

    def __init__(self, game) -> None:
        super().__init__(game)

        self.flags = save_mgr.load(self.game.nickname)

        # Map & camera
        self.tilemap = TileMap(phase1_room(), TILE_SIZE)
        self.camera = Camera(self.tilemap.width, self.tilemap.height)

        # Player
        cx, cy = self.tilemap.width // 2, self.tilemap.height // 2
        self.player = Player(cx, cy)
        save_mgr.apply_to_player(self.flags, self.player)

        # NPCs — door is at row 15, cols 11-12 (24×16 map)
        door_x = 11.5 * TILE_SIZE   # horizontal centre between cols 11-12
        door_y = 13 * TILE_SIZE     # two rows above the door tile
        self.manager = Manager([
            (door_x - 2 * TILE_SIZE, door_y),
            (door_x + 2 * TILE_SIZE, door_y),
            (door_x + 2 * TILE_SIZE, door_y - 2 * TILE_SIZE),
            (door_x - 2 * TILE_SIZE, door_y - 2 * TILE_SIZE),
        ])
        self.father: Father | None = None
        self.npcs: list = [self.manager]

        # Food
        self.food_group = pygame.sprite.Group()
        self._populate_food()
        self._nearby_food: FoodItem | None = None

        # Hiding
        self.hiding_zones = build_phase1_hiding_zones(TILE_SIZE)
        self._was_hidden = False

        # Systems
        self.sound = SoundPropagationSystem()
        self.hud = HUD(phase=self.PHASE)
        self.dialogue = DialogueSystem()

        # Door trigger zone — rows 12-15, cols 9-15 (24×16 map)
        self._door_trigger = pygame.Rect(
            9 * TILE_SIZE, 12 * TILE_SIZE,
            6 * TILE_SIZE, 4 * TILE_SIZE,
        )
        self._door_prompt_shown = False
        self._door_approach_thought_shown = False

        # Physical door blockers — row 15, cols 11-12 (24×16 map).
        # DOOR_OPEN is not solid in TileMap, so we add blockers here and
        # clear them only when the door is actually unlocked.
        _dr = 15  # ROWS - 1
        if self.flags.door_unlocked_phase1:
            # Save already has the door unlocked (e.g. returning to phase 1
            # after a previous playthrough). Skip the blocker entirely.
            self._door_walls: list[pygame.Rect] = []
        else:
            self._door_walls = [
                pygame.Rect(11 * TILE_SIZE, _dr * TILE_SIZE, TILE_SIZE, TILE_SIZE),
                pygame.Rect(12 * TILE_SIZE, _dr * TILE_SIZE, TILE_SIZE, TILE_SIZE),
            ]

        # Minigame
        self.minigame = DoorMinigame()

        # Voice wave visual
        self._voice_wave: dict | None = None

        # Screen flash
        self._flash: dict | None = None

        # Thoughts
        self._thought_idx = 0
        self._thought_timer = 0.0
        self._thought_interval = 14.0

        # --- State machine ---
        self._state: str = "cutscene"
        self._init_cutscene()

    # =========================================================================
    # Setup
    # =========================================================================

    def _populate_food(self) -> None:
        # Positions for 24×16 map
        self.food_group.add(FoodItem(*_ts(8,  5), FoodType.FRESH,  "milk"))
        self.food_group.add(FoodItem(*_ts(20, 2), FoodType.FRESH,  "apple"))
        self.food_group.add(FoodItem(*_ts(4, 10), FoodType.ROTTEN, "cheese"))
        self.food_group.add(FoodItem(*_ts(3, 13), FoodType.ROTTEN, "scraps"))

    # =========================================================================
    # Cutscene state
    # =========================================================================

    def _init_cutscene(self) -> None:
        self._cs_line = 0
        self._cs_chars: float = 0.0
        self._cs_speed = 38.0         # chars/sec
        self._cs_waiting = False      # waiting for ENTER after line done
        self._cs_done = False

    def _cutscene_handle(self, event: pygame.event.Event) -> None:
        if event.type != pygame.KEYDOWN:
            return
        if event.key in (pygame.K_RETURN, pygame.K_SPACE):
            if self._cs_waiting:
                self._cs_line += 1
                self._cs_chars = 0.0
                self._cs_waiting = False
                if self._cs_line >= len(_CUTSCENE):
                    self._enter_gameplay()
            else:
                # Skip current line typing
                self._cs_chars = len(_CUTSCENE[self._cs_line][1]) + 1.0
        elif event.key == pygame.K_ESCAPE:
            self._enter_gameplay()

    def _cutscene_update(self, dt: float) -> None:
        if self._cs_waiting or self._cs_line >= len(_CUTSCENE):
            return
        self._cs_chars += self._cs_speed * dt
        full_len = len(_CUTSCENE[self._cs_line][1])
        if self._cs_chars >= full_len:
            self._cs_chars = float(full_len)
            self._cs_waiting = True

    def _draw_cutscene(self, surface: pygame.Surface) -> None:
        surface.fill((5, 5, 5))
        if self._cs_line >= len(_CUTSCENE):
            return

        speaker, full_text = _CUTSCENE[self._cs_line]
        visible = full_text[:int(self._cs_chars)]

        cx, cy = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2

        # Speaker label
        if speaker:
            sfont = pygame.font.SysFont("monospace", 13)
            sl = sfont.render(speaker.upper(), True, (140, 120, 80))
            surface.blit(sl, sl.get_rect(centerx=cx, centery=cy - 28))

        # Text
        tfont = pygame.font.SysFont("serif", 22)
        tsurf = tfont.render(visible, True, (210, 200, 180))
        surface.blit(tsurf, tsurf.get_rect(centerx=cx, centery=cy))

        # Prompt
        if self._cs_waiting:
            pfont = pygame.font.SysFont("monospace", 12)
            prompt = pfont.render("[ ENTER ] Continuar", True, (80, 80, 80))
            surface.blit(prompt, prompt.get_rect(centerx=cx, centery=cy + 50))

        # Line counter
        counter_font = pygame.font.SysFont("monospace", 10)
        ctr = counter_font.render(
            f"{self._cs_line + 1}/{len(_CUTSCENE)}", True, (50, 50, 50)
        )
        surface.blit(ctr, (SCREEN_WIDTH - 40, SCREEN_HEIGHT - 20))

    # =========================================================================
    # Gameplay state
    # =========================================================================

    def _enter_gameplay(self) -> None:
        self._state = "gameplay"
        self._intro_timer = 0.0
        self._intro_idx = 0

    def _gameplay_handle(self, event: pygame.event.Event) -> None:
        if event.type != pygame.KEYDOWN:
            return
        match event.key:
            case pygame.K_ESCAPE:
                save_mgr.save(self.flags, self.player, self.game.nickname)
                self.transition_to("menu")
            case pygame.K_f:
                self._trigger_voice()
            case pygame.K_t:
                self._show_next_thought()
            case pygame.K_e:
                if self._door_trigger.colliderect(self.player.hitbox) \
                        and not self.flags.door_unlocked_phase1:
                    self._enter_minigame()
                else:
                    self._try_eat()
            case pygame.K_c:
                if self.player.z_level == "floor":
                    self.player.go_to_ceiling()
                else:
                    self.player.go_to_floor()
            case pygame.K_F3:
                self.DEBUG = not self.DEBUG

    def _gameplay_update(self, dt: float) -> None:
        # Intro dialogues queue
        if self._intro_idx < len(_INTRO_DIALOGUES):
            self._intro_timer += dt
            t, speaker, text = _INTRO_DIALOGUES[self._intro_idx]
            if self._intro_timer >= t:
                self.dialogue.show_dialogue(speaker, text, duration=5.0)
                self._intro_idx += 1

        self.player.update(dt)
        self._resolve_collisions()
        self.camera.update(self.player.pos)

        # Food
        self.food_group.update(dt)
        self._nearby_food = next(
            (f for f in self.food_group if f.is_near(self.player.pos)), None
        )

        # Hiding
        now_hidden = any(z.contains(self.player.hitbox) for z in self.hiding_zones)
        if now_hidden and not self._was_hidden:
            self.dialogue.show_thought("Aqui… ninguém vai me ver. Posso respirar.",
                                       duration=3.0, color=(100, 220, 140))
        self.player.hidden = now_hidden
        self._was_hidden = now_hidden

        # Sound
        if self.player.noise_radius > 0:
            self.sound.emit(self.player.pos, self.player.noise_radius)
        self.sound.update(dt)

        # NPCs
        for npc in self.npcs:
            npc.update(dt, self.tilemap, self.player, self.sound)

        # Father knockback
        if self.father:
            knocked = self.father.try_knockback(self.player)
            if knocked:
                self.sound.emit(self.player.pos, FOOTSTEP_NOISE_RADIUS * 1.5)

        # Door approach prompt
        if (self._door_trigger.colliderect(self.player.hitbox)
                and not self.flags.door_unlocked_phase1
                and not self._door_approach_thought_shown):
            self.dialogue.show_thought(_DOOR_APPROACH_THOUGHT,
                                       duration=4.0, color=(200, 200, 160))
            self._door_approach_thought_shown = True

        self._update_voice_wave(dt)
        self._update_flash(dt)
        self._update_thoughts(dt)
        self.dialogue.update(dt)

    # =========================================================================
    # Door minigame state
    # =========================================================================

    def _enter_minigame(self) -> None:
        self._state = "door_minigame"
        self.minigame.start()

    def _minigame_handle(self, event: pygame.event.Event) -> None:
        if event.type != pygame.KEYDOWN:
            return
        if event.key == pygame.K_e:
            result = self.minigame.attempt()
            if result == "unlock":
                self._on_door_unlocked()
            elif result == "exhausted":
                # Failed — go back to gameplay
                self.dialogue.show_thought(
                    "Não tenho forças… por enquanto.", duration=3.0,
                    color=(200, 100, 80),
                )
                self._state = "gameplay"
        elif event.key == pygame.K_ESCAPE:
            self.minigame.cancel()
            self._state = "gameplay"

    def _on_door_unlocked(self) -> None:
        self.flags.door_unlocked_phase1 = True
        save_mgr.save(self.flags, self.player, self.game.nickname)
        self._door_walls = []   # remove physical blocker — door is open
        self.dialogue.show_thought(
            "Consegui… a porta está aberta.", duration=3.0,
            color=(200, 220, 255),
        )
        self._flash = {"color": (255, 255, 200), "alpha": 130,
                       "duration": 0.5, "elapsed": 0.0}
        self._enter_phase_end()

    # =========================================================================
    # Phase end sequence
    # =========================================================================

    def _enter_phase_end(self) -> None:
        self._state = "phase_end"
        self._phase_end_timer = 0.0
        self._phase_end_idx = 0
        self._phase_end_done = False

        # Manager flees — remove from NPCs
        self.npcs = [n for n in self.npcs if n is not self.manager]

        # Spawn Father at the door (24×16 map: row 15, cols 11-12)
        door_cx = 11.5 * TILE_SIZE
        door_cy = 14 * TILE_SIZE
        room_cx = self.tilemap.width / 2
        room_cy = self.tilemap.height / 2
        self.father = Father(
            [(door_cx, door_cy)],
            room_center=(room_cx, room_cy),
        )
        self.npcs.append(self.father)

    def _phase_end_handle(self, event: pygame.event.Event) -> None:
        pass  # non-interactive

    def _phase_end_update(self, dt: float) -> None:
        self._phase_end_timer += dt
        # Trigger end dialogues at intervals
        intervals = [1.5, 3.5, 6.0]
        while (self._phase_end_idx < len(_PHASE_END_LINES)
               and self._phase_end_timer >= intervals[self._phase_end_idx]):
            speaker, text = _PHASE_END_LINES[self._phase_end_idx]
            self.dialogue.show_dialogue(speaker, text, duration=4.0)
            self._phase_end_idx += 1

        if self._phase_end_timer >= 9.0 and not self._phase_end_done:
            self._phase_end_done = True
            self.flags.phase1_complete = True
            self.flags.phase = 2
            save_mgr.save(self.flags, self.player, self.game.nickname)
            self.transition_to("transition_1_2")

    # =========================================================================
    # Shared helpers
    # =========================================================================

    def _resolve_collisions(self) -> None:
        from systems.collision import resolve_wall_collisions
        walls = self.tilemap.walls_near(self.player.hitbox) + self._door_walls
        resolve_wall_collisions(self.player, walls)

    def _try_eat(self) -> None:
        if not self._nearby_food:
            return
        result = self._nearby_food.consume(self.player, self.dialogue)
        if result == "repulse":
            self._flash = {"color": (200, 40, 40), "alpha": 110,
                           "duration": 0.45, "elapsed": 0.0}
        elif result == "restore":
            self._flash = {"color": (60, 180, 80), "alpha": 90,
                           "duration": 0.35, "elapsed": 0.0}
        self._nearby_food = None

    def _trigger_voice(self) -> None:
        self.dialogue.show_thought(
            '"Senhor Gerente, já estou abrindo! Tive um pequeno mal-estar!"',
            duration=3.5, color=(200, 220, 255),
        )
        self.sound.emit(self.player.pos, VOICE_NOISE_RADIUS, lifetime=0.5)
        self._voice_wave = {
            "pos": pygame.math.Vector2(self.player.pos),
            "radius": 0.0, "max_radius": VOICE_NOISE_RADIUS, "alpha": 180,
        }

    def _show_next_thought(self) -> None:
        text = _THOUGHTS[self._thought_idx % len(_THOUGHTS)]
        self.dialogue.show_thought(text, duration=4.5)
        self._thought_idx += 1

    def _update_thoughts(self, dt: float) -> None:
        self._thought_timer += dt
        if self._thought_timer >= self._thought_interval:
            self._thought_timer = 0.0
            self._show_next_thought()

    def _update_voice_wave(self, dt: float) -> None:
        if not self._voice_wave:
            return
        w = self._voice_wave
        w["radius"] += VOICE_NOISE_RADIUS * dt * 2.0
        w["alpha"] = max(0, int(180 * (1 - w["radius"] / w["max_radius"])))
        if w["radius"] >= w["max_radius"]:
            self._voice_wave = None

    def _update_flash(self, dt: float) -> None:
        if not self._flash:
            return
        self._flash["elapsed"] += dt
        ratio = self._flash["elapsed"] / self._flash["duration"]
        self._flash["alpha"] = max(0, int(130 * (1 - ratio)))
        if self._flash["elapsed"] >= self._flash["duration"]:
            self._flash = None

    # =========================================================================
    # Main routing
    # =========================================================================

    def handle_event(self, event: pygame.event.Event) -> None:
        match self._state:
            case "cutscene":     self._cutscene_handle(event)
            case "gameplay":     self._gameplay_handle(event)
            case "door_minigame":self._minigame_handle(event)
            case "phase_end":    self._phase_end_handle(event)
        self.dialogue.handle_event(event)

    def update(self, dt: float) -> None:
        match self._state:
            case "cutscene":
                self._cutscene_update(dt)
            case "gameplay":
                self._gameplay_update(dt)
            case "door_minigame":
                self._gameplay_update(dt)
                self.minigame.update(dt)
            case "phase_end":
                self._gameplay_update(dt)
                self._phase_end_update(dt)
        self.dialogue.update(dt)

    # =========================================================================
    # Draw
    # =========================================================================

    def draw(self, surface: pygame.Surface) -> None:
        if self._state == "cutscene":
            self._draw_cutscene(surface)
            return

        # World
        surface.fill(DARK_GRAY)
        self.tilemap.draw(surface, self.camera.offset)

        for npc in self.npcs:
            npc.draw_fov(surface, self.camera.offset)

        for food in self.food_group:
            surface.blit(food.image, self.camera.apply_rect(food.rect))

        for npc in self.npcs:
            surface.blit(npc.image, self.camera.apply_rect(npc.rect))
            npc.draw_alert_bar(surface, self.camera.offset)

        self._draw_player(surface)
        self._draw_ceiling_overlay(surface)
        self._draw_voice_wave(surface)

        if self._nearby_food and self._state == "gameplay":
            self._nearby_food.draw_prompt(surface, self.camera.offset)

        # Door indicator — always visible when door is locked
        if not self.flags.door_unlocked_phase1 and self._state in ("gameplay", "door_minigame"):
            self._draw_door_indicator(surface)

        if not self.flags.door_unlocked_phase1 \
                and self._door_trigger.colliderect(self.player.hitbox) \
                and self._state == "gameplay":
            self._draw_door_prompt(surface)

        self._draw_flash(surface)

        if self.DEBUG:
            self._draw_debug(surface)

        if self._state == "door_minigame":
            self.minigame.draw(surface)

        # HUD always on top
        self.hud.draw(surface, self.player, self.npcs)
        self.dialogue.draw(surface)
        self._draw_controls(surface)

    # -------------------------------------------------------------------------
    # Draw helpers
    # -------------------------------------------------------------------------

    def _draw_player(self, surface: pygame.Surface) -> None:
        img = self.player.image.copy()
        img.set_alpha(55 if self.player.hidden else 255)
        surface.blit(img, self.camera.apply_rect(self.player.rect))

    def _draw_ceiling_overlay(self, surface: pygame.Surface) -> None:
        if self.player.z_level != "ceiling":
            return
        ov = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        ov.fill((15, 25, 50, 70))
        surface.blit(ov, (0, 0))
        sp = self.camera.apply_vec(self.player.pos)
        sh = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        pygame.draw.ellipse(sh, (0, 0, 0, 90),
                            (int(sp.x) - 16, int(sp.y) + 8, 32, 12))
        surface.blit(sh, (0, 0))

    def _draw_voice_wave(self, surface: pygame.Surface) -> None:
        if not self._voice_wave:
            return
        w = self._voice_wave
        ws = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        sp = self.camera.apply_vec(w["pos"])
        pygame.draw.circle(ws, (180, 180, 255, w["alpha"]),
                           (int(sp.x), int(sp.y)), int(w["radius"]), 2)
        surface.blit(ws, (0, 0))

    def _draw_door_prompt(self, surface: pygame.Surface) -> None:
        font = pygame.font.SysFont("monospace", 13)
        surf = font.render("[ E ] Destrancar a porta", True, (255, 230, 80))
        surface.blit(surf, surf.get_rect(
            centerx=SCREEN_WIDTH // 2, centery=SCREEN_HEIGHT - 55))

    def _draw_door_indicator(self, surface: pygame.Surface) -> None:
        """Pulsing arrow + label drawn in world-space above the door tile."""
        import math
        pulse = (math.sin(pygame.time.get_ticks() / 380.0) + 1.0) / 2.0  # 0–1

        # World centre of the door (row 15, cols 11-12 → x=368, y=14.5*32)
        door_wx = 11.5 * TILE_SIZE
        door_wy = 14.0 * TILE_SIZE  # one row above the door tile

        sp = self.camera.apply_vec(pygame.math.Vector2(door_wx, door_wy))
        sx, sy = int(sp.x), int(sp.y)

        bright = int(180 + 75 * pulse)
        color  = (bright, int(bright * 0.87), 30)

        # Downward-pointing triangle
        sz = int(10 + 5 * pulse)
        pts = [(sx, sy + sz), (sx - sz, sy - sz // 2), (sx + sz, sy - sz // 2)]
        pygame.draw.polygon(surface, color, pts)
        pygame.draw.polygon(surface, (0, 0, 0), pts, 1)  # thin outline

        # "PORTA" label
        font = pygame.font.SysFont("monospace", 11)
        lbl = font.render("PORTA", True, color)
        surface.blit(lbl, lbl.get_rect(centerx=sx, bottom=sy - sz - 2))

    def _draw_flash(self, surface: pygame.Surface) -> None:
        if not self._flash:
            return
        fs = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        fs.fill((*self._flash["color"], self._flash["alpha"]))
        surface.blit(fs, (0, 0))

    def _draw_debug(self, surface: pygame.Surface) -> None:
        for wall in self.tilemap.wall_rects:
            pygame.draw.rect(surface, (255, 0, 0),
                             self.camera.apply_rect(wall), 1)
        pygame.draw.rect(surface, (0, 255, 0),
                         self.camera.apply_rect(self.player.hitbox), 1)
        screen_door = self._door_trigger.move(
            int(self.camera.offset.x), int(self.camera.offset.y))
        pygame.draw.rect(surface, (255, 220, 0), screen_door, 2)
        for zone in self.hiding_zones:
            zone.draw_debug(surface, self.camera.offset)
        self.sound.draw_debug(surface, self.camera.offset)
        for npc in self.npcs:
            npc.debug_fov = True

    def _draw_controls(self, surface: pygame.Surface) -> None:
        font = pygame.font.SysFont("monospace", 10)
        hints = [
            "WASD Mover", "C Teto/Chão", "E Interagir/Porta",
            "F Falar", "F3 Debug", "ESC Menu",
        ]
        for i, h in enumerate(hints):
            s = font.render(h, True, (55, 55, 55))
            surface.blit(s, (SCREEN_WIDTH - 122,
                             SCREEN_HEIGHT - 12 * len(hints) + i * 12))
