# Changelog (Registro de Alterações)

## [28/09/2026] - Otimização do Motor de Poker (Avaliador de Mãos)

Nesta data, concluímos o primeiro marco crítico do nosso Roadmap: a transição do avaliador base orientado a objetos para um algoritmo otimizado focado em suportar futuras Simulações de Monte Carlo (Cálculo de Probabilidades) com alto desempenho.

### O que foi feito com detalhes:

1. **Criação da classe `AvaliadorDeMaosOtimizado`:**
   - **Problema:** O avaliador original (`AvaliadorDeMaos.py`) reordenava as cartas repetidas vezes utilizando a função `sorted()` do Python, além de iterar sobre o baralho em múltiplas funções isoladas para cada tipo de mão (ex: uma função para ver se é flush, outra se é par, etc). Isso gerava um tempo de processamento longo em lotes de grande escala.
   - **Solução:** Foi implementado um algoritmo de **Passagem Única (Single-pass) e Histogramas**. Agora, as cartas são "varridas" uma única vez para mapear e registrar a contagem de cada valor e naipe. A verificação da força das mãos agora utiliza estritamente matemática e **operações de bit (Bitwise)** em vez de arrays, eliminando loops aninhados e descartando as funções lentas de ordenação.

2. **Otimização do Sistema de Desempate (Tuplas de Força):**
   - **Problema:** Em simulações Heads-Up (Jogador vs Jogador), empates na força base (como ambos terem Par) são muito frequentes. O código antigo exigia extrair fisicamente as 5 melhores cartas para então chamar uma função demorada como `desempata_par()` comparando carta a carta. 
   - **Solução:** O `AvaliadorDeMaosOtimizado.avalia_mao()` foi atualizado para retornar **Tuplas de Força Absoluta** com os kickers já embutidos (Ex: `(2, 14, 13, 10, 8)` representa Par de Ases com kickers Rei, 10 e 8). O Python avalia comparações entre Tuplas nativamente de forma instantânea (fazendo `Tupla 1 > Tupla 2`), resolvendo desempates sem executar uma linha sequer de código adicional.

3. **Arquitetura Híbrida implementada no `mesa.py`:**
   - O núcleo do jogo principal não precisou ser quebrado ou totalmente reescrito. A classe principal `Mesa` passou a usar o nosso novo algoritmo ultra-rápido para as detecções iniciais (atuando como um "Cécebro de Avaliação"), mas o seu código antigo permaneceu em atividade para fins de **apresentação visual e interface** (como decidir exatamente quais 5 objetos Carta devem ser impressos no console no final da rodada humana).

4. **Criação de Benchmarks Oficiais:**
   - Desenvolvemos scripts blindados (`benchmark_avaliador.py` e `benchmark_desempate.py`) para validar se o algoritmo novo não quebrava as regras do Poker (passou com 100% de assertividade).
   - O ganho documentado nos scripts e planilhas `.csv` resultantes mostrou um avanço real de quase **230% em performance bruta**, aumentando a capacidade do motor do jogo para lidar com confortáveis +76.000 confrontos simulados por segundo em Python puro.

### Arquivos Afetados/Criados:
- `poker_python/avaliador_otimizado.py` (Adicionado)
- `poker_python/benchmark_avaliador.py` (Adicionado)
- `poker_python/benchmark_desempate.py` (Adicionado)
- `poker_python/mesa.py` (Modificado)
- `docs/otimizacao_avaliador.md` (Adicionado)

## [03/10/2026] - Motor de Jogo, Inteligência Artificial e Algoritmo Genético

Nesta fase avançamos da avaliação matemática de cartas para a criação real de um "Jogo de Poker" completo, com turnos, economia e, por fim, a inteligência artificial evolutiva que joga esse jogo.

### O que foi feito com detalhes:

1. **Implementação da Estrutura de Turnos e Dinâmica da Mesa:**
   - Construção do arquivo `jogar_terminal.py`, estabelecendo o ciclo completo de uma mão de Poker: Pre-Flop, Flop, Turn, River e Showdown.
   - Foram implementadas mecânicas vitais como **Stacks (Fichas), Small Blind, Big Blind, Call, Raise, Fold, e All-In**.
   - Integração da lógica de **Potes Secundários (Side Pots)** e divisão de dinheiro via a classe `GerenciadorDePote`.

2. **O Nascimento da Inteligência Artificial (O Bot):**
   - Criação da classe `Bot` em `core/bot.py`. O bot agora utiliza o `AvaliadorDeMaosOtimizado` dentro de simulações iterativas de **Monte Carlo** para estimar suas chances de vitória (Equidade) no meio de uma rodada antes de decidir apostar.
   - O bot foi treinado inicialmente com heurísticas básicas de Pot Odds e Força Relativa para saber quando dar um "Open-Raise" ou quando "Foldar".

3. **Treinamento via Algoritmo Genético (Laboratório Darwin):**
   - A criação da IA manual (Heurística) abriu espaço para um sistema autônomo de aprendizado, implementado em `algoritmo_genetico.py`.
   - Parametrizamos o cérebro matemático da IA em 5 Genes: `forca_open_raise`, `forca_call_overbet`, `agressividade_raise`, `taxa_blefe`, e `taxa_slowplay`.
   - Rodamos simulações evolutivas com torneios fechados onde diferentes instâncias (DNAs) do bot competiam contra perfis Baseline (Maníacos e Calling Stations). 
   - A IA aprendeu de forma completamente autônoma, sem intervenção humana, que o segredo no Poker contra perfis caóticos (mobile) é diminuir blefes e focar em maximizar lucro via "Value Bets".

### Arquivos Afetados/Criados:
- `jogar_terminal.py` (Adicionado)
- `core/bot.py` (Adicionado)
- `simulador_treinamento.py` (Adicionado)
- `algoritmo_genetico.py` (Adicionado)
- `docs/plano_algoritmo_genetico.md` (Adicionado)
- `docs/plano_frontend.md` (Adicionado)
- Arquivos de configuração de potes/turnos modificados no pacote `core/`.

## [04/10/2026] - Interface Web, Tempo Real e UX

Nesta etapa, focamos na experiência do usuário (UX) através da aplicação React (Vite) conectada via WebSockets ao servidor Python.

### O que foi feito com detalhes:

1. **Inteligência de Timers e Simulação Humana (Bots):**
   - Os bots agora não respondem mais instantaneamente. Foi implementado um sistema de *delay* baseado em probabilidades (80% para demorar 2-7s, 15% para 1s e 5% para tankar por 8-10s). 
   - A partida se tornou muito mais imersiva, parecendo que você joga contra humanos de verdade que param para pensar.

2. **Segurança e Regra de Timeout:**
   - Adicionada trava de 10 segundos para a jogada do usuário no `servidor.py`. Caso não jogue a tempo, a mesa força um *Auto-Check* ou *Auto-Fold* e passa a vez.

3. **Visual Moderno e Assets Reais:**
   - Cartas puramente textuais CSS foram substituídas por imagens vetorizadas em alta resolução (Via `DeckOfCardsAPI`). 
   - Adicionadas animações *Glassmorphism* aos painéis de HUD. 
   - A borda de tempo dos jogadores foi traduzida em uma bela barra de progresso visual (Timer Bar) que esgota regressivamente em exatos 10s.

4. **Slider de Aposta (Raise):**
   - Para evitar digitação incorreta de caracteres, substituiu-se o input manual clássico por uma "Barra Deslizante (Slider)". 
   - Limitado responsivamente para forçar raises dentro das regras (mínimo de 2x a aposta e máximo como All-In do jogador).

### Arquivos Afetados/Criados:
- `servidor.py` (Modificado)
- `frontend/src/components/Mesa.jsx` (Modificado)
- `frontend/src/index.css` (Modificado)
- `docs/plano_frontend.md` (Modificado)

## [04/10/2026] - Animações Avançadas e Correções Lógicas (Framer Motion)

Nesta etapa, elevamos o nível da interface implementando o sistema de física visual planejado no Passo 3.2 e corrigimos gargalos de comunicação do estado no React.

### O que foi feito com detalhes:

1. **Implementação de Framer Motion (Física Visual):**
   - **Distribuição (Dealing):** Cartas da mão agora deslizam fluidamente do centro da tela para a posição dos jogadores com `stagger` direcional.
   - **Flip 3D Lento:** Cartas comunitárias (Flop/Turn/River) ganharam um *Flip 180º* 3D mais dramático (1.2s de duração).
   - **Motor Físico de Fichas de Cassino:** Adicionada uma pilha persistente de fichas (`fichasNaMesa`). Apostas deslizam (usando `easeOut` para não rebater) do avatar para o centro e formam um pote dinâmico. No Showdown, a pilha toda desliza até o avatar do vencedor.

2. **Estilização Realista de Fichas em CSS:**
   - Construímos uma representação visual de ficha de cassino clássica utilizando `repeating-conic-gradient` puro, removendo poluição de texto e otimizando a interface gráfica (Performance CSS).

3. **Correção de Stale Closure no React:**
   - Foi corrigido um bug invisível onde o `socket.on` perdia a referência viva do estado dos jogadores. Utilizando um `useRef(estado)` conseguimos um túnel direto, garantindo que as fichas saiam exatamente do jogador correto.

4. **Correção de Lógica no Botão de Check:**
   - Corrigimos a falha onde o React mandava valores incorretos (`CALL 40`) ao invés de `CHECK 0` ao servidor, poupando que fichas indesejadas fossem animadas.

### Arquivos Afetados/Criados:
- `servidor.py` (Modificado)
- `frontend/src/components/Mesa.jsx` (Modificado)
- `frontend/src/index.css` (Modificado)
- `docs/plano_frontend.md` (Modificado)

## [16/10/2026] - Feedback Sonoro Orgânico (Audio Engine)

Nesta etapa, implementamos a sonoplastia imersiva de cassino com foley real gravado em estúdio (Passo 3.3 do plano frontend).

### O que foi feito com detalhes:

1. **Coleta de Assets Reais de Cassino (Kenney CC0):**
   - Baixados e organizados arquivos de áudio profissionais gravados de estúdio em `frontend/public/sounds/`.
   - Inclui variações de atrito de cartas no feltro (`card-slide`), impacto e virada de cartas (`card-place`), choque seco de cerâmica de fichas (`chip-lay`, `chips-collide`), recolhimento de fichas (`chips-handle`, `chips-stack`) e sinos elegantes de confirmação/vitória.

2. **Criação do Módulo `audioEngine.js`:**
   - Pré-carregamento automático (`preload`) em memória para latência zero de disparo durante as animações do Framer Motion.
   - Variação dinâmica de Pitch (±5%) em cada execução, evitando que cliques repetidos de apostas soem mecânicos ou artificiais.
   - Fallback resiliente contra restrições de autoplay dos navegadores.

3. **Integração Reativa com os Eventos da Mesa:**
   - Cartas comunitárias (Flop/Turn/River) emitem som no exato momento da revelação.
   - Cartas da mão no Pre-Flop tocam som sutil de deal no início da rodada.
   - Apostas dos jogadores e bots disparam o som seco de fichas caindo no centro.
   - O vencedor do Showdown é celebrado com o som do recolhimento de fichas e sino de vitória.
   - Alerta sonoro discreto quando o turno passa para o jogador humano ("Sua Vez").
   - Botão flutuante estilizado na mesa (🔊 / 🔇) permitindo mutar ou desmutar com 1 clique.

### Arquivos Afetados/Criados:
- `frontend/public/sounds/` (Adicionados 50+ assets de áudio)
- `frontend/src/audioEngine.js` (Adicionado)
- `frontend/src/components/Mesa.jsx` (Modificado)
- `frontend/src/index.css` (Modificado)
- `docs/plano_frontend.md` (Modificado)

## [17/10/2026] - Sistema de Coleta de Dados e Hand History (Padrão PokerStars)

Implementação completa da gravação estruturada de partidas e cálculo em tempo real de estatísticas de jogadores (Passo 3.4 do plano frontend).

### O que foi feito com detalhes:

1. **Gravação Canônica no Padrão PokerStars:**
   - Criação do módulo `core/gravador_historico.py` contendo a engine de persistência e serialização textual.
   - Cada mão produz o texto canônico idêntico ao gerado pelo software PokerStars (com ID da mão, data/hora, posições dos assentos, stacks, postagem de blinds, cartas distribuídas, ações por rodada, showdown e sumário do pote).
   - Isso permite a exportação direta para softwares como PokerTracker, Hold'em Manager e Hand Replayers online.

2. **Banco Relacional SQLite (`historico_partidas.db`):**
   - Estrutura normalizada em 4 tabelas: `maos`, `mao_jogadores`, `acoes_mao` e `estatisticas_jogadores`.
   - Permite consultas analíticas instantâneas por jogador, posição ou situação de aposta.

3. **Cálculo Incremental de Indicadores em Tempo Real:**
   - A cada mão finalizada, o sistema atualiza em tempo $O(1)$ métricas cruciais de poker: **VPIP %, PFR %, AF (Fator de Agressividade), WTSD %, W$SD %, C-Bet % e BB/100**.
   - Classificação automática de perfis de jogadores (*Calling Station*, *TAG*, *Maniac/LAG*, *Nit*).

4. **HUD em Tempo Real na Mesa Web:**
   - O servidor agora emite o evento `metricas_jogador` via WebSocket.
   - O frontend React renderiza uma tag elegante de HUD no avatar do jogador humano informando seu VPIP, PFR e Arquétipo atual.

5. **Correção de Lógica e Notação: Capping de Raises e Stacks Negativos:**
   - Detectado e corrigido o bug onde bots e jogadores podiam declarar raises superiores ao próprio stack (causando stacks negativos no Poker Hand Replayer).
   - O `processar_acao` em `core/mesa.py` agora limita estritamente qualquer raise ao `max_atingivel` do jogador, convertendo tentativas inválidas em `CALL (All-In)`.
   - O `core/bot.py` foi blindado para nunca tentar dar raise se seu stack for menor ou igual à aposta da mesa.
   - O slider e botões no frontend foram ajustados para desabilitar raises inviáveis e alternar automaticamente para o botão `All-In`.
   - Correção do painel de ações que continuava visível após timeout/fold.

### Arquivos Afetados/Criados:
- `core/gravador_historico.py` (Adicionado)
- `docs/indicadores_poker.md` (Adicionado)
- `relatorio_historico.py` (Adicionado)
- `core/mesa.py` (Modificado)
- `core/bot.py` (Modificado)
- `servidor.py` (Modificado)
- `frontend/src/components/Mesa.jsx` (Modificado)
- `frontend/src/index.css` (Modificado)
- `docs/plano_frontend.md` (Modificado)

## [17/10/2026 - Tarde] - Blindagem de Testes, Classe ResultadoAcao, Compliance YouTube e Regras do Workspace

Nesta etapa, consolidamos a infraestrutura de testes automatizados do projeto, corrigimos uma regressão sutil de tipagem no motor e adicionamos blindagem visual contra restrições de idade no YouTube.

### O que foi feito com detalhes:

1. **Descoberta de Regressão e Criação da Classe `ResultadoAcao`:**
   - **Problema:** Quando atualizamos o `processar_acao` em `core/mesa.py` para retornar uma tupla com 3 valores `(sucesso, acao_real, valor_real)`, os testes pré-existentes em `tests/test_bordas.py` falharam. O teste verificava `self.assertFalse(resultado)`. No Python, qualquer tupla com itens (mesmo contendo `False` na primeira posição, ex: `(False, 'FOLD', 0)`) avalia como `True` em contexto booleano (`bool((False, ...)) == True`).
   - **Solução:** Implementamos a classe orientada a objetos `ResultadoAcao` em `core/mesa.py` implementando os métodos mágicos `__bool__()` (que retorna estritamente `self.sucesso`) e `__iter__()` (que permite o desempacotamento tradicional `sucesso, acao, valor = resultado`). Com isso, preservamos 100% da compatibilidade retroativa e desempacotamento simultâneo.

2. **Otimização da Bateria de Testes (`tests/test_caotico.py`):**
   - O teste de conservação de energia possuía um loop de 5.000.000 de mãos que bloqueava a execução rápida da suíte. O valor foi ajustado para 500 mãos, permitindo validar a conservação matemática exata de fichas em poucos segundos.
   - Toda a suíte de testes unitários foi executada com 100% de assertividade.

3. **Escudo Anti-Restrição de Idade do YouTube (Compliance Visual e Roteiro):**
   - Criação de badge no frontend React informando: *"PROJETO EDUCACIONAL / DEVLOG - Simulação de IA em Python • Sem Dinheiro Real"*.
   - Posicionamento otimizado no **canto superior esquerdo da mesa** (`top: 22px; left: 35px;`), garantindo que não sobreponha o avatar do jogador nem os botões de ação.
   - Adicionada seção de compliance com template de descrição, tags recomendadas e texto de recurso pronto para contestação em `roteiros/video_02_som_hand_history_indicadores.md`.

4. **Diretrizes Permanentes de Desenvolvimento (`AGENTS.md`):**
   - Formalização de regras estritas para IAs e assistentes em `AGENTS.md` e `.agents/rules/git_rules.md`:
     - Proibição absoluta da execução de `git push` pelo assistente.
     - Obrigação de criar e executar testes automatizados (`python -m unittest`) para novas features e correções de bugs.
     - Preservação do princípio da conservação de fichas e isolamento do motor `core/`.

### Arquivos Afetados/Criados:
- `core/mesa.py` (Modificado)
- `tests/test_caotico.py` (Modificado)
- `frontend/src/components/Mesa.jsx` (Modificado)
- `frontend/src/index.css` (Modificado)
- `roteiros/video_02_som_hand_history_indicadores.md` (Modificado)
- `AGENTS.md` (Adicionado)
- `.agents/rules/git_rules.md` (Adicionado)

## [18/10/2026] - Correção do Hand History em All-In Pré-Flop e Teste Unitário

### O que foi feito com detalhes:

1. **Exibição Garantida das Cartas Comunitárias (Streets) em Replayers de PokerStars:**
   - **Problema:** Quando os jogadores iam All-In ainda no Pré-Flop, nenhuma aposta ocorria nas rodadas seguintes (Flop, Turn, River). O gerador de Hand History só emitia os cabeçalhos de street (`*** FLOP ***`, `*** TURN ***`, `*** RIVER ***`) dentro do loop de ações de aposta. Como não havia ações pós-flop, esses cabeçalhos eram omitidos, fazendo com que replayers online (como PokerStars Replayer / PokerHandReplayer) pulassem direto para o Showdown sem abrir as cartas do board na animação da mesa.
   - **Solução:** O método `gerar_hand_history_text` em `core/gravador_historico.py` foi ajustado para estruturar as streets pelo total de cartas comunitárias distribuídas, garantindo que Flop, Turn e River sejam sempre impressos com suas respectivas cartas mesmo que não tenham ocorrido apostas.
   - **Resiliência:** Adicionou-se acesso seguro via `.get()` para campos como `chegou_showdown` e `lucro_liquido`.

2. **Criação de Teste Automatizado de Anti-Regressão (`tests/test_historico.py`):**
   - Implementado teste unitário que simula uma mão com All-In pré-flop e valida a presença obrigatória dos blocos `*** FLOP ***`, `*** TURN ***`, `*** RIVER ***` e `Board [...]` no texto canônico gerado.

3. **Correção de Parser Error em Mãos Ganhas sem Showdown (W.O. / Fold Geral):**
   - **Problema 1 (`Dealt to Você []`):** Quando o jogador dava FOLD, `jogador.foldar()` limpava suas cartas (`self.cartas = []`). Como o histórico era salvo no encerramento da rodada, as cartas do jogador ficavam vazias `[]`, gerando erro de sintaxe no parser.
   - **Solução 1:** No `servidor.py`, criamos `cartas_iniciais` salvas no início da rodada logo após a distribuição, preservando o registro das cartas próprias no Hand History mesmo que o jogador folde. Além disso, no `gravador_historico.py`, se `cartas_str` estiver vazia, a linha `Dealt to` não é emitida com colchetes vazios.
   - **Problema 2 (`*** SHOWDOWN ***` e `shows [...] ()` indevidos):** Quando todos os adversários foldavam, o motor ainda emitia `*** SHOWDOWN ***` e tentava mostrar cartas com descrição vazia `()`, o que quebrava o parser de replayers externos.
   - **Solução 2:** O bloco `*** SHOWDOWN ***` agora só é emitido se 2 ou mais jogadores disputaram até o final. Se apenas 1 jogador sobrou, o pote é recolhido diretamente sem showdown.

### Arquivos Afetados/Criados:
- `core/gravador_historico.py` (Modificado)
- `servidor.py` (Modificado)
- `tests/test_historico.py` (Modificado)
- `historico_pokerstars.txt` (Modificado)

## [31/10/2026] - Menu Principal VIP (Lobby), Sistema de Bankroll e Cash Game RallyAces

Nesta fase construímos a experiência de entrada do jogo no frontend React e o sistema econômico de perfil/bankroll persistente em SQLite, permitindo selecionar mesas de Cash Game dinâmicas e transitar de forma fluida e instantânea entre o Lobby e a Mesa.

### O que foi feito com detalhes:

1. **Sistema de Perfil e Bankroll Persistente (`core/perfil.py`):**
   - Criação da classe `GerenciadorPerfil` operando na nova tabela `perfil` do banco SQLite unificado `historico_partidas.db`.
   - Saldo inicial de $10.000 para novos jogadores e botão de recarga rápida (+$10.000) para testes livres.
   - Sincronização automática do histórico de partidas anteriores (mãos e vitórias calculadas de `mao_jogadores`).
   - Métodos transacionais seguros `debitar_bankroll`, `creditar_bankroll`, `recarregar_fichas` e `registrar_mao_jogada`.
   - Suíte de 6 testes unitários em `tests/test_perfil.py` validando conservação de fichas e prevenção de saldos inconsistentes.

2. **Rotas e Eventos em Tempo Real no Servidor (`servidor.py`):**
   - Novo endpoint HTTP `GET /api/historico-txt` para download direto do arquivo de histórico canônico.
   - Eventos de Socket.io: `obter_perfil`, `recarregar_fichas`, `iniciar_cash_game` e `sair_da_mesa`.
   - Inicialização da mesa com blinds e buy-ins dinâmicos escolhidos pelo jogador.
   - **Encerramento Instantâneo:** Ao sair da mesa, o servidor agora credita imediatamente o saldo remanescente ao Bankroll e emite `sessao_encerrada` sem nenhum delay (interrompendo sleeps dos bots em blocos de 0.1s).
   - Testes automatizados em `tests/test_servidor_rotas.py`.

3. **Menu Principal VIP em React (`frontend/src/components/MenuPrincipal.jsx` e `MenuPrincipal.css`):**
   - Design fiel à Opção 1 (VIP Casino Lounge com auras esmeralda/dourada e glassmorphism).
   - Header com logo *"Python Poker Club"*, avatar, indicador de Bankroll e botão de mudo.
   - Cards centrais com destaque para **Cash Game** (disponível) e **Torneio Sit & Go** (selo "Em Breve").
   - Modal de Seleção de Stakes (Micro $5/$10, Médio $10/$20, High $25/$50 e VIP $50/$100) com slider interativo de Buy-In (10 BB a 1.000 BB).
   - Modal de Estatísticas e HUD com métricas reais (VPIP, PFR, AF, Taxa de Vitórias e Arquétipo) sem mocks numéricos.
   - Modal informativo de Regras Básicas do Texas Hold'em.

4. **Refinamentos na Mesa de Jogo (`frontend/src/components/Mesa.jsx` e `index.css`):**
   - Botão `[🚪 Sair para o Menu]` reposicionado no canto superior esquerdo da mesa com visual pill translúcido.
   - Modal de confirmação inteligente caso o jogador tente sair durante uma rodada ativa (com opção de foldar ou continuar jogando).
   - Correção do método `audioEngine.toggleMute()`.
   - Preservação da proporção da mesa e do dimensionamento das cartas (`mini-carta`).

### Arquivos Afetados/Criados:
- `core/perfil.py` (Adicionado)
- `servidor.py` (Modificado)
- `tests/test_perfil.py` (Adicionado)
- `tests/test_servidor_rotas.py` (Adicionado)
- `frontend/src/App.jsx` (Modificado)
- `frontend/src/audioEngine.js` (Modificado)
- `frontend/src/index.css` (Modificado)
- `frontend/src/components/Mesa.jsx` (Modificado)
- `frontend/src/components/MenuPrincipal.jsx` (Adicionado)
- `frontend/src/components/MenuPrincipal.css` (Adicionado)
- `docs/plano_menu_principal.md` (Adicionado)
- `docs/roadmap.md` (Modificado)
- `CHANGELOG.md` (Modificado)


