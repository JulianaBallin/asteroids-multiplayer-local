import math
from random import random, uniform
import pygame as pg
import config as C

# Alias para vetor 2D do pygame
Vec = pg.math.Vector2


def envolver(pos: Vec) -> Vec:
    # Faz a posição aparecer no lado oposto ao sair da tela
    return Vec(pos.x % C.LARGURA, pos.y % C.ALTURA)


def ang_vec(graus: float) -> Vec:
    # Converte ângulo em graus para vetor unitário
    rad = math.radians(graus)
    return Vec(math.cos(rad), math.sin(rad))


def vec_aleatorio() -> Vec:
    # Gera vetor unitário em direção aleatória
    a = uniform(0, math.tau)
    return Vec(math.cos(a), math.sin(a))


def borda_aleatoria() -> Vec:
    # Gera posição aleatória em uma das bordas da tela
    if random() < 0.5:
        x = uniform(0, C.LARGURA)
        y = 0 if random() < 0.5 else C.ALTURA
    else:
        x = 0 if random() < 0.5 else C.LARGURA
        y = uniform(0, C.ALTURA)
    return Vec(x, y)


def poly(surf: pg.Surface, pts, cor=None):
    pg.draw.polygon(surf, cor or C.BRANCO, list(pts), width=1)


def circulo(surf: pg.Surface, pos: Vec, r: int, cor=None, esp: int = 1):
    pg.draw.circle(surf, cor or C.BRANCO, (int(pos.x), int(pos.y)), r, width=esp)


def txt(surf: pg.Surface, font: pg.font.Font, s: str, x: int, y: int, cor=None):
    s = font.render(s, True, cor or C.BRANCO)
    surf.blit(s, (x, y))
