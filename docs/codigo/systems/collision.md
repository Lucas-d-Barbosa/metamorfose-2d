# `systems/collision.py` — Colisão AABB

## Resumo
Função compartilhada **`resolve_wall_collisions(player, wall_rects)`**: empurra o
jogador para fora de qualquer parede sobreposta, usando **push-out AABB de menor
penetração**. Foi extraída dos quatro métodos `_resolve_collisions()` idênticos que
existiam em cada fase (eliminação de duplicação).

## Como funciona (AABB push-out)
AABB = *Axis-Aligned Bounding Box* (retângulo alinhado aos eixos). Para cada parede que
colide com o `player.hitbox`:
1. Calcula a **penetração em cada lado**:
   - `overlap_left = hitbox.right - wall.left`
   - `overlap_right = wall.right - hitbox.left`
   - `overlap_top`, `overlap_bot` análogos.
2. Pega o **menor** dos quatro (`minimum`).
3. Corrige só esse eixo (`move_x`/`move_y`) e **zera a velocidade** naquele eixo.

A ideia: a menor penetração indica de qual lado o jogador "entrou", então empurra-se
pela rota mais curta de saída.

## Padrão de uso (na cena)
```python
resolve_wall_collisions(self.player, self.tilemap.walls_near(self.player.hitbox))
```
Note o uso de `walls_near` (spatial hash) — testa só paredes próximas.

## Onde se encaixa
- Chamada por todas as fases após o movimento do [`Player`](../entities/player.md).
- Depende dos métodos `move_x/move_y` e do `hitbox`/`velocity` do jogador, e das
  paredes do [`TileMap`](../map/tilemap.md).

## Pontos de apresentação
- "Colisão clássica de jogo 2D: resolve um eixo por vez pela menor penetração."
- "Zerar a velocidade no eixo evita 'grudar' tremendo na parede."
- "Código único reutilizado pelas 4 fases — DRY."
