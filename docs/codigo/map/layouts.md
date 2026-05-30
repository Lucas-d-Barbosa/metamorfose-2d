# `map/layouts.py` — Geração das salas

## Resumo
Gera os **layouts (matrizes de tiles) de cada fase por código** — uma função por fase.
É uma solução temporária até mapas Tiled (`.tmx`) ficarem prontos. Cada função devolve
uma `list[list[int]]` de IDs de tile que alimenta o [`TileMap`](tilemap.md).

## Helpers de construção
- **`_empty(rows, cols)`** — preenche tudo com `FLOOR`.
- **`_border(layout)`** — transforma a borda inteira em `WALL`.
- **`_fill_rect(layout, r1, c1, r2, c2, tile)`** — preenche um retângulo com um tile
  (usado para móveis/entulho).

## Salas por fase
| Função | Dimensões | Tema |
|--------|-----------|------|
| `phase1_room()` | 24×16 (cabe inteira na tela) | Quarto de Gregor: cama, guarda-roupa, escrivaninha, acesso ao teto, porta |
| `phase2_room()` | 42×24 | Quarto **esvaziado**; só o quadro (objetivo) e marcas de arranhão no teto |
| `phase3_room()` | 42×24 | Quarto virou depósito: **labirinto de entulho** (Pai patrulha) |
| `phase4_room()` | 42×24 | O lixão/música: labirinto denso + passagem para a sala na parede direita |

Cada sala define os vãos de porta (`DOOR_OPEN`), pilhas de móveis (`FURNITURE`) e
faixas de `CEILING_ACCESS` (rotas pelo teto/parede).

## Relação com outros arquivos
As posições de móveis aqui precisam **bater** com:
- [`hiding_zones`](hiding_zones.md) — esconderijos junto aos móveis.
- [`trash`](trash.md) — zonas de lixo sobre o entulho das fases 3/4.

Por isso há comentários alinhando coordenadas (ex.: "cama nas linhas 4–6 → acesso ao
teto na linha 7").

## Pontos de apresentação
- "Os mapas são desenhados em código com 3 helpers simples — fácil de iterar."
- "A progressão narrativa aparece no mapa: o mesmo quarto vai sendo esvaziado e
  virando depósito/lixão fase a fase."
