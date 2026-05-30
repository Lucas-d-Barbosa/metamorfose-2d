# `entities/npcs/janitor.py` — A Faxineira (RF014)

## Resumo
Subclasse de [`NPC`](../npc.md). A **Faxineira** tem patrulha caótica e, ao colidir com
o jogador, aplica knockback com a vassoura. **Restrição crítica do GDD**: ela *nunca*
causa Game Over nem eleva o alerta global da casa — é apenas um obstáculo cinético.

## Constantes
| Constante | Valor |
|-----------|-------|
| `fov_range` / `fov_angle` | 100 / 80° (visão curta) |
| `speed` | 58.0 |
| `CONTACT_RADIUS` | `TILE_SIZE * 1.2` |
| `KNOCKBACK_FORCE` | 380.0 |

## Método `try_sweep(player)`
Se o jogador está dentro de `CONTACT_RADIUS`, aplica `receive_knockback` na direção de
fuga e retorna `True`. **Diferente do [Pai](father.md)**: não muda estado de alerta nem
chama `transition_to`/`game_over`.

## Invariante de design (GDD)
> *"Janitor never triggers game over"* — `try_sweep` só aplica knockback. Verificado
> por teste de QA. Nunca referencia `game_over`.

## Pontos de apresentação
- "Perigo 'inofensivo': te atrapalha e te joga pra longe, mas não te mata."
- "Bom exemplo de inimigo que cria caos sem ser letal."
