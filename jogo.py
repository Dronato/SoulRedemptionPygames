# --- START OF FILE main.py ---

import pygame
import sys
from player import Jogador
import inimigo
from inimigo import Inimigo1mp1, Inimigo1mp2
from map_loader import carregar_mapa, desenhar_mapa, criar_mapa_rects,criar_objetos_retangulos # Manter criar_mapa_rects

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

def exibir_mensagem_buraco():
    fonte = pygame.font.Font(None, 74)
    texto = fonte.render("Você caiu no buraco!! Perdeu", True, VERMELHO) # Mensagem e cor diferentes
    texto_rect = texto.get_rect(center=(LARGURA // 2, ALTURA // 2))
    tela.blit(texto, texto_rect)
    pygame.display.flip()
    pygame.time.wait(2500) # Talvez um pouco mais de tempo
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
altura_mapa = tmx_data.height * tmx_data.tileheight * 1.5 # Atenção: este 1.5 parece estranho, pode causar problemas de limite de câmera/mundo

# Definir o fator de zoom
zoom_level = 2.0  # Ajuste este valor para aumentar ou diminuir o zoom


# Criar retângulos de colisão a partir da camada "Chão"
colisao_rects = criar_mapa_rects(tmx_data, "Chão")

# --- NOVO: Criar retângulos de colisão para as rampas ---
try:
    rampas_esquerda_rects = criar_mapa_rects(tmx_data, "RampaParaEsquerda")
except ValueError:
    print("Aviso: Camada 'RampaParaEsquerda' não encontrada no mapa.")
    rampas_esquerda_rects = []
try:
    rampas_direita_rects = criar_mapa_rects(tmx_data, "RampaParaDireita")
except ValueError:
    print("Aviso: Camada 'RampaParaDireita' não encontrada no mapa.")
    rampas_direita_rects = []
# --- FIM NOVO ---
buraco_rects = criar_objetos_retangulos(tmx_data, "Buraco")

# Criar paredes de colisão (Manter como está, se necessário)
espessura_parede = 1
paredes_colisao = [
    pygame.Rect(0, 0, largura_mapa, espessura_parede),
    pygame.Rect(0, altura_mapa - espessura_parede, largura_mapa, espessura_parede),
    pygame.Rect(0, espessura_parede, espessura_parede, altura_mapa - 2 * espessura_parede),
    pygame.Rect(largura_mapa - espessura_parede, espessura_parede, espessura_parede, altura_mapa - 2 * espessura_parede)
]
colisao_rects.extend(paredes_colisao) # Adiciona paredes apenas aos colisores 'normais'

# --- ALTERADO: Passar os rects das rampas para o Jogador ---
jogador = Jogador(x=100, y=214,
                  colisao_rects=colisao_rects,
                  rampas_esquerda_rects=rampas_esquerda_rects, # Novo argumento
                  rampas_direita_rects=rampas_direita_rects,   # Novo argumento
                  buraco_rects=buraco_rects,tmx_data=tmx_data,
                  zoom_level=zoom_level)
# --- FIM ALTERADO ---

todos_sprites = pygame.sprite.Group(jogador)

mapas = {
    "mapa1": {"inimigos": [inimigo.Inimigo1mp1(x=2950, y=0,jogador=jogador, colisao_rects= colisao_rects, tmx_data=tmx_data,largura_mapa = largura_mapa, altura_mapa= altura_mapa), inimigo.Inimigo1mp2(x=4150, y=214,jogador=jogador, colisao_rects= colisao_rects, tmx_data=None,largura_mapa = largura_mapa, altura_mapa= altura_mapa)]}
}
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
mensagem = "teste" # Esta variável parece não ser usada para o popup, verificar lógica


# Modifique a função desenhar_mapa para aplicar o zoom
def desenhar_mapa_com_zoom(tela, tmx_data, deslocamento_camera_x, deslocamento_camera_y, zoom_level):
    # --- ALTERADO: Adicionar camadas de rampa ao desenho ---
    camadas_para_desenhar = [
        "Background",
        "Fundo",
        "Chão",
        "RampaParaEsquerda", # Adicionado
        "RampaParaDireita",  # Adicionado
        "Espinho_Maior",
        "Espinho_Menor"
    ]
    # --- FIM ALTERADO ---

    for nome_camada in camadas_para_desenhar:
        try:
            layer = tmx_data.get_layer_by_name(nome_camada)
        except ValueError:
            # Aviso já é impresso ao carregar rects, não precisa repetir
            # print(f"Aviso: Camada '{nome_camada}' não encontrada no mapa durante desenho.")
            continue

        if hasattr(layer, 'tiles'):  # Camadas de tiles
            for x, y, gid in layer:
                tile = tmx_data.get_tile_image_by_gid(gid)
                if tile:
                    largura_tile = int(tmx_data.tilewidth * zoom_level)
                    altura_tile = int(tmx_data.tileheight * zoom_level)
                    # Otimização: Escalar apenas uma vez se o tile for reutilizado
                    # tile_cache = {} # Implementar cache se necessário para performance
                    # if gid not in tile_cache:
                    #    tile_cache[gid] = pygame.transform.scale(tile, (largura_tile, altura_tile))
                    # tile_scaled = tile_cache[gid]
                    tile_scaled = pygame.transform.scale(tile, (largura_tile, altura_tile))


                    pos_x = x * tmx_data.tilewidth * zoom_level + deslocamento_camera_x
                    pos_y = y * tmx_data.tileheight * zoom_level + deslocamento_camera_y

                    tela.blit(tile_scaled, (pos_x, pos_y))

        # Lógica para ImageLayer e outras mantida como estava...
        elif isinstance(layer, pygame.Surface):
            largura_layer = int(layer.get_width() * zoom_level)
            altura_layer = int(layer.get_height() * zoom_level)
            layer_scaled = pygame.transform.scale(layer, (largura_layer, altura_layer))
            tela.blit(layer_scaled, (deslocamento_camera_x, deslocamento_camera_y))
        elif hasattr(layer, 'image'):
            largura_image = int(layer.image.get_width() * zoom_level)
            altura_image = int(layer.image.get_height() * zoom_level)
            image_scaled = pygame.transform.scale(layer.image, (largura_image, altura_image))
            offset_x = getattr(layer, 'offsetx', 0) * zoom_level
            offset_y = getattr(layer, 'offsety', 0) * zoom_level
            tela.blit(image_scaled, (offset_x + deslocamento_camera_x, offset_y + deslocamento_camera_y))


# Esta função não parece ser usada, mas a deixo caso seja necessária em outro lugar.
# def criar_mapa_rects_com_zoom(tmx_data, layer_name, zoom_level):
#     """Cria retângulos de colisão a partir de uma camada específica do mapa, aplicando o zoom."""
#     rects = []
#     layer = tmx_data.get_layer_by_name(layer_name)
#     for x, y, gid in layer:
#         if gid != 0:
#             rect = pygame.Rect(x * tmx_data.tilewidth * zoom_level, y * tmx_data.tileheight * zoom_level,
#                                 tmx_data.tilewidth * zoom_level, tmx_data.tileheight * zoom_level)
#             rects.append(rect)
#     return rects

# Carregamento de SPRITES mantido como estava...
# (O código original tinha um erro aqui, carregando os arquivos de imagem duas vezes,
# mas como instruído, não alterarei partes não relacionadas à funcionalidade de rampa)
SPRITES = {
    "enemyidle": {"file": "img/mapa1/inimigo1/inimigo1_andando.png", "frames": 3, "width": 445, "height": 394},
    "idle": {"file": "img/prota/parada.png", "frames": 6, "width": 176, "height": 148},
    "walk": {"file": "img/prota/andando.png", "frames": 10, "width": 198, "height": 144},
    "pulo": {"file": "img/prota/pulo.png", "frames": 15, "width": 256, "height": 256},
    "dash": {"file": "img/prota/dash.png", "frames": 5, "width": 214, "height": 144},
    "attack1": {"file": "img/prota/attack1.png", "frames": 6, "width": 339, "height": 402},
    "attack2": {"file": "img/prota/attack2.png", "frames": 7, "width": 339, "height": 402},
    "attack3": {"file": "img/prota/attack3.png", "frames": 8, "width": 339, "height": 402}
}
# O loop de carregamento com convert_alpha() estava aqui no original, manter se necessário
# for key, sprite_info in SPRITES.items():
    # sprite_info["file"] = pygame.image.load(sprite_info["file"]).convert_alpha() # CUIDADO: Isso sobrescreve o caminho do arquivo pela superfície carregada

executando = True
while executando:
    relogio.tick(FPS)
    tempo_agora = pygame.time.get_ticks() # Para popup

    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            executando = False
        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_ESCAPE: # Adicionar uma forma de sair
                 executando = False
            if evento.key == pygame.K_e:
                if not jogador.recuperar_vida():
                    mostrar_popup = True
                    # Usar a variável correta para a mensagem
                    popup_mensagem = "Você não pode curar mais!"
                    popup_timer = tempo_agora + popup_duracao # Definir tempo de expiração
                else:
                     # Opcional: Mostrar mensagem de sucesso
                     mostrar_popup = True
                     popup_mensagem = "Vida recuperada!"
                     popup_timer = tempo_agora + popup_duracao
            if evento.key == pygame.K_LSHIFT or evento.key == pygame.K_RSHIFT:
                jogador.iniciar_dash()
            if evento.key == pygame.K_z:
                jogador.atacar([*mapas[mapa_atual]["inimigos"]]) # Manter lógica de ataque

    # --- Ordem de Atualização e Colisão ---
    # 1. Atualizar estado e intenção de movimento do jogador (baseado em input)
    #    (A lógica de input está dentro de jogador.atualizar no seu código)

    # 2. Atualizar posição e aplicar colisões (incluindo rampas)
    jogador.atualizar(inimigos) # Passar inimigos continua necessário para dano

    # 3. Atualizar animação do jogador
    jogador.update_animation()

    # 4. Atualizar inimigos
    for inimigo_atual in inimigos:
        if isinstance(inimigo_atual, Inimigo1mp2):
            inimigo_atual.update()
            inimigo_atual.detectar_jogador()
        else:
            inimigo_atual.update()

    # 5. Colisão com espinhos (após movimento finalizado)
    espinho_maior_layer = tmx_data.get_layer_by_name("Espinho_Maior")
    espinho_menor_layer = tmx_data.get_layer_by_name("Espinho_Menor")
    jogador.handle_espinho_colisions(espinho_maior_layer, espinho_menor_layer)
    # --- Fim Ordem ---


    # --- Desenho ---
    tela.fill((0, 0, 0))

    # Ajuste da câmera (mantido como estava)
    deslocamento_camera_x = LARGURA // 2 - jogador.rect.centerx * zoom_level
    deslocamento_camera_y = ALTURA // 1.2 - jogador.rect.centery * zoom_level

    # Restringir a câmera (mantido como estava)
    # Atenção ao altura_mapa * 1.5 - recalcular limites se necessário
    largura_mapa_escalada = largura_mapa * zoom_level
    # altura_mapa_escalada = altura_mapa * zoom_level # Usar altura_mapa original para cálculo
    altura_mapa_escalada = (tmx_data.height * tmx_data.tileheight) * zoom_level # Cálculo mais preciso

    deslocamento_camera_x = min(deslocamento_camera_x, 0)
    deslocamento_camera_x = max(deslocamento_camera_x, LARGURA - largura_mapa_escalada)
    deslocamento_camera_y = min(deslocamento_camera_y, 0)
    deslocamento_camera_y = max(deslocamento_camera_y, ALTURA - altura_mapa_escalada)


    # Desenhar mapa com zoom
    desenhar_mapa_com_zoom(tela, tmx_data, deslocamento_camera_x, deslocamento_camera_y, zoom_level)

    # Checar condição de derrota
    if jogador.vida_atual <= 0:
        # Verifica SE a morte foi por queda no buraco usando a flag
        if hasattr(jogador, 'caiu_no_buraco') and jogador.caiu_no_buraco:
            exibir_mensagem_buraco() # Mostra mensagem específica
        else:
            exibir_mensagem_derrota()

    # Desenhar inimigos (aplicando zoom e câmera)
    for inimigo_sprite in inimigos: # Renomear variável local para evitar conflito com módulo 'inimigo'
        # Escalar imagem do inimigo
        img_inimigo_scaled = pygame.transform.scale(inimigo_sprite.image,
                                                    (int(inimigo_sprite.rect.width * zoom_level), # Usar rect.width/height para escala
                                                     int(inimigo_sprite.rect.height * zoom_level)))
        # Calcular posição na tela
        pos_inimigo_x = inimigo_sprite.rect.x * zoom_level + deslocamento_camera_x
        pos_inimigo_y = inimigo_sprite.rect.y * zoom_level + deslocamento_camera_y
        tela.blit(img_inimigo_scaled, (pos_inimigo_x, pos_inimigo_y))


    # Desenhar jogador (aplicando zoom e câmera)
    # Escalar imagem do jogador
    img_jogador_scaled = pygame.transform.scale(jogador.image,
                                                (int(jogador.rect.width * zoom_level), # Usar rect.width/height para escala
                                                 int(jogador.rect.height * zoom_level)))
     # Calcular posição na tela
    pos_jogador_x = jogador.rect.x * zoom_level + deslocamento_camera_x
    pos_jogador_y = jogador.rect.y * zoom_level + deslocamento_camera_y
    tela.blit(img_jogador_scaled, (pos_jogador_x, pos_jogador_y))


    # Desenhar UI (corações, poções) - não afetados por zoom/câmera
    desenhar_coracoes(tela, jogador)
    desenhar_pocoes(tela, jogador)

    # Exibir popup
    if mostrar_popup and tempo_agora < popup_timer:
        exibir_popup_cura(tela, popup_mensagem) # Passar a mensagem correta
    elif mostrar_popup and tempo_agora >= popup_timer:
        mostrar_popup = False # Esconder popup após o tempo

    pygame.display.flip()

pygame.quit()
sys.exit() # Adicionado para garantir saída limpa

# --- END OF FILE main.py ---