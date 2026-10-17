# Plano de Implementação do Frontend (React + Python)

Este documento descreve a arquitetura e o passo a passo para transformar o motor de Poker local (Python) em uma aplicação web full-stack completa, jogável por humanos através do navegador.

## 1. Visão Geral da Arquitetura (Monorepo)

O projeto deixará de ser um script que roda no terminal e passará a ser uma aplicação dividida em duas partes que se comunicam em tempo real (WebSockets).

```text
poker/
├── backend/                  <-- Nosso motor atual Python
│   ├── core/
│   └── servidor.py           <-- Novo servidor (Flask/FastAPI + Socket.io)
└── frontend/                 <-- Novo projeto Javascript/React
    ├── src/
    │   ├── components/       <-- Cartas, Mesa, HUD
    │   └── App.jsx
    └── public/assets/        <-- Imagens das cartas e fichas
```

## 2. O MVP (Minimum Viable Product)
**Objetivo:** Fazer o jogo rodar no navegador o mais rápido possível, sem perder tempo procurando imagens ou desenhando mesas 3D. Foco absoluto na comunicação entre Backend e Frontend.

### Passo 2.1: Inicialização do Projeto
- Criar a pasta `frontend/` usando o Vite (`npm create vite@latest frontend -- --template react`).
- Limpar o CSS padrão e preparar a estrutura de componentes.
- Instalar bibliotecas de comunicação (`socket.io-client`).

### Passo 2.2: Servidor Backend (O Porteiro)
- Criar um script `backend/servidor.py` usando `python-socketio` ou similar.
- Envolver a classe `Mesa` e o fluxo que hoje existe no `jogar_terminal.py` para emitir eventos de WebSocket. 
- *Exemplo:* Quando for o Pre-Flop, o servidor emite o evento `nova_rodada` passando um JSON com as cartas do jogador humano.

### Passo 2.3: Interface Provisória (Gráficos de Desenvolvedor)
No MVP, **não usaremos assets baixados da internet**.
- **Mesa:** Uma `div` HTML verde genérica com borda arredondada.
- **Cartas:** Renderizadas via CSS puro. Retângulos brancos. Para os naipes, usaremos símbolos de texto (♠️, ♥️, ♣️, ♦️) ou formas geométricas simples (ex: um losango vermelho desenhado no CSS para representar Ouros).
- **Fichas/Apostas:** Apenas texto simples (Ex: `Aposta: $200`) embaixo do nome do jogador.
- **Controles do Jogador:** 3 botões simples HTML (Fold, Call, Raise) e um campo de input (text box) para o valor do Raise.

**Critério de Conclusão do MVP:** Você consegue abrir o `localhost`, sentar na mesa visual, receber suas duas cartas desenhadas em CSS, ver os Bots "pensando" e jogando nos turnos deles, e a mesa calcular quem ganhou e distribuir o dinheiro.

---

## 3. Fase de Polimento (O Produto Profissional)
**Objetivo:** Transformar o MVP provisório em um jogo com estética de Cassino VIP, áudio e animações imersivas.

### Passo 3.1: Coleta de Assets Oficiais (✅ CONCLUÍDO)
- Substituir o CSS de cartas pelas imagens em vetor (SVG/PNG) de um baralho oficial (Usando DeckOfCardsAPI).
- Fundo de feltro e hud glassmorphism aplicados.
- Adicionar ícones de fichas e botões estilizados (Concluído usando emojis visuais nativos e gradientes modernos CSS).

### Passo 3.2: O Sistema de Animações (Framer Motion) (✅ CONCLUÍDO)
- **Animação de Distribuição:** Quando o servidor avisa que a mão começou, as cartas saem do centro (dealer) e deslizam de forma animada para a mão de cada jogador.
- **Animação de Cartas Comunitárias:** O Flop, Turn e River não devem apenas "aparecer" do nada. Eles devem girar (CSS 3D flip 180º).
- **Movimento de Fichas:** Quando alguém dá Call, um aglomerado visual de fichas deve pular do jogador para o centro da tela. No final da mão, o pote inteiro desliza para a direção do avatar do vencedor.

### Passo 3.3: Feedback Sonoro (Audio Engine) (✅ CONCLUÍDO)
- **Foley de Cassino Real (Kenney CC0):** Baixados e integrados assets autênticos de estúdio gravados em estúdio para cartas, fichas e vitória.
- **Disparo de Áudio Reativo:**
  - Som de clique seco de fichas/argila (`chipBet`) ao apostar, dar Call ou Raise.
  - Som sutil de papelão de carta deslizando no feltro (`cardSlide`) ao receber cartas no Pre-Flop.
  - Som de impacto no feltro (`cardPlace`) quando cartas comunitárias (Flop/Turn/River) viram.
  - Som de recolher fichas e vitória (`chipCollect` + `win`) no Showdown ao puxar o pote.
  - Som sutil de alerta (`alertTurn`) quando o turno chega para o jogador humano.
  - Som de "batidinha de mesa" para Check e som de descarte de cartas para Fold.
- **Engine com Variação Orgânica de Pitch:** O [audioEngine.js](file:///c:/Users/conta/Documents/programas/poker/Python/frontend/src/audioEngine.js) varia sutilmente o pitch (±5%) em cada execução para evitar repetição mecânica.
- **Controle de Mudo:** Botão flutuante estilizado (🔊 / 🔇) no canto da mesa para mutar/desmutar a qualquer momento.

### Passo 3.4: Sistema de Coleta de Dados e Evolução Contínua (✅ CONCLUÍDO)
- **Gravador Relacional + Padrão PokerStars ([core/gravador_historico.py](file:///c:/Users/conta/Documents/programas/poker/Python/core/gravador_historico.py)):**
  - Todas as mãos disputadas na mesa são persistidas no banco SQLite `historico_partidas.db`.
  - Cada mão gera automaticamente o texto exato da transcrição canônica do **PokerStars Hand History** (permitindo exportação para PokerTracker, Hold'em Manager e Hand Replayers).
- **Cálculo Incremental de Métricas em Tempo Real:**
  - O sistema calcula de forma instantânea $O(1)$ os indicadores fundamentais: **VPIP %, PFR %, AF (Fator de Agressividade), WTSD %, W$SD %, C-Bet % e BB/100**.
  - Classificação automática de arquétipos (*Calling Station*, *TAG*, *Maniac/LAG*, *Nit*).
- **HUD em Tempo Real na Mesa:**
  - O avatar do jogador humano no React agora exibe um badge flutuante com suas estatísticas e arquétipo atualizado a cada mão.
- **Exportação:** Método `exportar_pokerstars_txt()` para gerar lotes de mãos prontas para análise externa.

---

## 4. Próxima Fase: Lobby / Menu Inicial e Seleção de Modos

### Passo 4.1: Tela de Menu Inicial (Lobby)
- Interface de entrada no jogo antes de carregar a mesa.
- Seleção de Modos de Jogo:
  1. **Cash Game (Mesa Contínua):** Blinds fixos, rebuys automáticos ao zerar o stack, foco em maximizar BB/100.
  2. **Torneio Mata-Mata (Sit & Go / Knockout):** Buy-in único, eliminação direta ao zerar as fichas, sem rebuy, aumento gradual dos blinds e disputa por pódio (1º e 2º lugar).
- **Central de Dados & Exportação no Menu:**
  - Botão no Lobby para baixar o arquivo `.txt` do histórico de mãos (com filtro: "Últimas 50 mãos" ou "Histórico Completo").
  - Painel de estatísticas acumuladas do jogador no estilo gráfico/resumo.
