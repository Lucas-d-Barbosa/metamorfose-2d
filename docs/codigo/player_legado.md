# `player.py` (raiz) — Stub legado

## Resumo
Arquivo de **compatibilidade** com 2 linhas. A implementação real do jogador foi
movida para [`entities/player.py`](entities/player.md). Este arquivo só reexporta a
classe `Player` para que imports antigos (`from player import Player`) não quebrem.

## Código
```python
# Arquivo legado — use entities/player.py
from entities.player import Player  # noqa: F401
```

- `# noqa: F401` silencia o aviso do linter de "import não usado" (o import existe
  justamente para ser reexportado).

## Situação atual
Nenhum módulo do jogo importa daqui (a busca por `from player import` só encontra
este próprio arquivo). É efetivamente **código morto mantido por segurança**. Pode
ser removido sem impacto, desde que nenhum script externo dependa dele.

> Não confundir com [`entities/player.py`](entities/player.md), que é a classe real.

## Ponto de apresentação
- "Resquício de refatoração: o jogador foi reorganizado para `entities/`, e este stub
  evita quebrar imports antigos."
