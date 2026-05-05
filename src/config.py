import pygame as pg

# Tela
LARGURA = 960
ALTURA = 720
FPS = 60

# Máximo de jogadores simultâneos
MAX_JOGADORES = 4

# Cores por jogador (ciano, amarelo, verde, vermelho)
CORES_JOGADORES = [
    (0, 200, 255),
    (255, 220, 0),
    (0, 255, 100),
    (255, 80, 80),
]

# Posições de spawn iniciais por jogador
POSICOES_SPAWN = [
    (240, 384),
    (720, 384),
    (480, 220),
    (480, 580),
]

# Controles Tectoy por jogador
# Ordem: esquerda, direita, cima, fogo, hiperspace
CONTROLES = [
    # J1: WASD
    {'esq': pg.K_a, 'dir': pg.K_d, 'cima': pg.K_w, 'fogo': pg.K_LSHIFT, 'hiper': pg.K_q},
    # J2: setas do teclado
    {'esq': pg.K_LEFT, 'dir': pg.K_RIGHT, 'cima': pg.K_UP, 'fogo': pg.K_RSHIFT, 'hiper': pg.K_p},
    # J3: IJKL
    {'esq': pg.K_j, 'dir': pg.K_l, 'cima': pg.K_i, 'fogo': pg.K_h, 'hiper': pg.K_y},
    # J4: teclado numérico
    {'esq': pg.K_KP4, 'dir': pg.K_KP6, 'cima': pg.K_KP8, 'fogo': pg.K_KP0, 'hiper': pg.K_KP_ENTER},
]

# Nave
VIDAS_INICIAIS = 3
TEMPO_SEGURO = 2.0
ATRASO_ONDA = 2.0
RAIO_NAVE = 15
VEL_ROTACAO = 220.0
EMPUXO = 220.0
FRICCAO = 0.995
TAXA_TIRO = 0.2
VEL_BALA = 420.0
CUSTO_HIPER = 250
MAX_BALAS_POR_JOGADOR = 4

# Asteroides
VEL_AST_MIN = 30.0
VEL_AST_MAX = 90.0
TAMANHOS_AST = {
    "G": {"r": 46, "pontos": 20, "divide": ["M", "M"]},
    "M": {"r": 24, "pontos": 50, "divide": ["P", "P"]},
    "P": {"r": 12, "pontos": 100, "divide": []},
}

# Balas
RAIO_BALA = 2
TTL_BALA = 1.0

# OVNI
INTERVALO_OVNI = 15.0
VEL_OVNI = 80.0
INTERVALO_TIRO_OVNI = 1.2
VEL_BALA_OVNI = 260.0
TTL_BALA_OVNI = 1.8
OVNI_GRANDE = {"r": 18, "pontos": 200, "mira": 0.2}
OVNI_PEQUENO = {"r": 12, "pontos": 1000, "mira": 0.6}

# Cores gerais
BRANCO = (240, 240, 240)
CINZA = (80, 80, 80)
CINZA_CLARO = (160, 160, 160)
PRETO = (0, 0, 0)

DURACAO_FADE = 1.5

# Modos de jogo disponíveis
class Modo:
    SOLO            = "solo"
    COOPERATIVO     = "cooperativo"
    DUELO           = "duelo"
    TODOS_CONTRA_TODOS = "ffa"
    EQUIPES         = "equipes"

# Mecânica de resgate — jogador morto pode ser revivido por aliado próximo
ALCANCE_RESGATE = 80      # distância máxima em pixels para iniciar o resgate
DURACAO_RESGATE = 3.0     # segundos necessários para completar o resgate
TTL_CARCACA = 10.0        # tempo que a carcaça permanece disponível no mapa
COR_RESGATE = (0, 255, 120)  # cor da barra de progresso de resgate
