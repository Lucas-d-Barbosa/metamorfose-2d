# `data/event_flags.py` — Estado persistente do jogo

## Resumo
Define a **`EventFlags`**, uma `@dataclass` que contém **todo o estado que precisa
sobreviver entre sessões** (progresso, flags narrativas e stats do jogador). É o
objeto serializado para/de JSON pelo [`save_manager`](save_manager.md).

## Campos

### Progresso
| Campo | Default | Significado |
|-------|---------|-------------|
| `phase` | 1 | Fase atual |
| `phase1_complete` … `phase3_complete` | `False` | Fases já concluídas |

### Flags narrativas
| Campo | Default | Significado |
|-------|---------|-------------|
| `saved_picture` | `False` | Missão do Quadro (Fase 2) |
| `apple_debuff` | `False` | Maçã Crítica (Fase 3) — **permanente** |
| `door_unlocked_phase1` | `False` | Porta destrancada na Fase 1 |

### Stats persistentes do jogador
`max_stamina`, `current_stamina`, `max_hunger`, `current_hunger` (todos `float`,
default 100.0). Guardados porque o debuff da maçã modifica `max_stamina`
permanentemente.

## Métodos
- **`to_dict()`** — usa `dataclasses.asdict` para virar um `dict` serializável.
- **`from_dict(data)`** (classmethod) — reconstrói a partir de um `dict`,
  **filtrando chaves desconhecidas** (`if k in cls.__dataclass_fields__`). Isso
  torna o carregamento **tolerante a saves antigos**: campos que não existem mais são
  ignorados, e campos ausentes assumem o default.

## Por que dataclass?
- Gera `__init__`, `__repr__` e igualdade automaticamente.
- Defaults explícitos = "valores de novo jogo".
- `asdict` dá serialização gratuita.

## Onde se encaixa
- Criado/lido por [`save_manager.py`](save_manager.md).
- Aplicado ao [`Player`](../entities/player.md) via `apply_to_player`.

## Ponto de apresentação
- "É o 'cartão de memória' do jogo: uma única estrutura com tudo que persiste."
- "`from_dict` filtra chaves — saves de versões antigas não quebram o jogo."
