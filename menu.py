# --- START OF FILE menu.py ---
import pygame
import os # Usar os.path para verificar arquivos

# Obter o diretório onde o script menu.py está localizado
script_dir = os.path.dirname(os.path.abspath(__file__))

# Caminhos completos para as imagens do menu
fundo_menu_path = os.path.join(script_dir,  'fundo_menu.png')
# Usar o mesmo fundo para créditos, como no código original fornecido
fundo_creditos_path = os.path.join(script_dir, 'tileset_1.png')

# Carregar imagens do menu AQUI para que sejam carregadas apenas uma vez
try:
    if not os.path.exists(fundo_menu_path):
        raise FileNotFoundError(f"Arquivo não encontrado: {fundo_menu_path}")
    fundo_menu_surf = pygame.image.load(fundo_menu_path).convert() # Renomeado para evitar conflito com global
    print(f"DEBUG: Carregou fundo_menu de {fundo_menu_path}")

    if not os.path.exists(fundo_creditos_path):
         # Se o fundo de créditos for diferente e não existir, tratar aqui
         raise FileNotFoundError(f"Arquivo não encontrado: {fundo_creditos_path}")
    fundo_creditos_surf = pygame.image.load(fundo_creditos_path).convert() # Renomeado
    print(f"DEBUG: Carregou fundo_creditos de {fundo_creditos_path}")

except (pygame.error, FileNotFoundError) as e:
    print(f"AVISO: Erro ao carregar imagens do menu: {e}")
    print("       Usando fundos coloridos como placeholder.")
    fundo_menu_surf = None # Usar None inicialmente
    fundo_creditos_surf = None


class Menu():
    def __init__(self, main_game_instance):
        self.main_game = main_game_instance
        self.tela = main_game_instance.tela
        self.LARGURA = main_game_instance.LARGURA
        self.ALTURA = main_game_instance.ALTURA
        # Posição horizontal original mantida (LARGURA / 6)
        self.mid_w, self.mid_h = self.LARGURA / 6 , self.ALTURA / 2.3
        self.cursor_rect = pygame.Rect(0, 0, 30, 30)
        # Offset original mantido (-150)
        self.offset = -150
        self.font_name = 'EFCO Brookshire Regular.ttf'
        self.font_size_titulo = 50
        self.font_size_opcao = 35
        self.font_size_cursor = 40
        self.font_color = (255, 255, 255) # Branco

        # Referências às superfícies carregadas globalmente
        self.fundo_menu_scaled = None
        self.fundo_creditos_scaled = None

        # Escala as superfícies globais se elas foram carregadas
        global fundo_menu_surf, fundo_creditos_surf # Acessa as superfícies globais
        if fundo_menu_surf:
            self.fundo_menu_scaled = pygame.transform.scale(fundo_menu_surf, (self.LARGURA, self.ALTURA))
        else:
             self.fundo_menu_scaled = pygame.Surface((self.LARGURA, self.ALTURA))
             self.fundo_menu_scaled.fill((0, 0, 50)) # Azul escuro placeholder

        if fundo_creditos_surf:
            self.fundo_creditos_scaled = pygame.transform.scale(fundo_creditos_surf, (self.LARGURA, self.ALTURA))
        else:
             # Usa o mesmo placeholder do menu se o de créditos falhou (ou era o mesmo arquivo)
             self.fundo_creditos_scaled = pygame.Surface((self.LARGURA, self.ALTURA))
             self.fundo_creditos_scaled.fill((50, 0, 50)) # Roxo escuro placeholder


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
        Menu.__init__(self, main_game_instance)
        self.state = "Start" # Opção inicial

        # Posições das opções (sem Options)
        # Mantendo o espaçamento de 60px entre itens
        self.startx, self.starty = self.mid_w, self.mid_h + 0
        self.creditsx, self.creditsy = self.mid_w, self.mid_h + 60  # Credits agora está onde Options estava
        self.quitx, self.quity = self.mid_w, self.mid_h + 120 # Quit desce para preencher o espaço

        # Posição inicial do cursor
        self.cursor_rect.midtop = (self.startx + self.offset, self.starty)

    def display_menu(self):
        """Desenha os elementos do menu principal na tela."""
        # Usa a imagem de fundo escalada da classe base
        self.tela.blit(self.fundo_menu_scaled, (0,0))

        # Desenha o título e as opções restantes
        self.draw_text('Nome do Jogo', self.font_size_titulo, self.mid_w, self.mid_h - 100)
        self.draw_text('START', self.font_size_opcao, self.startx, self.starty)
        # self.draw_text('OPTIONS', self.font_size_opcao, self.optionsx, self.optionsy) # REMOVIDO
        self.draw_text('CREDITS', self.font_size_opcao, self.creditsx, self.creditsy) # Usa nova posição Y
        self.draw_text('QUIT', self.font_size_opcao, self.quitx, self.quity)       # Usa nova posição Y
        self.draw_cursor()

    def handle_input(self, events):
        """Processa input para o menu principal (sem Options)."""
        next_game_state = "MENU" # Continua no menu por padrão

        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_DOWN:
                    if self.state == 'Start':
                        self.state = 'Credits' # Pula Options
                        self.cursor_rect.midtop = (self.creditsx + self.offset, self.creditsy)
                    # elif self.state == 'Options': REMOVIDO
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
                    # elif self.state == 'Options': REMOVIDO
                    elif self.state == 'Credits':
                        self.state = 'Start' # Volta para Start
                        self.cursor_rect.midtop = (self.startx + self.offset, self.starty)
                    elif self.state == 'Quit':
                         self.state = 'Credits'
                         self.cursor_rect.midtop = (self.creditsx + self.offset, self.creditsy)

                elif event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                    if self.state == 'Start':
                        next_game_state = "PLAYING"
                    # elif self.state == 'Options': REMOVIDO
                    elif self.state == 'Credits':
                        next_game_state = "CREDITS"
                    elif self.state == 'Quit':
                         next_game_state = "QUIT"

                elif event.key == pygame.K_ESCAPE:
                     next_game_state = "QUIT"

        return next_game_state

# Classe OptionsMenu REMOVIDA COMPLETAMENTE

class CreditsMenu(Menu):
    def __init__(self, main_game_instance):
        Menu.__init__(self, main_game_instance)
        # Nenhuma mudança necessária aqui

    def display_menu(self):
        # Usa a imagem de fundo escalada da classe base
        self.tela.blit(self.fundo_creditos_scaled, (0,0))

        # Desenho original dos créditos mantido
        self.draw_text('CREDITS', self.font_size_titulo, self.mid_w, self.mid_h - 150)
        text_y_start = self.mid_h - 50
        line_height = 50
        # Ajuste a posição X se LARGURA/6 ficou muito à esquerda
        credits_text_x = self.LARGURA / 2 # Centralizar texto dos créditos pode ser melhor
        self.draw_text('Game Design - Seu Nome/Equipe', self.font_size_opcao, credits_text_x, text_y_start + 0 * line_height)
        self.draw_text('Programming - Seu Nome/Equipe', self.font_size_opcao, credits_text_x, text_y_start + 1 * line_height)
        self.draw_text('Art - Seu Nome/Equipe', self.font_size_opcao, credits_text_x, text_y_start + 2 * line_height)
        self.draw_text('Music - Seu Nome/Equipe', self.font_size_opcao, credits_text_x, text_y_start + 3 * line_height)
        self.draw_text('Press ENTER or ESC to go back', self.font_size_opcao - 10, self.LARGURA / 2, self.ALTURA - 60) # Centralizar instrução

    def handle_input(self, events):
        next_game_state = "CREDITS"
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER or \
                   event.key == pygame.K_ESCAPE or event.key == pygame.K_BACKSPACE:
                    next_game_state = "MENU"
        return next_game_state

# --- END OF FILE menu.py ---