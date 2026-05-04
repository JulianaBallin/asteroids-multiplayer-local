import sys
import pygame as pg
import config as C
from systems import Mundo
from utils import txt


class Jogo:
    def __init__(self):
        pg.init()
        self.tela = pg.display.set_mode((C.LARGURA, C.ALTURA))
        pg.display.set_caption("Asteroids Multiplayer Local")
        self.relogio = pg.time.Clock()

        # Fontes em tamanhos diferentes para o HUD e menus
        self.font = pg.font.SysFont("consolas", 18)
        self.font_grande = pg.font.SysFont("consolas", 46)
        self.font_media = pg.font.SysFont("consolas", 22)
        self.font_pequena = pg.font.SysFont("consolas", 11)

        self.cena = "menu"
        self.mundo: Mundo | None = None
        self.num_jogadores = 2
        self.fade_fim = 0.0

    def run(self):
        while True:
            dt = self.relogio.tick(C.FPS) / 1000.0

            for e in pg.event.get():
                if e.type == pg.QUIT:
                    pg.quit()
                    sys.exit()
                self._processar_evento(e)

            teclas = pg.key.get_pressed()
            self.tela.fill(C.PRETO)

            if self.cena == "menu":
                self._desenhar_menu()
            elif self.cena == "jogando":
                self.mundo.update(dt, teclas)
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
        if e.type != pg.KEYDOWN:
            return

        if self.cena == "menu":
            if e.key == pg.K_ESCAPE:
                pg.quit()
                sys.exit()
            elif e.key == pg.K_2:
                self.num_jogadores = 2
            elif e.key == pg.K_3:
                self.num_jogadores = 3
            elif e.key == pg.K_4:
                self.num_jogadores = 4
            elif e.key in (pg.K_RETURN, pg.K_SPACE):
                self._iniciar_jogo()

        elif self.cena == "jogando":
            if e.key == pg.K_ESCAPE:
                self.cena = "menu"
            # Hiperspace é ação pontual — usa evento de tecla pressionada
            for i in range(self.num_jogadores):
                if e.key == C.CONTROLES[i]['hiper']:
                    self.mundo.hiperspace(i)

        elif self.cena == "placar":
            if e.key == pg.K_ESCAPE:
                self.cena = "menu"
            elif e.key in (pg.K_RETURN, pg.K_SPACE):
                self._iniciar_jogo()

    def _iniciar_jogo(self):
        self.mundo = Mundo(self.num_jogadores)
        self.cena = "jogando"

    # --- telas ---

    def _desenhar_menu(self):
        cx = C.LARGURA // 2

        # Título
        txt(self.tela, self.font_grande, "ASTEROIDS", cx - 145, 100)
        txt(self.tela, self.font_media, "MULTIPLAYER LOCAL", cx - 105, 158, C.CINZA_CLARO)

        # Seleção de número de jogadores
        txt(self.tela, self.font, "Número de jogadores:", cx - 105, 220)
        for n in [2, 3, 4]:
            cor = C.CORES_JOGADORES[n - 2] if n == self.num_jogadores else C.CINZA_CLARO
            txt(self.tela, self.font_media, f"[{n}]", cx - 45 + (n - 2) * 60, 248, cor)
        txt(self.tela, self.font_pequena, "Pressione 2, 3 ou 4 para selecionar", cx - 150, 278, C.CINZA)

        txt(self.tela, self.font, "ENTER ou ESPACO para iniciar", cx - 155, 315)

        # Tabela de controles
        pg.draw.line(self.tela, C.CINZA, (cx - 250, 355), (cx + 250, 355))
        txt(self.tela, self.font_pequena, "CONTROLES", cx - 35, 362, C.CINZA_CLARO)

        linhas_ctrl = [
            ("J1: W/A/D  |  Fogo: LSHIFT  |  Hiper: Q", C.CORES_JOGADORES[0]),
            ("J2: Setas  |  Fogo: RSHIFT  |  Hiper: P", C.CORES_JOGADORES[1]),
            ("J3: I/J/L  |  Fogo: H       |  Hiper: Y", C.CORES_JOGADORES[2]),
            ("J4: Num8/4/6 | Fogo: Num0  |  Hiper: NumEnter", C.CORES_JOGADORES[3]),
        ]
        for i, (linha, cor) in enumerate(linhas_ctrl):
            txt(self.tela, self.font_pequena, linha, cx - 215, 378 + i * 16, cor)

        # Dica da mecânica de resgate
        pg.draw.line(self.tela, C.CINZA, (cx - 250, 450), (cx + 250, 450))
        txt(self.tela, self.font_pequena,
            "RESGATE: fique próximo da carcaça de um aliado por 3s para revivê-lo (+500 pts)",
            cx - 240, 458, C.COR_RESGATE)

        txt(self.tela, self.font_pequena, "ESC: sair", cx - 25, 510, C.CINZA)

    def _desenhar_hud(self):
        # Divide o topo da tela em seções iguais para cada jogador
        w_secao = C.LARGURA // self.num_jogadores

        for i in range(self.num_jogadores):
            nave = self.mundo.naves[i]
            cor = C.CORES_JOGADORES[i]
            x = i * w_secao + 8

            # Separador vertical entre seções
            if i > 0:
                pg.draw.line(self.tela, C.CINZA,
                             (i * w_secao, 0), (i * w_secao, 46))

            if not nave.ativa:
                # Verifica se há carcaça aguardando resgate
                carcaca_ativa = any(
                    c.jogador_id == i for c in self.mundo.carcacas
                )
                status = "AGUARDANDO..." if carcaca_ativa else "ELIMINADO"
                txt(self.tela, self.font_pequena, f"J{i + 1}", x, 5, cor)
                txt(self.tela, self.font_pequena, status, x, 18, C.CINZA_CLARO)
            else:
                vidas_str = "♥" * nave.vidas + "♡" * (C.VIDAS_INICIAIS - nave.vidas)
                txt(self.tela, self.font_pequena, f"J{i + 1}", x, 5, cor)
                txt(self.tela, self.font_pequena, vidas_str, x, 18, cor)
                txt(self.tela, self.font_pequena, f"{nave.pontos:06d}", x, 31, cor)

        # Onda atual no centro do HUD
        txt(self.tela, self.font_pequena,
            f"Onda {self.mundo.onda}", C.LARGURA // 2 - 26, 5, C.CINZA_CLARO)

        # Linha separadora entre HUD e área de jogo
        pg.draw.line(self.tela, C.CINZA, (0, 48), (C.LARGURA, 48))

    def _desenhar_placar(self):
        # Fundo escurecendo com fade
        alpha = min(255, int(255 * self.fade_fim / C.DURACAO_FADE))
        overlay = pg.Surface((C.LARGURA, C.ALTURA), pg.SRCALPHA)
        overlay.fill((0, 0, 0, alpha))
        self.tela.blit(overlay, (0, 0))

        if alpha < 60:
            return

        cx = C.LARGURA // 2
        txt(self.tela, self.font_grande, "FIM DE JOGO", cx - 170, 130)

        # Ranking por pontuação
        ranking = sorted(self.mundo.naves, key=lambda n: n.pontos, reverse=True)
        medalhas = ["1°", "2°", "3°", "4°"]

        txt(self.tela, self.font_pequena, "PLACAR FINAL", cx - 42, 220, C.CINZA_CLARO)
        pg.draw.line(self.tela, C.CINZA, (cx - 180, 232), (cx + 180, 232))

        for j, nave in enumerate(ranking):
            cor = C.CORES_JOGADORES[nave.jogador_id]
            y = 245 + j * 52
            txt(self.tela, self.font_media,
                f"{medalhas[j]}  Jogador {nave.jogador_id + 1}   {nave.pontos:06d} pts",
                cx - 155, y, cor)

        pg.draw.line(self.tela, C.CINZA, (cx - 180, 460), (cx + 180, 460))
        txt(self.tela, self.font, "ENTER: jogar novamente   ESC: menu", cx - 185, 472)
