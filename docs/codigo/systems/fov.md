# `systems/fov.py` — Campo de visão (raycasting)

## Resumo
Implementa o **campo de visão (FOV)** dos NPCs com raycasting top-down. Decide se um
NPC enxerga o jogador (cone + linha de visão sem paredes) e desenha o cone na tela.
Três funções públicas: `check_los`, `is_in_fov`, `draw_fov_cone`.

## `check_los(start, end, tilemap) -> bool`
Verifica **linha de visão** entre dois pontos (estilo DDA):
- Calcula direção e distância; **amostra a cada meio tile** (`TILE_SIZE//2`).
- Se qualquer amostra cair num tile sólido, não há visão (`False`).
- Checa também o ponto final exato.

É uma aproximação por amostragem — simples e barata; meio tile evita "atravessar"
paredes finas.

## `is_in_fov(npc_pos, npc_angle, fov_deg, fov_range, target_pos, tilemap) -> bool`
Combina **três testes**:
1. **Distância** ≤ `fov_range`.
2. **Ângulo**: diferença entre o ângulo até o alvo e a direção do NPC, normalizada para
   [-180,180], deve estar dentro de `±fov_deg/2`.
3. **Linha de visão** livre (`check_los`).

O truque `(target_angle - npc_angle + 180) % 360 - 180` resolve a descontinuidade do
ângulo (wrap em ±180°).

## `draw_fov_cone(...)`
Desenha um **cone preenchido semitransparente** em espaço de tela:
- Lança `ray_count` (24) raios entre `-half_fov` e `+half_fov`.
- Monta um polígono (vértice no NPC + pontas dos raios) e o pinta com alfa.
- Cor e alfa vêm do estado de alerta (ver [`npc.draw_fov`](../entities/npc.md)).

> Nota: o cone desenhado é uma "pizza" simples; não recorta nas paredes (a detecção
> real, sim, via `check_los`). É dica visual, não precisão pixel-perfect.

## Onde se encaixa
- `is_in_fov`/`check_los` usados em [`NPC.update`](../entities/npc.md) para detecção.
- `draw_fov_cone` usado no desenho dos NPCs e no [debug overlay](debug_overlay.md).

## Pontos de apresentação
- "Detecção = dentro do cone E sem parede no caminho — não basta estar perto."
- "Raycasting por amostragem de meio tile: barato e suficiente para o estilo do jogo."
