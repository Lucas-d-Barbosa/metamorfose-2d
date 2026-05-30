# Documentação de Código — Metamorfose 2D

Documentação técnica **arquivo por arquivo** do jogo *Metamorfose 2D* (Python/Pygame),
uma adaptação stealth top-down de *A Metamorfose* de Kafka. Cada arquivo de código-fonte
tem um `.md` correspondente nesta pasta, espelhando a estrutura de diretórios do projeto.

> Use esta pasta como roteiro de apresentação: cada documento explica **o que o arquivo faz,
> onde ele se encaixa na arquitetura, suas classes/funções principais e os pontos-chave do GDD**.

## Como o jogo está organizado

O jogo é uma **máquina de estados de cenas**. `main.py` cria o `Game` (`game.py`), que
mantém um registro de cenas e troca a cena atual quando `scene.next_scene` é definido.
O fluxo de cenas é:

```
menu → profile_select → intro_cutscene → tutorial
     → phase1 → transition_1_2 → phase2 → transition_2_3
     → phase3 → transition_3_4 → phase4 → epilogue   (ou → game_over)
```

Cada **fase** monta um `TileMap` (via `map/layouts.py`), instancia o `Player` e NPCs,
e usa os **sistemas** (`systems/`) de colisão, stealth, FOV, som, fog of war, etc.

## Índice por diretório

### Núcleo (raiz)
- [main.md](main.md) — ponto de entrada do programa
- [game.md](game.md) — loop principal e máquina de estados de cenas
- [settings.md](settings.md) — todas as constantes de tuning do jogo
- [crt.md](crt.md) — efeito visual CRT (scanlines + vinheta)
- [player_legado.md](player_legado.md) — stub legado de compatibilidade

### `data/` — persistência e configuração
- [data/event_flags.md](data/event_flags.md) — estado persistente (dataclass)
- [data/save_manager.md](data/save_manager.md) — salvar/carregar JSON
- [data/keybindings.md](data/keybindings.md) — mapeamento de teclas

### `entities/` — atores do jogo
- [entities/player.md](entities/player.md) — Gregor Samsa (personagem jogável)
- [entities/npc.md](entities/npc.md) — classe base de NPC + máquina de alerta
- [entities/food.md](entities/food.md) — comida/maçã (debuff)
- [entities/projectile.md](entities/projectile.md) — projéteis (maçã arremessada)
- [entities/npcs/manager.md](entities/npcs/manager.md) — Gerente
- [entities/npcs/father.md](entities/npcs/father.md) — Pai
- [entities/npcs/mother.md](entities/npcs/mother.md) — Mãe
- [entities/npcs/grete.md](entities/npcs/grete.md) — Grete (irmã)
- [entities/npcs/janitor.md](entities/npcs/janitor.md) — Faxineiro
- [entities/npcs/tenants.md](entities/npcs/tenants.md) — Inquilinos (grupo)

### `map/` — mapas e zonas
- [map/tilemap.md](map/tilemap.md) — grade de tiles + colisão
- [map/layouts.md](map/layouts.md) — geração das salas de cada fase
- [map/hiding_zones.md](map/hiding_zones.md) — esconderijos
- [map/trash.md](map/trash.md) — zona de lixo (tosse)
- [map/triggers.md](map/triggers.md) — gatilhos e zonas de escuta

### `scene/` — cenas
- [scene/base_scene.md](scene/base_scene.md) — classe abstrata de cena
- [scene/menu.md](scene/menu.md) — menu principal
- [scene/profile_select.md](scene/profile_select.md) — seleção de perfil
- [scene/intro_cutscene.md](scene/intro_cutscene.md) — cutscene de abertura
- [scene/tutorial.md](scene/tutorial.md) — tutorial
- [scene/phase1.md](scene/phase1.md) — Fase 1
- [scene/phase2.md](scene/phase2.md) — Fase 2
- [scene/phase3.md](scene/phase3.md) — Fase 3
- [scene/phase4.md](scene/phase4.md) — Fase 4
- [scene/transition.md](scene/transition.md) — transição entre capítulos
- [scene/epilogue.md](scene/epilogue.md) — epílogo
- [scene/game_over.md](scene/game_over.md) — tela de game over

### `systems/` — sistemas de jogo
- [systems/collision.md](systems/collision.md) — colisão AABB
- [systems/stealth.md](systems/stealth.md) — máquina de estados de alerta
- [systems/fov.md](systems/fov.md) — campo de visão (raycasting)
- [systems/fog_of_war.md](systems/fog_of_war.md) — névoa de guerra
- [systems/sound_propagation.md](systems/sound_propagation.md) — propagação de som
- [systems/violin.md](systems/violin.md) — áudio direcional do violino
- [systems/spatial_hash.md](systems/spatial_hash.md) — estrutura de aceleração espacial
- [systems/camera.md](systems/camera.md) — câmera com scroll suave
- [systems/sprite_generator.md](systems/sprite_generator.md) — geração de sprites por código
- [systems/sprite_loader.md](systems/sprite_loader.md) — carga/animação do sprite sheet
- [systems/tile_renderer.md](systems/tile_renderer.md) — geração de texturas de tiles
- [systems/debug_overlay.md](systems/debug_overlay.md) — overlay de depuração

### `ui/` — interface
- [ui/hud.md](ui/hud.md) — HUD (barras + medidor de alerta)
- [ui/dialogue.md](ui/dialogue.md) — balões de pensamento e legendas
- [ui/minigame_door.md](ui/minigame_door.md) — minigame de destrancar porta

### `tests/`
- [tests/test_qa.md](tests/test_qa.md) — testes de aceitação (GDD §7)

---

*Os arquivos `__init__.py` são marcadores de pacote (vazios ou quase) e não têm documento próprio.*
