# `game.py` — Loop principal e máquina de estados de cenas

## Resumo
Define a classe **`Game`**, o coração do jogo: ela é dona da janela Pygame, do
relógio (FPS), do efeito CRT e da **cena atual**. Mantém um registro de todas as
cenas (`_SCENE_REGISTRY`) e troca de cena quando a cena atual pede.

## Estruturas principais

### `_SCENE_REGISTRY: dict`
Mapeia **nomes de cena → classe da cena**. Quando uma cena define
`self.next_scene = "phase2"`, o `Game` procura `"phase2"` aqui e instancia a classe.

```python
_SCENE_REGISTRY = {
    "menu": MenuScene,
    "profile_select": ProfileSelectScene,
    "intro_cutscene": IntroCutsceneScene,
    "tutorial": TutorialScene,
    "phase1": Phase1Scene, ... "phase4": Phase4Scene,
    "game_over": GameOverScene,
    "epilogue": EpilogueScene,
    "transition_1_2": partial(ChapterTransitionScene, chapter_id="1_2"),
    ...
}
```
As transições usam `functools.partial` para **pré-preencher** o `chapter_id`, de
modo que todas as transições reusam a mesma classe `ChapterTransitionScene` com
argumentos diferentes.

### Classe `Game`

| Membro | Papel |
|--------|-------|
| `self.screen` | Superfície da janela (`SCREEN_WIDTH × SCREEN_HEIGHT`) |
| `self.clock` | `pygame.time.Clock` — controla os 60 FPS |
| `self.crt` | Instância de [`CRT`](crt.md), desenhada por cima de tudo |
| `self.nickname` | Apelido do jogador, definido por `ProfileSelectScene` |
| `self.current_scene` | A cena ativa (começa em `MenuScene`) |

#### Métodos
- **`run()`** — o loop principal. Cada iteração:
  1. `dt = clock.tick(FPS) / 1000.0` → tempo do frame em **segundos** (delta time).
  2. `_handle_events()` → repassa eventos à cena.
  3. `_update(dt)` → atualiza a cena e checa transição.
  4. `_draw()` → desenha a cena, depois o CRT, e dá `flip()`.
- **`_handle_events()`** — itera `pygame.event.get()`; trata `QUIT` (fecha o jogo) e
  delega cada evento a `current_scene.handle_event(event)`.
- **`_update(dt)`** — chama `current_scene.update(dt)`; se a cena setou `next_scene`,
  chama `_transition`.
- **`_draw()`** — desenha a cena, o overlay CRT e atualiza a tela.
- **`_transition(scene_name)`** — busca a classe no registro e **instancia uma cena
  nova** (estado da cena anterior é descartado). Erro se o nome não existe.
- **`register_scene(name, cls)`** — permite registrar cenas extras sem editar este
  arquivo (extensibilidade).

## Conceito-chave: delta time
Todo movimento usa `dt` (segundos do frame). Isso torna a física **independente do
FPS** — se o jogo rodar mais lento, `dt` cresce e os objetos andam proporcionalmente
mais por frame, mantendo a velocidade real constante.

## Onde se encaixa
- Instanciado por [`main.py`](main.md).
- Cada cena herda de [`BaseScene`](scene/base_scene.md) e recebe `self` (o `Game`) no
  construtor, podendo acessar `game.screen`, `game.nickname`, etc.

## Pontos de apresentação
- "É uma máquina de estados: só uma cena ativa por vez; a troca é dirigida por dados
  (`_SCENE_REGISTRY`), não por `if`s espalhados."
- "O CRT é desenhado por último, então o efeito retrô cobre toda a tela."
