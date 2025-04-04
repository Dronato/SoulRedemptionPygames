import pygame
from pytmx.util_pygame import load_pygame

def carregar_mapa(nome_arquivo):
    """Carrega os dados do mapa Tiled."""
    try:
        tmx_data = load_pygame(f"{nome_arquivo}")
        return tmx_data
    except FileNotFoundError:
        print(f"Erro: Mapa '{nome_arquivo}' não encontrado.")
        return None

def desenhar_mapa(tela, tmx_data, deslocamento_camera_x, deslocamento_camera_y):
    """Desenha o mapa na tela, aplicando o deslocamento da câmera."""

    # Ordem das camadas (ajuste conforme necessário)
    camadas_para_desenhar = [
        "Background",  # Primeiro: o fundo
        "Fundo",
        "Chão",       # Segundo: o chão
        "Espinho_Maior",
        "Espinho_Menor"
        # ... outras camadas em sua ordem desejada
    ]
    
    for nome_camada in camadas_para_desenhar:
        try:
            layer = tmx_data.get_layer_by_name(nome_camada)
        except ValueError:
            print(f"Aviso: Camada '{nome_camada}' não encontrada no mapa.")
            continue

        if hasattr(layer, 'tiles'):  # Camadas de tiles
            for x, y, gid in layer:
                tile = tmx_data.get_tile_image_by_gid(gid)
                if tile:
                    pos_x = x * tmx_data.tilewidth + deslocamento_camera_x
                    pos_y = y * tmx_data.tileheight + deslocamento_camera_y
                    tela.blit(tile, (pos_x, pos_y))
        elif isinstance(layer, pygame.Surface):  # Camadas de imagem (ImageLayer)
            tela.blit(layer, (deslocamento_camera_x, deslocamento_camera_y))
        elif hasattr(layer, 'image'):  # Para camadas de imagem com atributos de deslocamento
            offset_x = getattr(layer, 'offsetx', 0)
            offset_y = getattr(layer, 'offsety', 0)
            tela.blit(layer.image, (offset_x + deslocamento_camera_x, offset_y + deslocamento_camera_y))
def criar_mapa_rects(tmx_data, layer_name):
    """Cria retângulos de colisão a partir de uma camada específica do mapa."""
    rects = []
    layer = tmx_data.get_layer_by_name(layer_name)
    for x, y, gid in layer:
        if gid != 0:  # Assume que gid 0 é espaço vazio
            rect = pygame.Rect(x * tmx_data.tilewidth, y * tmx_data.tileheight,
                                tmx_data.tilewidth, tmx_data.tileheight)
            rects.append(rect)
    return rects

def criar_objetos_espinhos(tmx_data, layer_name):
    """Cria retângulos para os objetos da camada de espinhos."""
    rects = []
    layer = tmx_data.get_layer_by_name(layer_name)
    for obj in layer:
        rect = pygame.Rect(obj.x, obj.y, obj.width, obj.height)
        rects.append(rect)
    return rects
# --- START OF FILE map_loader.py ---
# ... (código existente: carregar_mapa, desenhar_mapa, criar_mapa_rects) ...

def criar_objetos_retangulos(tmx_data, layer_name):
    """Cria retângulos a partir dos OBJETOS de uma camada específica do mapa."""
    rects = []
    try:
        object_layer = tmx_data.get_layer_by_name(layer_name)
        # Iterar sobre os objetos na camada
        for obj in object_layer:
            # Criar um pygame.Rect com as coordenadas e dimensões do objeto Tiled
            # Certifique-se que as propriedades x, y, width, height existem no obj
            if hasattr(obj, 'x') and hasattr(obj, 'y') and hasattr(obj, 'width') and hasattr(obj, 'height'):
                rect = pygame.Rect(obj.x, obj.y, obj.width, obj.height)
                rects.append(rect)
            else:
                print(f"Aviso: Objeto na camada '{layer_name}' sem propriedades x, y, width ou height.")
    except ValueError:
        print(f"Aviso: Camada de Objetos '{layer_name}' não encontrada no mapa.")
    return rects

# --- Função antiga criar_objetos_espinhos removida ou renomeada se necessário ---
# Se você usava criar_objetos_espinhos, pode mantê-la ou
# usar criar_objetos_retangulos para os espinhos também, se forem objetos.
# Se os espinhos são tiles, mantenha criar_mapa_rects ou a lógica em handle_espinho_colisions.


# --- END OF FILE map_loader.py ---