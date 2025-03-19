import pygame

# Inicializar Pygame
pygame.init()

# Configurações
LARGURA, ALTURA = 800, 600
tela = pygame.display.set_mode((LARGURA, ALTURA))
relogio = pygame.time.Clock()

# Carregar e redimensionar imagens
img_jogador = pygame.image.load("goku.png").convert_alpha()
img_jogador = pygame.transform.scale(img_jogador, (100, 100))  # Reduzir tamanho

img_inimigo = pygame.image.load("stiti.png").convert_alpha()
img_inimigo = pygame.transform.scale(img_inimigo, (100, 100))  # Reduzir tamanho
2
# Classe do Jogador
class Jogador(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = img_jogador
        self.rect = self.image.get_rect(center=(100, ALTURA // 2))
        self.mask = pygame.mask.from_surface(self.image)  # Criar máscara baseada na imagem

    def update(self):
        teclas = pygame.key.get_pressed()
        if teclas[pygame.K_LEFT]:
            self.rect.x -= 5
        if teclas[pygame.K_RIGHT]:
            self.rect.x += 5
        if teclas[pygame.K_UP]:
            self.rect.y -= 5
        if teclas[pygame.K_DOWN]:
            
            self.rect.y += 5

# Classe do Inimigo
class Inimigo(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = img_inimigo
        self.rect = self.image.get_rect(center=(x, y))
        self.mask = pygame.mask.from_surface(self.image)  # Criar máscara baseada na imagem

# Criar instâncias dos sprites
jogador = Jogador()
inimigo = Inimigo(400, ALTURA // 2)

# Criar grupos de sprites
todos_sprites = pygame.sprite.Group(jogador, inimigo)
inimigos = pygame.sprite.Group(inimigo)

# Loop principal
executando = True
while executando:
    relogio.tick(60)

    # Eventos
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            executando = False

    # Atualizar jogador
    jogador.update()

    # Verificar colisão usando máscara (respeita pixels transparentes)
    colisoes = pygame.sprite.spritecollide(jogador, inimigos, dokill=True, collided=pygame.sprite.collide_mask)
    if colisoes:
        print("Colisão pixel-perfect detectada!")

    # Renderizar
    tela.fill((255, 255, 255))
    todos_sprites.draw(tela)
    pygame.display.flip()

pygame.quit()
