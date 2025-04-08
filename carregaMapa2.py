import pygame
from teste import carregar_mapa2, desenhar_mapa2  # tudo vem de teste.py

pygame.init()
tela = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
LARGURA, ALTURA = tela.get_size()
clock = pygame.time.Clock()

tmx_data = carregar_mapa2()
camera_x, camera_y = 0, 0

rodando = True
while rodando:
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            rodando = False

    tela.fill((0, 0, 0))


    # Depois o restante do mapa por cima
    desenhar_mapa2(tela, tmx_data, camera_x, camera_y)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
