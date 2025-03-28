import pygame

# Definição da tela e FPS
tela = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
LARGURA, ALTURA = tela.get_size()
FPS = 60
relogio = pygame.time.Clock()

# Estados de animação
IDLE = "idle"
WALK = "walk"
ATTACK = "attack"
INIMIGOIDLE = "enemyidle"

# Configuração dos sprites e frames
SPRITES = {
    INIMIGOIDLE: {"file": "img/mapa1/inimigo1/inimigo1_andando.png", "frames": 3, "width": 445, "height": 394},
    IDLE: {"file": "img/prota/spritesheet.png", "frames": 6, "width": 320, "height": 320},
    WALK: {"file": "img/prota/walk_sprite.png", "frames": 10, "width": 192, "height": 172},
    ATTACK: {"file": "img/prota/dano_spritesheet.png", "frames": 5, "width": 340, "height": 320},
}

class Inimigo1mp1(pygame.sprite.Sprite):
    def __init__(self, x, y, colisao_rects, tmx_data,largura_mapa, altura_mapa):
        super().__init__()
        self.state = INIMIGOIDLE
        self.frame_index = 0
        self.animation_timer = 0
        self.facing_right = True
        self.velocidade_x = 2
        self.velocidade_y = 0
        self.gravity = 0.5
        self.jump_strength = -10
        self.is_jumping = False
        self.moving = False

        self.colisao_rects = colisao_rects
        self.tmx_data = tmx_data
        self.largura_mapa = largura_mapa
        self.altura_mapa = altura_mapa

        # Carregar sprites
        self.frames = []
        self.load_sprites()

        # Definir limites da patrulha (sentinela)
        self.x_inicial = x  # Ponto de partida do inimigo
        self.x_final = x + 300  # Distância máxima para a direita
        self.patrulhando = True  # Estado de patrulha

        # Garantir que há pelo menos um frame válido
        if not self.frames:
            self.frames = [pygame.Surface((30, 30))]
            self.frames[0].fill((255, 0, 0))

        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect(topleft=(x, y))

    def load_sprites(self):
        """Carrega os sprites e os divide em frames."""
        if self.state not in SPRITES:
            print(f"Erro: Estado {self.state} não encontrado em SPRITES")
            return

        try:
            sprite_info = SPRITES[self.state]
            self.sprite_sheet = pygame.image.load(sprite_info["file"]).convert_alpha()
            self.frames = self.load_frames(sprite_info["frames"], sprite_info["width"], sprite_info["height"])
        except pygame.error:
            print(f"Erro ao carregar sprite {sprite_info['file']}")

    def load_frames(self, frame_count, width, height):
        """Divide a sprite sheet em frames individuais."""
        frames = []
        for i in range(frame_count):
            x = i * width
            frame = self.sprite_sheet.subsurface(pygame.Rect(x, 0, width, height))
            frame = pygame.transform.scale(frame, (80, 80))
            frames.append(frame)
        return frames
    
    def colisao_horizontal(self):
        """Verifica colisão horizontal com os retângulos do mapa."""
        for rect in self.colisao_rects:
            if self.rect.colliderect(rect):
                return rect
        return None

    def colisao_vertical(self):
        """Verifica colisão vertical com os retângulos do mapa."""
        for rect in self.colisao_rects:
            if self.rect.colliderect(rect):
                return rect
        return None

    def update_animation(self):
        """Atualiza a animação do inimigo."""
        if not self.frames:
            return  # Evita erro se não houver frames

        self.animation_timer += 1
        if self.animation_timer >= 10:  # Tempo entre cada frame
            self.frame_index = (self.frame_index + 1) % len(self.frames)
            self.animation_timer = 0

        # Atualiza o sprite conforme a direção
        self.image = pygame.transform.flip(self.frames[self.frame_index], True, False) 
        
        if not self.facing_right:
            self.image = self.frames[self.frame_index]

    def update(self):
        """Atualiza a posição e a animação do inimigo."""
        if self.patrulhando:
        # Movimento de patrulha entre os pontos x_inicial e x_final
            if self.facing_right:
                self.rect.x += self.velocidade_x
                if self.rect.right >= self.x_final:  # Se chegar ao limite direito
                    self.rect.right = self.x_final  # Garantir que ele não ultrapasse o limite
                    self.facing_right = False  # Mudar a direção para a esquerda
            else:
                self.rect.x -= self.velocidade_x
                if self.rect.left <= self.x_inicial:  # Se chegar ao limite esquerdo
                    self.rect.left = self.x_inicial  # Garantir que ele não ultrapasse o limite
                    self.facing_right = True  # Mudar a direção para a direita
        else:
        # Caso não esteja patrulhando, ele apenas se move com a velocidade definida
           self.rect.x += self.velocidade_x

    # Aplicar gravidade
        self.velocidade_y += self.gravity
        self.rect.y += self.velocidade_y

    # Verificar colisões horizontais
        colidiu = self.colisao_horizontal()
        if colidiu:
            self.velocidade_x = self.velocidade_x

    # Movimentação e Colisão Vertical
        self.rect.y += self.velocidade_y
        self.no_chao = False  # Reseta a flag
        colidiu = self.colisao_vertical()
        if colidiu:
            if self.velocidade_y > 0:
                self.rect.bottom = colidiu.top
                self.no_chao = True
                self.pulos_restantes = 2  # Resetar pulos ao tocar o chão
            elif self.velocidade_y < 0:
                self.rect.top = colidiu.bottom
            self.velocidade_y = self.velocidade_x

        # Aplicar gravidade
        self.velocidade_y += self.gravity
        self.rect.y += self.velocidade_y

        # Verificar se o inimigo atinge o "chão"
        if self.rect.bottom >= ALTURA - 50:
            self.rect.bottom = ALTURA - 50
            self.velocidade_y = 0
            self.is_jumping = False

        # **Chamando a atualização da animação!**
        self.update_animation()

    def draw(self, surface):
        """Desenha o inimigo na tela."""
        surface.blit(self.image, self.rect.topleft)
