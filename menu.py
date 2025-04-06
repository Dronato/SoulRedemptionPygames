# --- START OF FILE menu.py ---
import pygame
import os  # Usar os.path para verificar arquivos
from PIL import Image  # Biblioteca para manipulação de imagens (necessária para GIF animado)

# Obter o diretório onde o script menu.py está localizado
script_dir = os.path.dirname(os.path.abspath(__file__))

# Caminhos completos para as imagens do menu
fundo_menu_path = os.path.join(script_dir, 'fundo_menu.gif')
fundo_creditos_path = os.path.join(script_dir, 'tileset_1.png')  # Fundo estático para créditos

def load_gif_frames(path, size):
    """
    Carrega todos os frames de um GIF e os converte em superfícies do Pygame.
    :param path: caminho para o GIF.
    :param size: tupla (largura, altura) para redimensionar os frames.
    :return: lista de superfícies do Pygame.
    """
    frames = []
    try:
        pil_gif = Image.open(path)
        # Itera pelos frames do GIF
        try:
            while True:
                frame = pil_gif.copy().convert("RGBA")
                frame = frame.resize(size, Image.ANTIALIAS)
                mode = frame.mode
                frame_size = frame.size
                data = frame.tobytes()
                frame_surface = pygame.image.fromstring(data, frame_size, mode).convert_alpha()
                frames.append(frame_surface)
                pil_gif.seek(pil_gif.tell() + 1)
        except EOFError:
            pass  # Fim dos frames
        print(f"DEBUG: Carregados {len(frames)} frames do GIF {path}")
    except Exception as e:
        print(f"Erro ao carregar GIF '{path}': {e}")
    return frames

# Carregar a imagem estática para os créditos
try:
    if not os.path.exists(fundo_creditos_path):
         raise FileNotFoundError(f"Arquivo não encontrado: {fundo_creditos_path}")
    fundo_creditos_surf = pygame.image.load(fundo_creditos_path).convert()
    print(f"DEBUG: Carregou fundo_creditos de {fundo_creditos_path}")
except (pygame.error, FileNotFoundError) as e:
    print(f"AVISO: Erro ao carregar fundo de créditos: {e}")
    fundo_creditos_surf = None

class Menu():
    def __init__(self, main_game_instance):
        self.main_game = main_game_instance
        self.tela = main_game_instance.tela
        self.LARGURA = main_game_instance.LARGURA
        self.ALTURA = main_game_instance.ALTURA
        # Posição horizontal original mantida (LARGURA / 6)
        self.mid_w, self.mid_h = self.LARGURA / 6, self.ALTURA / 2.3
        self.cursor_rect = pygame.Rect(0, 0, 30, 30)
        # Offset original mantido (-150)
        self.offset = -150
        self.font_name = 'EFCO Brookshire Regular.ttf'
        self.font_size_titulo = 50
        self.font_size_opcao = 35
        self.font_size_cursor = 40
        self.font_color = (255, 255, 255)  # Branco

        # --- Configuração do fundo animado do menu ---
        if os.path.exists(fundo_menu_path):
            self.fundo_menu_frames = load_gif_frames(fundo_menu_path, (self.LARGURA, self.ALTURA))
            if not self.fundo_menu_frames:
                # Se ocorrer erro, cria um placeholder
                placeholder = pygame.Surface((self.LARGURA, self.ALTURA))
                placeholder.fill((0, 0, 50))
                self.fundo_menu_frames = [placeholder]
        else:
            placeholder = pygame.Surface((self.LARGURA, self.ALTURA))
            placeholder.fill((0, 0, 50))
            self.fundo_menu_frames = [placeholder]

        # Variáveis para animação
        self.current_frame = 0
        self.frame_timer = pygame.time.get_ticks()
        self.frame_delay = 100  # milissegundos entre os quadros (~10 fps)

        # --- Configuração do fundo estático para créditos ---
        global fundo_creditos_surf
        if fundo_creditos_surf:
            self.fundo_creditos_scaled = pygame.transform.scale(fundo_creditos_surf, (self.LARGURA, self.ALTURA))
        else:
            self.fundo_creditos_scaled = pygame.Surface((self.LARGURA, self.ALTURA))
            self.fundo_creditos_scaled.fill((50, 0, 50))  # Roxo escuro placeholder

    def draw_text(self, text, size, x, y, color=None):
        if color is None:
            color = self.font_color
        # Chama a função draw_text da instância principal do jogo
        self.main_game.draw_text(text, size, x, y, color=color, font_name=self.font_name)

    def draw_cursor(self):
        # Desenha o cursor na posição atual definida por self.cursor_rect
        self.draw_text('*', self.font_size_cursor, self.cursor_rect.x, self.cursor_rect.y)

class MainMenu(Menu):
    def __init__(self, main_game_instance):
        super().__init__(main_game_instance)
        self.state = "Start"  # Opção inicial
        # Posições das opções (sem Options)
        self.startx, self.starty = self.mid_w, self.mid_h + 0
        self.creditsx, self.creditsy = self.mid_w, self.mid_h + 60  # Credits na posição do antigo Options
        self.quitx, self.quity = self.mid_w, self.mid_h + 120  # Quit abaixo
        # Posição inicial do cursor
        self.cursor_rect.midtop = (self.startx + self.offset, self.starty)

    def display_menu(self):
        """Desenha os elementos do menu principal na tela, atualizando o fundo animado."""
        # Atualiza o frame do fundo animado com base no tempo
        now = pygame.time.get_ticks()
        if now - self.frame_timer > self.frame_delay:
            self.frame_timer = now
            self.current_frame = (self.current_frame + 1) % len(self.fundo_menu_frames)
        self.tela.blit(self.fundo_menu_frames[self.current_frame], (0, 0))

        # Desenha título e opções
        self.draw_text('Nome do Jogo', self.font_size_titulo, self.mid_w, self.mid_h - 100)
        self.draw_text('START', self.font_size_opcao, self.startx, self.starty)
        self.draw_text('CREDITS', self.font_size_opcao, self.creditsx, self.creditsy)
        self.draw_text('QUIT', self.font_size_opcao, self.quitx, self.quity)
        self.draw_cursor()

    def handle_input(self, events):
        """Processa input para o menu principal (sem Options)."""
        next_game_state = "MENU"  # Continua no menu por padrão
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_DOWN:
                    if self.state == 'Start':
                        self.state = 'Credits'
                        self.cursor_rect.midtop = (self.creditsx + self.offset, self.creditsy)
                    elif self.state == 'Credits':
                        self.state = 'Quit'
                        self.cursor_rect.midtop = (self.quitx + self.offset, self.quity)
                    elif self.state == 'Quit':
                        self.state = 'Start'
                        self.cursor_rect.midtop = (self.startx + self.offset, self.starty)
                elif event.key == pygame.K_UP:
                    if self.state == 'Start':
                        self.state = 'Quit'
                        self.cursor_rect.midtop = (self.quitx + self.offset, self.quity)
                    elif self.state == 'Credits':
                        self.state = 'Start'
                        self.cursor_rect.midtop = (self.startx + self.offset, self.starty)
                    elif self.state == 'Quit':
                        self.state = 'Credits'
                        self.cursor_rect.midtop = (self.creditsx + self.offset, self.creditsy)
                elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    if self.state == 'Start':
                        next_game_state = "PLAYING"
                    elif self.state == 'Credits':
                        next_game_state = "CREDITS"
                    elif self.state == 'Quit':
                        next_game_state = "QUIT"
                elif event.key == pygame.K_ESCAPE:
                    next_game_state = "QUIT"
        return next_game_state

class CreditsMenu(Menu):
    def __init__(self, main_game_instance):
        super().__init__(main_game_instance)

    def display_menu(self):
        # Fundo estático para créditos
        self.tela.blit(self.fundo_creditos_scaled, (0, 0))
        self.draw_text('CREDITS', self.font_size_titulo, self.mid_w, self.mid_h - 150)
        text_y_start = self.mid_h - 50
        line_height = 50
        credits_text_x = self.LARGURA / 2
        self.draw_text('Game Design - Seu Nome/Equipe', self.font_size_opcao, credits_text_x, text_y_start + 0 * line_height)
        self.draw_text('Programming - Seu Nome/Equipe', self.font_size_opcao, credits_text_x, text_y_start + 1 * line_height)
        self.draw_text('Art - Seu Nome/Equipe', self.font_size_opcao, credits_text_x, text_y_start + 2 * line_height)
        self.draw_text('Music - Seu Nome/Equipe', self.font_size_opcao, credits_text_x, text_y_start + 3 * line_height)
        self.draw_text('Press ENTER or ESC to go back', self.font_size_opcao - 10, self.LARGURA / 2, self.ALTURA - 60)

    def handle_input(self, events):
        next_game_state = "CREDITS"
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_ESCAPE, pygame.K_BACKSPACE):
                    next_game_state = "MENU"
        return next_game_state

# --- END OF FILE menu.py ---
