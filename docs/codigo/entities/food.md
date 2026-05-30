# `entities/food.py` — Itens de comida (RF010)

## Resumo
Define **`FoodItem`** e o enum **`FoodType`** (`FRESH`/`ROTTEN`). Mecânica temática da
metamorfose: como inseto, Gregor **repugna comida fresca** (dano) e **adora comida
podre** (recupera stamina). Cada item flutua (efeito "bob"), mostra um prompt `[E]
Comer` e dispara um pensamento ao ser consumido.

## Tipos e efeitos
| Tipo | Efeito ao comer | Pensamento |
|------|-----------------|-----------|
| `FRESH` (leite, maçã, pão) | **Dano**: −25% da stamina máxima | nojo |
| `ROTTEN` (queijo velho, restos, legumes) | **Cura**: +20–30% da stamina | prazer |

Retorna `"repulse"` ou `"restore"` para a cena reagir.

## Atributos e constantes
- `food_type`, `variant` (ex.: `"milk"`), `consumed`.
- `_INTERACTION_RANGE = 48.0` — distância para poder comer.
- `_SIZE = 16` — lado do sprite.

## Métodos
- **`_make_image()`** — desenha o item por código: anel de brilho, corpo, brilho
  interno e, se podre, manchas verdes de mofo. Azulado para fresco, marrom para podre.
- **`update(dt)`** — animação de flutuação: `bob = sin(elapsed*2.8)*2.0` desloca o
  `centery` verticalmente (item "boia").
- **`is_near(player_pos)`** — `True` se dentro do alcance e não consumido.
- **`consume(player, dialogue)`** — aplica o efeito, mata o sprite (`kill()`), mostra
  um pensamento aleatório colorido e retorna `"repulse"`/`"restore"`. Idempotente.
- **`draw_prompt(surface, camera_offset)`** — desenha `[ E ] Comer` com fundo
  translúcido acima do item.

## Onde se encaixa
- Espalhado pelas fases; a cena chama `is_near` + `consume` ao apertar interagir.
- Usa [`dialogue`](../ui/dialogue.md) para os pensamentos.
- A **maçã** propriamente dita como arma é o [`AppleProjectile`](projectile.md) (Fase 3).

## Pontos de apresentação
- "Inversão sensorial da metamorfose virou mecânica: comida boa machuca, lixo cura."
- "Comida podre é o único jeito de recuperar stamina — incentiva explorar o lixo."
