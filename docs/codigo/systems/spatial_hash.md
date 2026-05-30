# `systems/spatial_hash.py` — Hash espacial

## Resumo
Define **`SpatialHash`**, uma estrutura de aceleração de propósito geral para
`pygame.Rect`. Particiona o espaço em **células de tamanho fixo** para responder
rapidamente "quais retângulos podem colidir com este aqui?" sem testar todos.

## Por que existe
Um mapa grande tem centenas de paredes. Testar a colisão do jogador contra **todas**
elas a cada frame é O(n). O hash espacial reduz isso para ~O(1) na prática: só testa as
paredes nas **mesmas células** do jogador. É a fase "broad-phase" da colisão.

## API
- **`__init__(cell_size=64)`** — tamanho da célula (no jogo, `tile_size*2`).
- **`insert(rect)`** — adiciona um rect a todas as células que ele cobre.
- **`build(rects)`** — limpa e insere uma lista inteira (reconstruir quando o mapa muda).
- **`query(rect)`** — devolve os rects que **realmente** intersectam o `rect`,
  **deduplicados** (um rect grande aparece em várias células; usa `id()` num `set` para
  não repetir).

## Helper interno
- **`_cell_coords(rect)`** — devolve todas as coordenadas de célula que o rect cobre
  (divisão inteira de cada canto pelo `cell_size`).

## Onde se encaixa
- Construído dentro do [`TileMap`](../map/tilemap.md) com as `wall_rects`; consultado
  por `tilemap.walls_near(hitbox)`, que alimenta a [colisão](collision.md).

## Pontos de apresentação
- "Otimização clássica: dividir o mundo em grade e só olhar a vizinhança."
- "Transforma colisão de 'testar tudo' em 'testar o que está perto'."
