<p align="center">
  <img src="docs/diagrams/logo.svg" alt="Asteroids Multiplayer Local" width="420">
</p>

<p align="center">
  Versão multiplayer local do clássico Asteroids para até <strong>4 jogadores simultâneos</strong>,<br>
  com controles Tectoy, HUD por jogador e mecânica inédita de resgate entre aliados.<br>
  <em>Atividade 007 — UEA · Tópicos Especiais para Computação I</em>
</p>

---

<h2 align="center">🎮 Tecnologias Utilizadas</h2>

<p align="center">
  <img alt="Python" src="https://img.shields.io/badge/python-3.11-blue?style=for-the-badge&logo=python&logoColor=white">
  <img alt="Pygame" src="https://img.shields.io/badge/pygame-2.x-green?style=for-the-badge&logo=python&logoColor=white">
  <img alt="C4" src="https://img.shields.io/badge/C4%20Model-Diagramas-9B59B6?style=for-the-badge">
  <img alt="PlantUML" src="https://img.shields.io/badge/PlantUML-Documentação-FBBC04?style=for-the-badge">
</p>

---

<h2 align="center">📝 Descrição do Projeto</h2>

Este projeto é uma versão **multiplayer local** do jogo Asteroids, baseada no repositório original do professor [jucimarjr/asteroids_pygame](https://github.com/jucimarjr/asteroids_pygame).

O objetivo é transformar o jogo singleplayer em uma experiência divertida para **2 a 4 jogadores simultâneos**, com controles mapeados para os controles Tectoy deixados em sala, interface adaptada para múltiplos jogadores e uma nova mecânica cooperativa inédita: o **sistema de resgate**.

---

<h2 align="center">🎯 Funcionalidades Multiplayer</h2>

| Funcionalidade | Descrição |
|---|---|
| **2 a 4 jogadores** | Selecionável no menu inicial |
| **Cores por jogador** | Ciano (J1), Amarelo (J2), Verde (J3), Vermelho (J4) |
| **Placar individual** | Cada jogador acumula pontos separadamente |
| **Vidas individuais** | Cada nave tem 3 vidas independentes |
| **HUD dividido** | Topo da tela dividido em seções por jogador |
| **Placar final** | Ranking por pontos ao fim da partida |
| **OVNI inteligente** | Mira automaticamente na nave viva mais próxima |

---

<h2 align="center">🆕 Mecânica Inédita — Sistema de Resgate</h2>

Quando um jogador perde todas as suas vidas, sua nave vira uma **carcaça piscante** que permanece no mapa por **10 segundos**.

Qualquer jogador vivo pode **resgatar** um aliado eliminado aproximando sua nave da carcaça e permanecendo a menos de **80 pixels** por **3 segundos consecutivos**.

- Uma **barra de progresso verde** aparece acima da carcaça durante o resgate.
- O jogador resgatado é **revivido com 1 vida** na posição da carcaça.
- O jogador que realizou o resgate recebe **+500 pontos de bônus**.
- Se ninguém resgatar a tempo, a carcaça desaparece permanentemente.

Essa mecânica incentiva trabalho em equipe, criando momentos de tensão onde os jogadores precisam equilibrar destruir asteroides e salvar aliados.

---

<h2 align="center">🕹️ Controles (Tectoy)</h2>

| Jogador | Esquerda | Direita | Acelerar | Fogo | Hiperspace |
|---|---|---|---|---|---|
| **J1** | `A` | `D` | `W` | `LSHIFT` | `Q` |
| **J2** | `←` | `→` | `↑` | `RSHIFT` | `P` |
| **J3** | `J` | `L` | `I` | `H` | `Y` |
| **J4** | `Num4` | `Num6` | `Num8` | `Num0` | `NumEnter` |

> **Hiperspace:** teletransporta a nave para posição aleatória, custando 250 pontos.

---

<h2 align="center">📁 Estrutura do Projeto</h2>

```text
asteroids-multiplayer-local/
├── src/
│   ├── main.py        # ponto de entrada
│   ├── config.py      # constantes, cores e controles por jogador
│   ├── game.py        # loop, menus, HUD e placar
│   ├── sprites.py     # entidades: Nave, Bala, Asteroide, OVNI, Carcaca
│   ├── systems.py     # gerenciador do mundo e mecânica de resgate
│   └── utils.py       # funções matemáticas e de desenho
├── docs/
│   └── diagrams/
│       ├── logo.svg
│       ├── c4_nivel1_contexto.puml
│       ├── c4_nivel2_container.puml
│       └── c4_nivel3_componente.puml
├── requirements.txt
└── README.md
```

---

<h2 align="center">▶️ Como Executar</h2>

### 1. Clonar o repositório

```bash
git clone https://github.com/JulianaBallin/asteroids-multiplayer-local.git
cd asteroids-multiplayer-local
```

### 2. Criar ambiente virtual

```bash
python -m venv .venv
source .venv/bin/activate        # Linux/Mac
# .venv\Scripts\activate         # Windows
```

### 3. Instalar dependências

```bash
pip install -r requirements.txt
```

### 4. Iniciar o jogo

```bash
python src/main.py
```

---

<h2 align="center">📦 Dependências</h2>

```txt
pygame>=2.5.0
```

---

<h2 align="center">🗺️ Diagramas C4</h2>

Os diagramas estão na pasta `docs/diagrams/` em formato PlantUML (`.puml`).

Para renderizá-los:
- Use o [PlantUML Online Server](https://www.plantuml.com/plantuml/uml/)
- Ou instale o plugin PlantUML no VS Code

| Arquivo | Nível | Descrição |
|---|---|---|
| `c4_nivel1_contexto.puml` | Nível 1 | Visão geral do sistema e usuários |
| `c4_nivel2_container.puml` | Nível 2 | Containers da aplicação |
| `c4_nivel3_componente.puml` | Nível 3 | Componentes internos da aplicação |

---

<h2 align="center">⚠️ Limitações</h2>

- Suporte apenas a teclado (sem joystick USB nesta versão)
- Até 4 jogadores simultâneos no mesmo teclado
- Jogo reinicia do zero a cada partida (sem salvamento de pontuação)

---

<h2 align="center">📚 Referências</h2>

- Repositório original: [jucimarjr/asteroids_pygame](https://github.com/jucimarjr/asteroids_pygame)
- Documentação do pygame: [pygame.org/docs](https://www.pygame.org/docs/)
- C4 Model: [c4model.com](https://c4model.com)

---

<h2 align="center">👥 Equipe</h2>

<p align="center">

| Nome |
| ---- |
| Ana Beatriz Maciel Nunes |
| Fernando Luiz Da Silva Freire |
| Juliana Ballin Lima |

</p>

---

<h3 align="center">UEA · Tópicos Especiais para Computação I · Atividade 007 — Multiplayer Local</h3>
