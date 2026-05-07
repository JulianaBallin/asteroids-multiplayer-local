import pygame as pg

# Tela
LARGURA = 1280
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
    (320, 384),   # J1: esquerda (25% da largura)
    (960, 384),   # J2: direita  (75% da largura)
    (640, 230),   # J3: topo     (centro, acima)
    (640, 560),   # J4: baixo    (centro, abaixo)
]

# Controles Tectoy por jogador
# Ordem: esquerda, direita, cima, fogo, hiper (Pulsar EMP)
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
MAX_BALAS_POR_JOGADOR = 4

# Pulsar EMP (mesma tecla que o antigo HIPER)
EMP_RAIO_MAX = 220.0
EMP_VEL_EXPANSAO = 480.0
EMP_HIT_BAND = 20.0
EMP_COOLDOWN = 7.0
EMP_COR_ANEL_A = (190, 120, 255)   # roxo elétrico externo
EMP_COR_ANEL_B = (130, 60, 255)    # roxo médio
EMP_COR_FLASH = (230, 190, 255)
EMP_COR_JAM = (255, 80, 40)
EMP_AST_IMPULSO = 380.0
EMP_INVULN_ALIADO = 2.2
EMP_JAM_SEG = 2.5
EMP_JAM_ROT_FATOR = 0.32

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

# Rastro Gravitacional
RASTRO_INTERVALO = 0.06
RASTRO_TTL = 2.4
RASTRO_RAIO_VISUAL = 7
RASTRO_RAIO_INFLUENCIA = 110
RASTRO_FORCA_ASTEROIDE = 220.0
RASTRO_FORCA_BALA = 320.0
RASTRO_FORCA_NAVE = 150.0
RASTRO_COR_EXTERNA = (120, 80, 255)
RASTRO_COR_INTERNA = (80, 210, 255)
# Joystick
JOY_AXIS_LEFT_X = 0
JOY_AXIS_LEFT_Y = 1
JOY_BTN_SHOOT = 7     # R2/RT (digital) em mapeamento comum
JOY_BTN_SHOOT_ALT = 5 # R1/RB fallback
JOY_BTN_EMP = 4       # L1/LB
JOY_BTN_BACK = 8      # Select/Back
JOY_BTN_START = 9     # Start/Menu
JOY_DEADZONE = 0.25
