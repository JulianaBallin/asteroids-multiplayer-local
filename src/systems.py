from random import uniform
import pygame as pg
import config as C
from sprites import Asteroide, BalaOVNI, Carcaca, Nave, OVNI
from utils import Vec, borda_aleatoria, vec_aleatorio


class Mundo:
    def __init__(self, num_jogadores: int):
        self.num_jogadores = num_jogadores

        # Cria as naves dos jogadores nas posições de spawn
        self.naves: list[Nave] = []
        for i in range(num_jogadores):
            self.naves.append(Nave(Vec(*C.POSICOES_SPAWN[i]), i))

        # Grupo de balas separado por jogador para rastrear pontuação
        self.balas: list[pg.sprite.Group] = [pg.sprite.Group() for _ in range(num_jogadores)]
        self.balas_ovni = pg.sprite.Group()
        self.asteroides = pg.sprite.Group()
        self.ovnis = pg.sprite.Group()
        self.carcacas = pg.sprite.Group()

        # Dicionário que rastreia o tempo que cada nave fica próxima de cada carcaça
        # estrutura: {id(carcaca): {jogador_id: segundos_acumulados}}
        self.tempos_resgate: dict[int, dict[int, float]] = {}

        self.onda = 0
        self.cool_onda = C.ATRASO_ONDA
        self.timer_ovni = C.INTERVALO_OVNI
        self.fim_de_jogo = False

    # --- consultas de estado ---

    def naves_vivas(self) -> list[Nave]:
        return [n for n in self.naves if n.ativa]

    # --- criação de entidades ---

    def _criar_asteroide(self, pos: Vec, vel: Vec, tamanho: str):
        self.asteroides.add(Asteroide(pos, vel, tamanho))

    def _criar_ovni(self):
        if self.ovnis:
            return
        pequeno = uniform(0, 1) < 0.5
        y = uniform(0, C.ALTURA)
        x = 0 if uniform(0, 1) < 0.5 else C.LARGURA
        o = OVNI(Vec(x, y), pequeno)
        o.direcao = Vec(1, 0) if x == 0 else Vec(-1, 0)
        self.ovnis.add(o)

    def iniciar_onda(self):
        self.onda += 1
        # Quantidade de asteroides cresce com a onda
        for _ in range(3 + self.onda):
            pos = borda_aleatoria()
            vel = vec_aleatorio() * uniform(C.VEL_AST_MIN, C.VEL_AST_MAX)
            self._criar_asteroide(pos, vel, "G")

    # --- ações dos jogadores ---

    def tentar_atirar(self, jogador_id: int):
        nave = self.naves[jogador_id]
        if not nave.ativa:
            return
        if len(self.balas[jogador_id]) >= C.MAX_BALAS_POR_JOGADOR:
            return
        b = nave.atirar()
        if b:
            self.balas[jogador_id].add(b)

    def hiperspace(self, jogador_id: int):
        if self.naves[jogador_id].ativa:
            self.naves[jogador_id].hiperspace()

    # --- loop principal ---

    def update(self, dt: float, teclas):
        vivas = self.naves_vivas()
        if not vivas:
            self.fim_de_jogo = True
            return

        # Atualiza naves e balas
        for nave in vivas:
            nave.controlar(teclas, dt)
            nave.update(dt)

            # Tiro contínuo enquanto a tecla de fogo estiver pressionada
            if teclas[C.CONTROLES[nave.jogador_id]['fogo']]:
                self.tentar_atirar(nave.jogador_id)

        for grupo in self.balas:
            grupo.update(dt)
        self.balas_ovni.update(dt)
        self.asteroides.update(dt)
        self.ovnis.update(dt)
        self.carcacas.update(dt)

        # OVNI mira na nave viva mais próxima
        for ovni in self.ovnis:
            if not vivas:
                break
            alvo = min(vivas, key=lambda n: (n.pos - ovni.pos).length())
            b = ovni.atirar_em(alvo.pos)
            if b:
                self.balas_ovni.add(b)

        # Temporizador de spawn do OVNI
        self.timer_ovni -= dt
        if self.timer_ovni <= 0 and not self.ovnis:
            self._criar_ovni()
            self.timer_ovni = C.INTERVALO_OVNI

        self._resolver_colisoes()
        self._atualizar_resgates(dt)

        # Nova onda quando todos os asteroides forem destruídos
        if not self.asteroides:
            self.cool_onda -= dt
            if self.cool_onda <= 0:
                self.iniciar_onda()
                self.cool_onda = C.ATRASO_ONDA

    # --- colisões ---

    def _resolver_colisoes(self):
        # Balas dos jogadores vs asteroides
        for i, grupo in enumerate(self.balas):
            nave = self.naves[i]
            for ast in list(self.asteroides):
                for bala in list(grupo):
                    if (ast.pos - bala.pos).length() < ast.r:
                        self._dividir_asteroide(ast, nave)
                        bala.kill()
                        break

        # Balas dos jogadores vs OVNI
        for i, grupo in enumerate(self.balas):
            nave = self.naves[i]
            for ovni in list(self.ovnis):
                for bala in list(grupo):
                    if (ovni.pos - bala.pos).length() < ovni.r + bala.r:
                        pts = C.OVNI_PEQUENO["pontos"] if ovni.pequeno else C.OVNI_GRANDE["pontos"]
                        nave.pontos += pts
                        ovni.kill()
                        bala.kill()
                        break

        # Balas do OVNI vs naves
        for nave in self.naves_vivas():
            if nave.invuln > 0:
                continue
            for bala in list(self.balas_ovni):
                if (nave.pos - bala.pos).length() < nave.r + bala.r:
                    bala.kill()
                    self._nave_morreu(nave)
                    break

        # Naves vs asteroides
        for nave in self.naves_vivas():
            if nave.invuln > 0:
                continue
            for ast in list(self.asteroides):
                if (nave.pos - ast.pos).length() < nave.r + ast.r:
                    self._nave_morreu(nave)
                    break

        # Naves vs OVNI
        for nave in self.naves_vivas():
            if nave.invuln > 0:
                continue
            for ovni in list(self.ovnis):
                if (nave.pos - ovni.pos).length() < nave.r + ovni.r:
                    self._nave_morreu(nave)
                    break

    def _dividir_asteroide(self, ast: Asteroide, nave: Nave):
        nave.pontos += C.TAMANHOS_AST[ast.tamanho]["pontos"]
        pos = Vec(ast.pos)
        fragmentos = C.TAMANHOS_AST[ast.tamanho]["divide"]
        ast.kill()
        for t in fragmentos:
            vel = vec_aleatorio() * uniform(C.VEL_AST_MIN, C.VEL_AST_MAX) * 1.2
            self._criar_asteroide(pos, vel, t)

    def _nave_morreu(self, nave: Nave):
        nave.vidas -= 1
        if nave.vidas <= 0:
            # Eliminado — cria carcaça para possível resgate
            nave.ativa = False
            c = Carcaca(Vec(nave.pos), nave.angulo, nave.jogador_id)
            self.carcacas.add(c)
            self.tempos_resgate[id(c)] = {}
        else:
            # Respawn na posição inicial com invulnerabilidade
            nave.pos = Vec(*C.POSICOES_SPAWN[nave.jogador_id])
            nave.vel = Vec(0, 0)
            nave.angulo = -90.0
            nave.invuln = C.TEMPO_SEGURO

    # --- mecânica de resgate ---

    def _atualizar_resgates(self, dt: float):
        for carcaca in list(self.carcacas):
            cid = id(carcaca)
            if cid not in self.tempos_resgate:
                self.tempos_resgate[cid] = {}

            for nave in self.naves_vivas():
                # Jogador não pode se auto-resgatar
                if nave.jogador_id == carcaca.jogador_id:
                    continue

                dist = (nave.pos - carcaca.pos).length()
                if dist <= C.ALCANCE_RESGATE:
                    # Acumula tempo de proximidade
                    atual = self.tempos_resgate[cid].get(nave.jogador_id, 0.0)
                    self.tempos_resgate[cid][nave.jogador_id] = atual + dt
                else:
                    # Reseta se saiu do alcance
                    self.tempos_resgate[cid][nave.jogador_id] = 0.0

                # Resgate completo
                if self.tempos_resgate[cid].get(nave.jogador_id, 0.0) >= C.DURACAO_RESGATE:
                    self._executar_resgate(carcaca, nave)
                    break

            # Atualiza barra visual de progresso da carcaça
            if cid in self.tempos_resgate and self.tempos_resgate[cid]:
                maximo = max(self.tempos_resgate[cid].values())
                carcaca.progresso = min(1.0, maximo / C.DURACAO_RESGATE)

    def _executar_resgate(self, carcaca: Carcaca, resgatador: Nave):
        # Revive o jogador com 1 vida na posição da carcaça
        nave_resgatada = self.naves[carcaca.jogador_id]
        nave_resgatada.vidas = 1
        nave_resgatada.ativa = True
        nave_resgatada.pos = Vec(carcaca.pos)
        nave_resgatada.vel = Vec(0, 0)
        nave_resgatada.angulo = -90.0
        nave_resgatada.invuln = C.TEMPO_SEGURO

        # Regatador ganha bônus de pontos pelo salvamento
        resgatador.pontos += 500

        cid = id(carcaca)
        self.tempos_resgate.pop(cid, None)
        carcaca.kill()

    # --- desenho ---

    def draw(self, surf: pg.Surface, font_pequena: pg.font.Font):
        for ast in self.asteroides:
            ast.draw(surf)

        for ovni in self.ovnis:
            ovni.draw(surf)

        for bala in self.balas_ovni:
            bala.draw(surf)

        for i, grupo in enumerate(self.balas):
            cor = C.CORES_JOGADORES[i]
            for bala in grupo:
                bala.draw(surf, cor)

        for carcaca in self.carcacas:
            carcaca.draw(surf)

        for nave in self.naves:
            nave.draw(surf)
            if nave.ativa:
                # Rótulo do jogador acima da nave
                label = font_pequena.render(f"J{nave.jogador_id + 1}", True, nave.cor)
                surf.blit(label, (int(nave.pos.x) - 8, int(nave.pos.y) - nave.r - 16))
