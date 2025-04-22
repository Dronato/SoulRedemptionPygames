import pygame

PARADO_ANDY = 'parado A'
PARADO_RAFA = 'parado F'
PARADO_GAB = 'parado G'

SPRITES = {
    PARADO_ANDY: {"file": "img/npc/andy.png", "frames": 2, "width": 635, "height": 941},
    PARADO_RAFA: {"file": "img/npc/rafa.png", "frames": 3, "width": 261, "height": 394},
    PARADO_GAB: {"file": "img/npc/gabriel.png", "frames": 2, "width": 648, "height": 877}
}

# MAGO ANDERSON

class NPC_Andy(pygame.sprite.Sprite):
    def __init__(self, x, y, zoom_level=2.0):
        super().__init__()
        self.state = PARADO_ANDY
        self._sprites_cache = {}
        self.facing_right = True
        self.animation_timer = 0
        self.animation_speed = 8
        self.frame_index = 0
        self.zoom_level = zoom_level

        self.load_sprites()
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect(topleft=(x, y))
        
        # DEF DE CONVERSAR COM O ANDY
        self.contador = 1  # Começa na fala 1
        self.total_falas = 5  # Total de imagens de fala
        


    def load_sprites(self):
        sprite_info = SPRITES[self.state]
        self.frames = self.load_frames(sprite_info["file"], sprite_info["frames"], sprite_info["width"], sprite_info["height"], (33, 48))


    def load_frames(self, file, frame_count, width, height, resize):
        """Separa os frames da sprite sheet e os redimensiona se necessário."""
        sheet = pygame.image.load(file).convert_alpha()
        frames = []
        
        for i in range(frame_count):
            x = i * width
            frame = sheet.subsurface(pygame.Rect(x, 0, width, height))
            frame = pygame.transform.scale(frame, resize)
            frames.append(frame)
        
        return frames

    def atualizar(self):
        self.animation_timer += 1
        if self.animation_timer >= self.animation_speed:
            self.animation_timer = 0
            self.frame_index = (self.frame_index + 1) % len(self.frames)
            self.image = self.frames[self.frame_index]
            
    def conversar(self, tela, largura_tela, altura_tela):
        caminho = f"img/npc/fala_andy{self.contador}.png"

        imagem = pygame.image.load(caminho).convert_alpha()
        largura_fala = int(largura_tela * 0.7)
        altura_fala = int(altura_tela * 0.25)
        imagem = pygame.transform.scale(imagem, (largura_fala, altura_fala))

        pos_x = (largura_tela - largura_fala) // 2
        pos_y = altura_tela - altura_fala - 30

        tela.blit(imagem, (pos_x, pos_y))
        
    def avancar_conversa(self):
        self.contador += 1
        if self.contador > self.total_falas:
            self.contador = 1
            return False  # Fim da conversa
        return True  # Ainda tem falas

    def voltar_conversa(self):
        self.contador -= 1
        if self.contador < 1:
            self.contador = 1  # Garante que não vá abaixo de 1

        
# FANTASMA RAFAEL    

class NPC_Rafa(pygame.sprite.Sprite):
    def __init__(self, x, y, zoom_level=2.0):
        super().__init__()
        self.state = PARADO_RAFA
        self._sprites_cache = {}
        self.facing_right = True
        self.animation_timer = 0
        self.animation_speed = 8
        self.frame_index = 0
        self.zoom_level = zoom_level

        self.load_sprites()
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect(topleft=(x, y))
        
        # DEF DE CONVERSAR COM O ANDY
        self.contador = 1  # Começa na fala 1
        self.total_falas = 3  # Total de imagens de fala


    # def load_sprites(self):
    #     sprite_info = SPRITES[self.state]
    #     self.frames = self.load_frames(sprite_info["file"], sprite_info["frames"], sprite_info["width"], sprite_info["height"], (33, 48))
        
    def load_sprites(self):
        sprite_info = SPRITES[self.state]
        self.frames = self.load_frames(sprite_info["file"], sprite_info["frames"], sprite_info["width"], sprite_info["height"], (33, 48))
        print(f"{self.__class__.__name__} - Frames carregados: {len(self.frames)}")


    def load_frames(self, file, frame_count, width, height, resize):
        """Separa os frames da sprite sheet e os redimensiona se necessário."""
        sheet = pygame.image.load(file).convert_alpha()
        frames = []
        
        for i in range(frame_count):
            x = i * width
            frame = sheet.subsurface(pygame.Rect(x, 0, width, height))
            frame = pygame.transform.scale(frame, resize)
            frames.append(frame)
        return frames
        


    def atualizar(self):
        self.animation_timer += 1
        if self.animation_timer >= self.animation_speed:
            self.animation_timer = 0
            self.frame_index = (self.frame_index + 1) % len(self.frames)
            self.image = self.frames[self.frame_index]
            
    def conversar(self, tela, largura_tela, altura_tela):
        caminho = f"img/npc/fala_fantasma{self.contador}.png"

        imagem = pygame.image.load(caminho).convert_alpha()
        largura_fala = int(largura_tela * 0.7)
        altura_fala = int(altura_tela * 0.25)
        imagem = pygame.transform.scale(imagem, (largura_fala, altura_fala))

        pos_x = (largura_tela - largura_fala) // 2
        pos_y = altura_tela - altura_fala - 30

        tela.blit(imagem, (pos_x, pos_y))
    
    def avancar_conversa(self):
        self.contador += 1
        if self.contador > self.total_falas:
            self.contador = 1
            return False  # Fim da conversa
        return True  # Ainda tem falas

    def voltar_conversa(self):
        self.contador -= 1
        if self.contador < 1:
            self.contador = 1  # Garante que não vá abaixo de 1

# GABRIEL

class NPC_Gab(pygame.sprite.Sprite):
    def __init__(self, x, y, zoom_level=2.0):
        super().__init__()
        self.state = PARADO_GAB
        self._sprites_cache = {}
        self.facing_right = True
        self.animation_timer = 0
        self.animation_speed = 8
        self.frame_index = 0
        self.zoom_level = zoom_level

        self.load_sprites()
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect(topleft=(x, y))
        
        # DEF DE CONVERSAR COM O ANDY
        self.contador = 1  # Começa na fala 1
        self.total_falas = 2  # Total de imagens de fala


        
    def load_sprites(self):
        sprite_info = SPRITES[self.state]
        self.frames = self.load_frames(sprite_info["file"], sprite_info["frames"], sprite_info["width"], sprite_info["height"], (55, 70))
        print(f"{self.__class__.__name__} - Frames carregados: {len(self.frames)}")


    def load_frames(self, file, frame_count, width, height, resize):
        """Separa os frames da sprite sheet e os redimensiona se necessário."""
        sheet = pygame.image.load(file).convert_alpha()
        frames = []
        
        for i in range(frame_count):
            x = i * width
            frame = sheet.subsurface(pygame.Rect(x, 0, width, height))
            frame = pygame.transform.scale(frame, resize)
            frames.append(frame)
        return frames
        


    def atualizar(self):
        self.animation_timer += 1
        if self.animation_timer >= self.animation_speed:
            self.animation_timer = 0
            self.frame_index = (self.frame_index + 1) % len(self.frames)
            self.image = self.frames[self.frame_index]
            
    def conversar(self, tela, largura_tela, altura_tela):
        caminho = f"img/npc/fala_gabriel{self.contador}.png"

        imagem = pygame.image.load(caminho).convert_alpha()
        largura_fala = int(largura_tela * 0.7)
        altura_fala = int(altura_tela * 0.25)
        imagem = pygame.transform.scale(imagem, (largura_fala, altura_fala))

        pos_x = (largura_tela - largura_fala) // 2
        pos_y = altura_tela - altura_fala - 30

        tela.blit(imagem, (pos_x, pos_y))

    def avancar_conversa(self):
        self.contador += 1
        if self.contador > self.total_falas:
            self.contador = 1
            return False  # Fim da conversa
        return True  # Ainda tem falas

    def voltar_conversa(self):
        self.contador -= 1
        if self.contador < 1:
            self.contador = 1  # Garante que não vá abaixo de 1