import sys

import pygame as pg

import config as C
from config import Modo
from input import InputManager
from systems import Mundo
from utils import txt


# Cada entrada: (nome exibido, constante, min_jogadores, max_jogadores, descrição)
MODOS = [
    ("Solo", Modo.SOLO, 1, 1, "1 jogador vs asteroides — modo classico"),
    ("Cooperativo", Modo.COOPERATIVO, 2, 4, "Todos contra os asteroides — resgate entre aliados ativo"),
    ("Duelo", Modo.DUELO, 2, 2, "1 vs 1 — fogo amigo ativo — sem resgate"),
    ("Todos vs Todos", Modo.TODOS_CONTRA_TODOS, 2, 4, "Cada um por si — fogo amigo ativo — sem resgate"),
    ("Equipes 2v2", Modo.EQUIPES, 4, 4, "J1+J2 vs J3+J4 — resgate somente dentro da equipe"),
]


class Jogo:
    def __init__(self):
        pg.init()
        pg.joystick.init()

        self.tela = pg.display.set_mode((C.LARGURA, C.ALTURA))
        pg.display.set_caption("Asteroids Multiplayer Local")
        self.relogio = pg.time.Clock()

        self.font = pg.font.SysFont("consolas", 18)
        self.font_grande = pg.font.SysFont("consolas", 46)
        self.font_media = pg.font.SysFont("consolas", 22)
        self.font_pequena = pg.font.SysFont("consolas", 11)

        self.cena = "menu"
        self.mundo: Mundo | None = None
        self.modo_idx = 1
        self.num_jogadores = 2
        self.fade_fim = 0.0

        self.input_manager = InputManager()
        self.entradas_atuais = []
        self.teste_dispositivo = [
            {"mov": False, "tiro": False, "emp": False} for _ in range(C.MAX_JOGADORES)
        ]

    # --- helpers ---
    def _modo_atual(self):
        return MODOS[self.modo_idx]

    def _ajustar_jogadores(self):
        _, _, min_j, max_j, _ = self._modo_atual()
        self.num_jogadores = max(min_j, min(max_j, self.num_jogadores))

    def _botao_back_evento(self, e: pg.event.Event) -> bool:
        if not hasattr(e, "instance_id"):
            return e.button == C.JOY_BTN_BACK
        return self.input_manager.botao_back(e.instance_id, e.button)

    def _botao_start_evento(self, e: pg.event.Event) -> bool:
        if not hasattr(e, "instance_id"):
            return e.button in (C.JOY_BTN_START, C.JOY_BTN_SHOOT, C.JOY_BTN_SHOOT_ALT)
        return self.input_manager.botao_start(e.instance_id, e.button)

    # --- loop ---
    def run(self):
        while True:
            dt = self.relogio.tick(C.FPS) / 1000.0

            for e in pg.event.get():
                if e.type == pg.QUIT:
                    pg.quit()
                    sys.exit()
                self._processar_evento(e)

            self.input_manager.update()
            entradas = self.input_manager.inputs_por_jogador(self.num_jogadores)
            self.entradas_atuais = entradas

            for i, e_in in enumerate(entradas):
                t = self.teste_dispositivo[i]
                t["mov"] = t["mov"] or e_in.rotate_left or e_in.rotate_right or e_in.thrust
                t["tiro"] = t["tiro"] or e_in.shoot
                t["emp"] = t["emp"] or e_in.emp_pressed

            self.tela.fill(C.PRETO)

            if self.cena == "menu":
                self._desenhar_menu()
            elif self.cena == "jogando":
                if self.mundo is not None:
                    self.mundo.update(dt, entradas)
                    self.mundo.draw(self.tela, self.font_pequena)
                    self._desenhar_hud()
                    if self.mundo.fim_de_jogo:
                        self.fade_fim = 0.0
                        self.cena = "placar"
            elif self.cena == "placar":
                self.fade_fim += dt
                self._desenhar_placar()

            pg.display.flip()

    def _processar_evento(self, e: pg.event.Event):
        if e.type in (pg.JOYDEVICEADDED, pg.JOYDEVICEREMOVED):
            self.input_manager.marcar_scan_joystick()
            return
        if e.type not in (pg.KEYDOWN, pg.JOYBUTTONDOWN, pg.JOYHATMOTION):
            return

        if self.cena == "menu":
            if e.type == pg.KEYDOWN:
                if e.key == pg.K_ESCAPE:
                    pg.quit()
                    sys.exit()
                elif e.key == pg.K_LEFT:
                    self.modo_idx = (self.modo_idx - 1) % len(MODOS)
                    self._ajustar_jogadores()
                elif e.key == pg.K_RIGHT:
                    self.modo_idx = (self.modo_idx + 1) % len(MODOS)
                    self._ajustar_jogadores()
                elif e.key in (pg.K_2, pg.K_3, pg.K_4):
                    n = {pg.K_2: 2, pg.K_3: 3, pg.K_4: 4}[e.key]
                    _, _, min_j, max_j, _ = self._modo_atual()
                    if min_j <= n <= max_j:
                        self.num_jogadores = n
                elif e.key in (pg.K_RETURN, pg.K_SPACE):
                    self._iniciar_jogo()

            elif e.type == pg.JOYHATMOTION:
                if e.hat != 0:
                    return
                if e.value[0] == -1:
                    self.modo_idx = (self.modo_idx - 1) % len(MODOS)
                    self._ajustar_jogadores()
                elif e.value[0] == 1:
                    self.modo_idx = (self.modo_idx + 1) % len(MODOS)
                    self._ajustar_jogadores()
                elif e.value[1] == 1:
                    _, _, _, max_j, _ = self._modo_atual()
                    self.num_jogadores = min(max_j, self.num_jogadores + 1)
                elif e.value[1] == -1:
                    _, _, min_j, _, _ = self._modo_atual()
                    self.num_jogadores = max(min_j, self.num_jogadores - 1)

            elif e.type == pg.JOYBUTTONDOWN:
                if self._botao_back_evento(e):
                    pg.quit()
                    sys.exit()
                if self._botao_start_evento(e):
                    self._iniciar_jogo()

        elif self.cena == "jogando":
            if e.type == pg.KEYDOWN and e.key == pg.K_ESCAPE:
                self.cena = "menu"
            elif e.type == pg.JOYBUTTONDOWN and self._botao_back_evento(e):
                self.cena = "menu"

        elif self.cena == "placar":
            if e.type == pg.KEYDOWN:
                if e.key == pg.K_ESCAPE:
                    self.cena = "menu"
                elif e.key in (pg.K_RETURN, pg.K_SPACE):
                    self._iniciar_jogo()
            elif e.type == pg.JOYBUTTONDOWN:
                if self._botao_back_evento(e):
                    self.cena = "menu"
                elif self._botao_start_evento(e):
                    self._iniciar_jogo()

    def _iniciar_jogo(self):
        _, modo, _, _, _ = self._modo_atual()
        self.mundo = Mundo(self.num_jogadores, modo)
        self.cena = "jogando"

    # --- tela: menu ---
    def _desenhar_menu(self):
        cx = C.LARGURA // 2
        nome, _, min_j, max_j, desc = self._modo_atual()

        txt(self.tela, self.font_grande, "ASTEROIDS", cx - 145, 88)
        txt(self.tela, self.font_media, "MULTIPLAYER LOCAL", cx - 105, 146, C.CINZA_CLARO)
        pg.draw.line(self.tela, C.CINZA, (cx - 290, 176), (cx + 290, 176))

        txt(self.tela, self.font_pequena, "< MODO >", cx - 30, 184, C.CINZA_CLARO)
        nome_w = self.font_media.size(nome)[0]
        cor_modo = C.CORES_JOGADORES[self.modo_idx % 4]
        txt(self.tela, self.font_media, nome, cx - nome_w // 2, 200, cor_modo)
        desc_w = self.font_pequena.size(desc)[0]
        txt(self.tela, self.font_pequena, desc, cx - desc_w // 2, 228, C.CINZA_CLARO)

        if min_j != max_j:
            txt(self.tela, self.font_pequena, "Jogadores:", cx - 140, 256, C.CINZA_CLARO)
            for n in range(min_j, max_j + 1):
                cor = C.BRANCO if n == self.num_jogadores else C.CINZA
                offset = (n - min_j) * 55
                txt(self.tela, self.font_media, f"[{n}]", cx - 30 + offset, 251, cor)
            txt(self.tela, self.font_pequena, "Pressione 2, 3 ou 4 para selecionar", cx - 155, 279, C.CINZA)
        else:
            txt(self.tela, self.font_pequena, f"Jogadores: {min_j}", cx - 55, 256, C.CINZA_CLARO)

        pg.draw.line(self.tela, C.CINZA, (cx - 290, 298), (cx + 290, 298))

        start_txt = "ENTER ou ESPACO para iniciar"
        txt(self.tela, self.font, start_txt, cx - self.font.size(start_txt)[0] // 2, 308)
        txt(self.tela, self.font_pequena, "Setas ou direcional do controle mudam modo/jogadores", cx - 190, 335, C.CINZA_CLARO)
        txt(self.tela, self.font_pequena, "ESC ou BACK sai / volta ao menu", cx - 118, 354, C.CINZA_CLARO)

        self._desenhar_controles(cx)
        self._desenhar_mecanicas(cx)
        self._desenhar_status_controles(cx)

    def _desenhar_controles(self, cx: int):
        y = 392
        txt(self.tela, self.font_pequena, "CONTROLES", cx - 38, y, C.CINZA_CLARO)
        linhas = [
            "J1: J/L giram | I acelera | H atira | Y EMP | U Fenda",
            "J2: Num4/Num6 giram | Num8 acelera | Num0 atira | Enter EMP | Num9 Fenda",
            "J3: A/D giram | W acelera | LSHIFT atira | Q EMP | E Fenda",
            "J4: ←/→ giram | ↑ acelera | RSHIFT atira | P EMP | O Fenda",
        ]
        for i, linha in enumerate(linhas):
            txt(self.tela, self.font_pequena, linha, cx - 250, y + 24 + i * 18, C.CINZA_CLARO)

    def _desenhar_mecanicas(self, cx: int):
        y = 505
        txt(self.tela, self.font_pequena, "MECANICAS", cx - 42, y, C.CINZA_CLARO)
        linhas = [
            "PULSAR EMP: empurra asteroides, protege aliados e trava inimigos",
            "RESGATE: em coop/equipes, fique perto da carcaca aliada para reviver",
            "FENDA GRAVITACIONAL: use o botão próprio para dar dash e rasgar o espaco",
        ]
        for i, linha in enumerate(linhas):
            txt(self.tela, self.font_pequena, linha, cx - 285, y + 24 + i * 18, C.CINZA_CLARO)

    def _desenhar_status_controles(self, cx: int):
        nomes = self.input_manager.joysticks_conectados()
        y = 628
        if nomes:
            txt(self.tela, self.font_pequena, "Controles detectados:", cx - 95, y, C.CINZA_CLARO)
            for i, nome in enumerate(nomes[:C.MAX_JOGADORES]):
                cor = C.CORES_JOGADORES[i]
                txt(self.tela, self.font_pequena, f"J{i + 1}: {nome}", cx - 230, y + 18 + i * 14, cor)
        else:
            txt(self.tela, self.font_pequena, "Nenhum controle detectado — usando teclado", cx - 150, y, C.CINZA_CLARO)

    # --- HUD e placar ---
    def _desenhar_hud(self):
        if self.mundo is None:
            return

        y = 10
        for nave in self.mundo.naves:
            cor = nave.cor
            status = "ON" if nave.ativa else "OFF"
            cd_emp = self.mundo.cooldown_emp[nave.jogador_id]
            cd_fenda = self.mundo.cooldown_fenda[nave.jogador_id]
            linha = (
                f"J{nave.jogador_id + 1} {status} | vidas: {nave.vidas} | "
                f"pts: {nave.pontos} | EMP: {cd_emp:.0f}s | Fenda: {cd_fenda:.0f}s"
            )
            txt(self.tela, self.font_pequena, linha, 12, y, cor)
            y += 16

        txt(self.tela, self.font_pequena, f"Onda: {self.mundo.onda}", C.LARGURA - 100, 12, C.CINZA_CLARO)

    def _desenhar_placar(self):
        if self.mundo is None:
            return

        cx = C.LARGURA // 2
        txt(self.tela, self.font_grande, "FIM DE JOGO", cx - 145, 120)

        if self.mundo.msg_vitoria:
            w = self.font_media.size(self.mundo.msg_vitoria)[0]
            txt(self.tela, self.font_media, self.mundo.msg_vitoria, cx - w // 2, 180, C.CINZA_CLARO)

        ordenados = sorted(self.mundo.naves, key=lambda n: n.pontos, reverse=True)
        y = 250
        for nave in ordenados:
            linha = f"J{nave.jogador_id + 1}: {nave.pontos} pontos"
            txt(self.tela, self.font_media, linha, cx - 105, y, nave.cor)
            y += 34

        txt(self.tela, self.font, "ENTER/START para jogar novamente", cx - 165, 500)
        txt(self.tela, self.font, "ESC/BACK para voltar ao menu", cx - 150, 530, C.CINZA_CLARO)
