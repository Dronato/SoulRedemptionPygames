import pygame
import math
import random




# Definição da tela e FPS
tela = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
LARGURA, ALTURA = tela.get_size()
FPS = 60
relogio = pygame.time.Clock()

# Estados de animação
IDLE = "idle"
WALK = "walk"
ATTACK = "attack"

MAPA1 = "inimigos do mapa 1"
INIMIGO1MP1 = "inimigo 1 do mapa 1"
INIMIGO1MP1IDLE = "enemyidle"
INIMIGO1MP1ATTACK = "ataque do inimigo 1"
INIMIGO1MP1DANO = "inimigo 1 do mapa 1 sofrendo dano"
INIMIGO1MP1MORTO = "inimigo 1 do mapa 1 morto"


MAPA2 = "inimigos do mapa 2"
INIMIGO1MP2 = "inimigo 1 do mapa 2"
INIMIGO1MP2IDLE = "enemyidle"
INIMIGO1MP2ATTACK = "ataque do inimigo 1 do mapa 2"
INIMIGO1MP2DANO = "inimigo 1 do mapa 2 sofrendo dano"
INIMIGO1MP2MORTO = "inimigo 1 do mapa 2 morto"
INIMIGO1MP2CARREGANDO = "inimigo1 do mapa 2 carregando o ataque"
INIMIGO1MP2TIRO = "tiro do inimigo 1 do mapa 2"

# Dragão
# Obs: inimigo 3 - temporariamente
INIMIGO3MP2 = "inimigo 3 do mapa 2"
INIMIGO3MP2IDLE = "enemyidle"
INIMIGO3MP2ATTACK = "ataque do inimigo 3 do mapa 2"
INIMIGO3MP2DANO = "inimigo 3 do mapa 2 sofrendo dano"
INIMIGO3MP2MORTO = "inimigo 3 do mapa 2 morto"

# Geleia/Slime
INIMIGO2MP2 = "inimigo 2 do mapa 2"
INIMIGO2MP2IDLE = "enemyidle"
INIMIGO2MP2ATTACK = "ataque do inimigo 2 do mapa 2"
INIMIGO2MP2DANO = "inimigo 2 do mapa 2 sofrendo dano"
INIMIGO2MP2MORTO = "inimigo 2 do mapa 2 morto"
INIMIGO2MP2CARREGANDO = "inimigo 2 do mapa 2 carregando o ataque"
INIMIGO2MP2PROJETIL = "projetil lançado pelo inimigo 2 do mapa 2"

# Estados do Boss
BOSS_IDLE = "boss_idle"
BOSS_WALK = "boss_walk" # Se ele se mover
BOSS_CHARGE_FALLING = "boss_charge_falling"
BOSS_ATTACK_FALLING = "boss_attack_falling"
BOSS_CHARGE_PROJECTILE = "boss_charge_projectile"
BOSS_ATTACK_PROJECTILE = "boss_attack_projectile"
BOSS_CHARGE_MELEE = "boss_charge_melee"
BOSS_ATTACK_MELEE = "boss_attack_melee"
BOSS_HIT = "boss_hit"
BOSS_DEATH = "boss_death"
BOSS_CHARGE_DASH = "boss_charge_dash"  # Estado para carregar o dash
BOSS_ATTACK_DASH = "boss_attack_dash"

# Configuração dos sprites e frames
SPRITES = {

    "BOSS_FINAL": {
        # ... (entradas existentes para IDLE, FALLING, PROJECTILE, MELEE, HIT, DEATH) ...
        BOSS_IDLE :{"file": "img/sala_boss/boss_parado.png", "frames": 11, "width": 517, "height": 420}, 
        BOSS_HIT :{"file": "img/sala_boss/boss_hit.png", "frames": 5, "width": 517, "height": 420}, 
        BOSS_CHARGE_FALLING :{"file": "img/sala_boss/boss_meteoro.png", "frames": 21, "width": 517, "height": 420}, 
        BOSS_CHARGE_PROJECTILE :{"file": "img/sala_boss/boss_projetil.png", "frames": 19, "width": 517, "height": 420}, 
        BOSS_CHARGE_MELEE :{"file": "img/sala_boss/boss_melle.png", "frames": 11, "width": 300, "height": 420}, 
        BOSS_ATTACK_FALLING :{"file": "img/sala_boss/boss_parado.png", "frames": 11, "width": 517, "height": 420}, 
        BOSS_ATTACK_PROJECTILE :{"file": "img/sala_boss/boss_parado.png", "frames": 11, "width": 517, "height": 420}, 
        BOSS_ATTACK_MELEE :{"file": "img/sala_boss/boss_melle.png", "frames": 11, "width": 300, "height": 420}, 
        BOSS_CHARGE_DASH :{"file": "img/sala_boss/boss_dash1.png", "frames": 6, "width": 517, "height": 420},
        BOSS_ATTACK_DASH :{"file": "img/sala_boss/boss_dash2.png", "frames": 16, "width": 517, "height": 420},
        BOSS_DEATH :{"file": "img/sala_boss/boss_morto.png", "frames": 24, "width": 517, "height": 420},
        # BOSS_CHARGE_DASH :{"file": "img/sala_boss/boss_melle.png", "frames": 11, "width": 300, "height": 420},
        # BOSS_ATTACK_DASH :{"file": "img/sala_boss/boss_melle.png", "frames": 11, "width": 300, "height": 420},
        BOSS_DEATH :{"file": "img/sala_boss/boss_morto.png", "frames": 24, "width": 517, "height": 724},
        # <<< ADICIONADO >>>
        # Use seus arquivos ou mantenha placeholder.
        # CHARGE pode ser um brilho ou pose diferente.
        # BOSS_CHARGE_DASH: {"file": "placeholder", "frames": 1, "width": 120, "height": 180},
        # ATTACK pode ser a animação de IDLE/WALK ou uma específica de "voo".
        # BOSS_ATTACK_DASH: {"file": "placeholder", "frames": 1, "width": 120, "height": 180},
    },
    MAPA1:{
        INIMIGO1MP1:{
            INIMIGO1MP1IDLE:{"file": "img/mapa1/inimigo1/inimigo1_andando.png", "frames": 4, "width": 445, "height": 389},
            INIMIGO1MP1ATTACK:{"file": "img/mapa1/inimigo1/inimigo1mp1_ataque.png", "frames": 12, "width": 445, "height": 389},
            INIMIGO1MP1DANO:{"file": "img/mapa1/inimigo1/inimigo1mp1_dano.png", "frames": 10, "width": 445, "height": 389},
            INIMIGO1MP1MORTO:{"file": "img/mapa1/inimigo1/inimigo1mp1_morto.png", "frames": 1, "width": 445, "height": 389}
            ,}
            },
    MAPA2:{
        INIMIGO1MP2:{
            INIMIGO1MP2IDLE:{"file": "img/mapa2/inimigo1/inimigo1mp2_andando.png", "frames": 15, "width": 400, "height": 400},
            INIMIGO1MP2ATTACK:{"file": "img/mapa2/inimigo1/inimigo1mp2_ataque.png", "frames": 1, "width": 400, "height": 400},
            INIMIGO1MP2DANO:{"file": "img/mapa2/inimigo1/inimigo1mp2_dano.png", "frames": 13, "width": 400, "height": 400},
            INIMIGO1MP2MORTO:{"file": "img/mapa2/inimigo1/inimigo1mp2_morto.png", "frames": 21, "width": 400.380952, "height": 400},
            INIMIGO1MP2CARREGANDO:{"file": "img/mapa2/inimigo1/inimigo1mp2_carregandolaser.png", "frames": 12, "width": 400, "height": 400},
            INIMIGO1MP2TIRO:{"file": "img/mapa1/inimigo1/inimigo1mp2_tiro.png", "frames": 11, "width": 400, "height": 400}
            },
        INIMIGO2MP2:{
            INIMIGO2MP2IDLE:{"file": "img/mapa2/inimigo2/inimigo2mp2_andando.png", "frames": 6, "width": 129, "height": 91}, 
            INIMIGO2MP2ATTACK:{"file": "img/mapa2/inimigo2/inimigo2mp2_ataque.png", "frames": 15, "width": 193, "height": 161},
            INIMIGO2MP2DANO:{"file": "img/mapa2/inimigo2/inimigo2mp2_dano.png", "frames": 5, "width": 482, "height": 99},
            INIMIGO2MP2MORTO:{"file": "img/mapa2/inimigo2/inimigo2mp2_morto.png", "frames": 11, "width": 482, "height": 183},
            INIMIGO2MP2PROJETIL:{"file": "img/mapa2/inimigo2/inimigo2mp2_projetil.png", "frames": 1, "width": 134, "height": 136},
        },
        INIMIGO3MP2:{
            INIMIGO3MP2IDLE:{"file": "img/mapa2/inimigo3/inimigo3mp2_andando.png", "frames": 10, "width": 344, "height": 628},
            INIMIGO3MP2ATTACK:{"file": "img/mapa2/inimigo3/inimigo3mp2_atacando.png", "frames": 25, "width": 854, "height": 792},
            INIMIGO3MP2DANO:{"file": "img/mapa2/inimigo3/inimigo3mp2_dano.png", "frames": 5, "width": 427, "height": 473},
            INIMIGO3MP2MORTO:{"file": "img/mapa2/inimigo3/inimigo3mp2_morto.png", "frames": 13, "width": 427, "height": 473}
        }
            },

}

class Inimigo1mp1(pygame.sprite.Sprite):
    def __init__(self, x, y,jogador, colisao_rects, tmx_data,largura_mapa, altura_mapa):
        super().__init__()
        self.state = INIMIGO1MP1IDLE
        self.frame_index = 0 
        self.animation_timer = 0
        self.attack_animation_timer = 0  # Novo timer para animação de ataque
        self.facing_right = True
        self.velocidade_x = 2
        self.velocidade_y = 0
        self.gravity = 0.5
        self.jump_strength = -10
        self.is_jumping = False
        self.moving = False
        self.atacando = False  # Novo estado para verificar ataque
        self.morto = False
        self.dano = 1

        self.tempo_ataque_inicio = 0
        self.cooldown_ataque = 700  # em milissegundos (ex: 1 segundo)
        self.preparando_ataque = False


        self.jogador = jogador
        self.grupo_jogador = pygame.sprite.GroupSingle(self.jogador)
        self.colisao_rects = colisao_rects
        self.tmx_data = tmx_data
        self.largura_mapa = largura_mapa
        self.altura_mapa = altura_mapa

        self.sofrendo_dano = False
        self.dano_recebido = 0
        self.vida = 4 # Vida do inimigo

        # Carregar sprites
        self.frames = []
        self.load_sprites()

        # Definir limites da patrulha (sentinela)
        self.x_inicial = x  # Ponto de partida do inimigo
        self.x_final = x + 200  # Distância máxima para a direita
        self.patrulhando = True  # Estado de patrulha

        # Garantir que há pelo menos um frame válido
        if not self.frames:
            self.frames = [pygame.Surface((30, 30))]
            self.frames[0].fill((255, 0, 0))

        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect(topleft=(x, y))
        self.hitbox = pygame.Rect(self.rect.x + 10, self.rect.y + 10, self.rect.width - 20, self.rect.height - 20)


    def load_sprites(self):
        """Carrega os sprites e os divide em frames."""
        if self.state not in SPRITES[MAPA1][INIMIGO1MP1]:
            print(f"Erro: Estado {self.state} não encontrado em SPRITES")
            return

        try:
            sprite_info = SPRITES[MAPA1][INIMIGO1MP1][self.state]
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
            if self.state == INIMIGO1MP1ATTACK:
                frame = pygame.transform.scale(frame, (80, 80))

        return frames
    
    def receber_dano(self, dano, atacando=False):
        """Método para diminuir a vida do inimigo quando receber dano."""
        if atacando and not self.sofrendo_dano:
            self.state = INIMIGO1MP1DANO
            self.load_sprites()
            self.index_anim = 0
            self.sofrendo_dano = True
            self.tempo_entre_frames = 100  # ou o valor que preferir
            self.ultimo_frame = pygame.time.get_ticks()
            self.dano_recebido = dano

    def morrer(self):
        self.dano = 0
        """Define o estado de morte do inimigo, exibe a imagem parada e remove após 1 segundo."""
        agora = pygame.time.get_ticks()

        if self.state != INIMIGO1MP1MORTO:
            self.state = INIMIGO1MP1MORTO
            self.load_sprites()
            self.frame_index = 0
            self.image = self.frames[self.frame_index]
            self.velocidade_x = 0
            self.velocidade_y = 0
            self.atacando = False
            self.patrulhando = False
            self.morto = True
            self.dano = 0
            self.tempo_morte = agora  # Marca o tempo da morte

        # Espera 1 segundo para remover
        elif agora - self.tempo_morte > 3000:
            self.dano = 0
            self.kill()

    
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
        if self.state == INIMIGO1MP1MORTO:
            return  # Se o inimigo estiver morto, não atualiza nada

        if not self.frames:
            return  # Evita erro se não houver frames
        self.animation_timer += 1
        if self.animation_timer >= 10:
            self.frame_index += 1
            self.animation_timer = 0

            if self.frame_index >= len(self.frames):
                if self.state == INIMIGO1MP1ATTACK:
                    self.atacando = False
                    self.mudar_estado(INIMIGO1MP1IDLE)
                self.frame_index = 0
        # Atualiza o sprite conforme a direção
        if not self.facing_right:
            self.image = self.frames[self.frame_index]
        else:
            self.image = pygame.transform.flip(self.frames[self.frame_index], True, False)

    def mudar_estado(self, novo_estado):
        if self.state != novo_estado:
            self.state = novo_estado
            self.load_sprites()
            self.frame_index = 0
            self.image = pygame.transform.flip(self.frames[self.frame_index], True, False) 
        
            if not self.facing_right:
                self.image = self.frames[self.frame_index]

    def patrulhar(self):
        if self.patrulhando:
            self.atacando = False
            self.mudar_estado(INIMIGO1MP1IDLE)
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

    def atacar(self):
        """Método para iniciar o ataque com animação."""
        distancia = abs(self.rect.centerx - self.jogador.rect.centerx)
        
        if not self.atacando:
            self.atacando = True
            self.patrulhando = False
            self.mudar_estado(INIMIGO1MP1ATTACK)
            self.frame_index = 0
            self.animation_timer = 0

    def perseguir(self):
        self.atacando = False
        self.mudar_estado(INIMIGO1MP1IDLE)
        """Função de perseguição do inimigo."""
        if self.jogador.rect.centerx > self.rect.centerx:
            self.rect.x += self.velocidade_x  # Mover para a direita
            self.facing_right = True
            self.mudar_estado(INIMIGO1MP1IDLE)
        else:
            self.mudar_estado(INIMIGO1MP1IDLE)
            self.rect.x -= self.velocidade_x  # Mover para a esquerda
            self.facing_right = False

    def update(self):

        if self.state == INIMIGO1MP1MORTO:
            self.dano = 0
            self.morrer()
            return  # Sai da função para não atualizar nada
        
        distancia = abs(self.rect.centerx - self.jogador.rect.centerx)
        distanciab = abs(self.x_final - self.x_inicial)

        if distancia >= distanciab:
            self.patrulhando = True
            self.atacando = False
            self.mudar_estado(INIMIGO1MP1IDLE)
            self.patrulhar()
        else:
            if not self.atacando:
                self.patrulhando = False
                self.mudar_estado(INIMIGO1MP1IDLE)
                self.perseguir()

                # Verifica distância para iniciar ataque
                if distancia <= 20:
                    self.atacar()


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



        if self.state != INIMIGO1MP1MORTO:
            inimigos_atingidos = pygame.sprite.spritecollide(self, self.grupo_jogador, False, collided=pygame.sprite.collide_mask)
            for jogador in inimigos_atingidos:
                self.receber_dano(jogador.dano)

        if self.sofrendo_dano:
            agora = pygame.time.get_ticks()
            if agora - self.ultimo_frame > self.tempo_entre_frames:
                self.ultimo_frame = agora
                if self.index_anim < len(self.frames):
                    self.image = self.frames[self.index_anim]
                    self.index_anim += 1
                else:
                    self.sofrendo_dano = False
                    self.vida -= self.dano_recebido
                    if self.vida <= 0:
                        self.morto = True
                        self.morrer()
                        
        self.hitbox.x = self.rect.x + 10
        self.hitbox.y = self.rect.y + 10
        # **Chamando a atualização da animação!**
        self.update_animation()

    def draw(self, surface):
        """Desenha o inimigo na tela."""
        surface.blit(self.image, self.rect.topleft)
        pygame.draw.rect(surface, (255, 0, 0), self.hitbox, 2)  # vermelho, só o contorno


class Inimigo2mp1(pygame.sprite.Sprite):
    def __init__(self, x, y,jogador, colisao_rects, tmx_data,largura_mapa, altura_mapa):
        super().__init__()
        self.state = INIMIGO1MP1IDLE
        self.frame_index = 0 
        self.animation_timer = 0
        self.attack_animation_timer = 0  # Novo timer para animação de ataque
        self.facing_right = True
        self.velocidade_x = 2
        self.velocidade_y = 0
        self.gravity = 0.5
        self.jump_strength = -10
        self.is_jumping = False
        self.moving = False
        self.atacando = False  # Novo estado para verificar ataque
        self.dano = 1



        self.jogador = jogador
        self.grupo_jogador = pygame.sprite.GroupSingle(self.jogador)
        self.colisao_rects = colisao_rects
        self.tmx_data = tmx_data
        self.largura_mapa = largura_mapa
        self.altura_mapa = altura_mapa


        self.vida = 10  # Vida do inimigo

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
        if self.state not in SPRITES[MAPA1][INIMIGO1MP1]:
            print(f"Erro: Estado {self.state} não encontrado em SPRITES")
            return

        try:
            sprite_info = SPRITES[MAPA1][INIMIGO1MP1][self.state]
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
    
    def receber_dano(self, dano, atacando=False):
        """Método para diminuir a vida do inimigo quando receber dano."""
        if atacando:  # Verifica se o jogador está atacando
            self.state = INIMIGO1MP1DANO
            self.load_sprites()
            self.vida -= dano
            if self.vida <= 0:
                self.morrer()

    def morrer(self):
        """Define o estado de morte do inimigo e mantém a imagem parada."""
        self.state = INIMIGO1MP1MORTO
        self.load_sprites()
        self.frame_index = 0  # Garante que apenas o primeiro frame da morte seja mostrado
        self.image = self.frames[self.frame_index]  # Define a imagem para a de morte
        self.velocidade_x = 0  # Impede movimento
        self.velocidade_y = 0
        self.atacando = False
        self.patrulhando = False
        self.dano = 0

    
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
        if self.state == INIMIGO1MP1MORTO:
            return  # Se o inimigo estiver morto, não atualiza nada

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

    def patrulhar(self):
        if self.patrulhando:
            self.state = INIMIGO1MP1IDLE
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

    def atacar(self):
        distancia = abs(self.rect.centerx - self.jogador.rect.centerx)
        """Método para iniciar o ataque."""
        if distancia <= 20:
            self.patrulhando = False
            self.atacando = True
            self.state = INIMIGO1MP1ATTACK
            self.load_sprites()
            self.atacando = True
        if distancia >= 100:
            self.atacando = False
            self.patrulhar()

    def perseguir(self):
   
        """Função de perseguição do inimigo."""
        if self.jogador.rect.centerx > self.rect.centerx:
            self.rect.x += self.velocidade_x  # Mover para a direita
            self.facing_right = True
            self.state = INIMIGO1MP1IDLE
        else:
            self.state = INIMIGO1MP1IDLE
            self.rect.x -= self.velocidade_x  # Mover para a esquerda
            self.facing_right = False

    def update(self):

        if self.state == INIMIGO1MP1MORTO:
            return  # Sai da função para não atualizar nada
        
        distancia = abs(self.rect.centerx - self.jogador.rect.centerx)
        distanciab = abs(self.x_final - self.x_inicial)

        if distancia <= 20 or self.rect.colliderect(self.jogador.rect):
            self.atacar()
        elif distancia <= distanciab:
            self.perseguir()
            self.patrulhando = False
        else:
            self.patrulhar()
            self.patrulhando = True

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



        inimigos_atingidos = pygame.sprite.spritecollide(self, self.grupo_jogador, False, collided=pygame.sprite.collide_mask)
        for jogador in inimigos_atingidos:
            self.receber_dano(jogador.dano)

        # **Chamando a atualização da animação!**
        self.update_animation()

    def draw(self, surface):
        """Desenha o inimigo na tela."""
        surface.blit(self.image, self.rect.topleft)



def bresenham_line(x1, y1, x2, y2):
    x1 = int(x1); y1 = int(y1); x2 = int(x2); y2 = int(y2)
    dx = abs(x2 - x1)
    dy = abs(y2 - y1)
    sx = 1 if x1 < x2 else -1
    sy = 1 if y1 < y2 else -1
    err = dx - dy
    while True:
        yield (x1, y1)
        if x1 == x2 and y1 == y2:
            break
        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            x1 += sx
        if e2 < dx:
            err += dx
            y1 += sy

class Inimigo1mp2(pygame.sprite.Sprite):
    def __init__(self, x, y,jogador, colisao_rects, tmx_data,largura_mapa, altura_mapa):
        super().__init__()
        self.state = INIMIGO1MP2IDLE
        self.frame_index = 0 
        self.animation_timer = 0
        self.attack_animation_timer = 0  # Novo timer para animação de ataque
        self.facing_right = True
        self.velocidade_x = 1
        self.velocidade_y = 0
        self.gravity = 0.5
        self.jump_strength = -10
        self.is_jumping = False
        self.moving = False
        self.atacando = False  # Novo estado para verificar ataque
        self.ja_disparou = False

        self.raio_laser = None
        self.alvo_travado = None  # Posição do jogador quando o ataque começa
        self.esta_atacando = False
        self.indicador_visivel = False
        self.tempo_ataque = 0
        self.tempo_max_ataque = 1000  # 1 segundo
        self.laser_cooldown = 3000  # 3 segundos
        self.ultimo_ataque = 0
        self.tempo_nova_detecao = 100  # 0.5s após ataque
        self.ultimo_ataque = 0
        self.dano = 2


        self.laser_visivel = False
        self.morto = False
        
        self.esta_atacando = False
        self.laser_completo = False
        self.tempo_inicio_laser = None
        self.tempo_laser_completo = None
        self.indicador_visivel = True  # Indicador de alvo
        self.alvo_travado = None  # Alvo do laser
        self.particulas = [] 

        

        self.jogador = jogador
        self.grupo_jogador = pygame.sprite.GroupSingle(self.jogador)
        self.colisao_rects = colisao_rects
        self.tmx_data = tmx_data
        self.largura_mapa = largura_mapa
        self.altura_mapa = altura_mapa


        self.vida = 50  # Vida do inimigo

        # Carregar sprites
        self.frames = []
        self.load_sprites()

        # Definir limites da patrulha (sentinela)
        self.x_inicial = x  # Ponto de partida do inimigo
        self.x_final = x + 200  # Distância máxima para a direita
        self.patrulhando = True  # Estado de patrulha
        self.offset_y_ataque = 0  # Correção de altura durante ataque

        # Garantir que há pelo menos um frame válido
        if not self.frames:
            self.frames = [pygame.Surface((30, 30))]
            self.frames[0].fill((255, 0, 0))

        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect(topleft=(x, y))

    def load_sprites(self):
        """Carrega os sprites e os divide em frames."""
        if self.state not in SPRITES[MAPA2][INIMIGO1MP2]:
            print(f"Erro: Estado {self.state} não encontrado em SPRITES")
            self.frames = [pygame.Surface((80, 80))]
            self.frames[0].fill((255, 0, 255))  # cor visível de erro
            return

        try:
            sprite_info = SPRITES[MAPA2][INIMIGO1MP2][self.state]
            self.sprite_sheet = pygame.image.load(sprite_info["file"]).convert_alpha()
            self.frames = self.load_frames(sprite_info["frames"], sprite_info["width"], sprite_info["height"])
        except pygame.error:
            print(f"Erro ao carregar sprite {sprite_info['file']}")
            self.frames = [pygame.Surface((80, 80))]
            self.frames[0].fill((255, 0, 255))  # fallback visível

    def load_frames(self, frame_count, width, height):
        """Divide a sprite sheet em frames individuais."""
        frames = []
        for i in range(frame_count):
            x = i * width
            frame = self.sprite_sheet.subsurface(pygame.Rect(x, 0, width, height))
            frame = pygame.transform.scale(frame, (80, 80))
            frames.append(frame)
        return frames
    
    def receber_dano(self, dano, atacando=False):
        """Método para diminuir a vida do inimigo quando receber dano."""
        if atacando:  # Verifica se o jogador está atacando
            self.state = INIMIGO1MP2DANO
            self.load_sprites()
            self.vida -= dano
            if self.vida <= 0:
                self.morrer()

    def morrer(self):
        agora = pygame.time.get_ticks()

        if self.state != INIMIGO1MP2MORTO:
            self.state = INIMIGO1MP2MORTO
            self.load_sprites()
            self.velocidade_x = 0
            self.velocidade_y = 0
            self.atacando = False
            self.patrulhando = False
            self.dano = 0
            self.morto = True
            self.frame_index = 0
            self.tempo_morte = agora
            self.animation_timer = 0

        # Avança a animação de morte
        if self.animation_timer >= 10:
            self.frame_index += 1
            self.animation_timer = 0

            if self.frame_index >= len(self.frames):
                self.kill()  # remove o inimigo após mostrar todos os frames
            else:
                self.image = self.frames[self.frame_index]
        else:
            self.animation_timer += 1
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
        if not self.frames or self.frame_index >= len(self.frames):
            print(f"[ERRO] Frames vazios ou frame_index inválido para estado: {self.state}")
            self.frame_index = 0
            if self.frames:
                self.image = self.frames[0]
            return        
        if self.state == INIMIGO1MP2MORTO:
            return  # Se o inimigo estiver morto, não atualiza nada

        if not self.frames:
            return  # Evita erro se não houver frames

        self.animation_timer += 1
        if self.animation_timer >= 10:  # Tempo entre cada frame
            self.frame_index = (self.frame_index + 1) % len(self.frames)
            self.animation_timer = 0


        # Atualiza o sprite conforme a direção
        if self.facing_right:
            self.image = pygame.transform.flip(self.frames[self.frame_index], True, False)
        else:
            self.image = self.frames[self.frame_index]

    def criar_laser(self):
        self.alvo_travado = (self.jogador.rect.centerx, self.jogador.rect.centery)
        self.atacando = True
        self.tempo_ataque = self.tempo_max_ataque

    def patrulhar(self):
        self.state = INIMIGO1MP2IDLE
        self.alvo_travado = None
        self.patrulhando = True

        if self.facing_right:
            self.rect.x += self.velocidade_x
            if self.rect.right >= self.x_final:
                self.rect.right = self.x_final
                self.facing_right = False
        else:
            self.rect.x -= self.velocidade_x
            if self.rect.left <= self.x_inicial:
                self.rect.left = self.x_inicial
                self.facing_right = True

    def detectar_jogador(self, surface):
        # Posição da cabeça do inimigo (origem do laser)
        x1 = self.rect.centerx
        y1 = self.rect.centery

        # Posição do centro do jogador
        x2 = self.jogador.rect.centerx
        y2 = self.jogador.rect.centery

        # Verificar se há parede no caminho (linha de visão bloqueada)
        for px, py in bresenham_line(x1, y1, x2, y2):
            for rect in self.colisao_rects:
                if rect.collidepoint(px, py):
                    # Linha de visão bloqueada, não trava alvo
                    self.patrulhando = True
                    self.alvo_travado = None
                    self.patrulhar()
                    return

        # Linha de visão livre! Agora sim trava o alvo e começa o ataque
        self.patrulhando = False
        self.facing_right = self.jogador.rect.centerx > self.rect.centerx
        self.alvo_travado = (x2, y2)
        self.tempo_ataque = pygame.time.get_ticks()
        self.esta_atacando = False
        self.indicador_visivel = True
        self.state = INIMIGO1MP2CARREGANDO  # Começa o ciclo do laser
        self.load_sprites()
        self.carregar_laser(surface)

    def carregar_laser(self, surface):
        agora = pygame.time.get_ticks()

        tempo_passado = agora - self.tempo_ataque

        if tempo_passado < 1000:
            self.state = INIMIGO1MP2IDLE  # 1º estágio
            self.indicador_visivel = False
            self.laser_visivel = False
            self.esta_atacando = False

        elif tempo_passado < 1500:
            self.state = INIMIGO1MP2CARREGANDO  # 2º estágio: aviso
            self.indicador_visivel = True
            self.laser_visivel = True
            self.esta_atacando = False

        elif tempo_passado < 2400:
            if not self.esta_atacando:
                self.atacar()  # Executa só uma vez
            self.laser_visivel = True

        else:
            # Reset do ataque
            self.tempo_ataque = None
            self.alvo_travado = None
            self.indicador_visivel = False
            self.laser_visivel = False
            self.esta_atacando = False
            self.mudar_estado(INIMIGO1MP2IDLE)
    def atacar(self):
        print("Atacando!")  # só pra testar
        self.state = INIMIGO1MP2ATTACK
        self.load_sprites()
        self.frame_index = 0
        self.image = self.frames[self.frame_index]
        self.esta_atacando = True
        self.indicador_visivel = False


    def laser_atingiu_jogador(self):
        return self.rect.colliderect(self.jogador.rect)
    
    def mudar_estado(self, novo_estado):
        if self.state != novo_estado:
            self.state = novo_estado
            self.load_sprites()
            self.frame_index = 0
            self.image = pygame.transform.flip(self.frames[self.frame_index], True, False) 
        
            if not self.facing_right:
                self.image = self.frames[self.frame_index]

    def update(self, surface=None):
        agora = pygame.time.get_ticks()

        if self.state == INIMIGO1MP2MORTO:
            self.dano = 0
            self.morrer()
            return

        distancia = abs(self.rect.centerx - self.jogador.rect.centerx)
        distanciab = abs(self.x_final - self.x_inicial)
        
        if self.tempo_ataque:
            self.carregar_laser(surface)
        elif distancia <= distanciab:
            self.detectar_jogador(surface)
        else:
            self.patrulhar()



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

        if self.esta_atacando and hasattr(self, "laser_rect") and self.mask and self.jogador.mask:
            offset = (
                self.jogador.rect.left - self.laser_rect.left,
                self.jogador.rect.top - self.laser_rect.top
            )
            if self.mask.overlap(self.jogador.mask, offset):
                print("Jogador atingido pelo laser!")
                self.jogador.receber_dano(self.dano)



        if self.state != INIMIGO1MP2MORTO:
            inimigos_atingidos = pygame.sprite.spritecollide(self, self.grupo_jogador, False, collided=pygame.sprite.collide_mask)
            for jogador in inimigos_atingidos:
                self.receber_dano(jogador.dano)

        # **Chamando a atualização da animação!**
        self.update_animation()
        self.mask = pygame.mask.from_surface(self.image)



    
    def draw(self, surface, zoom_level=1.0, deslocamento_camera_x=0, deslocamento_camera_y=0):
        surface.blit(self.image, self.rect.topleft)

        if self.alvo_travado:
            x1 = self.rect.centerx * zoom_level + deslocamento_camera_x
            y1 = self.rect.centery * zoom_level + deslocamento_camera_y
            x2 = self.alvo_travado[0] * zoom_level + deslocamento_camera_x
            y2 = self.alvo_travado[1] * zoom_level + deslocamento_camera_y

            # Indicador visual antes do ataque
            if self.indicador_visivel:
                linha_parou = False
                for px, py in bresenham_line(x1, y1 - 11, x2, y2):
                    px_real = (px - deslocamento_camera_x) / zoom_level
                    py_real = (py - deslocamento_camera_y) / zoom_level
                    if self.jogador.rect.collidepoint(px_real, py_real):
                        x2 = px
                        y2 = py
                        linha_parou = True
                        break
                    for rect in self.colisao_rects:
                        if rect.collidepoint(px_real, py_real):
                            self.mudar_estado(INIMIGO1MP2IDLE)
                            self.alvo_travado = None
                            self.indicador_visivel = False
                            self.esta_atacando = False
                            self.laser_completo = False
                            self.tempo_inicio_laser = None
                            self.patrulhar()
                            x2 = px
                            y2 = py
                            linha_parou = True
                            return
                    if linha_parou:
                        break
                pygame.draw.line(surface, (255, 255, 0), (x1, y1 - 11), (x2, y2), 3)

            if not self.esta_atacando and self.laser_completo:
                self.particulas.clear()

            # Lógica do laser
            if self.esta_atacando:

                if not hasattr(self, "tempo_inicio_laser") or self.tempo_inicio_laser is None:
                    print("Inicializando tempo_inicio_laser...")
                    self.tempo_inicio_laser = pygame.time.get_ticks()  # Inicializa o tempo
                    self.laser_completo = False  # Garantir que o laser esteja em estado inicial
                    print(f"tempo_inicio_laser inicializado: {self.tempo_inicio_laser}")

                tempo_passado = pygame.time.get_ticks() - self.tempo_inicio_laser
                print(f"Tempo passado desde início do laser: {tempo_passado}ms")

                duracao_laser = 400
                delay_apos_laser = 800

                linha_parou = False
                for px, py in bresenham_line(x1, y1 - 11, x2, y2):
                    px_real = (px - deslocamento_camera_x) / zoom_level
                    py_real = (py - deslocamento_camera_y) / zoom_level
                    if self.jogador.rect.collidepoint(px_real, py_real):
                        x2 = px
                        y2 = py
                        linha_parou = True
                        break
                    for rect in self.colisao_rects:
                        if rect.collidepoint(px_real, py_real):
                            x2 = px
                            y2 = py
                            linha_parou = True
                            break
                    if linha_parou:
                        break
                dx = x2 - x1
                dy = y2 - y1

                if not self.laser_completo:
                    progresso = min(1, tempo_passado / duracao_laser)
                    x2_animado = x1 + dx * progresso
                    y2_animado = y1 + dy * progresso

                    sombra_offset = 5
                    for i in range(6):  # Número de camadas
                        alpha = int(20 + (i * 12))  # Começa mais claro, termina mais opaco
                        largura = 12 - i  # Camadas mais internas são mais finas

                        sombra_surface = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
                        cor_sombra = (255, 0, 0, alpha)  # RGBA: vermelho com transparência
                        pygame.draw.line(sombra_surface, cor_sombra, 
                                        (x1 + sombra_offset, y1 - 11 + sombra_offset), 
                                        (x2_animado + sombra_offset, y2_animado + sombra_offset), 
                                        largura)
                        surface.blit(sombra_surface, (0, 0))
                    # Laser vermelho neon com brilho

                    pygame.draw.line(surface, (255, 0, 0, 80), (x1, y1 - 11), (x2_animado, y2_animado), 6)


                    vibração_offset = random.randint(-2, 2)
                    pygame.draw.line(surface, (255, 0, 0, 80), 
                                    (x1 + vibração_offset, y1 - 11 + vibração_offset), 
                                    (x2_animado + vibração_offset, y2_animado + vibração_offset), 4)

                    # Efeito glow (brilho)
                    glow_offset = 3
                    pygame.draw.line(surface, (255, 0, 0, 80), 
                                    (x1 - glow_offset, y1 - 11 - glow_offset), 
                                    (x2_animado - glow_offset, y2_animado - glow_offset), 
                                    6)  # Camada adicional para o brilho

                    # Adicionando círculos nas pontas do laser para deixá-las arredondadas
                    
                    pygame.draw.circle(surface, (255, 0, 0, 80), (x2_animado, y2_animado), 4)  # Círculo na ponta final

                    if progresso >= 1:
                        self.laser_completo = True
                        self.tempo_laser_completo = pygame.time.get_ticks()
                        print("Laser completo! Tempo do laser completo:", self.tempo_laser_completo)

                else:
                    tempo_desde_completo = pygame.time.get_ticks() - self.tempo_laser_completo
                    print(f"Tempo desde que o laser foi completado: {tempo_desde_completo}ms")
                    if tempo_desde_completo <= delay_apos_laser:
                        sombra_offset = 5
                        # Sombra com gradiente de vermelho
                        for i in range(10):
                            intensidade = 255 - int((255 / 10) * i)
                            pygame.draw.line(surface, (intensidade, 0, 0), 
                                            (x1 + sombra_offset, y1 - 11 + sombra_offset), 
                                            (x2 + sombra_offset, y2 + sombra_offset), 
                                            5 - i)

                        # Laser vermelho neon
                        
                        pygame.draw.line(surface, (255, 0, 0, 80), (x1, y1 - 11), (x2-30, y2), 6)
                       

                        laser_rect = pygame.Rect(min(x1, x2), min(y1, y2), abs(x2 - x1), abs(y2 - y1))
                        laser_rect.inflate_ip(3, 3)

                        # Converte o rect do jogador para a tela (com zoom e câmera)
                        player_rect_tela = pygame.Rect(
                            self.jogador.rect.x * zoom_level + deslocamento_camera_x,
                            self.jogador.rect.y * zoom_level + deslocamento_camera_y,
                            self.jogador.rect.width * zoom_level,
                            self.jogador.rect.height * zoom_level
                        )
                        print("laser_rect:", laser_rect)
                        print("player_rect_tela:", player_rect_tela)
                        print("zoom_level:", zoom_level, "deslocamento_camera_x:", deslocamento_camera_x)

                        # Verifica colisão
                        if laser_rect.colliderect(player_rect_tela):
                            print("🔥 Jogador atingido pelo LASER!")
                            self.jogador.receber_dano(self.dano)

                        vibração_offset = random.randint(-2, 2)
                        pygame.draw.line(surface, (255, 0, 0, 80), 
                                        (x1 + vibração_offset, y1 - 11 + vibração_offset), 
                                        (x2 + vibração_offset, y2 + vibração_offset), 4)

                        # Efeito glow (brilho)
                        glow_offset = 3
                        pygame.draw.line(surface, (255, 0, 0, 80), 
                                        (x1 - glow_offset, y1 - 11 - glow_offset), 
                                        (x2 - glow_offset, y2 - glow_offset), 
                                        8)

                        # Adicionando círculos nas pontas do laser para deixá-las arredondadas
                       
                        pygame.draw.circle(surface, (255, 0, 0, 80), (x2, y2), 4)  # Círculo na ponta final

                    else:
                        print("Resetando o ataque de laser...")
                        self.esta_atacando = False
                        if hasattr(self, "tempo_inicio_laser"):
                            del self.tempo_inicio_laser
                        if hasattr(self, "tempo_laser_completo"):
                            del self.tempo_laser_completo
                        if hasattr(self, "laser_completo"):
                            del self.laser_completo
                        self.laser_completo = False  # Garantir reset correto

                    if self.laser_completo:
                        self.particulas.append([x2, y2, random.randint(-5, 5), random.randint(-5, 5)])

                    for part in self.particulas:
                        pygame.draw.circle(surface, (255, 0, 0, 80), (int(part[0]), int(part[1])), 3)
                        part[0] += part[2]
                        part[1] += part[3]

                        if part[0] < 0 or part[1] < 0 or part[0] > surface.get_width() or part[1] > surface.get_height():
                            self.particulas.remove(part)
                            
class BossProjectile(pygame.sprite.Sprite):
    """Projétil disparado pelo Boss."""
    def __init__(self, x, y, target_x, target_y, speed, colisao_rects, dano=1):
        super().__init__()
        self.size = 25 # Tamanho do placeholder (um pouco maior)

        self.caminho_imagem = None
        # --- Se uma imagem for fornecida ---
        if self.caminho_imagem:
            imagem_original = pygame.image.load(self.caminho_imagem).convert_alpha()
            self.image = pygame.transform.scale(imagem_original, (self.size, self.size))
        else:
            # --- Placeholder visual se imagem não for passada ---
            self.image = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
            pygame.draw.circle(self.image, (0, 0, 0), (self.size//2, self.size//2), self.size//2)
            pygame.draw.circle(self.image, (55, 55, 55), (self.size//2, self.size//2), self.size//2, 2)

        self.rect = self.image.get_rect(center=(x, y))
        self.colisao_rects = colisao_rects
        self.dano = dano
        self.speed = speed
        direction_x = target_x - x
        direction_y = target_y - y
        distance = math.hypot(direction_x, direction_y)
        if distance == 0:
            self.vel_x, self.vel_y = 0, -self.speed
        else:
            self.vel_x = (direction_x / distance) * self.speed
            self.vel_y = (direction_y / distance) * self.speed
        self.pos_x, self.pos_y = float(x), float(y)
        print(f"[Projectile CREATED] @ ({x:.0f},{y:.0f})")

    def update(self, jogador):
        self.pos_x += self.vel_x
        self.pos_y += self.vel_y
        self.rect.center = (int(self.pos_x), int(self.pos_y))

        # Colisão com cenário
        for rect_colisao in self.colisao_rects:
            if self.rect.colliderect(rect_colisao):
                self.kill(); return

        # Remoção se sair muito da área de jogo
        tela_rect_margem = pygame.Rect(-LARGURA//2, -ALTURA//2, LARGURA*2, ALTURA*2) # Margem grande
        if not tela_rect_margem.colliderect(self.rect):
            print(f"[Projectile KILL] Off Screen: {self.rect.center}") # DEBUG
            self.kill()


class FallingObject(pygame.sprite.Sprite): # <<< CLASSE REVISADA >>>
    """Objeto que cai do céu."""
    def __init__(self, x, y, speed, colisao_rects, altura_mapa, dano=1):
        super().__init__()
        self.width, self.height = 50, 75 # Tamanho placeholder (BEM MAIOR)

        # --- Placeholder Visual (Amarelo Brilhante) ---
        self.caminho_imagem = "img/sala_boss/estaca.png"
        self.imagem_original = pygame.image.load(self.imagem_path).convert_alpha()
        self.image = pygame.transform.scale(self.imagem_original, (self.width, self.height))

        # --- Fim Placeholder ---
        self.rect = self.image.get_rect(midbottom=(x, y))
        self.colisao_rects = colisao_rects # Retângulos sólidos do mapa
        self.dano = dano
        self.speed = speed
        self.altura_mapa = altura_mapa
        print(f"[FallingObject CREATED] @ ({x:.0f},{y:.0f}) Speed:{speed}")

    def update(self, jogador):
        """Move o objeto para baixo e verifica colisões SOMENTE com o mapa."""
        self.rect.y += self.speed
        # print(f"[FallingObject UPDATE] Pos: {self.rect.midbottom}") # DEBUG

        # Colisão com chão/plataformas (Apenas esta condição mata o objeto)
        for rect_colisao in self.colisao_rects:
            # Verifica colisão E se a base do objeto está tocando ou abaixo do topo da plataforma
            if self.rect.colliderect(rect_colisao) and self.rect.bottom >= rect_colisao.top:
                print(f"[FallingObject KILL] Ground Collision: {self.rect} vs {rect_colisao}") # DEBUG
                self.kill()
                return # Para de verificar colisões e de mover

        # <<< REMOVIDO: Checagem de limite inferior para evitar kill prematuro >>>
        # if self.rect.top > self.altura_mapa + 100:
        #     print(f"[FallingObject KILL] Off Screen Bottom: {self.rect}") # DEBUG
        #     self.kill()


# ===============================================
#      CLASSE PRINCIPAL DO BOSS (REFINADA)
# ===============================================
class FallingProjectile(pygame.sprite.Sprite):
    """Projétil que cai verticalmente do céu, com aparência de projétil."""
    def __init__(self, x, y_start,speed, colisao_rects, altura_mapa, dano=1):
        super().__init__()
        self.dano = dano
        self.speed = speed
        self.colisao_rects = colisao_rects # Retângulos sólidos do mapa (para colisão com chão)
        self.altura_mapa = altura_mapa

        # --- Aparência (similar ao BossProjectile ou customizada) ---
        self.size = 25 # Tamanho do projétil
        self.caminho_imagem = "img/sala_boss/estaca.png"
        self.imagem_original = pygame.image.load(self.caminho_imagem).convert_alpha()
        self.image = pygame.transform.scale(self.imagem_original, (self.size, self.size*4))

        # Posição inicial: x aleatório, y fixo acima da tela
        self.rect = self.image.get_rect(centerx=x, top=y_start) # Começa pelo topo

        #print(f"[FallingProjectile CREATED] @ ({x:.0f},{y_start}) Speed:{speed}") # DEBUG opcional

    def update(self, jogador): # 'jogador' não é usado diretamente aqui
        """Move o projétil para baixo e verifica colisões com o chão/plataformas."""
        self.rect.y += self.speed
        #print(f"[FallingProjectile UPDATE] Pos: {self.rect.center}") # DEBUG opcional

        # Colisão com chão/plataformas (kill())
        for rect_colisao in self.colisao_rects:
            # Verifica colisão e se está tocando/atravessando o topo da plataforma
            if self.rect.colliderect(rect_colisao) and self.rect.bottom >= rect_colisao.top:
                #print(f"[FallingProjectile KILL] Ground Collision: {self.rect} vs {rect_colisao}") # DEBUG opcional
                self.kill()
                return # Para de verificar após colidir

        # Opcional: Remover se sair muito por baixo da tela (segurança)
        if self.rect.top > self.altura_mapa + 200:
            #print(f"[FallingProjectile KILL] Off Screen Bottom: {self.rect}") # DEBUG opcional
            self.kill()


class BossFinal(pygame.sprite.Sprite): # <<< CLASSE REVISADA >>>
    # --- __init__ (Garante que altura_mapa está sendo passada) ---
    def __init__(self, x, y, jogador, colisao_rects, largura_mapa, altura_mapa):
        super().__init__()
        self.jogador = jogador
        self.colisao_rects = colisao_rects
        self.largura_mapa = largura_mapa
        self.altura_mapa = altura_mapa # Essencial para FallingObject
        self.morto = False

        self.vida_maxima = 10; self.vida = self.vida_maxima
        self.facing_right = True; self.no_chao = True; self.is_dead = False
        self.invulnerable_timer = 0; self.invulnerable_duration = 300

        self.state = BOSS_IDLE; self.frames = {}; self.frames_atual = []
        self.frame_index = 0; self.animation_timer = 0; self.animation_speed = 10
        self.image = pygame.Surface((370, 300)) # <-- PROPORÇÃO
        self.image.fill((50, 50, 50))
        self.rect = self.image.get_rect(midbottom=(x, y))
        self.original_x = self.rect.centerx # Guarda o CENTRO X inicial
        self.original_y = self.rect.centery # Guarda o CENTRO Y inicial

        self.load_all_sprites() # Garante placeholders se sprites reais falharem
        self.change_state(BOSS_IDLE)

        self.ai_state = 'IDLE'; self.attack_cooldown = 3000
        self.last_attack_time = pygame.time.get_ticks() - self.attack_cooldown
        self.charge_duration = 1000; self.action_start_time = 0
        self.chosen_attack = None; self.hit_recovery_time = 400; self.last_hit_time = 0
        self.use_falling_next = True

        # <<< ATRIBUTOS PARA FALLING OBJECT AJUSTADOS >>>
        self.falling_object_min_count = 6
        self.falling_object_max_count = 8 # Ajustado para ser inclusivo no randint
        self.falling_object_speed = 6 # Um pouco mais rápido
        self.falling_attack_duration = 800
        self.falling_objects_group = pygame.sprite.Group()

        self.projectile_count = 2; self.projectile_speed = 7
        self.projectile_interval = 300; self.projectiles_fired = 0
        self.projectile_attack_animation_duration = 1000
        self.projectiles_group = pygame.sprite.Group()

        self.melee_range = 150; 
        self.melee_dano = 2; self.is_melee_active = False; self.melee_attack_duration = 600

                # <<< ADICIONADO: Atributos para Fase 2 e Dash >>>
        self.is_phase_2 = False
        self.phase_2_threshold = 0.20 # Ativa com 20% de vida ou menos
        self.is_dashing = False        # Flag: está no meio do dash?
        self.dash_speed = 18           # Pixels por frame (ajuste a gosto)
        self.dash_y = self.original_y  # O Y será fixo durante o dash
        self.dash_direction = 0        # -1 (esquerda), 1 (retorno da direita)
        self.dash_dano = 1             # Dano de contato do dash
        self.can_dash_damage = False 
        self.dash_phase = 0
        
        # EFEITOS
        self.efeito_frames = []
        self.efeito_index = 0
        self.efeito_timer = 0
        self.efeito_speed = 4 # ajuste como quiser
        self.zoom_level = 1.0  # zoom da câmera (ajuste conforme o jogo)
        self.load_efeito()
        
        # PIXEL
        self.mask = pygame.mask.from_surface(self.image)

    # --- _create_placeholder (sem mudanças) ---
    def _create_placeholder(self, color, size=(370, 300)):
        surf = pygame.Surface(size, pygame.SRCALPHA)
        surf.fill(color)
        pygame.draw.rect(surf, (255,255,255), surf.get_rect(), 1)
        return surf

    # --- load_all_sprites (sem mudanças significativas, apenas garante placeholders) ---
    def load_all_sprites(self):
        boss_sprites_def = SPRITES.get("BOSS_FINAL", {})
        colors = {
            BOSS_IDLE: (100, 100, 100), BOSS_WALK: (100, 100, 100),
            BOSS_CHARGE_FALLING: (200, 200, 0), BOSS_ATTACK_FALLING: (255, 255, 0),
            BOSS_CHARGE_PROJECTILE: (0, 0, 200), BOSS_ATTACK_PROJECTILE: (0, 0, 255),
            BOSS_CHARGE_MELEE: (200, 0, 0), BOSS_ATTACK_MELEE: (255, 0, 0),
            BOSS_HIT: (255, 128, 0), BOSS_DEATH: (0, 0, 0),BOSS_CHARGE_DASH:(22,22,22),
            BOSS_ATTACK_DASH:(44,44,44),
        }
        all_boss_states = list(colors.keys())
        for state in all_boss_states:
            info = boss_sprites_def.get(state)
            placeholder_size = (370, 300) # <-- PROPORÇÃO
            loaded_ok = False
            if info:
                 placeholder_size = (info.get("width", 370), info.get("height", 300)) # <-- PROPORÇÃO
                 if info.get("file") != "placeholder" and info.get("frames", 0) > 0:
                     try:
                         # (Código de carregamento de spritesheet omitido para brevidade, igual ao anterior)
                         if isinstance(info["file"], str): sprite_sheet = pygame.image.load(info["file"]).convert_alpha()
                         else: sprite_sheet = info["file"]
                         frames_list = []
                         target_w, target_h = 370, 300 # <-- PROPORÇÃO
                         for i in range(info["frames"]):
                             frame=sprite_sheet.subsurface(pygame.Rect(i*info["width"],0,info["width"],info["height"]))
                             frame = pygame.transform.scale(frame, (target_w, target_h)); frames_list.append(frame)
                         self.frames[state] = frames_list; loaded_ok = True
                     except Exception as e: print(f"[BOSS Load] Falha '{state}': {e}")
            if not loaded_ok: self.frames[state] = [self._create_placeholder(colors.get(state,(255,255,255)), placeholder_size)]

    # --- change_state (sem mudanças) ---
    def change_state(self, new_state):
        if (self.state != new_state or not self.frames_atual) and not self.is_dead:
            if new_state in self.frames and self.frames[new_state]:
                self.state = new_state; self.frames_atual = self.frames[new_state]
                self.frame_index = 0; self.animation_timer = 0
                base_image = self.frames_atual[0]
                self.image = pygame.transform.flip(base_image, True, False) if not self.facing_right else base_image
                
                self.mask = pygame.mask.from_surface(self.image)
                
            else:
                print(f"[BOSS Change] ERRO: '{new_state}' sem frames!")
                if self.state != BOSS_IDLE and BOSS_IDLE in self.frames and self.frames[BOSS_IDLE]: self.change_state(BOSS_IDLE)

    # --- update_animation (sem mudanças) ---
    def update_animation(self):
        if not self.frames_atual: return
        if self.is_dead and self.state == BOSS_DEATH:
             if self.frame_index >= len(self.frames_atual) - 1:
                 self.image = self.frames_atual[-1]
                 if not self.facing_right: self.image = pygame.transform.flip(self.image, True, False)
                 return
        self.animation_timer += 1
        if self.animation_timer >= self.animation_speed:
            self.animation_timer = 0
            self.frame_index = (self.frame_index + 1) % len(self.frames_atual)
            base_image = self.frames_atual[self.frame_index]
            self.image = pygame.transform.flip(base_image, True, False) if not self.facing_right else base_image
            
            self.mask = pygame.mask.from_surface(self.image)


    # ATAQUE MELEE DO BOSS 
    
    def load_efeito(self):

        caminho = 'img/sala_boss/efeito_soco.png'
        frame_width = 570
        frame_height = 420
        num_frames = 14
        # resize = (570, 90)  ""

        sheet = pygame.image.load(caminho).convert_alpha()
        self.efeito_frames = []  # Limpa qualquer frame anterior

        for i in range(num_frames):
            frame = sheet.subsurface(pygame.Rect(i * frame_width, 0, frame_width, frame_height))
            frame = pygame.transform.scale(frame, (880, 669))
            self.efeito_frames.append(frame)


    def desenhar_efeito_melee(self, tela, deslocamento_x, deslocamento_y):
        if not self.efeito_ativo or not self.efeito_frames:
            return

        # Avança o frame até o fim da lista
        self.efeito_timer += 1
        if self.efeito_timer >= self.efeito_speed:
            self.efeito_timer = 0
            self.efeito_index += 1
            if self.efeito_index >= len(self.efeito_frames):
                self.efeito_ativo = False
                return  # Acabou a animação

        # Pega o frame atual
        frame = self.efeito_frames[self.efeito_index]
        if not self.facing_right:
            frame = pygame.transform.flip(frame, True, False)

        scaled_w = int(frame.get_width() * self.zoom_level)
        scaled_h = int(frame.get_height() * self.zoom_level)
        frame_scaled = pygame.transform.scale(frame, (scaled_w, scaled_h))

        centro_x = self.rect.centerx + 900
        centro_y = self.rect.centery + 550

        x_tela = centro_x * self.zoom_level + deslocamento_x - scaled_w // 2
        y_tela = centro_y * self.zoom_level + deslocamento_y - scaled_h // 2

        tela.blit(frame_scaled, (x_tela, y_tela))

        # # --- COLISÃO PERFEITA COM MÁSCARA ---
        # efeito_mask = pygame.mask.from_surface(frame_scaled)
        # efeito_rect_mundo = pygame.Rect(
        #     centro_x - scaled_w // 2,
        #     centro_y - scaled_h // 2,
        #     scaled_w,
        #     scaled_h
        # )

        # for inimigo in inimigos:
        #     if not hasattr(inimigo, "mask") or not inimigo.mask:
        #         continue

        #     offset = (
        #         inimigo.rect.left - efeito_rect_mundo.left,
        #         inimigo.rect.top - efeito_rect_mundo.top
        #     )

        #     if efeito_mask.overlap(inimigo.mask, offset):
        #         print(f"[DEBUG] Efeito colidiu com inimigo em {inimigo.rect.topleft}")
        #         inimigo.receber_dano(2, atacando=True)

    
    # FINAL DO ATAQUE DO MELEE 


    # --- Movimento Removido ---
    def update_movement_and_physics(self): pass
    def check_vertical_collision(self): pass
    def check_horizontal_collision(self): pass
    
    
    def update(self):
        current_time = pygame.time.get_ticks()

        if self.is_dead:
            self.update_animation()
            return

        if self.is_dashing: # Controla todo o processo do dash
            self.rect.centery = self.dash_y # Mantém Y constante
            self.rect.x += self.dash_speed * self.dash_direction # Move para esquerda

            # --- Lógica baseada na Fase do Dash ---
            if self.dash_phase == 1: # Fase 1: Indo para esquerda para sair
                if self.rect.right < 0: # Saiu pela borda esquerda?
                    print("    [DASH Update] Fase 1: Saiu pela esquerda. Teleportando & mudando para Fase 2...")
                    self.rect.left = self.largura_mapa # Teleporta para a borda direita
                    self.dash_phase = 2 # <<< MUDA PARA FASE 2 >>>
                    self.can_dash_damage = True # Permite dano na volta
                    print(f"    [DASH Update] Teleportado para x={self.rect.left}. Fase atual: {self.dash_phase}")

            elif self.dash_phase == 2: # Fase 2: Voltando da direita para o centro
                if self.rect.centerx <= self.original_x: # Chegou ou passou do centro original?
                    print("    [DASH Update] Fase 2: Retornou à posição original. Finalizando dash.")
                    # Reseta tudo
                    self.is_dashing = False
                    self.dash_phase = 0 # Reseta fase
                    self.rect.centerx = self.original_x # Garante posição X
                    self.rect.centery = self.original_y # Garante posição Y
                    self.dash_direction = 0
                    self.can_dash_damage = False
                    # Finaliza IA
                    self.ai_state = 'COOLDOWN'
                    self.last_attack_time = current_time
                    self.chosen_attack = None
                    self.change_state(BOSS_IDLE)

            self.update_animation() # Atualiza animação do dash
            return # Pula IA normal

        # --- Lógica Fora do Dash ---
        self.update_ai(current_time) # IA só roda se não estiver dashando
        self.update_animation()      # Animação normal


    # Dentro de BossFinal:
    def update_ai(self, current_time):
        # Guarda inicial: Não faz nada se morto, em hit ou dashando
        if self.is_dead: return
        if self.state == BOSS_HIT:
            # Lógica de recuperação do hit (sem mudança)
            if current_time - self.last_hit_time >= self.hit_recovery_time:
                self.change_state(BOSS_IDLE)
                self.ai_state = 'IDLE'
                self.is_melee_active = False
            else:
                return # Continua em recuperação
        # <<< ADICIONADO: Guarda para DASHING >>>
        if self.ai_state == 'DASHING':
            # A lógica do dash é tratada no método update principal.
            # A IA não deve interferir aqui.
            # print("[AI Update] Em estado DASHING, AI pausada.") # DEBUG
            return

        # Máquina de Estados Normal (IDLE, CHARGING, ATTACKING, COOLDOWN)
        if self.ai_state == 'IDLE':
            if current_time - self.last_attack_time >= self.attack_cooldown:
                self.choose_attack()
                if self.chosen_attack:
                    self.ai_state = 'CHARGING'
                    self.action_start_time = current_time
                    self.start_charging_animation()
        elif self.ai_state == 'CHARGING':
            if current_time - self.action_start_time >= self.charge_duration:
                self.ai_state = 'ATTACKING'
                self.action_start_time = current_time
                self.execute_attack(current_time)
        elif self.ai_state == 'ATTACKING':
            # Verifica fim da ANIMAÇÃO/AÇÃO para ataques baseados em TEMPO
            # IMPORTANTE: O DASH NÃO É FINALIZADO AQUI
            if self.chosen_attack == 'DASH': # << Se o ataque for DASH, sai daqui
                 return                   #    pois update() controla o fim.
             

            attack_timer_ended = False
            duration_to_check = 0
            if self.chosen_attack == 'FALLING':
                duration_to_check = self.falling_attack_duration
            elif self.chosen_attack == 'PROJECTILE':
                duration_to_check = self.projectile_attack_animation_duration
                self.handle_projectile_attack(current_time) # Continua disparando
            elif self.chosen_attack == 'MELEE':
                duration_to_check = self.melee_attack_duration

            # Verifica se o timer acabou (para ataques NÃO-DASH)
            if duration_to_check > 0 and current_time - self.action_start_time >= duration_to_check:
                 attack_timer_ended = True
                 if self.chosen_attack == 'MELEE':
                     self.is_melee_active = False

            # Transição para COOLDOWN se o ataque (NÃO-DASH) terminou
            if attack_timer_ended:
                 print(f"[AI Update] Ataque '{self.chosen_attack}' terminou por tempo. Indo para COOLDOWN.")
                 self.ai_state = 'COOLDOWN'
                 self.last_attack_time = current_time
                 self.chosen_attack = None
                 if self.state != BOSS_HIT: # Não muda se estiver tomando dano
                     self.change_state(BOSS_IDLE)

        elif self.ai_state == 'COOLDOWN':
            if current_time - self.last_attack_time >= self.attack_cooldown:
                  self.ai_state = 'IDLE'
                  if self.state != BOSS_HIT:
                      self.change_state(BOSS_IDLE)
# --- END OF FILE inimigo.py ---
    # --- choose_attack (sem mudanças) ---
    def choose_attack(self):
        distance_to_player = math.hypot(self.rect.centerx - self.jogador.rect.centerx, self.rect.centery - self.jogador.rect.centery)

        possible_attacks = []

        # Melee só é possível se perto
        if distance_to_player <= self.melee_range:
            possible_attacks.append('MELEE')

        # Ataques padrão sempre possíveis (se não melee)
        possible_attacks.append('FALLING')
        possible_attacks.append('PROJECTILE')

        # <<< ADICIONADO: Dash apenas na Fase 2 >>>
        if self.is_phase_2:
            possible_attacks.append('DASH')
            print("[BOSS Choose] Fase 2 ativa, DASH é uma opção.")

        # Lógica de Escolha (exemplo: prioriza melee se perto, senão aleatório)
        if 'MELEE' in possible_attacks: # Se melee é opção (está perto)
             # Exemplo: 50% de chance de usar melee, 50% de escolher outro
             if random.random() < 0.5:
                 self.chosen_attack = 'MELEE'
             else:
                 # Remove melee para escolher entre os outros
                 possible_attacks.remove('MELEE')
                 if possible_attacks: # Garante que ainda há opções
                     self.chosen_attack = random.choice(possible_attacks)
                 else:
                     self.chosen_attack = 'MELEE' # Fallback se só havia melee
        elif possible_attacks: # Se não está perto para melee, escolhe dos restantes
            # Remove 'MELEE' caso tenha sido adicionado por engano (não deveria)
            if 'MELEE' in possible_attacks: possible_attacks.remove('MELEE')
            if possible_attacks:
                 self.chosen_attack = random.choice(possible_attacks)
            else:
                 self.chosen_attack = None # Segurança
                 print("[BOSS Choose] AVISO: Nenhuma opção de ataque encontrada!")
        else:
             self.chosen_attack = None # Segurança
             print("[BOSS Choose] AVISO: Nenhuma opção de ataque encontrada!")


        print(f"[BOSS Choose] Ataque Escolhido: {self.chosen_attack}")

        # Resets específicos
        if self.chosen_attack == 'PROJECTILE':
            self.projectiles_fired = 0

    # --- start_charging_animation (sem mudanças) ---
    def start_charging_animation(self):
        print(f"[BOSS Charge] Iniciando carga para: {self.chosen_attack}")
        if self.chosen_attack == 'FALLING':
            self.change_state(BOSS_CHARGE_FALLING)
        elif self.chosen_attack == 'PROJECTILE':
            self.change_state(BOSS_CHARGE_PROJECTILE)
        elif self.chosen_attack == 'MELEE':
            self.change_state(BOSS_CHARGE_MELEE)
            self.efeito_index = 0
            self.efeito_timer = 0
            self.efeito_ativo = True
        # <<< ADICIONADO >>>
        elif self.chosen_attack == 'DASH':
            self.change_state(BOSS_CHARGE_DASH)

    # --- execute_attack (sem mudanças) ---
    def execute_attack(self, current_time):
        print(f"[DEBUG Execute] Executando ataque: {self.chosen_attack}")
        if self.chosen_attack == 'FALLING':
            self.change_state(BOSS_ATTACK_FALLING)
            self.spawn_falling_objects()
        elif self.chosen_attack == 'PROJECTILE':
            self.change_state(BOSS_ATTACK_PROJECTILE)
            self.handle_projectile_attack(current_time) # Dispara o primeiro projétil
        elif self.chosen_attack == 'MELEE':
            self.change_state(BOSS_ATTACK_MELEE)
            self.is_melee_active = True
            
        # <<< ADICIONADO >>>
        elif self.chosen_attack == 'DASH':
            print("    [Execute DASH] Configurando variáveis do dash...")
            self.change_state(BOSS_ATTACK_DASH)
            self.is_dashing = True
            self.dash_y = self.rect.centery
            self.dash_direction = -1 # Sempre move para esquerda
            # <<< MODIFICADO: Iniciar Fase 1 >>>
            self.dash_phase = 1
            self.can_dash_damage = True
            self.ai_state = 'DASHING'
            print(f"    Dash iniciado: Fase {self.dash_phase}, Direção {self.dash_direction}, Y: {self.dash_y}, Retorno X: {self.original_x}")
    # --- spawn_falling_objects (REVISADO) ---
    def spawn_falling_objects(self):
        """Cria entre 6 a 8 projéteis amarelos que caem do céu."""
        print(">>>>>>>> [BOSS SPAWN] DENTRO DE spawn_falling_objects (usando FallingProjectile) <<<<<<<<") # DEBUG
        num_objects = random.randint(self.falling_object_min_count, self.falling_object_max_count)
        print(f"    [BOSS SPAWN] Tentando criar {num_objects} FallingProjectiles...") # DEBUG
        created_count = 0
        LARGURA_APROX = 1280 # Aproximação da largura da tela para dispersão

        for i in range(num_objects):
            player_x = self.jogador.rect.centerx
            # Área de spawn horizontal perto do jogador, limitada pelo mapa
            min_x_dispersao = player_x - LARGURA_APROX * 0.6
            max_x_dispersao = player_x + LARGURA_APROX * 0.6
            min_x = max(10, min_x_dispersao)
            max_x = min(self.largura_mapa - 10, max_x_dispersao)

            if min_x >= max_x:
                print(f"    [BOSS SPAWN] Objeto {i}: Área inválida (min_x={min_x}, max_x={max_x}), pulando.")
                continue

            spawn_x = random.uniform(min_x, max_x)
            spawn_y = 50 # Y inicial ACIMA da tela (ajustado para 'top' em FallingProjectile)

            print(f"    [BOSS SPAWN] Criando FallingProjectile {i} em ({spawn_x:.1f}, y_start={spawn_y})") # DEBUG

            # <<< ALTERAÇÃO PRINCIPAL AQUI >>>
            # Instancia a nova classe FallingProjectile
            obj = FallingProjectile(spawn_x, spawn_y, self.falling_object_speed,
                                    self.colisao_rects, self.altura_mapa, dano=1) # Dano padrão 1
            # <<< FIM DA ALTERAÇÃO >>>

            self.falling_objects_group.add(obj) # Adiciona ao grupo LOCAL do boss (o nome do grupo pode ser mantido)
            created_count += 1
        print(f"    [BOSS SPAWN] Criados: {created_count}. Tamanho GRUPO LOCAL (falling_objects_group): {len(self.falling_objects_group)}") # DEBUG


    # --- handle_projectile_attack (sem mudanças) ---
    def handle_projectile_attack(self, current_time):
        if self.projectiles_fired < self.projectile_count and \
           current_time - self.action_start_time >= self.projectiles_fired * self.projectile_interval:
            spawn_x, spawn_y = self.rect.center
            target_x, target_y = self.jogador.rect.center
            proj = BossProjectile(spawn_x, spawn_y, target_x, target_y, self.projectile_speed, self.colisao_rects)
            self.projectiles_group.add(proj)
            self.projectiles_fired += 1
            print(f"[BOSS] Disparou projétil {self.projectiles_fired}") # DEBUG

    # --- handle_melee_attack (sem mudanças) ---
    def handle_melee_attack(self, current_time): pass



    # --- receber_dano (sem mudanças) ---
    def receber_dano(self, dano, atacando=False):
        current_time = pygame.time.get_ticks()
        if self.is_dead or current_time < self.invulnerable_timer:
            return

        self.vida -= dano
        self.last_hit_time = current_time
        self.invulnerable_timer = current_time + self.invulnerable_duration
        print(f"[BOSS] DANO RECEBIDO: {dano}, Vida: {self.vida}/{self.vida_maxima}")

        if self.vida <= 0:
            self.change_state(BOSS_DEATH)
            self.vida = 0
            self.morrer()
        else:
            # Interrompe ação atual se for atingido (exceto durante o dash)
            if not self.is_dashing:
                self.change_state(BOSS_HIT)
                if self.ai_state in ['CHARGING', 'ATTACKING']:
                    print("[BOSS] Hit interrompeu CHARGING/ATTACKING.")
                    self.ai_state = 'IDLE' # Volta para IDLE para reavaliar após hit
                    self.is_melee_active = False
                    self.projectiles_fired = 0

            # <<< ADICIONADO: Verificação da Fase 2 >>>
            if not self.is_phase_2 and (self.vida / self.vida_maxima) <= self.phase_2_threshold:
                self.is_phase_2 = True
                print("\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
                print("!!!!!!!!!! BOSS FASE 2 ATIVADA !!!!!!!!!!")
                print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n")


    # --- morrer (sem mudanças) ---
    def morrer(self):
        if not self.is_dead:
            print("[BOSS] MORREU!"); self.is_dead = True
            self.change_state(BOSS_DEATH); self.is_melee_active = False

    # --- update (sem mudanças) ---
# --- Dentro da classe BossFinal em inimigo.py ---


    # --- draw (sem mudanças) ---
    def draw(self, surface): 
        # if self.boss_instance and self.boss_instance.state == BOSS_ATTACK_MELEE:
        #     self.boss_instance.desenhar_efeito_melee(
        #         tela, self.deslocamento_camera_x, self.deslocamento_camera_y, self.inimigos
        #     )
        pass


# ---------------------------------------------------------------------------------Inimigo_Geleia/Slime - (Rai - Pode reclamar) - Atira

class ProjetilGeleia(pygame.sprite.Sprite):
    def __init__(self, x, y, direcao, grupo_jogador, colisao_rects):
        super().__init__()
        self.colisao_rects = colisao_rects
        self.morto = False
        try:
            sprite_info = SPRITES[MAPA2][INIMIGO2MP2][INIMIGO2MP2PROJETIL]
            sprite = pygame.image.load(sprite_info["file"]).convert_alpha()
            sprite = pygame.transform.scale(sprite, (28, 28))
        except:
            sprite = pygame.Surface((40, 40), pygame.SRCALPHA)
            pygame.draw.circle(sprite, (0, 255, 0), (20, 20), 20)

        if direcao > 0:
            sprite = pygame.transform.flip(sprite, True, False)


        self.image = sprite
        self.rect = self.image.get_rect(center=(x, y))
        self.vel_x = 2 * direcao
        self.dano = 1
        self.grupo_jogador = grupo_jogador

    def update(self):
        self.rect.x += self.vel_x

        # Destruir projétil se o jogador estiver atacando e ele estiver no alcance do ataque
        for jogador in self.grupo_jogador:
            if hasattr(jogador, "atacando") and jogador.atacando:
                # Definir uma área de ataque do jogador
                if jogador.facing_right:
                    area_ataque = pygame.Rect(jogador.rect.right, jogador.rect.top, 30, jogador.rect.height)
                else:
                    area_ataque = pygame.Rect(jogador.rect.left - 30, jogador.rect.top, 30, jogador.rect.height)

                if self.rect.colliderect(area_ataque):
                    self.kill()
                    return


        # Colisão com jogador
        atingidos = pygame.sprite.spritecollide(self, self.grupo_jogador, False, collided=pygame.sprite.collide_mask)
        for jogador in atingidos:
            jogador.receber_dano(self.dano)
            self.kill()

        # ✅ Colisão com o mapa (paredes)
        for rect in self.colisao_rects:
            if self.rect.colliderect(rect):
                self.kill()
                print("Projétil destruído por colisão com parede")                
                return

        # Fora da tela
        if self.rect.right < 0 or self.rect.left > LARGURA:
            self.kill()
            print("Projétil fora da tela")

# ---------------------------------------------------------------------------------

class Inimigo2mp2(pygame.sprite.Sprite):
    def __init__(self, x, y, jogador, colisao_rects, tmx_data, largura_mapa, altura_mapa):
        super().__init__()
        self.state = INIMIGO2MP2IDLE
        self.frame_index = 0
        self.animation_timer = 0
        self.facing_right = True
        self.velocidade_x = 1
        self.velocidade_y = 0
        self.gravity = 0.5
        self.dano = 1
        self.vida = 3
        self.morto = False

        self.jogador = jogador
        self.grupo_jogador = pygame.sprite.GroupSingle(jogador)
        self.colisao_rects = colisao_rects
        self.tmx_data = tmx_data
        self.largura_mapa = largura_mapa
        self.altura_mapa = altura_mapa

        self.x_inicial = x
        self.x_final = x + 170
        self.grupo_projeteis = pygame.sprite.Group()

        self.tempo_ataque = 0
        self.etapa_ataque = None

        self.frames = []
        self.load_sprites()
        self.image = self.frames[self.frame_index] if self.frames else pygame.Surface((32, 32))
        self.rect = self.image.get_rect(topleft=(x, y))
        self.offset_y_ataque = 0  # Correção de altura durante ataque

    def load_sprites(self):
        try:
            sprite_info = SPRITES[MAPA2][INIMIGO2MP2][self.state]
            self.sprite_sheet = pygame.image.load(sprite_info["file"]).convert_alpha()
            self.frames = self.load_frames(sprite_info["frames"], sprite_info["width"], sprite_info["height"])
        except Exception as e:
            print(f"[Erro sprites]: {e}")
            self.frames = [pygame.Surface((28, 28))]
            self.frames[0].fill((255, 0, 0))

    def load_frames(self, frame_count, width, height):
        frames = []
        for i in range(frame_count):
            x = i * width
            frame = self.sprite_sheet.subsurface(pygame.Rect(x, 0, width, height))

            # Aumenta o tamanho da animação de morte
            if self.state == INIMIGO1MP1IDLE:
                frame = pygame.transform.scale(frame, (28, 28))  # ← maior
            else:
                frame = pygame.transform.scale(frame, (40, 40))

            frames.append(frame)
        return frames

    def update_animation(self):
        if not self.frames:
            return

        # Se for animação de morte, deixa mais lenta
        if self.state == INIMIGO2MP2MORTO:
            velocidade_anim = 7
        elif self.state == INIMIGO2MP2IDLE:
            velocidade_anim = 4
        else:
            velocidade_anim = 4

        self.animation_timer += 1
        if self.animation_timer >= velocidade_anim:
            if self.state == INIMIGO2MP2MORTO:
                # Avança até o último frame e para
                if self.frame_index < len(self.frames) - 1:
                    self.frame_index += 1
            else:
                self.frame_index = (self.frame_index + 1) % len(self.frames)

            self.animation_timer = 0

        frame = self.frames[self.frame_index]
        self.image = pygame.transform.flip(frame, True, False) if self.facing_right else frame

    def linha_de_visao_livre(self):
        # Pega o ponto central do inimigo e do jogador
        x1, y1 = self.rect.center
        x2, y2 = self.jogador.rect.center

        # Divide a linha em passos para checar por obstáculos no caminho
        passos = max(abs(x2 - x1), abs(y2 - y1))
        if passos == 0:
            return True  # mesmo ponto, sem obstáculos

        for i in range(passos + 1):
            t = i / passos
            x = int(x1 + (x2 - x1) * t)
            y = int(y1 + (y2 - y1) * t)

            ponto = pygame.Rect(x, y, 1, 1)  # ponto de verificação como retângulo
            for obstaculo in self.colisao_rects:
                if ponto.colliderect(obstaculo):
                    return False  # obstáculo na frente
        return True  # caminho livre

    def patrulhar(self):
        self.state = INIMIGO2MP2IDLE
        if self.facing_right:
            self.rect.x += self.velocidade_x
            if self.rect.right >= self.x_final:
                self.rect.right = self.x_final
                self.facing_right = False
        else:
            self.rect.x -= self.velocidade_x
            if self.rect.left <= self.x_inicial:
                self.rect.left = self.x_inicial
                self.facing_right = True

    def atacar(self):
        agora = pygame.time.get_ticks()
        if agora - self.tempo_ataque > 1000:  # tempo de recarga reduzido
            self.tempo_ataque = agora
            self.etapa_ataque = "carregando"
            self.frame_index = 0

            self.facing_right = self.jogador.rect.centerx > self.rect.centerx

            # Salvar a posição dos pés antes de trocar o sprite
            pos_pe = self.rect.bottom

            self.state = INIMIGO2MP2ATTACK
            self.load_sprites()

            # Ajustar a nova posição para manter os pés no chão
            self.rect = self.image.get_rect(midbottom=(self.rect.centerx, pos_pe))

    def disparar_projétil(self):
        self.facing_right = self.jogador.rect.centerx > self.rect.centerx  # virar para o jogador
        direcao = 1 if self.facing_right else -1
        proj = ProjetilGeleia(
            self.rect.centerx,
            self.rect.centery,
            direcao,
            self.grupo_jogador,
            self.colisao_rects  # <<< adiciona os rects aqui
        )
        print(f"Projétil criado em: ({proj.rect.x}, {proj.rect.y}) com direção: {direcao}")
        print("Slime disparou!")

        self.grupo_projeteis.add(proj)

    def receber_dano(self, quantidade, atacando=False):
        self.vida -= quantidade

        # Se morreu
        if self.vida <= 0:
            self.vida = 0
            self.state = INIMIGO2MP2MORTO
            self.frame_index = 0
            self.load_sprites()
            return

        # Se ainda está vivo, entra no estado de dano
        self.state = INIMIGO2MP2DANO
        self.frame_index = 0
        self.load_sprites()

        # ❌ Cancelar ataque se estava carregando
        self.etapa_ataque = None

    def update(self):
        if self.state == INIMIGO2MP2DANO:
            self.update_animation()

            # Quando a animação de dano terminar, volta ao normal
            if self.frame_index == len(self.frames) - 1:
                self.state = INIMIGO2MP2IDLE
                self.load_sprites()
                self.frame_index = 0
            return

        if self.vida <= 0:
            # Se estiver no estado de morte, anima até o fim e remove
            if self.state == INIMIGO2MP2MORTO:
                self.update_animation()
                if self.frame_index == len(self.frames) - 1:
                    self.kill()
            return

        distancia = abs(self.rect.centerx - self.jogador.rect.centerx)
        alinhado = abs(self.rect.centery - self.jogador.rect.centery) < 40
        mesma_direcao = (
            (self.facing_right and self.jogador.rect.centerx > self.rect.centerx) or
            (not self.facing_right and self.jogador.rect.centerx < self.rect.centerx)
        )
        agora = pygame.time.get_ticks()

        if self.etapa_ataque == "carregando":
            if self.frame_index >= len(self.frames) - 1:
                self.disparar_projétil()
                self.etapa_ataque = None
                self.state = INIMIGO2MP2IDLE
                self.load_sprites()
                self.frame_index = 0
        elif distancia < 250 and alinhado and (agora - self.tempo_ataque > 1000) and self.linha_de_visao_livre():
            self.atacar()
        else:
            self.patrulhar()

        self.velocidade_y += self.gravity
        self.rect.y += self.velocidade_y
        colidiu = self.colisao_vertical()
        if colidiu:
            if self.velocidade_y > 0:
                self.rect.bottom = colidiu.top
            elif self.velocidade_y < 0:
                self.rect.top = colidiu.bottom
            self.velocidade_y = 0

        self.grupo_projeteis.update()
        self.update_animation()


    def colisao_vertical(self):
        for rect in self.colisao_rects:
            if self.rect.colliderect(rect):
                return rect
        return None

    def draw(self, surface, zoom=1.0, deslocamento_x=0, deslocamento_y=0):
        # Desenhar o slime
        scaled_image = pygame.transform.scale(
            self.image,
            (
                int(self.image.get_width() * zoom),
                int(self.image.get_height() * zoom)
            )
        )

        pos_x = self.rect.x * zoom + deslocamento_x
        # Ajuste vertical para ataque
        if self.state == INIMIGO2MP2ATTACK:
            offset_y = -8
        elif self.state == INIMIGO2MP2DANO:
            offset_y = -12
        else:
            offset_y = 0

        pos_y = (self.rect.y + offset_y) * zoom + deslocamento_y
        surface.blit(scaled_image, (pos_x, pos_y))


        # ✅ Desenhar projéteis (usando o nome correto do grupo!)
        for proj in self.grupo_projeteis:
            proj_image = pygame.transform.scale(
                proj.image,
                (
                    int(proj.image.get_width() * zoom),
                    int(proj.image.get_height() * zoom)
                )
            )
            proj_x = proj.rect.x * zoom + deslocamento_x
            proj_y = proj.rect.y * zoom + deslocamento_y
            surface.blit(proj_image, (proj_x, proj_y))

# ---------------------------------------------------------------------------------Inimigo_Geleia/Slime - (Rai - Pode reclamar) - Não atira

class Inimigo2mp2_1(pygame.sprite.Sprite):
    def __init__(self, x, y, jogador, colisao_rects, tmx_data, largura_mapa, altura_mapa):
        super().__init__()
        self.state = INIMIGO2MP2IDLE
        self.frame_index = 0
        self.animation_timer = 0
        self.facing_right = True
        self.velocidade_x = 1
        self.velocidade_y = 0
        self.gravity = 0.5
        self.dano = 1
        self.vida = 3
        self.morto = False

        self.jogador = jogador
        self.grupo_jogador = pygame.sprite.GroupSingle(jogador)
        self.colisao_rects = colisao_rects
        self.tmx_data = tmx_data
        self.largura_mapa = largura_mapa
        self.altura_mapa = altura_mapa

        self.x_inicial = x
        self.x_final = x + 170

        self.frames = []
        self.load_sprites()
        self.image = self.frames[self.frame_index] if self.frames else pygame.Surface((32, 32))
        self.rect = self.image.get_rect(topleft=(x, y))

    def load_sprites(self):
        try:
            sprite_info = SPRITES[MAPA2][INIMIGO2MP2][self.state]
            self.sprite_sheet = pygame.image.load(sprite_info["file"]).convert_alpha()
            self.frames = self.load_frames(sprite_info["frames"], sprite_info["width"], sprite_info["height"])
        except Exception as e:
            print(f"[Erro sprites]: {e}")
            self.frames = [pygame.Surface((28, 28))]
            self.frames[0].fill((255, 0, 0))

    def load_frames(self, frame_count, width, height):
        frames = []
        for i in range(frame_count):
            x = i * width
            frame = self.sprite_sheet.subsurface(pygame.Rect(x, 0, width, height))

            if self.state == INIMIGO1MP1IDLE:
                frame = pygame.transform.scale(frame, (28, 28))  # ← maior
            else:
                frame = pygame.transform.scale(frame, (40, 40))

            frames.append(frame)
        return frames

    def update_animation(self):
        if not self.frames:
            return

        if self.state == INIMIGO2MP2MORTO:
            velocidade_anim = 7
        elif self.state == INIMIGO2MP2IDLE:
            velocidade_anim = 4
        else:
            velocidade_anim = 4

        self.animation_timer += 1
        if self.animation_timer >= velocidade_anim:
            if self.state == INIMIGO2MP2MORTO:
                if self.frame_index < len(self.frames) - 1:
                    self.frame_index += 1
            else:
                self.frame_index = (self.frame_index + 1) % len(self.frames)

            self.animation_timer = 0

        frame = self.frames[self.frame_index]
        self.image = pygame.transform.flip(frame, True, False) if self.facing_right else frame

    def patrulhar(self):
        self.state = INIMIGO2MP2IDLE
        if self.facing_right:
            self.rect.x += self.velocidade_x
            if self.rect.right >= self.x_final:
                self.rect.right = self.x_final
                self.facing_right = False
        else:
            self.rect.x -= self.velocidade_x
            if self.rect.left <= self.x_inicial:
                self.rect.left = self.x_inicial
                self.facing_right = True

    def receber_dano(self, quantidade, atacando=False):
        self.vida -= quantidade

        if self.vida <= 0:
            self.vida = 0
            self.state = INIMIGO2MP2MORTO
            self.frame_index = 0
            self.load_sprites()
            return

        self.state = INIMIGO2MP2DANO
        self.frame_index = 0
        self.load_sprites()

    def update(self):
        if self.state == INIMIGO2MP2DANO:
            self.update_animation()
            if self.frame_index == len(self.frames) - 1:
                self.state = INIMIGO2MP2IDLE
                self.load_sprites()
                self.frame_index = 0
            return

        if self.vida <= 0:
            if self.state == INIMIGO2MP2MORTO:
                self.update_animation()
                if self.frame_index == len(self.frames) - 1:
                    self.kill()
            return

        distancia = abs(self.rect.centerx - self.jogador.rect.centerx)
        alinhado = abs(self.rect.centery - self.jogador.rect.centery) < 40
        mesma_direcao = (
            (self.facing_right and self.jogador.rect.centerx > self.rect.centerx) or
            (not self.facing_right and self.jogador.rect.centerx < self.rect.centerx)
        )

        # Remover a verificação da linha de visão
        if distancia < 250 and alinhado:
            self.patrulhar()
        else:
            self.patrulhar()

        self.velocidade_y += self.gravity
        self.rect.y += self.velocidade_y
        colidiu = self.colisao_vertical()
        if colidiu:
            if self.velocidade_y > 0:
                self.rect.bottom = colidiu.top
            elif self.velocidade_y < 0:
                self.rect.top = colidiu.bottom
            self.velocidade_y = 0

        self.update_animation()


    def colisao_vertical(self):
        for rect in self.colisao_rects:
            if self.rect.colliderect(rect):
                return rect
        return None

    def draw(self, surface, zoom=1.0, deslocamento_x=0, deslocamento_y=0):
        scaled_image = pygame.transform.scale(
            self.image,
            (
                int(self.image.get_width() * zoom),
                int(self.image.get_height() * zoom)
            )
        )

        pos_x = self.rect.x * zoom + deslocamento_x
        if self.state == INIMIGO2MP2ATTACK:
            offset_y = -8
        elif self.state == INIMIGO2MP2DANO:
            offset_y = -12
        else:
            offset_y = 0

        pos_y = (self.rect.y + offset_y) * zoom + deslocamento_y
        surface.blit(scaled_image, (pos_x, pos_y))


# ---------------------------------------------------------------------------------------------Inimigo_Dragão - (Rai - Pode reclamar)

class Inimigo3mp2(pygame.sprite.Sprite):
    def __init__(self, x, y, jogador, colisao_rects, tmx_data, largura_mapa, altura_mapa):
        super().__init__()
        self.state = INIMIGO3MP2IDLE
        self.frame_index = 0
        self.animation_timer = 0
        self.facing_right = True
        self.velocidade_x = 1
        self.velocidade_y = 0
        self.gravity = 0.5
        self.atacando = False
        self.dano = 1
        self.morto = False

        self.jogador = jogador
        self.grupo_jogador = pygame.sprite.GroupSingle(self.jogador)
        self.colisao_rects = colisao_rects
        self.tmx_data = tmx_data
        self.largura_mapa = largura_mapa
        self.altura_mapa = altura_mapa

        self.vida = 80

        self.sprites_por_estado = {}
        self.sprites_flip_por_estado = {}
        self.carregar_todos_sprites()
        self.frames = self.sprites_por_estado[self.state]
        self.frames_flip = self.sprites_flip_por_estado[self.state]

        self.x_inicial = x
        self.x_final = x + 190
        self.patrulhando = True

        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect(topleft=(x, y))
        self.mask = pygame.mask.from_surface(self.image)

    def carregar_todos_sprites(self):
        for estado in SPRITES[MAPA2][INIMIGO3MP2]:
            info = SPRITES[MAPA2][INIMIGO3MP2][estado]
            sprite_sheet = pygame.image.load(info["file"]).convert_alpha()
            frames = self.load_frames(info["frames"], info["width"], info["height"], sprite_sheet)
            frames_flip = [pygame.transform.flip(f, True, False) for f in frames]
            self.sprites_por_estado[estado] = frames
            self.sprites_flip_por_estado[estado] = frames_flip

    def mudar_estado(self, novo_estado):
        if self.state != novo_estado:
            self.state = novo_estado
            self.frames = self.sprites_por_estado[novo_estado]
            self.frames_flip = self.sprites_flip_por_estado[novo_estado]
            self.frame_index = 0
            self.animation_timer = 0

    def load_frames(self, frame_count, width, height, sprite_sheet):
        frames = []
        for i in range(frame_count):
            x = i * width
            frame = sprite_sheet.subsurface(pygame.Rect(x, 0, width, height))
            if self.state == INIMIGO3MP2ATTACK:
                frame = pygame.transform.scale(frame, (80, 80))
            else:
                frame = pygame.transform.scale(frame, (50, 50))
            frames.append(frame)
        return frames

    def update_animation(self):
        if not self.frames:
            return

        if self.state == INIMIGO3MP2DANO:
            velocidade_anim = 5
        elif self.state == INIMIGO3MP2MORTO:
            velocidade_anim = 3
        else:
            velocidade_anim = 6 if self.state == INIMIGO3MP2ATTACK else 10

        self.animation_timer += 1
        if self.animation_timer >= velocidade_anim:
            self.frame_index += 1
            self.animation_timer = 0


            if self.frame_index >= len(self.frames):
                if self.state == INIMIGO3MP2MORTO:
                    self.kill()
                    return
                elif self.state == INIMIGO3MP2DANO:
                    self.mudar_estado(INIMIGO3MP2IDLE)
                    return
                elif self.state == INIMIGO3MP2ATTACK:
                    self.mudar_estado(INIMIGO3MP2IDLE)
                    self.atacando = False
                    return
                self.frame_index %= len(self.frames)

        frame = self.frames[self.frame_index]
        self.image = frame if self.facing_right else self.frames_flip[self.frame_index]
        if self.state == INIMIGO3MP2ATTACK:
            self.image = pygame.transform.scale(self.image, (90, 90))
        elif self.state == INIMIGO3MP2DANO:
            self.image = pygame.transform.scale(self.image, (65, 65))

        old_center = self.rect.center
        self.rect = self.image.get_rect()
        self.rect.center = old_center
        self.mask = pygame.mask.from_surface(self.image)


    def receber_dano(self, dano, atacando=False):
        if self.morto:
            return  # já morreu, ignora dano
        if atacando:
            self.vida -= dano
            self.rect.y += 7  # <- Desce um pouco
            if self.vida <= 0:
                self.morrer()
            else:
                self.mudar_estado(INIMIGO3MP2DANO)

    def morrer(self):
        self.mudar_estado(INIMIGO3MP2MORTO)
        self.morto = True
        self.frame_index = 0
        self.animation_timer = 0

    def colisao_vertical(self):
        for rect in self.colisao_rects:
            if self.rect.colliderect(rect):
                return rect
        return None

    def patrulhar(self):
        self.mudar_estado(INIMIGO3MP2IDLE)
        if self.facing_right:
            if self.ha_chao_a_frente(10):
                self.rect.x += self.velocidade_x
                if self.rect.right >= self.x_final:
                    self.rect.right = self.x_final
                    self.facing_right = False
            else:
                self.facing_right = False
        else:
            if self.ha_chao_a_frente(-10):
                self.rect.x -= self.velocidade_x
                if self.rect.left <= self.x_inicial:
                    self.rect.left = self.x_inicial
                    self.facing_right = True
            else:
                self.facing_right = True

    def ha_chao_a_frente(self, offset_x):
        check_x = self.rect.midbottom[0] + offset_x
        check_y = self.rect.midbottom[1] + 50
        ponto_teste = pygame.Rect(check_x, check_y, 1, 1)
        for rect in self.colisao_rects:
            if rect.colliderect(ponto_teste):
                return True
        return False

    def perseguir(self):
        self.mudar_estado(INIMIGO3MP2IDLE)
        if self.jogador.rect.centerx > self.rect.centerx:
            if self.ha_chao_a_frente(10):
                self.rect.x += self.velocidade_x
            if not self.facing_right:
                self.facing_right = True
        else:
            if self.ha_chao_a_frente(-10):
                self.rect.x -= self.velocidade_x
            if self.facing_right:
                self.facing_right = False

    def atacar(self):
        if not self.atacando:
            self.atacando = True
            self.mudar_estado(INIMIGO3MP2ATTACK)

    def update(self):
        if self.atacando:
            self.velocidade_y += self.gravity
            self.rect.y += self.velocidade_y

            colidiu = self.colisao_vertical()
            if colidiu:
                if self.velocidade_y > 0:
                    self.rect.bottom = colidiu.top
                elif self.velocidade_y < 0:
                    self.rect.top = colidiu.bottom
                self.velocidade_y = 0

            if pygame.sprite.collide_mask(self, self.jogador):
                self.jogador.receber_dano(self.dano)

            self.update_animation()
            return

        distancia = abs(self.rect.centerx - self.jogador.rect.centerx)
        distanciab = abs(self.x_final - self.x_inicial)

        if distancia >= distanciab:
            self.patrulhando = True
            self.patrulhar()
        else:
            self.patrulhando = False
            self.perseguir()
            if distancia <= 33 or pygame.sprite.collide_mask(self, self.jogador):
                self.atacar()

        self.velocidade_y += self.gravity
        self.rect.y += self.velocidade_y

        colidiu = self.colisao_vertical()
        if colidiu:
            if self.velocidade_y > 0:
                self.rect.bottom = colidiu.top
            elif self.velocidade_y < 0:
                self.rect.top = colidiu.bottom
            self.velocidade_y = 0

        if pygame.sprite.collide_mask(self, self.jogador):
            self.jogador.receber_dano(self.dano)

        self.mask = pygame.mask.from_surface(self.image)
        self.update_animation()

