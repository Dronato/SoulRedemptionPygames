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

class Inimigo(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.state = INIMIGOIDLE
        self.frame_index = 0
        self.animation_timer = 0
        self.facing_right = True
        self.velocidade_x = 3
        self.velocidade_y = 0
        self.gravity = 0.5
        self.jump_strength = -10
        self.is_jumping = False
        self.moving = False

        # Carregar sprites
        self.frames = []
        self.load_sprites()

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
            frame = pygame.transform.scale(frame, (150, 150))
            frames.append(frame)
        return frames

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
        self.rect.x += self.velocidade_x
        if self.rect.left < 0 or self.rect.right > LARGURA:
            self.velocidade_x *= -1
            self.facing_right = not self.facing_right  # Faz o inimigo virar corretamente

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
