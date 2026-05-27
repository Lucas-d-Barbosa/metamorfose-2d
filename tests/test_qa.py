"""
Bateria de testes QA — valida os Critérios de Aceitação do GDD §7.

Executa sem janela (headless pygame). Rode com:
    python -m pytest tests/test_qa.py -v
ou
    python tests/test_qa.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pygame
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
pygame.init()
pygame.display.set_mode((1, 1))

import unittest
import json
import tempfile
from pathlib import Path


# ---------------------------------------------------------------------------
# GDD §7.1 — Estamina no teto = 50% do valor base
# ---------------------------------------------------------------------------
class TestCeilingStamina(unittest.TestCase):
    def test_decay_modifier_is_exactly_half(self):
        from settings import CEILING_STAMINA_MODIFIER
        self.assertAlmostEqual(CEILING_STAMINA_MODIFIER, 0.5,
                               msg="CEILING_STAMINA_MODIFIER deve ser 0.5")

    def test_player_ceiling_decay_halved(self):
        from entities.player import Player
        from settings import STAMINA_DECAY_RATE, CEILING_STAMINA_MODIFIER

        p = Player(100, 100)
        p.max_stamina = 100.0
        p.current_stamina = 100.0
        p.go_to_ceiling()

        # Simulate 1 second moving
        original_dir = p.direction
        p.direction = pygame.math.Vector2(1, 0)
        p._update_stats(1.0)

        floor_decay = STAMINA_DECAY_RATE * 1.0
        ceiling_decay = floor_decay * CEILING_STAMINA_MODIFIER
        expected = 100.0 - ceiling_decay
        self.assertAlmostEqual(p.current_stamina, expected, places=2,
                               msg="Decay no teto deve ser 50% do decay no chão")


# ---------------------------------------------------------------------------
# GDD §7.2 — Apple debuff persiste através de save/load
# ---------------------------------------------------------------------------
class TestAppleDebuffPersistence(unittest.TestCase):
    def _temp_save_path(self):
        return Path(tempfile.mktemp(suffix=".json"))

    def test_debuff_survives_save_load(self):
        import data.save_manager as sm
        from data.event_flags import EventFlags
        from entities.player import Player

        tmp = self._temp_save_path()
        original_path = sm._SAVE_PATH
        sm._SAVE_PATH = tmp

        try:
            flags = EventFlags()
            flags.apple_debuff = True
            player = Player(0, 0)
            player.apply_apple_debuff()

            sm.save(flags, player)

            loaded = sm.load()
            self.assertTrue(loaded.apple_debuff,
                            "apple_debuff deve ser True após load")

            p2 = Player(0, 0)
            sm.apply_to_player(loaded, p2)
            self.assertTrue(p2.apple_debuff,
                            "apply_to_player deve restaurar apple_debuff")
            self.assertAlmostEqual(p2.max_stamina, 50.0, places=1,
                                   msg="max_stamina deve ser 50 com debuff")
        finally:
            sm._SAVE_PATH = original_path
            tmp.unlink(missing_ok=True)

    def test_debuff_or_logic(self):
        """Once True, apple_debuff never reverts to False on save."""
        import data.save_manager as sm
        from data.event_flags import EventFlags
        from entities.player import Player

        tmp = self._temp_save_path()
        original_path = sm._SAVE_PATH
        sm._SAVE_PATH = tmp

        try:
            flags = EventFlags()
            flags.apple_debuff = True
            player = Player(0, 0)
            player.apple_debuff = False  # mismatch — flags says True

            sm.save(flags, player)
            loaded = sm.load()
            self.assertTrue(loaded.apple_debuff,
                            "OR lógico: flags.True deve prevalecer sobre player.False")
        finally:
            sm._SAVE_PATH = original_path
            tmp.unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# GDD §7.3 — Lixo: 1.5s → tosse com raio 2× passos
# ---------------------------------------------------------------------------
class TestTrashCough(unittest.TestCase):
    def test_cough_delay(self):
        from settings import TRASH_COUGH_DELAY
        self.assertAlmostEqual(TRASH_COUGH_DELAY, 1.5,
                               msg="TRASH_COUGH_DELAY deve ser 1.5s")

    def test_cough_radius_double_footstep(self):
        from settings import COUGH_NOISE_RADIUS, FOOTSTEP_NOISE_RADIUS
        self.assertAlmostEqual(COUGH_NOISE_RADIUS, FOOTSTEP_NOISE_RADIUS * 2.0,
                               msg="COUGH_NOISE_RADIUS deve ser 2× FOOTSTEP")

    def test_cough_fires_after_1_5s(self):
        from map.trash import TrashZone
        import pygame as pg

        zone = TrashZone(pg.Rect(0, 0, 64, 64), label="test")
        hitbox = pg.Rect(10, 10, 20, 20)

        # Accumulate 1.4s — should NOT fire yet
        result = False
        t = 0.0
        while t < 1.4:
            dt = 0.1
            result = zone.update(dt, hitbox, player_moving=True)
            t += dt
        self.assertFalse(result, "Não deve tossir antes de 1.5s")

        # One more step past 1.5s — should fire
        result = zone.update(0.15, hitbox, player_moving=True)
        self.assertTrue(result, "Deve tossir após 1.5s de movimento")

    def test_cough_cooldown_prevents_immediate_repeat(self):
        from map.trash import TrashZone
        import pygame as pg

        zone = TrashZone(pg.Rect(0, 0, 64, 64), label="test")
        hitbox = pg.Rect(10, 10, 20, 20)

        zone.update(1.6, hitbox, player_moving=True)  # fires once

        # Immediately after: should NOT fire again
        result = zone.update(1.6, hitbox, player_moving=True)
        self.assertFalse(result, "Cooldown deve impedir segunda tosse imediata")


# ---------------------------------------------------------------------------
# GDD §7.4 — FOV dos Inquilinos = Manager × 1.3
# ---------------------------------------------------------------------------
class TestTenantFOV(unittest.TestCase):
    def test_tenant_fov_30pct_larger_than_manager(self):
        from entities.npcs.manager import Manager
        from entities.npcs.tenants import Tenant

        self.assertAlmostEqual(
            Tenant.fov_angle, Manager.fov_angle * 1.3, places=0,
            msg="Tenant.fov_angle deve ser Manager.fov_angle × 1.3"
        )
        self.assertAlmostEqual(
            Tenant.fov_range, Manager.fov_range * 1.3, places=0,
            msg="Tenant.fov_range deve ser Manager.fov_range × 1.3"
        )

    def test_tenant_group_shared_alert(self):
        from entities.npcs.tenants import TenantGroup
        from systems.stealth import AlertState

        wps = [
            [(100,100),(200,100)],
            [(300,100),(400,100)],
            [(500,100),(600,100)],
        ]
        group = TenantGroup(wps)

        # Force one tenant to ALERT
        group.tenants[0].alert.suspicion = 100.0
        group.tenants[0].alert.state = AlertState.ALERT

        # Sync
        group._sync_alert()

        for i, t in enumerate(group.tenants):
            self.assertGreaterEqual(
                t.alert.suspicion, 100.0,
                f"Tenant {i} deveria ter suspicion=100 após sync"
            )


# ---------------------------------------------------------------------------
# GDD §7.5 — Fog of War radii corretos por fase
# ---------------------------------------------------------------------------
class TestFogOfWar(unittest.TestCase):
    def test_fog_radii_by_phase(self):
        from settings import FOG_RADIUS_BY_PHASE
        self.assertAlmostEqual(FOG_RADIUS_BY_PHASE[1], 1.0,
                               msg="Fase 1: sem fog (ratio 1.0)")
        self.assertAlmostEqual(FOG_RADIUS_BY_PHASE[2], 1.0,
                               msg="Fase 2: sem fog (ratio 1.0)")
        self.assertAlmostEqual(FOG_RADIUS_BY_PHASE[3], 0.6,
                               msg="Fase 3: 60%")
        self.assertAlmostEqual(FOG_RADIUS_BY_PHASE[4], 0.4,
                               msg="Fase 4: 40%")

    def test_fog_phase1_skipped(self):
        from systems.fog_of_war import FogOfWar, _SKIP_PHASES
        self.assertIn(1, _SKIP_PHASES)
        self.assertIn(2, _SKIP_PHASES)

    def test_fog_phase3_radius_smaller_than_phase1(self):
        from systems.fog_of_war import FogOfWar
        f1 = FogOfWar(1)
        f3 = FogOfWar(3)
        f4 = FogOfWar(4)
        self.assertGreater(f1.radius, f3.radius,
                           "Fase 1 deve ter raio maior que Fase 3")
        self.assertGreater(f3.radius, f4.radius,
                           "Fase 3 deve ter raio maior que Fase 4")

    def test_fog_load_save_uses_correct_phase(self):
        """FogOfWar deve ser inicializado com a fase correta do save."""
        import data.save_manager as sm
        from data.event_flags import EventFlags
        from systems.fog_of_war import FogOfWar, FOG_RADIUS_BY_PHASE
        import math

        flags = EventFlags(phase=3)
        fog = FogOfWar(flags.phase)
        diag = math.sqrt(1280**2 + 720**2)
        expected_r = int(diag * FOG_RADIUS_BY_PHASE[3] * 0.5)
        self.assertEqual(fog.radius, expected_r)


# ---------------------------------------------------------------------------
# GDD §7.6 — Faxineira nunca invoca Game Over
# ---------------------------------------------------------------------------
class TestJanitorNoGameOver(unittest.TestCase):
    def test_janitor_has_no_game_over_trigger(self):
        """Janitor.try_sweep deve retornar bool, não transicionar cenas."""
        import inspect
        from entities.npcs.janitor import Janitor

        src = inspect.getsource(Janitor.try_sweep)
        self.assertNotIn("game_over", src,
                         "try_sweep não deve mencionar game_over")
        self.assertNotIn("transition_to", src,
                         "try_sweep não deve chamar transition_to")

    def test_janitor_fov_alert_does_not_propagate(self):
        """Janitor não tem shared alert — é independente."""
        from entities.npcs.janitor import Janitor
        # Janitor should not be a TenantGroup member
        j = Janitor([(0, 0)])
        self.assertFalse(hasattr(j, 'tenants'),
                         "Janitor não deve ter atributo 'tenants'")


# ---------------------------------------------------------------------------
# GDD §7.7 — Violin panning muda com coordenada X/Y
# ---------------------------------------------------------------------------
class TestViolinPanning(unittest.TestCase):
    def test_pan_right_when_source_is_to_the_right(self):
        from systems.violin import ViolinSystem
        v = ViolinSystem(pygame.math.Vector2(1000, 300))
        v.update(pygame.math.Vector2(100, 300))  # player left of source
        self.assertGreater(v.pan_right, v.pan_left,
                           "pan_right deve ser maior quando fonte está à direita")

    def test_pan_left_when_source_is_to_the_left(self):
        from systems.violin import ViolinSystem
        v = ViolinSystem(pygame.math.Vector2(100, 300))
        v.update(pygame.math.Vector2(1000, 300))  # player right of source
        self.assertGreater(v.pan_left, v.pan_right,
                           "pan_left deve ser maior quando fonte está à esquerda")

    def test_volume_decreases_with_distance(self):
        from systems.violin import ViolinSystem
        source = pygame.math.Vector2(500, 300)
        v = ViolinSystem(source)

        v.update(pygame.math.Vector2(500, 300))   # at source
        vol_near = v.volume

        v.update(pygame.math.Vector2(0, 0))        # far away
        vol_far = v.volume

        self.assertGreater(vol_near, vol_far,
                           "Volume deve diminuir com a distância")


# ---------------------------------------------------------------------------
# GDD §7.8 — Player speed debuff
# ---------------------------------------------------------------------------
class TestAppleSpeedDebuff(unittest.TestCase):
    def test_effective_speed_reduced(self):
        from entities.player import Player
        from settings import BASE_SPEED, APPLE_SPEED_PENALTY

        p = Player(0, 0)
        speed_before = p.effective_speed

        p.apply_apple_debuff()
        speed_after = p.effective_speed

        expected = BASE_SPEED * APPLE_SPEED_PENALTY
        self.assertAlmostEqual(speed_after, expected, places=1,
                               msg="Velocidade com debuff deve ser BASE_SPEED × APPLE_SPEED_PENALTY")
        self.assertLess(speed_after, speed_before)


# ---------------------------------------------------------------------------
# Run
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    loader = unittest.TestLoader()
    suite  = loader.loadTestsFromModule(__import__(__name__))
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)
