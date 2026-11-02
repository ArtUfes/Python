# Roadmap Oficial do Poker em Python + React 🃏🚀

Este documento define a visão de produto, os marcos tecnológicos já consolidados e o planejamento estratégico de evolução contínua para o nosso simulador profissional de Texas Hold'em. O projeto alia aprendizado de máquina, desenvolvimento fullstack em tempo real e produção de conteúdo didático (Devlog no YouTube).

---

## 🏆 Visão Geral dos Marcos e Complexidade

| Fase | Tópico | Dificuldade (1-10) | Status | Episódio / Ref |
| :--- | :--- | :---: | :---: | :---: |
| **Fase 1** | Avaliador de Mãos Otimizado (Bitwise & Single-Pass) | 7/10 | 🟢 Concluído | Vídeo 1 |
| **Fase 2** | Motor de Apostas, Turnos e Divisão de Potes (Side Pots) | 8/10 | 🟢 Concluído | Vídeo 1 |
| **Fase 3** | Primeiro Bot IA com Monte Carlo e Algoritmo Genético | 6/10 | 🟢 Concluído | Vídeo 1 |
| **Fase 4** | Interface Web Realtime (React + Framer Motion + WebSockets) | 6/10 | 🟢 Concluído | Vídeo 2 |
| **Fase 5** | Áudio Procedural, Hand History PokerStars e HUD | 4/10 | 🟢 Concluído | Vídeo 2 |
| **Fase 6.1** | Lobby VIP, Economia de Bankroll ($100k) e Modo Espectador | 5/10 | 🟢 Concluído | Vídeo 3 |
| **Fase 6.2** | **Torneio Mata-Mata (Sit & Go) com Subida de Blinds e Pódio** | **5/10** | 🟡 **PRÓXIMO PASSO** | **Vídeo 4** |
| **Fase 7** | Identidade Visual 2.0 & Assets Customizados | 3/10 | ⚪ Planejado | — |
| **Fase 8** | Feedback de Showdown & Animação das 5 Melhores Cartas | 4/10 | ⚪ Planejado | — |
| **Fase 9** | Suporte a Mesas Flexíveis de 2 a 9 Jogadores (Full Ring) | 7/10 | ⚪ Planejado | — |
| **Fase 10** | Audio FX 2.0 & Ambiência Imersiva de Cassino | 3/10 | ⚪ Planejado | — |
| **Fase 11** | Perfis Comportamentais de Bots & Treinamento Competitivo | 8/10 | ⚪ Planejado | — |
| **Fase 12** | Modo Multiplayer com Contas de Usuários (Salas para Amigos) | 8/10 | ⚪ Planejado | — |
| **Fase 13** | Blindagem de Segurança, Anti-Cheat e Hardening de Dados | 6/10 | ⚪ Planejado | — |
| **Fase 14** | Analisador Didático de EV+ & Mentor de Decisões em Tempo Real | 8/10 | ⚪ Planejado | — |

---

## ✅ Marcos Consolidados (O que já está pronto)

### ~~1. Otimização do Avaliador de Mãos (Performance Bruta)~~
* **Dificuldade:** 7/10
* **Resumo:** Avaliador `AvaliadorDeMaosOtimizado` baseado em contagem de frequência (Histogramas) e operações bitwise, atingindo mais de 200.000 avaliações por segundo. Desempates resolvidos nativamente com Tuplas de Força em tempo constante $O(1)$.

### ~~2. Motor de Regras, Turnos e Side Pots~~
* **Dificuldade:** 8/10
* **Resumo:** Ciclo formal do Texas Hold'em (Pré-Flop, Flop, Turn, River e Showdown). Algoritmo de resolução e divisão de potes principais e paralelos (`GerenciadorDePote`) suportando All-Ins múltiplos e empates (Split Pots).

### ~~3. Inteligência Artificial Inicial dos Bots~~
* **Dificuldade:** 6/10
* **Resumo:** Cálculo de equidade via Simulação iterativa de Monte Carlo em tempo real. Parametrização em genes evolutivos (taxa de blefe, agressividade, call em overbet).

### ~~4. Interface Web Realtime com Física Visual~~
* **Dificuldade:** 6/10
* **Resumo:** Monorepo com Flask-SocketIO e React 18 + Vite. Física visual de cartas e pilhas de fichas com Framer Motion e layout Glassmorphism.

### ~~5. Hand History Oficial e Indicadores de Carreira~~
* **Dificuldade:** 4/10
* **Resumo:** Gravação de partidas no padrão canônico do PokerStars, exportável para PokerTracker e Hand Replayers online. Cálculo em tempo real de estatísticas de jogo: VPIP, PFR, AF, C-Bet e Taxa de Vitória.

### ~~6.1. Lobby VIP, Cash Game Completo e Modo Espectador~~
* **Dificuldade:** 5/10
* **Resumo:** 
  - **Lobby VIP (Menu Principal):** Seleção de stakes (Micro $5/$10 a VIP $50/$100), saldo persistente em SQLite ($100.000 padrão) e slider de buy-in flexível (10 a 1.000 BBs).
  - **Conservação Estrita de Fichas:** Débito atômico de buy-in e crédito integral ao sair da mesa.
  - **Modo Espectador & Botão `↑ Levantar`:** Desocupação de assento a qualquer momento com fold seguro, vaga livre pulsante (`⬇ Sentar`), retorno em mãos futuras e rebuy com delay inteligente pós-showdown.
  - **Dinâmica Acelerada dos Bots:** Centralização no dicionário `CONFIG_TEMPOS` (83% de respostas entre 1-3s).
  - **Bateria de Testes:** 24 testes unitários e de borda aprovados com 100% de sucesso.

---

## 🎯 Próximo Passo Imediato (Foco do Vídeo 4)

### 🏆 Fase 6.2: Modo Torneio Mata-Mata (Sit & Go)
* **Dificuldade:** 5/10
* **Detalhamento:**
  - **Estrutura de Inscrição:** Buy-In fixo com stack inicial idêntico para todos os competidores (ex: $1.500 fichas para 4 jogadores).
  - **Sem Rebuy (Eliminação Direta):** Jogador que zera o stack é permanentemente eliminado da mesa.
  - **Subida Periódica de Blinds (Blind Levels):**
    - Temporizador de nível (Blind Clock) ou subida a cada $N$ mãos (ex: Nível 1: $10/$20, Nível 2: $20/$40, Nível 3: $30/$60, Nível 4: $50/$100...).
    - Notificação visual dramática na mesa quando os blinds aumentam, forçando a agressividade.
  - **Transição de Mesa:** Ajuste dinâmico quando jogadores são eliminados (de 4 para 3 jogadores, e Heads-Up final 1 vs 1).
  - **Tela de Vitória e Premiação:**
    - Animação festiva de pódio com entrega do Troféu Dourado para o 1º Lugar.
    - Divisão da premiação do pote acumulado (ex: 70% para o campeão e 30% para o vice).

---

## 🔮 Fases Futuras do Roadmap (Visão Estratégica)

### 🎨 Fase 7: Identidade Visual 2.0 & Assets Customizados
* **Dificuldade:** 3/10
* **Detalhamento:**
  - **Salto Visual do Jogo:** Substituir elementos genéricos por um pacote coeso e autoral de assets estilizados.
  - **Baralho e Cartas:** Ilustrações vetorizadas exclusivas para figuras (J, Q, K, A) e opções de estampas elegantes para o verso das cartas.
  - **Fichas 3D:** Texturas detalhadas para fichas de diferentes denominações ($5, $25, $100, $500, $1.000, $5.000).
  - **Feltro e Mesas:** Opções de cores e texturas de mesa (Verde Clássico, Azul Noite, Vermelho Borgonha, Preto VIP Carbono).

### 🃏 Fase 8: Feedback de Showdown & Destaque das 5 Melhores Cartas
* **Dificuldade:** 4/10
* **Detalhamento:**
  - **Clareza no Desfecho:** Ao final da mão, iluminar e destacar exatamente quais 5 cartas (entre as 2 da mão e as 5 da mesa) formaram o jogo de cada jogador que disputou o showdown.
  - **Identificação do Vencedor:** Cartões destacados mostrando o nome da mão vencedora (ex: *"Sequência de 9 ao Rei"* ou *"Dois Pares: Áses e Damas"*).
  - **Física dos Potes:** Animação de fichas deslizando de forma precisa e sem engasgos para o vencedor (ou dividindo suavemente entre os empatados em Split Pots).

### 🪑 Fase 9: Mesas Dinâmicas de 2 a 9 Jogadores (Full Ring)
* **Dificuldade:** 7/10
* **Detalhamento:**
  - **Flexibilidade Total:** Superar a limitação atual de 4 jogadores fixos, permitindo partidas com qualquer quantidade entre 2 e 9 participantes.
  - **Redesenho Oval da Mesa:** Arquitetura geométrica para dispor os assentos em elipse de forma harmônica e responsiva para mobile e desktop.
  - **Posicionamento Polar:** Algoritmo dinâmico de distribuição de coordenadas para Heads-Up (2p), 3-Max, 4-Max, 6-Max e Full Ring (9p).
  - **Lógica de Dealer & Blinds:** Ajuste estrito da rotação das posições oficiais (Button, Small Blind, Big Blind, UTG, Middle Position, Hijack, Cutoff).

### 🎵 Fase 10: Audio FX 2.0 & Ambiência Imersiva
* **Dificuldade:** 3/10
* **Detalhamento:**
  - **Design Sonoro Completo:** Refinamento dos efeitos sintetizados na Web Audio API com sonoridades ricas e orgânicas.
  - **Efeitos Dramáticos:**
    - Som de embaralhar e corte de baralho no início da rodada.
    - Efeito sonoro de batimentos cardíacos nos últimos segundos da barra de tempo do jogador (Timer Countdown).
    - Som metálico pesado ao anunciar All-In.
    - Fanfarra/comemoração sutil ao puxar um grande pote.

### 🧠 Fase 11: Perfis Comportamentais de Bots & Treinamento Competitivo
* **Dificuldade:** 8/10
* **Detalhamento:**
  - **Arquétipos de Jogadores Reais:** Criação de bots com estilos de jogo distintos e reconhecíveis:
    - *O Rocha (Tight-Passive):* Só aposta com mãos pré-flop premium; desiste fácil para agressão.
    - *O Pagador (Calling Station):* Paga apostas até o river com qualquer par ou draw, quase nunca aplica raises.
    - *O Maníaco (Loose-Aggressive / LAG):* Alta frequência de open-raises, overbets e blefes agressivos pós-flop.
    - *O Estrategista (Tight-Aggressive / TAG):* Joga poucas mãos, mas com agressividade cirúrgica baseada em posição e equidade.
  - **Treino Competitivo Robusto:** Treinamento em massa via simulações com reforço genético para criar bots avançados capazes de derrotar jogadores médios e experientes.

### 👥 Fase 12: Modo Multiplayer com Contas de Usuários (Lobby com Amigos)
* **Dificuldade:** 8/10
* **Detalhamento:**
  - **Sistema de Autenticação:** Criação de contas seguras (Registro, Login, Recuperação de Senha) para que familiares e amigos joguem juntos.
  - **Mesas Privadas & Públicas:** Possibilidade de criar uma mesa de Cash Game ou torneio com código de convite para jogar contra pessoas reais em tempo real.
  - **Sincronização Multi-Client Resiliente:** Arquitetura WebSocket com reconexão automática e gerenciamento de desconexões (auto-check/fold após tempo limite).

### 🛡️ Fase 13: Blindagem de Segurança, Anti-Cheat e Hardening de Dados
* **Dificuldade:** 6/10
* **Detalhamento:**
  - **Autoridade Estrita no Servidor (Server-Authoritative):** O cliente React atua apenas como visor visual. Cartas ocultas dos oponentes, lógica de baralho, cálculo de potes e saldo residem 100% no servidor Python, impossibilitando inspeção de cartas via DevTools do navegador.
  - **Proteção de Dados Sensíveis:** Isolamento completo de variáveis de ambiente (`.env`), hash seguro de senhas (bcrypt/argon2) e restrição total de acesso a arquivos de banco SQLite.
  - **Anti-Abuso & Rate Limiting:** Proteção contra spam de requisições, injeção de dados ou tentativas de exploração de endpoints da API.

### 📊 Fase 14: Analisador Didático de EV+ & Mentor de Decisões em Tempo Real
* **Dificuldade:** 8/10
* **Detalhamento:**
  - **Fusão Jogo + Software de Estudo (Poker Coach):** Modo especial de treino onde a tela exibe um painel lateral de análise estratégica avançada:
    - **Cálculo de EV (Expected Value):** Indicação se o movimento (Fold, Call, Raise) é matematicamente EV+ (lucrativo a longo prazo) ou EV- (prejudicial).
    - **Frequências de Decisão:** Exibição da distribuição recomendada para aquela situação (ex: *70% Raise / 30% Check*).
    - **Explicação Conceitual Didática:** Porcentagem exata de vitória contra o range provável dos adversários, pot odds necessárias e lições táticas em tempo real para o jogador evoluir e entender a lógica por trás de cada jogada.

---

## 💡 Sugestões da IA para Você (Ideias Extras para Enriquecer o Jogo e seu Portfólio)

Analisando a arquitetura do projeto e o potencial para o seu canal do YouTube, aqui estão **8 ideias de alto impacto** com suas respectivas notas de complexidade (1-10):

### 1. Replayer de Mão Nativo no Próprio Jogo (Native Hand Replayer Modal)
* **Dificuldade:** 5/10
* **Conceito:** Em vez de depender de copiar o texto e colar em sites externos (como PokerStars Replayer), criar um botão `"⏮ Rever Última Mão"` diretamente na mesa ou no lobby.
* **Implementação:** Um modal interativo com uma barra deslizante (*scrubber*) e botões de `Play / Pause / Passo a Passo` que anima novamente a rodada completa, mostrando a ação exata street por street.
* **Impacto no Portfólio:** Demonstra domínio avançado de manipulação de estado cronológico e animações orientadas a eventos no React.

### 2. Ações Antecipadas estilo PokerStars (Pre-Action Checkboxes)
* **Dificuldade:** 3/10
* **Conceito:** Enquanto os adversários ou bots estão pensando, permitir que o jogador marque opções antes de chegar a sua vez: `[ ] Check/Fold`, `[ ] Check`, `[ ] Call Any`, `[ ] Auto-Fold`.
* **Implementação:** Assim que a ação chega na vez do jogador humano, o frontend dispara a jogada imediatamente sem travar o jogo nem esperar o timer.
* **Impacto no Jogo:** Acelera exponencialmente o ritmo da mesa e dá a autêntica sensação dos maiores clientes profissionais de poker online do mundo.

### 3. Baralho de 4 Cores (Four-Color Deck) e Personalização de Skins
* **Dificuldade:** 2/10
* **Conceito:** No poker profissional online, o padrão da indústria é o baralho de 4 cores: **Espadas (Preto ♠)**, **Copas (Vermelho ♥)**, **Ouros (Azul ♦)** e **Paus (Verde ♣)**.
* **Implementação:** Um seletor de tema nas configurações do menu que permite alternar entre Baralho Clássico (2 cores) e Baralho Pro (4 cores), além de escolher temas para o feltro (Verde Cassino, Azul Cyber, Vermelho Royal).
* **Impacto no Canal:** Cria conteúdo visual excelente mostrando opções de acessibilidade e design de interface centrado no usuário.

### 4. Sistema de Conquistas & Missões Diárias (Gamificação com Badges)
* **Dificuldade:** 4/10
* **Conceito:** Desafios gamificados para engajar o jogador, tais como:
  * *"Caçador de Trincas"*: Acerte uma trinca no Flop.
  * *"Blefe de Mestre"*: Ganhe uma mão no River tendo apenas Carta Alta após aplicar uma overbet.
  * *"Rei do Sit & Go"*: Vença seu primeiro torneio mata-mata em 1º lugar.
* **Implementação:** Uma tabela `conquistas` no SQLite. Sempre que o servidor detecta o evento no final da mão, registra a conquista e dispara um banner comemorativo no React.
* **Impacto no Portfólio:** Mostra capacidade de arquitetar sistemas completos de gamificação e regras de negócio complexas.

### 5. Chat com Reações de Emojis e Provocações dos Bots (Table Banter)
* **Dificuldade:** 3/10
* **Conceito:** Permitir que o jogador envie emojis flutuantes sobre seu avatar (😎, 🤬, 🍿, 🏆) e fazer os bots "falarem" frases curtas no log de ações baseadas no seu perfil.
* **Implementação:** O bot *Maníaco* pode mandar um texto *"Pagou pra ver o ferro!"*, enquanto o *Rocha* diz *"Essa eu não largo..."*.
* **Impacto no Jogo:** Dá muita personalidade e humor aos vídeos do YouTube, tornando a partida divertida de assistir além do aspecto puramente matemático.

### 6. Gráfico de Evolução de Bankroll e Lucro Esperado (SharkScope / PokerTracker)
* **Dificuldade:** 5/10
* **Conceito:** No modal de estatísticas do jogador, exibir um gráfico dinâmico de linha (utilizando Chart.js ou Recharts) mostrando a curva de fichas ao longo das mãos jogadas.
* **Implementação:** O gráfico traça duas linhas clássicas do poker:
  * **Linha Verde (Lucro Real):** Quanto dinheiro o jogador realmente ganhou/perdeu.
  * **Linha Amarela (All-In EV):** Quanto dinheiro ele *deveria* ter ganho matematicamente baseado na equidade no momento dos All-Ins (medindo se o jogador está com sorte ou azar).
* **Impacto no Portfólio:** Extremamente valorizado por recrutadores e empresas de dados/fintechs/gaming por demonstrar computação estatística avançada.

### 7. Calculadora de Equidade Integrada (Mini-Equilab no Menu)
* **Dificuldade:** 4/10
* **Conceito:** Uma aba utilitária no lobby onde o usuário pode selecionar manualmente 2 cartas para ele, 2 cartas para um vilão, e 0 a 5 cartas comunitárias para calcular as probabilidades exatas.
* **Implementação:** Interface visual interativa de seleção de cartas que roda 50.000 simulações no backend em Python em menos de 0.2 segundos e devolve a fatia de vitória de cada mão.
* **Impacto Didático:** Transforma o projeto em uma ferramenta completa de estudo de poker que espectadores do canal podem baixar e usar no dia a dia.

### 8. Suporte a Progressive Web App (PWA / Modo Mobile)
* **Dificuldade:** 5/10
* **Conceito:** Adaptar a mesa e o menu para formatos verticais responsivos, permitindo que o jogo seja instalado direto no smartphone como um aplicativo nativo (sem precisar de Play Store).
* **Implementação:** Configuração de `manifest.json`, Service Workers para cache de assets e media queries CSS adaptando a disposição dos assentos em formato portrait.
* **Impacto no Portfólio:** Prova sólida de competência em desenvolvimento frontend responsivo moderno e arquitetura PWA.
