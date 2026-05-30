# `main.py` — Ponto de entrada

## Resumo
Arquivo mais curto do projeto (4 linhas). É o **ponto de entrada** executado com
`python main.py`. Apenas importa a classe `Game` e inicia o loop.

## Código
```python
from game import Game

if __name__ == "__main__":
    Game().run()
```

## O que faz
1. Importa `Game` de [`game.py`](game.md).
2. Sob a guarda `if __name__ == "__main__"` (só roda quando executado diretamente,
   não quando importado), cria uma instância de `Game` e chama `.run()`.

## Onde se encaixa
É o topo da cadeia de execução. Toda a lógica real vive em `game.py` e nas cenas.
Manter `main.py` mínimo é um padrão comum: facilita testes (importar `game` sem
disparar o loop) e deixa o entrypoint trivial.

## Ponto de apresentação
- "O jogo começa aqui, mas é só um disparador — a arquitetura real está no `Game`."
- Comando para rodar: `python main.py`.
