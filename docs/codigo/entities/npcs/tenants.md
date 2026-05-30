# `entities/npcs/tenants.py` — Os Três Inquilinos

## Resumo
Define **`Tenant`** (subclasse de [`NPC`](../npc.md)) e **`TenantGroup`** (wrapper de 3
inquilinos). Os inquilinos têm o **maior FOV do jogo** e **compartilham alerta**: se um
vê o jogador, todos sabem na hora.

## `Tenant` — constantes (GDD §7)
| Constante | Valor | Origem |
|-----------|-------|--------|
| `fov_range` | 286.0 | Gerente 220 × 1.3 |
| `fov_angle` | 130.0 | Gerente 100 × 1.3 |
| `speed` | 72.0 | — |
| `sprite_key` | `"tenant"` | — |

> **Restrição GDD**: FOV dos Inquilinos = FOV do [Gerente](manager.md) × 1.3.
> Verificada pelo teste `TestTenantFOV`.

## `TenantGroup`
Trata três inquilinos como uma unidade.

- **`__init__(waypoint_sets)`** — exige exatamente 3 listas de waypoints (`assert`).
  Escalona o waypoint inicial de cada um (`_wp_index = i`) para se espalharem pela sala.
- **`update(dt, tilemap, player, sound_system)`** — atualiza os três e depois chama
  `_sync_alert`.
- **`_sync_alert()`** — se **qualquer** inquilino está em `ALERT`, força a suspeita dos
  outros a 100 (entram em alerta instantaneamente). É o "um viu → todos sabem".
- **Proxies** para a cena tratar o grupo como lista: `__iter__`, `__len__`,
  `alert_states`, `any_alerted()`.
- **Desenho**: `draw_fov_all` (cones) e `draw_sprites_all` (sprites + barras de alerta),
  usando a [câmera](../../systems/camera.md).

## Onde se encaixa
- Usados na fase dos inquilinos (Fase 4). O alerta compartilhado os torna o desafio
  stealth mais difícil — não dá para isolar um.

## Pontos de apresentação
- "Maior visão do jogo + alerta em grupo = a fase mais tensa."
- "O número 1.3 não é mágico: vem direto do GDD e é travado por teste."
