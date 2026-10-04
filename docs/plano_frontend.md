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

### Passo 3.2: O Sistema de Animações (Framer Motion)
- **Animação de Distribuição:** Quando o servidor avisa que a mão começou, as cartas saem do centro (dealer) e deslizam de forma animada para a mão de cada jogador.
- **Animação de Cartas Comunitárias:** O Flop, Turn e River não devem apenas "aparecer" do nada. Eles devem girar (CSS 3D flip 180º).
- **Movimento de Fichas:** Quando alguém dá Call, um aglomerado visual de fichas deve pular do jogador para o centro da tela. No final da mão, o pote inteiro desliza para a direção do avatar do vencedor.

### Passo 3.3: Feedback Sonoro (Audio Engine)
- Disparar um som de "Click" seco de plástico batendo toda vez que alguém aposta.
- Som sutil de papel de carta deslizando na mesa quando o Flop/Turn/River é virado.
- Som de vitória (caixa registradora ou sininho de jackpot) ao ganhar um pote grande.

### Passo 3.4: Sistema de Coleta de Dados e Evolução Contínua
- Gravação furtiva das partidas. Toda vez que um jogador Humano (você, seu pai, seu irmão) tomar uma decisão, o Backend Python salva a situação em um banco local de dados (`historico_humanos.db`).
- Extração de estatísticas (VPIP e PFR) da sua família para montar Perfis no Algoritmo Genético.
- Rodaremos a evolução das IAs contra esses "Fantasmas" virtuais da sua família para garantir que os Bots aprendam a extrair dinheiro especificamente dos erros que vocês cometem.
