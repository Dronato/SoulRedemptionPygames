# --- START OF FILE main.py ---

import pygame
import sys
import os

# Importar componentes do jogo
import player
import inimigo
# Ajuste os imports de inimigo conforme necessário
from inimigo import Inimigo1mp1, Inimigo1mp2 # Exemplo para mapa 1
from npc import NPC_Andy, NPC_Rafa
# from inimigo import InimigoTipoA, InimigoTipoB # Exemplo para mapa 2 (precisaria existir em inimigo.py)
from map_loader import carregar_mapa, desenhar_mapa, criar_mapa_rects, criar_objetos_retangulos

pygame.init()
pygame.font.init()

try:
    from menu import MainMenu, CreditsMenu
except ImportError:
    print("---------------------------------------------------------")
    print("ERRO: Não foi possível encontrar ou importar 'menu.py'.")
    print("Certifique-se de que o arquivo 'menu.py' com as classes")
    print("MainMenu e CreditsMenu está na mesma pasta")
    print("que este arquivo 'main.py'.")
    print("---------------------------------------------------------")
    pygame.quit()
    sys.exit()
except Exception as e:
    print(f"Erro inesperado ao importar 'menu.py': {e}")
    pygame.quit()
    sys.exit()

class Game:
    def __init__(self):
        """Inicializa o Pygame, a tela, e as configurações gerais."""
        print("DEBUG: Iniciando Game.__init__")
        if not pygame.get_init():
            raise RuntimeError("Pygame não foi inicializado corretamente antes de Game.__init__")
        if not pygame.font.get_init():
             raise RuntimeError("Pygame Font não foi inicializado corretamente antes de Game.__init__")

        try:
            self.tela = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
            self.LARGURA, self.ALTURA = self.tela.get_size()
            pygame.display.set_caption("Soul Redemption") # Mudar nome
            print(f"DEBUG: Tela criada: {self.LARGURA}x{self.ALTURA}")
        except pygame.error as e:
            print(f"ERRO ao criar a tela: {e}")
            pygame.quit()
            sys.exit()

        self.FPS = 60
        self.relogio = pygame.time.Clock()

        self.TRANSPARENTE = (0, 0, 0, 0)
        self.BRANCO = (255, 255, 255)
        self.AZUL = (0, 0, 255)
        self.VERMELHO = (255, 0, 0)
        self.MARROM = (139, 69, 19)
        self.PRETO = (0, 0, 0)
        self.AMARELO = (255, 255, 0)

        self.game_state = "MENU"
        self.fonts = {}
        self.default_font_name = None

        try:
            # Tenta encontrar uma fonte específica na pasta 'fonts'
            font_path_teste = os.path.join("fonts", "AncientModernTales.ttf") # <-- COLOQUE O NOME DA SUA FONTE TTF AQUI
            if os.path.exists(font_path_teste):
                 self.default_font_name = font_path_teste
                 print(f"DEBUG: Usando fonte padrão: {self.default_font_name}")
            else:
                 print("DEBUG: Fonte TTF padrão não encontrada, usando SysFont.")
        except Exception as e:
             print(f"AVISO: Erro ao tentar definir fonte padrão: {e}. Usando SysFont.")


        try:
            base_path_ui = "img/ui"
            if not os.path.isdir(base_path_ui): base_path_ui = ""

            coracao_path = os.path.join(base_path_ui, "coracao_cheio.png")
            coracao_v_path = os.path.join(base_path_ui, "coracao_vazio.png")
            pocao_c_path = os.path.join(base_path_ui, "pocao_cheia.png")
            pocao_v_path = os.path.join(base_path_ui, "pocao_vazia.png")

            ui_icon_size = (35, 35)

            self.coracao_cheio = pygame.image.load(coracao_path).convert_alpha()
            self.coracao_vazio = pygame.image.load(coracao_v_path).convert_alpha()
            self.coracao_cheio = pygame.transform.scale(self.coracao_cheio, ui_icon_size)
            self.coracao_vazio = pygame.transform.scale(self.coracao_vazio, ui_icon_size)

            self.pocao_cheia = pygame.image.load(pocao_c_path).convert_alpha()
            self.pocao_vazia = pygame.image.load(pocao_v_path).convert_alpha()
            self.pocao_cheia = pygame.transform.scale(self.pocao_cheia, ui_icon_size)
            self.pocao_vazia = pygame.transform.scale(self.pocao_vazia, ui_icon_size)
            print(f"DEBUG: Imagens da UI carregadas (buscadas em '{base_path_ui}').")
        except (pygame.error, FileNotFoundError) as e:
            print(f"AVISO: Erro ao carregar imagens da UI (coração/poção): {e}")
            self.coracao_cheio = self.coracao_vazio = self.pocao_cheia = self.pocao_vazia = None

        try:
            self.main_menu = MainMenu(self)
            self.credits_menu = CreditsMenu(self)
            print("DEBUG: Instâncias do Menu (MainMenu, CreditsMenu) criadas.")
        except Exception as e:
             print(f"ERRO CRÍTICO ao criar instâncias do Menu: {e}")
             self.quit_game()

        self.tmx_data = None
        self.largura_mapa = 0
        self.altura_mapa_real = 0
        self.zoom_level = 2.0

        self.colisao_rects = []
        self.rampas_esquerda_rects = []
        self.rampas_direita_rects = []
        self.buraco_rects = []
        self.porta_rects = []
        self.lava_rects = [] # Inicializa lista de rects de lava

        self.jogador = None
        self.inimigos = pygame.sprite.Group()
        self.todos_sprites = pygame.sprite.Group()

        # VARIAVEIS DA CONVERSA
        self.em_conversa = False
        self.tempo_conversa = 0
        self.duracao_conversa = 7000  # milissegundos (7 segundos)
        self.npc_A = None
        self.npc_F = None
        self.npc = None

        self.mapa_atual_path = "Mapa.tmx"
        self.proximo_mapa_path = "Mapa(2).tmx"

        self.deslocamento_camera_x = 0
        self.deslocamento_camera_y = 0

        self.mostrar_popup = False
        self.popup_mensagem = ""
        self.popup_timer = 0
        self.popup_duracao = 1500

        # fonte 
        self.arcane_font_path = os.path.join("ARCADE_N.ttf")

        self.mostrar_prompt_porta = False

        # Referências às camadas de perigo (serão preenchidas em start_game)
        self.espinho_maior_layer = None
        self.espinho_menor_layer = None

        print("DEBUG: Game.__init__ concluído.")

    # --- Funções Auxiliares ---

    def get_font(self, font_name, size):
        if not pygame.font.get_init(): pygame.font.init()
        key = (font_name, size)
        if key not in self.fonts:
            try:
                effective_font_name = font_name if font_name else self.default_font_name
                if effective_font_name and os.path.exists(effective_font_name):
                    self.fonts[key] = pygame.font.Font(effective_font_name, size)
                else:
                    if effective_font_name:
                         print(f"AVISO: Fonte '{effective_font_name}' não encontrada ou inválida. Usando SysFont.")
                    self.fonts[key] = pygame.font.SysFont(None, size)
            except pygame.error as e:
                 print(f"AVISO: Erro Pygame ao carregar fonte '{effective_font_name}' (tamanho {size}): {e}. Usando SysFont.")
                 self.fonts[key] = pygame.font.SysFont(None, size)
            except Exception as e:
                 print(f"AVISO: Erro inesperado ao carregar fonte '{effective_font_name}': {e}. Usando SysFont.")
                 self.fonts[key] = pygame.font.SysFont(None, size)
        return self.fonts[key]


    def draw_text(self, text, size, x, y, color, font_name=None, center=False):
        try:
            font = pygame.font.Font(font_name, size) if font_name else pygame.font.SysFont(None, size)
            text_surface = font.render(text, True, color)
            text_rect = text_surface.get_rect()
            if center:
                text_rect.center = (x, y)
            else:
                text_rect.topleft = (x, y)
            self.tela.blit(text_surface, text_rect)
        except Exception as e:
            print(f"ERRO ao desenhar texto '{text}': {e}")
            try:
                fallback_font = pygame.font.SysFont(None, size)
                error_surface = fallback_font.render("ERR", True, self.VERMELHO)
                error_rect = error_surface.get_rect(center=(int(x), int(y)))
                self.tela.blit(error_surface, error_rect)
            except: pass


    def desenhar_coracoes(self):
        if not self.jogador or self.coracao_cheio is None: return
        x_inicial, y_inicial = 15, 15
        espacamento = 40
        for i in range(self.jogador.vida_maxima):
            img_para_desenhar = self.coracao_cheio if i < self.jogador.vida_atual else self.coracao_vazio
            pos_x = x_inicial + i * espacamento
            self.tela.blit(img_para_desenhar, (pos_x, y_inicial))

    def desenhar_pocoes(self):
        if not self.jogador or self.pocao_cheia is None: return
        icon_width = self.pocao_cheia.get_width()
        espacamento = 10
        total_width = (self.jogador.curas_maximas * icon_width) + ((self.jogador.curas_maximas - 1) * espacamento)
        x_inicial = self.LARGURA - 15 - total_width
        y_inicial = 15
        for i in range(self.jogador.curas_maximas):
            img_para_desenhar = self.pocao_cheia if i < self.jogador.curas_restantes else self.pocao_vazia
            pos_x = x_inicial + i * (icon_width + espacamento)
            self.tela.blit(img_para_desenhar, (pos_x, y_inicial))

    def exibir_mensagem_final(self, mensagem, cor):
        overlay = pygame.Surface((self.LARGURA, self.ALTURA), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.tela.blit(overlay, (0, 0))
        self.draw_text(mensagem, 74, self.LARGURA // 2, self.ALTURA // 2, color=cor, font_name=self.default_font_name)
        pygame.display.flip()
        pygame.time.wait(3000)
        self.game_state = "MENU"
        
    # MENSAGEM NPC
    def exibir_mensagem_npc(self, mensagem, cor):
        overlay = pygame.Surface((self.LARGURA, self.ALTURA), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180)); self.tela.blit(overlay, (0, 0))
        self.draw_text(mensagem, 74, self.LARGURA // 2, self.ALTURA // 2, color=cor) # Usa draw_text da classe
        pygame.display.flip(); pygame.time.wait(3000)
        # self.game_state = "PLAYING"

    def exibir_popup(self, mensagem):
        self.popup_mensagem = mensagem
        self.mostrar_popup = True
        self.popup_timer = pygame.time.get_ticks() + self.popup_duracao

    def desenhar_popup(self):
        if self.mostrar_popup and pygame.time.get_ticks() < self.popup_timer:
             try:
                 fonte_size = 28
                 fonte = self.get_font(self.default_font_name, fonte_size)
                 texto_surface = fonte.render(self.popup_mensagem, True, self.BRANCO)
                 texto_rect = texto_surface.get_rect(center=(self.LARGURA // 2, self.ALTURA - 60))

                 bg_rect = texto_rect.inflate(20, 10)
                 bg_surface = pygame.Surface(bg_rect.size, pygame.SRCALPHA)
                 bg_surface.fill((50, 50, 50, 200))
                 pygame.draw.rect(bg_surface, self.BRANCO, bg_surface.get_rect(), 1, border_radius=5)

                 self.tela.blit(bg_surface, bg_rect.topleft)
                 self.tela.blit(texto_surface, texto_rect)
             except Exception as e:
                 print(f"Erro ao exibir popup: {e}")
                 self.mostrar_popup = False
        elif self.mostrar_popup and pygame.time.get_ticks() >= self.popup_timer:
             self.mostrar_popup = False


    def desenhar_mapa_com_zoom(self):
        """Desenha as camadas visíveis do mapa com zoom e otimização."""
        if not self.tmx_data: return

        camadas_mapa_atual = []
        if self.mapa_atual_path == "Mapa.tmx":
            # Camadas visuais do Mapa 1 (confirmar ordem)
            camadas_mapa_atual = [
                "Background", "Fundo", "Chão", "RampaParaEsquerda",
                "RampaParaDireita","FiguraPorta", "Espinho_Maior", "Espinho_Menor",
            ]
        elif self.mapa_atual_path == "Mapa(2).tmx":
            # Camadas visuais do Mapa 2
            # A ordem importa! Desenha do fundo para a frente.
            camadas_mapa_atual = [
                "Background",          # Camada de imagem de fundo
                "Detalhes",            # Tiles decorativos (sem colisão)
                "Fundo",               # Tiles sólidos (desenhados)
                               # Tiles de lava (desenhados, mas sem colisão sólida)
                "Representacao_Porta",
                "Lava"
                # Tiles da porta (sem colisão)
            ]
        else:
            print(f"AVISO: Nenhuma camada de desenho definida para o mapa: {self.mapa_atual_path}")

        # Área visível na tela (em coordenadas do mundo) para otimização (culling)
        tela_rect_mundo = pygame.Rect(
            -self.deslocamento_camera_x / self.zoom_level,
            -self.deslocamento_camera_y / self.zoom_level,
            self.LARGURA / self.zoom_level,
            self.ALTURA / self.zoom_level
        )

        for nome_camada in camadas_mapa_atual:
            try:
                layer = self.tmx_data.get_layer_by_name(nome_camada)
            except ValueError:
                continue # Pula para a próxima camada

            # Camadas de Tiles
            if hasattr(layer, 'tiles'):
                tile_w_orig = self.tmx_data.tilewidth
                tile_h_orig = self.tmx_data.tileheight
                tile_w_scaled = int(tile_w_orig * self.zoom_level)
                tile_h_scaled = int(tile_h_orig * self.zoom_level)

                if tile_w_scaled <= 0 or tile_h_scaled <= 0: continue

                for x, y, gid in layer:
                    if gid == 0: continue
                    tile_mundo_rect = pygame.Rect(x * tile_w_orig, y * tile_h_orig, tile_w_orig, tile_h_orig)
                    # Otimização: Verificar se o tile está na área visível
                    if not tela_rect_mundo.colliderect(tile_mundo_rect):
                        continue

                    tile_image = self.tmx_data.get_tile_image_by_gid(gid)
                    if tile_image:
                        try:
                            if self.zoom_level != 1.0:
                                tile_scaled = pygame.transform.scale(tile_image, (tile_w_scaled, tile_h_scaled))
                            else:
                                tile_scaled = tile_image
                            pos_x_tela = tile_mundo_rect.x * self.zoom_level + self.deslocamento_camera_x
                            pos_y_tela = tile_mundo_rect.y * self.zoom_level + self.deslocamento_camera_y
                            self.tela.blit(tile_scaled, (pos_x_tela, pos_y_tela))
                        except (ValueError, pygame.error) as scale_error:
                            # print(f"Erro ao escalar tile da camada '{nome_camada}': {scale_error}")
                            pass # Ignora o tile problemático

            # Camadas de Imagem
            elif hasattr(layer, 'image'):
                 try:
                     img_orig = layer.image
                     img_w_orig, img_h_orig = img_orig.get_size()
                     img_w_scaled = int(img_w_orig * self.zoom_level)
                     img_h_scaled = int(img_h_orig * self.zoom_level)
                     if img_w_scaled <= 0 or img_h_scaled <= 0: continue

                     offset_x_orig = getattr(layer, 'offsetx', 0)
                     offset_y_orig = getattr(layer, 'offsety', 0)
                     img_mundo_rect = pygame.Rect(offset_x_orig, offset_y_orig, img_w_orig, img_h_orig)

                     # Otimização de visibilidade
                     if not tela_rect_mundo.colliderect(img_mundo_rect):
                         continue

                     if self.zoom_level != 1.0:
                         img_scaled = pygame.transform.scale(img_orig, (img_w_scaled, img_h_scaled))
                     else:
                         img_scaled = img_orig

                     pos_x_tela = offset_x_orig * self.zoom_level + self.deslocamento_camera_x
                     pos_y_tela = offset_y_orig * self.zoom_level + self.deslocamento_camera_y
                     self.tela.blit(img_scaled, (pos_x_tela, pos_y_tela))
                 except (AttributeError, ValueError, pygame.error) as img_layer_error:
                      print(f"Erro ao processar camada de imagem '{nome_camada}': {img_layer_error}")
                      pass


    def start_game(self, map_path):
        """Configura e carrega os recursos para um mapa específico."""
        print(f"DEBUG: Chamando start_game() para o mapa: {map_path}")

        # --- 1. Resetar Estado Anterior ---
        self.inimigos.empty()
        self.todos_sprites.empty()
        self.jogador = None
        self.npc_A = None
        self.npc_F = None
        self.colisao_rects = []
        self.rampas_esquerda_rects = []
        self.rampas_direita_rects = []
        self.buraco_rects = []
        self.porta_rects = []
        self.lava_rects = [] # Resetar lava rects também
        self.tmx_data = None
        self.largura_mapa = 0
        self.altura_mapa_real = 0
        self.espinho_maior_layer = None
        self.espinho_menor_layer = None

        # --- 2. Carregar Dados do Novo Mapa ---
        self.tmx_data = carregar_mapa(map_path)
        if not self.tmx_data:
            print(f"ERRO FATAL: Não foi possível carregar o mapa '{map_path}'. Voltando ao menu.")
            self.game_state = "MENU"
            return

        self.mapa_atual_path = map_path
        self.largura_mapa = self.tmx_data.width * self.tmx_data.tilewidth
        self.altura_mapa_real = self.tmx_data.height * self.tmx_data.tileheight
        print(f"DEBUG: Mapa '{map_path}' carregado. Dimensões: {self.largura_mapa}x{self.altura_mapa_real} pixels.")

        # --- 3. Criar Retângulos de Colisão e Objetos (CONDICIONAL POR MAPA) ---
        print(f"DEBUG: Criando retângulos para {map_path}...")

        # Variáveis para nomes de camadas
        chao_layers = []
        rampa_e_layer = None
        rampa_d_layer = None
        buraco_layer = None
        porta_layer = None
        espinho_m_layer = None
        espinho_p_layer = None
        lava_layer = None # Nome da camada de lava para carregar os rects de perigo

        if map_path == "Mapa.tmx":
            # Camadas específicas do Mapa.tmx
            chao_layers = ["Chão"]
            rampa_e_layer = "RampaParaEsquerda"
            rampa_d_layer = "RampaParaDireita"
            buraco_layer = "Buraco" # Objeto
            porta_layer = "Porta"   # Objeto
            espinho_m_layer = "Espinho_Maior" # Tile
            espinho_p_layer = "Espinho_Menor" # Tile
            jogador_start_x, jogador_start_y = 100, 400

        elif map_path == "Mapa(2).tmx":
            # --- AJUSTE AQUI ---
            # Camadas sólidas: Apenas "Fundo"
            chao_layers = ["Fundo"]
            # -----------------
            # Sem rampas ou espinhos neste mapa (assumindo)
            rampa_e_layer = None
            rampa_d_layer = None
            espinho_m_layer = None
            espinho_p_layer = None
            # Camadas de perigo/interação
            buraco_layer = "Buraco" # Objeto
            porta_layer = "Porta"   # Objeto
            lava_layer = "Lava"     # Tile (Perigo, não sólido)
            # Posição inicial
            jogador_start_x, jogador_start_y = 70, 1250 # Ajuste conforme necessário

        else:
            print(f"ERRO: Configuração de camadas não definida para o mapa '{map_path}' em start_game.")
            # Fallback
            chao_layers = ["Chão"]
            buraco_layer = "Buraco"; porta_layer = "Porta"
            jogador_start_x, jogador_start_y = 100, 100

        # --- Carregar os rects ---
        # Colisões sólidas
        self.colisao_rects = []
        for layer_name in chao_layers:
            if layer_name:
                print(f"DEBUG: Carregando colisões sólidas da camada: {layer_name}")
                self.colisao_rects.extend(criar_mapa_rects(self.tmx_data, layer_name))

        # Rampas
        if rampa_e_layer: self.rampas_esquerda_rects = criar_mapa_rects(self.tmx_data, rampa_e_layer)
        if rampa_d_layer: self.rampas_direita_rects = criar_mapa_rects(self.tmx_data, rampa_d_layer)

        # Objetos
        if buraco_layer: self.buraco_rects = criar_objetos_retangulos(self.tmx_data, buraco_layer)
        if porta_layer: self.porta_rects = criar_objetos_retangulos(self.tmx_data, porta_layer)

        # --- AJUSTE: Carregar Rects de Lava (Perigo) ---
        if lava_layer:
            print(f"DEBUG: Carregando retângulos de perigo (Lava) da camada: {lava_layer}")
            self.lava_rects = criar_mapa_rects(self.tmx_data, lava_layer)
        # ---------------------------------------------

        # Guardar referências às camadas de espinhos (para colisão em player.py)
        try:
            if espinho_m_layer: self.espinho_maior_layer = self.tmx_data.get_layer_by_name(espinho_m_layer)
        except ValueError: print(f"AVISO: Camada de tiles '{espinho_m_layer}' não encontrada.")
        try:
            if espinho_p_layer: self.espinho_menor_layer = self.tmx_data.get_layer_by_name(espinho_p_layer)
        except ValueError: print(f"AVISO: Camada de tiles '{espinho_p_layer}' não encontrada.")

        # Adicionar paredes limites
        espessura_parede = 5
        paredes_limite = [
            pygame.Rect(-espessura_parede, -espessura_parede, espessura_parede, self.altura_mapa_real + 2 * espessura_parede), # Esquerda
            pygame.Rect(self.largura_mapa, -espessura_parede, espessura_parede, self.altura_mapa_real + 2 * espessura_parede),    # Direita
            pygame.Rect(-espessura_parede, -espessura_parede, self.largura_mapa + 2 * espessura_parede, espessura_parede), # Topo
        ]
        self.colisao_rects.extend(paredes_limite)
        print(f"DEBUG: Total de {len(self.colisao_rects)} rects de colisão sólida (incluindo limites).")
        print(f"DEBUG: {len(self.rampas_esquerda_rects)} rampas esquerda, {len(self.rampas_direita_rects)} rampas direita.")
        print(f"DEBUG: {len(self.buraco_rects)} rects de buraco, {len(self.porta_rects)} rects de porta.")
        print(f"DEBUG: {len(self.lava_rects)} rects de lava (perigo).")

        # --- 4. Criar Jogador ---
        try:
            self.jogador = player.Jogador(
                x=jogador_start_x, y=jogador_start_y,
                colisao_rects=self.colisao_rects,
                rampas_esquerda_rects=self.rampas_esquerda_rects,
                rampas_direita_rects=self.rampas_direita_rects,
                buraco_rects=self.buraco_rects,
                lava_rects=self.lava_rects, # <-- PASSAR OS RECTS DA LAVA
                tmx_data=self.tmx_data,
                zoom_level=self.zoom_level
            )
            self.todos_sprites.add(self.jogador)
            print(f"DEBUG: Jogador criado na posição ({jogador_start_x}, {jogador_start_y}).")
        except Exception as e:
            print(f"ERRO CRÍTICO ao criar Jogador: {e}")
            import traceback; traceback.print_exc()
            self.game_state = "MENU"
            return
        

        # --- 5. Criar Inimigos (CONDICIONAL POR MAPA) ---
        print(f"DEBUG: Criando inimigos para {map_path}...")
        lista_inimigos_mapa = []
        if map_path == "Mapa.tmx":
            # Fazer NPC
            try:
                self.npc_A = NPC_Andy(x=208, y=398, zoom_level=self.zoom_level)
                self.npc_F = NPC_Rafa(x=5667, y=398, zoom_level=self.zoom_level)
                self.todos_sprites.add(self.npc_A, self.npc_F)
                print("DEBUG: NPCs criados no Mapa 1.")
            except Exception as e:
                print(f"ERRO CRÍTICO ao criar NPCs no Mapa 1: {e}")
                self.game_state = "MENU"
                return
            
            try:
                inimigo1 = inimigo.Inimigo1mp1(x=2950, y=0, jogador=self.jogador, colisao_rects=self.colisao_rects, tmx_data=self.tmx_data, largura_mapa=self.largura_mapa, altura_mapa=self.altura_mapa_real)
                inimigo2 = inimigo.Inimigo1mp2(x=4150, y=214, jogador=self.jogador, colisao_rects=self.colisao_rects, tmx_data=self.tmx_data, largura_mapa=self.largura_mapa, altura_mapa=self.altura_mapa_real)
                lista_inimigos_mapa.extend([inimigo1, inimigo2])
            except Exception as e: print(f"ERRO ao criar inimigos para Mapa.tmx: {e}")

        elif map_path == "Mapa(2).tmx":
             # TODO: ADICIONE AQUI A CRIAÇÃO DOS INIMIGOS PARA O MAPA 2
             print("TODO: Adicionar criação de inimigos para Mapa(2).tmx")
             # Exemplo:
             # try:
             #     inimigoA = inimigo.InimigoTipoA(x=500, y=300, ...)
             #     inimigoB = inimigo.InimigoTipoB(x=1200, y=350, ...)
             #     lista_inimigos_mapa.extend([inimigoA, inimigoB])
             # except NameError: print("ERRO: Classes InimigoTipoA/B não encontradas em inimigo.py")
             # except Exception as e: print(f"ERRO ao criar inimigos para Mapa(2).tmx: {e}")
             pass

        if lista_inimigos_mapa:
             self.inimigos.add(*lista_inimigos_mapa)
             self.todos_sprites.add(*lista_inimigos_mapa)
             print(f"DEBUG: {len(lista_inimigos_mapa)} inimigos adicionados ao mapa.")
        else:
            print("DEBUG: Nenhum inimigo definido ou criado para este mapa.")
        

        # --- 6. Resetar Câmera e Estado Final ---
        self.deslocamento_camera_x = 0
        self.deslocamento_camera_y = 0
        self.mostrar_popup = False
        self.mostrar_prompt_porta = False
        self.mostrar_msg_npc = False
        self.game_state = "PLAYING"
        print(f"DEBUG: start_game concluído. Estado definido para PLAYING.")


    def exibir_conversa(self):
    # Escurece o fundo
        overlay = pygame.Surface((self.LARGURA, self.ALTURA), pygame.SRCALPHA)
        overlay.fill((60, 60, 60, 10))
        self.tela.blit(overlay, (0, 0))

        if self.npc:  # Verifica se há um NPC com quem conversar
            self.npc.conversar(self.tela, self.LARGURA, self.ALTURA)

        pygame.display.flip()
    
    def run(self):
        """Loop principal do jogo que gerencia estados, eventos, atualizações e desenho."""
        print("DEBUG: Iniciando loop principal (run)")
        executando = True
        while executando:
            delta_time = self.relogio.tick(self.FPS) / 1000.0
            tempo_agora = pygame.time.get_ticks()
            eventos_frame = pygame.event.get()

            # --- Lógica de Estados ---
            if self.game_state == "MENU":
                next_state = self.main_menu.handle_input(eventos_frame)
                if next_state == "PLAYING":
                    self.start_game(self.mapa_atual_path)
                    if self.game_state != "PLAYING": continue
                elif next_state == "CREDITS": self.game_state = "CREDITS"
                elif next_state == "QUIT": executando = False

            elif self.game_state == "CREDITS":
                next_state = self.credits_menu.handle_input(eventos_frame)
                if next_state == "MENU": self.game_state = "MENU"

            elif self.game_state == "PLAYING":
                if not self.jogador or not self.tmx_data:
                     print("ERRO GRAVE: Estado 'PLAYING' sem jogador ou tmx_data. Voltando ao menu.")
                     self.game_state = "MENU"; continue

                # --- Processar Eventos do Jogo ---
                colidindo_com_porta = False
                if self.porta_rects:
                     for porta in self.porta_rects:
                         if self.jogador.collision_rect.colliderect(porta):
                             self.mostrar_prompt_porta = True
                             colidindo_com_porta = True; break
                             
                # CODIGO PARA APARECER O TEXTO DE CONVERSA COM NPC
                if self.mapa_atual_path == "Mapa.tmx":
                    self.mostrar_msg_npc = False
                    npc_proximo = None
                    distancia_limite = 100  # Distância máxima para interação

                    jogador_x, jogador_y = self.jogador.rect.center

                    for npc in [self.npc_A, self.npc_F]:
                        npc_x, npc_y = npc.rect.center
                        distancia = ((jogador_x - npc_x) ** 2 + (jogador_y - npc_y) ** 2) ** 0.5

                        if distancia < distancia_limite:
                            self.mostrar_msg_npc = True
                            npc_proximo = npc
                            break

                    if npc_proximo:
                        self.npc = npc_proximo  
                    else:
                        self.npc = None  

                for evento in eventos_frame:
                    if evento.type == pygame.QUIT: executando = False
                    if evento.type == pygame.KEYDOWN:
                        if self.em_conversa and self.npc:
                            if evento.key == pygame.K_RIGHT:
                                self.npc.contador += 1
                                if self.npc.contador > self.npc.total_falas:
                                    self.em_conversa = False
                                    self.npc.contador = 1  

                            elif evento.key == pygame.K_LEFT:
                                if self.npc.contador > 1:
                                    self.npc.contador -= 1
                                else:
                                    self.npc.contador = 1  # Garante que não vá abaixo de 1
                        if evento.key == pygame.K_ESCAPE: self.game_state = "MENU"
                        elif evento.key == pygame.K_e: # Tecla 'E'
                             if colidindo_com_porta: # Se está na porta E pressionou E
                                 print(f"DEBUG: Interação com porta! Mapa atual: {self.mapa_atual_path}")
                                 mapa_a_carregar = None
                                 if self.mapa_atual_path == "Mapa.tmx":
                                     mapa_a_carregar = self.proximo_mapa_path # Vai para Mapa(2).tmx
                                     print(f"DEBUG: Tentando carregar: {mapa_a_carregar}")
                                 elif self.mapa_atual_path == "Mapa(2).tmx":
                                     # TODO: Definir para onde ir a partir do Mapa 2 (se houver)
                                     mapa_a_carregar = None # Ex: Fim ou voltar pro menu
                                     print("DEBUG: Fim do Mapa 2 ou transição não definida.")

                                 if mapa_a_carregar:
                                     self.start_game(mapa_a_carregar)
                                     if self.game_state != "PLAYING": executando = False
                                     continue # Pula para próximo frame após iniciar carregamento
                                 else:
                                     self.game_state = "MENU"; continue # Volta pro menu se não houver próximo mapa
                             else: # Se pressionou E sem estar na porta -> Cura
                                curou = self.jogador.recuperar_vida()
                                msg = "Vida recuperada!" if curou else "Não foi possível curar!"
                                self.exibir_popup(msg)
                        elif evento.key == pygame.K_LSHIFT or evento.key == pygame.K_RSHIFT: self.jogador.iniciar_dash()
                        elif evento.key == pygame.K_z: self.jogador.atacar(list(self.inimigos))
                        elif evento.key == pygame.K_f:
                                jogador_x, jogador_y = self.jogador.rect.center
                                npc_proximo = None
                                menor_distancia = float("inf")
                                for npc in [self.npc_A, self.npc_F]:
                                    npc_x, npc_y = npc.rect.center
                                    distancia = ((jogador_x - npc_x) ** 2 + (jogador_y - npc_y) ** 2) ** 0.5
                                    if distancia < 100 and distancia < menor_distancia:
                                        menor_distancia = distancia
                                        npc_proximo = npc

                                if npc_proximo:
                                    self.npc = npc_proximo
                                    self.em_conversa = True
                                                                       
                        # Debug keys...

                # --- Atualizações do Jogo ---
                if self.game_state == "PLAYING": # Checar de novo caso evento tenha mudado
                    # Atualizar Jogador (inclui checagem de buraco/lava agora)
                    self.jogador.atualizar(self.inimigos)
                    self.jogador.update_animation()
                    if self.em_conversa:
                        self.exibir_conversa()
                        continue 
                    if self.mapa_atual_path == "Mapa.tmx":
                        self.npc_A.atualizar()
                        self.npc_F.atualizar()
                    
                    # Atualizar Inimigos
                    for inimigo_atual in self.inimigos:
                        if hasattr(inimigo_atual, 'update') and callable(inimigo_atual.update):
                             inimigo_atual.update()

                    # Colisão com Espinhos (se o jogador ainda estiver vivo)
                    if self.jogador and self.jogador.vida_atual > 0:
                        self.jogador.handle_espinho_colisions(self.espinho_maior_layer, self.espinho_menor_layer)

                    # --- Checar Derrota ---
                    if self.jogador.vida_atual <= 0:
                        msg = "Você Perdeu!" # Mensagem padrão
                        cor = self.VERMELHO # Cor padrão

                        # Verificar causa específica da morte (acessando flags do jogador)
                        # Usar hasattr para segurança caso as flags não existam por algum motivo
                        if hasattr(self.jogador, 'morreu_queimado') and self.jogador.morreu_queimado:
                            msg = "Você morreu queimado!"
                            # cor = (255, 100, 0) # Laranja para queimado? (Opcional)
                        elif hasattr(self.jogador, 'caiu_no_buraco') and self.jogador.caiu_no_buraco:
                            msg = "Você caiu no buraco!"

                        self.exibir_mensagem_final(msg, cor)
                        continue # Pula o desenho deste frame e vai pro próximo loop (que estará no MENU)

                    # Checar Vitória...

            # --- Desenho ---
            self.tela.fill(self.PRETO) # Limpa a tela

            if self.game_state == "MENU":
                self.main_menu.display_menu()
            elif self.game_state == "CREDITS":
                self.credits_menu.display_menu()
            elif self.game_state == "PLAYING":
                if self.jogador and self.tmx_data:
                    # --- Cálculo da Câmera ---
                    target_x = self.jogador.rect.centerx
                    target_y = self.jogador.rect.centery
                    self.deslocamento_camera_x = self.LARGURA / 2 - target_x * self.zoom_level
                    largura_mapa_escalada = self.largura_mapa * self.zoom_level
                    self.deslocamento_camera_x = min(0, self.deslocamento_camera_x)
                    if largura_mapa_escalada > self.LARGURA: self.deslocamento_camera_x = max(self.LARGURA - largura_mapa_escalada, self.deslocamento_camera_x)
                    else: self.deslocamento_camera_x = (self.LARGURA - largura_mapa_escalada) / 2
                    self.deslocamento_camera_y = self.ALTURA / 1.8 - target_y * self.zoom_level
                    altura_mapa_escalada = self.altura_mapa_real * self.zoom_level
                    self.deslocamento_camera_y = min(0, self.deslocamento_camera_y)
                    if altura_mapa_escalada > self.ALTURA: self.deslocamento_camera_y = max(self.ALTURA - altura_mapa_escalada, self.deslocamento_camera_y)
                    else: self.deslocamento_camera_y = (self.ALTURA - altura_mapa_escalada) / 2

                
                    # --- Desenhar Jogo ---
                    # 1. Mapa com Zoom
                    self.desenhar_mapa_com_zoom()
                    

                    # 2. Todos os Sprites (Inimigos e Jogador)
                    sprites_para_desenhar = list(self.inimigos) + [self.jogador]
                    if self.npc_A: sprites_para_desenhar.append(self.npc_A)
                    if self.npc_F: sprites_para_desenhar.append(self.npc_F)
                    
                    for sprite in sprites_para_desenhar:
                         if sprite:
                             try:
                                  sprite_image = sprite.image
                                  scaled_w = int(sprite.rect.width * self.zoom_level)
                                  scaled_h = int(sprite.rect.height * self.zoom_level)
                                  if scaled_w > 0 and scaled_h > 0:
                                       img_scaled = pygame.transform.scale(sprite_image, (scaled_w, scaled_h))
                                       pos_x_tela = sprite.rect.x * self.zoom_level + self.deslocamento_camera_x
                                       pos_y_tela = sprite.rect.y * self.zoom_level + self.deslocamento_camera_y
                                       sprite_tela_rect = pygame.Rect(pos_x_tela, pos_y_tela, scaled_w, scaled_h)
                                       if self.tela.get_rect().colliderect(sprite_tela_rect):
                                            self.tela.blit(img_scaled, (pos_x_tela, pos_y_tela))
                                            # Debug rects...
                             except (AttributeError, ValueError, pygame.error) as draw_error:
                                  # print(f"Erro ao desenhar sprite {sprite}: {draw_error}")
                                  pass

            
# --- Desenhar UI ---
                    self.desenhar_coracoes()
                    self.desenhar_pocoes()
                    self.desenhar_popup()
                    if self.mostrar_msg_npc:
                        self.draw_text("Pressione F para conversar", 16, self.LARGURA // 2, self.ALTURA - 30, color=self.AMARELO, font_name=self.arcane_font_path, center=True)
                    if self.mostrar_prompt_porta:
                        self.draw_text("Pressione E para próxima fase", 16, self.LARGURA // 2, self.ALTURA - 30, color=self.AMARELO, font_name=self.arcane_font_path, center=True)
                    

            # Atualizar a tela inteira
            pygame.display.flip()

        # Fim do loop while executando
        self.quit_game()


    def quit_game(self):
        """Encerra o Pygame e sai do programa."""
        print("DEBUG: Chamando quit_game()")
        pygame.quit()
        print("DEBUG: Pygame finalizado.")
        sys.exit()

# --- Ponto de Entrada Principal ---
if __name__ == '__main__':
    print("DEBUG: Executando Bloco Principal (__name__ == '__main__')")
    if not pygame.get_init(): print("ERRO FATAL: Pygame não inicializado. Saindo."); sys.exit()
    if not pygame.font.get_init(): print("ERRO FATAL: Pygame Font não inicializado. Saindo."); pygame.quit(); sys.exit()

    game_instance = None
    try:
        print("DEBUG: Criando instância da classe Game...")
        game_instance = Game()
        print("DEBUG: Instância de Game criada. Chamando game_instance.run()...")
        game_instance.run()
    except Exception as e:
         print("\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
         print(f"ERRO NÃO TRATADO NO NÍVEL SUPERIOR: {e}")
         import traceback; traceback.print_exc()
         print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n")
    finally:
        if pygame.get_init(): print("DEBUG: Saindo pelo bloco finally, chamando pygame.quit()"); pygame.quit()
        print("DEBUG: Fim da execução.")

# --- END OF FILE main.py ---