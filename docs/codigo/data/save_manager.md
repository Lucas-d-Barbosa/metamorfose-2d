# `data/save_manager.py` — Salvar e carregar (multi-slot)

## Resumo
Módulo de **persistência**. Salva/carrega o estado ([`EventFlags`](event_flags.md))
em arquivos JSON, **um por jogador**, identificados pelo apelido:
`saves/<nickname>.json`. Expõe uma API de funções (não há classe).

> Evolução: o `CLAUDE.md` menciona um `save.json` único na raiz; o código **atual** já
> usa múltiplos slots dentro de `saves/`. Esta documentação reflete o código real.

## API pública
| Função | O que faz |
|--------|-----------|
| `list_saves()` | Lista apelidos com save existente (ordem alfabética) |
| `save(flags, player, nickname)` | Grava o estado em `saves/<nick>.json` |
| `load(nickname)` | Carrega `EventFlags` (ou um novo se não existir) |
| `apply_to_player(flags, player)` | Restaura stats/debuffs em um `Player` novo |
| `has_save(nickname)` | Diz se existe save para o apelido |
| `delete_save(nickname)` | Apaga o save (silencioso se não existir) |

## Helpers internos
- **`_sanitize(nickname)`** — `re.sub(r"[^\w\- ]", "_", ...)` troca qualquer caractere
  perigoso (barras, pontos) por `_`. **Proteção contra path traversal** — impede que
  um apelido vire um caminho arbitrário no disco.
- **`_path(nickname)`** — devolve o `Path` final `saves/<sanitizado>.json`.

## Pontos críticos

### 1. Debuff da maçã é permanente (restrição GDD §7)
No `save()`:
```python
data["apple_debuff"] = flags.apple_debuff or player.apple_debuff
```
A **lógica OR** garante que, uma vez `True`, o debuff *nunca* volta a `False` —
persiste por morte, reinício de fase e recarregamento. É a invariante mais importante
do sistema de save.

### 2. Não reaplicar multiplicadores ao carregar
No `apply_to_player()`, quando `apple_debuff` é `True`, ele **só** seta a flag, sem
multiplicar de novo a stamina — porque os stats já foram salvos *com* o multiplicador
aplicado. Reaplicar causaria "double-apply" (stamina caindo pela metade a cada load).

### 3. Carregamento tolerante a falhas
`load()` retorna um `EventFlags()` novo se o arquivo não existe **ou** se o JSON está
corrompido (`except json.JSONDecodeError, TypeError`). O jogo nunca trava por save ruim.

## Onde se encaixa
- Usado por [`ProfileSelectScene`](../scene/profile_select.md) (listar/criar/escolher
  perfil) e pelas fases (salvar progresso ao concluir).
- Opera sobre [`EventFlags`](event_flags.md) e [`Player`](../entities/player.md).
- A pasta `saves/` é ignorada pelo Git (dados de runtime).

## Pontos de apresentação
- "Multi-slot: cada apelido tem seu próprio save."
- "Duas invariantes de ouro: o debuff da maçã nunca reverte (OR), e os stats não são
  multiplicados duas vezes ao carregar."
- "Apelidos são sanitizados — segurança contra nomes de arquivo maliciosos."
