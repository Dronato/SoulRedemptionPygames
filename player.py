import pygame

tela = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
LARGURA, ALTURA = tela.get_size()
FPS = 60
relogio = pygame.time.Clock()

# Configuração dos sprites e frames
IDLE = "idle"
WALK = "walk"
ATTACK = "attack"
PULO = 'pulo'
DASH = 'dash'
ATTACK1 = 'attack1'
ATTACK2 = 'attack2'
ATTACK3 = 'attack3'
INIMIGOIDLE = "enemyidle"
SPRITES = {
    INIMIGOIDLE:{"file": "img/mapa1/inimigo1/inimigo1_andando.png", "frames": 3, "width":445 , "height": 394},
    IDLE: {"file": "img/prota/parada.png", "frames": 6, "width": 176, "height": 148},
    WALK: {"file": "img/prota/andando.png", "frames": 10, "width": 198, "height": 144},
    ATTACK: {"file": "img/prota/dano_spritesheet.png", "frames": 5, "width": 340, "height": 320},
    PULO: {"file": "img/prota/pulo.png", "frames": 15, "width": 256, "height": 256},
    DASH: {"file": "img/prota/dash.png", "frames": 5, "width": 214, "height": 144},
    ATTACK1: {"file": "img/prota/attack1.png", "frames": 6, "width": 339, "height": 402},
    ATTACK2: {"file": "img/prota/attack2.png", "frames": 7, "width": 339, "height": 402},
    ATTACK3: {"file": "img/prota/attack3.png", "frames": 8, "width": 339, "height": 402},    
}

class Jogador(pygame.sprite.Sprite):
    def __init__(self, x, y, colisao_rects, tmx_data,zoom_level = 2.0):
        super().__init__()
        self.state = IDLE
        self.load_sprites()
        self.frame_index = 0
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect(topleft=(x, y))
        self.mask = pygame.mask.from_surface(self.image)
        self.colisao_rects = colisao_rects
        self.tmx_data = tmx_data
        self.zoom_level = zoom_level
        # Timer para dano dos espinhos
        self.ultimo_dano_espinhos = 0
        self.intervalo_dano_espinhos = 1000  # 1 segundo em milissegundos

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
        # attack
        self.attack_sequence = []
        self.last_attack_time = 0
        self.MAX_ATTACK_INTERVAL = 700
        self.ataque_pressionado = False


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
            frame = pygame.transform.scale(frame, (50, 50))
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
        self.state = DASH
        self.load_sprites()
        if self.pode_dash and tempo_atual - self.ultimo_dash_time > self.dash_cooldown_duration:
            self.dash_ativo = True
            self.dash_timer = self.dash_duracao
            self.ultimo_dash_time = tempo_atual
            self.vel_x = self.direcao_dash * self.velocidade_dash
            self.vel_y = 0
            self.pode_dash = False # Impede dashes consecutivos muito rápidos

    # FUNÇÃO DE ATACAR DO PEDRO E GUI
    def atacar(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_attack_time > self.MAX_ATTACK_INTERVAL:
            self.attack_sequence.clear()
        
        if len(self.attack_sequence) < 3:
            self.attack_sequence.append(f"attack{len(self.attack_sequence) + 1}")
            self.last_attack_time = current_time
            self.state = self.attack_sequence[-1]
            
            self.frame_index = 0
        self.load_sprites()
        print(self.state)
    # FIM DEF ATACAR

    def atualizar(self, inimigos):
        teclas = pygame.key.get_pressed()
        new_state = self.state
        

        if not self.dash_ativo:
            self.vel_x = 0
            new_state = IDLE
            
            # ATTACK PEDRO E GUI

            if self.state == ATTACK1:
                    if self.frame_index < len(self.frames) - 1:
                        return 
                    else:
                        new_state = IDLE
            else: 
                new_state = IDLE
            if self.state == ATTACK2:
                    if self.frame_index < len(self.frames) - 1:
                        return 
                    else:
                        new_state = IDLE
            else: 
                new_state = IDLE
            if self.state == ATTACK3:
                    if self.frame_index < len(self.frames) - 1:
                        return 
                    else:
                        new_state = IDLE
            else: 
                new_state = IDLE
            # FIM DO ATTACK

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
        colidiu_horizontal = self.colisao_horizontal()
        if colidiu_horizontal:
            if self.vel_x > 0:  # Movendo para a direita
                self.rect.right = colidiu_horizontal.left
            elif self.vel_x < 0:  # Movendo para a esquerda
                self.rect.left = colidiu_horizontal.right
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
            # Cria um novo retângulo com as dimensões escaladas
            rect_escalado = pygame.Rect(rect.x * self.zoom_level, rect.y * self.zoom_level,
                                        rect.width * self.zoom_level, rect.height * self.zoom_level)
            
            # Cria um novo retângulo para o jogador com as dimensões escaladas
            jogador_rect_escalado = pygame.Rect(self.rect.x * self.zoom_level, self.rect.y * self.zoom_level,
                                                self.rect.width * self.zoom_level, self.rect.height * self.zoom_level)
            
            if jogador_rect_escalado.colliderect(rect_escalado):
                return rect
        return None

    def colisao_vertical(self):
        """Verifica colisão vertical com os retângulos do mapa."""
        for rect in self.colisao_rects:
            # Cria um novo retângulo com as dimensões escaladas
            rect_escalado = pygame.Rect(rect.x * self.zoom_level, rect.y * self.zoom_level,
                                        rect.width * self.zoom_level, rect.height * self.zoom_level)
            
            # Cria um novo retângulo para o jogador com as dimensões escaladas
            jogador_rect_escalado = pygame.Rect(self.rect.x * self.zoom_level, self.rect.y * self.zoom_level,
                                                self.rect.width * self.zoom_level, self.rect.height * self.zoom_level)
            
            if jogador_rect_escalado.colliderect(rect_escalado):
                return rect
        return None
    def handle_espinho_colisions(self, espinho_maior_layer, espinho_menor_layer):
        tempo_atual = pygame.time.get_ticks()

        # Crie um retângulo escalado para o jogador
        jogador_rect_escalado = pygame.Rect(self.rect.x * self.zoom_level, self.rect.y * self.zoom_level,
                                            self.rect.width * self.zoom_level, self.rect.height * self.zoom_level)

        # Colisão com Espinho_Maior
        if espinho_maior_layer is not None and hasattr(espinho_maior_layer, 'tiles'):
            for x, y, gid in espinho_maior_layer:
                if gid != 0:  # Assume que gid 0 é espaço vazio
                    tile_rect = pygame.Rect(x * self.tmx_data.tilewidth * self.zoom_level, y * self.tmx_data.tileheight * self.zoom_level,
                                            self.tmx_data.tilewidth * self.zoom_level, self.tmx_data.tileheight * self.zoom_level)
                    if jogador_rect_escalado.colliderect(tile_rect):
                        if tempo_atual - self.ultimo_dano_espinhos > self.intervalo_dano_espinhos:
                            self.receber_dano(1)
                            self.ultimo_dano_espinhos = tempo_atual
                            print('danoMaior')

        # Colisão com Espinho_Menor
        if espinho_menor_layer is not None and hasattr(espinho_menor_layer, 'tiles'):
            for x, y, gid in espinho_menor_layer:
                if gid != 0:  # Assume que gid 0 é espaço vazio
                    tile_rect = pygame.Rect(x * self.tmx_data.tilewidth * self.zoom_level, y * self.tmx_data.tileheight * self.zoom_level,
                                            self.tmx_data.tilewidth * self.zoom_level, self.tmx_data.tileheight * self.zoom_level)
                    if jogador_rect_escalado.colliderect(tile_rect):
                        if tempo_atual - self.ultimo_dano_espinhos > self.intervalo_dano_espinhos:
                            self.receber_dano(1)
                            self.ultimo_dano_espinhos = tempo_atual
                            print('danoMenor')