import pygame
import sys

# Inicializar Pygame
pygame.init()

# Configurações básicas
tela = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
LARGURA, ALTURA = tela.get_size()
FPS = 60
relogio = pygame.time.Clock()

# Cores
TRANSPARENTE = (0, 0, 0, 0)
BRANCO = (255, 255, 255)
AZUL = (0, 0, 255)
VERMELHO = (255, 0, 0)
MARROM = (139, 69, 19)
PRETO = (0, 0, 0)

# Carregar imagens dos corações
coracao_cheio = pygame.image.load("coracao_cheio.png")
coracao_vazio = pygame.image.load("coracao_vazio.png")
coracao_cheio = pygame.transform.scale(coracao_cheio, (40, 40))
coracao_vazio = pygame.transform.scale(coracao_vazio, (40, 40))

# Carregar imagens das poções
pocao_cheia = pygame.image.load("pocao_cheia.png")
pocao_vazia = pygame.image.load("pocao_vazia.png")
pocao_cheia = pygame.transform.scale(pocao_cheia, (40, 40))
pocao_vazia = pygame.transform.scale(pocao_vazia, (40, 40))

# Classe do Jogador
class Jogador(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((40, 60))
        self.image.fill(AZUL)
        self.rect = self.image.get_rect()
        self.rect.center = (LARGURA // 2, ALTURA - 100)

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

    def atualizar(self, plataformas, inimigos):
        teclas = pygame.key.get_pressed()

        if not self.dash_ativo:
            self.vel_x = 0
            if teclas[pygame.K_LEFT] or teclas[pygame.K_a]:
                self.vel_x = -self.velocidade
                self.direcao_dash = -1
            if teclas[pygame.K_RIGHT] or teclas[pygame.K_d]:
                self.vel_x = self.velocidade
                self.direcao_dash = 1

            if teclas[pygame.K_SPACE] or teclas[pygame.K_w]:
                if not self.pulo_pressionado and self.pulos_restantes > 0:
                    self.vel_y = self.forca_pulo
                    self.pulos_restantes -= 1
                    self.pulo_pressionado = True
            else:
                self.pulo_pressionado = False

            self.vel_y += self.gravidade

        if self.dash_ativo:
            self.dash_timer -= 1
            if self.dash_timer <= 0:
                self.dash_ativo = False
                self.pode_dash = True # Permite dash novamente após o término

        self.rect.x += self.vel_x
        for plataforma in plataformas:
            if self.rect.colliderect(plataforma.rect):
                if self.vel_x > 0:
                    self.rect.right = plataforma.rect.left
                elif self.vel_x < 0:
                    self.rect.left = plataforma.rect.right

        self.rect.y += self.vel_y
        self.no_chao = False
        for plataforma in plataformas:
            if self.rect.colliderect(plataforma.rect):
                if self.vel_y > 0:
                    self.rect.bottom = plataforma.rect.top
                    self.vel_y = 0
                    self.no_chao = True
                    self.pulos_restantes = 2
                elif self.vel_y < 0:
                    self.rect.top = plataforma.rect.bottom
                    self.vel_y = 0

        if self.rect.bottom >= ALTURA - 50:
            self.rect.bottom = ALTURA - 50
            self.vel_y = 0
            self.no_chao = True
            self.pulos_restantes = 2

        # Colisão com inimigos
        inimigos_atingidos = pygame.sprite.spritecollide(self, inimigos, False)
        for inimigo in inimigos_atingidos:
            self.receber_dano(1)

# Classe do Inimigo
class Inimigo(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((30, 30))
        self.image.fill(VERMELHO)
        self.rect = self.image.get_rect(topleft=(x, y))
        self.velocidade_x = 3
        self.velocidade_y = 0

    def update(self):
        self.rect.x += self.velocidade_x
        if self.rect.left < 0 or self.rect.right > LARGURA:
            self.velocidade_x *= -1

# Função para desenhar os corações
def desenhar_coracoes(tela, jogador):
    x, y = 20, 20
    espacamento = 50
    for i in range(jogador.vida_maxima):
        if i < jogador.vida_atual:
            tela.blit(coracao_cheio, (x + i * espacamento, y))
        else:
            tela.blit(coracao_vazio, (x + i * espacamento, y))

# Função para desenhar as poções
def desenhar_pocoes(tela, jogador):
    x, y = LARGURA - 20 - (jogador.curas_maximas * 40) - ((jogador.curas_maximas - 1) * 10), 20 # Calcula a posição inicial no canto direito
    espacamento = 50
    for i in range(jogador.curas_maximas):
        if i < jogador.curas_restantes:
            tela.blit(pocao_cheia, (x + i * espacamento, y))
        else:
            tela.blit(pocao_vazia, (x + i * espacamento, y))

# Função para exibir mensagem de derrota
def exibir_mensagem_derrota():
    fonte = pygame.font.Font(None, 74)
    texto = fonte.render("Você Perdeu!", True, (255, 0, 0))
    texto_rect = texto.get_rect(center=(LARGURA // 2, ALTURA // 2))
    tela.blit(texto, texto_rect)
    pygame.display.flip()
    pygame.time.wait(2000)  # Espera 2 segundos
    pygame.quit()
    sys.exit()

# Função para exibir pop-up de cura
def exibir_popup_cura(tela, mensagem):
    fonte = pygame.font.Font(None, 30)
    texto = fonte.render(mensagem, True, BRANCO)
    texto_rect = texto.get_rect(center=(LARGURA // 2, ALTURA - 50))
    pygame.draw.rect(tela, PRETO, texto_rect.inflate(20, 10))
    tela.blit(texto, texto_rect)

# Criar jogador
jogador = Jogador()
todos_sprites = pygame.sprite.Group(jogador)

# Criar plataformas
class Plataforma(pygame.sprite.Sprite):
    def __init__(self, x, y, largura, altura):
        super().__init__()
        self.image = pygame.Surface((largura, altura))
        self.image.fill(MARROM)
        self.rect = self.image.get_rect(topleft=(x, y))

plataformas = pygame.sprite.Group()
dados_plataformas = [(200, 850, 150, 20), (400, 750, 200, 20)]
for x, y, w, h in dados_plataformas:
    plataformas.add(Plataforma(x, y, w, h))

# Criar inimigos
inimigos = pygame.sprite.Group()
inimigos.add(Inimigo(600, 800))
inimigos.add(Inimigo(800, 700))

deslocamento_camera_x = 0
deslocamento_camera_y = 0
mostrar_popup = False
popup_mensagem = ""
popup_timer = 0
popup_duracao = 1000 # 1 segundo
executando = True
while executando:
    relogio.tick(FPS)
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            executando = False
        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_e:
                if not jogador.recuperar_vida():
                    mostrar_popup = True
                    popup_mensagem = "Você não pode curar mais!"
                    popup_timer = pygame.time.get_ticks() + popup_duracao
            if evento.key == pygame.K_LSHIFT or evento.key == pygame.K_RSHIFT:
                jogador.iniciar_dash()

    jogador.atualizar(plataformas, inimigos)
    inimigos.update()

    if jogador.vida_atual <= 0:
        exibir_mensagem_derrota()

    deslocamento_camera_x = LARGURA // 2 - jogador.rect.centerx
    deslocamento_camera_y = ALTURA // 1.3 - jogador.rect.centery

    tela.fill(BRANCO)

    for plataforma in plataformas:
        tela.blit(plataforma.image, (plataforma.rect.x + deslocamento_camera_x, plataforma.rect.y + deslocamento_camera_y))

    for inimigo in inimigos:
        tela.blit(inimigo.image, (inimigo.rect.x + deslocamento_camera_x, inimigo.rect.y + deslocamento_camera_y))

    tela.blit(jogador.image, (jogador.rect.x + deslocamento_camera_x, jogador.rect.y + deslocamento_camera_y))

    desenhar_coracoes(tela, jogador)
    desenhar_pocoes(tela, jogador) # Chama a função para desenhar as poções

    if mostrar_popup and pygame.time.get_ticks() < popup_timer:
        exibir_popup_cura(tela, popup_mensagem)

    pygame.display.flip()

pygame.quit()