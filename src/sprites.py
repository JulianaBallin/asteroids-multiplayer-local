import math
from random import uniform
import pygame as pg
import config as C
from utils import Vec, ang_vec, envolver, circulo


class Bala(pg.sprite.Sprite):
    # Projétil disparado pela nave de um jogador
    def __init__(self, pos: Vec, vel: Vec, dono: int):
        super().__init__()
        self.pos = Vec(pos)
        self.vel = Vec(vel)
        self.dono = dono   # índice do jogador dono da bala
        self.ttl = C.TTL_BALA
        self.r = C.RAIO_BALA
        self.rect = pg.Rect(0, 0, 4, 4)

    def update(self, dt: float):
        self.pos += self.vel * dt
        self.pos = envolver(self.pos)
        self.ttl -= dt
        if self.ttl <= 0:
            self.kill()
        self.rect.center = (int(self.pos.x), int(self.pos.y))

    def draw(self, surf: pg.Surface, cor):
        circulo(surf, self.pos, self.r, cor)


class BalaOVNI(pg.sprite.Sprite):
    # Projétil disparado pelo OVNI inimigo
    def __init__(self, pos: Vec, vel: Vec):
        super().__init__()
        self.pos = Vec(pos)
        self.vel = Vec(vel)
        self.ttl = C.TTL_BALA_OVNI
        self.r = C.RAIO_BALA
        self.rect = pg.Rect(0, 0, 4, 4)

    def update(self, dt: float):
        self.pos += self.vel * dt
        self.pos = envolver(self.pos)
        self.ttl -= dt
        if self.ttl <= 0:
            self.kill()
        self.rect.center = (int(self.pos.x), int(self.pos.y))

    def draw(self, surf: pg.Surface):
        circulo(surf, self.pos, self.r, (255, 80, 80))


class PulsoEMP(pg.sprite.Sprite):
    def __init__(self, pos: Vec, dono_id: int):
        super().__init__()
        self.pos = Vec(pos)
        self.dono_id = dono_id
        self.r = 0.0
        self.rect = pg.Rect(0, 0, int(C.EMP_RAIO_MAX * 2) + 8, int(C.EMP_RAIO_MAX * 2) + 8)

    def ancorar(self, pos: Vec):
        self.pos.xy = pos

    def update(self, dt: float):
        self.r += C.EMP_VEL_EXPANSAO * dt
        if self.r >= C.EMP_RAIO_MAX:
            self.kill()
        self.rect.center = (int(self.pos.x), int(self.pos.y))

    def draw(self, surf: pg.Surface):
        if self.r < 3.0:
            return
        ro = max(4, int(self.r))
        ri = max(2, ro - 6)
        circulo(surf, self.pos, ro, C.EMP_COR_ANEL_A, esp=2)
        circulo(surf, self.pos, ri, C.EMP_COR_ANEL_B, esp=1)


class Asteroide(pg.sprite.Sprite):
    def __init__(self, pos: Vec, vel: Vec, tamanho: str):
        super().__init__()
        self.pos = Vec(pos)
        self.vel = Vec(vel)
        self.tamanho = tamanho
        self.r = C.TAMANHOS_AST[tamanho]["r"]
        self.forma = self._gerar_forma()
        self.rect = pg.Rect(0, 0, self.r * 2, self.r * 2)

    def _gerar_forma(self):
        # Polígono irregular com variação aleatória nos vértices
        n = 12 if self.tamanho == "G" else 10 if self.tamanho == "M" else 8
        pts = []
        for i in range(n):
            ang = i * (360 / n)
            r = self.r * uniform(0.75, 1.2)
            pts.append(Vec(math.cos(math.radians(ang)), math.sin(math.radians(ang))) * r)
        return pts

    def update(self, dt: float):
        self.pos += self.vel * dt
        self.pos = envolver(self.pos)
        self.rect.center = (int(self.pos.x), int(self.pos.y))

    def draw(self, surf: pg.Surface):
        pg.draw.polygon(surf, C.BRANCO, [(self.pos + p) for p in self.forma], width=1)


class Carcaca(pg.sprite.Sprite):
    # Destroços da nave de um jogador eliminado — pode ser resgatada por aliados
    def __init__(self, pos: Vec, angulo: float, jogador_id: int):
        super().__init__()
        self.pos = Vec(pos)
        self.angulo = angulo
        self.jogador_id = jogador_id
        self.cor = C.CORES_JOGADORES[jogador_id]
        self.ttl = C.TTL_CARCACA
        self.progresso = 0.0   # 0.0 a 1.0 — preenchido pelo Mundo durante o resgate
        self.r = C.RAIO_NAVE
        self.rect = pg.Rect(0, 0, self.r * 2, self.r * 2)

    def update(self, dt: float):
        self.ttl -= dt
        if self.ttl <= 0:
            self.kill()
        self.rect.center = (int(self.pos.x), int(self.pos.y))

    def draw(self, surf: pg.Surface):
        # Pisca lentamente para indicar que está disponível para resgate
        if int(self.ttl * 3) % 2 == 0:
            d = ang_vec(self.angulo)
            p1 = self.pos + d * self.r
            p2 = self.pos + ang_vec(self.angulo + 140) * self.r * 0.9
            p3 = self.pos + ang_vec(self.angulo - 140) * self.r * 0.9
            pg.draw.polygon(surf, self.cor, [p1, p2, p3], width=1)

        # Barra de progresso do resgate acima da carcaça
        if self.progresso > 0:
            bx = int(self.pos.x) - 25
            by = int(self.pos.y) - self.r - 14
            pg.draw.rect(surf, C.CINZA, (bx, by, 50, 6))
            pg.draw.rect(surf, C.COR_RESGATE, (bx, by, int(50 * self.progresso), 6))


class Nave(pg.sprite.Sprite):
    def __init__(self, pos: Vec, jogador_id: int):
        super().__init__()
        self.pos = Vec(pos)
        self.vel = Vec(0, 0)
        self.angulo = -90.0
        self.cooldown_tiro = 0.0
        self.invuln = 0.0
        self.vidas = C.VIDAS_INICIAIS
        self.pontos = 0
        self.jogador_id = jogador_id
        self.cor = C.CORES_JOGADORES[jogador_id]
        self.r = C.RAIO_NAVE
        self.ativa = True
        self.rect = pg.Rect(0, 0, self.r * 2, self.r * 2)

    def controlar(self, teclas, dt: float):
        ctrl = C.CONTROLES[self.jogador_id]
        if teclas[ctrl['esq']]:
            self.angulo -= C.VEL_ROTACAO * dt
        if teclas[ctrl['dir']]:
            self.angulo += C.VEL_ROTACAO * dt
        if teclas[ctrl['cima']]:
            self.vel += ang_vec(self.angulo) * C.EMPUXO * dt
        self.vel *= C.FRICCAO

    def atirar(self) -> 'Bala | None':
        if self.cooldown_tiro > 0:
            return None
        d = ang_vec(self.angulo)
        self.cooldown_tiro = C.TAXA_TIRO
        return Bala(self.pos + d * (self.r + 6), self.vel + d * C.VEL_BALA, self.jogador_id)

    def hiperspace(self):
        self.pos = Vec(uniform(0, C.LARGURA), uniform(0, C.ALTURA))
        self.vel.xy = (0, 0)
        self.invuln = 1.0
        self.pontos = max(0, self.pontos - C.CUSTO_HIPER)

    def update(self, dt: float):
        if not self.ativa:
            return
        if self.cooldown_tiro > 0:
            self.cooldown_tiro -= dt
        if self.invuln > 0:
            self.invuln -= dt
        self.pos += self.vel * dt
        self.pos = envolver(self.pos)
        self.rect.center = (int(self.pos.x), int(self.pos.y))

    def draw(self, surf: pg.Surface):
        if not self.ativa:
            return
        d = ang_vec(self.angulo)
        p1 = self.pos + d * self.r
        p2 = self.pos + ang_vec(self.angulo + 140) * self.r * 0.9
        p3 = self.pos + ang_vec(self.angulo - 140) * self.r * 0.9

        # Anel piscante durante invulnerabilidade
        if self.invuln > 0 and int(self.invuln * 10) % 2 == 0:
            circulo(surf, self.pos, self.r + 6, self.cor)

        pg.draw.polygon(surf, self.cor, [p1, p2, p3], width=2)


class OVNI(pg.sprite.Sprite):
    def __init__(self, pos: Vec, pequeno: bool):
        super().__init__()
        self.pos = Vec(pos)
        self.pequeno = pequeno
        p = C.OVNI_PEQUENO if pequeno else C.OVNI_GRANDE
        self.r = p["r"]
        self.mira = p["mira"]
        self.cooldown = C.INTERVALO_TIRO_OVNI
        self.direcao = Vec(1 if uniform(0, 1) < 0.5 else -1, 0)
        self.rect = pg.Rect(0, 0, self.r * 2, self.r * 2)

    def update(self, dt: float):
        self.pos += self.direcao * C.VEL_OVNI * dt
        self.cooldown -= dt
        # Sai da tela → se destrói
        if self.pos.x < -self.r * 2 or self.pos.x > C.LARGURA + self.r * 2:
            self.kill()
        self.rect.center = (int(self.pos.x), int(self.pos.y))

    def atirar_em(self, alvo: Vec) -> 'BalaOVNI | None':
        if self.cooldown > 0:
            return None
        d = Vec(alvo) - self.pos
        if d.length_squared() == 0:
            d = Vec(self.direcao)
        else:
            d = d.normalize()
        # Adiciona erro de mira proporcional à dificuldade
        d = d.rotate(uniform(-(1 - self.mira) * 60, (1 - self.mira) * 60))
        self.cooldown = C.INTERVALO_TIRO_OVNI
        return BalaOVNI(self.pos + d * (self.r + 6), d * C.VEL_BALA_OVNI)

    def draw(self, surf: pg.Surface):
        w, h = self.r * 2, self.r
        pg.draw.ellipse(surf, C.BRANCO,
                        (int(self.pos.x - w / 2), int(self.pos.y - h / 2), w, h), width=1)
        pg.draw.ellipse(surf, C.BRANCO,
                        (int(self.pos.x - w / 4), int(self.pos.y - h), w // 2, int(h * 0.7)), width=1)
