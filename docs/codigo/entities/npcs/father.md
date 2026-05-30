# `entities/npcs/father.py` — O Pai

## Resumo
Subclasse de [`NPC`](../npc.md). O **Pai** é o inimigo mais agressivo: FOV mais
estreito que o Gerente, porém **muito mais rápido**. Ao encostar no jogador aplica
knockback; na **Fase 3** também arremessa maçãs ([`AppleProjectile`](../projectile.md),
RF013) que aplicam o debuff permanente.

## Constantes
| Constante | Valor |
|-----------|-------|
| `fov_range` / `fov_angle` | 170 / 80° (estreito) |
| `speed` | 115.0 (o mais rápido) |
| `KNOCKBACK_FORCE` | 500.0 |
| `CONTACT_RADIUS` | `TILE_SIZE` |

Constantes de módulo: `THROW_COOLDOWN = 4.5s`, `THROW_RANGE = 280.0`.

## Construtor
`Father(waypoints, room_center=(0,0), throws_apples=False)`:
- `room_center` — direção do knockback "pra dentro da sala".
- `throws_apples` — liga o arremesso (ativado só na Fase 3).
- `_throw_timer` começa em metade do cooldown (primeiro arremesso vem mais cedo).

## Métodos
- **`try_knockback(player)`** — se o jogador está dentro de `CONTACT_RADIUS`, aplica
  `receive_knockback` na direção de fuga. Retorna `True` se empurrou.
- **`try_throw(dt, player_pos)`** — RF013: acumula o timer; se passou o cooldown **e**
  o jogador está em alcance, zera o timer e retorna uma `AppleProjectile` mirada no
  jogador. Caso contrário `None`. Só age quando `throws_apples=True`.
  - O import de `AppleProjectile` é **tardio** (dentro do método) para evitar import
    circular.

## Onde se encaixa
- Instanciado em [`phase1`](../../scene/phase1.md) e [`phase3`](../../scene/phase3.md).
- O acerto da maçã liga-se ao debuff permanente do [`Player`](../player.md).

## Pontos de apresentação
- "Inimigo mais perigoso: rápido, empurra e — na Fase 3 — marca você com a maçã."
- "Diferente do faxineiro, o contato do Pai tem peso narrativo e mecânico."
