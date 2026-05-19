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

        self.font = pg.font.SysFont("consolas", 22)
        self.font_grande = pg.font.SysFont("consolas", 60)
        self.font_media = pg.font.SysFont("consolas", 28)
        self.font_pequena = pg.font.SysFont("consolas", 15)

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

        titulo = "ASTEROIDS"
        txt(self.tela, self.font_grande, titulo, cx - self.font_grande.size(titulo)[0] // 2, 90)
        sub = "MULTIPLAYER LOCAL"
        txt(self.tela, self.font_media, sub, cx - self.font_media.size(sub)[0] // 2, 164, C.CINZA_CLARO)
        pg.draw.line(self.tela, C.CINZA, (cx - 360, 206), (cx + 360, 206))

        modo_label = "< MODO >"
        txt(self.tela, self.font_pequena, modo_label, cx - self.font_pequena.size(modo_label)[0] // 2, 218, C.CINZA_CLARO)
        cor_modo = C.CORES_JOGADORES[self.modo_idx % 4]
        txt(self.tela, self.font_media, nome, cx - self.font_media.size(nome)[0] // 2, 236, cor_modo)
        txt(self.tela, self.font_pequena, desc, cx - self.font_pequena.size(desc)[0] // 2, 274, C.CINZA_CLARO)

        if min_j != max_j:
            jog_label = "Jogadores:"
            txt(self.tela, self.font_pequena, jog_label, cx - self.font_pequena.size(jog_label)[0] // 2 - 80, 310, C.CINZA_CLARO)
            for n in range(min_j, max_j + 1):
                cor = C.BRANCO if n == self.num_jogadores else C.CINZA
                offset = (n - min_j) * 66
                txt(self.tela, self.font_media, f"[{n}]", cx - 40 + offset, 305, cor)
            sel_txt = "Pressione 2, 3 ou 4 para selecionar"
            txt(self.tela, self.font_pequena, sel_txt, cx - self.font_pequena.size(sel_txt)[0] // 2, 344, C.CINZA)
        else:
            jog_txt = f"Jogadores: {min_j}"
            txt(self.tela, self.font_pequena, jog_txt, cx - self.font_pequena.size(jog_txt)[0] // 2, 310, C.CINZA_CLARO)

        pg.draw.line(self.tela, C.CINZA, (cx - 360, 368), (cx + 360, 368))

        start_txt = "ENTER ou ESPACO para iniciar"
        txt(self.tela, self.font, start_txt, cx - self.font.size(start_txt)[0] // 2, 384)
        setas_txt = "Setas ou direcional do controle mudam modo e jogadores"
        txt(self.tela, self.font_pequena, setas_txt, cx - self.font_pequena.size(setas_txt)[0] // 2, 416, C.CINZA_CLARO)
        esc_txt = "ESC ou BACK sai e volta ao menu"
        txt(self.tela, self.font_pequena, esc_txt, cx - self.font_pequena.size(esc_txt)[0] // 2, 438, C.CINZA_CLARO)

        self._desenhar_controles(cx)
        self._desenhar_mecanicas(cx)
        self._desenhar_status_controles(cx)

    def _desenhar_controles(self, cx: int):
        y = 468
        header = "CONTROLES"
        txt(self.tela, self.font_pequena, header, cx - self.font_pequena.size(header)[0] // 2, y, C.CINZA_CLARO)
        linhas = [
            "J1: J/L giram | I acelera | H atira | Y EMP | U Fenda",
            "J2: Num4/Num6 giram | Num8 acelera | Num0 atira | Enter EMP | Num9 Fenda",
            "J3: A/D giram | W acelera | LSHIFT atira | Q EMP | E Fenda",
            "J4: seta esq/dir giram | seta cima acelera | RSHIFT atira | P EMP | O Fenda",
        ]
        for i, linha in enumerate(linhas):
            txt(self.tela, self.font_pequena, linha, cx - self.font_pequena.size(linha)[0] // 2, y + 22 + i * 20, C.CINZA_CLARO)

    def _desenhar_mecanicas(self, cx: int):
        y = 572
        header = "MECANICAS"
        txt(self.tela, self.font_pequena, header, cx - self.font_pequena.size(header)[0] // 2, y, C.CINZA_CLARO)
        linhas = [
            "PULSAR EMP: empurra asteroides, trava inimigos e neutraliza OVNIs",
            "RESGATE: em coop/equipes, fique perto da carcaca aliada para reviver",
            "FENDA GRAVITACIONAL: dash rapido que rasga o espaco e destroe projeteis",
        ]
        for i, linha in enumerate(linhas):
            txt(self.tela, self.font_pequena, linha, cx - self.font_pequena.size(linha)[0] // 2, y + 22 + i * 20, C.CINZA_CLARO)

    def _desenhar_status_controles(self, cx: int):
        nomes = self.input_manager.joysticks_conectados()
        y = 658
        if nomes:
            header = "Controles detectados:"
            txt(self.tela, self.font_pequena, header, cx - self.font_pequena.size(header)[0] // 2, y, C.CINZA_CLARO)
            for i, nome in enumerate(nomes[:C.MAX_JOGADORES]):
                cor = C.CORES_JOGADORES[i]
                joy_txt = f"J{i + 1}: {nome}"
                txt(self.tela, self.font_pequena, joy_txt, cx - self.font_pequena.size(joy_txt)[0] // 2, y + 20 + i * 18, cor)
        else:
            aviso = "Nenhum controle detectado, usando teclado"
            txt(self.tela, self.font_pequena, aviso, cx - self.font_pequena.size(aviso)[0] // 2, y, C.CINZA_CLARO)

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
            y += 20

        onda_txt = f"Onda: {self.mundo.onda}"
        txt(self.tela, self.font_pequena, onda_txt, C.LARGURA - self.font_pequena.size(onda_txt)[0] - 12, 10, C.CINZA_CLARO)

        minutos = int(self.mundo.tempo_restante // 60)
        segundos = int(self.mundo.tempo_restante % 60)
        tempo_str = f"{minutos:02d}:{segundos:02d}"
        cor_tempo = (255, 80, 80) if self.mundo.tempo_restante <= 30 else C.BRANCO
        txt(self.tela, self.font_media, tempo_str, C.LARGURA // 2 - self.font_media.size(tempo_str)[0] // 2, 8, cor_tempo)

    def _desenhar_placar(self):
        if self.mundo is None:
            return

        cx = C.LARGURA // 2
        fim_txt = "FIM DE JOGO"
        txt(self.tela, self.font_grande, fim_txt, cx - self.font_grande.size(fim_txt)[0] // 2, 130)

        if self.mundo.msg_vitoria:
            w = self.font_media.size(self.mundo.msg_vitoria)[0]
            txt(self.tela, self.font_media, self.mundo.msg_vitoria, cx - w // 2, 210, C.CINZA_CLARO)

        ordenados = sorted(self.mundo.naves, key=lambda n: n.pontos, reverse=True)
        y = 280
        for nave in ordenados:
            linha = f"J{nave.jogador_id + 1}: {nave.pontos} pontos"
            txt(self.tela, self.font_media, linha, cx - self.font_media.size(linha)[0] // 2, y, nave.cor)
            y += 42

        novo_txt = "ENTER ou START para jogar novamente"
        txt(self.tela, self.font, novo_txt, cx - self.font.size(novo_txt)[0] // 2, 560)
        menu_txt = "ESC ou BACK para voltar ao menu"
        txt(self.tela, self.font, menu_txt, cx - self.font.size(menu_txt)[0] // 2, 598, C.CINZA_CLARO)
