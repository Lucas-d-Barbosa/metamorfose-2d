"""
scene/profile_select.py

Tela de seleção / criação de perfil de jogador.

Estados internos
----------------
"list"   — navega perfis existentes + opção "Novo perfil"
"typing" — digita um nickname novo
"confirm_delete" — confirma exclusão de um perfil

Fluxo de transição
------------------
Perfil novo          → intro_cutscene (primeira vez no jogo)
Perfil existente p=1 → phase1          (voltando antes de terminar cap. 1)
Perfil existente p≥2 → phase{n}        (continua de onde parou)
"""

import pygame

import data.save_manager as save_mgr
from scene.base_scene import BaseScene
from settings import AMBER, DARK_GRAY, SCREEN_HEIGHT, SCREEN_WIDTH, WHITE

_BG         = DARK_GRAY
_TITLE_COL  = AMBER
_SEL_COL    = (240, 220, 140)
_IDLE_COL   = (140, 128, 100)
_HINT_COL   = (70, 65, 52)
_ERROR_COL  = (210, 70, 60)
_NEW_COL    = (100, 180, 110)
_DEL_COL    = (200, 70, 60)

_PHASE_SCENES: dict[int, str] = {
    1: "phase1",
    2: "phase2",
    3: "phase3",
    4: "phase4",
}


class ProfileSelectScene(BaseScene):

    def __init__(self, game) -> None:
        super().__init__(game)

        self._profiles: list[str] = save_mgr.list_saves()
        self._cursor:   int       = 0        # 0..len(profiles) inclusive; last = "Novo"
        self._state:    str       = "list"

        # Typing state
        self._input:    str       = ""
        self._error:    str       = ""

        # Delete-confirm state
        self._del_target: str     = ""

        # Fonts
        self._title_font = pygame.font.SysFont("serif", 38)
        self._item_font  = pygame.font.SysFont("monospace", 18)
        self._hint_font  = pygame.font.SysFont("monospace", 12)
        self._sub_font   = pygame.font.SysFont("serif", 16)

        self._blink      = 0.0
        self._blink_vis  = True

    # ------------------------------------------------------------------
    # BaseScene interface
    # ------------------------------------------------------------------

    def handle_event(self, event: pygame.event.Event) -> None:
        if self._state == "list":
            self._handle_list(event)
        elif self._state == "typing":
            self._handle_typing(event)
        elif self._state == "confirm_delete":
            self._handle_delete_confirm(event)

    def update(self, dt: float) -> None:
        self._blink += dt
        if self._blink >= 0.55:
            self._blink     = 0.0
            self._blink_vis = not self._blink_vis

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill(_BG)
        if self._state == "list":
            self._draw_list(surface)
        elif self._state == "typing":
            self._draw_typing(surface)
        elif self._state == "confirm_delete":
            self._draw_delete_confirm(surface)

    # ------------------------------------------------------------------
    # List state
    # ------------------------------------------------------------------

    def _handle_list(self, event: pygame.event.Event) -> None:
        if event.type != pygame.KEYDOWN:
            return
        n = len(self._profiles)  # index n == "Novo perfil"

        if event.key in (pygame.K_UP, pygame.K_w):
            self._cursor = (self._cursor - 1) % (n + 1)
        elif event.key in (pygame.K_DOWN, pygame.K_s):
            self._cursor = (self._cursor + 1) % (n + 1)
        elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
            if self._cursor == n:
                self._state = "typing"
                self._input = ""
                self._error = ""
            else:
                self._launch_profile(self._profiles[self._cursor])
        elif event.key == pygame.K_DELETE:
            if self._cursor < n:
                self._del_target = self._profiles[self._cursor]
                self._state = "confirm_delete"
        elif event.key == pygame.K_ESCAPE:
            self.transition_to("menu")

    def _launch_profile(self, nickname: str) -> None:
        self.game.nickname = nickname
        flags = save_mgr.load(nickname)
        scene = _PHASE_SCENES.get(flags.phase, "phase1")
        # New save (phase=1, nothing done) → full intro experience
        if flags.phase == 1 and not flags.phase1_complete:
            scene = "intro_cutscene"
        self.transition_to(scene)

    def _draw_list(self, surface: pygame.Surface) -> None:
        cx = SCREEN_WIDTH  // 2
        cy_start = 160

        # Title
        ts = self._title_font.render("Metamorfose", True, _TITLE_COL)
        surface.blit(ts, ts.get_rect(centerx=cx, centery=80))

        sub = self._sub_font.render("Selecione um perfil ou crie um novo", True, _IDLE_COL)
        surface.blit(sub, sub.get_rect(centerx=cx, centery=122))

        pygame.draw.line(surface, (55, 48, 36), (cx - 220, 140), (cx + 220, 140), 1)

        # Profile list
        row_h = 44
        n     = len(self._profiles)
        for i, name in enumerate(self._profiles):
            y      = cy_start + i * row_h
            sel    = (i == self._cursor)
            color  = _SEL_COL if sel else _IDLE_COL
            prefix = "▶ " if sel else "  "

            # Load phase info for this profile
            flags = save_mgr.load(name)
            phase_tag = f"Cap. {flags.phase}" if flags.phase > 1 else "Cap. 1"

            item  = self._item_font.render(f"{prefix}{name}", True, color)
            ptag  = self._hint_font.render(phase_tag, True,
                                           (100, 160, 100) if sel else (65, 65, 65))
            surface.blit(item, item.get_rect(centerx=cx - 20, centery=y))
            surface.blit(ptag, ptag.get_rect(
                left=cx + item.get_width() // 2 + 12, centery=y))

            if sel:
                pygame.draw.line(surface, _SEL_COL,
                                 (cx - 160, y + 14), (cx + 160, y + 14), 1)

        # "Novo perfil" option
        new_y   = cy_start + n * row_h
        new_sel = (self._cursor == n)
        new_col = _NEW_COL if new_sel else (60, 100, 65)
        new_pre = "▶ " if new_sel else "  "
        ns      = self._item_font.render(f"{new_pre}+ Novo perfil", True, new_col)
        surface.blit(ns, ns.get_rect(centerx=cx, centery=new_y))

        # Bottom hints
        hints = "↑↓ Navegar   ENTER Selecionar   DEL Apagar perfil   ESC Menu"
        hs = self._hint_font.render(hints, True, _HINT_COL)
        surface.blit(hs, hs.get_rect(centerx=cx, centery=SCREEN_HEIGHT - 24))

    # ------------------------------------------------------------------
    # Typing state
    # ------------------------------------------------------------------

    def _handle_typing(self, event: pygame.event.Event) -> None:
        if event.type != pygame.KEYDOWN:
            return
        if event.key == pygame.K_ESCAPE:
            self._state = "list"
            self._error = ""
        elif event.key == pygame.K_RETURN:
            self._try_create()
        elif event.key == pygame.K_BACKSPACE:
            self._input = self._input[:-1]
            self._error = ""
        else:
            if len(self._input) < 20 and event.unicode and event.unicode.isprintable():
                self._input += event.unicode
                self._error = ""

    def _try_create(self) -> None:
        name = self._input.strip()
        if len(name) < 2:
            self._error = "Nome muito curto — mínimo 2 caracteres."
            return
        if name.lower() in [p.lower() for p in self._profiles]:
            self._error = "Já existe um perfil com este nome."
            return
        self.game.nickname = name
        self.transition_to("intro_cutscene")

    def _draw_typing(self, surface: pygame.Surface) -> None:
        cx = SCREEN_WIDTH  // 2
        cy = SCREEN_HEIGHT // 2

        ts = self._title_font.render("Novo perfil", True, _TITLE_COL)
        surface.blit(ts, ts.get_rect(centerx=cx, centery=cy - 120))

        prompt = self._sub_font.render("Digite seu nickname:", True, _IDLE_COL)
        surface.blit(prompt, prompt.get_rect(centerx=cx, centery=cy - 68))

        # Input box
        box_w, box_h = 320, 40
        box_rect = pygame.Rect(cx - box_w // 2, cy - 30, box_w, box_h)
        pygame.draw.rect(surface, (22, 20, 16), box_rect)
        pygame.draw.rect(surface, _SEL_COL, box_rect, 1)

        cursor_str = "_" if self._blink_vis else " "
        text_surf  = self._item_font.render(self._input + cursor_str, True, WHITE)
        surface.blit(text_surf, text_surf.get_rect(
            midleft=(box_rect.left + 10, box_rect.centery)))

        if self._error:
            es = self._hint_font.render(self._error, True, _ERROR_COL)
            surface.blit(es, es.get_rect(centerx=cx, centery=cy + 24))

        hints_text = "ENTER Confirmar   ESC Cancelar"
        hs = self._hint_font.render(hints_text, True, _HINT_COL)
        surface.blit(hs, hs.get_rect(centerx=cx, centery=SCREEN_HEIGHT - 24))

    # ------------------------------------------------------------------
    # Delete-confirm state
    # ------------------------------------------------------------------

    def _handle_delete_confirm(self, event: pygame.event.Event) -> None:
        if event.type != pygame.KEYDOWN:
            return
        if event.key in (pygame.K_RETURN, pygame.K_y):
            save_mgr.delete_save(self._del_target)
            self._profiles = save_mgr.list_saves()
            self._cursor   = min(self._cursor, len(self._profiles))
            self._state    = "list"
        elif event.key in (pygame.K_ESCAPE, pygame.K_n):
            self._state = "list"

    def _draw_delete_confirm(self, surface: pygame.Surface) -> None:
        cx = SCREEN_WIDTH  // 2
        cy = SCREEN_HEIGHT // 2

        # Dim overlay
        ov = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        ov.fill((0, 0, 0, 160))
        surface.blit(ov, (0, 0))

        msg = self._sub_font.render(
            f'Apagar o perfil  "{self._del_target}"?', True, WHITE)
        surface.blit(msg, msg.get_rect(centerx=cx, centery=cy - 24))

        warn = self._hint_font.render(
            "Esta ação não pode ser desfeita.", True, _DEL_COL)
        surface.blit(warn, warn.get_rect(centerx=cx, centery=cy + 8))

        confirm = self._hint_font.render(
            "ENTER / Y — Confirmar     ESC / N — Cancelar", True, _HINT_COL)
        surface.blit(confirm, confirm.get_rect(centerx=cx, centery=cy + 40))
