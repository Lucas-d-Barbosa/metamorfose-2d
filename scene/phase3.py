"""
Fase 3 — A Agressão e a Deterioração.

States: cutscene → gameplay → apple_hit → phase_end

RF013 — Maçã Crítica: Pai arremessa AppleProjectile periodicamente.
         Se acertar: aplica debuff permanente, salva no JSON, exibe pensamento.
RF014 — Faxineira: knockback sem game over (não ativa nessa fase; ela é da Fase 4).
"""

import pygame

import data.save_manager as save_mgr
from entities.food import FoodItem, FoodType
from entities.npcs.father import Father
from entities.player import Player
from entities.projectile import AppleProjectile
from map.hiding_zones import HidingZone
from map.layouts import phase3_room
from map.tilemap import TileMap
from map.trash import DustParticle, TrashZone, build_phase3_trash_zones
from scene.base_scene import BaseScene
from settings import (
    COUGH_NOISE_RADIUS,
    DARK_GRAY,
    FOOTSTEP_NOISE_RADIUS,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    TILE_SIZE,
    VOICE_NOISE_RADIUS,
)
from systems.camera import Camera
from systems.fog_of_war import FogOfWar
from systems.sound_propagation import SoundPropagationSystem
from ui.dialogue import DialogueSystem
from ui.hud import HUD

# ---------------------------------------------------------------------------
# Narrative data
# ---------------------------------------------------------------------------

_CUTSCENE = [
    ("Pai",   "O que foi essa confusão? Ela desmaiou de novo?!"),
    ("Grete", "Foi ele, pai! Ele escapou do quarto!"),
    ("Pai",   "Eu já disse para vocês! Eu sabia que isso ia acontecer!"),
]

_PATROL_DIALOGUES = [
    (4.0,  "Pai",    "Fique no seu canto! Não chegue perto da sua mãe!"),
    (10.0, "Gregor", "Não consigo ver direito. Ele está jogando… maçãs da fruteira?"),
    (18.0, "Pai",    "Saia daí! Para dentro!"),
]

_THOUGHTS_IDLE = [
    "A visão está turva. O quarto parece menor.",
    "Cada movimento me custa mais. Esse lixo todo…",
    "Eu lembro quando havia uma cama aqui. Minha cama.",
    "Aguento mais um pouco. Preciso aguentar.",
]

_APPLE_HIT_THOUGHT = (
    "Atingiu minhas costas. Uma dor terrível. "
    "Acho que quebrou minha carapaça… Não consigo me mover direito."
)

_PHASE_END_LINES = [
    ("Gregor", "A dor vai passando. Mas algo ficou diferente. Permanente."),
]


def _ts(col: int, row: int) -> tuple[float, float]:
    return col * TILE_SIZE + TILE_SIZE / 2, row * TILE_SIZE + TILE_SIZE / 2


# ---------------------------------------------------------------------------
# Scene
# ---------------------------------------------------------------------------

class Phase3Scene(BaseScene):
    PHASE = 3
    DEBUG = False

    def __init__(self, game) -> None:
        super().__init__(game)

        self.flags = save_mgr.load()

        self.tilemap = TileMap(phase3_room(), TILE_SIZE)
        self.camera = Camera(self.tilemap.width, self.tilemap.height)

        # Spawn player away from Father's starting position
        cx = self.tilemap.width // 2
        cy = self.tilemap.height // 2 - 3 * TILE_SIZE
        self.player = Player(cx, cy)
        save_mgr.apply_to_player(self.flags, self.player)

        # Father — patrols the room, throws apples (RF013)
        door_x = 19.5 * TILE_SIZE
        door_y = 22.0 * TILE_SIZE
        mid_x = self.tilemap.width / 2
        mid_y = self.tilemap.height / 2
        self.father = Father(
            [
                (door_x, door_y),
                (mid_x - 6 * TILE_SIZE, mid_y + 2 * TILE_SIZE),
                (mid_x + 6 * TILE_SIZE, mid_y + 2 * TILE_SIZE),
                (mid_x, mid_y - 4 * TILE_SIZE),
            ],
            room_center=(mid_x, mid_y),
            throws_apples=True,
        )
        self.npcs = [self.father]

        # Projectiles
        self.projectiles: list[AppleProjectile] = []
        self._apple_debuff_applied = self.flags.apple_debuff

        # Food (RF010 — only rotten food restores in Phase 3)
        self.food_group = pygame.sprite.Group()
        self._populate_food()
        self._nearby_food: FoodItem | None = None

        # Hiding zones (corners between junk)
        self.hiding_zones = self._build_hiding_zones()
        self._was_hidden = False

        # RF011 — Trash zones + dust particles
        self.trash_zones: list[TrashZone] = build_phase3_trash_zones(TILE_SIZE)
        self.dust_particles: list[DustParticle] = []

        # Systems
        self.sound = SoundPropagationSystem()
        self.hud = HUD(phase=self.PHASE)
        self.dialogue = DialogueSystem()
        self.fog = FogOfWar(self.PHASE)

        # Screen flash
        self._flash: dict | None = None
        self._voice_wave: dict | None = None

        # Thoughts
        self._thought_idx = 0
        self._thought_timer = 0.0
        self._thought_interval = 15.0

        # Intro dialogues queue
        self._intro_timer = 0.0
        self._intro_idx = 0

        # State
        self._state = "cutscene"
        self._init_cutscene()

    # =========================================================================
    # Setup
    # =========================================================================

    def _populate_food(self) -> None:
        self.food_group.add(FoodItem(*_ts(11, 11), FoodType.ROTTEN, "scraps"))
        self.food_group.add(FoodItem(*_ts(24, 17), FoodType.ROTTEN, "cheese"))
        self.food_group.add(FoodItem(*_ts(36, 12), FoodType.ROTTEN, "scraps"))
        self.food_group.add(FoodItem(*_ts(10,  6), FoodType.FRESH,  "apple"))

    def _build_hiding_zones(self) -> list[HidingZone]:
        ts = TILE_SIZE
        return [
            HidingZone(pygame.Rect(1 * ts, 10 * ts, 2 * ts, 4 * ts), label="canto-esq"),
            HidingZone(pygame.Rect(39 * ts, 10 * ts, 2 * ts, 4 * ts), label="canto-dir"),
            HidingZone(pygame.Rect(18 * ts, 1 * ts, 6 * ts, 2 * ts), label="topo"),
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
        surface.fill((8, 5, 5))
        if self._cs_line >= len(_CUTSCENE):
            return
        speaker, full_text = _CUTSCENE[self._cs_line]
        visible = full_text[:int(self._cs_chars)]
        cx, cy = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
        if speaker:
            sf = pygame.font.SysFont("monospace", 13)
            sl = sf.render(speaker.upper(), True, (160, 100, 80))
            surface.blit(sl, sl.get_rect(centerx=cx, centery=cy - 28))
        tf = pygame.font.SysFont("serif", 22)
        ts = tf.render(visible, True, (220, 195, 175))
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
        self._intro_timer = 0.0
        self._intro_idx = 0
        self._phase_end_triggered = False
        self._phase_end_timer = 0.0

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
        # Intro dialogues
        if self._intro_idx < len(_PATROL_DIALOGUES):
            self._intro_timer += dt
            t, speaker, text = _PATROL_DIALOGUES[self._intro_idx]
            if self._intro_timer >= t:
                self.dialogue.show_dialogue(speaker, text, duration=5.0)
                self._intro_idx += 1

        self.player.update(dt)
        self._resolve_collisions()
        self.camera.update(self.player.pos)

        self.food_group.update(dt)
        self._nearby_food = next(
            (f for f in self.food_group if f.is_near(self.player.pos)), None
        )

        now_hidden = any(z.contains(self.player.hitbox) for z in self.hiding_zones)
        if now_hidden and not self._was_hidden:
            self.dialogue.show_thought("Aqui dentro do lixo ele não me vê.",
                                       duration=2.5, color=(100, 220, 140))
        self.player.hidden = now_hidden
        self._was_hidden = now_hidden

        if self.player.noise_radius > 0:
            self.sound.emit(self.player.pos, self.player.noise_radius)
        self.sound.update(dt)

        # Father update + apple throw
        for npc in self.npcs:
            npc.update(dt, self.tilemap, self.player)
        apple = self.father.try_throw(dt, self.player.pos)
        if apple:
            self.projectiles.append(apple)
            self.dialogue.show_dialogue(
                "Pai", "Fique no seu canto!", duration=2.5)

        # Knockback on contact
        if self.father.try_knockback(self.player):
            self.sound.emit(self.player.pos, FOOTSTEP_NOISE_RADIUS * 1.5)

        # Projectile updates + hit detection
        self._update_projectiles(dt)

        # RF011 — Trash zones + dust particles
        self._update_trash(dt)

        self._update_thoughts(dt)
        self._update_flash(dt)
        self._update_voice_wave(dt)
        self.dialogue.update(dt)

        # Phase ends after apple_debuff applied OR after a timed escape
        if not self._phase_end_triggered:
            self._phase_end_timer += dt
            if self._apple_debuff_applied and self.player.apple_debuff:
                # Debuff was applied this session — give narrative beat
                if self._phase_end_timer >= 35.0:
                    self._trigger_phase_end()
            elif self._phase_end_timer >= 45.0:
                # Player survived without being hit — still advance
                self._trigger_phase_end()

    # =========================================================================
    # RF013 — Projectile logic
    # =========================================================================

    def _update_projectiles(self, dt: float) -> None:
        for proj in self.projectiles:
            proj.update(dt, self.tilemap)
            if proj.alive and proj.check_hit(self.player.pos):
                self._on_apple_hit()

        self.projectiles = [p for p in self.projectiles if p.alive]

    def _on_apple_hit(self) -> None:
        if self.player.apple_debuff:
            # Already debuffed — just knockback
            diff = self.player.pos - self.father.pos
            if diff.length_squared() > 0:
                self.player.receive_knockback(diff.normalize(), 350.0)
            return

        self.player.apply_apple_debuff()
        self.flags.apple_debuff = True
        save_mgr.save(self.flags, self.player)
        self._apple_debuff_applied = True

        self._flash = {"color": (220, 60, 30), "alpha": 160,
                       "duration": 0.7, "elapsed": 0.0}
        self.dialogue.show_thought(_APPLE_HIT_THOUGHT, duration=6.0,
                                   color=(220, 80, 60))

    # =========================================================================
    # Phase end
    # =========================================================================

    def _trigger_phase_end(self) -> None:
        self._phase_end_triggered = True
        self._state = "phase_end"
        self._phase_end_countdown = 0.0
        self.npcs = []
        self.projectiles = []
        for speaker, text in _PHASE_END_LINES:
            self.dialogue.show_dialogue(speaker, text, duration=5.0)

    def _phase_end_update(self, dt: float) -> None:
        self._phase_end_countdown += dt
        self.dialogue.update(dt)
        if self._phase_end_countdown >= 8.0:
            self.flags.phase3_complete = True
            self.flags.phase = 4
            save_mgr.save(self.flags, self.player)
            self.transition_to("phase4")

    # =========================================================================
    # RF011 — Trash + dust
    # =========================================================================

    def _update_trash(self, dt: float) -> None:
        player_moving = self.player.direction.length_squared() > 0
        for zone in self.trash_zones:
            coughed = zone.update(dt, self.player.hitbox, player_moving)
            if coughed:
                self._on_cough()
            # Spawn dust while player moves inside zone
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
        self.dialogue.show_thought(
            "*tosse* O pó… não consigo parar.", duration=2.5,
            color=(180, 160, 100),
        )
        self._flash = {"color": (140, 120, 60), "alpha": 70,
                       "duration": 0.3, "elapsed": 0.0}

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
            '"Eu estou aqui! Não me machuque!"',
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
        self._flash["alpha"] = max(0, int(160 * (1 - ratio)))
        if self._flash["elapsed"] >= self._flash["duration"]:
            self._flash = None

    # =========================================================================
    # Main routing
    # =========================================================================

    def handle_event(self, event: pygame.event.Event) -> None:
        match self._state:
            case "cutscene":
                self._cutscene_handle(event)
            case "gameplay" | "phase_end":
                self._gameplay_handle(event)
        self.dialogue.handle_event(event)

    def update(self, dt: float) -> None:
        match self._state:
            case "cutscene":
                self._cutscene_update(dt)
            case "gameplay":
                self._gameplay_update(dt)
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

        for proj in self.projectiles:
            proj.draw(surface, self.camera.offset)

        # Dust particles (below player)
        for p in self.dust_particles:
            p.draw(surface, self.camera.offset)

        self._draw_player(surface)
        self._draw_ceiling_overlay(surface)
        self._draw_voice_wave(surface)

        if self._nearby_food and self._state == "gameplay":
            self._nearby_food.draw_prompt(surface, self.camera.offset)

        self._draw_flash(surface)

        # RF007 — Fog of War (above world, below HUD)
        player_screen = self.camera.apply_vec(self.player.pos)
        self.fog.draw(surface, player_screen)

        if self.DEBUG:
            self._draw_debug(surface)

        # Apple debuff indicator
        if self.player.apple_debuff:
            self._draw_debuff_indicator(surface)

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
