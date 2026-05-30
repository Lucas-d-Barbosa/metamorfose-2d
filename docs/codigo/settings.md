# `settings.py` — Constantes de tuning

## Resumo
Centraliza **todas as constantes de configuração e balanceamento** do jogo. Regra de
ouro do projeto (ver `CLAUDE.md`): *nunca* hardcode valores em cenas/entidades —
sempre importe daqui. Todas as constantes usam `typing.Final` (sinalizam que não
devem ser reatribuídas).

## Grupos de constantes

### Tela e tempo
| Constante | Valor | Significado |
|-----------|-------|-------------|
| `SCREEN_WIDTH` / `SCREEN_HEIGHT` | 1280 × 720 | Resolução da janela |
| `FPS` | 60 | Quadros por segundo alvo |
| `TILE_SIZE` | 32 | Lado de um tile em pixels |

### Cores (`Color = Tuple[int,int,int]`)
`BLACK`, `WHITE`, `RED`, `GREEN`, `BLUE`, `GRAY`, `DARK_GRAY`, `AMBER` — paleta base
reutilizada por HUD, sprites e cenas.

### Jogador
| Constante | Valor | Significado |
|-----------|-------|-------------|
| `BASE_SPEED` | 160.0 | Velocidade base (px/s) |
| `ACCELERATION` | 1200.0 | Aceleração |
| `FRICTION` | 10.0 | Fator de atrito (usado no `lerp` de velocidade) |

### Stamina e fome
| Constante | Valor | Significado |
|-----------|-------|-------------|
| `STAMINA_DECAY_RATE` | 12.0 | Decaimento de stamina por segundo |
| `CEILING_STAMINA_MODIFIER` | 0.5 | No teto, a stamina cai pela metade |
| `HUNGER_DECAY_RATE` | 4.0 | Decaimento de fome por segundo |

### Propagação de som
| Constante | Valor | Significado |
|-----------|-------|-------------|
| `FOOTSTEP_NOISE_RADIUS` | 120.0 | Raio do ruído de passos |
| `VOICE_NOISE_RADIUS` | 200.0 | Raio do ruído de voz |
| `COUGH_NOISE_RADIUS` | `FOOTSTEP × 2.0` = 240.0 | **Restrição GDD**: tosse = 2× passo |
| `VOICE_ALERT_MULTIPLIER` | 0.5 | Peso da voz no alerta |

### Lixo e maçã
| Constante | Valor | Significado |
|-----------|-------|-------------|
| `TRASH_COUGH_DELAY` | 1.5 | Segundos dentro do lixo até tossir |
| `APPLE_STAMINA_PENALTY` | 0.5 | Maçã reduz stamina máxima à metade |
| `APPLE_SPEED_PENALTY` | 0.7 | Maçã reduz velocidade a 70% |

### Fog of war por fase
```python
FOG_RADIUS_BY_PHASE = {1: 1.0, 2: 1.0, 3: 0.6, 4: 0.4}
```
Fração do raio de visão (1.0 = sem névoa). Fases 1–2 sem névoa; fase 3 a 60%; fase 4
a 40% (mais escura/tensa).

## Onde se encaixa
Importado por praticamente todos os módulos. É a **fonte única de verdade** do
balanceamento — alterar o jogo significa, em muitos casos, só mudar um número aqui.

## Pontos de apresentação
- "Todo o balanceamento está em um arquivo só — fácil de ajustar e de testar."
- As constantes derivadas (`COUGH_NOISE_RADIUS`, `FOG_RADIUS_BY_PHASE`) refletem
  **restrições do GDD** verificadas pelos testes de QA.
