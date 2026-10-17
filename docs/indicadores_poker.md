# Indicadores de Poker e Análise de Desempenho (Cash Game vs Torneios)

Este documento registra a matriz estratégica de indicadores estatísticos de Poker, suas definições matemáticas, relevância por modalidade e a arquitetura de armazenamento para análise de desempenho e calibração de Inteligências Artificiais.

---

## 1. Matriz de Indicadores: Cash Game vs Torneio (MTT/SNG)

| Indicador | O que mede | Cash Game | Torneio (MTT/SNG) | Fórmula / Critério |
| :--- | :--- | :--- | :--- | :--- |
| **VPIP** *(Voluntarily Put $ in Pot)* | % de vezes que o jogador coloca fichas no pote pré-flop por vontade própria (exclui check no Big Blind). | **Essencial** (Geralmente 20% a 28% em mesas 6-max). | **Dinâmico** (Varia radicalmente da fase inicial deep stack para a fase de short stack/bolha). | `(Mãos com Call ou Raise Pré-Flop) / (Total de Mãos Ativas)` |
| **PFR** *(Pre-Flop Raise)* | % de vezes que entra no pote aplicando aumento (raise). | **Essencial**. A diferença entre VPIP e PFR identifica o arquétipo do jogador: Passivo (Calling Station) vs Agressivo (TAG/LAG). | **Essencial**. Mede a agressividade de abertura de ranges e roubo de blinds. | `(Mãos com Raise Pré-Flop) / (Total de Mãos Ativas)` |
| **3-Bet %** | % de vezes que reaumenta contra um raise pré-flop já existente. | **Crítico** para diagnosticar agressividade em posição e frequência de blefes pré-flop. | Importante, mas muito condicionado a faixas de Stack Efetivo e All-In direto. | `(Vezes que fez 3-Bet) / (Oportunidades de 3-Bet)` |
| **WTSD %** *(Went To Showdown)* | % de vezes que, após ver o Flop, segue até o Showdown final sem desistir. | **Diagnóstico de Teimosia:** se for > 35%, indica tendência a pagar apostas pesadas com pares baixos/médios. | Afetado por All-in pré-flop (onde não há decisão pós-flop). | `(Vezes que viu Showdown) / (Vezes que viu o Flop)` |
| **W$SD %** *(Won $ at Showdown)* | % de vezes que ganha fichas quando a mão chega ao Showdown. | **Validador de Lucratividade:** Se WTSD for alto (>35%) e W$SD for baixo (<45%), o jogador está pagando com mãos perdedoras. | Idem. | `(Showdowns Ganhos) / (Total de Showdowns Disputados)` |
| **AF / AFq** *(Aggression Factor / Frequency)* | Proporção de agressão pós-flop: medir se o jogador tenta vencer apostando ou se é puramente passivo. | **Fundamental:** Separa jogadores que lideram a mesa daqueles que só "pagam para ver". | **Importante.** | `(Total Bets + Total Raises) / (Total Calls)` |
| **C-Bet Flop %** *(Continuation Bet)* | % de vezes que o agressor pré-flop dispara uma aposta no Flop. | **Indispensável:** Revela se aposta por padrão ou apenas quando conecta acertando o bordo. | **Indispensável.** | `(C-Bets no Flop) / (Oportunidades de C-Bet como agressor pré-flop)` |
| **Fold to C-Bet %** | % de vezes que o jogador desiste quando o oponente aplica uma C-Bet. | **Mina de Ouro Estratégica:** Se > 60-70%, a IA aprende a apostar 100% dos flops contra ele lucrativamente. | Idem. | `(Folds para C-Bet no Flop) / (Vezes que enfrentou C-Bet no Flop)` |
| **BB/100** *(Big Blinds / 100 mãos)* | Taxa de ganho normalizada por volume de jogo. | **A métrica suprema do Cash Game.** Mede rentabilidade sem distorção pelo valor absoluto das fichas. | **Não aplicável.** Fichas de torneio não têm valor linear por causa do ICM. | `(Lucro Líquido em Fichas / Valor do Big Blind) * (100 / Total de Mãos)` |
| **ROI % / ITM %** *(Return on Investment / In The Money)* | Retorno financeiro sobre buy-ins e frequência de entrada na zona de premiação. | **Não existe em Cash Game** (entradas e saídas são instantâneas em dinheiro/fichas). | **A métrica suprema de Torneios.** Mede consistência e profundidade de premiação. | `ROI = ((Premiação Total - Buyins) / Buyins) * 100` |
| **ICM Pressure / Bubble Factor** | Modelo Independente de Fichas: peso monetário de perder fichas vs ganhar fichas. | Zero relevância (rebuys imediatos). | **Crítico na fase de bolha e mesa final.** Modifica ranges de All-in e Call matematicamente. | Cálculo ponderado pela distribuição de prêmios da grade do torneio. |

---

## 2. Padrões de Arquétipos de Jogadores (Identificação via Métricas)

Com base na relação **VPIP vs PFR vs AF**, o motor de análise classifica automaticamente qualquer adversário:

1. **Tight-Aggressive (TAG) - O Tubarão Padrão:**
   - *VPIP:* 18% - 25%
   - *PFR:* 15% - 22% (Diferença pequena para o VPIP)
   - *AF:* 2.5 - 4.0
   - *Comportamento:* Joga apenas mãos fortes, raramente apenas paga (dá raise), aposta por valor e sabe quando largar.

2. **Loose-Passive (Calling Station) - O Pato Favorito:**
   - *VPIP:* 35% - 60%+
   - *PFR:* 5% - 12% (Grande abismo entre VPIP e PFR)
   - *AF:* < 1.5
   - *Comportamento:* Quer ver quase todos os flops pagando o blind, não aumenta, odeia foldar e paga até o River com qualquer pedaço de par.

3. **Loose-Aggressive (LAG) - O Maníaco / Pressão:**
   - *VPIP:* 30% - 45%
   - *PFR:* 25% - 38%
   - *AF:* > 4.0
   - *Comportamento:* Blefa em alta frequência, aplica 3-bets frequentes em posição e tenta expulsar adversários do pote.

4. **Nit / Rock - O Ultra Conservador:**
   - *VPIP:* < 15%
   - *PFR:* < 12%
   - *Comportamento:* Só entra com topo de range (AA, KK, AK). Muito previsível; fácil de foldar contra as apostas dele.

---

## 3. Aplicação no Projeto
- **Calibração do Algoritmo Genético:** Gerar instâncias virtuais com esses exatos perfis para treinar os bots.
- **HUD em Tempo Real (Heads-Up Display):** Exibir caixinhas flutuantes ao lado dos avatares (`VPIP / PFR / AF`) durante a partida web.
- **Relatórios de Sessão:** Apontar no final da sessão do usuário humano onde estão os maiores *leaks* (vazamentos de fichas).
