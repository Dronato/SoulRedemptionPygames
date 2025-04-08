import pygame
from pytmx.util_pygame import load_pygame
import os
import pytmx

# Inicialização
pygame.init()
tela = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Mapa com Player")
relogio = pygame.time.Clock()

# Carrega o mapa
def carregar_mapa(caminho_mapa):
    return load_pygame(caminho_mapa)

# Função de desenho com camadas organizadas
def desenhar_mapa(tela, tmx_data, offset_x=0, offset_y=0):
    for layer in tmx_data.layers:
        if isinstance(layer, pytmx.TiledImageLayer):
            if layer.image:
                img_offset_x = getattr(layer, 'offsetx', 0)
                img_offset_y = getattr(layer, 'offsety', 0)
                tela.blit(layer.image, (img_offset_x + offset_x, img_offset_y + offset_y))

        elif isinstance(layer, pytmx.TiledTileLayer):
            for x, y, gid in layer:
                tile = tmx_data.get_tile_image_by_gid(gid)
                if tile:
                    tela.blit(tile, (x * tmx_data.tilewidth + offset_x,
                                     y * tmx_data.tileheight + offset_y))

        elif isinstance(layer, pytmx.TiledObjectGroup):
            for obj in layer:
                pygame.draw.rect(
                    tela,
                    (255, 0, 0),  # vermelho para debug
                    pygame.Rect(obj.x + offset_x, obj.y + offset_y, obj.width, obj.height),
                    2
                )

# --- Setup ---
base_dir = os.path.dirname(os.path.abspath(__file__))
caminho_mapa = os.path.join(base_dir, "Mapa(2).tmx")
tmx_data = carregar_mapa(caminho_mapa)

# Player
player = pygame.Rect(100, 100, 32, 48)
velocidade = 5

# Loop principal
rodando = True
while rodando:
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            rodando = False

    # Movimento
    teclas = pygame.key.get_pressed()
    if teclas[pygame.K_LEFT]:
        player.x -= velocidade
    if teclas[pygame.K_RIGHT]:
        player.x += velocidade
    if teclas[pygame.K_UP]:
        player.y -= velocidade
    if teclas[pygame.K_DOWN]:
        player.y += velocidade

    # Câmera
    camera_x = player.centerx - tela.get_width() // 2
    camera_y = player.centery - tela.get_height() // 2

    # Desenhar
    tela.fill((0, 0, 0))
    desenhar_mapa(tela, tmx_data, -camera_x, -camera_y)
    pygame.draw.rect(tela, (0, 255, 0), (player.x - camera_x, player.y - camera_y, player.width, player.height))
    pygame.display.flip()
    relogio.tick(60)

pygame.quit()
