"""
Fase 4 — A Música e a Morte.

States: cutscene → gameplay → violin_climax → epilogue

RF014 — Faxineira: knockback, sem game over.
RF015 — Violino: guia áudio/visual até a porta da sala.
RF007 — Fog of War: raio 40%.
RF008 — Zonas de Escuta (parede da cozinha / corredor).
RF011 — Lixo com tosse.

Objetivo: Gregor segue o violino até a porta da sala. A detecção
pelos Inquilinos é o desfecho narrativo intencional — não é game over.
"""

import pygame

import data.save_manager as save_mgr
from entities.food import FoodItem, FoodType
from entities.npcs.janitor import Janitor
from entities.npcs.tenants import TenantGroup
from entities.player import Player
from map.hiding_zones import HidingZone
from map.layouts import phase4_room
from map.tilemap import TileMap
from map.trash import DustParticle, TrashZone, build_phase4_trash_zones
from map.triggers import ListeningZone
from scene.base_scene import BaseScene
from settings import (
    COUGH_NOISE_RADIUS,
    DARK_GRAY,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    TILE_SIZE,
    VOICE_NOISE_RADIUS,
)
from systems.camera import Camera
from systems.fog_of_war import FogOfWar
from systems.sound_propagation import SoundPropagationSystem
from systems.violin import ViolinSystem
from ui.dialogue import DialogueSystem
from ui.hud import HUD

# ---------------------------------------------------------------------------
# Sala door position (right wall, row 11-12 center)
# ---------------------------------------------------------------------------
_SALA_DOOR_WORLD = pygame.math.Vector2(41 * TILE_SIZE, 11.5 * TILE_SIZE)

# ---------------------------------------------------------------------------
# Narrative
# ---------------------------------------------------------------------------

_CUTSCENE = [
    ("Faxineira", "Anda, sai do meio do caminho, seu besouro velho."),
    ("Faxineira", "Não tenho medo de você, não."),
    ("Gregor",    "A sujeira tomou conta de tudo. Mal consigo respirar."),
]

_LISTEN_KITCHEN = [
    ("Pai",  "O dinheiro mal dá para as contas. Tivemos que vender as joias da sua mãe."),
    ("Mãe",  "Pelo menos os senhores inquilinos pagam adiantado. Mas eles são tão exigentes com a limpeza…"),
]

_LISTEN_CORRIDOR = [
    ("Inquilino 1", "Senhor Samsa! Essa música é irritante. Mande parar."),
    ("Pai",         "Minha filha está apenas tocando no corredor…"),
]

_THOUGHTS_IDLE = [
    "A visão quase não alcança as paredes.",
    "Ao ouvir a família discutir dinheiro… A culpa é minha. Eu falhei com eles.",
    "Ela não me olha mais nos olhos. Só empurra a comida com a vassoura e corre.",
    "O amor dela também secou.",
]

_VIOLIN_THOUGHT = (
    "Que som lindo… Como eu posso ser um monstro repulsivo "
    "se essa música enche meu peito de tanta luz?"
)

_CLIMAX_DIALOGUES = [
    ("Gregor",      "Como eu posso ser um animal se a música me toca tanto?"),
    ("Gregor",      "Quero chegar perto. Quero dizer à Grete que vou pagar os estudos dela…"),
    ("Inquilino 2", "O QUE É ISSO? Senhor Samsa! O senhor mantém um inseto imundo junto dos hóspedes?!"),
    ("Inquilino 3", "Isso é nojento! Exigimos rescisão imediata do contrato!"),
    ("Inquilino 3", "Não pagaremos nada por este chiqueiro!"),
]

_SENTENCE = [
    ("Grete",  "Pai… Mãe… não podemos continuar assim."),
    ("Grete",  "Eu não vou pronunciar o nome do meu irmão na frente desse monstro."),
    ("Grete",  "Nós tentamos cuidar. Tentamos suportar. Mas precisamos nos livrar dele."),
    ("Grete",  "Se fosse o Gregor de verdade, ele teria ido embora por conta própria."),
    ("Gregor", "Ela tem razão. Minhas dores estão passando… Que a escuridão leve tudo logo…"),
]


def _ts(col: int, row: int) -> tuple[float, float]:
    return col * TILE_SIZE + TILE_SIZE / 2, row * TILE_SIZE + TILE_SIZE / 2


# ---------------------------------------------------------------------------
# Scene
# ---------------------------------------------------------------------------

class Phase4Scene(BaseScene):
    PHASE = 4
    DEBUG = False

    # Trigger zone: player reaching the sala door starts the climax
    _SALA_TRIGGER_RECT = pygame.Rect(
        38 * TILE_SIZE, 9 * TILE_SIZE, 3 * TILE_SIZE, 6 * TILE_SIZE
    )

    def __init__(self, game) -> None:
        super().__init__(game)

        self.flags = save_mgr.load()

        self.tilemap = TileMap(phase4_room(), TILE_SIZE)
        self.camera = Camera(self.tilemap.width, self.tilemap.height)

        # Spawn player far from the sala passage
        cx = 5 * TILE_SIZE
        cy = self.tilemap.height // 2
        self.player = Player(cx, cy)
        save_mgr.apply_to_player(self.flags, self.player)

        # Janitor — patrols the full quarto (RF014)
        mid_x = self.tilemap.width / 2
        mid_y = self.tilemap.height / 2
        self.janitor = Janitor([
            (5 * TILE_SIZE,  5 * TILE_SIZE),
            (mid_x,          5 * TILE_SIZE),
            (mid_x,          mid_y),
            (5 * TILE_SIZE,  mid_y),
            (5 * TILE_SIZE,  18 * TILE_SIZE),
            (mid_x,          18 * TILE_SIZE),
        ])

        # Three Tenants — patrol near the sala passage (right side)
        self.tenant_group = TenantGroup([
            [  # Tenant 0 — wide patrol
                _ts(32, 5), _ts(38, 5), _ts(38, 18), _ts(32, 18),
            ],
            [  # Tenant 1 — guards the passage
                _ts(36, 9), _ts(39, 9), _ts(39, 14), _ts(36, 14),
            ],
            [  # Tenant 2 — mid-right sweep
                _ts(30, 11), _ts(36, 11), _ts(36, 13), _ts(30, 13),
            ],
        ])

        # Food (only rotten restores in Phase 4)
        self.food_group = pygame.sprite.Group()
        self._populate_food()
        self._nearby_food: FoodItem | None = None

        # Hiding zones
        self.hiding_zones = self._build_hiding_zones()
        self._was_hidden = False

        # RF011 trash + dust
        self.trash_zones: list[TrashZone] = build_phase4_trash_zones(TILE_SIZE)
        self.dust_particles: list[DustParticle] = []

        # RF008 listening zones
        self.listening_zones = self._build_listening_zones()
        self._listen_queue: list[tuple[str, str]] = []
        self._listen_delay_timer = 0.0
        self._listen_progress_zone: ListeningZone | None = None

        # Systems
        self.sound = SoundPropagationSystem()
        self.hud = HUD(phase=self.PHASE)
        self.dialogue = DialogueSystem()
        self.fog = FogOfWar(self.PHASE)
        self.violin = ViolinSystem(_SALA_DOOR_WORLD)

        # Flash / voice wave
        self._flash: dict | None = None
        self._voice_wave: dict | None = None

        # Thoughts
        self._thought_idx = 0
        self._thought_timer = 0.0
        self._thought_interval = 14.0
        self._violin_thought_shown = False

        # Climax sequence
        self._climax_idx = 0
        self._climax_timer = 0.0
        self._sentence_idx = 0
        self._sentence_timer = 0.0

        # State
        self._state = "cutscene"
        self._init_cutscene()

    # =========================================================================
    # Setup
    # =========================================================================

    def _populate_food(self) -> None:
        self.food_group.add(FoodItem(*_ts(10, 6),  FoodType.ROTTEN, "scraps"))
        self.food_group.add(FoodItem(*_ts(20, 16), FoodType.ROTTEN, "cheese"))
        self.food_group.add(FoodItem(*_ts( 8, 20), FoodType.ROTTEN, "scraps"))

    def _build_hiding_zones(self) -> list[HidingZone]:
        ts = TILE_SIZE
        return [
            HidingZone(pygame.Rect(1*ts,  1*ts,  3*ts, 6*ts), label="canto-topo"),
            HidingZone(pygame.Rect(1*ts, 15*ts,  3*ts, 6*ts), label="canto-baixo"),
            HidingZone(pygame.Rect(20*ts, 1*ts,  6*ts, 2*ts), label="topo-centro"),
        ]

    def _build_listening_zones(self) -> list[ListeningZone]:
        ts = TILE_SIZE
        return [
            ListeningZone(
                pygame.Rect(1*ts, 10*ts, 4*ts, 4*ts),
                _LISTEN_KITCHEN,
                required_still=2.5, label="cozinha",
            ),
            ListeningZone(
                pygame.Rect(35*ts, 1*ts, 5*ts, 4*ts),
                _LISTEN_CORRIDOR,
                required_still=2.0, label="corredor",
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
        if self._cs_chars >= len(_CUTSCENE[self._cs_line][1]):
            self._cs_chars = float(len(_CUTSCENE[self._cs_line][1]))
            self._cs_waiting = True

    def _draw_cutscene(self, surface: pygame.Surface) -> None:
        surface.fill((5, 4, 8))
        if self._cs_line >= len(_CUTSCENE):
            return
        speaker, full_text = _CUTSCENE[self._cs_line]
        visible = full_text[:int(self._cs_chars)]
        cx, cy = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
        if speaker:
            sf = pygame.font.SysFont("monospace", 13)
            surface.blit(sf.render(speaker.upper(), True, (120, 110, 140)),
                         sf.render(speaker.upper(), True, (120,110,140)).get_rect(
                             centerx=cx, centery=cy - 28))
        tf = pygame.font.SysFont("serif", 22)
        ts_surf = tf.render(visible, True, (200, 195, 210))
        surface.blit(ts_surf, ts_surf.get_rect(centerx=cx, centery=cy))
        if self._cs_waiting:
            pf = pygame.font.SysFont("monospace", 12)
            ps = pf.render("[ ENTER ] Continuar", True, (70, 70, 80))
            surface.blit(ps, ps.get_rect(centerx=cx, centery=cy + 50))
        cf = pygame.font.SysFont("monospace", 10)
        cs = cf.render(f"{self._cs_line+1}/{len(_CUTSCENE)}", True, (50,50,50))
        surface.blit(cs, (SCREEN_WIDTH - 40, SCREEN_HEIGHT - 20))

    # =========================================================================
    # Gameplay
    # =========================================================================

    def _enter_gameplay(self) -> None:
        self._state = "gameplay"
        self.violin.start()

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
            self.dialogue.show_thought("Nas sombras… impossível me verem aqui.",
                                       duration=2.5, color=(100, 220, 140))
        self.player.hidden = now_hidden
        self._was_hidden = now_hidden

        if self.player.noise_radius > 0:
            self.sound.emit(self.player.pos, self.player.noise_radius)
        self.sound.update(dt)

        # Janitor sweep (RF014 — no game over)
        self.janitor.update(dt, self.tilemap, self.player)
        if self.janitor.try_sweep(self.player):
            self.dialogue.show_dialogue(
                "Faxineira", "Sai da frente, seu besouro!", duration=2.0)

        # Tenants patrol
        self.tenant_group.update(dt, self.tilemap, self.player)

        # RF011 trash
        self._update_trash(dt)

        # RF008 listening zones
        self._update_listening_zones(dt)

        # RF015 violin
        self.violin.update(self.player.pos)
        if self.violin.volume > 0.3 and not self._violin_thought_shown:
            self._violin_thought_shown = True
            self.dialogue.show_thought(_VIOLIN_THOUGHT, duration=6.0,
                                       color=(220, 210, 160))

        self._update_thoughts(dt)
        self._update_flash(dt)
        self._update_voice_wave(dt)
        self.dialogue.update(dt)

        # Sala door trigger → climax
        if self._SALA_TRIGGER_RECT.colliderect(self.player.hitbox):
            self._enter_climax()

    # =========================================================================
    # RF011 trash
    # =========================================================================

    def _update_trash(self, dt: float) -> None:
        player_moving = self.player.direction.length_squared() > 0
        for zone in self.trash_zones:
            if zone.update(dt, self.player.hitbox, player_moving):
                self._on_cough()
            if zone.rect.colliderect(self.player.hitbox) and player_moving:
                self._spawn_dust(zone)
        for p in self.dust_particles:
            p.update(dt)
        self.dust_particles = [p for p in self.dust_particles if p.alive]

    def _spawn_dust(self, zone: TrashZone) -> None:
        import random
        if len(self.dust_particles) < 40 and random.random() < 0.25:
            cx = self.player.pos.x + random.uniform(-8, 8)
            cy = self.player.pos.y + random.uniform(-8, 8)
            self.dust_particles.append(DustParticle(cx, cy))

    def _on_cough(self) -> None:
        self.sound.emit(self.player.pos, COUGH_NOISE_RADIUS, lifetime=0.4)
        self.dialogue.show_thought("*tosse* A poeira…", duration=2.0,
                                   color=(180, 160, 100))
        self._flash = {"color": (140, 120, 60), "alpha": 70,
                       "duration": 0.3, "elapsed": 0.0}

    # =========================================================================
    # RF008 listening zones
    # =========================================================================

    def _update_listening_zones(self, dt: float) -> None:
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
    # Violin climax
    # =========================================================================

    def _enter_climax(self) -> None:
        self._state = "violin_climax"
        self._climax_idx = 0
        self._climax_timer = 0.0
        # Stop regular gameplay music if any; violin stays at full volume
        self.violin.update(self.violin.source)  # max volume

    def _climax_update(self, dt: float) -> None:
        self._climax_timer += dt
        intervals = [2.0, 5.0, 8.5, 12.0, 15.5]

        while (self._climax_idx < len(_CLIMAX_DIALOGUES)
               and self._climax_timer >= intervals[self._climax_idx]):
            speaker, text = _CLIMAX_DIALOGUES[self._climax_idx]
            self.dialogue.show_dialogue(speaker, text, duration=4.0)
            self._climax_idx += 1

        self.dialogue.update(dt)
        self._update_flash(dt)

        if self._climax_timer >= 18.0:
            self._enter_sentence()

    # =========================================================================
    # Grete's sentence → epilogue
    # =========================================================================

    def _enter_sentence(self) -> None:
        self._state = "sentence"
        self._sentence_idx = 0
        self._sentence_timer = 0.0
        self.violin.stop()

    def _sentence_update(self, dt: float) -> None:
        self._sentence_timer += dt
        interval = 4.5
        if (self._sentence_timer >= interval
                and self._sentence_idx < len(_SENTENCE)):
            speaker, text = _SENTENCE[self._sentence_idx]
            self.dialogue.show_dialogue(speaker, text, duration=4.0)
            self._sentence_idx += 1
            self._sentence_timer = 0.0

        self.dialogue.update(dt)

        if self._sentence_idx >= len(_SENTENCE) and self._sentence_timer >= 5.0:
            self.transition_to("epilogue")

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
        color = (200, 40, 40) if result == "repulse" else (60, 180, 80)
        alpha = 110 if result == "repulse" else 90
        dur = 0.45 if result == "repulse" else 0.35
        if result in ("repulse", "restore"):
            self._flash = {"color": color, "alpha": alpha,
                           "duration": dur, "elapsed": 0.0}
        self._nearby_food = None

    def _trigger_voice(self) -> None:
        self.dialogue.show_thought('"Estou aqui…"', duration=2.5,
                                   color=(200, 220, 255))
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
        self._flash["alpha"] = max(
            0, int(self._flash["alpha"] * (1 - self._flash["elapsed"] /
                                            self._flash["duration"])))
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
            case "violin_climax" | "sentence":
                pass  # non-interactive
        self.dialogue.handle_event(event)

    def update(self, dt: float) -> None:
        match self._state:
            case "cutscene":
                self._cutscene_update(dt)
            case "gameplay":
                self._gameplay_update(dt)
            case "violin_climax":
                self._climax_update(dt)
            case "sentence":
                self._sentence_update(dt)

    # =========================================================================
    # Draw
    # =========================================================================

    def draw(self, surface: pygame.Surface) -> None:
        if self._state == "cutscene":
            self._draw_cutscene(surface)
            return

        if self._state in ("violin_climax", "sentence"):
            self._draw_climax(surface)
            return

        # --- Normal gameplay draw ---
        surface.fill(DARK_GRAY)
        self.tilemap.draw(surface, self.camera.offset)

        self.tenant_group.draw_fov_all(surface, self.camera.offset)

        for food in self.food_group:
            surface.blit(food.image, self.camera.apply_rect(food.rect))

        surface.blit(self.janitor.image,
                     self.camera.apply_rect(self.janitor.rect))
        self.janitor.draw_alert_bar(surface, self.camera.offset)
        self.tenant_group.draw_sprites_all(surface, self.camera)

        for p in self.dust_particles:
            p.draw(surface, self.camera.offset)

        self._draw_player(surface)
        self._draw_ceiling_overlay(surface)
        self._draw_voice_wave(surface)

        if self._nearby_food:
            self._nearby_food.draw_prompt(surface, self.camera.offset)

        self._draw_flash(surface)

        # RF007 fog (40%)
        player_screen = self.camera.apply_vec(self.player.pos)
        self.fog.draw(surface, player_screen)

        if self.DEBUG:
            self._draw_debug(surface)

        if self.player.apple_debuff:
            self._draw_debuff_indicator(surface)

        self.hud.draw(surface, self.player,
                      list(self.tenant_group) + [self.janitor])

        # RF015 violin guide
        self.violin.draw_hud(surface, cx=SCREEN_WIDTH // 2, cy=36)

        # RF008 listen progress
        if self._listen_progress_zone:
            self._draw_listen_progress(surface)

        self.dialogue.draw(surface)
        self._draw_controls(surface)

    # -------------------------------------------------------------------------
    # Draw helpers
    # -------------------------------------------------------------------------

    def _draw_climax(self, surface: pygame.Surface) -> None:
        surface.fill((5, 4, 8))
        self.dialogue.draw(surface)

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

    def _draw_debuff_indicator(self, surface: pygame.Surface) -> None:
        font = pygame.font.SysFont("monospace", 10)
        surf = font.render("[ DEBILITADO ]", True, (200, 80, 60))
        surface.blit(surf, surf.get_rect(
            centerx=SCREEN_WIDTH // 2, centery=SCREEN_HEIGHT - 42))

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
        for zone in self.trash_zones:
            zone.draw_debug(surface, self.camera.offset)
        for zone in self.listening_zones:
            zone.draw_debug(surface, self.camera.offset)
        # Sala trigger
        sr = self._SALA_TRIGGER_RECT.move(
            int(self.camera.offset.x), int(self.camera.offset.y))
        pygame.draw.rect(surface, (255, 220, 0), sr, 2)
        self.sound.draw_debug(surface, self.camera.offset)
        for t in self.tenant_group:
            t.debug_fov = True
        self.janitor.debug_fov = True

    def _draw_controls(self, surface: pygame.Surface) -> None:
        font = pygame.font.SysFont("monospace", 10)
        hints = ["WASD Mover", "C Teto/Chão", "E Comer", "F Falar",
                 "F3 Debug", "ESC Menu"]
        for i, h in enumerate(hints):
            s = font.render(h, True, (55, 55, 55))
            surface.blit(s, (SCREEN_WIDTH - 122,
                             SCREEN_HEIGHT - 12 * len(hints) + i * 12))
