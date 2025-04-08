# --- START OF FILE map_loader.py ---

import pygame
from pytmx.util_pygame import load_pygame
import os

def carregar_mapa(nome_arquivo):
    """Carrega os dados do mapa Tiled."""
    # Assume que o arquivo está na mesma pasta ou em uma subpasta 'maps'
    # Tenta carregar diretamente primeiro
    if not os.path.isfile(nome_arquivo):
        # Se não encontrar, tenta procurar na pasta raiz do script
        base_dir = os.path.dirname(os.path.abspath(__file__))
        caminho_alternativo = os.path.join(base_dir, nome_arquivo)
        if os.path.isfile(caminho_alternativo):
            nome_arquivo = caminho_alternativo
        else:
            # Se ainda não encontrar, tenta em uma pasta 'maps'
            caminho_maps = os.path.join(base_dir, "maps", nome_arquivo)
            if os.path.isfile(caminho_maps):
                nome_arquivo = caminho_maps
            else:
                print(f"ERRO: Mapa '{nome_arquivo}' não encontrado nas pastas usuais.")
                return None # Retorna None se não encontrar o arquivo

    print(f"[DEBUG] Tentando carregar mapa de: {os.path.abspath(nome_arquivo)}")

    try:
        tmx_data = load_pygame(nome_arquivo)
        print(f"[DEBUG] Mapa '{os.path.basename(nome_arquivo)}' carregado com sucesso.")
        return tmx_data
    except FileNotFoundError:
        # Esta exceção não deveria ocorrer por causa das verificações acima, mas por segurança
        print(f"Erro Inesperado: Mapa '{nome_arquivo}' não encontrado mesmo após verificação.")
        return None
    except Exception as e:
        print(f"Erro ao carregar o mapa '{nome_arquivo}' com pytmx: {e}")
        import traceback
        traceback.print_exc() # Imprime mais detalhes do erro
        return None


def desenhar_mapa(tela, tmx_data, deslocamento_camera_x, deslocamento_camera_y):
    """
    Desenha o mapa na tela (sem zoom), aplicando o deslocamento da câmera.
    Esta função NÃO é usada por padrão no main.py atual que usa zoom.
    """
    if not tmx_data:
        print("AVISO: Tentativa de desenhar mapa sem dados TMX carregados (desenhar_mapa).")
        return

    # Ordem das camadas (ajuste conforme necessário ou passe como argumento)
    camadas_para_desenhar = [
        "Background",  # Primeiro: o fundo mais distante
        "Fundo",       # Segundo: elementos de fundo
        "Chão",        # Plataformas e chão principal
        "RampaParaEsquerda", # Rampas
        "RampaParaDireita",
        "Espinho_Maior", # Perigos
        "Espinho_Menor",
        "FiguraPorta", # Elementos decorativos/interativos
        "Porta",
        "Representacao_Porta",
        'Detalhes',
        'Lava'
        
        # Camada de interação (pode ser objeto ou tile)
        # ... adicione outras camadas na ordem desejada
    ]

    for nome_camada in camadas_para_desenhar:
        try:
            layer = tmx_data.get_layer_by_name(nome_camada)
        except ValueError:
            # Não é um erro grave, a camada pode não existir no mapa atual
            # print(f"Aviso: Camada '{nome_camada}' não encontrada no mapa (desenhar_mapa).")
            continue

        # Desenhar Camadas de Tiles
        if hasattr(layer, 'tiles'):
            for x, y, gid in layer:
                tile = tmx_data.get_tile_image_by_gid(gid)
                if tile:
                    # Aplicar deslocamento da câmera
                    pos_x = x * tmx_data.tilewidth + deslocamento_camera_x
                    pos_y = y * tmx_data.tileheight + deslocamento_camera_y
                    # Otimização: Só desenhar se estiver visível na tela (aproximado)
                    tile_rect = pygame.Rect(pos_x, pos_y, tmx_data.tilewidth, tmx_data.tileheight)
                    if tela.get_rect().colliderect(tile_rect):
                         tela.blit(tile, (pos_x, pos_y))

        # Desenhar Camadas de Imagem (ImageLayer)
        elif hasattr(layer, 'image'): # Verifica se tem o atributo 'image'
            try:
                 # Camadas de imagem podem ter offset
                 offset_x = getattr(layer, 'offsetx', 0)
                 offset_y = getattr(layer, 'offsety', 0)
                 pos_x = offset_x + deslocamento_camera_x
                 pos_y = offset_y + deslocamento_camera_y
                 # Otimização de visibilidade
                 img_rect = layer.image.get_rect(topleft=(pos_x, pos_y))
                 if tela.get_rect().colliderect(img_rect):
                      tela.blit(layer.image, (pos_x, pos_y))
            except AttributeError:
                print(f"Aviso: Camada de imagem '{nome_camada}' encontrada, mas falta atributo 'image'.")


def criar_mapa_rects(tmx_data, layer_name):
    """Cria uma lista de pygame.Rect para todos os tiles de uma camada específica."""
    rects = []
    if not tmx_data: return rects # Retorna lista vazia se não há mapa

    try:
        layer = tmx_data.get_layer_by_name(layer_name)
        if not hasattr(layer, 'tiles'):
            # print(f"Aviso: Camada '{layer_name}' encontrada, mas não é uma camada de tiles.")
            return rects # Retorna lista vazia se não for camada de tile

        tile_width = tmx_data.tilewidth
        tile_height = tmx_data.tileheight

        for x, y, gid in layer:
            if gid != 0:  # Assume que gid 0 é espaço vazio (transparente)
                # Cria o retângulo na posição do mundo (sem zoom)
                rect = pygame.Rect(x * tile_width, y * tile_height, tile_width, tile_height)
                rects.append(rect)
        # print(f"[DEBUG] Criados {len(rects)} retângulos para a camada '{layer_name}'.")

    except ValueError:
        # A camada pode não existir neste mapa específico, não é um erro fatal.
        print(f"Aviso: Camada de Tiles '{layer_name}' não encontrada ao criar rects.")
    except Exception as e:
        print(f"Erro inesperado ao criar rects para a camada '{layer_name}': {e}")

    return rects


def criar_objetos_retangulos(tmx_data, layer_name):
    """Cria uma lista de pygame.Rect a partir dos OBJETOS de uma Object Layer específica."""
    rects = []
    if not tmx_data: return rects # Retorna lista vazia se não há mapa

    try:
        object_layer = tmx_data.get_layer_by_name(layer_name)
        # Verificar se é realmente uma camada de objetos (pytmx pode ter tipos diferentes)
        # A iteração direta geralmente funciona para camadas de objetos em pytmx
        # if not isinstance(object_layer, ???): # Verificar tipo específico se necessário
        #     print(f"Aviso: Camada '{layer_name}' não é uma camada de objetos reconhecida.")
        #     return rects

        for obj in object_layer:
            # Objetos em Tiled têm x, y, width, height
            if hasattr(obj, 'x') and hasattr(obj, 'y') and hasattr(obj, 'width') and hasattr(obj, 'height'):
                # Cria o retângulo na posição e tamanho definidos no Tiled (sem zoom)
                rect = pygame.Rect(obj.x, obj.y, obj.width, obj.height)
                rects.append(rect)
            else:
                # Isso pode acontecer se houver objetos não retangulares (elipse, ponto, polígono)
                # ou se a camada contiver algo inesperado.
                # print(f"Aviso: Objeto na camada '{layer_name}' não possui x, y, width ou height. Tipo: {type(obj)}")
                pass # Ignora objetos que não são retangulares por padrão

        # print(f"[DEBUG] Criados {len(rects)} retângulos de objetos para a camada '{layer_name}'.")

    except ValueError:
        # A camada de objetos pode não existir neste mapa, não é um erro fatal.
        print(f"Aviso: Camada de Objetos '{layer_name}' não encontrada ao criar rects.")
    except Exception as e:
        print(f"Erro inesperado ao criar rects de objetos para a camada '{layer_name}': {e}")

    return rects

# Função criar_objetos_espinhos removida pois criar_objetos_retangulos é mais genérica
# Se os espinhos eram TILES, use criar_mapa_rects com o nome da camada de tiles dos espinhos.
# Se os espinhos eram OBJETOS, use criar_objetos_retangulos com o nome da camada de objetos dos espinhos.
# A lógica de dano dos espinhos em player.py parece assumir que são TILES (usa gid).

# --- END OF FILE map_loader.py ---