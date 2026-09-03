# Roadmap do Poker em Python (v2.0 e Futuro)

Este documento guarda as diretrizes, otimizações e novas funcionalidades que devem ser implementadas no projeto nas futuras atualizações com auxílio de IA.

## 1. Otimização do `AvaliadorDeMaos` (Performance / Monte Carlo)
O avaliador atual possui lógica perfeita para regras e desempates, mas não está otimizado para simulações de milhões de cenários.

**Problema atual:**
As funções iteram múltiplas vezes pela mesma mão (`O(N)`) e chamam `sorted()` dezenas de vezes para checar as mãos possíveis do maior para o menor.

**Solução (Mapas de Frequência):**
- **Extração única:** A mão de 7 cartas deve ser lida apenas 1 vez (O(N)).
- **Histograma de Valores (Hash Map):** Criar um dicionário/array que conte a frequência de cartas (ex: `{'A': 2, 'K': 1}`). Isso permite achar quadras, trincas e pares em `O(1)`.
- **Histograma de Naipes:** Dicionário que conta os naipes, tornando o reconhecimento de Flushes instantâneo em `O(1)`.
- **Bitmasks / Lookup Tables:** Para simulações ainda mais extremas, migrar para avaliação bit-a-bit (Cactus Kev / TwoPlusTwo).

## 2. Sistema de Apostas e Motor do Jogo
Para que o jogo seja completo, precisamos ir além de comparar quem ganha e quem perde, e implementar a "Economia" do jogo.
- **Estruturas de Apostas:** Lógica para Blind (Small/Big), Call, Raise (com regras matemáticas de tamanho mínimo), Check e Fold.
- **Gerenciamento do Pote (Pot Management):** Somar fichas e transferir para o ganhador.
- **Divisão de Potes (Side Pots e Split Pots):** Esse é um dos maiores desafios lógicos! Lidar com empates (Split Pot) e principalmente com cenários de All-In (Side Pots). Por exemplo: Se o jogador A aposta 100, B paga 100, mas C tem apenas 50 e dá All-in. Precisamos criar o "Pote Principal" de 150 (disputado pelos três) e o "Side Pot" de 100 (disputado apenas por A e B).

## 3. Construção de um "Bot/AI" Adversário
Implementar um agente inteligente capaz de jogar contra um usuário humano. 

**Como fazer um bot forte no Poker:**
Como nosso simulador (`app.py`) já tem suporte a "Simulações de Equidade", o bot usará **Simulação de Monte Carlo** no momento de sua decisão:
1. O bot olha suas próprias 2 cartas e as cartas da mesa.
2. Ele projeta 10.000 cenários aleatórios de possíveis cartas para o oponente e para o resto da mesa.
3. Se a "Equidade" dele (porcentagem de vitória) for alta, ele aposta/aumenta.
4. Se for média, ele paga (call).
5. Se for muito baixa, ele foge (fold).

Esse comportamento matemático, alinhado ao conceito de *Expected Value (EV)*, criará um adversário duro na queda e matematicamente correto na maior parte das decisões!

## 4. Interface de Jogo (Front-end)
- Evoluir o Streamlit (`app.py`) de uma ferramenta de simulação de equidade (Calculadora) para um jogo real por turnos (Pré-Flop, Flop, Turn, River).
- Manter o histórico de apostas (Pote).

## 5. PokerStars Hand History Parser (Analisador de Histórico)
Criar um módulo capaz de ler os arquivos de texto (`.txt`) gerados pelo PokerStars contendo o histórico de mãos jogadas pelo usuário.
- **Leitura e Parsing:** Extrair dados de apostas, cartas, tamanhos de pote e posição dos jogadores a partir do texto puro do PokerStars.
- **Integração com Monte Carlo:** Rodar nosso próprio motor de simulação por baixo dos panos para avaliar se as jogadas feitas pelo usuário no passado tiveram EV Positivo ou Negativo.
- **Dashboards:** Criar gráficos e tabelas no Streamlit mostrando vazamentos no jogo (leaks), taxa de vitórias com certas mãos, e sugerindo correções baseadas em matemática.

## 6. Mentor de Poker com LLM (Integração de IA Generativa)
Enviar o sumário da análise matemática do Monte Carlo + o histórico da mão para uma API de IA (como o Gemini) com um prompt de sistema configurado para atuar como um **Professor Profissional de Poker**.
- A IA vai explicar em linguagem natural por que uma jogada foi ruim ou boa.
- Criar relatórios de sessão ("Aulas") textuais focadas nas maiores fraquezas detectadas matematicamente na sessão do jogador.
