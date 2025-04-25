# --- START OF FILE main.py ---
import cv2
import pygame
import sys
import os
import random # Importar random
import math   # Importar math
if pygame.display.get_init():
    tela_info = pygame.display.get_info()
    LARGURA, ALTURA = tela_info.current_w, tela_info.current_h
# Importar componentes do jogo
import player
import inimigo
# Ajuste os imports de inimigo conforme necessário
from inimigo import Inimigo1mp1, Inimigo1mp2, BossFinal, BossProjectile, FallingObject
from npc import NPC_Andy, NPC_Rafa, NPC_Gab
# <<< ADICIONADO >>> Importar classe do Boss se existir (necessário para SalaBoss)
# from inimigo import Boss # Descomente e ajuste quando tiver a classe Boss
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

        # Carregar fonte padrão
        try:
            font_path_teste = os.path.join("fonts", "AncientModernTales.ttf")
            # <<< CORREÇÃO: Usar caminho absoluto relativo ao script pode ser mais robusto >>>
            base_dir = os.path.dirname(os.path.abspath(__file__))
            font_dir_path = os.path.join(base_dir, "fonts", "AncientModernTales.ttf")
            if os.path.exists(font_dir_path):
                 self.default_font_name = font_dir_path
                 print(f"DEBUG: Usando fonte padrão: {self.default_font_name}")
            elif os.path.exists(font_path_teste):
                 self.default_font_name = font_path_teste
                 print(f"DEBUG: Usando fonte padrão (fallback): {self.default_font_name}")
            else:
                 print("DEBUG: Fonte TTF padrão não encontrada, usando SysFont.")
        except Exception as e:
             print(f"AVISO: Erro ao tentar definir fonte padrão: {e}. Usando SysFont.")


        # Carregar imagens da UI
        try:
            # <<< CORREÇÃO: Usar caminho absoluto relativo ao script >>>
            base_dir = os.path.dirname(os.path.abspath(__file__))
            base_path_ui = os.path.join(base_dir, "img", "ui")
            if not os.path.isdir(base_path_ui):
                 base_path_ui_fallback = os.path.join("img", "ui") # Fallback relativo simples
                 if os.path.isdir(base_path_ui_fallback): base_path_ui = base_path_ui_fallback
                 else: base_path_ui = "" # Não encontrou

            coracao_path = os.path.join(base_path_ui, "coracao_cheio.png")
            coracao_v_path = os.path.join(base_path_ui, "coracao_vazio.png")
            pocao_c_path = os.path.join(base_path_ui, "pocao_cheia.png")
            pocao_v_path = os.path.join(base_path_ui, "pocao_vazia.png")

            ui_icon_size = (35, 35)

            # Função auxiliar para carregar/escalar ícones com verificação
            def load_ui_icon(path, size):
                 if os.path.exists(path):
                     try:
                         img = pygame.image.load(path).convert_alpha()
                         return pygame.transform.scale(img, size)
                     except Exception as e: print(f"Erro carregando/escalando {path}: {e}"); return None
                 else: print(f"AVISO: UI Icon não encontrado: {path}"); return None

            self.coracao_cheio = load_ui_icon(coracao_path, ui_icon_size)
            self.coracao_vazio = load_ui_icon(coracao_v_path, ui_icon_size)
            self.pocao_cheia = load_ui_icon(pocao_c_path, ui_icon_size)
            self.pocao_vazia = load_ui_icon(pocao_v_path, ui_icon_size)

            print(f"DEBUG: Imagens da UI carregadas (buscadas em '{base_path_ui}').")
        except Exception as e: # Captura geral para erros de UI
            print(f"AVISO: Erro ao carregar imagens da UI: {e}")
            self.coracao_cheio = self.coracao_vazio = self.pocao_cheia = self.pocao_vazia = None

        # Instanciar Menus
        try:
            self.main_menu = MainMenu(self)
            self.credits_menu = CreditsMenu(self)
            print("DEBUG: Instâncias do Menu (MainMenu, CreditsMenu) criadas.")
        except Exception as e:
             print(f"ERRO CRÍTICO ao criar instâncias do Menu: {e}")
             self.quit_game()

            #Boss 
        self.boss_projectiles = pygame.sprite.Group()
        self.boss_falling_objects = pygame.sprite.Group()
        self.boss_instance = None # Referência ao boss atual
        # Variáveis de Jogo
        self.tmx_data = None
        self.largura_mapa = 0
        self.altura_mapa_real = 0
        self.zoom_level = 2.0 # Zoom padrão

        self.colisao_rects = []
        self.rampas_esquerda_rects = []
        self.rampas_direita_rects = []
        self.buraco_rects = []
        self.porta_rects = []
        self.lava_rects = []

        self.jogador = None
        self.inimigos = pygame.sprite.Group()
        self.todos_sprites = pygame.sprite.Group() # Para desenhar tudo

        # Variáveis de Conversa
        self.em_conversa = False
        # self.tempo_conversa = 0 # Não usado
        # self.duracao_conversa = 7000 # Usado em popup, não aqui
        self.npc_A = None
        self.npc_F = None
        self.npc = None # NPC em foco

        # Controle de Mapa
        self.mapa_atual_path = "Mapa.tmx" # Começa no Mapa 1
        # self.proximo_mapa_path = "Mapa(2).tmx" # Removido, lógica agora é contextual

        # Câmera e Popups
        self.deslocamento_camera_x = 0
        self.deslocamento_camera_y = 0
        self.mostrar_popup = False
        self.popup_mensagem = ""
        self.popup_timer = 0
        self.popup_duracao = 1500 # Duração do popup

        # Fonte Arcade
        base_dir = os.path.dirname(os.path.abspath(__file__))
        arcade_font_candidate = os.path.join(base_dir, "ARCADE_N.TTF")
        self.arcane_font_path = arcade_font_candidate if os.path.exists(arcade_font_candidate) else None
        if not self.arcane_font_path: print("AVISO: Fonte ARCADE_N.ttf não encontrada.")

        # Música e Prompts
        self.musica_atual = None
        self.mostrar_prompt_porta = False
        self.mostrar_msg_npc = False # Flag para prompt de conversa

        # Camadas de Perigo (referências)
        self.espinho_maior_layer = None
        self.espinho_menor_layer = None

        print("DEBUG: Game.__init__ concluído.")

    def tocar_musica_fundo(self, map_path):
        if map_path == "Mapa.tmx":
            pygame.mixer.music.load("musica/musica_medo.mp3")
        elif map_path == "Mapa(2).tmx":
            pygame.mixer.music.load("musica/musica_raiva.mp3")
        elif map_path == "SalaBoss.tmx":
            pygame.mixer.music.load("musica/musica_culpa.mp3")
        else:
            print(f"[MÚSICA] Nenhuma música definida para o mapa: {map_path}")
            return

        pygame.mixer.music.set_volume(0.5)  # você pode ajustar o volume aqui
        pygame.mixer.music.play(-1)  # -1 faz a música tocar em loop

    # --- Funções Auxiliares ---

    def get_font(self, font_name_or_path, size):
        """Obtém uma fonte do cache ou a carrega, com fallback para SysFont."""
        if not pygame.font.get_init(): pygame.font.init()
        key = (font_name_or_path, size)
        if key not in self.fonts:
            try:
                effective_font_path = font_name_or_path if font_name_or_path else self.default_font_name
                if effective_font_path and os.path.exists(effective_font_path):
                    self.fonts[key] = pygame.font.Font(effective_font_path, size)
                else:
                    if effective_font_path: print(f"AVISO: Fonte '{effective_font_path}' não encontrada. Usando SysFont.")
                    self.fonts[key] = pygame.font.SysFont(None, size)
            except Exception as e:
                 print(f"AVISO: Erro ao carregar fonte '{effective_font_path}' ({size}): {e}. Usando SysFont.")
                 self.fonts[key] = pygame.font.SysFont(None, size)
        return self.fonts[key]


    def draw_text(self, text, size, x, y, color, font_name=None, center=False):
        """Desenha texto na tela."""
        try:
            # Prioriza fonte passada, depois arcane, depois default, depois sysfont
            font_to_use = font_name if font_name else self.arcane_font_path
            font = self.get_font(font_to_use, size) # Usa cache/fallback
            text_surface = font.render(text, True, color)
            text_rect = text_surface.get_rect()
            if center: text_rect.center = (int(x), int(y))
            else: text_rect.topleft = (int(x), int(y))
            self.tela.blit(text_surface, text_rect)
        except Exception as e:
            print(f"ERRO ao desenhar texto '{text}': {e}")
            # Fallback visual
            try:
                fb_font = pygame.font.SysFont(None, 20)
                fb_surf = fb_font.render("ERR", True, self.VERMELHO)
                fb_rect = fb_surf.get_rect(center=(int(x), int(y)))
                self.tela.blit(fb_surf, fb_rect)
            except: pass


    def desenhar_coracoes(self):
        """Desenha a UI de vida."""
        if not self.jogador or self.coracao_cheio is None or self.coracao_vazio is None: return
        x, y, spacing = 15, 15, 40
        for i in range(self.jogador.vida_maxima):
            img = self.coracao_cheio if i < self.jogador.vida_atual else self.coracao_vazio
            if img: self.tela.blit(img, (x + i * spacing, y))

    def desenhar_pocoes(self):
        """Desenha a UI de poções."""
        if not self.jogador or self.pocao_cheia is None or self.pocao_vazia is None: return
        icon_w = self.pocao_cheia.get_width()
        spacing = 10
        count = self.jogador.curas_maximas
        total_w = (count * icon_w) + ((count - 1) * spacing)
        x, y = self.LARGURA - 15 - total_w, 15
        for i in range(count):
            img = self.pocao_cheia if i < self.jogador.curas_restantes else self.pocao_vazia
            if img: self.tela.blit(img, (x + i * (icon_w + spacing), y))

    def exibir_mensagem_final(self, mensagem, cor):
        """Mostra mensagem final e volta ao menu."""
        overlay = pygame.Surface((self.LARGURA, self.ALTURA), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.tela.blit(overlay, (0, 0))
        # <<< CORREÇÃO: Usar draw_text com fonte arcade e centralizado >>>
        self.draw_text(mensagem, 60, self.LARGURA // 2, self.ALTURA // 2, cor, self.arcane_font_path, center=True)
        pygame.display.flip()
        pygame.time.wait(3000)
        self.game_state = "MENU"

    # A função exibir_mensagem_npc não é mais necessária, pois draw_text faz o trabalho.

    def exibir_popup(self, mensagem):
        """Ativa popup de mensagem curta."""
        self.popup_mensagem = mensagem
        self.mostrar_popup = True
        self.popup_timer = pygame.time.get_ticks() + self.popup_duracao

    def desenhar_popup(self):
        """Desenha o popup se ativo."""
        if self.mostrar_popup and pygame.time.get_ticks() < self.popup_timer:
             try:
                 fonte = self.get_font(self.default_font_name, 28) # Usa fonte default
                 texto_surface = fonte.render(self.popup_mensagem, True, self.BRANCO)
                 texto_rect = texto_surface.get_rect(center=(self.LARGURA // 2, self.ALTURA - 60))
                 bg_rect = texto_rect.inflate(20, 10)
                 bg_surface = pygame.Surface(bg_rect.size, pygame.SRCALPHA)
                 bg_surface.fill((50, 50, 50, 200)) # Fundo cinza escuro
                 pygame.draw.rect(bg_surface, self.BRANCO, bg_surface.get_rect(), 1, border_radius=5) # Borda
                 self.tela.blit(bg_surface, bg_rect.topleft)
                 self.tela.blit(texto_surface, texto_rect)
             except Exception as e:
                 print(f"Erro ao exibir popup: {e}"); self.mostrar_popup = False
        elif self.mostrar_popup and pygame.time.get_ticks() >= self.popup_timer:
             self.mostrar_popup = False


    def desenhar_mapa_com_zoom(self):
        """Desenha as camadas visíveis do mapa com zoom e otimização."""
        if not self.tmx_data: return

        camadas_mapa_atual = []
        # <<< MODIFICADO: Adicionar definição para SalaBoss.tmx >>>
        if self.mapa_atual_path == "Mapa.tmx":
            camadas_mapa_atual = [
                "Background", "Fundo", "Chão", "RampaParaEsquerda",
                "RampaParaDireita", "Espinho_Maior", "Espinho_Menor", "FiguraPorta"
            ]
        elif self.mapa_atual_path == "Mapa(2).tmx":
            camadas_mapa_atual = [
                "Background", "Fundo", "Lava", "Detalhes", "Representacao_Porta"
            ]
        elif self.mapa_atual_path == "SalaBoss.tmx": # <<< ADICIONADO >>>
            camadas_mapa_atual = ["Background"] # Apenas a camada de imagem de fundo
        else:
            print(f"AVISO: Nenhuma camada de desenho definida para o mapa: {self.mapa_atual_path}")

        # Área visível na tela (em coordenadas do mundo) para culling
        try:
             inv_zoom = 1.0 / self.zoom_level if self.zoom_level != 0 else 1.0
             culling_margin = 64 # Margem extra
             tela_rect_mundo = pygame.Rect(
                 (-self.deslocamento_camera_x * inv_zoom) - culling_margin,
                 (-self.deslocamento_camera_y * inv_zoom) - culling_margin,
                 (self.LARGURA * inv_zoom) + 2 * culling_margin,
                 (self.ALTURA * inv_zoom) + 2 * culling_margin
             )
        except ZeroDivisionError: # Segurança caso zoom seja 0
             tela_rect_mundo = self.tela.get_rect() # Sem culling se zoom for 0


        for nome_camada in camadas_mapa_atual:
            try: layer = self.tmx_data.get_layer_by_name(nome_camada)
            except ValueError: continue # Pula camada não encontrada

            # Camadas de Tiles
            if hasattr(layer, 'tiles'):
                tile_w, tile_h = self.tmx_data.tilewidth, self.tmx_data.tileheight
                tile_w_z, tile_h_z = int(tile_w * self.zoom_level), int(tile_h * self.zoom_level)
                if tile_w_z <= 0 or tile_h_z <= 0: continue

                for x, y, gid in layer:
                    if gid == 0: continue
                    tile_rect_mundo = pygame.Rect(x * tile_w, y * tile_h, tile_w, tile_h)
                    if not tela_rect_mundo.colliderect(tile_rect_mundo): continue # Culling

                    tile_img = self.tmx_data.get_tile_image_by_gid(gid)
                    if tile_img:
                        try:
                            tile_scaled = pygame.transform.scale(tile_img, (tile_w_z, tile_h_z))
                            pos_x = tile_rect_mundo.x * self.zoom_level + self.deslocamento_camera_x
                            pos_y = tile_rect_mundo.y * self.zoom_level + self.deslocamento_camera_y
                            self.tela.blit(tile_scaled, (pos_x, pos_y))
                        except: pass # Ignora erros de escala/blit de tile individual

            # Camadas de Imagem
            elif hasattr(layer, 'image'):
                 try:
                     img_orig = layer.image
                     if not img_orig: continue
                     w_orig, h_orig = img_orig.get_size()
                     w_z, h_z = int(w_orig * self.zoom_level), int(h_orig * self.zoom_level)
                     if w_z <= 0 or h_z <= 0: continue

                     off_x = getattr(layer, 'offsetx', 0); off_y = getattr(layer, 'offsety', 0)
                     img_rect_mundo = pygame.Rect(off_x, off_y, w_orig, h_orig)
                     if not tela_rect_mundo.colliderect(img_rect_mundo): continue # Culling

                     img_scaled = pygame.transform.scale(img_orig, (w_z, h_z))
                     pos_x = off_x * self.zoom_level + self.deslocamento_camera_x
                     pos_y = off_y * self.zoom_level + self.deslocamento_camera_y
                     self.tela.blit(img_scaled, (pos_x, pos_y))
                 except Exception as e: print(f"Erro desenhando ImageLayer '{nome_camada}': {e}")


    def start_game(self, map_path):
        """Configura e carrega os recursos para um mapa específico."""
        print(f"\nDEBUG: >>> Iniciando carregamento do mapa: {map_path} <<<")

        # --- 1. Resetar Estado Anterior ---
        print("DEBUG: Resetando estado anterior...")
        self.inimigos.empty(); self.todos_sprites.empty()
        self.boss_projectiles.empty(); self.boss_falling_objects.empty()
        self.boss_instance = None
        self.jogador = None; self.npc_A = None; self.npc_F = None; self.npc_G = None ;self.npc = None
        self.colisao_rects = []; self.rampas_esquerda_rects = []; self.rampas_direita_rects = []
        self.buraco_rects = []; self.porta_rects = []; self.lava_rects = []
        self.tmx_data = None; self.largura_mapa = 0; self.altura_mapa_real = 0
        self.espinho_maior_layer = None; self.espinho_menor_layer = None
        self.em_conversa = False; self.mostrar_prompt_porta = False; self.mostrar_msg_npc = False
        pygame.mixer.music.stop(); self.musica_atual = None

        # --- 2. Carregar Dados do Novo Mapa ---
        self.tmx_data = carregar_mapa(map_path)
        if not self.tmx_data:
            print(f"ERRO FATAL: Não foi possível carregar o mapa '{map_path}'. Voltando ao menu.")
            self.exibir_mensagem_final(f"Erro: Mapa não encontrado\n{os.path.basename(map_path)}", self.VERMELHO)
            self.game_state = "MENU"
            return

        self.mapa_atual_path = map_path # Atualiza o path atual
        self.largura_mapa = self.tmx_data.width * self.tmx_data.tilewidth
        self.altura_mapa_real = self.tmx_data.height * self.tmx_data.tileheight
        print(f"DEBUG: Mapa '{map_path}' carregado ({self.largura_mapa}x{self.altura_mapa_real}px).")

        # --- 3. Definir Nomes de Camadas e Posição Inicial por Mapa ---
        print(f"DEBUG: Configurando camadas para '{map_path}'...")
        chao_layers = []; rampa_e_layer = None; rampa_d_layer = None
        buraco_layer = None; porta_layer = None; espinho_m_layer = None
        espinho_p_layer = None; lava_layer = None
        jogador_start_x, jogador_start_y = 100, 100 # Padrão

        if map_path == "Mapa.tmx":
            chao_layers = ["Chão"]; rampa_e_layer = "RampaParaEsquerda"; rampa_d_layer = "RampaParaDireita"
            buraco_layer = "Buraco"; porta_layer = "Porta"
            espinho_m_layer = "Espinho_Maior"; espinho_p_layer = "Espinho_Menor"
            jogador_start_x, jogador_start_y = 100, 400
            print("DEBUG: Camadas para Mapa.tmx definidas.")
        elif map_path == "Mapa(2).tmx":
            try:
                caminho_musica = os.path.join("musica", "musica_raiva.mp3")
                pygame.mixer.music.load(caminho_musica)
                pygame.mixer.music.play(-1)  # -1 faz tocar em loop
                print("DEBUG: Música do Mapa 2 iniciada.")
            except Exception as e:
                print(f"[ERRO] Ao carregar música do mapa 2: {e}")            
            # VERIFIQUE ESTES NOMES E TIPOS NO SEU ARQUIVO Mapa(2).tmx!
            chao_layers = ["Fundo"] # Camada sólida
            buraco_layer = "Buraco" # Camada de objetos
            porta_layer = "Porta"   # Camada de objetos
            lava_layer = "Lava"     # Camada de tiles (perigo)
            jogador_start_x, jogador_start_y = 70, 1250
            print("DEBUG: Camadas para Mapa(2).tmx definidas.")
        # <<< ADICIONADO: Configuração para SalaBoss.tmx >>>
        elif map_path == "SalaBoss.tmx":
            chao_layers = [] # Sem chão de tiles, usará limites
            porta_layer = "Porta" # Para interação de saída (se existir no TMX)
            # Posição inicial (ajuste se necessário)
            jogador_start_x = self.largura_mapa // 2
            jogador_start_y = self.altura_mapa_real - 100

            self.boss_start_x = self.largura_mapa - 200
            self.boss_start_y = self.altura_mapa_real - 7   
            print("DEBUG: Camadas para SalaBoss.tmx definidas.")
        else:
            print(f"AVISO: Configuração de fallback para mapa desconhecido: {map_path}")
            chao_layers = ["Chão"]; porta_layer = "Porta"; buraco_layer = "Buraco"

        # --- 4. Carregar Retângulos de Colisão/Interação ---
        print("DEBUG: Carregando retângulos das camadas...")
        self.colisao_rects = []; self.rampas_esquerda_rects = []; self.rampas_direita_rects = []
        self.buraco_rects = []; self.porta_rects = []; self.lava_rects = []
        # Colisões Sólidas
        for name in chao_layers: rects = criar_mapa_rects(self.tmx_data, name); self.colisao_rects.extend(rects); print(f"  - Colisão '{name}': {len(rects)} rects")
        # Rampas
        if rampa_e_layer: self.rampas_esquerda_rects = criar_mapa_rects(self.tmx_data, rampa_e_layer); print(f"  - Rampa Esq '{rampa_e_layer}': {len(self.rampas_esquerda_rects)} rects")
        if rampa_d_layer: self.rampas_direita_rects = criar_mapa_rects(self.tmx_data, rampa_d_layer); print(f"  - Rampa Dir '{rampa_d_layer}': {len(self.rampas_direita_rects)} rects")
        # Objetos
        if buraco_layer: self.buraco_rects = criar_objetos_retangulos(self.tmx_data, buraco_layer); print(f"  - Buraco Obj '{buraco_layer}': {len(self.buraco_rects)} rects")
        if porta_layer: self.porta_rects = criar_objetos_retangulos(self.tmx_data, porta_layer); print(f"  - Porta Obj '{porta_layer}': {len(self.porta_rects)} rects")
        # Perigos (Tiles)
        if lava_layer: self.lava_rects = criar_mapa_rects(self.tmx_data, lava_layer); print(f"  - Lava Tile '{lava_layer}': {len(self.lava_rects)} rects")
        # Camadas de Espinhos (Referências)
        try:
            if espinho_m_layer: self.espinho_maior_layer = self.tmx_data.get_layer_by_name(espinho_m_layer)
            if espinho_p_layer: self.espinho_menor_layer = self.tmx_data.get_layer_by_name(espinho_p_layer)
        except ValueError as e: print(f"AVISO: Camada de espinho não encontrada: {e}")

        # Adicionar Limites do Mapa (SEMPRE)
        esp = 5
        limites = [ pygame.Rect(-esp, -esp, esp, self.altura_mapa_real + 2*esp), pygame.Rect(self.largura_mapa, -esp, esp, self.altura_mapa_real + 2*esp), pygame.Rect(-esp, -esp, self.largura_mapa + 2*esp, esp), pygame.Rect(-esp, self.altura_mapa_real, self.largura_mapa + 2*esp, esp) ]
        self.colisao_rects.extend(limites)
        print(f"DEBUG: Limites adicionados. Total colisões sólidas: {len(self.colisao_rects)}.")

        # --- 5. Criar Jogador ---
        print(f"DEBUG: Criando jogador em ({jogador_start_x},{jogador_start_y})...")
        try:
            self.jogador = player.Jogador( x=jogador_start_x, y=jogador_start_y, colisao_rects=self.colisao_rects, rampas_esquerda_rects=self.rampas_esquerda_rects, rampas_direita_rects=self.rampas_direita_rects, buraco_rects=self.buraco_rects, lava_rects=self.lava_rects, tmx_data=self.tmx_data, zoom_level=self.zoom_level )
            self.todos_sprites.add(self.jogador)
            print("DEBUG: Jogador criado.")
        except Exception as e:
            print(f"ERRO CRÍTICO ao criar Jogador: {e}"); import traceback; traceback.print_exc()
            self.exibir_mensagem_final("Erro ao criar jogador", self.VERMELHO)
            self.game_state = "MENU"; return

        # --- 6. Criar NPCs e Inimigos ---
        print(f"DEBUG: Criando entidades para '{map_path}'...")
        lista_inimigos_mapa = []
        if map_path == "Mapa.tmx":
            try: # NPCs
                self.npc_A = NPC_Andy(x=208, y=398, zoom_level=self.zoom_level)
                self.npc_F = NPC_Rafa(x=5667, y=398, zoom_level=self.zoom_level)
                self.todos_sprites.add(self.npc_A, self.npc_F)
                print("DEBUG: NPCs (Andy, Rafa) criados.")
            except NameError: print("ERRO: Classes NPC não encontradas.")
            except Exception as e: print(f"Erro criando NPCs (Mapa.tmx): {e}")
            try: # Inimigos
                inimigo1 = Inimigo1mp1(x=590, y=220, jogador=self.jogador, colisao_rects=self.colisao_rects, tmx_data=self.tmx_data, largura_mapa=self.largura_mapa, altura_mapa=self.altura_mapa_real)
                inimigo2 = Inimigo1mp2(x=2050, y=214, jogador=self.jogador, colisao_rects=self.colisao_rects, tmx_data=self.tmx_data, largura_mapa=self.largura_mapa, altura_mapa=self.altura_mapa_real)
                inimigo3 = Inimigo1mp1(x=1500, y=0, jogador=self.jogador, colisao_rects=self.colisao_rects, tmx_data=self.tmx_data, largura_mapa=self.largura_mapa, altura_mapa=self.altura_mapa_real)            
                inimigo4 = Inimigo1mp1(x=3050, y=0, jogador=self.jogador, colisao_rects=self.colisao_rects, tmx_data=self.tmx_data, largura_mapa=self.largura_mapa, altura_mapa=self.altura_mapa_real)
                inimigo5 = Inimigo1mp1(x=3700, y=214, jogador=self.jogador, colisao_rects=self.colisao_rects, tmx_data=self.tmx_data, largura_mapa=self.largura_mapa, altura_mapa=self.altura_mapa_real)            
                inimigo6 = Inimigo1mp2(x=4250, y=214, jogador=self.jogador, colisao_rects=self.colisao_rects, tmx_data=self.tmx_data, largura_mapa=self.largura_mapa, altura_mapa=self.altura_mapa_real)
                inimigo7 = Inimigo1mp2(x=5500, y=0, jogador=self.jogador, colisao_rects=self.colisao_rects, tmx_data=self.tmx_data, largura_mapa=self.largura_mapa, altura_mapa=self.altura_mapa_real)
                lista_inimigos_mapa.extend([inimigo1, inimigo2, inimigo3, inimigo4, inimigo5, inimigo6, inimigo7])
                print("DEBUG: Inimigos (mp1, mp2) criados.")
            except NameError: print("ERRO: Classes Inimigo não encontradas.")
            except Exception as e: print(f"Erro criando Inimigos (Mapa.tmx): {e}")

        elif map_path == "Mapa(2).tmx":
            try:
                self.npc_G = NPC_Gab(x=463, y=970, zoom_level=self.zoom_level)
                self.todos_sprites.add(self.npc_G)
                inimigo8 = inimigo.Inimigo2mp2(x=690, y=1150, jogador=self.jogador, colisao_rects=self.colisao_rects, tmx_data=self.tmx_data, largura_mapa=self.largura_mapa, altura_mapa=self.altura_mapa_real)
                inimigo9 = inimigo.Inimigo3mp2(x=1730, y=1100, jogador=self.jogador, colisao_rects=self.colisao_rects, tmx_data=self.tmx_data, largura_mapa=self.largura_mapa, altura_mapa=self.altura_mapa_real)
                inimigo10 = inimigo.Inimigo2mp2_1(x=2165, y=1118, jogador=self.jogador, colisao_rects=self.colisao_rects, tmx_data=self.tmx_data, largura_mapa=self.largura_mapa, altura_mapa=self.altura_mapa_real)
                inimigo11 = inimigo.Inimigo2mp2_1(x=2795, y=1000, jogador=self.jogador, colisao_rects=self.colisao_rects, tmx_data=self.tmx_data, largura_mapa=self.largura_mapa, altura_mapa=self.altura_mapa_real)        
                inimigo12 = inimigo.Inimigo3mp2(x=3130, y=1100, jogador=self.jogador, colisao_rects=self.colisao_rects, tmx_data=self.tmx_data, largura_mapa=self.largura_mapa, altura_mapa=self.altura_mapa_real)        
                inimigo13 = inimigo.Inimigo2mp2_1(x=3390, y=1100, jogador=self.jogador, colisao_rects=self.colisao_rects, tmx_data=self.tmx_data, largura_mapa=self.largura_mapa, altura_mapa=self.altura_mapa_real)  

                inimigo14 = inimigo.Inimigo2mp2(x=945, y=336, jogador=self.jogador, colisao_rects=self.colisao_rects, tmx_data=self.tmx_data, largura_mapa=self.largura_mapa, altura_mapa=self.altura_mapa_real)  
                inimigo15 = inimigo.Inimigo2mp2(x=1360, y=336, jogador=self.jogador, colisao_rects=self.colisao_rects, tmx_data=self.tmx_data, largura_mapa=self.largura_mapa, altura_mapa=self.altura_mapa_real)  
                inimigo16 = inimigo.Inimigo3mp2(x=2090, y=526, jogador=self.jogador, colisao_rects=self.colisao_rects, tmx_data=self.tmx_data, largura_mapa=self.largura_mapa, altura_mapa=self.altura_mapa_real)  
                inimigo17 = inimigo.Inimigo2mp2_1(x=2820, y=382, jogador=self.jogador, colisao_rects=self.colisao_rects, tmx_data=self.tmx_data, largura_mapa=self.largura_mapa, altura_mapa=self.altura_mapa_real)  
    
                lista_inimigos_mapa.extend([inimigo8, inimigo9, inimigo10, inimigo11, inimigo12, inimigo13, inimigo14, inimigo15, inimigo16, inimigo17])
                print(f"[DEBUG] Inimigo2mp2 criado no mapa: {id(inimigo3)}")
            except Exception as e: print(f"ERRO ao criar inimigos para Mapa.tmx: {e}")

        # <<< ADICIONADO: Criação de entidades para SalaBoss.tmx >>>
        elif map_path == "SalaBoss.tmx":
             print(f"DEBUG: Criando Boss em ({self.boss_start_x},{self.boss_start_y})...")
             try:
                 # Passa os colisao_rects gerais (chão/paredes)
                 self.boss_instance = BossFinal(x=self.boss_start_x, y=self.boss_start_y,
                                                jogador=self.jogador,
                                                colisao_rects=self.colisao_rects,
                                                largura_mapa=self.largura_mapa,
                                                altura_mapa=self.altura_mapa_real)
                 lista_inimigos_mapa.append(self.boss_instance) # Adiciona à lista para grupos
                 print("DEBUG: BossFinal criado.")
             except NameError: print("ERRO CRÍTICO: Classe BossFinal não encontrada/importada.")
             except Exception as e: print(f"Erro criando BossFinal: {e}")
             

        # Adicionar inimigos aos grupos
        if lista_inimigos_mapa:
             self.inimigos.add(*lista_inimigos_mapa)
             self.todos_sprites.add(*lista_inimigos_mapa)
             print(f"DEBUG: {len(lista_inimigos_mapa)} inimigos/boss adicionados.")

        # --- 7. Finalizar Configuração ---
        self.deslocamento_camera_x = 0; self.deslocamento_camera_y = 0
        self.game_state = "PLAYING"
        print(f"DEBUG: >>> Carregamento de '{map_path}' CONCLUÍDO. Estado: PLAYING <<<")

        self.tocar_musica_fundo(map_path)

    def exibir_conversa(self):
        """Desenha a UI de conversa."""
        overlay = pygame.Surface((self.LARGURA, self.ALTURA), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 170)) # Fundo escuro
        self.tela.blit(overlay, (0, 0))
        if self.npc and hasattr(self.npc, 'conversar'):
            try: self.npc.conversar(self.tela, self.LARGURA, self.ALTURA)
            except Exception as e: print(f"Erro em NPC.conversar: {e}"); self.em_conversa = False
        else: self.em_conversa = False # Sai se não houver NPC válido

#    ====================================== Cutscenes 
    def play_cutscene(self, video_path, tela, audio_path=None):
        clock = pygame.time.Clock()

        # Inicializa o mixer do Pygame, caso não tenha sido inicializado
        if not pygame.mixer.get_init():
            pygame.mixer.init()

        # Carrega o áudio, caso fornecido
        if audio_path and os.path.exists(audio_path):
            try:
                pygame.mixer.music.load(audio_path)
                pygame.mixer.music.set_volume(0.7)
                pygame.mixer.music.play()
            except Exception as e:
                print(f"Erro ao carregar áudio: {e}")
        else:
            print("Aviso: Áudio da cutscene não encontrado.")

        # Abre o vídeo com OpenCV
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            print(f"Erro ao abrir o vídeo: {video_path}")
            return

        # Obtém as dimensões do vídeo e configura a tela do Pygame
        video_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        video_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        video_fps = cap.get(cv2.CAP_PROP_FPS) or 30

        tela = pygame.display.set_mode((video_width, video_height))
        pygame.display.set_caption("Cutscene")

        # Loop para exibir o vídeo frame a frame
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            # 🔄 Rotaciona o vídeo 270 graus no sentido horário
            frame = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)

            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    cap.release()
                    pygame.quit()
                    exit()
                elif evento.type == pygame.KEYDOWN:
                    if evento.key == pygame.K_ESCAPE or evento.key == pygame.K_RETURN:
                        cap.release()
                        pygame.mixer.music.stop()
                        return  # Sai da função, pulando a cutscene

            # Converte o frame para o formato RGB
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Converte o frame para uma superfície Pygame
            frame_surface = pygame.surfarray.make_surface(frame)
            frame_surface = pygame.transform.scale(frame_surface, (video_width, video_height))

            # Exibe o frame na tela do Pygame
            tela.blit(frame_surface, (0, 0))
            pygame.display.flip()

            clock.tick(video_fps)

        cap.release()
        pygame.mixer.music.stop()



    def tocar_cutscene(self, caminho_cutscene="cutscenes/Cutscene 01.mp4", caminho_audio="cutscenes/Cutscene-01.mp3"):
            import cv2
            # Carrega e toca o áudio com pygame.mixer
            pygame.mixer.music.load(caminho_audio)
            pygame.mixer.music.play()

            cap = cv2.VideoCapture(caminho_cutscene)
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break

                frame = cv2.resize(frame, (self.LARGURA, self.ALTURA))
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                surface = pygame.surfarray.make_surface(frame_rgb.swapaxes(0, 1))
                self.tela.blit(surface, (0, 0))
                pygame.display.update()

                for evento in pygame.event.get():
                    if evento.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    elif evento.type == pygame.KEYDOWN and evento.key == pygame.K_RETURN:
                        pygame.mixer.music.stop()  # Para o som se pular
                        cap.release()
                        return

                pygame.time.delay(30)  # Ajuste para o fps do vídeo (~30fps)

            cap.release()
            pygame.mixer.music.stop()  # Garante que o som pare ao fim da cutscene
    # ==================== LOOP PRINCIPAL ====================
    def run(self):
        """Loop principal do jogo."""
        print("DEBUG: Iniciando loop principal (Game.run)")
        executando = True
        while executando:
            # --- Tempo e Eventos ---
            delta_time = self.relogio.tick(self.FPS) / 1000.0 # Delta time (não usado diretamente)
            tempo_agora = pygame.time.get_ticks()
            eventos_frame = pygame.event.get()

            # --- Gerenciamento de Estados ---
            if self.game_state == "MENU":
                next_state = self.main_menu.handle_input(eventos_frame)
                if next_state == "PLAYING": self.start_game(self.mapa_atual_path); continue # Reinicia com mapa atual
                elif next_state == "CREDITS": self.game_state = "CREDITS"
                elif next_state == "QUIT": executando = False
            elif self.game_state == "CREDITS":
                if self.credits_menu.handle_input(eventos_frame) == "MENU": self.game_state = "MENU"

            # --- Lógica do Jogo Ativo ---
            elif self.game_state == "PLAYING":
                if not self.jogador or not self.tmx_data: # Segurança
                     print("ERRO GRAVE: Tentando rodar PLAYING sem jogador ou tmx_data."); self.game_state = "MENU"; continue

                # --- Música ---
                musica_necessaria = None # Lógica para trocar música (igual ao anterior)
                if self.mapa_atual_path == "Mapa.tmx" and self.musica_atual != "fase1":
                     musica_necessaria = "musica/musica_medo.mp3"; self.musica_atual = "fase1"
                # Adicionar elif para Mapa(2) e SalaBoss se tiverem músicas
                elif self.mapa_atual_path == "Mapa(2).tmx" and self.musica_atual != "fase2":
                      # musica_necessaria = "musica/fase2.ogg"; self.musica_atual = "fase2"
                      pass
                elif self.mapa_atual_path == "SalaBoss.tmx" and self.musica_atual != "boss":
                      # musica_necessaria = "musica/boss.ogg"; self.musica_atual = "boss"
                      pass
                if musica_necessaria:
                     try: pygame.mixer.music.load(musica_necessaria); pygame.mixer.music.play(-1)
                     except pygame.error as e: print(f"Erro música {musica_necessaria}: {e}"); self.musica_atual = None

                # --- Processar Interações (Porta, NPC) ---
                self.mostrar_prompt_porta = False; colidindo_com_porta = False
                self.mostrar_msg_npc = False; npc_proximo = None
                if self.jogador:
                    # Porta
                    if self.porta_rects:
                        for porta in self.porta_rects:
                            if self.jogador.collision_rect.colliderect(porta):
                                self.mostrar_prompt_porta = True; colidindo_com_porta = True; break
                    # NPC (Apenas Mapa 1)
                    if self.mapa_atual_path == "Mapa.tmx":
                        npcs_aqui = [n for n in [self.npc_A, self.npc_F] if n]
                        if npcs_aqui:
                            for npc_atual in npcs_aqui:
                                if pygame.math.Vector2(self.jogador.rect.center).distance_to(npc_atual.rect.center) < 100:
                                    self.mostrar_msg_npc = True; npc_proximo = npc_atual; break
                            self.npc = npc_proximo # Atualiza NPC em foco
                    if self.mapa_atual_path == "Mapa(2).tmx":
                        npcs_aqui = [n for n in [self.npc_G] if n]
                        if npcs_aqui:
                            for npc_atual in npcs_aqui:
                                if pygame.math.Vector2(self.jogador.rect.center).distance_to(npc_atual.rect.center) < 50:
                                    self.mostrar_msg_npc = True; npc_proximo = npc_atual; break
                            self.npc = npc_proximo # Atualiza NPC em foco

                # --- Processar Eventos ---
                for evento in eventos_frame:
                    if evento.type == pygame.QUIT: executando = False
                    if evento.type == pygame.KEYDOWN:
                        if evento.key == pygame.K_ESCAPE: # Voltar ao Menu
                            self.game_state = "MENU"; pygame.mixer.music.stop(); self.musica_atual = None; break

                        # Input em Conversa
                        if self.em_conversa:
                            if self.npc:
                                if evento.key in [pygame.K_RIGHT, pygame.K_f, pygame.K_SPACE, pygame.K_RETURN]:
                                    if hasattr(self.npc, 'avancar_conversa'):
                                         try:
                                             if not self.npc.avancar_conversa(): self.em_conversa = False; self.npc = None
                                         except Exception as e: print(f"Erro avancar_conversa: {e}"); self.em_conversa = False
                                elif evento.key == pygame.K_LEFT:
                                     if hasattr(self.npc, 'voltar_conversa'):
                                         try: self.npc.voltar_conversa()
                                         except Exception as e: print(f"Erro voltar_conversa: {e}")
                            else: self.em_conversa = False # Segurança
                            continue # Pular input normal se estava em conversa

                        # Input Normal
                        elif evento.key == pygame.K_e: # Interagir / Curar
                             if colidindo_com_porta: # Mudar de Mapa
                                 mapa_a_carregar = None
                                 # <<< MODIFICADO: Lógica de transição >>>
                                 if self.mapa_atual_path == "Mapa.tmx":
                                     mapa_a_carregar = "Mapa(2).tmx"
                                     pygame.mixer.music.stop()  # Para música do mapa
                                     self.tocar_cutscene("cutscenes/Cutscene 01.mp4", "cutscenes/Cutscene-01.mp3")
                                 elif self.mapa_atual_path == "Mapa(2).tmx":
                                    pygame.mixer.music.stop()  # Para música do mapa
                                    self.tocar_cutscene("cutscenes/Cutscene 01.mp4", "cutscenes/Cutscene-01.mp3")
                                    mapa_a_carregar = "SalaBoss.tmx"
                                 elif self.mapa_atual_path == "SalaBoss.tmx":
                                     if self.boss_instance: self.boss_instance.update_animation()
                                     # Só sai da sala do boss se ele foi derrotado?
                                     if not self.boss_instance or self.boss_instance.is_dead:
                                         print("DEBUG: Saindo da Sala Boss -> Créditos/Menu")
                                        # AQUI VOCÊ DECIDE: ir para créditos, menu ou cutscene final
                                         self.exibir_mensagem_final("VOCÊ VENCEU!", self.AMARELO) # Mostra vitória antes
                                         self.game_state = "MENU" # Exemplo: volta ao menu
                                         pygame.mixer.music.stop()
                                         break
                                     else:
                                         self.exibir_popup("Derrote o chefe primeiro!")
                                # --- Fim da Modificação ---

                                     if self.game_state != "PLAYING": break # Se mudou de estado (MENU)
                                 
                                 if mapa_a_carregar:
                                     print(f"DEBUG: Carregando mapa: {mapa_a_carregar}")
                                     self.start_game(mapa_a_carregar)
                                     break # Sai do loop de eventos para processar novo estado/mapa
                                 elif self.game_state == "MENU": break # Se ação foi ir pro menu                                   

                             elif self.jogador: # Curar
                                curou = self.jogador.recuperar_vida()
                                self.exibir_popup("Vida recuperada!" if curou else "Não foi possível curar!")

                        elif evento.key == pygame.K_f: # Tecla F: Prioriza Conversa, depois Ataque
                             # Prioridade 1: Conversar se o prompt estiver visível e houver um NPC
                             if self.mostrar_msg_npc and self.npc:
                                 self.em_conversa = True
                                 if hasattr(self.npc, 'iniciar_conversa'):
                                      try: self.npc.iniciar_conversa()
                                      except Exception as e: print(f"Erro iniciar_conversa: {e}")
                                 # A flag em_conversa bloqueia outras ações no início do loop

                             # Prioridade 2: Atacar com F (se não iniciou conversa)
                             elif self.jogador:
                                 print("DEBUG: Tecla F pressionada para Ataque") # Log
                                 self.jogador.atacar(list(self.inimigos))

                        # Ações do JogadorW
                        elif evento.key == pygame.K_LSHIFT or evento.key == pygame.K_RSHIFT:
                             if self.jogador: self.jogador.iniciar_dash()
                        elif evento.key == pygame.K_z: # Ataque (Z ou X)
                             if self.jogador: self.jogador.atacar(list(self.inimigos))

                # --- Atualizações (se jogando e não em conversa) ---
                if self.game_state == "PLAYING" and not self.em_conversa:
                    # Atualizar todas as entidades
                    if self.jogador: 
                        self.jogador.atualizar(self.inimigos)
                        self.jogador.update_animation()
                    # Atualizar NPCs do Mapa 1
                    if self.mapa_atual_path == "Mapa.tmx":
                        if self.npc_A: self.npc_A.atualizar()
                        if self.npc_F: self.npc_F.atualizar()
                    if self.mapa_atual_path == "Mapa(2).tmx":
                        if self.npc_G: self.npc_G.atualizar()
                        self.jogador.velocidade_dash = 13
                        self.jogador.velocidade = 9
                        self.jogador.forca_pulo = -12
                        self.jogador.animation_speed = 4
                        self.jogador.gravidade = 1.2
                    # Atualizar Inimigos
                    if self.mapa_atual_path == "SalaBoss.tmx":
                        self.jogador.velocidade_dash = 10
                        self.jogador.velocidade = 5
                        self.jogador.forca_pulo = -9.5
                        self.jogador.animation_speed = 7
                        self.jogador.gravidade = 0.6
                    self.inimigos.update() # Chama update() de todos os inimigos no grupo


                    new_projectiles = pygame.sprite.Group()
                    new_falling_objects = pygame.sprite.Group()
                    if self.boss_instance and not self.boss_instance.is_dead:
                         # Boss pode ter criado novos projéteis/objetos no seu update()
                         new_projectiles.add(self.boss_instance.projectiles_group.sprites())
                         new_falling_objects.add(self.boss_instance.falling_objects_group.sprites())
                         # Limpa os grupos internos do boss para não adicionar duplicado
                         self.boss_instance.projectiles_group.empty()
                         self.boss_instance.falling_objects_group.empty()

                    # Adiciona aos grupos globais
                    self.boss_projectiles.add(new_projectiles)
                    self.boss_falling_objects.add(new_falling_objects)
                    self.todos_sprites.add(new_projectiles) # Adiciona para desenho
                    self.todos_sprites.add(new_falling_objects) # Adiciona para desenho

                    # 2. Atualizar Grupos Auxiliares (projéteis, objetos caindo)
                    self.boss_projectiles.update(self.jogador) # Passa jogador para referência interna se necessário
                    self.boss_falling_objects.update(self.jogador)
                    # Atualizar Animações (após lógica de estado)
                    #
                    # 
                    # 
                    # 
                    # 
                    # 
                    
                    
                    
                    
                    
                    
                    
                    # self.todos_sprites.update() # <<< Assume que player/inimigo/npc tem update para animação ou chama aqui >>>











                    # Alternativa: chamar update_animation individualmente
                    # for sprite in self.todos_sprites:
                    #     if hasattr(sprite, 'update_animation'): sprite.update_animation()

                    # Colisão com Espinhos
                    if self.jogador and self.jogador.vida_atual > 0:
                        self.jogador.handle_espinho_colisions(self.espinho_maior_layer, self.espinho_menor_layer)


                    proj_hits = pygame.sprite.spritecollide(self.jogador, self.boss_projectiles, True, pygame.sprite.collide_mask)
                    for proj in proj_hits:
                         if self.jogador: self.jogador.receber_dano(proj.dano)
                         # Efeito sonoro/visual de hit

                    #   c) Jogador vs Objetos Caindo do Boss
                    fall_hits = pygame.sprite.spritecollide(self.jogador, self.boss_falling_objects, True, pygame.sprite.collide_mask)
                    for obj in fall_hits:
                         if self.jogador: self.jogador.receber_dano(obj.dano)
                         # Efeito sonoro/visual de hit

                    if self.boss_instance and self.boss_instance.is_dashing and self.boss_instance.can_dash_damage:
                             # Colisão direta com o rect do boss durante o dash
                             # Usar collide_mask se ambos tiverem mask, senão collide_rect
                        if pygame.sprite.collide_rect(self.jogador, self.boss_instance): # Ou collide_mask
                             print(f"    [COLLISION] Jogador atingido pelo DASH! Vida antes: {self.jogador.vida_atual}") # DEBUG
                             self.jogador.receber_dano(self.boss_instance.dash_dano)
                                 # Impede dano múltiplo na MESMA passagem do dash
                             self.boss_instance.can_dash_damage = False
                             print(f"    [COLLISION] Vida depois: {self.jogador.vida_atual}. can_dash_damage = False") # DEBUG
                                 # Adicionar efeito sonoro/visual de impacto e talvez empurrar o jogador

                    #   d) Jogador vs Melee do Boss
                    if self.boss_instance and self.boss_instance.is_melee_active and self.jogador:
                         melee_hitbox = self.boss_instance.get_melee_hitbox()
                         if melee_hitbox and self.jogador.collision_rect.colliderect(melee_hitbox):
                              # Aplicar dano apenas uma vez por ativação do melee
                              # (Pode precisar de um timer ou flag no jogador pós-hit)
                              self.jogador.receber_dano(self.boss_instance.melee_dano)
                              # Empurrar jogador?

                    # --- Checar Derrota ---
                    if self.jogador and self.jogador.vida_atual <= 0:
                        pygame.mixer.music.stop(); self.musica_atual = None
                        causa = "Eitaa, Perdeu!!"
                        if hasattr(self.jogador, 'morreu_queimado') and self.jogador.morreu_queimado: causa = "Olha o churrasco!"
                        elif hasattr(self.jogador, 'caiu_no_buraco') and self.jogador.caiu_no_buraco: causa = "Cuidado com o buraco!"
                        self.exibir_mensagem_final(causa, self.VERMELHO); continue

                    if self.mapa_atual_path == "SalaBoss.tmx" and self.boss_instance and self.boss_instance.is_dead:
                         # Checa se a animação de morte terminou ou espera um pouco
                         # Exemplo: espera 2 segundos após a morte antes de declarar vitória
                         if tempo_agora - self.boss_instance.last_attack_time > 2000: # Reusa last_attack_time como tempo da morte
                              if self.jogador and self.jogador.vida_atual > 0: # Só vence se vivo
                                   pygame.mixer.music.stop(); self.musica_atual = None
                                   self.exibir_mensagem_final("VOCÊ VENCEU!", self.AMARELO)
                                   self.game_state = "MENU" # Ou CREDITS
                                   continue

            # --- Desenho ---
            self.tela.fill(self.PRETO) # Limpa a tela

            if self.game_state == "MENU":
                self.main_menu.display_menu()
            elif self.game_state == "CREDITS":
                self.credits_menu.display_menu()
            elif self.game_state == "PLAYING":
                if self.jogador and self.tmx_data:
                    # --- Câmera ---
                    target_x = self.jogador.rect.centerx
                    target_y = self.jogador.rect.centery
                    cam_x = self.LARGURA / 2 - target_x * self.zoom_level
                    cam_y = self.ALTURA / 1.8 - target_y * self.zoom_level
                    # Limites
                    map_w_z = self.largura_mapa * self.zoom_level; map_h_z = self.altura_mapa_real * self.zoom_level
                    cam_x = min(0, max(self.LARGURA - map_w_z, cam_x)) if map_w_z > self.LARGURA else (self.LARGURA - map_w_z) / 2
                    cam_y = min(0, max(self.ALTURA - map_h_z, cam_y)) if map_h_z > self.ALTURA else (self.ALTURA - map_h_z) / 2
                    self.deslocamento_camera_x, self.deslocamento_camera_y = cam_x, cam_y

                    # --- Desenhar Jogo ---
                    # 1. Mapa
                    self.desenhar_mapa_com_zoom()
                    if self.boss_instance and self.boss_instance.is_melee_active == True:
                        self.boss_instance.desenhar_efeito_melee(self.tela, self.deslocamento_camera_x, self.deslocamento_camera_y)

                    
                    # FUNÇÃO QUE DESENHA O EFEITO DA PLAYER
                    self.jogador.desenhar_efeito_ataque(self.tela, self.deslocamento_camera_x, self.deslocamento_camera_y,self.inimigos)
                    
                    # 2. Sprites (com zoom)
                    for sprite in self.todos_sprites:
                            if isinstance(sprite, (inimigo.Inimigo2mp2, inimigo.ProjetilGeleia)):
                                sprite.draw(
                                    self.tela,
                                    zoom=self.zoom_level,
                                    deslocamento_x=self.deslocamento_camera_x,
                                    deslocamento_y=self.deslocamento_camera_y
                                )
                            else:
                                try:
                                    img = sprite.image # Pega a imagem atualizada
                                    w_z = int(sprite.rect.width * self.zoom_level)
                                    h_z = int(sprite.rect.height * self.zoom_level)
                                    if w_z > 0 and h_z > 0:
                                        img_scaled = pygame.transform.scale(img, (w_z, h_z))
                                        px = sprite.rect.x * self.zoom_level + cam_x
                                        py = sprite.rect.y * self.zoom_level + cam_y
                                        sprite_rect_tela = pygame.Rect(px, py, w_z, h_z)
                                        # Desenhar se visível
                                        if self.tela.get_rect().colliderect(sprite_rect_tela):
                                                self.tela.blit(img_scaled, sprite_rect_tela.topleft)
                                except: pass # Ignora erros de desenho
                                
                            if isinstance(sprite, BossFinal):
                              if sprite.is_melee_active:
                                   melee_box_mundo = sprite.get_melee_hitbox()
                                   if melee_box_mundo:
                                       # Converter para coordenadas da tela
                                       box_x_tela = melee_box_mundo.x * self.zoom_level + self.deslocamento_camera_x
                                       box_y_tela = melee_box_mundo.y * self.zoom_level + self.deslocamento_camera_y
                                       box_w_tela = melee_box_mundo.width * self.zoom_level
                                       box_h_tela = melee_box_mundo.height * self.zoom_level
                                       debug_rect_tela = pygame.Rect(box_x_tela, box_y_tela, box_w_tela, box_h_tela)
                                       pygame.draw.rect(self.tela, (255, 0, 0, 100), debug_rect_tela, 2) # Vermelho semi-transparente

                    for inimigo_atual in self.inimigos:
                        if isinstance(inimigo_atual, Inimigo1mp2) and callable(inimigo_atual.update):
                            inimigo_atual.update(self.tela)
                            inimigo_atual.draw(self.tela,
                            zoom_level=self.zoom_level,
                            deslocamento_camera_x=self.deslocamento_camera_x,
                            deslocamento_camera_y=self.deslocamento_camera_y
                        )
                        else:
                            inimigo_atual.update() # Chama update() de todos os inimigos no grupo

                    # 3. UI (HUD, Popups, Prompts)
                    self.desenhar_coracoes(); self.desenhar_pocoes(); self.desenhar_popup()
                    # Prompts
                    prompt_y = self.ALTURA - 40; prompt_size = 24
                    if self.mostrar_msg_npc:
                        self.draw_text("Pressione F para conversar", prompt_size, self.LARGURA // 2, prompt_y, self.AMARELO, self.arcane_font_path, center=True)
                    elif self.mostrar_prompt_porta:
                        # <<< MODIFICADO: Mensagem da porta contextual >>>
                        msg_porta = "Pressione E para interagir"
                        if self.mapa_atual_path == "Mapa.tmx": msg_porta = "Pressione E para próxima fase"
                        elif self.mapa_atual_path == "Mapa(2).tmx": msg_porta = "Pressione E para a Sala do Chefe"
                        elif self.mapa_atual_path == "SalaBoss.tmx": msg_porta = "Pressione E para sair"
                        # --- Fim da Modificação ---
                        self.draw_text(msg_porta, prompt_size, self.LARGURA // 2, prompt_y, self.AMARELO, self.arcane_font_path, center=True)
                    if self.boss_instance and not self.boss_instance.is_dead:
                         bar_width = self.LARGURA * 0.6
                         bar_height = 25
                         bar_x = (self.LARGURA - bar_width) / 2
                         bar_y = 30
                         hp_ratio = max(0, self.boss_instance.vida / self.boss_instance.vida_maxima)
                         fill_width = bar_width * hp_ratio

                         bg_rect = pygame.Rect(bar_x, bar_y, bar_width, bar_height)
                         fill_rect = pygame.Rect(bar_x, bar_y, fill_width, bar_height)

                         pygame.draw.rect(self.tela, (50, 0, 0), bg_rect) # Fundo vermelho escuro
                         pygame.draw.rect(self.tela, self.VERMELHO, fill_rect) # Barra vermelha
                         pygame.draw.rect(self.tela, self.BRANCO, bg_rect, 2) # Borda

                         # Nome do Boss (opcional)
                         self.draw_text("CHEFE FINAL", 20, self.LARGURA / 2, bar_y - 15, self.BRANCO, center=True)         
                    # 4. Interface de Conversa (se ativa)
                    if self.em_conversa: self.exibir_conversa()

            # --- Atualizar Tela ---
            pygame.display.flip()

        # --- Fim do Loop ---
        self.quit_game()

    def quit_game(self):
        """Encerra Pygame."""
        print("DEBUG: Chamando quit_game()")
        pygame.quit()
        print("DEBUG: Pygame finalizado.")
        sys.exit()

# --- Ponto de Entrada ---
if __name__ == '__main__':
    print("DEBUG: Executando __main__")
    if not pygame.get_init(): print("ERRO FATAL: Pygame não inicializado."); sys.exit()
    if not pygame.font.get_init(): print("ERRO FATAL: Pygame Font não inicializado."); pygame.quit(); sys.exit()

    game_instance = None
    try:
        print("DEBUG: Criando instância de Game...")
        game_instance = Game()
        print("DEBUG: Chamando game_instance.run()...")
        game_instance.run()
    except Exception as e:
         print("\n!!!!!!!!!!!!!!!! ERRO NÃO TRATADO !!!!!!!!!!!!!!")
         print(f"ERRO: {e}")
         import traceback; traceback.print_exc()
         print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n")
    finally:
        if pygame.get_init(): print("DEBUG: Saindo pelo finally, quit()"); pygame.quit()
        print("DEBUG: Fim da execução.")

# --- END OF FILE main.py ---wd
