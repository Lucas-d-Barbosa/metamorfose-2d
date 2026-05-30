# `map/tilemap.py` — Grade de tiles e colisão

## Resumo
Define a classe **`TileMap`**: o mapa baseado em grade de tiles. Converte uma matriz
2D de IDs de tile em geometria de colisão, responde consultas de "é sólido aqui?" e
desenha apenas os tiles visíveis na tela (culling).

## IDs de tile (constantes de módulo)
| ID | Nome | Sólido? | Significado |
|----|------|---------|-------------|
| 0 | `FLOOR` | não | chão andável |
| 1 | `WALL` | **sim** | parede |
| 2 | `FURNITURE` | **sim** | móvel/entulho (visual diferente) |
| 3 | `DOOR_OPEN` | não | vão de porta (passável) |
| 4 | `CEILING_ACCESS` | não | ponto para subir ao teto / rota de parede |

`_SOLID = {WALL, FURNITURE}` define o que bloqueia.

## Construtor
A partir do `layout` calcula linhas/colunas/largura/altura, constrói a lista de
`wall_rects` (um `pygame.Rect` por tile sólido) e **indexa esses rects num**
[`SpatialHash`](../systems/spatial_hash.md) (células de `tile_size*2`) para consulta
rápida de colisão.

## Métodos
- **`walls_near(hitbox)`** — devolve só as paredes que **realmente** podem colidir com
  o hitbox (consulta ao spatial hash). É a base de performance da colisão.
- **`is_solid_at(x, y)`** — converte pixel→célula; **fora do mapa conta como sólido**
  (impede sair pelas bordas).
- **`tile_at(x, y)`** — ID do tile naquele pixel (WALL se fora dos limites).
- **`draw(surface, camera_offset)`** — **culling**: calcula a janela de linhas/colunas
  visíveis e só desenha esses tiles, pegando a textura de
  [`tile_renderer.get_tile_surface`](../systems/tile_renderer.md).

## Por que culling + spatial hash?
Mapas grandes (até 42×24 tiles) teriam centenas de paredes. Desenhar/testar tudo todo
frame seria caro. O culling desenha só o que está na tela; o spatial hash testa
colisão só contra paredes próximas. Ambos mantêm 60 FPS.

## Onde se encaixa
- Construído em cada fase a partir de [`layouts`](layouts.md).
- Consultado por [`collision`](../systems/collision.md), [`fov`](../systems/fov.md),
  [`sound_propagation`](../systems/sound_propagation.md) e projéteis.

## Pontos de apresentação
- "O mapa é só uma matriz de números; tudo o mais (colisão, render) deriva dela."
- "Duas otimizações importantes: culling no desenho, spatial hash na colisão."
