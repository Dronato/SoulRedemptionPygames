import pygame

tela = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
LARGURA, ALTURA = tela.get_size()
FPS = 60
relogio = pygame.time.Clock()

# Configuração dos sprites e frames
IDLE = "idle"
WALK = "walk"
ATTACK = "attack"
INIMIGOIDLE = "enemyidle"

SPRITES = {
    INIMIGOIDLE:{"file": "img/mapa1/inimigo1/inimigo1_andando.png", "frames": 3, "width":445 , "height": 394},
    IDLE: {"file": "img/prota/spritesheet.png", "frames": 6, "width": 320, "height": 320},
    WALK: {"file": "img/prota/walk_sprite.png", "frames": 10, "width": 192, "height": 172},
    ATTACK: {"file": "img/prota/dano_spritesheet.png", "frames": 5, "width": 340, "height": 320},
}

class Jogador(pygame.sprite.Sprite):
    def __init__(self,x,y, colisao_rects, tmx_data):
        super().__init__()
        self.state = IDLE
        self.load_sprites()
        self.frame_index = 0
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect(topleft=(x, y))
        self.mask = pygame.mask.from_surface(self.image)
        self.colisao_rects = colisao_rects
        self.tmx_data = tmx_data

        self.vel_x = 0
        self.vel_y = 0
        self.velocidade = 5
        self.velocidade_dash = 16
        self.dash_ativo = False
        self.dash_duracao = 16  # Reduz a duração do dash para ser mais instantâneo
        self.dash_timer = 0
        self.dash_cooldown_duration = 1500  # 1,5 segundos em milissegundos
        self.ultimo_dash_time = 0
        self.direcao_dash = 1
        self.pode_dash = True

        self.forca_pulo = -15
        self.gravidade = 0.8
        self.no_chao = False
        self.pulos_restantes = 2
        self.pulo_pressionado = False

        # Sistema de vida
        self.vida_maxima = 5
        self.vida_atual = 5
        self.invulneravel = False
        self.ultimo_dano = 0
        self.tempo_invulneravel = 1000

        # Sistema de cura
        self.curas_maximas = 3
        self.curas_restantes = self.curas_maximas
        self.pode_curar = True

        # funções gui e pe
        self.facing_right = True
        self.animation_timer = 0


    # funções de animações
    def load_sprites(self):
        sprite_info = SPRITES[self.state]
        self.sprite_sheet = pygame.image.load(sprite_info["file"]).convert_alpha()
        self.frames = self.load_frames(sprite_info["frames"], sprite_info["width"], sprite_info["height"])

    def load_frames(self, frame_count, width, height):
        frames = []
        for i in range(frame_count):
            x = i * width
            frame = self.sprite_sheet.subsurface(pygame.Rect(x, 0, width, height))
            frame = pygame.transform.scale(frame, (160, 160))
            frames.append(frame)
        return frames

    def receber_dano(self, dano):
        tempo_atual = pygame.time.get_ticks()
        if not self.invulneravel or tempo_atual - self.ultimo_dano > self.tempo_invulneravel:
            self.vida_atual -= dano
            self.vida_atual = max(self.vida_atual, 0)
            self.invulneravel = True
            self.ultimo_dano = tempo_atual

    def recuperar_vida(self):
        if self.curas_restantes > 0 and self.vida_atual < self.vida_maxima:
            cura = 2
            self.vida_atual += cura
            self.vida_atual = min(self.vida_atual, self.vida_maxima)
            self.curas_restantes -= 1
            return True
        return False

    def iniciar_dash(self):
        tempo_atual = pygame.time.get_ticks()
        if self.pode_dash and tempo_atual - self.ultimo_dash_time > self.dash_cooldown_duration:
            self.dash_ativo = True
            self.dash_timer = self.dash_duracao
            self.ultimo_dash_time = tempo_atual
            self.vel_x = self.direcao_dash * self.velocidade_dash
            self.vel_y = 0
            self.pode_dash = False # Impede dashes consecutivos muito rápidos

    def atualizar(self, inimigos):
        teclas = pygame.key.get_pressed()
        new_state = self.state
        

        if not self.dash_ativo:
            self.vel_x = 0
            new_state = IDLE
            
            
            if teclas[pygame.K_LEFT] or teclas[pygame.K_a]:
                self.vel_x = -self.velocidade
                self.direcao_dash = -1
                self.facing_right = False
                new_state = WALK
            if teclas[pygame.K_RIGHT] or teclas[pygame.K_d]:
                self.vel_x = self.velocidade
                self.direcao_dash = 1
                self.facing_right = True
                new_state = WALK

            if teclas[pygame.K_z]:
                new_state = ATTACK

            if teclas[pygame.K_SPACE] or teclas[pygame.K_w]:
                if not self.pulo_pressionado and self.pulos_restantes > 0:
                    self.vel_y = self.forca_pulo
                    self.pulos_restantes -= 1
                    self.pulo_pressionado = True
            
            else:
                self.pulo_pressionado = False
            
            if new_state != self.state:
                self.state = new_state
                self.load_sprites()
                self.frame_index = 0

            self.vel_y += self.gravidade

        if self.dash_ativo:
            self.dash_timer -= 1
            if self.dash_timer <= 0:
                self.dash_ativo = False
                self.pode_dash = True # Permite dash novamente após o término

        # Movimentação e Colisão Horizontal
        self.rect.x += self.vel_x
        colidiu = self.colisao_horizontal()
        if colidiu:
            self.vel_x = 0

        # Movimentação e Colisão Vertical
        self.rect.y += self.vel_y
        self.no_chao = False  # Reseta a flag
        colidiu = self.colisao_vertical()
        if colidiu:
            if self.vel_y > 0:
                self.rect.bottom = colidiu.top
                self.no_chao = True
                self.pulos_restantes = 2  # Resetar pulos ao tocar o chão
            elif self.vel_y < 0:
                self.rect.top = colidiu.bottom
            self.vel_y = 0
        
        self.colisao_espinhos()
            
     

        if self.rect.bottom >= ALTURA - 50:
            self.rect.bottom = ALTURA - 50
            self.vel_y = 0
            self.no_chao = True
            self.pulos_restantes = 2

        # Colisão com inimigos
        inimigos_atingidos = pygame.sprite.spritecollide(self, inimigos, False,collided=pygame.sprite.collide_mask)
        for inimigo in inimigos_atingidos:
            self.receber_dano(1)
        
        
        
    def update_animation(self):
        self.animation_timer += 1
        if self.animation_timer >= 10:
            self.frame_index = (self.frame_index + 1) % len(self.frames)
            self.animation_timer = 0

            self.image = self.frames[self.frame_index]
        if not self.facing_right:
            self.image = pygame.transform.flip(self.frames[self.frame_index], True, False) if not self.facing_right else self.frames[self.frame_index]
            self.mask = pygame.mask.from_surface(self.image)
            
    def draw(self, surface, position):
        surface.blit(self.image, position)

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
        
    def colisao_espinhos(self):
        """Verifica colisão com os espinhos e aplica dano."""
    
        layer = self.tmx_data.get_layer_by_name("Espinho")
        if hasattr(layer, 'objects'):  # Verifica se a camada tem objetos
            for obj in layer:
                espinhos_rect = pygame.Rect(obj.x, obj.y, obj.width, obj.height)
                if self.rect.colliderect(espinhos_rect):
                    self.receber_dano(1)  # Aplica dano