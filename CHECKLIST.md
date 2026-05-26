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

- [ ] `map/triggers.py` — zonas trigger no Tiled (object layer)
- [ ] **RF012** Missão do Quadro — timer visual, pathfinding Mãe/Irmã, flag `saved_picture`
- [ ] Animação de desmaio da Mãe
- [ ] **RF008** Zonas de Escuta — trigger de inatividade → legendas + atualiza flags
- [ ] Fase 2 mapa e eventos completos

---

## Sprint 11–12 — Projéteis & Debuffs

- [ ] `entities/projectile.py` — colisão de projéteis (arco em top-down)
- [ ] **RF013** A Maçã Crítica — atingido: troca spritesheet + salva `apple_debuff: true` no JSON
- [ ] Debuff persistente carregado no save (`max_stamina *= 0.5`, `speed *= 0.7`)
- [ ] `entities/npcs/janitor.py` — Faxineira com knockback sem game over (**RF014**)
- [ ] Fase 3 mapa e eventos completos

---

## Sprint 13–15 — IA Complexa & Lixo

- [ ] Hitboxes de lixo: acumula `delta_time` → 1.5s → tosse (**RF011**)
- [ ] Partículas de poeira ao atravessar lixo
- [ ] `entities/npcs/tenants.py` — 3 Inquilinos: patrulha sincronizada, FOV 30% maior, alerta compartilhado
- [ ] **RF007** Fog of War / Miopia — alpha mask sobre o mapa, raio por fase: 100%→60%→40%
- [ ] `systems/fog_of_war.py` — Surface de miopia renderizada abaixo do HUD

---

## Sprint 16–18 — Áudio Posicional & Fase 4

- [ ] **RF015** Violino — panning L/R e volume por distância player→porta (**pygame.mixer** stereo)
- [ ] Áudio ambiente por fase (chuva, silêncio, etc.)
- [ ] Cutscenes e diálogos das Fases 3 e 4
- [ ] Tela de Game Over narrativo (sentença da Grete)
- [ ] Epílogo: imagens estáticas em aquarela + texto
- [ ] Fase 4 mapa e eventos completos

---

## Sprint 19–22 — Polimento & QA

- [ ] Assets de pixel art reais (substituindo retângulos coloridos)
- [ ] Balanceamento: jogo concluível com `apple_debuff` ativo
- [ ] Modo debug: visualização de FOV, hitboxes de som, z_level
- [ ] Opções de acessibilidade: remapeamento de teclas, filtro daltonismo
- [ ] Otimização: dirty rects, spatial hashing para colisões
- [ ] Bateria de testes QA (todos os critérios de aceitação do GDD)

---

## Critérios de Aceitação (GDD §7)

- [ ] Transição chão/teto sem clipping de hitbox
- [ ] Estamina no teto = exatamente 50% do valor base (validar no debug)
- [ ] Comunicação Reversa altera estado do NPC instantaneamente se dentro do raio
- [ ] Som não atravessa paredes com flag `isolante`
- [ ] Fog of War carregada corretamente no Load Save (fase correta)
- [ ] UI/HUD renderizada **acima** da camada de miopia
- [ ] Missão do Quadro: timer visível, `saved_picture: true` no JSON no sucesso
- [ ] Apple debuff persiste através de morte, reinício de fase e reload
- [ ] Lixo: 1.5s → tosse com raio 2x maior que passos
- [ ] FOV dos Inquilinos 30% maior (verificável no modo debug)
- [ ] Faxineira: colisão nunca invoca Game Over
- [ ] Violino: canais L/R alteram dinamicamente por coordenada X/Y
