"""
scene/transition.py

ChapterTransitionScene — shown between phases as a chapter-break cinematic.

States:
  "end_card"   auto-advances after CARD_HOLD seconds (chapter-end title card)
  "dialogue"   typewriter lines, ENTER to advance / ESC to skip all
  "start_card" auto-advances after CARD_HOLD seconds (next-chapter title card)
  → then transition_to(next_scene)
"""

import pygame

from scene.base_scene import BaseScene
from settings import SCREEN_HEIGHT, SCREEN_WIDTH

# ---------------------------------------------------------------------------
# Timing
# ---------------------------------------------------------------------------

CARD_HOLD  = 2.8   # seconds to hold each title card
CS_SPEED   = 40.0  # typewriter chars per second

# ---------------------------------------------------------------------------
# Chapter data
# ---------------------------------------------------------------------------
# speaker == "" renders as a narrator caption (no speaker label, dimmer colour)

_CHAPTERS: dict[str, dict] = {
    "1_2": {
        "end_title":   "FIM — CAPÍTULO I",
        "end_sub":     "O Despertar e o Pânico",
        "start_title": "CAPÍTULO II",
        "start_sub":   "Adaptação e as Memórias",
        "bg":          (4, 4, 6),
        "next_scene":  "phase2",
        "lines": [
            ("Gerente",  "Aaaah! O que é isso?! Meu Deus!"),
            ("Mãe",      "(som de desmaio imediato)"),
            ("Pai",      "Volte para lá! Volte agora, seu monstro!"),
            ("",         "— Dias se passaram. —"),
            ("Gregor",   "Preciso encontrar comida antes que amanheça."),
        ],
        "tips": [
            "A casa está mais escura — a família dorme, mas os sons carregam.",
            "Explore a cozinha e a sala para encontrar comida antes do amanhecer.",
            "Fique longe do quarto do Pai — ele reage rápido ao menor barulho.",
        ],
    },
    "2_3": {
        "end_title":   "FIM — CAPÍTULO II",
        "end_sub":     "Adaptação e as Memórias",
        "start_title": "CAPÍTULO III",
        "start_sub":   "A Agressão e a Deterioração",
        "bg":          (6, 4, 4),
        "next_scene":  "phase3",
        "lines": [
            ("Gregor", "Só o quadro restou. Meu último elo com quem eu fui."),
            ("",       "— O quarto virou depósito. —"),
            ("Pai",    "O que foi essa confusão? Ela desmaiou de novo?!"),
            ("Grete",  "Foi ele, pai! Ele escapou do quarto!"),
            ("Pai",    "Eu já disse para vocês! Eu sabia que isso ia acontecer!"),
        ],
        "tips": [
            "A névoa de guerra se intensifica — você enxerga menos longe.",
            "Os inquilinos são implacáveis e patrulham em grupo sincronizado.",
            "Se o Pai te atingir com a maçã, o efeito é permanente.",
        ],
    },
    "3_4": {
        "end_title":   "FIM — CAPÍTULO III",
        "end_sub":     "A Agressão e a Deterioração",
        "start_title": "CAPÍTULO IV",
        "start_sub":   "A Música e a Morte",
        "bg":          (6, 3, 3),
        "next_scene":  "phase4",
        "lines": [
            ("Gregor",     "A dor vai passando. Mas algo ficou diferente. Permanente."),
            ("Gregor",     "A maçã apodreceu nas minhas costas. Não consigo tirá-la."),
            ("",           "— O apartamento foi alugado a três senhores rigorosos. —"),
            ("Faxineira",  "Anda, sai do meio do caminho, seu besouro velho."),
            ("Faxineira",  "Não tenho medo de você, não."),
        ],
        "tips": [
            "A névoa é densa — o campo de visão está muito reduzido.",
            "Siga o som do violino de Grete: é sua única orientação.",
            "Esta é a última fase. Não há mais retorno.",
        ],
    },
}

# ---------------------------------------------------------------------------
# Scene
# ---------------------------------------------------------------------------

class ChapterTransitionScene(BaseScene):

    def __init__(self, game, chapter_id: str) -> None:
        super().__init__(game)
        self._chapter = _CHAPTERS[chapter_id]
        self._state  = "end_card"
        self._timer  = 0.0

        # Dialogue state
        self._cs_line:    int   = 0
        self._cs_chars:   float = 0.0
        self._cs_waiting: bool  = False

        # Phase tips state
        self._tip_idx: int = 0

    # =========================================================================
    # BaseScene interface
    # =========================================================================

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type != pygame.KEYDOWN:
            return
        if self._state == "dialogue":
            if event.key == pygame.K_ESCAPE:
                self._skip_to_start_card()
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                if self._cs_waiting:
                    self._advance_line()
                else:
                    line_len = len(self._chapter["lines"][self._cs_line][1])
                    self._cs_chars = float(line_len) + 1.0
        elif self._state == "phase_tips":
            if event.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_ESCAPE):
                self.transition_to(self._chapter["next_scene"])

    def update(self, dt: float) -> None:
        if self._state == "end_card":
            self._timer += dt
            if self._timer >= CARD_HOLD:
                self._enter_dialogue()
        elif self._state == "dialogue":
            self._update_dialogue(dt)
        elif self._state == "start_card":
            self._timer += dt
            if self._timer >= CARD_HOLD:
                tips = self._chapter.get("tips")
                if tips:
                    self._state = "phase_tips"
                    self._tip_idx = 0
                else:
                    self.transition_to(self._chapter["next_scene"])
        # phase_tips waits for key input (handled in handle_event)

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill(self._chapter["bg"])
        if self._state == "end_card":
            self._draw_card(surface, self._chapter["end_title"],
                            self._chapter["end_sub"])
        elif self._state == "dialogue":
            self._draw_dialogue(surface)
        elif self._state == "start_card":
            self._draw_card(surface, self._chapter["start_title"],
                            self._chapter["start_sub"])
        elif self._state == "phase_tips":
            self._draw_phase_tips(surface)

    # =========================================================================
    # State transitions
    # =========================================================================

    def _enter_dialogue(self) -> None:
        self._state = "dialogue"
        self._cs_line    = 0
        self._cs_chars   = 0.0
        self._cs_waiting = False

    def _advance_line(self) -> None:
        self._cs_line   += 1
        self._cs_chars   = 0.0
        self._cs_waiting = False
        if self._cs_line >= len(self._chapter["lines"]):
            self._skip_to_start_card()

    def _skip_to_start_card(self) -> None:
        self._state = "start_card"
        self._timer = 0.0

    # =========================================================================
    # Dialogue update
    # =========================================================================

    def _update_dialogue(self, dt: float) -> None:
        if self._cs_waiting:
            return
        line_len = len(self._chapter["lines"][self._cs_line][1])
        self._cs_chars += CS_SPEED * dt
        if self._cs_chars >= line_len:
            self._cs_chars   = float(line_len)
            self._cs_waiting = True

    # =========================================================================
    # Draw helpers
    # =========================================================================

    def _draw_phase_tips(self, surface: pygame.Surface) -> None:
        tips = self._chapter.get("tips", [])
        cx = SCREEN_WIDTH  // 2
        cy = SCREEN_HEIGHT // 2

        # Header
        hfont = pygame.font.SysFont("serif", 22)
        hsurf = hfont.render("DICAS PARA O PRÓXIMO CAPÍTULO", True, (160, 140, 90))
        surface.blit(hsurf, hsurf.get_rect(centerx=cx, centery=cy - 80))
        pygame.draw.line(surface, (60, 52, 38),
                         (cx - 220, cy - 60), (cx + 220, cy - 60), 1)

        # Tips list
        tfont = pygame.font.SysFont("serif", 18)
        bfont = pygame.font.SysFont("monospace", 12)
        for i, tip in enumerate(tips):
            bullet = bfont.render("•", True, (130, 110, 60))
            tsurf  = tfont.render(tip, True, (195, 188, 170))
            row_y  = cy - 30 + i * 34
            surface.blit(bullet, (cx - 230, row_y - 9))
            surface.blit(tsurf, tsurf.get_rect(left=cx - 210, centery=row_y))

        # Advance hint
        pfont = pygame.font.SysFont("monospace", 11)
        psurf = pfont.render("[ ENTER ] Começar o capítulo", True, (65, 60, 48))
        surface.blit(psurf, psurf.get_rect(centerx=cx, centery=SCREEN_HEIGHT - 28))

    def _draw_card(self, surface: pygame.Surface,
                   title: str, subtitle: str) -> None:
        cx = SCREEN_WIDTH  // 2
        cy = SCREEN_HEIGHT // 2

        # Title
        tfont = pygame.font.SysFont("serif", 36)
        tsurf = tfont.render(title, True, (215, 200, 170))
        surface.blit(tsurf, tsurf.get_rect(centerx=cx, centery=cy - 22))

        # Subtitle
        sfont = pygame.font.SysFont("serif", 20)
        ssurf = sfont.render(subtitle, True, (165, 148, 118))
        surface.blit(ssurf, ssurf.get_rect(centerx=cx, centery=cy + 16))

        # Decorative line under title
        pygame.draw.line(surface, (80, 72, 58),
                         (cx - 140, cy + 4), (cx + 140, cy + 4), 1)

        # Wait hint
        hfont = pygame.font.SysFont("monospace", 10)
        hint  = hfont.render("[ aguarde... ]", True, (50, 48, 44))
        surface.blit(hint, hint.get_rect(centerx=cx,
                                          centery=SCREEN_HEIGHT - 28))

    def _draw_dialogue(self, surface: pygame.Surface) -> None:
        if self._cs_line >= len(self._chapter["lines"]):
            return

        speaker, full_text = self._chapter["lines"][self._cs_line]
        visible = full_text[:int(self._cs_chars)]

        cx = SCREEN_WIDTH  // 2
        cy = SCREEN_HEIGHT // 2

        if speaker:
            # Speaker label
            nfont = pygame.font.SysFont("monospace", 13)
            nsurf = nfont.render(speaker.upper(), True, (145, 128, 96))
            surface.blit(nsurf, nsurf.get_rect(centerx=cx, centery=cy - 32))
            # Dialogue text
            tfont = pygame.font.SysFont("serif", 22)
            tsurf = tfont.render(visible, True, (215, 205, 185))
            surface.blit(tsurf, tsurf.get_rect(centerx=cx, centery=cy))
        else:
            # Narrator caption — dimmer, no label
            nfont = pygame.font.SysFont("serif", 18)
            nsurf = nfont.render(visible, True, (130, 120, 102))
            surface.blit(nsurf, nsurf.get_rect(centerx=cx, centery=cy))

        # Advance prompt
        if self._cs_waiting:
            pfont = pygame.font.SysFont("monospace", 11)
            psurf = pfont.render("[ ENTER ] Continuar  |  [ ESC ] Pular",
                                 True, (68, 62, 52))
            surface.blit(psurf, psurf.get_rect(centerx=cx,
                                                centery=SCREEN_HEIGHT - 28))

        # Line progress
        cfont = pygame.font.SysFont("monospace", 10)
        csurf = cfont.render(
            f"{self._cs_line + 1}/{len(self._chapter['lines'])}",
            True, (50, 46, 40),
        )
        surface.blit(csurf, (SCREEN_WIDTH - 42, SCREEN_HEIGHT - 18))
