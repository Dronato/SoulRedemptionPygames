# --- START OF FILE player.py ---

import pygame

# Constantes da tela e FPS (idealmente definidas em main.py ou um config.py)
# tela = pygame.display.set_mode((0, 0), pygame.FULLSCREEN) # Remover daqui
# LARGURA, ALTURA = tela.get_size() # Remover daqui
# FPS = 60 # Remover daqui
# relogio = pygame.time.Clock() # Remover daqui

# Configuração dos sprites e frames (manter)
IDLE = "idle"
WALK = "walk"
# ATTACK = "attack" # Parece não usado, comentar ou remover se confirmado
PULO = 'pulo'
DASH = 'dash'
ATTACK1 = 'attack1'
ATTACK2 = 'attack2'
ATTACK3 = 'attack3'
INIMIGOIDLE = "enemyidle" # Definido mas não usado na classe Jogador?
SPRITES = {
    # INIMIGOIDLE:{"file": "img/mapa1/inimigo1/inimigo1_andando.png", "frames": 3, "width":445 , "height": 394}, # Mover para inimigo.py se for do inimigo
    IDLE: {"file": "img/prota/parada.png", "frames": 6, "width": 176, "height": 148},
    WALK: {"file": "img/prota/andando.png", "frames": 10, "width": 198, "height": 144},
    # ATTACK: {"file": "img/prota/dano_spritesheet.png", "frames": 5, "width": 340, "height": 320}, # Comentado
    PULO: {"file": "img/prota/pulo.png", "frames": 15, "width": 256, "height": 256},
    DASH: {"file": "img/prota/dash.png", "frames": 5, "width": 214, "height": 144},
    ATTACK1: {"file": "img/prota/attack1.png", "frames": 6, "width": 339, "height": 402},
    ATTACK2: {"file": "img/prota/attack2.png", "frames": 7, "width": 339, "height": 402},
    ATTACK3: {"file": "img/prota/attack3.png", "frames": 8, "width": 339, "height": 402},
}

# --- START OF FILE player.py ---

import pygame

# Constantes e SPRITES (como estavam antes)
# ... (resto das constantes e dicionário SPRITES) ...

class Jogador(pygame.sprite.Sprite):
    def __init__(self, x, y, colisao_rects, rampas_esquerda_rects, rampas_direita_rects,buraco_rects,lava_rects, tmx_data, zoom_level=2.0):
        super().__init__()
        self.state = IDLE
        self._sprites_cache = {} # Cache para superfícies de sprites carregadas

        # --- MOVER DEFINIÇÕES PARA CÁ ---
        self.facing_right = True # Definir ANTES de load_sprites
        self.animation_timer = 0
        self.animation_speed = 8
        self.frame_index = 0 # Definir frame_index inicial
        # --- FIM DAS DEFINIÇÕES MOVIDAS ---
        self.LAVA_SINK_DURATION = 750  # Milissegundos (0.75 segundos) para afundar antes de morrer
        self.LAVA_SINK_SPEED = 1.5 
        # Chamar load_sprites AGORA que facing_right existe
        self.load_sprites()
        # self.frame_index = 0 # frame_index já foi definido antes e resetado em load_sprites se necessário
        self.image = self.frames[self.frame_index]

        # Definir rects de posição e colisão
        self.rect = self.image.get_rect(topleft=(x, y))
        self.collision_rect = pygame.Rect(self.rect.left + 5, self.rect.top, self.rect.width - 10, self.rect.height)
        self.collision_rect.midbottom = self.rect.midbottom

        # Armazenar rects de colisão e rampas
        self.colisao_rects = colisao_rects
        self.rampas_esquerda = rampas_esquerda_rects
        self.rampas_direita = rampas_direita_rects
        self.tmx_data = tmx_data
        self.zoom_level = zoom_level

        # Timer para dano dos espinhos
        self.ultimo_dano_espinhos = 0
        self.intervalo_dano_espinhos = 1000
        
        self.buraco_rects = buraco_rects
        self.lava_rects = lava_rects
        self.morreu_queimado = False
        self.sinking_in_lava = False         # <-- NOVO: Flag para indicar afundamento
        self.lava_sink_start_time = 0
        # Atributos de movimento e física
        self.vel_x = 0
        self.vel_y = 0
        self.velocidade = 5
        self.velocidade_dash = 7
        self.forca_pulo = -10
        self.gravidade = 0.8
        self.no_chao = False
        self.on_ramp = False # Flag para indicar se está em uma rampa
        self.pulos_restantes = 2
        self.pulo_pressionado = False

        # Atributos de Dash
        self.dash_ativo = False
        self.dash_duracao = 12
        self.dash_timer = 0
        self.dash_cooldown_duration = 1500
        self.ultimo_dash_time = 0
        self.direcao_dash = 1 # Inicializa com a direção padrão (direita)
        self.pode_dash = True

        # Sistema de vida
        self.vida_maxima = 5
        self.vida_atual = 5
        self.invulneravel = False
        self.ultimo_dano = 0
        self.tempo_invulneravel = 1000

        # Sistema de cura
        self.curas_maximas = 3
        self.curas_restantes = self.curas_maximas
        # self.pode_curar = True # Esta flag parece não ser usada

        # Ataque
        self.attack_sequence = []
        self.last_attack_time = 0
        self.MAX_ATTACK_INTERVAL = 700
        # self.ataque_pressionado = False # Flag não usada?
        self.is_attacking = False
        self.dano = 10

    # --- O resto do código da classe Jogador (load_sprites, atualizar, etc.) permanece o mesmo ---
    # ... (funções load_sprites, load_frames, receber_dano, etc.) ...

    def check_buraco_collision(self):
        """Verifica colisão do jogador com os retângulos da camada 'Buraco'."""
        for buraco_rect in self.buraco_rects:
            # Usar collision_rect para a física
            if self.collision_rect.colliderect(buraco_rect):
                self.vida_atual = 0  # Morte instantânea
                self.caiu_no_buraco = True # Marca a causa da morte
                print("Jogador caiu no buraco!") # Log
                return True # Colidiu com um buraco
        return False # Nenhuma colisão com buraco
    
    def check_lava_collision(self):
        """Verifica colisão com 'Lava'. Inicia o processo de afundar."""
        # Só checa se não estiver já afundando
        if self.sinking_in_lava: return False

        for lava_rect in self.lava_rects:
            # Usar uma colisão um pouco mais generosa (ex: centro ou base do jogador)
            # para iniciar o afundamento talvez um pouco antes
            # check_point = self.collision_rect.midbottom
            # if lava_rect.collidepoint(check_point):
            if self.collision_rect.colliderect(lava_rect): # Manter colisão de rect por enquanto
                if self.vida_atual > 0 and not self.sinking_in_lava: # Começa a afundar
                    self.sinking_in_lava = True
                    self.lava_sink_start_time = pygame.time.get_ticks()
                    self.vel_x = 0 # Parar movimento horizontal ao cair na lava
                    self.vel_y = self.LAVA_SINK_SPEED # Iniciar afundamento imediatamente
                    print("Jogador começou a afundar na lava!")
                    # Tocar som de lava?
                    # Mudar para animação específica de lava?
                    # self.state = "LAVA_SINK" # Se tiver animação
                    # self.load_sprites()
                    return True # Indica que tocou na lava
        return False # Não tocou ou já estava afundando
    def load_sprites(self):
        # Otimização: Usar um cache para não recarregar/redimensionar toda vez
        state_info = SPRITES[self.state]
        sprite_key = (self.state, self.facing_right) # Chave pode incluir direção se houver sprites diferentes

        if sprite_key in self._sprites_cache:
            self.frames = self._sprites_cache[sprite_key]
            # Garantir que a imagem atual seja definida corretamente ao carregar do cache
            self.frame_index = min(self.frame_index, len(self.frames) - 1)
            self.image = self.frames[self.frame_index]
            return

        # Carregar e processar se não estiver no cache
        try:
            # Verificar se 'file' é string (caminho) ou Surface (já carregado - como no seu main.py original)
            if isinstance(state_info["file"], str):
                 sprite_sheet = pygame.image.load(state_info["file"]).convert_alpha()
            else:
                 sprite_sheet = state_info["file"] # Assume que já é uma Surface carregada

            frames = []
            for i in range(state_info["frames"]):
                x = i * state_info["width"]
                frame = sprite_sheet.subsurface(pygame.Rect(x, 0, state_info["width"], state_info["height"]))
                # Redimensionar para o tamanho desejado do jogador *no jogo* (não o tamanho do tile do mapa)
                # Usar self.rect.width/height aqui pode ser problemático se o rect ainda não foi inicializado corretamente
                # Definir um tamanho padrão ou derivá-lo do primeiro estado (IDLE) pode ser melhor
                target_width = 50 # Exemplo: tamanho fixo no jogo
                target_height = 50 # Exemplo: tamanho fixo no jogo
                # frame = pygame.transform.scale(frame, (self.rect.width, self.rect.height)) # Usar tamanho do rect
                frame = pygame.transform.scale(frame, (target_width, target_height)) # Usar tamanho fixo

                frames.append(frame)

            self.frames = frames
            self._sprites_cache[sprite_key] = frames
            self.frame_index = 0 # Resetar frame index ao carregar novos sprites
            self.image = self.frames[self.frame_index]
            # self.mask = pygame.mask.from_surface(self.image) # Atualizar máscara se usar colisão por máscara

            # Definir o rect inicial com base no primeiro frame carregado
            if self.rect.width == 0 or self.rect.height == 0: # Se o rect não foi inicializado
                 self.rect = self.image.get_rect(topleft=self.rect.topleft)
                 self.collision_rect = pygame.Rect(self.rect.left + 5, self.rect.top, self.rect.width - 10, self.rect.height)
                 self.collision_rect.midbottom = self.rect.midbottom

        except Exception as e:
            print(f"Erro ao carregar sprites para o estado {self.state}: {e}")
            # Fallback para um placeholder ou estado anterior, se possível
            if IDLE in SPRITES and sprite_key != (IDLE, self.facing_right): # Evitar recursão infinita
                print(f"Tentando carregar estado IDLE como fallback.")
                self.state = IDLE
                self.load_sprites()
            else:
                 # Criar um surface vazia como último recurso
                 self.image = pygame.Surface((50, 50), pygame.SRCALPHA)
                 self.image.fill((255,0,255)) # Magenta para indicar erro
                 self.frames = [self.image]
                 self.rect = self.image.get_rect(topleft=self.rect.topleft if hasattr(self, 'rect') else (0,0))
                 self.collision_rect = self.rect.copy()


    def load_frames(self, frame_count, width, height):
        # Esta função parece redundante agora que a lógica está em load_sprites. Remover ou ajustar.
        # A lógica original está incorporada em load_sprites.
        # Se precisar dela separada, certifique-se que ela retorna a lista de frames.
        # Exemplo:
        frames = []
        sprite_info = SPRITES[self.state] # Precisa saber qual sprite sheet usar
        sprite_sheet = sprite_info["file"] # Assumindo que 'file' é uma Surface
        for i in range(frame_count):
            x = i * width
            frame = sprite_sheet.subsurface(pygame.Rect(x, 0, width, height))
            # Escala consistente
            target_width = 50
            target_height = 50
            frame = pygame.transform.scale(frame, (target_width, target_height))
            frames.append(frame)
        return frames

    def receber_dano(self, dano):
        tempo_atual = pygame.time.get_ticks()
        # Simplificar condição: só recebe dano se não estiver invulnerável
        if not self.invulneravel:
            self.vida_atual -= dano
            self.vida_atual = max(self.vida_atual, 0) # Garante que não fique negativo
            self.invulneravel = True
            self.ultimo_dano = tempo_atual
            print(f"Recebeu {dano} de dano. Vida: {self.vida_atual}") # Log

    def recuperar_vida(self):
        if self.curas_restantes > 0 and self.vida_atual < self.vida_maxima:
            cura = 2 # Quantidade de cura
            self.vida_atual += cura
            self.vida_atual = min(self.vida_atual, self.vida_maxima) # Garante que não ultrapasse o máximo
            self.curas_restantes -= 1
            print(f"Curou {cura}. Vida: {self.vida_atual}. Curas restantes: {self.curas_restantes}") # Log
            return True
        print("Não foi possível curar.") # Log
        return False

    def iniciar_dash(self):
        tempo_atual = pygame.time.get_ticks()
        # Verificar cooldown e se não está no meio de um ataque/outra ação impeditiva
        if not self.dash_ativo and not self.is_attacking and tempo_atual - self.ultimo_dash_time > self.dash_cooldown_duration:
            # Definir estado para DASH antes de carregar sprites
            previous_state = self.state
            self.state = DASH
            self.load_sprites()
            if not self.frames: # Verifica se o carregamento falhou
                 print("Erro ao carregar sprites de Dash. Abortando dash.")
                 self.state = previous_state # Reverte para o estado anterior
                 self.load_sprites() # Recarrega sprites do estado anterior
                 return

            self.dash_ativo = True
            self.dash_timer = self.dash_duracao
            self.ultimo_dash_time = tempo_atual
            # Usar self.direcao_dash que é atualizado no movimento normal
            self.vel_x = self.direcao_dash * self.velocidade_dash
            self.vel_y = 0 # Dash geralmente ignora gravidade temporariamente
            self.pode_dash = False # Impede dash imediatamente após este terminar (será resetado)
            print("Iniciou Dash")

    def atacar(self,inimigos):
        current_time = pygame.time.get_ticks()
        # Não atacar se já estiver atacando, dando dash ou em outra ação
        if self.is_attacking or self.dash_ativo:
             return

        # Limpar sequência se o intervalo for muito grande
        if current_time - self.last_attack_time > self.MAX_ATTACK_INTERVAL:
            self.attack_sequence.clear()
            print("Resetou sequência de ataque (intervalo)")

        # Adicionar próximo ataque à sequência
        if len(self.attack_sequence) < 3:
            next_attack_state = f"attack{len(self.attack_sequence) + 1}"
            if next_attack_state in SPRITES: # Verificar se o sprite existe
                self.attack_sequence.append(next_attack_state)
                self.last_attack_time = current_time
                self.state = self.attack_sequence[-1]
                self.frame_index = 0
                self.is_attacking = True # Marcar que está atacando
                self.load_sprites() # Carregar sprites do ataque
                print(f"Iniciou ataque: {self.state}")
            for inimigo in inimigos:
                if self.rect.colliderect(inimigo.rect):
                    inimigo.receber_dano(2, atacando=True)
            else:
                 print(f"Sprite para estado {next_attack_state} não encontrado.")
        else:
            print("Sequência máxima de ataque atingida.")


    def atualizar(self, inimigos):
        tempo_atual = pygame.time.get_ticks()
        teclas = pygame.key.get_pressed()
        previous_state = self.state # Guardar estado para detecção de mudança

        # --- Resetar flags no início de cada atualização ---
        self.on_ramp = False # Resetar flag de rampa
        if self.sinking_in_lava:
            # 1. Verificar Timer de Morte
            if tempo_atual - self.lava_sink_start_time > self.LAVA_SINK_DURATION:
                if self.vida_atual > 0: # Só mata uma vez
                    self.vida_atual = 0
                    self.morreu_queimado = True
                    self.sinking_in_lava = False # Para de afundar logicamente
                    print("Jogador morreu na lava (timer expirou)")
                # Não precisa retornar aqui, a checagem de vida <= 0 no main fará o resto

            # 2. Se ainda não morreu, continuar afundando
            else:
                self.vel_x = 0 # Garante que não se mova para os lados
                self.vel_y = self.LAVA_SINK_SPEED # Força velocidade para baixo
                self.no_chao = False # Garante que não está "no chão"
                self.on_ramp = False # Garante que não está na rampa

                # Aplicar movimento vertical (afundando)
                self.collision_rect.y += self.vel_y

                # Atualizar posição principal do rect visual
                self.rect.midbottom = self.collision_rect.midbottom

                # Atualizar animação (se houver uma específica) ou apenas a imagem
                self.update_animation() # Continua animando o estado atual (ou poderia forçar um estado)

                # Opcional: Aplicar efeito visual (tint)
                try:
                    # Criar uma cópia para não afetar o cache/frames originais
                    tinted_image = self.frames[self.frame_index].copy()
                    # Aplicar uma cor vermelha/laranja semi-transparente
                    # A intensidade do alfa (último valor) controla o quão forte é o tint
                    alpha = min(200, 50 + int((tempo_atual - self.lava_sink_start_time) / self.LAVA_SINK_DURATION * 150)) # Aumenta alpha
                    tint_surface = pygame.Surface(tinted_image.get_size(), pygame.SRCALPHA)
                    tint_surface.fill((255, 60, 0, alpha)) # Laranja/vermelho, alpha variável
                    tinted_image.blit(tint_surface, (0, 0))
                    self.image = tinted_image # Atualiza a imagem a ser desenhada
                    # Flip se necessário
                    if not self.facing_right:
                        self.image = pygame.transform.flip(self.image, True, False)
                except IndexError:
                     print(f"AVISO: Índice de frame {self.frame_index} inválido ao tentar aplicar tint de lava.")
                     # Usar a imagem base sem tint neste caso
                     self.image = self.frames[0].copy() if self.frames else self._create_fallback_surface()
                     if not self.facing_right:
                         self.image = pygame.transform.flip(self.image, True, False)
                except Exception as e:
                     print(f"Erro inesperado ao aplicar tint de lava: {e}")


                # Pular o resto da lógica de atualização normal
                return        

        # --- Lógica de Estados e Input ---
        if self.is_attacking:
            # Animação de ataque continua até o fim
            # A transição para IDLE será feita em update_animation ou aqui
            if self.frame_index >= len(self.frames) - 1: # Chegou ao último frame
                 # Verificar se há próximo ataque na sequência e se o input foi rápido o suficiente
                 # (Essa lógica de combo pode precisar ser mais sofisticada)
                 # Por agora, simplesmente volta para IDLE ao final da animação
                 self.is_attacking = False
                 self.attack_sequence.clear() # Limpa a sequência atual
                 self.state = IDLE
                 self.load_sprites()
                 # Não retorna aqui, permite que o movimento seja aplicado mesmo no último frame do ataque

        elif self.dash_ativo:
            self.dash_timer -= 1
            if self.dash_timer <= 0:
                self.dash_ativo = False
                self.vel_x = 0 # Parar movimento horizontal do dash
                self.pode_dash = True # Permitir dash novamente após cooldown (controlado em iniciar_dash)
                self.state = IDLE # Voltar para idle ou estado apropriado
                self.load_sprites()
            # Durante o dash, geralmente não se aceita outro input de movimento/ação
            # A velocidade (vel_x, vel_y) já foi definida em iniciar_dash

        else: # Se não está atacando nem dando dash
            # Movimento Horizontal
            self.vel_x = 0
            current_state = IDLE # Estado padrão se nenhuma tecla de movimento for pressionada
            if teclas[pygame.K_LEFT] or teclas[pygame.K_a]:
                self.vel_x = -self.velocidade
                self.direcao_dash = -1 # Guarda última direção para o dash
                self.facing_right = False
                current_state = WALK
            if teclas[pygame.K_RIGHT] or teclas[pygame.K_d]:
                self.vel_x = self.velocidade
                self.direcao_dash = 1
                self.facing_right = True
                current_state = WALK # Sobrescreve se ambas as teclas forem pressionadas (direita tem prioridade)

            # Pulo
            if (teclas[pygame.K_SPACE] or teclas[pygame.K_w]) and not self.pulo_pressionado:
                 if self.pulos_restantes > 0:
                     self.vel_y = self.forca_pulo
                     self.pulos_restantes -= 1
                     self.no_chao = False # Saiu do chão
                     self.pulo_pressionado = True # Previne pulos múltiplos com uma só pressionada
                     # Opcional: Mudar estado para PULO
                     # current_state = PULO # Descomentar se tiver animação de pulo
                     print(f"Pulou! Pulos restantes: {self.pulos_restantes}")
            elif not (teclas[pygame.K_SPACE] or teclas[pygame.K_w]):
                 self.pulo_pressionado = False # Reseta quando a tecla é solta

            # Aplicar Gravidade (apenas se não estiver no chão ou em rampa estável)
            # A gravidade é aplicada *antes* da colisão vertical
            if not self.no_chao:
                 self.vel_y += self.gravidade
                 # Limitar velocidade de queda máxima (opcional)
                 max_fall_speed = 15
                 if self.vel_y > max_fall_speed:
                     self.vel_y = max_fall_speed


            # Atualizar Estado (se mudou e não está atacando/dando dash)
            if current_state != self.state and not self.is_attacking and not self.dash_ativo:
                 # Adicionar verificação para estado de pulo/queda aqui se necessário
                 if not self.no_chao and current_state == IDLE and PULO in SPRITES: # Se está no ar e parado, usar PULO?
                     self.state = PULO
                 else:
                     self.state = current_state
                 self.load_sprites()
                 self.frame_index = 0 # Reinicia animação do novo estado


        # --- Movimentação e Colisão ---
        # Usar self.collision_rect para física

        # Movimentação e Colisão Horizontal
        self.collision_rect.x += self.vel_x
        colidiu_horizontal = self.check_collision(self.colisao_rects, 'horizontal')
        if colidiu_horizontal:
            if self.vel_x > 0: # Movendo para a direita
                self.collision_rect.right = colidiu_horizontal.left
            elif self.vel_x < 0: # Movendo para a esquerda
                self.collision_rect.left = colidiu_horizontal.right
            # self.vel_x = 0 # Parar movimento se colidir com parede? Opcional.

        # Movimentação e Colisão Vertical (Chão Normal)
        self.collision_rect.y += self.vel_y
        self.no_chao = False # Assume que está no ar até que colisão prove o contrário
        colidiu_vertical = self.check_collision(self.colisao_rects, 'vertical')
        if colidiu_vertical:
            if self.vel_y > 0: # Movendo para baixo (caindo)
                self.collision_rect.bottom = colidiu_vertical.top
                self.no_chao = True
                self.pulos_restantes = 2 # Resetar pulos ao tocar o chão
            elif self.vel_y < 0: # Movendo para cima (pulando)
                self.collision_rect.top = colidiu_vertical.bottom
            self.vel_y = 0 # Parar movimento vertical ao colidir

        # --- NOVO: Lógica de Colisão com Rampas ---
        # Deve ser chamada *depois* da colisão vertical normal
        # para que a rampa possa substituir o estado 'no_chao' se necessário.
        self.handle_ramp_collision()
        # --- FIM NOVO ---


        # --- Atualizar posição principal do rect baseado no collision_rect ---
        self.rect.midbottom = self.collision_rect.midbottom
        
        
        if self.check_buraco_collision():
            # Morte já tratada dentro da função check_buraco_collision
            # Não precisa fazer mais nada aqui, a checagem em main.py.run() pegará vida <= 0
             pass
        elif self.check_lava_collision(): # Usar elif para evitar checar lava se já caiu no buraco
            # Morte já tratada dentro da função check_lava_collision
             pass
        # --- Verificações Finais ---
        # Condição de queda para fora do mapa (exemplo)
        # if self.rect.top > ALTURA + 200: # Usar ALTURA do mapa, não da tela
        #     self.vida_atual = 0 # Ou teletransportar para ponto seguro

        # Colisão com inimigos (usar collision_rect)
        inimigos_atingidos = pygame.sprite.spritecollide(self, inimigos, False, collided=lambda s1, s2: s1.collision_rect.colliderect(s2.rect)) # Assume inimigo usa self.rect
        for inimigo in inimigos_atingidos:
            self.receber_dano(1) # Ou dano específico do inimigo

        # Atualizar estado de invulnerabilidade
        if self.invulneravel and tempo_atual - self.ultimo_dano > self.tempo_invulneravel:
            self.invulneravel = False
            # print("Jogador não está mais invulnerável")


    # --- NOVO: Função para checar colisão horizontal/vertical ---
    def check_collision(self, rect_list, direction):
        """Verifica colisão do self.collision_rect com uma lista de retângulos."""
        for rect in rect_list:
            if self.collision_rect.colliderect(rect):
                 # Retorna o rect com o qual colidiu para resolução
                 return rect
        return None # Nenhuma colisão

        # --- NOVO: Função para lidar com colisão de Rampa ---
    def handle_ramp_collision(self):
        """Verifica e ajusta a posição do jogador em rampas com suavização e base melhorada."""
        player_center_x = self.collision_rect.centerx
        player_bottom = self.collision_rect.bottom

        collided_ramp = None
        target_y = player_bottom  # Y alvo inicial é a posição atual

        lerp_factor = 0.5  # Fator de suavização para interpolação linear
        base_offset = 24  # Ajuste fino para evitar "quadradão" na base

        # --- RampaParaEsquerda ( \ ) ---
        for rampa in self.rampas_esquerda:
            if self.collision_rect.colliderect(rampa):
                relative_x = max(0, min(player_center_x - rampa.left, rampa.width))
                altura_na_rampa = ((rampa.width - relative_x) / rampa.width) * rampa.height + base_offset
                y_rampa_no_x = rampa.bottom - altura_na_rampa

                if player_bottom >= y_rampa_no_x - 1 and rampa.left <= player_center_x <= rampa.right:
                    if collided_ramp is None or y_rampa_no_x < target_y:
                        target_y = y_rampa_no_x
                        collided_ramp = rampa
                        self.on_ramp = True

        # --- RampaParaDireita ( / ) ---
        for rampa in self.rampas_direita:
            if self.collision_rect.colliderect(rampa):
                relative_x = max(0, min(player_center_x - rampa.left, rampa.width))
                altura_na_rampa = (relative_x / rampa.width) * rampa.height + base_offset
                y_rampa_no_x = rampa.bottom - altura_na_rampa

                if player_bottom >= y_rampa_no_x - 1 and rampa.left <= player_center_x <= rampa.right:
                    if collided_ramp is None or y_rampa_no_x < target_y:
                        target_y = y_rampa_no_x
                        collided_ramp = rampa
                        self.on_ramp = True

        # --- Aplicação do Ajuste Suave ---
        if collided_ramp:
            if self.vel_y >= 0:
                self.collision_rect.bottom += (target_y - self.collision_rect.bottom) * lerp_factor  # Suavização
                self.vel_y = 0
                self.no_chao = True
                self.pulos_restantes = 2


    def update_animation(self):
        # Atualizar animação baseado no estado atual
        if not self.frames: # Se não há frames carregados, não faz nada
            return

        self.animation_timer += 1
        if self.animation_timer >= self.animation_speed: # Usar animation_speed
            self.animation_timer = 0
            self.frame_index = (self.frame_index + 1) % len(self.frames)

            # Lógica específica de fim de animação (ex: ataque)
            if self.is_attacking and self.frame_index == 0: # Se a animação de ataque completou o ciclo
                 # A lógica de voltar para IDLE já está em atualizar()
                 pass # Ou poderia ser movida para cá

            self.image = self.frames[self.frame_index]
            # Virar a imagem se necessário (Flip)
            if not self.facing_right:
                self.image = pygame.transform.flip(self.image, True, False)

            # Atualizar máscara se estiver usando colisão por máscara
            # self.mask = pygame.mask.from_surface(self.image)


    def draw(self, surface, position):
        # Esta função não é usada no loop principal (main.py),
        # o desenho é feito diretamente em main.py.
        # Pode ser removida ou usada se refatorar o desenho.
        surface.blit(self.image, position)


    # --- FUNÇÕES DE COLISÃO ANTIGAS (Substituídas por check_collision e handle_ramp_collision) ---
    # Manter estas se precisar da lógica específica de escalar dentro delas,
    # mas a abordagem atual com check_collision é mais limpa se o zoom for
    # gerenciado principalmente na câmera/renderização.
    # Se precisar delas, ajuste para usar self.collision_rect e remova a escala interna.

    # def colisao_horizontal(self):
    #     """Verifica colisão horizontal com os retângulos do mapa."""
    #     # ... (código original com zoom) ...
    #     # RECOMENDAÇÃO: Adaptar para usar self.collision_rect e rect_list sem zoom interno
    #     for rect in self.colisao_rects: # Apenas colisao_rects (chão/paredes)
    #         if self.collision_rect.colliderect(rect):
    #              return rect # Retorna o rect original (sem zoom)
    #     return None

    # def colisao_vertical(self):
    #     """Verifica colisão vertical com os retângulos do mapa."""
    #     # ... (código original com zoom) ...
    #      # RECOMENDAÇÃO: Adaptar para usar self.collision_rect e rect_list sem zoom interno
    #     for rect in self.colisao_rects: # Apenas colisao_rects (chão/paredes)
    #         if self.collision_rect.colliderect(rect):
    #              return rect # Retorna o rect original (sem zoom)
    #     return None
    # --- FIM FUNÇÕES ANTIGAS ---


    def handle_espinho_colisions(self, espinho_maior_layer, espinho_menor_layer):
        # --- REVISAR USO DO ZOOM AQUI ---
        # Se a colisão com espinhos deve considerar zoom, mantenha.
        # Se não (colisão no mundo não escalado), remova a multiplicação por zoom_level.
        # A abordagem atual usa coordenadas escaladas, o que pode ser inconsistente
        # se o resto da física usa coordenadas não escaladas.
        # VAMOS ASSUMIR QUE A FÍSICA/COLISÃO OCORRE NO MUNDO *NÃO ESCALADO*
        # E O ZOOM É APENAS PARA RENDERIZAÇÃO.

        tempo_atual = pygame.time.get_ticks()

        # Usar self.collision_rect para a colisão (coordenadas não escaladas)
        jogador_rect_colisao = self.collision_rect

        # Colisão com Espinho_Maior
        if espinho_maior_layer is not None and hasattr(espinho_maior_layer, 'tiles'):
            tile_w = self.tmx_data.tilewidth
            tile_h = self.tmx_data.tileheight
            for x, y, gid in espinho_maior_layer:
                if gid != 0:
                    # Coordenadas não escaladas do tile
                    tile_rect = pygame.Rect(x * tile_w, y * tile_h, tile_w, tile_h)
                    if jogador_rect_colisao.colliderect(tile_rect):
                        # Adicionar um pequeno delay antes de permitir dano novamente
                        if tempo_atual - self.ultimo_dano_espinhos > self.intervalo_dano_espinhos:
                            self.receber_dano(1) # Dano do espinho
                            self.ultimo_dano_espinhos = tempo_atual # Reseta timer específico do espinho
                            # print('Dano Espinho Maior') # Log
                            # Opcional: Empurrar o jogador para trás/cima ao tocar espinho
                            # self.vel_y = -5 # Exemplo: pequeno impulso para cima
                            # break # Sair do loop se já tomou dano nesta camada

        # Colisão com Espinho_Menor (mesma lógica)
        if espinho_menor_layer is not None and hasattr(espinho_menor_layer, 'tiles'):
            tile_w = self.tmx_data.tilewidth
            tile_h = self.tmx_data.tileheight
            for x, y, gid in espinho_menor_layer:
                if gid != 0:
                    tile_rect = pygame.Rect(x * tile_w, y * tile_h, tile_w, tile_h)
                    if jogador_rect_colisao.colliderect(tile_rect):
                        if tempo_atual - self.ultimo_dano_espinhos > self.intervalo_dano_espinhos:
                            self.receber_dano(1)
                            self.ultimo_dano_espinhos = tempo_atual
                            # print('Dano Espinho Menor')
                            # self.vel_y = -5
                            # break

# --- END OF FILE player.py ---