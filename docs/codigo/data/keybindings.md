# `data/keybindings.py` — Mapeamento de teclas

## Resumo
Sistema de **remapeamento de teclas**. Carrega bindings de `data/keybindings.json`
(se existir) ou usa defaults. Expõe um singleton **`KB`** que todas as cenas usam para
ler teclas, em vez de hardcodar `pygame.K_*`.

## Uso típico
```python
from data.keybindings import KB

if event.key == KB.INTERACT: ...        # via __getattr__
keys = pygame.key.get_pressed()
if keys[KB.MOVE_UP]: ...
```

## Defaults (`_DEFAULTS`)
| Ação | Tecla |
|------|-------|
| `MOVE_UP/DOWN/LEFT/RIGHT` | W / S / A / D |
| `INTERACT` | E |
| `SPEAK` | F |
| `THOUGHT` | T |
| `Z_LEVEL` | C (alternar chão/teto) |
| `DEBUG` | F3 |
| `PAUSE` | ESC |
| `CONFIRM` | ENTER |
| `SKIP` | ESPAÇO |

## Classe `_KeyBindings`
- **`__init__`** — copia os defaults e tenta `_load()`.
- **`_load()`** — lê o JSON; para cada ação conhecida, aceita **tanto** um inteiro
  (código da tecla) **quanto** uma string com o nome da constante Pygame (ex.: `"K_w"`,
  resolvido via `getattr(pygame, ...)`). Ignora chaves desconhecidas e JSON inválido.
- **`save()`** — grava os bindings atuais usando `pygame.key.name(key)` (nomes
  legíveis em vez de números).
- **`get(name)` / `set(name, key)`** — acesso programático; `set` só aceita ações
  válidas (presentes em `_DEFAULTS`).
- **`__getattr__(name)`** — açúcar sintático: `KB.INTERACT` devolve o código da tecla.
  Protege contra recursão ignorando nomes que começam com `_`.

## Singleton `KB`
No fim do módulo: `KB = _KeyBindings()`. Uma única instância compartilhada por todo o
jogo (importar o módulo já carrega o JSON uma vez).

## Onde se encaixa
- Importado pelas cenas/entidades para ler input.
- Complementa o input direto em [`Player._read_input`](../entities/player.md), que
  hoje ainda usa `pygame.K_w/a/s/d` fixos (ponto de melhoria: passar a usar `KB`).

## Pontos de apresentação
- "Permite remapear teclas sem mexer no código — basta um JSON."
- "Aceita nomes legíveis (`K_w`) ou códigos numéricos; salva sempre no formato legível."
