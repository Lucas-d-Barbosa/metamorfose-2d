"""
Fase 2 — Adaptação e as Memórias (O Quarto Vazio).

States: cutscene → gameplay → picture_mission → phase_end

RF008 — Zonas de Escuta: player fica parado perto da parede → legendas automáticas.
RF012 — Missão do Quadro: Mãe e Grete entram no quarto, timer visível,
         player deve estar no teto adjacente ao quadro antes do tempo acabar.
         Sucesso → saved_picture: true. Falha → Mãe desmaia.
"""

import pygame

import data.save_manager as save_mgr
from data.event_flags import EventFlags
from entities.food import FoodItem, FoodType
from entities.npcs.grete import Grete
from entities.npcs.mother import Mother
from entities.player import Player
from map.hiding_zones import HidingZone
from map.layouts import phase2_room
from map.tilemap import TileMap
from map.triggers import ListeningZone
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
from systems.fov import is_in_fov
from systems.sound_propagation import SoundPropagationSystem
from ui.dialogue import DialogueSystem
from ui.hud import HUD

# ---------------------------------------------------------------------------
# Narrative data
# ---------------------------------------------------------------------------

_CUTSCENE = [
    ("Grete", "Ele deve estar com tanta fome… deixei o leite fresquinho que ele sempre gostou."),
    ("Gregor", "Era minha bebida favorita… mas o cheiro… me dá nojo agora."),
    ("Gregor", "Dias se passaram. Preciso encontrar comida antes que amanheça."),
]

# RF008 — listening zones dialogues
_LISTEN_DOOR = [
    ("Mãe",   "Tem certeza, Grete? Ele pode precisar dos móveis."),
    ("Grete",  "Não, mãe. Ele precisa de espaço para rastejar pelas paredes."),
    ("Grete",  "Vamos tirar o armário pesado primeiro."),
]

_LISTEN_KITCHEN_WALL = [
    ("Pai",  "O dinheiro mal dá para as contas. Tivemos que vender as joias da sua mãe."),
    ("Mãe",  "Pelo menos os senhores inquilinos pagam adiantado. Mas eles são tão exigentes com a limpeza…"),
]

_LISTEN_CORRIDOR = [
    ("Grete", "Mãe, acho que ele ainda reconhece o quarto. Fique calma."),
    ("Mãe",   "Minha nossa, e se ele não quiser que tiremos nada?"),
]

# RF012 — mission dialogues
_MISSION_START = [
    ("Mãe",   "Tem certeza, Grete? Ele pode precisar dos móveis."),
    ("Grete",  "Não, mãe. Ele precisa de espaço para rastejar pelas paredes. Vamos tirar o armário pesado primeiro."),
]

_MISSION_PATROL_THOUGHTS = [
    "Elas estão tirando tudo. O armário, a escrivaninha…",
    "Vão levar meu passado embora. Preciso salvar pelo menos o quadro da mulher de peles!",
    "Se eu me posicionar no teto sobre o quadro, elas não vão levá-lo.",
]

_MISSION_SUCCESS = [
    ("Grete",  "Acho que já tiramos o suficiente por hoje. Vem, mãe. Deixe esse quadro aí."),
]

_MISSION_FAIL_MOTHER = [
    ("Mãe",   "Ah… Gregor!"),
    ("Grete",  "Mãe! O que você fez com ela, seu monstro?!"),
]

_THOUGHTS_IDLE = [
    "O chão é frio e distante daqui do teto. Aqui me sinto quase livre.",
    "Nunca pensei que lixo me daria tanta água na boca.",
    "Ela não me olha mais nos olhos. Só empurra a comida com a vassoura e corre.",
    "Se eu me apressar, posso chegar de volta antes que amanheça.",
]

_PHASE_END_LINES = [
    ("Gregor", "Só o quadro restou. Meu último elo com quem eu fui."),
]

MISSION_DURATION = 30.0   # seconds before Mother/Grete take the picture
PICTURE_TILE = (1, 6)     # col, row — picture frame position in the map


def _ts(col: int, row: int) -> tuple[float, float]:
    return col * TILE_SIZE + TILE_SIZE / 2, row * TILE_SIZE + TILE_SIZE / 2


# ---------------------------------------------------------------------------
# Scene
# ---------------------------------------------------------------------------

class Phase2Scene(BaseScene):
    PHASE = 2
    DEBUG = False

    def __init__(self, game) -> None:
        super().__init__(game)

        self.flags = save_mgr.load()

        self.tilemap = TileMap(phase2_room(), TILE_SIZE)
        self.camera = Camera(self.tilemap.width, self.tilemap.height)

        cx, cy = self.tilemap.width // 2, self.tilemap.height // 2
        self.player = Player(cx, cy)
        save_mgr.apply_to_player(self.flags, self.player)

        self.npcs: list = []
        self.mother: Mother | None = None
        self.grete: Grete | None = None

        # Food (RF010 rules still apply — Phase 2 inverts fresh/rotten preference)
        self.food_group = pygame.sprite.Group()
        self._populate_food()
        self._nearby_food: FoodItem | None = None

        # Hiding zones (no furniture; just corners and scratch marks)
        self.hiding_zones: list[HidingZone] = self._build_hiding_zones()
        self._was_hidden = False

        # Systems
        self.sound = SoundPropagationSystem()
        self.hud = HUD(phase=self.PHASE)
        self.dialogue = DialogueSystem()

        # RF008 — Listening zones
        self.listening_zones = self._build_listening_zones()
        self._listen_queue: list[tuple[str, str]] = []
        self._listen_delay_timer = 0.0
        self._listen_delay = 0.0
        self._listen_progress_zone: "ListeningZone | None" = None

        # Screen flash / voice wave
        self._flash: dict | None = None
        self._voice_wave: dict | None = None

        # Thoughts
        self._thought_idx = 0
        self._thought_timer = 0.0
        self._thought_interval = 16.0

        # --- State machine ---
        self._state: str = "cutscene"
        self._init_cutscene()

    # =========================================================================
    # Setup helpers
    # =========================================================================

    def _populate_food(self) -> None:
        # Phase 2: only rotten food available (gives stamina)
        self.food_group.add(FoodItem(*_ts(20, 10), FoodType.ROTTEN, "scraps"))
        self.food_group.add(FoodItem(*_ts(30, 15), FoodType.ROTTEN, "cheese"))
        # Grete left fresh milk near door (causes stamina loss)
        self.food_group.add(FoodItem(*_ts(19, 21), FoodType.FRESH, "milk"))

    def _build_hiding_zones(self) -> list[HidingZone]:
        ts = TILE_SIZE
        return [
            HidingZone(pygame.Rect(1 * ts, 5 * ts, 2 * ts, 4 * ts), label="parede-quadro"),
            HidingZone(pygame.Rect(38 * ts, 1 * ts, 3 * ts, 4 * ts), label="canto-direito"),
            HidingZone(pygame.Rect(1 * ts, 18 * ts, 2 * ts, 4 * ts), label="canto-esquerdo"),
        ]

    def _build_listening_zones(self) -> list[ListeningZone]:
        ts = TILE_SIZE
        return [
            ListeningZone(
                pygame.Rect(1 * ts, 19 * ts, 4 * ts, 4 * ts),
                _LISTEN_DOOR,
                required_still=2.5,
                label="porta",
            ),
            ListeningZone(
                pygame.Rect(38 * ts, 10 * ts, 3 * ts, 6 * ts),
                _LISTEN_KITCHEN_WALL,
                required_still=2.5,
                label="cozinha",
            ),
            ListeningZone(
                pygame.Rect(20 * ts, 1 * ts, 8 * ts, 3 * ts),
                _LISTEN_CORRIDOR,
                required_still=2.0,
                label="corredor",
            ),
        ]

    # =========================================================================
    # Cutscene
    # =========================================================================

    def _init_cutscene(self) -> None:
        self._cs_line = 0
        self._cs_chars: float = 0.0
        self._cs_speed = 36.0
        self._cs_waiting = False

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
        surface.fill((5, 5, 10))
        if self._cs_line >= len(_CUTSCENE):
            return
        speaker, full_text = _CUTSCENE[self._cs_line]
        visible = full_text[:int(self._cs_chars)]
        cx, cy = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
        if speaker:
            sf = pygame.font.SysFont("monospace", 13)
            sl = sf.render(speaker.upper(), True, (140, 120, 80))
            surface.blit(sl, sl.get_rect(centerx=cx, centery=cy - 28))
        tf = pygame.font.SysFont("serif", 22)
        ts = tf.render(visible, True, (210, 200, 180))
        surface.blit(ts, ts.get_rect(centerx=cx, centery=cy))
        if self._cs_waiting:
            pf = pygame.font.SysFont("monospace", 12)
            ps = pf.render("[ ENTER ] Continuar", True, (80, 80, 80))
            surface.blit(ps, ps.get_rect(centerx=cx, centery=cy + 50))
        cf = pygame.font.SysFont("monospace", 10)
        cs = cf.render(f"{self._cs_line + 1}/{len(_CUTSCENE)}", True, (50, 50, 50))
        surface.blit(cs, (SCREEN_WIDTH - 40, SCREEN_HEIGHT - 20))

    # =========================================================================
    # Gameplay
    # =========================================================================

    def _enter_gameplay(self) -> None:
        self._state = "gameplay"
        self._mission_timer_elapsed = 0.0
        # Mission triggers after short delay so player can explore
        self._mission_trigger_delay = 8.0
        self._mission_triggered = False

    def _gameplay_handle(self, event: pygame.event.Event) -> None:
        if event.type != pygame.KEYDOWN:
            return
        match event.key:
            case pygame.K_ESCAPE:
                save_mgr.save(self.flags, self.player)
                self.transition_to("menu")
            case pygame.K_f:
                self._trigger_voice()
            case pygame.K_e:
                self._try_eat()
            case pygame.K_c:
                if self.player.z_level == "floor":
                    self.player.go_to_ceiling()
                else:
                    self.player.go_to_floor()
            case pygame.K_F3:
                self.DEBUG = not self.DEBUG

    def _gameplay_update(self, dt: float) -> None:
        self.player.update(dt)
        self._resolve_collisions()
        self.camera.update(self.player.pos)

        self.food_group.update(dt)
        self._nearby_food = next(
            (f for f in self.food_group if f.is_near(self.player.pos)), None
        )

        now_hidden = any(z.contains(self.player.hitbox) for z in self.hiding_zones)
        if now_hidden and not self._was_hidden:
            self.dialogue.show_thought("Nas sombras… respiro melhor.", duration=2.5,
                                       color=(100, 220, 140))
        self.player.hidden = now_hidden
        self._was_hidden = now_hidden

        if self.player.noise_radius > 0:
            self.sound.emit(self.player.pos, self.player.noise_radius)
        self.sound.update(dt)

        for npc in self.npcs:
            npc.update(dt, self.tilemap, self.player)

        # RF008 — Listening zones
        self._update_listening_zones(dt)

        self._update_thoughts(dt)
        self._update_flash(dt)
        self._update_voice_wave(dt)
        self.dialogue.update(dt)

        # Mission auto-trigger
        if not self._mission_triggered:
            self._mission_trigger_delay -= dt
            if self._mission_trigger_delay <= 0:
                self._enter_picture_mission()

    # =========================================================================
    # RF008 — Listening zones
    # =========================================================================

    def _update_listening_zones(self, dt: float) -> None:
        # Drain existing queue with a small inter-line delay
        if self._listen_queue:
            self._listen_delay_timer -= dt
            if self._listen_delay_timer <= 0:
                speaker, text = self._listen_queue.pop(0)
                self.dialogue.show_dialogue(speaker, text, duration=4.5)
                self._listen_delay_timer = 5.0
            return

        self._listen_progress_zone = None
        for zone in self.listening_zones:
            fired = zone.update(dt, self.player.hitbox, self.player.velocity)
            if fired:
                self._listen_queue = list(fired)
                self._listen_delay_timer = 0.0
                return
            if zone.is_inside(self.player.hitbox) and not zone.activated:
                self._listen_progress_zone = zone

    # =========================================================================
    # RF012 — Picture Mission
    # =========================================================================

    def _enter_picture_mission(self) -> None:
        self._state = "picture_mission"
        self._mission_triggered = True
        self._mission_elapsed = 0.0
        self._mission_done = False
        self._mission_patrol_thought_idx = 0
        self._mission_patrol_thought_timer = 0.0

        # Spawn Mother and Grete entering from the door
        door_x = 19.5 * TILE_SIZE
        door_y = 22.0 * TILE_SIZE
        mid_x = self.tilemap.width / 2
        mid_y = self.tilemap.height / 2

        self.mother = Mother([
            (door_x, door_y),
            (mid_x - 4 * TILE_SIZE, mid_y),
            (mid_x + 4 * TILE_SIZE, mid_y - 3 * TILE_SIZE),
        ])
        self.grete = Grete([
            (door_x + 2 * TILE_SIZE, door_y),
            (mid_x + 4 * TILE_SIZE, mid_y),
            (mid_x - 3 * TILE_SIZE, mid_y + 3 * TILE_SIZE),
        ])
        self.npcs = [self.mother, self.grete]

        for speaker, text in _MISSION_START:
            self.dialogue.show_dialogue(speaker, text, duration=5.0)

        self.dialogue.show_thought(_MISSION_PATROL_THOUGHTS[0], duration=5.0,
                                   color=(200, 200, 160))
        self._mission_patrol_thought_idx = 1

    def _picture_mission_handle(self, event: pygame.event.Event) -> None:
        if event.type != pygame.KEYDOWN:
            return
        match event.key:
            case pygame.K_ESCAPE:
                save_mgr.save(self.flags, self.player)
                self.transition_to("menu")
            case pygame.K_f:
                self._trigger_voice()
            case pygame.K_e:
                self._try_eat()
            case pygame.K_c:
                if self.player.z_level == "floor":
                    self.player.go_to_ceiling()
                else:
                    self.player.go_to_floor()
            case pygame.K_F3:
                self.DEBUG = not self.DEBUG

    def _picture_mission_update(self, dt: float) -> None:
        if self._mission_done:
            return

        self._mission_elapsed += dt

        # Base gameplay still runs
        self.player.update(dt)
        self._resolve_collisions()
        self.camera.update(self.player.pos)
        self.food_group.update(dt)
        self._nearby_food = next(
            (f for f in self.food_group if f.is_near(self.player.pos)), None
        )
        now_hidden = any(z.contains(self.player.hitbox) for z in self.hiding_zones)
        self.player.hidden = now_hidden
        self._was_hidden = now_hidden

        if self.player.noise_radius > 0:
            self.sound.emit(self.player.pos, self.player.noise_radius)
        self.sound.update(dt)

        for npc in self.npcs:
            npc.update(dt, self.tilemap, self.player)

        self._update_flash(dt)
        self._update_voice_wave(dt)
        self.dialogue.update(dt)

        # Periodic patrol thoughts
        self._mission_patrol_thought_timer += dt
        if (self._mission_patrol_thought_timer >= 8.0
                and self._mission_patrol_thought_idx < len(_MISSION_PATROL_THOUGHTS)):
            self.dialogue.show_thought(
                _MISSION_PATROL_THOUGHTS[self._mission_patrol_thought_idx],
                duration=5.0, color=(200, 200, 160),
            )
            self._mission_patrol_thought_idx += 1
            self._mission_patrol_thought_timer = 0.0

        # Check failure: Mother or Grete sees Gregor
        detected = self._check_npc_detection()
        if detected:
            self._on_mission_fail()
            return

        # Check success: player on ceiling adjacent to picture tile
        if self._is_player_at_picture():
            self._on_mission_success()
            return

        # Timer ran out — mission fails
        if self._mission_elapsed >= MISSION_DURATION:
            self._on_mission_fail()

    def _check_npc_detection(self) -> bool:
        if self.player.hidden:
            return False
        for npc in self.npcs:
            if is_in_fov(npc.pos, npc.facing_angle, npc.fov_angle,
                         npc.fov_range, self.player.pos, self.tilemap):
                return True
        return False

    def _is_player_at_picture(self) -> bool:
        if self.player.z_level != "ceiling":
            return False
        pic_x = PICTURE_TILE[0] * TILE_SIZE
        pic_y = PICTURE_TILE[1] * TILE_SIZE
        pic_rect = pygame.Rect(pic_x - TILE_SIZE, pic_y - TILE_SIZE,
                               TILE_SIZE * 4, TILE_SIZE * 4)
        return pic_rect.colliderect(self.player.hitbox)

    def _on_mission_success(self) -> None:
        self._mission_done = True
        self.flags.saved_picture = True
        save_mgr.save(self.flags, self.player)
        self._flash = {"color": (200, 220, 255), "alpha": 130,
                       "duration": 0.6, "elapsed": 0.0}
        self.dialogue.show_thought(
            "Salvei o quadro. Meu único elo com o que fui.", duration=5.0,
            color=(200, 220, 255),
        )
        for speaker, text in _MISSION_SUCCESS:
            self.dialogue.show_dialogue(speaker, text, duration=5.0)
        self.npcs = []
        self._state = "phase_end"
        self._phase_end_timer = 0.0

    def _on_mission_fail(self) -> None:
        self._mission_done = True
        self._flash = {"color": (200, 40, 40), "alpha": 110,
                       "duration": 0.5, "elapsed": 0.0}
        for speaker, text in _MISSION_FAIL_MOTHER:
            self.dialogue.show_dialogue(speaker, text, duration=4.5)
        self.npcs = []
        self._state = "phase_end"
        self._phase_end_timer = 0.0

    # =========================================================================
    # Phase end
    # =========================================================================

    def _phase_end_update(self, dt: float) -> None:
        self._phase_end_timer += dt
        self.dialogue.update(dt)
        if self._phase_end_timer >= 8.0:
            self.flags.phase2_complete = True
            self.flags.phase = 3
            save_mgr.save(self.flags, self.player)
            self.transition_to("phase3")

    # =========================================================================
    # Shared helpers
    # =========================================================================

    def _resolve_collisions(self) -> None:
        from systems.collision import resolve_wall_collisions
        resolve_wall_collisions(self.player, self.tilemap.walls_near(self.player.hitbox))

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
            '"Aguardem! Eu estou bem!"',
            duration=3.0, color=(200, 220, 255),
        )
        self.sound.emit(self.player.pos, VOICE_NOISE_RADIUS, lifetime=0.5)
        self._voice_wave = {
            "pos": pygame.math.Vector2(self.player.pos),
            "radius": 0.0, "max_radius": VOICE_NOISE_RADIUS, "alpha": 180,
        }

    def _update_thoughts(self, dt: float) -> None:
        self._thought_timer += dt
        if self._thought_timer >= self._thought_interval:
            self._thought_timer = 0.0
            text = _THOUGHTS_IDLE[self._thought_idx % len(_THOUGHTS_IDLE)]
            self.dialogue.show_thought(text, duration=4.5)
            self._thought_idx += 1

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
            case "cutscene":
                self._cutscene_handle(event)
            case "gameplay":
                self._gameplay_handle(event)
            case "picture_mission":
                self._picture_mission_handle(event)
            case "phase_end":
                pass
        self.dialogue.handle_event(event)

    def update(self, dt: float) -> None:
        match self._state:
            case "cutscene":
                self._cutscene_update(dt)
            case "gameplay":
                self._gameplay_update(dt)
            case "picture_mission":
                self._picture_mission_update(dt)
            case "phase_end":
                self._phase_end_update(dt)

    # =========================================================================
    # Draw
    # =========================================================================

    def draw(self, surface: pygame.Surface) -> None:
        if self._state == "cutscene":
            self._draw_cutscene(surface)
            return

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

        if self._nearby_food and self._state in ("gameplay", "picture_mission"):
            self._nearby_food.draw_prompt(surface, self.camera.offset)

        self._draw_flash(surface)

        if self._state == "picture_mission":
            self._draw_mission_timer(surface)
            self._draw_picture_hint(surface)

        if self.DEBUG:
            self._draw_debug(surface)

        self.hud.draw(surface, self.player, self.npcs)

        # RF008 listen progress indicator
        if self._listen_progress_zone:
            self._draw_listen_progress(surface)

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

    def _draw_flash(self, surface: pygame.Surface) -> None:
        if not self._flash:
            return
        fs = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        fs.fill((*self._flash["color"], self._flash["alpha"]))
        surface.blit(fs, (0, 0))

    def _draw_mission_timer(self, surface: pygame.Surface) -> None:
        remaining = max(0.0, MISSION_DURATION - self._mission_elapsed)
        ratio = remaining / MISSION_DURATION

        bar_w = 260
        bar_h = 14
        x = SCREEN_WIDTH // 2 - bar_w // 2
        y = 12

        color = (
            (80, 220, 100) if ratio > 0.5
            else (220, 180, 40) if ratio > 0.25
            else (220, 60, 40)
        )

        pygame.draw.rect(surface, (40, 40, 40), (x, y, bar_w, bar_h))
        pygame.draw.rect(surface, color, (x, y, int(bar_w * ratio), bar_h))
        pygame.draw.rect(surface, (200, 200, 200), (x, y, bar_w, bar_h), 1)

        font = pygame.font.SysFont("monospace", 10)
        label = font.render(
            f"QUADRO  {remaining:.0f}s", True, (200, 200, 200)
        )
        surface.blit(label, label.get_rect(centerx=SCREEN_WIDTH // 2, centery=y + bar_h + 10))

    def _draw_picture_hint(self, surface: pygame.Surface) -> None:
        if self._is_player_at_picture() and self.player.z_level != "ceiling":
            font = pygame.font.SysFont("monospace", 11)
            hint = font.render("[ C ] Subir ao teto — abraçar o quadro", True,
                                (200, 200, 120))
            surface.blit(hint, hint.get_rect(
                centerx=SCREEN_WIDTH // 2, centery=SCREEN_HEIGHT - 55))

    def _draw_listen_progress(self, surface: pygame.Surface) -> None:
        zone = self._listen_progress_zone
        ratio = zone.listen_progress
        w, h = 120, 6
        x = SCREEN_WIDTH // 2 - w // 2
        y = SCREEN_HEIGHT - 45
        pygame.draw.rect(surface, (30, 30, 30), (x, y, w, h))
        pygame.draw.rect(surface, (80, 160, 220), (x, y, int(w * ratio), h))
        pygame.draw.rect(surface, (120, 160, 200), (x, y, w, h), 1)
        font = pygame.font.SysFont("monospace", 10)
        lbl = font.render("escutando…", True, (100, 150, 200))
        surface.blit(lbl, lbl.get_rect(centerx=SCREEN_WIDTH // 2, centery=y - 8))

    def _draw_debug(self, surface: pygame.Surface) -> None:
        for wall in self.tilemap.wall_rects:
            pygame.draw.rect(surface, (255, 0, 0),
                             self.camera.apply_rect(wall), 1)
        pygame.draw.rect(surface, (0, 255, 0),
                         self.camera.apply_rect(self.player.hitbox), 1)
        for zone in self.hiding_zones:
            zone.draw_debug(surface, self.camera.offset)
        for lz in self.listening_zones:
            lz.draw_debug(surface, self.camera.offset)
        self.sound.draw_debug(surface, self.camera.offset)
        for npc in self.npcs:
            npc.debug_fov = True

    def _draw_controls(self, surface: pygame.Surface) -> None:
        font = pygame.font.SysFont("monospace", 10)
        hints = ["WASD Mover", "C Teto/Chão", "E Comer", "F Falar", "F3 Debug", "ESC Menu"]
        for i, h in enumerate(hints):
            s = font.render(h, True, (55, 55, 55))
            surface.blit(s, (SCREEN_WIDTH - 122,
                             SCREEN_HEIGHT - 12 * len(hints) + i * 12))
