import pygame

# Configurações básicas
tela = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
LARGURA, ALTURA = tela.get_size() 
FPS = 60

# Inicializar Pygame
pygame.init()
tela = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Teste de Colisão")
relogio = pygame.time.Clock()

# Cores
BRANCO = (255, 255, 255)
AZUL = (0, 0, 255)
VERMELHO = (255, 0, 0)

# Classe do Jogador
class Jogador(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((50, 50))
        self.image.fill(AZUL)
        self.rect = self.image.get_rect(center=(100, ALTURA // 2))
        self.velocidade = 5

    def update(self):
        teclas = pygame.key.get_pressed()
        if teclas[pygame.K_LEFT]:
            self.rect.x -= self.velocidade
        if teclas[pygame.K_RIGHT]:
            self.rect.x += self.velocidade
        if teclas[pygame.K_UP]:
            self.rect.y -= self.velocidade
        if teclas[pygame.K_DOWN]:
            self.rect.y += self.velocidade

# Classe do Inimigo
class Inimigo(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((50, 50))
        self.image.fill(VERMELHO)
        self.rect = self.image.get_rect(center=(x, y))

# Criando os sprites
jogador = Jogador()
inimigo = Inimigo(400, ALTURA // 2)

# Grupos de sprites
todos_sprites = pygame.sprite.Group()
todos_sprites.add(jogador, inimigo)

inimigos = pygame.sprite.Group()
inimigos.add(inimigo)

# Loop principal
executando = True
while executando:
    relogio.tick(FPS)
    
    # Eventos
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            executando = False
    
    # Atualiza
    todos_sprites.update()
    
    # Verificar colisão do jogador com inimigo
    if pygame.sprite.spritecollide(jogador, inimigos, True):
        print("Inimigo derrotado!")
    
    # Renderizar
    tela.fill(BRANCO)
    todos_sprites.draw(tela)
    pygame.display.flip()

pygame.quit()