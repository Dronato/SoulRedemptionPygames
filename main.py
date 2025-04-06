# --- START OF FILE main.py ---

import pygame
import sys
import os

# Importar componentes do jogo
from player import Jogador
import inimigo # Importar o módulo todo
from inimigo import Inimigo1mp1, Inimigo1mp2
from map_loader import carregar_mapa, desenhar_mapa, criar_mapa_rects, criar_objetos_retangulos
pygame.init() # Mover pygame.init() para o início da classe Game é mais comum

# Importar classes do menu (SEM OptionsMenu)
try:
    from menu import MainMenu, CreditsMenu # REMOVIDO OptionsMenu
except ImportError:
    print("---------------------------------------------------------")
    print("ERRO: Não foi possível encontrar ou importar 'menu.py'.")
    print("Certifique-se de que o arquivo 'menu.py' com as classes")
    print("MainMenu e CreditsMenu está na mesma pasta")
    print("que este arquivo 'main.py'.")
    print("---------------------------------------------------------")
    sys.exit()
except Exception as e:
    print(f"Erro inesperado ao importar 'menu.py': {e}")
    sys.exit()

class Game:
    def __init__(self):
        """Inicializa o Pygame, a tela, e as configurações gerais."""
        print("DEBUG: Iniciando Game.__init__")
        try:
            # Inicializar Pygame AQUI é mais padrão
            init_success, init_failure = pygame.init()
            print(f"DEBUG: pygame.init() -> Sucesso={init_success}, Falha={init_failure}")
            if init_failure > 0:
                 print("ERRO: Falha ao inicializar módulos do Pygame!")
                 # Tentar identificar qual módulo falhou
                 try: pygame.display.init()
                 except pygame.error as e: print(f" - Display: {e}")
                 try: pygame.font.init() # Fontes também são importantes
                 except pygame.error as e: print(f" - Font: {e}")
                 # Adicione outros se necessário (mixer)
                 raise RuntimeError("Falha na inicialização de módulos Pygame.")

            # Inicializar módulo de fontes separadamente (redundante se pygame.init() teve sucesso, mas seguro)
            pygame.font.init()
            if not pygame.font.get_init():
                 raise RuntimeError("Falha na inicialização do módulo de fontes (pygame.font).")
            print("DEBUG: Pygame e Fontes inicializados.")

        except Exception as e:
            print(f"ERRO CRÍTICO durante a inicialização do Pygame: {e}")
            sys.exit()

        # Configurações básicas da tela
        try:
            self.tela = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
            self.LARGURA, self.ALTURA = self.tela.get_size()
            pygame.display.set_caption("Meu Jogo")
            print(f"DEBUG: Tela criada: {self.LARGURA}x{self.ALTURA}")
        except pygame.error as e:
            print(f"ERRO ao criar a tela: {e}")
            pygame.quit()
            sys.exit()

        # Configurações de Jogo
        self.FPS = 60
        self.relogio = pygame.time.Clock()


        # Cores
        self.TRANSPARENTE = (0, 0, 0, 0)
        self.BRANCO = (255, 255, 255)
        self.AZUL = (0, 0, 255)
        self.VERMELHO = (255, 0, 0)
        self.MARROM = (139, 69, 19)
        self.PRETO = (0, 0, 0)

        # Estado Inicial do Jogo
        self.game_state = "MENU"

        # Cache de Fontes
        self.default_font = None
        self.fonts = {}

        # Carregar recursos da UI (Corações, Poções)
        try:
            # Assumindo que as imagens UI estão na raiz ou em 'img/ui/'
            # Ajuste os paths conforme necessário
            base_path_ui = "img/ui" # Mude para "" se estiverem na raiz
            if not os.path.isdir(base_path_ui):
                 base_path_ui = "" # Tenta a raiz se a pasta não existir

            coracao_path = os.path.join(base_path_ui, "coracao_cheio.png")
            coracao_v_path = os.path.join(base_path_ui, "coracao_vazio.png")
            pocao_c_path = os.path.join(base_path_ui, "pocao_cheia.png")
            pocao_v_path = os.path.join(base_path_ui, "pocao_vazia.png")

            self.coracao_cheio = pygame.image.load(coracao_path).convert_alpha()
            self.coracao_vazio = pygame.image.load(coracao_v_path).convert_alpha()
            self.coracao_cheio = pygame.transform.scale(self.coracao_cheio, (40, 40))
            self.coracao_vazio = pygame.transform.scale(self.coracao_vazio, (40, 40))

            self.pocao_cheia = pygame.image.load(pocao_c_path).convert_alpha()
            self.pocao_vazia = pygame.image.load(pocao_v_path).convert_alpha()
            self.pocao_cheia = pygame.transform.scale(self.pocao_cheia, (40, 40))
            self.pocao_vazia = pygame.transform.scale(self.pocao_vazia, (40, 40))
            print(f"DEBUG: Imagens da UI carregadas (buscadas em '{base_path_ui}').")
        except (pygame.error, FileNotFoundError) as e:
            print(f"AVISO: Erro ao carregar imagens da UI (coração/poção): {e}")
            print("       Verifique os paths das imagens .png.")
            self.coracao_cheio = self.coracao_vazio = self.pocao_cheia = self.pocao_vazia = None


        # Criar instâncias dos menus (sem options_menu)
        try:
            self.main_menu = MainMenu(self)
            self.credits_menu = CreditsMenu(self)
            print("DEBUG: Instâncias do Menu (MainMenu, CreditsMenu) criadas.")
        except Exception as e:
             print(f"ERRO CRÍTICO ao criar instâncias do Menu: {e}")
             print("Verifique o código em 'menu.py' e se ele consegue carregar seus próprios recursos.")
             self.quit_game()


        # --- Variáveis do Jogo (inicializadas como None/Vazio) ---
        self.tmx_data = None
        self.largura_mapa = 0
        # self.altura_mapa = 0 # Removida, usaremos altura_mapa_real
        self.altura_mapa_real = 0 # Adicionado para clareza
        self.altura_mapa_calculada_original = 0 # Mantido por compatibilidade se usado em start_game
        self.zoom_level = 2.0
        self.colisao_rects = []
        self.rampas_esquerda_rects = []
        self.rampas_direita_rects = []
        self.buraco_rects = []
        self.jogador = None
        self.inimigos = pygame.sprite.Group()
        self.todos_sprites = pygame.sprite.Group()
        self.mapa_atual = "mapa1"
        self.deslocamento_camera_x = 0
        self.deslocamento_camera_y = 0
        self.mostrar_popup = False
        self.popup_mensagem = ""
        self.popup_timer = 0
        self.popup_duracao = 1000
        self.mensagem = "teste"

        # Dicionário de SPRITES (mantido do código original)
        # O carregamento real das imagens deve ocorrer nas classes Player/Inimigo
        self.SPRITES = {
            "enemyidle": {"file": "img/mapa1/inimigo1/inimigo1_andando.png", "frames": 3, "width": 445, "height": 394},
            "idle": {"file": "img/prota/parada.png", "frames": 6, "width": 176, "height": 148},
            "walk": {"file": "img/prota/andando.png", "frames": 10, "width": 198, "height": 144},
            "pulo": {"file": "img/prota/pulo.png", "frames": 15, "width": 256, "height": 256},
            "dash": {"file": "img/prota/dash.png", "frames": 5, "width": 214, "height": 144},
            "attack1": {"file": "img/prota/attack1.png", "frames": 6, "width": 339, "height": 402},
            "attack2": {"file": "img/prota/attack2.png", "frames": 7, "width": 339, "height": 402},
            "attack3": {"file": "img/prota/attack3.png", "frames": 8, "width": 339, "height": 402}
        }
        print("DEBUG: Game.__init__ concluído.")

    # --- Funções Auxiliares de Desenho e Lógica ---

    # --- Função get_font (mantida como estava na última versão que aceita font_name) ---
    def get_font(self, font_name, size):
        if not pygame.font.get_init(): pygame.font.init()
        key = (font_name, size)
        if key not in self.fonts:
            try:
                if font_name is None or not font_name:
                    print(f"DEBUG: Usando SysFont (tamanho {size}).")
                    self.fonts[key] = pygame.font.SysFont(None, size)
                else:
                    if not os.path.exists(font_name):
                        raise FileNotFoundError(f"Arquivo de fonte não encontrado em get_font: '{font_name}'")
                    print(f"DEBUG: Tentando carregar Font '{font_name}' (tamanho {size}).")
                    self.fonts[key] = pygame.font.Font(font_name, size)
            except FileNotFoundError as e:
                 print(f"!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
                 print(f"AVISO: ARQUIVO DE FONTE NÃO ENCONTRADO: {e}")
                 print(f"       Verifique se a pasta 'fonts' existe e contém o arquivo TTF.")
                 print(f"       Usando fonte padrão do sistema (SysFont).")
                 print(f"!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
                 self.fonts[key] = pygame.font.SysFont(None, size) # Fallback
            except pygame.error as e:
                 print(f"AVISO: Erro Pygame ao carregar fonte '{font_name}' (tamanho {size}): {e}. Usando SysFont.")
                 self.fonts[key] = pygame.font.SysFont(None, size) # Fallback
            except Exception as e:
                 print(f"AVISO: Erro inesperado ao carregar fonte '{font_name}': {e}. Usando SysFont.")
                 self.fonts[key] = pygame.font.SysFont(None, size) # Fallback
        return self.fonts[key]

    # --- Função draw_text (mantida como estava na última versão que aceita font_name) ---
    def draw_text(self, text, size, x, y, color=(255, 255, 255), font_name=None):
        if font_name:
            font_path = os.path.join(os.path.dirname(__file__), font_name)
            font = pygame.font.Font(font_path, size)
        else:
            font = pygame.font.SysFont(None, size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        text_rect.center = (x, y)
        self.tela.blit(text_surface, text_rect)

    # --- Funções desenhar_coracoes, desenhar_pocoes, exibir_mensagem_final, exibir_popup_cura ---
    # (Mantidas como estavam na última versão)
    def desenhar_coracoes(self):
        if not self.jogador or self.coracao_cheio is None: return
        x, y = 20, 20; espacamento = 50
        for i in range(self.jogador.vida_maxima):
            img = self.coracao_cheio if i < self.jogador.vida_atual else self.coracao_vazio
            self.tela.blit(img, (x + i * espacamento, y))

    def desenhar_pocoes(self):
        if not self.jogador or self.pocao_cheia is None: return
        x = self.LARGURA - 20 - (self.jogador.curas_maximas * 40) - ((self.jogador.curas_maximas - 1) * 10)
        y = 20; espacamento = 50
        for i in range(self.jogador.curas_maximas):
            img = self.pocao_cheia if i < self.jogador.curas_restantes else self.pocao_vazia
            self.tela.blit(img, (x + i * espacamento, y))

    def exibir_mensagem_final(self, mensagem, cor):
        overlay = pygame.Surface((self.LARGURA, self.ALTURA), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180)); self.tela.blit(overlay, (0, 0))
        self.draw_text(mensagem, 74, self.LARGURA // 2, self.ALTURA // 2, color=cor) # Usa draw_text da classe
        pygame.display.flip(); pygame.time.wait(3000)
        self.game_state = "MENU"

    def exibir_popup_cura(self):
        try:
            # Usa get_font sem nome para usar a fonte padrão/fallback
            fonte = self.get_font(None, 30)
            texto = fonte.render(self.popup_mensagem, True, self.BRANCO)
            texto_rect = texto.get_rect(center=(self.LARGURA // 2, self.ALTURA - 50))
            pygame.draw.rect(self.tela, self.PRETO, texto_rect.inflate(20, 10), border_radius=5)
            self.tela.blit(texto, texto_rect)
        except Exception as e: print(f"Erro ao exibir popup de cura: {e}")

    # --- Função desenhar_mapa_com_zoom (mantida como estava na última versão) ---
    def desenhar_mapa_com_zoom(self):
        if not self.tmx_data: return
        camadas_para_desenhar = [
            "Background", "Fundo", "Chão", "RampaParaEsquerda",
            "RampaParaDireita","FiguraPorta", "Espinho_Maior", "Espinho_Menor"
        ]
        for nome_camada in camadas_para_desenhar:
            try: layer = self.tmx_data.get_layer_by_name(nome_camada)
            except ValueError: continue
            if hasattr(layer, 'tiles'):
                for x, y, gid in layer:
                    tile = self.tmx_data.get_tile_image_by_gid(gid)
                    if tile:
                        try:
                            lw = int(self.tmx_data.tilewidth * self.zoom_level)
                            lh = int(self.tmx_data.tileheight * self.zoom_level)
                            if self.zoom_level != 1.0 and lw > 0 and lh > 0: tile_s = pygame.transform.scale(tile, (lw, lh))
                            else: tile_s = tile
                            px = x * self.tmx_data.tilewidth * self.zoom_level + self.deslocamento_camera_x
                            py = y * self.tmx_data.tileheight * self.zoom_level + self.deslocamento_camera_y
                            tr = pygame.Rect(px, py, lw, lh)
                            if tr.colliderect(self.tela.get_rect()): self.tela.blit(tile_s, (px, py))
                        except (ValueError, pygame.error): pass
            elif isinstance(layer, pygame.Surface):
                 try:
                     lw = int(layer.get_width() * self.zoom_level); lh = int(layer.get_height() * self.zoom_level)
                     if lw > 0 and lh > 0: layer_s = pygame.transform.scale(layer, (lw, lh)); self.tela.blit(layer_s, (self.deslocamento_camera_x, self.deslocamento_camera_y))
                 except (ValueError, pygame.error): pass
            elif hasattr(layer, 'image'):
                 try:
                     lw = int(layer.image.get_width() * self.zoom_level); lh = int(layer.image.get_height() * self.zoom_level)
                     if lw > 0 and lh > 0:
                          img_s = pygame.transform.scale(layer.image, (lw, lh))
                          ox = getattr(layer, 'offsetx', 0) * self.zoom_level; oy = getattr(layer, 'offsety', 0) * self.zoom_level
                          self.tela.blit(img_s, (ox + self.deslocamento_camera_x, oy + self.deslocamento_camera_y))
                 except (AttributeError, ValueError, pygame.error): pass
    # --- Fim das funções auxiliares ---

    def start_game(self):
        """Configura tudo para iniciar uma nova sessão de jogo."""
        print("DEBUG: Chamando start_game()")
        self.inimigos.empty(); self.todos_sprites.empty(); self.jogador = None
        self.tmx_data = carregar_mapa("Mapa.tmx")
        

        self.largura_mapa = self.tmx_data.width * self.tmx_data.tilewidth
        # --- Cálculo Original da Altura ---
        # Mantendo o cálculo original com * 1.5 para altura_mapa_calculada_original
        # Esta variável é usada nos limites das paredes e na criação dos inimigos originais
        self.altura_mapa_calculada_original = self.tmx_data.height * self.tmx_data.tileheight * 1.5
        # Calculando a altura real separadamente para os limites da câmera
        self.altura_mapa_real = self.tmx_data.height * self.tmx_data.tileheight
        # --- Fim Cálculo Altura ---

        # Criação de Rects (sem mudanças)
        try: self.colisao_rects = criar_mapa_rects(self.tmx_data, "Chão")
        except ValueError: self.colisao_rects = []; print("AVISO: Camada 'Chão' não encontrada.")
        try: self.rampas_esquerda_rects = criar_mapa_rects(self.tmx_data, "RampaParaEsquerda")
        except ValueError: self.rampas_esquerda_rects = []; print("AVISO: Camada 'RampaParaEsquerda' não encontrada.")
        try: self.rampas_direita_rects = criar_mapa_rects(self.tmx_data, "RampaParaDireita")
        except ValueError: self.rampas_direita_rects = []; print("AVISO: Camada 'RampaParaDireita' não encontrada.")
        try: self.buraco_rects = criar_objetos_retangulos(self.tmx_data, "Buraco")
        except ValueError: self.buraco_rects = []; print("AVISO: Objeto/Camada 'Buraco' não encontrado.")

        # Paredes de colisão originais (usando altura_mapa_calculada_original)
        espessura_parede = 1
        paredes_colisao = [
            pygame.Rect(0, 0, self.largura_mapa, espessura_parede),
            pygame.Rect(0, self.altura_mapa_calculada_original - espessura_parede, self.largura_mapa, espessura_parede),
            pygame.Rect(0, espessura_parede, espessura_parede, self.altura_mapa_calculada_original - 2 * espessura_parede),
            pygame.Rect(self.largura_mapa - espessura_parede, espessura_parede, espessura_parede, self.altura_mapa_calculada_original - 2 * espessura_parede)
        ]
        self.colisao_rects.extend(paredes_colisao)

        # Criação do Jogador (sem mudanças)
        try:
            self.jogador = Jogador(x=100, y=214, colisao_rects=self.colisao_rects,
                                   rampas_esquerda_rects=self.rampas_esquerda_rects,
                                   rampas_direita_rects=self.rampas_direita_rects,
                                   buraco_rects=self.buraco_rects, tmx_data=self.tmx_data,
                                   zoom_level=self.zoom_level)
            self.todos_sprites.add(self.jogador); print("DEBUG: Jogador criado.")
        except Exception as e: print(f"ERRO CRÍTICO ao criar Jogador: {e}"); self.game_state = "MENU"; return

        # Criação dos Inimigos (usando altura_mapa_calculada_original como no original)
        mapas_inimigos_orig = {
            "mapa1": {"inimigos": [
                inimigo.Inimigo1mp1(x=2950, y=0, jogador=self.jogador, colisao_rects=self.colisao_rects, tmx_data=self.tmx_data, largura_mapa=self.largura_mapa, altura_mapa=self.altura_mapa_calculada_original),
                inimigo.Inimigo1mp2(x=4150, y=214, jogador=self.jogador, colisao_rects=self.colisao_rects, tmx_data=None, largura_mapa=self.largura_mapa, altura_mapa=self.altura_mapa_calculada_original)
            ]}}
        try:
             lista_inimigos = mapas_inimigos_orig[self.mapa_atual]["inimigos"]
             self.inimigos.add(*lista_inimigos); self.todos_sprites.add(*lista_inimigos)
             print(f"DEBUG: {len(lista_inimigos)} inimigos criados.")
        except Exception as e: print(f"ERRO ao adicionar inimigos: {e}")

        # Reset final e mudança de estado
        self.deslocamento_camera_x = 0; self.deslocamento_camera_y = 0; self.mostrar_popup = False
        self.game_state = "PLAYING"; print("DEBUG: Estado definido para PLAYING.")

    def run(self):
        """Loop principal do jogo que gerencia estados, eventos, atualizações e desenho."""
        print("DEBUG: Iniciando loop principal (run)")
        executando = True
        while executando:
            self.relogio.tick(self.FPS)
            tempo_agora = pygame.time.get_ticks()
            eventos_frame = pygame.event.get()

            # --- Lógica de Estados ---
            if self.game_state == "MENU":
                next_state = self.main_menu.handle_input(eventos_frame)
                if next_state == "PLAYING": self.start_game()
                elif next_state == "CREDITS": self.game_state = "CREDITS"
                elif next_state == "QUIT": executando = False

            elif self.game_state == "CREDITS":
                next_state = self.credits_menu.handle_input(eventos_frame)
                if next_state == "MENU": self.game_state = "MENU"

            elif self.game_state == "PLAYING":
                if not self.jogador or not self.tmx_data:
                     print("ERRO: 'PLAYING' sem jogador/mapa. Voltando ao menu.")
                     self.game_state = "MENU"; continue

                # --- Processar Eventos do Jogo ---
                for evento in eventos_frame:
                    if evento.type == pygame.QUIT: executando = False
                    if evento.type == pygame.KEYDOWN:
                        if evento.key == pygame.K_ESCAPE: self.game_state = "MENU"
                        elif evento.key == pygame.K_e:
                            curou = self.jogador.recuperar_vida()
                            self.mostrar_popup = True
                            self.popup_mensagem = "Vida recuperada!" if curou else "Você não pode curar mais!"
                            self.popup_timer = tempo_agora + self.popup_duracao
                        elif evento.key == pygame.K_LSHIFT or evento.key == pygame.K_RSHIFT: self.jogador.iniciar_dash()
                        elif evento.key == pygame.K_z: self.jogador.atacar(list(self.inimigos))

                # --- Atualizações do Jogo ---
                self.jogador.atualizar(self.inimigos)
                self.jogador.update_animation()
                for inimigo_atual in self.inimigos:
                    if isinstance(inimigo_atual, Inimigo1mp2): inimigo_atual.update(); inimigo_atual.detectar_jogador()
                    else: inimigo_atual.update()
                try:
                    layer_m = self.tmx_data.get_layer_by_name("Espinho_Maior"); layer_p = self.tmx_data.get_layer_by_name("Espinho_Menor")
                    self.jogador.handle_espinho_colisions(layer_m, layer_p)
                except ValueError: pass
                except AttributeError as e: print(f"Erro: {e}"); self.game_state = "MENU"; continue

                # --- Checar Derrota ---
                if self.jogador.vida_atual <= 0:
                    msg = "Você caiu no buraco!! Perdeu" if hasattr(self.jogador, 'caiu_no_buraco') and self.jogador.caiu_no_buraco else "Você Perdeu!"
                    cor = self.VERMELHO if "buraco" in msg else self.BRANCO
                    self.exibir_mensagem_final(msg, cor); continue

            # --- Desenho ---
            self.tela.fill(self.PRETO)

            if self.game_state == "MENU": self.main_menu.display_menu()
            elif self.game_state == "CREDITS": self.credits_menu.display_menu()
            elif self.game_state == "PLAYING":
                if self.jogador and self.tmx_data:

                    # ===========================================================
                    # VVV CÂMERA EXATAMENTE COMO NO jogo.py VVV
                    # ===========================================================

                    # Ajuste da câmera
                    self.deslocamento_camera_x = self.LARGURA // 2 - self.jogador.rect.centerx * self.zoom_level
                    self.deslocamento_camera_y = self.ALTURA // 1.2 - self.jogador.rect.centery * self.zoom_level

                    # Restringir a câmera
                    largura_mapa_escalada = self.largura_mapa * self.zoom_level
                    # Usando altura_mapa_real para limitar corretamente a câmera ao fundo do mapa Tiled
                    altura_mapa_escalada = self.altura_mapa_real * self.zoom_level

                    # Limites aplicados na mesma ordem do jogo.py
                    self.deslocamento_camera_x = min(self.deslocamento_camera_x, 0)
                    self.deslocamento_camera_x = max(self.deslocamento_camera_x, self.LARGURA - largura_mapa_escalada)
                    self.deslocamento_camera_y = min(self.deslocamento_camera_y, 0)
                    self.deslocamento_camera_y = max(self.deslocamento_camera_y, self.ALTURA - altura_mapa_escalada)

                    # ===========================================================
                    # ^^^ FIM DA SEÇÃO DA CÂMERA DO jogo.py ^^^
                    # ===========================================================

                    # --- Desenhar Jogo (mapa, inimigos, jogador) ---
                    self.desenhar_mapa_com_zoom()
                    for sprite in self.todos_sprites: # Desenha todos (jogador e inimigos) de uma vez
                         try:
                              # Escala baseada no rect do sprite individual
                              scaled_w = int(sprite.rect.width * self.zoom_level)
                              scaled_h = int(sprite.rect.height * self.zoom_level)
                              if scaled_w > 0 and scaled_h > 0:
                                   img_s = pygame.transform.scale(sprite.image, (scaled_w, scaled_h))
                                   px = sprite.rect.x * self.zoom_level + self.deslocamento_camera_x
                                   py = sprite.rect.y * self.zoom_level + self.deslocamento_camera_y
                                   self.tela.blit(img_s, (px, py))
                         except (AttributeError, ValueError, pygame.error): pass # Ignora erros de sprite/desenho

                    # --- Desenhar UI (corações, poções, popup) ---
                    self.desenhar_coracoes()
                    self.desenhar_pocoes()
                    if self.mostrar_popup and tempo_agora < self.popup_timer: self.exibir_popup_cura()
                    elif self.mostrar_popup and tempo_agora >= self.popup_timer: self.mostrar_popup = False

            # Atualizar a tela inteira
            pygame.display.flip()

        # Fim do loop while executando
        self.quit_game()

    def quit_game(self):
        """Encerra o Pygame e sai do programa."""
        print("DEBUG: Chamando quit_game()")
        pygame.quit()
        sys.exit()

# --- Ponto de Entrada Principal ---
if __name__ == '__main__':
    print("DEBUG: Executando Bloco Principal (__name__ == '__main__')")
    if not pygame.get_init(): print("ERRO FATAL: Pygame não inicializado. Saindo."); sys.exit()
    if not pygame.font.get_init(): print("ERRO FATAL: Pygame Font não inicializado. Saindo."); sys.exit()

    game_instance = None
    try:
        game_instance = Game()
        game_instance.run()
    except Exception as e:
         print("\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
         print(f"ERRO NÃO TRATADO NO NÍVEL SUPERIOR: {e}")
         import traceback; traceback.print_exc()
         print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n")
    finally:
        # Garante que Pygame finalize mesmo em caso de erro
        if pygame.get_init(): print("DEBUG: Saindo pelo bloco finally, chamando pygame.quit()"); pygame.quit()

# --- END OF FILE main.py ---