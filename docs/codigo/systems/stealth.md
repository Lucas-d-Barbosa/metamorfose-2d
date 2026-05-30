# `systems/stealth.py` — Máquina de estados de alerta

## Resumo
Coração da IA de stealth. Define o enum **`AlertState`** e a classe
**`AlertStateMachine`**. Cada [NPC](../entities/npc.md) tem uma instância; a cena a
"tica" todo frame com dados dos sensores (vê/ouve o jogador) e ela decide o
comportamento.

## Os 4 estados
```
PATROL → SUSPICIOUS → ALERT → SEARCH → PATROL
```
| Estado | Significado | Cor |
|--------|-------------|-----|
| `PATROL` | rotina normal | verde |
| `SUSPICIOUS` | desconfiado (algo viu/ouviu) | amarelo |
| `ALERT` | detectou! persegue | vermelho |
| `SEARCH` | perdeu de vista, procura na última posição | laranja |

## Modelo de "suspeita" (0–100)
O comportamento é dirigido por um **medidor de suspeita** que enche e drena:
| Constante | Valor | Papel |
|-----------|-------|-------|
| `_FILL_RATES["sight"]` | 100/s | visão direta enche rápido |
| `_FILL_RATES["sound"]` | 30/s | som enche devagar |
| `_DRAIN_RATE` | 20/s | sem estímulo, drena |
| `_SUSPICIOUS_THRESHOLD` | 40 | vira SUSPICIOUS |
| `_ALERT_THRESHOLD` | 100 | vira ALERT |
| `_SEARCH_DURATION` | 6.0s | tempo procurando antes de voltar a patrulhar |

## `tick(dt, *, sees_player, hears_player, player_pos)`
1. Escolhe o estímulo: visão (prioridade) ou som. Atualiza `last_known_pos`.
2. Sobe a suspeita (`+stimulus*dt`) ou drena (`-_DRAIN_RATE*dt`), limitada a [0,100].
3. `_update_state(dt)` faz as transições conforme os limiares.
4. Retorna o estado atual.

### Transições (`_update_state`)
- `PATROL` → `ALERT` (suspeita ≥100) ou `SUSPICIOUS` (≥40).
- `SUSPICIOUS` → `ALERT` (≥100) ou volta a `PATROL` (chegou a 0).
- `ALERT` → `SEARCH` quando a suspeita zera (perdeu o alvo).
- `SEARCH` → conta `_search_timer`; após 6s sem reachar, limpa `last_known_pos` e volta
  a `PATROL`.

## Propriedades úteis
- **`suspicion_ratio`** — 0–1 (para a barra de alerta).
- **`color`** — cor do estado (usada no sprite e no cone de visão dos NPCs).

## Onde se encaixa
- Usada por [`NPC.update`](../entities/npc.md); o resultado escolhe patrulhar/perseguir/
  buscar. Os [Inquilinos](../entities/npcs/tenants.md) forçam `suspicion=100` para
  sincronizar o alerta em grupo.

## Pontos de apresentação
- "Não é liga/desliga: há um medidor que enche (ver enche mais rápido que ouvir) e
  drena — dá margem para o jogador recuar."
- "O estado SEARCH torna os inimigos 'inteligentes': eles vão até onde te viram por último."
