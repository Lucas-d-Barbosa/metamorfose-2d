# `entities/npc.py` — NPC base (patrulha + detecção)

## Resumo
Define a classe base **`NPC`** (herda `pygame.sprite.Sprite`). Implementa
**patrulha por waypoints** e **detecção stealth** baseada em campo de visão (FOV) e
audição. Cada NPC possui uma [`AlertStateMachine`](../systems/stealth.md) que dirige
seu comportamento. As subclasses (Gerente, Pai, etc.) só ajustam constantes.

## Constantes sobrescrevíveis (de classe)
| Constante | Default | Significado |
|-----------|---------|-------------|
| `fov_range` | 180.0 | Alcance do cone de visão |
| `fov_angle` | 90.0 | Abertura do cone (graus) |
| `speed` | 70.0 | Velocidade de patrulha |
| `color` | marrom | Cor do fallback |
| `sprite_key` | `"generic"` | Chave do sprite no gerador |

## Construtor
Recebe uma lista de **waypoints** (≥1, garantido por `assert`). Inicializa posição no
primeiro waypoint, velocidade, `facing_angle`, índice de waypoint, timer de espera
(`_wait_at_wp = 1.2s`) e a `AlertStateMachine`.

## `update(dt, tilemap, player, sound_system=None)`
O cérebro do NPC, por frame:
1. **Vê?** `is_in_fov(...)` checa se o jogador está no cone (com raycasting contra
   paredes via [`fov`](../systems/fov.md)).
2. **Ouve?** `sound_system.heard_at(...)` (se houver sistema de som).
3. **Tick da máquina de alerta** — passa `sees_player=sees and not player.hidden` e
   `hears_player`. Retorna o novo estado.
4. **Age conforme o estado**:
   - `PATROL`/`SUSPICIOUS` → `_patrol`
   - `ALERT` → `_chase` (persegue o jogador, 1.6× a velocidade)
   - `SEARCH` → `_search` (vai à última posição conhecida, 0.8× a velocidade)
5. `_redraw_sprite()` — atualiza imagem (com **ponto colorido** indicando o estado de
   alerta) e rotaciona conforme o `facing_angle`.

## Comportamentos de movimento
- **`_patrol`** — caminha até o waypoint atual; ao chegar (`dist < 4`), espera
  `_wait_at_wp` e avança para o próximo (ciclo com módulo).
- **`_chase`** — vai direto ao jogador, acelerado (×1.6).
- **`_search`** — vai à `last_known_pos` da máquina de alerta (×0.8); para ao chegar.

## Renderização de depuração/feedback
- **`draw_fov(surface, camera_offset)`** — desenha o cone de visão, **colorido pelo
  estado** (amarelo patrulha → vermelho alerta), via [`fov.draw_fov_cone`](../systems/fov.md).
- **`draw_alert_bar(...)`** — barra de suspeita acima do NPC (só aparece com suspeita
  ≥ 1). Usa offset Y fixo porque a altura da imagem varia com a rotação.

## Onde se encaixa
- Subclasseado em [`entities/npcs/`](manager.md) (cada personagem).
- Usa [`stealth`](../systems/stealth.md), [`fov`](../systems/fov.md),
  [`sprite_generator`](../systems/sprite_generator.md).
- As fases passam `sound_system` para os NPCs ouvirem ruído.

## Pontos de apresentação
- "Toda a IA dos inimigos vive aqui; cada personagem só muda números (FOV, velocidade)."
- "Três velocidades por estado: patrulha normal, perseguição rápida, busca lenta."
- "O cone muda de cor conforme a suspeita — feedback visual imediato pro jogador."
