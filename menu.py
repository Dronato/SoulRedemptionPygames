import cv2
import pygame
import os
import webbrowser

# --- Função para tocar a cutscene com texto "PULAR" ---
def play_cutscene(video_path, tela, audio_path=None):
    clock = pygame.time.Clock()

    if not pygame.mixer.get_init():
        pygame.mixer.init()

    if audio_path and os.path.exists(audio_path):
        pygame.mixer.music.load(audio_path)
        pygame.mixer.music.set_volume(0.7)
        pygame.mixer.music.play()
    else:
        print("Aviso: Áudio da cutscene não encontrado.")

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Erro ao abrir o vídeo: {video_path}")
        return

    video_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    video_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    video_fps = cap.get(cv2.CAP_PROP_FPS) or 30

    tela = pygame.display.set_mode((video_width, video_height))
    pygame.display.set_caption("Cutscene")

    arcade_font_path = os.path.join(os.path.dirname(__file__), "ARCADE_N.ttf")
    if os.path.exists(arcade_font_path):
        font = pygame.font.Font(arcade_font_path, 16)
    else:
        print("Fonte 'ARCADE_N.ttf' não encontrada, usando fonte pixelada padrão.")
        font = pygame.font.SysFont("Courier New", 16, bold=True)

    skip = False
    while cap.isOpened() and not skip:
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_surface = pygame.surfarray.make_surface(frame.swapaxes(0, 1))
        tela.blit(frame_surface, (0, 0))

        # Texto "PULAR" no canto superior direito
        text_surface = font.render("aperte enter para pular", True, (255, 255, 255))
        text_rect = text_surface.get_rect(topright=(video_width - 20, 20))
        tela.blit(text_surface, text_rect)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                cap.release()
                pygame.quit()
                return
            elif event.type == pygame.KEYDOWN:
                if event.key in [pygame.K_ESCAPE, pygame.K_SPACE, pygame.K_RETURN]:
                    skip = True
                    break

        clock.tick(video_fps)

    cap.release()
    pygame.mixer.music.stop()

# --- Caminhos dos arquivos ---
script_dir = os.path.dirname(os.path.abspath(__file__))
fundo_menu_path = os.path.join(script_dir, 'fundo_menu.png')
fundo_creditos_path = os.path.join(script_dir, 'call.png')

try:
    fundo_menu_surf = pygame.image.load(fundo_menu_path).convert()
    fundo_creditos_surf = pygame.image.load(fundo_creditos_path).convert()
except:
    fundo_menu_surf = None
    fundo_creditos_surf = None

# --- CLASSES DE MENU ---

class Menu():
    def __init__(self, main_game_instance):
        pygame.mixer.init()
        if not pygame.mixer.music.get_busy():
            pygame.mixer.music.load("musica/MUSICA Tela Inicial.mp3")
            pygame.mixer.music.set_volume(0.5)
            pygame.mixer.music.play(-1)

        self.main_game = main_game_instance
        self.tela = main_game_instance.tela
        self.LARGURA = main_game_instance.LARGURA
        self.ALTURA = main_game_instance.ALTURA
        self.mid_w, self.mid_h = self.LARGURA / 6, self.ALTURA / 1.7
        self.cursor_rect = pygame.Rect(0, 0, 0, 0)
        self.offset = -100
        self.font_name = 'EFCO Brookshire Regular.ttf'
        self.font_size_titulo = 100
        self.font_size_opcao = 50
        self.font_size_cursor = 40
        self.font_color = (216, 226, 248)  # #d8e2f8

        global fundo_menu_surf, fundo_creditos_surf
        self.fundo_menu_scaled = pygame.transform.scale(fundo_menu_surf, (self.LARGURA, self.ALTURA)) if fundo_menu_surf else pygame.Surface((self.LARGURA, self.ALTURA)).fill((0, 0, 50))
        self.fundo_creditos_scaled = pygame.transform.scale(fundo_creditos_surf, (self.LARGURA, self.ALTURA)) if fundo_creditos_surf else pygame.Surface((self.LARGURA, self.ALTURA)).fill((50, 0, 50))

    def draw_text(self, text, size, x, y, color=None):
        if color is None:
            color = self.font_color
        font = pygame.font.Font(self.font_name, size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        text_rect.topleft = (x, y)
        self.tela.blit(text_surface, text_rect)

    def draw_cursor(self):
        self.draw_text('*', self.font_size_cursor, self.cursor_rect.x, self.cursor_rect.y)


class MainMenu(Menu):
    def __init__(self, main_game_instance):
        Menu.__init__(self, main_game_instance)
        self.state = "Start"
        self.menu_x = self.LARGURA // 6
        self.startx, self.starty = self.menu_x, self.mid_h + 0
        self.creditsx, self.creditsy = self.menu_x, self.mid_h + 60
        self.quitx, self.quity = self.menu_x, self.mid_h + 120
        self.offset = -40
        self.cursor_rect.midtop = (self.startx + self.offset, self.starty)
        self.blink_visible = True
        self.last_toggle_time = pygame.time.get_ticks()
        self.toggle_interval = 500

        # --- Fundo animado com frames ---
        self.frames = []
        self.current_frame = 0
        self.frame_timer = 0
        self.frame_interval = 40  # milissegundos por frame (10 FPS)

        gif_folder = os.path.join(os.path.dirname(__file__), "gif")
        if os.path.exists(gif_folder):
            frame_files = sorted([
                os.path.join(gif_folder, f)
                for f in os.listdir(gif_folder)
                if f.lower().endswith(('.png', '.jpg', '.jpeg'))
            ])
            for frame_path in frame_files:
                img = pygame.image.load(frame_path).convert()
                img = pygame.transform.scale(img, (self.LARGURA, self.ALTURA))
                self.frames.append(img)
        else:
            print("Pasta 'gif' com frames do fundo animado não encontrada.")

    def display_menu(self):
        # Fundo animado
        if self.frames:
            current_time = pygame.time.get_ticks()
            if current_time - self.frame_timer > self.frame_interval:
                self.current_frame = (self.current_frame + 1) % len(self.frames)
                self.frame_timer = current_time
            self.tela.blit(self.frames[self.current_frame], (0, 0))
        else:
            self.tela.blit(self.fundo_menu_scaled, (0, 0))

        current_time = pygame.time.get_ticks()
        if current_time - self.last_toggle_time > self.toggle_interval:
            self.blink_visible = not self.blink_visible
            self.last_toggle_time = current_time

        # Lógica de piscar apenas o item selecionado
        if self.state == 'Start':
            if self.blink_visible:
                self.draw_text('start', self.font_size_opcao, self.startx + 2, self.starty + 2, (120, 127, 143))
                self.draw_text('start', self.font_size_opcao, self.startx, self.starty)
        else:
            self.draw_text('start', self.font_size_opcao, self.startx, self.starty)

        if self.state == 'Credits':
            if self.blink_visible:
                self.draw_text('credits', self.font_size_opcao, self.creditsx, self.creditsy)
        else:
            self.draw_text('credits', self.font_size_opcao, self.creditsx, self.creditsy)

        if self.state == 'Quit':
            if self.blink_visible:
                self.draw_text('quit', self.font_size_opcao, self.quitx, self.quity)
        else:
            self.draw_text('quit', self.font_size_opcao, self.quitx, self.quity)

        self.draw_cursor()

    def handle_input(self, events):
        next_game_state = "MENU"

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
                        pygame.mixer.music.pause()
                        video_path = os.path.join(script_dir, "cutscenes", "Cutscene 01.mp4")
                        audio_path = os.path.join(script_dir, "cutscenes", "Cutscene-01.mp3")
                        play_cutscene(video_path, self.tela, audio_path)
                        pygame.mixer.music.unpause()
                        next_game_state = "PLAYING"
                    elif self.state == 'Credits':
                        pygame.mixer.music.pause()
                        next_game_state = "CREDITS"
                    elif self.state == 'Quit':
                        pygame.mixer.music.stop()
                        next_game_state = "QUIT"

                elif event.key == pygame.K_ESCAPE:
                    pygame.mixer.music.stop()
                    next_game_state = "QUIT"

        return next_game_state


class CreditsMenu(Menu):
    def __init__(self, main_game_instance):
        super().__init__(main_game_instance)

        # Lista com nome, posição e link de cada personagem
        self.characters = [
            {"name": "CARLOS",  "rect": pygame.Rect(237,  30,  200, 130), "url": "https://github.com/cDorth"},
            {"name": "RAFAELA",   "rect": pygame.Rect(720, 30,  200, 130), "url": "https://github.com/bruxa61"},
            {"name": "RAÍ",      "rect": pygame.Rect(1203, 30,  200, 130), "url": "https://github.com/Rai123100"},
            {"name": "BRUNA",    "rect": pygame.Rect(237,  317, 200, 130), "url": "https://github.com/brubsb"},
            {"name": "DAVI",     "rect": pygame.Rect(720, 317, 200, 130), "url": "https://github.com/DaviTorralvo"},
            {"name": "ARTHUR",   "rect": pygame.Rect(1203, 317, 200, 130), "url": "https://github.com/intentdoor"},
            {"name": "PEDRO",    "rect": pygame.Rect(237,  605, 200, 130), "url": "https://github.com/pe-odake"},
            {"name": "GUILHERME",  "rect": pygame.Rect(720, 605, 200, 130), "url": "https://github.com/gprsilva"},
            {"name": "MATHEUS","rect": pygame.Rect(1203, 605, 200, 130), "url": "https://github.com/vicenteruedamatheus"},
        ]

        self.selected_index = 0
        self.blink_visible = True
        self.last_toggle_time = pygame.time.get_ticks()
        self.toggle_interval = 500

        self.back_button_rect = pygame.Rect(50, self.main_game.ALTURA - 110, 135, 60)
        self.back_button_color = (50, 50, 50)
        self.back_button_hover_color = (100, 100, 100)
        self.back_button_text_color = (255, 255, 255)

    def display_menu(self):
        self.tela.blit(self.fundo_creditos_scaled, (0, 0))

        current_time = pygame.time.get_ticks()
        if current_time - self.last_toggle_time > self.toggle_interval:
            self.blink_visible = not self.blink_visible
            self.last_toggle_time = current_time

        for i, char in enumerate(self.characters):
            rect = char["rect"]
            if i == self.selected_index and self.blink_visible:
                # Desenha o asterisco à esquerda do personagem
                self.draw_text("*", 40, rect.left - 25, rect.top + 40, (255, 255, 255))

        mouse_pos = pygame.mouse.get_pos()
        is_hovering = self.back_button_rect.collidepoint(mouse_pos)

        button_color = self.back_button_hover_color if is_hovering else self.back_button_color
        pygame.draw.rect(self.tela, button_color, self.back_button_rect, border_radius=10)

        self.draw_text("voltar", 30, self.back_button_rect.x + 30, self.back_button_rect.y + 10, self.back_button_text_color)

    def handle_input(self, events):
        next_game_state = "CREDITS"

        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key in [pygame.K_ESCAPE, pygame.K_BACKSPACE]:
                    pygame.mixer.music.unpause()
                    next_game_state = "MENU"

                elif event.key == pygame.K_RETURN:
                    selected_char = self.characters[self.selected_index]
                    webbrowser.open(selected_char["url"])

                elif event.key == pygame.K_DOWN:
                    self.selected_index = (self.selected_index + 3) % len(self.characters)
                elif event.key == pygame.K_UP:
                    self.selected_index = (self.selected_index - 3) % len(self.characters)
                elif event.key == pygame.K_LEFT:
                    if self.selected_index % 3 != 0:
                        self.selected_index -= 1
                elif event.key == pygame.K_RIGHT:
                    if (self.selected_index + 1) % 3 != 0:
                        self.selected_index += 1

            # ESTE BLOCO AQUI DEVE FICAR FORA DO if KEYDOWN:
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = pygame.mouse.get_pos()
                if self.back_button_rect.collidepoint(mouse_pos):
                    pygame.mixer.music.unpause()
                    next_game_state = "MENU"

        return next_game_state