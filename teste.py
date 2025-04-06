import pygame
import sys
from map_loader import carregar_mapa, desenhar_mapa

# Inicialização
pygame.init()
largura_tela = 800
altura_tela = 600
tela = pygame.display.set_mode((largura_tela, altura_tela))
pygame.display.set_caption("Visualizador do Mapa2")
clock = pygame.time.Clock()

# Carregar o Mapa2
tmx_data = carregar_mapa("Mapa(2).tmx")
if tmx_data is None:
    print("Erro crítico: Falha ao carregar o Mapa2.")
    pygame.quit()
    sys.exit()

# Variáveis da câmera
camera_x = 0
camera_y = 0
velocidade_camera = 10

# Loop principal
rodando = True
while rodando:
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            rodando = False

    # Controles da câmera
    teclas = pygame.key.get_pressed()
    if teclas[pygame.K_LEFT]:
        camera_x += velocidade_camera
    if teclas[pygame.K_RIGHT]:
        camera_x -= velocidade_camera
    if teclas[pygame.K_UP]:
        camera_y += velocidade_camera
    if teclas[pygame.K_DOWN]:
        camera_y -= velocidade_camera

    tela.fill((0, 0, 0))
    desenhar_mapa(tela, tmx_data, camera_x, camera_y)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
