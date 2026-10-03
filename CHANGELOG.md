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
- Arquivos de configuração de potes/turnos modificados no pacote `core/`.
