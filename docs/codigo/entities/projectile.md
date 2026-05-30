# `entities/projectile.py` — Projéteis (RF013)

## Resumo
Define **`Projectile`** (base) e **`AppleProjectile`** (a maçã crítica arremessada
pelo Pai na Fase 3). Movimento retilíneo top-down com tempo de vida, colisão com
paredes e detecção de acerto no jogador.

## Classe `Projectile`
Constantes (sobrescrevíveis): `RADIUS=6`, `SPEED=320`, `LIFETIME=3.0`, `COLOR`.

### Construtor `(origin, target)`
Calcula a velocidade na direção `target - origin`, normalizada × `SPEED`. Se origem ==
alvo, dispara para a direita por padrão. Estado: `alive`, `hit`.

### Métodos
- **`update(dt, tilemap)`** — acumula tempo; morre ao exceder `LIFETIME`; integra a
  posição; **morre se atingir parede** (`tilemap.is_solid_at`).
- **`check_hit(player_pos, player_radius=10)`** — colisão círculo-círculo: se as
  distâncias somam menos que os raios, marca `hit=True`, mata o projétil e retorna
  `True`.
- **`draw(surface, camera_offset)`** — desenha um círculo com **wobble** senoidal no
  raio (vida visual) e um contorno mais claro.

## Classe `AppleProjectile(Projectile)`
A maçã crítica: `RADIUS=7`, `SPEED=280`, `LIFETIME=2.5`, cor vermelha, e o marcador
`IS_APPLE = True`. **Ao acertar, a cena aplica o debuff permanente** da maçã ao
jogador (`player.apply_apple_debuff()`), que persiste para sempre via
[`save_manager`](../data/save_manager.md).

## Onde se encaixa
- Criado pelo [`Father`](npcs/father.md)/Fase 3 quando o Pai ataca.
- O acerto liga-se à mecânica permanente do [`Player`](player.md) e ao save.

## Pontos de apresentação
- "É o momento mais punitivo do jogo: a maçã marca o Gregor para o resto da partida."
- "Herança limpa: a maçã é só um `Projectile` com constantes diferentes + um flag."
