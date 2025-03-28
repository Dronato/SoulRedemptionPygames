import pygame
import sys
from player import Jogador
import inimigo
from map_loader import carregar_mapa, desenhar_mapa, criar_mapa_rects

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
    "mapa1": {"inimigos": [inimigo.Inimigo1mp1(300, 500), inimigo.Inimigo1mp1(400, 500)]}
}

# Carregar imagens dos corações
coracao_cheio = pygame.image.load("coracao_cheio.png").convert_alpha()
coracao_vazio = pygame.image.load("coracao_vazio.png").convert_alpha()
coracao_cheio = pygame.transform.scale(coracao_cheio, (40, 40))
coracao_vazio = pygame.transform.scale(coracao_vazio, (40, 40))

# Carregar imagens das poções
pocao_cheia = pygame.image.load("pocao_cheia.png").convert_alpha()
pocao_vazia = pygame.image.load("pocao_vazia.png").convert_alpha()
pocao_cheia = pygame.transform.scale(pocao_cheia, (40, 40))
pocao_vazia = pygame.transform.scale(pocao_vazia, (40, 40))


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
    x, y = LARGURA - 20 - (jogador.curas_maximas * 40) - ((jogador.curas_maximas - 1) * 10), 20  # Calcula a posição inicial no canto direito
    espacamento = 50
    for i in range(jogador.curas_maximas):
        if i < jogador.curas_restantes:
            tela.blit(pocao_cheia, (x + i * espacamento, y))
        else:
            tela.blit(pocao_vazia, (x + i * espacamento, y))


# Função para exibir mensagem de derrota
def exibir_mensagem_derrota():
    fonte = pygame.font.Font(None, 74)
    texto = fonte.render("Você Perdeu!", True, BRANCO)
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


# Carregar o mapa
tmx_data = carregar_mapa("Mapa.tmx")
if not tmx_data:
    sys.exit()

# Calcular os limites do mapa
largura_mapa = tmx_data.width * tmx_data.tilewidth
altura_mapa = tmx_data.height * tmx_data.tileheight * 1.5

# Definir o fator de zoom
zoom_level = 2.0  # Ajuste este valor para aumentar ou diminuir o zoom


# Criar retângulos de colisão a partir da camada "Chão"
colisao_rects = criar_mapa_rects(tmx_data, "Chão")

# Criar paredes de colisão
espessura_parede = 1  # Ajuste conforme necessário
paredes_colisao = [
    pygame.Rect(0, 0, largura_mapa, espessura_parede),  # Parede superior
    pygame.Rect(0, altura_mapa - espessura_parede, largura_mapa, espessura_parede),  # Parede inferior
    pygame.Rect(0, espessura_parede, espessura_parede, altura_mapa - 2 * espessura_parede),  # Parede esquerda
    pygame.Rect(largura_mapa - espessura_parede, espessura_parede, espessura_parede, altura_mapa - 2 * espessura_parede)  # Parede direita
]

# Adicionar as paredes à lista de retângulos de colisão
colisao_rects.extend(paredes_colisao)

# Criar jogador
jogador = Jogador(100, 214, colisao_rects, tmx_data, zoom_level)
todos_sprites = pygame.sprite.Group(jogador)

# Criar inimigos
inimigos = pygame.sprite.Group()
mapa_atual = "mapa1"
inimigos.add(*mapas[mapa_atual]["inimigos"])

deslocamento_camera_x = 0
deslocamento_camera_y = 0
mostrar_popup = False
popup_mensagem = ""
popup_timer = 0
popup_duracao = 1000  # 1 segundo
mensagem = "teste"


# Modifique a função desenhar_mapa para aplicar o zoom
def desenhar_mapa_com_zoom(tela, tmx_data, deslocamento_camera_x, deslocamento_camera_y, zoom_level):
    camadas_para_desenhar = [
        "Background",
        "Fundo",
        "Chão",
        "Espinho_Maior",
        "Espinho_Menor"
    ]

    for nome_camada in camadas_para_desenhar:
        try:
            layer = tmx_data.get_layer_by_name(nome_camada)
        except ValueError:
            print(f"Aviso: Camada '{nome_camada}' não encontrada no mapa.")
            continue

        if hasattr(layer, 'tiles'):  # Camadas de tiles
            for x, y, gid in layer:
                tile = tmx_data.get_tile_image_by_gid(gid)
                if tile:
                    # Escala o tile
                    largura_tile = int(tmx_data.tilewidth * zoom_level)
                    altura_tile = int(tmx_data.tileheight * zoom_level)
                    tile_scaled = pygame.transform.scale(tile, (largura_tile, altura_tile))

                    # Calcula a posição com o deslocamento da câmera
                    pos_x = x * tmx_data.tilewidth * zoom_level + deslocamento_camera_x
                    pos_y = y * tmx_data.tileheight * zoom_level + deslocamento_camera_y

                    tela.blit(tile_scaled, (pos_x, pos_y))

        elif isinstance(layer, pygame.Surface):  # Camadas de imagem
            # Escala a camada de imagem
            largura_layer = int(layer.get_width() * zoom_level)
            altura_layer = int(layer.get_height() * zoom_level)
            layer_scaled = pygame.transform.scale(layer, (largura_layer, altura_layer))
            tela.blit(layer_scaled, (deslocamento_camera_x, deslocamento_camera_y))

        elif hasattr(layer, 'image'):  # Camadas de imagem com atributos de deslocamento
            # Escala a imagem
            largura_image = int(layer.image.get_width() * zoom_level)
            altura_image = int(layer.image.get_height() * zoom_level)
            image_scaled = pygame.transform.scale(layer.image, (largura_image, altura_image))

            offset_x = getattr(layer, 'offsetx', 0) * zoom_level
            offset_y = getattr(layer, 'offsety', 0) * zoom_level

            tela.blit(image_scaled, (offset_x + deslocamento_camera_x, offset_y + deslocamento_camera_y))


def criar_mapa_rects_com_zoom(tmx_data, layer_name, zoom_level):
    """Cria retângulos de colisão a partir de uma camada específica do mapa, aplicando o zoom."""
    rects = []
    layer = tmx_data.get_layer_by_name(layer_name)
    for x, y, gid in layer:
        if gid != 0:  # Assume que gid 0 é espaço vazio
            rect = pygame.Rect(x * tmx_data.tilewidth * zoom_level, y * tmx_data.tileheight * zoom_level,
                                tmx_data.tilewidth * zoom_level, tmx_data.tileheight * zoom_level)
            rects.append(rect)
    return rects

# Carregar as imagens dos sprites do jogador com convert_alpha()
SPRITES = {
    "enemyidle": {"file": "img/mapa1/inimigo1/inimigo1_andando.png", "frames": 3, "width": 445, "height": 394},
    "idle": {"file": "img/prota/parada.png", "frames": 6, "width": 176, "height": 148},
    "walk": {"file": "img/prota/andando.png", "frames": 10, "width": 198, "height": 144},
   # "attack": {"file": "img/prota/dano_spritesheet.png", "frames": 5, "width": 340, "height": 320}, aa
    "pulo": {"file": "img/prota/pulo.png", "frames": 15, "width": 256, "height": 256},
    "dash": {"file": "img/prota/dash.png", "frames": 5, "width": 214, "height": 144},
    "attack1": {"file": "img/prota/attack1.png", "frames": 6, "width": 339, "height": 402},
    "attack2": {"file": "img/prota/attack2.png", "frames": 7, "width": 339, "height": 402},
    "attack3": {"file": "img/prota/attack3.png", "frames": 8, "width": 339, "height": 402}
}

# Percorra o dicionário de sprites e carregue cada imagem com convert_alpha()
for key, sprite_info in SPRITES.items():
    sprite_info["file"] = pygame.image.load(sprite_info["file"]).convert_alpha()

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
            if evento.key == pygame.K_z:
                jogador.atacar()

    # Aplique os Espinhos
    # Obtenha as camadas de espinhos do mapa
    espinho_maior_layer = tmx_data.get_layer_by_name("Espinho_Maior")
    espinho_menor_layer = tmx_data.get_layer_by_name("Espinho_Menor")

    # Passe as camadas para a função handle_espinho_colisions do jogador
    jogador.handle_espinho_colisions(espinho_maior_layer, espinho_menor_layer)

    jogador.atualizar(inimigos)
    jogador.update_animation()
    inimigos.update()
    tela.fill((0, 0, 0))  # Fundo preto

    # Ajuste o deslocamento da câmera para manter o jogador centralizado e abaixar o mapa
    deslocamento_camera_x = LARGURA // 2 - jogador.rect.centerx * zoom_level
    deslocamento_camera_y = ALTURA // 1.2 - jogador.rect.centery * zoom_level  # Adiciona o deslocamento para abaixar o mapa

    # Restringir a câmera aos limites do mapa escalado
    largura_mapa_escalada = largura_mapa * zoom_level
    altura_mapa_escalada = altura_mapa * zoom_level

    deslocamento_camera_x = min(deslocamento_camera_x, 0)
    deslocamento_camera_x = max(deslocamento_camera_x, LARGURA - largura_mapa_escalada)
    deslocamento_camera_y = min(deslocamento_camera_y, 0)
    deslocamento_camera_y = max(deslocamento_camera_y, ALTURA - altura_mapa_escalada)

    # Desenhe o mapa com zoom
    desenhar_mapa_com_zoom(tela, tmx_data, deslocamento_camera_x, deslocamento_camera_y, zoom_level)

    if jogador.vida_atual <= 0:
        exibir_mensagem_derrota()

    for inimigo in inimigos:
        tela.blit(pygame.transform.scale(inimigo.image, (int(inimigo.image.get_width() * zoom_level), int(inimigo.image.get_height() * zoom_level))),
                  (inimigo.rect.x * zoom_level + deslocamento_camera_x, inimigo.rect.y * zoom_level + deslocamento_camera_y))

    tela.blit(pygame.transform.scale(jogador.image, (int(jogador.image.get_width() * zoom_level), int(jogador.image.get_height() * zoom_level))),
              (jogador.rect.x * zoom_level + deslocamento_camera_x, jogador.rect.y * zoom_level + deslocamento_camera_y))

    desenhar_coracoes(tela, jogador)
    desenhar_pocoes(tela, jogador)  # Chama a função para desenhar as poções

    if mostrar_popup and pygame.time.get_ticks() < popup_timer:
        exibir_popup_cura(tela, mensagem)

    pygame.display.flip()

pygame.quit()