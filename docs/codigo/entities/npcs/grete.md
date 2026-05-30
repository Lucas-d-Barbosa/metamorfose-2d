# `entities/npcs/grete.py` — Grete (irmã)

## Resumo
Subclasse de [`NPC`](../npc.md). **Grete**, a irmã de Gregor, é mais rápida que a Mãe
mas tem FOV **estreito** (olha focada para frente). Personagem narrativamente
importante (é quem mais se relaciona com Gregor no conto).

## Constantes
| Constante | Valor |
|-----------|-------|
| `fov_range` | 130.0 |
| `fov_angle` | 70.0 (estreito) |
| `speed` | 65.0 |
| `sprite_key` | `"grete"` |

## Papel no design
FOV estreito = fácil de flanquear pelos lados, mas pega quem fica na frente. Contraste
de design com a [Mãe](mother.md) (lenta/ampla) e o [Pai](father.md) (rápido/estreito).

## Pontos de apresentação
- "Grete vê pouco de lado — dá pra passar pelas costas/flancos dela."
