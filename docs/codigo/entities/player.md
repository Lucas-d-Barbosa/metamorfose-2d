# `entities/player.py` — Gregor Samsa (jogador)

## Resumo
Define a classe **`Player`** (herda `pygame.sprite.Sprite`): o inseto controlável.
Movimento top-down com aceleração/atrito, dois níveis (`floor`/`ceiling`), stamina e
fome, debuff da maçã, emissão de ruído e **animação direcional** via sprite sheet.

## Estado principal
| Atributo | Papel |
|----------|-------|
| `pos`, `velocity`, `direction` | Vetores de posição/velocidade/entrada |
| `z_level` | `"floor"` ou `"ceiling"` (chão/teto) |
| `hidden` | Está escondido (não emite ruído nem é visto) |
| `facing_angle` | Direção em graus (0 = direita) |
| `max/current_stamina`, `max/current_hunger` | Stats |
| `apple_debuff` | Debuff **permanente** da maçã |
| `noise_radius` | Raio de ruído emitido no frame (lido pelo som) |
| `_anim_name`, `_anim_frame`, `_anim_timer` | Estado de animação |

## Fluxo de `update(dt)`
Ordem fixa por frame:
1. `_read_input()` — lê WASD, monta `direction` normalizada.
2. `_move(dt)` — `velocity.lerp(direction * effective_speed, FRICTION*dt)`; integra a
   posição. Usa **lerp** para aceleração/desaceleração suaves.
3. `_update_stats(dt)` — decai stamina (metade no teto) e fome; define `noise_radius`
   (= `FOOTSTEP_NOISE_RADIUS` se andando e não escondido).
4. `_update_facing()` — atualiza `facing_angle` e **escolhe a animação** (idle /
   walk_left/right / stealth_left/right). Stealth quando `hidden` ou `apple_debuff`.
5. `_advance_animation(dt)` — avança o frame conforme o FPS da animação.
6. `_build_sprite()` — busca o frame em [`sprite_loader`](../systems/sprite_loader.md);
   rotaciona **só** o idle (top-down) e atualiza `self.image`/`self.rect`.

## Mecânicas-chave
- **`apply_apple_debuff()`** — idempotente (sai cedo se já aplicado): seta a flag e
  multiplica `max_stamina` por `APPLE_STAMINA_PENALTY` (0.5). A reversão nunca ocorre.
- **`effective_speed`** (property) — `BASE_SPEED`, reduzido a 70% se debuffado.
- **`go_to_ceiling()` / `go_to_floor()`** — trocam `z_level`. No teto a stamina cai
  pela metade (`CEILING_STAMINA_MODIFIER`).
- **`receive_knockback(dir, force)`** — empurrão (usado pelo faxineiro/projétil).
- **`move_x/move_y`** — usados pela [colisão](../systems/collision.md) para empurrar
  o jogador eixo a eixo após o movimento.
- **`draw_hud(surface)`** — desenha barras de stamina/fome e indicador CHÃO/TETO.

## Tamanho de sprite consistente
A animação podia "mudar de tamanho" entre idle e walk; isso foi corrigido no
[`sprite_loader`](../systems/sprite_loader.md) normalizando todas as frames num canvas
quadrado fixo. Aqui, o `_build_sprite` apenas rotaciona o idle e centra o `rect`.

## Onde se encaixa
- Instanciado por cada fase ([`phase1`](../scene/phase1.md) …).
- Lido por [`stealth`](../systems/stealth.md)/[`fov`](../systems/fov.md) (visão),
  [`sound_propagation`](../systems/sound_propagation.md) (`noise_radius`),
  [`save_manager`](../data/save_manager.md) (stats/debuff).

## Pontos de apresentação
- "Movimento com lerp dá inércia — não é teletransporte, há aceleração."
- "O debuff da maçã é permanente e muda velocidade, stamina e *animação* (vira stealth)."
- "Stamina cai pela metade no teto — incentiva escolher quando subir."
