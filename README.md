# Simulador de Poker em Python 🃏

Este é um projeto de simulação de Poker em Python criado para representar toda a lógica do jogo: cartas, baralho, jogadores, mesa, identificação de mãos (pares, flushes, sequências) e algoritmos precisos de desempate.

## 🎯 Objetivo do Projeto
A ideia principal é construir um motor de poker completo e otimizado, capaz de não apenas jogar rodadas normais no terminal ou via interface gráfica, mas também atuar como um **Simulador de Probabilidades (Monte Carlo)** de alto desempenho, podendo avaliar milhões de cenários em poucos segundos.

## 📁 Estrutura do Projeto

O projeto adota uma arquitetura modular focada em separação de responsabilidades:

- `core/` : O "motor" do jogo. Contém todas as classes fundamentais (`mesa.py`, `carta.py`, `jogador.py`) e os avaliadores de mãos (`avaliador_de_maos.py` e `avaliador_otimizado.py`).
- `app/` : Componentes visuais e de interface (como o aplicativo web usando Streamlit).
- `benchmarks/` : Scripts rigorosos para medir a performance e a velocidade dos algoritmos em cenários extremos (ex: 5 milhões de mãos).
- `tests/` : Scripts de validação para garantir que os cálculos de empate e força das mãos estão perfeitos.
- `docs/` : Documentação do projeto, incluindo o nosso `roadmap.md` de evolução contínua e análises técnicas.
- `main.py` : O ponto de entrada interativo para rodar o jogo e as simulações diretamente via Terminal.

## 🚀 Como Executar

Para rodar o jogo de forma interativa no seu terminal, basta executar:
```bash
python main.py
```

## 📜 Histórico de Atualizações
Para mais detalhes sobre as atualizações técnicas e otimizações, consulte o arquivo `CHANGELOG.md`.

- **Setembro/2026**: Implementação de algoritmos *Single-Pass* e *Bitwise* para avaliação ultra-rápida de mãos, atingindo mais de 200.000 avaliações por segundo. Criação de arquitetura híbrida de desempate e reorganização modular da estrutura de diretórios do projeto.
- **Maio/2024**: Implementação robusta dos algoritmos de desempate de pares e identificação das 5 melhores cartas de um jogador na mesa.

[poker_python: Programa de simular Poker, a ideia é fazer todas classes que representam cartas,
baralho, jogadores, mesa, etc. Fazer funções que identificam qual a classificação da mão do jogador
para aquela rodada, quais são as 5 combinações de cartas do jogador que resulta na melhor mão naquela
rodada, desempate de jogadores, entre muitas outras coisas que irei desenvolvendo que eu achar interessante.

Dia 27/04/2024: Consegui realizar completamente o desempate do par, ou seja, agora ele consegue indicar certinho quais jogadores ganharam aquela rodada a partir de um empate de várias pessoas com um par. Agora é desenvolver o desempate para cada uma das mãos existentes e depois lembrar de pensar em como fazer para imprimir sempre ao lado da mensagem dos vencedores, qual foi a combinação de cinco cartas que resultou na melhor mão da rodada, depois disso tudo, lembrar de otimizar e 
modularizar tudo. Também realizei muitos comentários explicativos do passo a passo do desempate de pares]