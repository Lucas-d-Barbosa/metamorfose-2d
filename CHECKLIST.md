# Metamorfose 2D — Checklist de Desenvolvimento

> Marque com `[x]` conforme for concluindo. Ordem sugerida de cima pra baixo.

---

## Sprint 1–2 — Foundation Top-Down

### Estrutura & Setup
- [x] Criar estrutura de pastas (`scene/`, `entities/`, `systems/`, `ui/`, `map/`, `data/`, `assets/`)
- [x] `settings.py` atualizado com constantes do top-down
- [x] `player.py` refatorado para top-down (sem gravidade, z_level chão/teto)
- [x] `game.py` com state machine de cenas
- [x] `scene/base_scene.py` — classe abstrata de fase
- [x] `scene/phase1.py` — esqueleto da Fase 1
- [x] `scene/menu.py` — tela de menu inicial
- [x] `scene/game_over.py` — tela de game over narrativo
- [x] `systems/camera.py` — câmera com scroll suave + CameraGroup
- [x] `map/tilemap.py` — TileMap com layout em código (pytmx quando Tiled estiver pronto)
- [x] `map/layouts.py` — layout da Fase 1: quarto 42×24 tiles com cama, guarda-roupa, mesa
- [x] Colisão AABB com tiles de parede
- [ ] Criar mapa da Fase 1 no Tiled (`.tmx`) — _substituir layouts.py quando pronto_

---

## Sprint 3–4 — Stealth & FOV

- [x] `systems/fov.py` — raycasting 2D DDA (cone de visão bloqueado por paredes)
- [x] `systems/stealth.py` — máquina de estados: PATROL→SUSPICIOUS→ALERT→SEARCH
- [x] `entities/npc.py` — NPC base com waypoints de patrulha, chase e search
- [x] `entities/npcs/manager.py` — Gerente: FOV largo, patrol na porta
- [x] `systems/sound_propagation.py` — NoiseEvent circular com check LOS
- [x] `ui/hud.py` — barras de estamina/fome + medidor de alerta + z-level
- [x] **RF006** Comunicação Reversa — tecla F: balão de texto + onda visual + noise event

---

## Sprint 5–6 — Sobrevivência & Comida

- [x] `ui/hud.py` — barras de estamina e fome + indicador `[ OCULTO ]`
- [x] `entities/food.py` — FoodItem (FRESH/ROTTEN) com bob animation e prompt de interação
- [x] **RF010** — comida fresca: -25% estamina + flash vermelho + balão de repulsa; podre: +20–30% + flash verde
- [x] Decay de estamina com multiplicador de z_level (50% no teto) — `entities/player.py`
- [x] `map/hiding_zones.py` — HidingZone rect-based; 3 zonas na Fase 1 (cama, guarda-roupa, escrivaninha)
- [x] Frestas/esconderijos: player.hidden = True ao entrar → NPCs não detectam, sprite semi-transparente, `[ OCULTO ]` no HUD

---

## Sprint 7–8 — Fase 1 Completa

- [ ] Mapa completo do quarto em Tiled (layers: floor, walls, objects, ceiling) — _adiado para quando Tiled estiver configurado_
- [x] `ui/minigame_door.py` — timing bar com cursor bouncing, zona verde, 3 sucessos necessários, feedback de miss/hit
- [x] NPC Gerente — rotina de patrulha na porta, FOV, estado de alerta ativo
- [x] `entities/npcs/father.py` — NPC Pai: velocidade alta, FOV estreito, knockback ao contato
- [x] `ui/dialogue.py` — balões de pensamento (fade, borda colorida) + legendas de diálogo já implementados
- [x] Cutscene de abertura da Fase 1 — tela preta, typewriter, avança linha a linha com ENTER
- [x] `data/save_manager.py` — save/load JSON com `apple_debuff` permanente (OR lógico na escrita)
- [x] `data/event_flags.py` — `saved_picture`, `apple_debuff`, `door_unlocked_phase1`, stats do player
- [x] Máquina de estados da Fase 1: `cutscene → gameplay → door_minigame → phase_end`
- [x] Diálogos automáticos de intro (fila com timestamps: Mãe, Pai, Grete, Gerente)
- [x] Sequência de fim da Fase 1: Gerente foge, Pai aparece na porta, knockback, save, transição

---

## Sprint 9–10 — Missão do Quadro & Zonas de Escuta

- [x] `map/triggers.py` — `TriggerZone` base + `ListeningZone` (inatividade)
- [x] **RF012** Missão do Quadro — timer visual, Mãe/Grete patrulham, flag `saved_picture`
- [ ] Animação de desmaio da Mãe
- [x] **RF008** Zonas de Escuta — 3 zonas (porta, cozinha, corredor) → legendas automáticas
- [x] Fase 2 mapa e eventos completos (`scene/phase2.py`, `map/layouts.py phase2_room`)
- [x] `entities/npcs/mother.py` e `entities/npcs/grete.py`
- [x] Fase 1 → Fase 2 transição (antes ia para game_over)

---

## Sprint 11–12 — Projéteis & Debuffs

- [x] `entities/projectile.py` — `Projectile` base + `AppleProjectile` (RF013)
- [x] **RF013** A Maçã Crítica — hit: `apply_apple_debuff()` + `apple_debuff: true` no JSON
- [x] Debuff persistente (`max_stamina *= 0.5`, `speed *= 0.7`) — já em `player.py` / `save_manager.py`
- [x] `entities/npcs/janitor.py` — Faxineira com `try_sweep()` knockback sem game over (**RF014**)
- [x] Fase 3 mapa e eventos completos (`scene/phase3.py`, `map/layouts.py phase3_room`)
- [x] Father.try_throw() — arremessa AppleProjectile a cada 4.5s quando em range
- [x] Fase 2 → Fase 3 transição (antes ia para game_over)

---

## Sprint 13–15 — IA Complexa & Lixo

- [x] `map/trash.py` — `TrashZone` (1.5s timer → tosse RF011) + `DustParticle`
- [x] Partículas de poeira ao atravessar lixo (spawn ao mover dentro da zone)
- [x] Tosse: emite `COUGH_NOISE_RADIUS` (2× passos) + flash ocre + pensamento
- [x] `entities/npcs/tenants.py` — `Tenant` (FOV 130°/286px = Manager×1.3) + `TenantGroup` (alerta compartilhado)
- [x] **RF007** Fog of War implementado: phase1-2 = sem fog, phase3 = 60%, phase4 = 40%
- [x] `systems/fog_of_war.py` — gradiente radial, renderizado acima do mundo e abaixo do HUD
- [x] Fog + trash integrados em `scene/phase3.py`

---

## Sprint 16–18 — Áudio Posicional & Fase 4

- [x] **RF015** `systems/violin.py` — panning L/R + volume por distância; Channel.set_volume(L,R); visual HUD guide (seta + barra) para quando não há arquivo de áudio
- [ ] Áudio ambiente por fase — aguardando assets em `assets/audio/`
- [x] Cutscenes e diálogos da Fase 4 completos (Faxineira, clímax, sentença, epílogo)
- [x] Tela de Game Over narrativo reescrita — sentença de Grete + pensamento final de Gregor
- [x] `scene/epilogue.py` — 4 telas sequenciais, texto + avanço automático/manual
- [x] `scene/phase4.py` — Fase 4 completa: Faxineira (RF014), TenantGroup, fog 40%, trash, listening zones, violino, sala trigger → climax → sentença → epilogue
- [x] `map/layouts.py phase4_room()` — quarto-depósito com labirinto denso + passagem da sala (col 41, rows 10-13)
- [x] Fase 3 → Fase 4 → Epílogo: cadeia de transições completa

---

## Sprint 19–22 — Polimento & QA

- [x] Assets de pixel art reais — `systems/sprite_loader.py` carrega `assets/sprites/gregor.png`, colorkey+crop+tint
- [x] Balanceamento: `apple_debuff` corrige double-apply em `save_manager.apply_to_player`
- [x] Modo debug — `systems/debug_overlay.py`: FPS, stats, FOV NPC, raios de som, fog ratios
- [x] Opções de acessibilidade — `data/keybindings.py`: remapeamento via `data/keybindings.json`
- [x] Otimização — `systems/spatial_hash.py` + `tilemap.walls_near()` + `systems/collision.py`; `_resolve_collisions` refatorado em todas as 4 fases
- [x] Bateria de testes QA — `tests/test_qa.py`: 20/20 passando (GDD §7.1–7.8)

---

## Critérios de Aceitação (GDD §7)

- [x] Transição chão/teto sem clipping de hitbox
- [x] Estamina no teto = exatamente 50% do valor base (validar no debug)
- [ ] Comunicação Reversa altera estado do NPC instantaneamente se dentro do raio
- [ ] Som não atravessa paredes com flag `isolante`
- [x] Fog of War carregada corretamente no Load Save (fase correta)
- [ ] UI/HUD renderizada **acima** da camada de miopia
- [x] Missão do Quadro: timer visível, `saved_picture: true` no JSON no sucesso
- [x] Apple debuff persiste através de morte, reinício de fase e reload
- [x] Lixo: 1.5s → tosse com raio 2x maior que passos
- [x] FOV dos Inquilinos 30% maior (verificável no modo debug)
- [x] Faxineira: colisão nunca invoca Game Over
- [x] Violino: canais L/R alteram dinamicamente por coordenada X/Y
