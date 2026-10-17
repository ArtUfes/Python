# Roadmap do Poker em Python (v2.0 e Futuro)

Este documento guarda as diretrizes, otimizações e novas funcionalidades que devem ser implementadas no projeto nas futuras atualizações com auxílio de IA.

## ~~1. Otimização do `AvaliadorDeMaos` (Performance / Monte Carlo)~~
O avaliador atual possui lógica perfeita para regras e desempates, mas não está otimizado para simulações de milhões de cenários.

**Problema atual:**
As funções iteram múltiplas vezes pela mesma mão (`O(N)`) e chamam `sorted()` dezenas de vezes para checar as mãos possíveis do maior para o menor.

**Solução (Mapas de Frequência):**
- **Extração única:** A mão de 7 cartas deve ser lida apenas 1 vez (O(N)).
- **Histograma de Valores (Hash Map):** Criar um dicionário/array que conte a frequência de cartas (ex: `{'A': 2, 'K': 1}`). Isso permite achar quadras, trincas e pares em `O(1)`.
- **Histograma de Naipes:** Dicionário que conta os naipes, tornando o reconhecimento de Flushes instantâneo em `O(1)`.
- **Bitmasks / Lookup Tables:** Para simulações ainda mais extremas, migrar para avaliação bit-a-bit (Cactus Kev / TwoPlusTwo).

## ~~2. Sistema de Apostas e Motor do Jogo~~
Para que o jogo seja completo, precisamos ir além de comparar quem ganha e quem perde, e implementar a "Economia" do jogo.
- **Estruturas de Apostas:** Lógica para Blind (Small/Big), Call, Raise (com regras matemáticas de tamanho mínimo), Check e Fold.
- **Gerenciamento do Pote (Pot Management):** Somar fichas e transferir para o ganhador.
- **Divisão de Potes (Side Pots e Split Pots):** Esse é um dos maiores desafios lógicos! Lidar com empates (Split Pot) e principalmente com cenários de All-In (Side Pots). Por exemplo: Se o jogador A aposta 100, B paga 100, mas C tem apenas 50 e dá All-in. Precisamos criar o "Pote Principal" de 150 (disputado pelos três) e o "Side Pot" de 100 (disputado apenas por A e B).

## ~~3. Construção de um "Bot/AI" Adversário~~
Implementar um agente inteligente capaz de jogar contra um usuário humano. 

**Como fazer um bot forte no Poker:**
Como nosso simulador (`app.py`) já tem suporte a "Simulações de Equidade", o bot usará **Simulação de Monte Carlo** no momento de sua decisão:
1. O bot olha suas próprias 2 cartas e as cartas da mesa.
2. Ele projeta 10.000 cenários aleatórios de possíveis cartas para o oponente e para o resto da mesa.
3. Se a "Equidade" dele (porcentagem de vitória) for alta, ele aposta/aumenta.
4. Se for média, ele paga (call).
5. Se for muito baixa, ele foge (fold).

Esse comportamento matemático, alinhado ao conceito de *Expected Value (EV)*, criará um adversário duro na queda e matematicamente correto na maior parte das decisões!

## ~~4. Interface de Jogo (Front-end Web em Tempo Real)~~
- Implementada aplicação full-stack monorepo: Servidor Python WebSocket (`servidor.py`) + Client React/Vite (`frontend/`).
- Física de cartas e fichas de cassino com Framer Motion e design VIP Glassmorphism.
- Feedback Sonoro Orgânico (Audio Engine) com foley real de estúdio (cartas, fichas, mesa).
- HUD de indicadores em tempo real.

## ~~5. PokerStars Hand History & Coleta de Dados~~
- Criado o módulo `core/gravador_historico.py` com persistência em SQLite (`historico_partidas.db`).
- Geração automática da transcrição textual canônica oficial do PokerStars.
- Exportação direta para softwares de análise (PokerTracker, HM3) e Hand Replayers online.
- Cálculo de métricas $O(1)$ de VPIP, PFR, AF, WTSD, W$SD, C-Bet e BB/100.

> [!IMPORTANT]
> **Diretriz Estratégica Atual (Foco em Game Dev & Experiência):**
> O foco do projeto agora está **100% concentrado no desenvolvimento do jogo em si** (Criação de Modos de Jogo, Lobby/Menu Inicial, Regras de Torneio vs Cash Game, UX/UI e integração com Hand Replayer), **ao invés de focar no treinamento avançado de bots por enquanto**. Os bots atuais (Monte Carlo + DNA Darwin v1) já são oponentes funcionais excelentes para alimentar a dinâmica e validar a economia das partidas.

## 6. Menu Inicial (Lobby), Modos de Jogo e Experiência do Jogador (FOCO ATUAL)
- **Tela de Lobby Inicial (Full Web Experience):**
  - Entrada visual premium antes de carregar a mesa de feltro.
  - Painel de perfil do jogador (Avatar, Banca acumulada, Indicadores de Carreira como VPIP, PFR e Arquétipo).
- **Seleção de Modos de Jogo:**
  - **Modo 1: Cash Game (Mesa Contínua):**
    - Blinds fixos (ex: $10/$20).
    - Rebuys ilimitados ao zerar fichas (recarga instantânea).
    - Foco estratégico: Maximizar lucro a longo prazo e taxa de **BB/100**.
    - O jogador pode entrar e sair da mesa a qualquer momento com o saldo acumulado.
  - **Modo 2: Torneio Mata-Mata (Sit & Go / Knockout):**
    - Buy-in fixo (ex: $500 para entrar) e stack inicial igual para todos os 4 jogadores.
    - **Sem rebuy:** Se as fichas zerarem, o jogador/bot é eliminado da mesa (eliminação direta).
    - **Aumento progressivo dos Blinds (Blind Levels):** A cada $N$ mãos (ex: a cada 5 mãos), os blinds sobem (10/20 -> 20/40 -> 40/80 -> 100/200), forçando a agressão.
    - **Disputa por Pódio:** Premiação para 1º lugar (Troféu/Premiação máx) e 2º lugar.
- **Central de Dados & Exportação no Menu:**
  - Botão de download rápido de arquivo `.txt` do histórico de mãos (Padrão PokerStars) pronto para colar em replayers externos.
  - Visualizador interno rápido de histórico com resumo das últimas mãos jogadas.

## 7. Organização e Limpeza da Estrutura do Repositório (Refatoração)
- Limpeza da raiz do projeto para isolar arquivos transitórios e gerados:
  - Mover arquivos de dados (`historico_partidas.db`, logs de treinamento, exportações `.txt`) para uma pasta estruturada `/data` ou `/storage`.
  - Mover scripts avulsos da raiz para pastas semânticas (`scripts/` ou `benchmarks/`).
  - Configurar `.gitignore` robusto para não commitar bancos locais ou arquivos de exportação desnecessários.

## 8. Bateria de Testes Automatizados e Política Anti-Regressão
- Implementar suite de testes automatizados com `pytest`:
  - **Testes Unitários:** Avaliador de mãos, desempates, cálculo de pot odds, split pots e side pots.
  - **Testes de Regras e Economia:** Garantir que o stack nunca fique negativo, que raises acima do all-in sejam bloqueados e que jogadores sem fichas sejam eliminados ou façam rebuy.
  - **Política Anti-Regressão:** Para cada novo bug descoberto e corrigido, criar obrigatoriamente um teste unitário correspondente antes de fechar a tarefa, garantindo que o bug nunca volte em versões futuras.

## 9. Mentor de Poker com LLM (Integração de IA Generativa)
- Enviar o sumário da análise matemática do Monte Carlo + o histórico da mão para uma API de IA (como o Gemini) com um prompt de sistema configurado para atuar como um **Professor Profissional de Poker**.
- A IA vai explicar em linguagem natural por que uma jogada foi ruim ou boa.
- Criar relatórios de sessão ("Aulas") textuais focadas nas maiores fraquezas detectadas matematicamente na sessão do jogador.
