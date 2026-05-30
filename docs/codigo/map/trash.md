# `map/trash.py` — Zonas de lixo e poeira (RF011)

## Resumo
Define **`TrashZone`** (hitbox de lixo que faz Gregor tossir) e **`DustParticle`**
(efeito visual de poeira). Tossir é arriscado: emite um ruído grande
(`COUGH_NOISE_RADIUS` = 2× passo) que pode atrair NPCs.

## `TrashZone`
Constantes: `COUGH_COOLDOWN = 4.0s`.

### `update(dt, hitbox, player_moving) -> bool`
Retorna `True` **exatamente uma vez** quando a tosse deve disparar:
1. Em cooldown? decrementa e retorna `False`.
2. Fora da zona? zera o timer.
3. Dentro: se **andando**, o timer sobe; se parado, **decai lentamente** (×0.4) — não
   dá para "burlar" ficando imóvel.
4. Ao atingir `TRASH_COUGH_DELAY` (1.5s), zera o timer, ativa o cooldown e dispara.

- **`timer_ratio`** (property) — progresso 0–1 (para HUD/debug).
- **`draw_debug`** — desenha a zona com preenchimento proporcional ao timer.

## `DustParticle`
Partícula simples gerada ao atravessar o lixo:
- Velocidade inicial aleatória pra cima/lados; `lifetime` 0.35–0.75s.
- **`update`** — integra posição, aplica **arrasto horizontal** e leve **gravidade**.
- **`alive`** (property) — viva enquanto `_elapsed < lifetime`.
- **`draw`** — círculo que **desvanece** (alpha cai com o tempo).

## Builders
- **`build_phase3_trash_zones()`** / **`build_phase4_trash_zones()`** — listas de zonas
  com coordenadas casadas ao entulho dos [`layouts`](layouts.md) das fases 3 e 4.

## Onde se encaixa
- A cena chama `zone.update(...)`; no `True`, emite um `NoiseEvent` de tosse via
  [`sound_propagation`](../systems/sound_propagation.md) e cria poeira.
- A tosse alta = restrição GDD (`COUGH_NOISE_RADIUS = FOOTSTEP × 2`).

## Pontos de apresentação
- "Atravessar o lixo é tenso: a tosse te entrega com um ruído enorme."
- "Não dá pra trapacear parando: o timer decai devagar, mas o lixo ainda incomoda."
