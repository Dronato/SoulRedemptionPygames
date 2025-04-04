import pygame
import math



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

# Configuração dos sprites e frames
SPRITES = {
    MAPA1:{
        INIMIGO1MP1:{
            INIMIGO1MP1IDLE:{"file": "img/mapa1/inimigo1/inimigo1_andando.png", "frames": 3, "width": 445, "height": 394},
            INIMIGO1MP1ATTACK:{"file": "img/mapa1/inimigo1/inimigo1mp1_ataque.png", "frames": 12, "width": 445, "height": 389},
            INIMIGO1MP1DANO:{"file": "img/mapa1/inimigo1/inimigo1mp1_dano.png", "frames": 10, "width": 445, "height": 389},
            INIMIGO1MP1MORTO:{"file": "img/mapa1/inimigo1/inimigo1mp1_morto.png", "frames": 1, "width": 445, "height": 389}
            ,}
            },
    MAPA2:{
        INIMIGO1MP2:{
            INIMIGO1MP2IDLE:{"file": "img/mapa2/inimigo1/inimigo1mp2_andando.png", "frames": 3, "width": 445, "height": 394},
            INIMIGO1MP2ATTACK:{"file": "img/mapa2/inimigo1/inimigo1mp2_ataque.png", "frames": 12, "width": 445, "height": 389},
            INIMIGO1MP2DANO:{"file": "img/mapa2/inimigo1/inimigo1mp2_dano.png", "frames": 10, "width": 445, "height": 389},
            INIMIGO1MP2MORTO:{"file": "img/mapa2/inimigo1/inimigo1mp2_morto.png", "frames": 1, "width": 445, "height": 389},
            INIMIGO1MP2CARREGANDO:{"file": "img/mapa2/inimigo1/inimigo1mp2_carregandolaser.png", "frames": 13, "width": 400, "height": 400}
            ,}
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

        self.image = pygame.Surface((30, 30))
        self.image.fill((255, 0, 0))
        self.rect = self.image.get_rect(topleft=(x, y))

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
            return

        try:
            sprite_info = SPRITES[MAPA2][INIMIGO1MP2][self.state]
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
            self.state = INIMIGO1MP2DANO
            self.load_sprites()
            self.vida -= dano
            if self.vida <= 0:
                self.morrer()

    def morrer(self):
        """Define o estado de morte do inimigo e mantém a imagem parada."""
        self.state = INIMIGO1MP2MORTO
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
        if self.state == INIMIGO1MP2MORTO:
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

    def criar_laser(self):
        self.alvo_travado = (self.jogador.rect.centerx, self.jogador.rect.centery)
        self.atacando = True
        self.tempo_ataque = self.tempo_max_ataque



    def patrulhar(self):
        if self.patrulhando:
            self.state = INIMIGO1MP2IDLE
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
            self.state = INIMIGO1MP2ATTACK
            self.load_sprites()
            self.atacando = True
            if self.jogador.rect.centerx > self.rect.centerx:
                self.rect.x += self.velocidade_x  # Mover para a direita
                self.facing_right = True
                self.state = INIMIGO1MP2ATTACK
            else:
                self.state = INIMIGO1MP2ATTACK
                self.rect.x -= self.velocidade_x  # Mover para a esquerda
                self.facing_right = False
        if distancia >= 100:
            self.atacando = False
            self.patrulhar()

    def detectar_jogador(self):
        distancia = abs(self.rect.centerx - self.jogador.rect.centerx)
        distanciab = abs(self.x_final - self.x_inicial)

        if distancia <= distanciab:
            self.patrulhando = False
            self.facing_right = self.jogador.rect.centerx > self.rect.centerx
            self.alvo_travado = (self.jogador.rect.centerx, self.jogador.rect.centery)
            self.indicador_visivel = True
            self.tempo_ataque = pygame.time.get_ticks()
            self.carregar_laser()

    
    def carregar_laser(self):
        """Faz o inimigo carregar o ataque antes de disparar o laser."""
        agora = pygame.time.get_ticks()
        
        if agora - self.ultimo_ataque >= self.laser_cooldown:  # Verifica cooldown
            self.ultimo_ataque = agora
            self.state = INIMIGO1MP2CARREGANDO
            self.load_sprites()
            self.indicador_visivel = True
            self.esta_atacando = True
            self.tempo_ataque = agora  # Marca o início do carregamento

    def update(self):

        agora = pygame.time.get_ticks()

        if self.state == INIMIGO1MP2MORTO:
            return  # Sai da função para não atualizar nada
        
        # distancia = abs(self.rect.centerx - self.jogador.rect.centerx)
        # distanciab = abs(self.x_final - self.x_inicial)
        
        if self.esta_atacando:
            if agora - self.tempo_ataque >= 1000:  # Aviso dura 1 segundo
                self.laser_visivel = True
            if agora - self.tempo_ataque >= 2000:  # Ataque finaliza após 2s
                self.esta_atacando = False
                self.laser_visivel = False
                self.patrulhando = True
                self.ultimo_ataque = agora
        else:
            if agora - self.ultimo_ataque >= self.laser_cooldown + self.tempo_nova_detecao:
                self.detectar_jogador()
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



        inimigos_atingidos = pygame.sprite.spritecollide(self, self.grupo_jogador, False, collided=pygame.sprite.collide_mask)
        for jogador in inimigos_atingidos:
            self.receber_dano(jogador.dano)

        # **Chamando a atualização da animação!**
        self.update_animation()

    def draw(self, surface):
        """Desenha o inimigo na tela."""
        surface.blit(self.image, self.rect.topleft)
        if self.indicador_visivel and self.alvo_travado:
            pygame.draw.line(surface, (255, 255, 0), self.rect.center, self.alvo_travado, 3)
        if self.atacando and self.alvo_travado:
            pygame.draw.line(surface, (255, 0, 0), self.rect.center, self.alvo_travado, 6)
