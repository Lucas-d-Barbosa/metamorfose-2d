# `entities/npcs/manager.py` — O Gerente

## Resumo
Subclasse de [`NPC`](../npc.md). O **Gerente** é rápido e tem um cone de visão amplo;
patrulha perto da porta (Fase 1). Apenas redefine constantes de classe — toda a lógica
(patrulha, detecção, alerta) vem da base.

## Constantes
| Constante | Valor | vs. base |
|-----------|-------|----------|
| `fov_range` | 220.0 | maior (base 180) |
| `fov_angle` | 100.0 | mais amplo (base 90) |
| `speed` | 85.0 | mais rápido (base 70) |
| `sprite_key` | `"manager"` | sprite próprio |

## Papel no design
É o **inimigo de referência** do jogo: o FOV dos [Inquilinos](tenants.md) é definido
como o do Gerente × 1.3 (restrição GDD §7). Memorize estes números — eles aparecem nos
testes de QA.

## Pontos de apresentação
- "Herança em ação: o Gerente é literalmente 5 linhas — só os números mudam."
- "É a baseline de detecção contra a qual outros inimigos são calibrados."
