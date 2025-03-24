import pygame
import sys
from player import Jogador
import inimigo

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


mapas = {
    "mapa1": {"inimigos": [inimigo.Inimigo1mp1(300, 500),inimigo.Inimigo1mp1(400, 500)], "cenario": "img/mapa1/cenario1.png"}
}


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


# Classe do Inimigo


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
jogador = Jogador(100, 214)
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

mapa_atual = "mapa1"
inimigos.add(*mapas[mapa_atual]["inimigos"])
cenario_atual = pygame.image.load(mapas[mapa_atual]["cenario"])
cenario_atual = pygame.transform.scale(cenario_atual, (LARGURA, ALTURA))


deslocamento_camera_x = 0
deslocamento_camera_y = 0
mostrar_popup = False
popup_mensagem = ""
popup_timer = 0
popup_duracao = 1000 # 1 segundo
executando = True
while executando:
    relogio.tick(FPS)
    tela.blit(cenario_atual,(0,0))
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
    jogador.update_animation()
    inimigos.update()

    if jogador.vida_atual <= 0:
        exibir_mensagem_derrota()

    deslocamento_camera_x = LARGURA // 2 - jogador.rect.centerx
    deslocamento_camera_y = ALTURA // 1.3 - jogador.rect.centery

    

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