# `map/hiding_zones.py` — Esconderijos (RF004)

## Resumo
Define **`HidingZone`**: retângulos onde Gregor fica **escondido**. Quando o hitbox do
jogador entra na zona, a cena seta `player.hidden = True`; os [NPCs](../entities/npc.md)
já checam `player.hidden` antes de reportar uma detecção.

## Classe `HidingZone`
- **`__init__(rect, label)`** — guarda o retângulo (frestas, embaixo de móveis) e um
  rótulo (ex.: "cama").
- **`contains(hitbox)`** — `True` se o hitbox colide com a zona.
- **`draw_debug(surface, camera_offset)`** — desenha a zona em verde translúcido com o
  rótulo (visível no overlay de debug).

## Builder
- **`build_phase1_hiding_zones(tile_size=32)`** — devolve as 3 zonas da Fase 1
  (cama, guarda-roupa, escrivaninha), com coordenadas **alinhadas** ao
  [`phase1_room()`](layouts.md).

## Onde se encaixa
- A cena chama `contains(player.hitbox)` a cada frame; se alguma zona contém o jogador,
  ele fica invisível para os NPCs e **não emite ruído** de passos (o `noise_radius` é
  zerado quando `hidden`).

## Pontos de apresentação
- "Esconder é binário e simples: dentro do retângulo = invisível."
- "Acoplado ao stealth: NPC só denuncia se `not player.hidden`."
