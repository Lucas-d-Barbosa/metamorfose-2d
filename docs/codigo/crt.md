# `crt.py` — Efeito visual CRT

## Resumo
Define a classe **`CRT`**, um overlay visual que imita um monitor CRT antigo
(scanlines horizontais + vinheta escura nas bordas). Dá ao jogo a estética retrô
"GBA/anos 90". Desenhado por último, por cima de toda a cena.

## Classe `CRT`

### `__init__(self, screen)`
Pré-renderiza **dois overlays** uma única vez (otimização — não recalcula por frame):

1. **Scanlines** (`self.scanlines`):
   - Superfície do tamanho da tela com canal alfa (`SRCALPHA`).
   - Desenha uma linha preta a cada 2 pixels na vertical (`range(0, height, 2)`).
   - `set_alpha(35)` → linhas bem sutis (translúcidas).

2. **Vinheta** (`self.vignette`):
   - Desenha um retângulo preto **só com borda** (espessura `border`), escurecendo
     as margens da tela. `border = max(24, min(w,h)//12)`.
   - `set_alpha(70)` → escurecimento moderado das bordas.

### `draw(self)`
Faz `blit` dos dois overlays na tela, na ordem scanlines → vinheta. Chamado por
`Game._draw()` depois da cena e antes do `pygame.display.flip()`.

## Por que pré-renderizar?
Gerar as linhas e a vinheta toda frame seria caro. Como o efeito é estático,
criamos as superfícies uma vez no `__init__` e só fazemos `blit` (barato) por frame.

## Onde se encaixa
- Criado em [`game.py`](game.md) (`self.crt = CRT(self.screen)`).
- Chamado em `Game._draw()` após a cena ser desenhada.

## Pontos de apresentação
- "É puramente cosmético, mas vende a estética retrô do jogo."
- "Performance: os overlays são gerados uma vez; o loop só faz dois `blit`."
