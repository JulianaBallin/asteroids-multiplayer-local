import sys
import pygame as pg
import config as C
from config import Modo
from systems import Mundo
from utils import txt

# Cada entrada: (nome exibido, constante, min_jogadores, max_jogadores, descrição)
MODOS = [
    ("Solo",            Modo.SOLO,              1, 1,
     "1 jogador vs asteroides — modo classico"),
    ("Cooperativo",     Modo.COOPERATIVO,       2, 4,
     "Todos contra os asteroides — resgate entre aliados ativo"),
    ("Duelo",           Modo.DUELO,             2, 2,
     "1 vs 1 — fogo amigo ativo — sem resgate"),
    ("Todos vs Todos",  Modo.TODOS_CONTRA_TODOS, 2, 4,
     "Cada um por si — fogo amigo ativo — sem resgate"),
    ("Equipes 2v2",     Modo.EQUIPES,           4, 4,
     "J1+J2 vs J3+J4 — resgate somente dentro da equipe"),
]


class Jogo:
    def __init__(self):
        pg.init()
        self.tela = pg.display.set_mode((C.LARGURA, C.ALTURA))
        pg.display.set_caption("Asteroids Multiplayer Local")
        self.relogio = pg.time.Clock()

        self.font        = pg.font.SysFont("consolas", 18)
        self.font_grande = pg.font.SysFont("consolas", 46)
        self.font_media  = pg.font.SysFont("consolas", 22)
        self.font_pequena = pg.font.SysFont("consolas", 11)

        self.cena = "menu"
        self.mundo: Mundo | None = None
        self.modo_idx = 1      # começa em Cooperativo
        self.num_jogadores = 2
        self.fade_fim = 0.0

    # --- helpers ---

    def _modo_atual(self):
        return MODOS[self.modo_idx]

    def _ajustar_jogadores(self):
        _, _, min_j, max_j, _ = self._modo_atual()
        self.num_jogadores = max(min_j, min(max_j, self.num_jogadores))

    # --- loop ---

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
            # Navega entre modos com as setas esquerda/direita
            elif e.key == pg.K_LEFT:
                self.modo_idx = (self.modo_idx - 1) % len(MODOS)
                self._ajustar_jogadores()
            elif e.key == pg.K_RIGHT:
                self.modo_idx = (self.modo_idx + 1) % len(MODOS)
                self._ajustar_jogadores()
            # Ajusta número de jogadores (apenas nos modos com variação)
            elif e.key in (pg.K_2, pg.K_3, pg.K_4):
                n = {pg.K_2: 2, pg.K_3: 3, pg.K_4: 4}[e.key]
                _, _, min_j, max_j, _ = self._modo_atual()
                if min_j <= n <= max_j:
                    self.num_jogadores = n
            elif e.key in (pg.K_RETURN, pg.K_SPACE):
                self._iniciar_jogo()

        elif self.cena == "jogando":
            if e.key == pg.K_ESCAPE:
                self.cena = "menu"
            # Hiperspace é ação pontual (evento de tecla, não tecla mantida)
            for i in range(self.num_jogadores):
                if e.key == C.CONTROLES[i]['hiper']:
                    self.mundo.hiperspace(i)

        elif self.cena == "placar":
            if e.key == pg.K_ESCAPE:
                self.cena = "menu"
            elif e.key in (pg.K_RETURN, pg.K_SPACE):
                self._iniciar_jogo()

    def _iniciar_jogo(self):
        _, modo, _, _, _ = self._modo_atual()
        self.mundo = Mundo(self.num_jogadores, modo)
        self.cena = "jogando"

    # --- tela: menu ---

    def _desenhar_menu(self):
        cx = C.LARGURA // 2
        nome, modo, min_j, max_j, desc = self._modo_atual()

        # Cabeçalho
        txt(self.tela, self.font_grande, "ASTEROIDS", cx - 145, 88)
        txt(self.tela, self.font_media, "MULTIPLAYER LOCAL", cx - 105, 146, C.CINZA_CLARO)
        pg.draw.line(self.tela, C.CINZA, (cx - 290, 176), (cx + 290, 176))

        # Seleção de modo
        txt(self.tela, self.font_pequena, "< MODO >", cx - 30, 184, C.CINZA_CLARO)

        nome_w = self.font_media.size(nome)[0]
        cor_modo = C.CORES_JOGADORES[self.modo_idx % 4]
        txt(self.tela, self.font_media, nome, cx - nome_w // 2, 200, cor_modo)

        desc_w = self.font_pequena.size(desc)[0]
        txt(self.tela, self.font_pequena, desc, cx - desc_w // 2, 228, C.CINZA_CLARO)

        # Seleção de número de jogadores (só aparece em modos com variação)
        if min_j != max_j:
            txt(self.tela, self.font_pequena, "Jogadores:", cx - 140, 256, C.CINZA_CLARO)
            for n in range(min_j, max_j + 1):
                cor = C.BRANCO if n == self.num_jogadores else C.CINZA
                offset = (n - min_j) * 55
                txt(self.tela, self.font_media, f"[{n}]", cx - 30 + offset, 251, cor)
            txt(self.tela, self.font_pequena,
                "Pressione 2, 3 ou 4 para selecionar", cx - 155, 279, C.CINZA)
        else:
            txt(self.tela, self.font_pequena,
                f"Jogadores: {min_j}", cx - 55, 256, C.CINZA_CLARO)

        pg.draw.line(self.tela, C.CINZA, (cx - 290, 298), (cx + 290, 298))

        start_txt = "ENTER ou ESPACO para iniciar"
        txt(self.tela, self.font, start_txt,
            cx - self.font.size(start_txt)[0] // 2, 308)

        # Controles dos jogadores ativos
        pg.draw.line(self.tela, C.CINZA, (cx - 290, 340), (cx + 290, 340))
        txt(self.tela, self.font_pequena, "CONTROLES", cx - 33, 348, C.CINZA_CLARO)

        linhas_ctrl = [
            ("J1: W/A/D   | Fogo: LSHIFT  | Hiper: Q",        C.CORES_JOGADORES[0]),
            ("J2: Setas   | Fogo: RSHIFT  | Hiper: P",        C.CORES_JOGADORES[1]),
            ("J3: I/J/L   | Fogo: H       | Hiper: Y",        C.CORES_JOGADORES[2]),
            ("J4: Num8/4/6 | Fogo: Num0   | Hiper: NumEnter", C.CORES_JOGADORES[3]),
        ]
        for i in range(min(self.num_jogadores, 4)):
            linha, cor = linhas_ctrl[i]
            if modo == Modo.EQUIPES:
                eq = "A" if i < 2 else "B"
                linha = f"[Eq.{eq}] {linha}"
            txt(self.tela, self.font_pequena, linha, cx - 220, 364 + i * 16, cor)

        # Nota sobre resgate (só nos modos que o suportam)
        if modo in (Modo.COOPERATIVO, Modo.EQUIPES):
            pg.draw.line(self.tela, C.CINZA, (cx - 290, 436), (cx + 290, 436))
            nota = "RESGATE: fique proximo da carcaca de um aliado por 3s para revive-lo (+500 pts)"
            txt(self.tela, self.font_pequena, nota, cx - 235, 444, C.COR_RESGATE)

        txt(self.tela, self.font_pequena, "Seta esq/dir: mudar modo   ESC: sair",
            cx - 140, 508, C.CINZA)

    # --- tela: hud durante o jogo ---

    def _desenhar_hud(self):
        w_secao = C.LARGURA // self.num_jogadores

        for i in range(self.num_jogadores):
            nave = self.mundo.naves[i]
            cor = C.CORES_JOGADORES[i]
            x = i * w_secao + 8

            if i > 0:
                pg.draw.line(self.tela, C.CINZA,
                             (i * w_secao, 0), (i * w_secao, 46))

            # Indicador de equipe no modo equipes
            prefixo = ""
            if self.mundo.modo == Modo.EQUIPES:
                prefixo = "[A] " if i < 2 else "[B] "

            if not nave.ativa:
                # Verifica se há carcaça aguardando resgate (só nos modos com resgate)
                tem_carcaca = (
                    self.mundo.modo in (Modo.COOPERATIVO, Modo.EQUIPES) and
                    any(c.jogador_id == i for c in self.mundo.carcacas)
                )
                status = "AGUARDANDO..." if tem_carcaca else "ELIMINADO"
                txt(self.tela, self.font_pequena, f"{prefixo}J{i + 1}", x, 5, cor)
                txt(self.tela, self.font_pequena, status, x, 18, C.CINZA_CLARO)
            else:
                vidas_str = "♥" * nave.vidas + "♡" * (C.VIDAS_INICIAIS - nave.vidas)
                txt(self.tela, self.font_pequena, f"{prefixo}J{i + 1}", x, 5, cor)
                txt(self.tela, self.font_pequena, vidas_str, x, 18, cor)
                txt(self.tela, self.font_pequena, f"{nave.pontos:06d}", x, 31, cor)

        txt(self.tela, self.font_pequena,
            f"Onda {self.mundo.onda}", C.LARGURA // 2 - 26, 5, C.CINZA_CLARO)
        pg.draw.line(self.tela, C.CINZA, (0, 48), (C.LARGURA, 48))

    # --- tela: placar final ---

    def _desenhar_placar(self):
        alpha = min(255, int(255 * self.fade_fim / C.DURACAO_FADE))
        overlay = pg.Surface((C.LARGURA, C.ALTURA), pg.SRCALPHA)
        overlay.fill((0, 0, 0, alpha))
        self.tela.blit(overlay, (0, 0))

        if alpha < 60:
            return

        cx = C.LARGURA // 2
        msg = self.mundo.msg_vitoria

        if msg:
            # Colorir a mensagem pelo vencedor
            cor_msg = C.BRANCO
            for i in range(4):
                if f"JOGADOR {i + 1}" in msg:
                    cor_msg = C.CORES_JOGADORES[i]
            if "EQUIPE A" in msg:
                cor_msg = C.CORES_JOGADORES[0]
            elif "EQUIPE B" in msg:
                cor_msg = C.CORES_JOGADORES[2]
            msg_w = self.font_grande.size(msg)[0]
            txt(self.tela, self.font_grande, msg, cx - msg_w // 2, 120, cor_msg)
        else:
            txt(self.tela, self.font_grande, "FIM DE JOGO", cx - 170, 120)

        # Ranking por pontos
        ranking = sorted(self.mundo.naves, key=lambda n: n.pontos, reverse=True)
        medalhas = ["1°", "2°", "3°", "4°"]
        txt(self.tela, self.font_pequena, "PLACAR FINAL", cx - 42, 215, C.CINZA_CLARO)
        pg.draw.line(self.tela, C.CINZA, (cx - 185, 228), (cx + 185, 228))

        for j, nave in enumerate(ranking):
            cor = C.CORES_JOGADORES[nave.jogador_id]
            # Indica equipe no modo equipes
            sufixo = ""
            if self.mundo.modo == Modo.EQUIPES:
                sufixo = "  [Eq.A]" if nave.jogador_id < 2 else "  [Eq.B]"
            txt(self.tela, self.font_media,
                f"{medalhas[j]}  J{nave.jogador_id + 1}   {nave.pontos:06d} pts{sufixo}",
                cx - 155, 242 + j * 48, cor)

        pg.draw.line(self.tela, C.CINZA, (cx - 185, 440), (cx + 185, 440))
        txt(self.tela, self.font, "ENTER: jogar novamente   ESC: menu",
            cx - 175, 452)
