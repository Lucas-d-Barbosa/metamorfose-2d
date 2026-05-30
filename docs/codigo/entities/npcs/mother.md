# `entities/npcs/mother.py` — A Mãe

## Resumo
Subclasse de [`NPC`](../npc.md). A **Mãe** patrulha devagar com FOV amplo. É central na
**Missão do Quadro** (Fase 2): se Gregor entrar no campo de visão dela, o evento falha.

## Constantes
| Constante | Valor |
|-----------|-------|
| `fov_range` | 160.0 |
| `fov_angle` | 90.0 (amplo) |
| `speed` | 50.0 (lenta) |
| `sprite_key` | `"mother"` |

## Papel no design
Lenta porém vigilante: o desafio com a Mãe não é fugir, é **evitar a linha de visão**
enquanto se cumpre o objetivo do quadro. Ligada à flag `saved_picture` em
[`event_flags`](../../data/event_flags.md).

## Pontos de apresentação
- "Inimiga 'de paciência': você espera o cone passar, não corre dela."
