# `map/triggers.py` — Gatilhos e zonas de escuta (RF008)

## Resumo
Define **`TriggerZone`** (gatilho retangular genérico, com flag one-shot) e
**`ListeningZone`** (subclasse: o jogador precisa **ficar parado** dentro da zona por
alguns segundos para disparar uma fila de diálogos). Usado para eventos roteirizados e
"escutar conversas".

## `TriggerZone`
- **`is_inside(hitbox)`** — colisão com o retângulo.
- **`reset()`** — limpa a flag `activated` (reutilizar o gatilho).
- **`draw_debug(...)`** — desenha a zona em azul translúcido com rótulo.
- `one_shot` — se `True`, dispara só uma vez.

## `ListeningZone(TriggerZone)`
Constante: `IDLE_THRESHOLD = 8.0` px/s (abaixo disso = "parado").

### `__init__(rect, dialogues, required_still=2.0, label)`
Guarda a lista de diálogos `(falante, texto)` e quanto tempo parado é exigido.

### `update(dt, hitbox, velocity) -> list | None`
- Já ativada → `None`.
- Fora da zona ou se movendo (`velocity.length() > IDLE_THRESHOLD`) → zera o timer e
  retorna `None`.
- Parado dentro: acumula `_still_timer`; ao atingir `required_still`, marca `activated`
  e **retorna a lista de diálogos** (uma vez só).
- **`listen_progress`** (property) — razão 0–1 para indicador de HUD.

## Padrão de uso (na cena)
```python
fired = zone.update(dt, player.hitbox, player.velocity)
if fired:
    for speaker, text in fired:
        dialogue.show_dialogue(speaker, text)
```

## Onde se encaixa
- As fases criam `ListeningZone`s em pontos de narrativa; alimentam o sistema de
  [`dialogue`](../ui/dialogue.md).

## Pontos de apresentação
- "Recompensa a paciência: parar e escutar revela história."
- "`TriggerZone` é a base genérica reutilizada para qualquer evento por área."
