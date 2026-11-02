# Roteiro - Vídeo 3: Do Tabuleiro Solto a um Cassino VIP Completo! (Lobby VIP, Modo Cash Game, Bankroll no SQLite e Modo Espectador)

---

## 📋 Ficha Técnica do Vídeo

* **Tema:** A maior evolução visual e de engenharia do projeto até agora: Criação do Lobby VIP estilo Cassino de Luxo, sistema econômico unificado e persistente com SQLite (Princípio de Conservação de Fichas), Modo Cash Game dinâmico (Blinds de Micro a High Roller), aceleração do ritmo dos Bots para gameplay ágil, e as mecânicas inovadoras de **"Levantar da Mesa" (Modo Espectador)** e **"Sentar no Assento Vago"** com animação interativa.
* **Duração Estimada:** 14 a 18 minutos.
* **Tom do Vídeo:** Muito empolgado, didático, técnico e visual (estilo *Devlog indie premium*, com demonstração prática em tempo real no navegador e inspeção de código no editor).

### 💡 Sugestões de Títulos Chamativos
1. **Opção 1 (Apelativa & Curiosa - Recomendada):** *TRANSFORMEI MEU POKER EM PYTHON NUM CASSINO VIP PROFISSIONAL! (Devlog #3)*
2. **Opção 2 (Focada em Engenharia/Gameplay):** *Criei um Modo Cash Game Completo com Bots Inteligentes e Modo Espectador em Python!*
3. **Opção 3 (Direta e Técnica):** *Devlog 03: Lobby VIP, Arquitetura de Bankroll com SQLite e Mesa Contínua em Python + React*

### 🎨 Ideias de Thumbnail
* **Conceito A (Impacto Visual Noturno):** A tela do Menu VIP com neon esmeralda e dourado em destaque; ao centro, você apontando para o botão *"CASH GAME"* com o badge *"DISPONÍVEL"*, e um balão de texto em amarelo: *"PARECE CASSINO DE VERDADE?!"*.
* **Conceito B (A Mágica do Espectador):** Split da mesa mostrando a sua cadeira vazia com a seta pulsante dourada `⬇ LUGAR LIVRE - CLIQUE PARA SENTAR` enquanto os 3 bots disputam um pote de $50.000 ao fundo, com a legenda: *"LEVANTEI E ELES CONTINUAM JOGANDO?!"*.

---

## 🛠️ Checklist de Preparação (Antes de Gravar!)

Deixe tudo engatilhado nas suas abas e janelas para a gravação fluir perfeitamente:

1. **Aba 1 (Seu Jogo):** Servidor Python rodando (`python servidor.py`) e frontend Vite em `http://localhost:5173`.
   * **Importante:** Inicie a gravação com o saldo do seu perfil em **$100.000** (já resetado para demonstrar os cálculos matemáticos exatos no vídeo!).
2. **Aviso de Compliance Automático:** O badge oficial no cabeçalho (*"PROJETO EDUCACIONAL • SIMULAÇÃO DE IA • SEM DINHEIRO REAL"*) já está visível tanto no Lobby quanto na mesa. Destaque-o nos primeiros 40 segundos para evitar qualquer restrição do YouTube.
3. **Áudio do Sistema no OBS:** Verifique se os efeitos sonoros das cartas e das fichas de cerâmica estão com volume agradável.
4. **Janela do VS Code / Editor:**
   * `servidor.py` (aberto na seção `CONFIG_TEMPOS` e `mesa_lock`).
   * `docs/tempos_e_dinamica_de_jogo.md`.
   * `core/perfil.py`.
5. **Terminal:** Pronto para mostrar os testes automatizados passando:
   ```powershell
   python -m unittest tests/test_perfil.py tests/test_servidor_rotas.py tests/test_bordas.py
   ```

---

## ⏱️ Estrutura & Minutagem do Vídeo

```text
00:00 - 02:00 | Bloco 1: Abertura, Disclaimer de Compliance & O Choque do Novo Lobby VIP
02:00 - 04:30 | Bloco 2: A Arquitetura do Banco SQLite & O Princípio de Conservação Econômica
04:30 - 07:00 | Bloco 3: Configuração do Cash Game (Blinds de $5/$10 a $50/$100 e Slider Dinâmico)
07:00 - 09:45 | Bloco 4: Gameplay na Mesa: O Novo Ritmo dos Bots (83% em 1-3s) e All-in com Suspense
09:45 - 12:30 | Bloco 5: O Pulo do Gato: O Botão "Levantar da Mesa" e o Modo Espectador em Ação
12:30 - 14:45 | Bloco 6: O Assento Livre Dinâmico & A Mágica de Sentar Novamente
14:45 - 16:30 | Bloco 7: Rebuy Inteligente sem Travar a Partida & Saída com Saldo Protegido
16:30 - 18:00 | Bloco 8: Testes de Borda, Próximo Passo (Torneio Mata-Mata) & Conclusão
```

---

## 🎬 Roteiro Detalhado Passo a Passo

---

### Bloco 1: Abertura & O Choque do Novo Lobby VIP (00:00 - 02:00)

**[O que mostrar na tela]:**
* *Câmera frontal com um corte rápido mostrando o visual incrível do novo Menu Principal (`localhost:5173`) com neon esmeralda, detalhes dourados e vidro fosco (glassmorphism).*

**[Fala sugerida]:**
> "Fala, pessoal! Sejam muito bem-vindos ao terceiro episódio do nosso devlog construindo um software profissional de Poker do absoluto zero com Python e React!
>
> *(Aviso Obrigatório de Compliance nos primeiros segundos):*
> **Como sempre, vale reforçar com clareza: este é um projeto 100% didático e acadêmico de ciência da computação e inteligência artificial. Não existe nenhuma aposta ou dinheiro real envolvido: todas as moedas e fichas são estritamente fictícias para simulação de algoritmos.**
>
> Pessoal, se no vídeo passado nós colocamos alma no jogo com efeitos sonoros de estúdio e histórico canônico do PokerStars... hoje nós demos o **maior salto de qualidade de todo o canal**.
>
> Dá uma olhada nessa tela inicial! *(Mostre o MenuPrincipal em tela cheia)*.
> Nós saímos daquele protótipo onde a partida iniciava do nada em uma mesa isolada e construímos um **Lobby VIP de Cassino completo**. 
> Temos um cabeçalho com a nossa marca 'Python Poker Club', controle de áudio, carteira global do jogador, painel de estatísticas com arquétipo de jogo em tempo real, e a seleção dos dois grandes modos: o **Modo Cash Game**, que está 100% pronto e polido, e o card de **Torneio Sit & Go**, que é o nosso próximo grande marco!
>
> Mas o que tem por trás dessa beleza visual é onde a verdadeira engenharia acontece: nós implementamos um sistema de persistência com banco de dados SQLite, um fluxo rigoroso de conservação de fichas e duas mecânicas que vocês me pediram muito: o **Modo Espectador** com botão de **Levantar da Mesa** e o **Assento Livre com reentrada dinâmica**!
>
> Prepara o café, deixa aquele like maroto e bora ver tudo funcionando!"

---

### Bloco 2: A Arquitetura do Banco SQLite & Conservação Econômica (02:00 - 04:30)

**[O que mostrar na tela]:**
* *Abra o editor no arquivo `core/perfil.py` e depois mostre o card de saldo no topo do menu (`$100,000`).*

**[Fala sugerida]:**
> "Antes de sentar na mesa, deixa eu explicar como nós resolvemos um dos maiores desafios de arquitetura de jogos de cartas: **a gestão do saldo (Bankroll)**.
>
> Até o vídeo passado, as fichas existiam apenas na memória RAM enquanto a partida rodava. Se reiniciasse o servidor, tudo sumia.
> Agora, criamos o `GerenciadorPerfil` em Python puro com SQLite unificado.
>
> Mas tem uma regra de ouro em engenharia de jogos de cassino: **O Princípio de Conservação de Fichas (Zero-Sum Chip Conservation)**:
> $\text{Bankroll no Cofre} + \text{Fichas na Mesa} = \text{Total Constante}$
>
> Vejam como funciona na prática:
> 1. Aqui no topo do menu, o meu perfil começa com **$100.000** no cofre.
> 2. No momento em que eu escolho sentar no Cash Game com **$10.000**, o backend debita imediatamente o cofre no SQLite: o meu saldo no banco vai para **$90.000** e a mesa abre com **$10.000** na minha frente.
> 3. Durante as mãos, o meu dinheiro do banco fica intocado e 100% protegido. O que sobe e desce são apenas as fichas do meu stack na mesa.
> 4. E no momento em que eu decido sair da mesa ou me levantar, o backend faz o **Cash Out atômico**: pega qualquer centavo que sobrou na minha frente na mesa e credita de volta ao cofre com lock de thread para evitar qualquer condição de corrida.
>
> Vamos ver isso na prática agora mesmo!"

---

### Bloco 3: Configuração do Cash Game & Slider Interativo (04:30 - 07:00)

**[O que mostrar na tela]:**
* *No navegador, clique no botão dourado "JOGAR AGORA" do card de Cash Game.*
* *O modal de setup abre com animação suave.*
* *Mostre a seleção de mesas e mexa no slider de Buy-in.*

**[Fala sugerida]:**
> "Ao clicar em 'JOGAR AGORA', abre esse modal configurador inspirado nos melhores apps profissionais, como o RallyAces e PokerStars:
>
> Aqui nós temos **4 níveis de mesa**:
> * **Micro Stakes:** Blinds de $5 / $10 (entrada de $100 a $10.000).
> * **Médio Stakes:** Blinds de $10 / $20 (entrada de $200 a $20.000).
> * **High Stakes:** Blinds de $25 / $50.
> * **VIP High Roller:** Blinds pesados de $50 / $100.
>
> Cada mesa tem a regra clássica de Cash Game: você pode entrar com no mínimo **10 Big Blinds** e no máximo **1000 Big Blinds**.
> E nós criamos esse slider interativo com botões de atalho rápido:
> * Botão 'Mínimo (10 BB)': já calcula o piso exato da mesa selecionada.
> * Botão 'Padrão (100 BB)': o stack clássico de poker profissional.
> * Botão 'Máximo': respeita o limite do teto da mesa ou o total disponível no seu Bankroll!
>
> Eu vou selecionar a mesa de Médio Stakes ($10/$20) e vou entrar com exatamente **$10.000**.
> Prestem atenção: meu saldo atual é $100.000. Vou clicar em 'SENTAR NA MESA'!"

---

### Bloco 4: Gameplay na Mesa: O Novo Ritmo dos Bots & All-In com Suspense (07:00 - 09:45)

**[O que mostrar na tela]:**
* *A tela transiciona suavemente para a mesa de poker.*
* *Mostre o seu stack de $10.000.*
* *Jogue 1 ou 2 mãos contra os bots (ProBot_1, ProBot_2, ProBot_3).*
* *Destaque a velocidade ágil das ações dos bots.*

**[Fala sugerida]:**
> "Entramos na mesa! 
> Notem duas coisas fundamentais logo de cara:
> Primeiro: no canto superior esquerdo, a mesa está limpa e elegante. Nós temos apenas o botão discreto de saída e o novo botão **'↑ Levantar'**, sem poluição visual.
> 
> Segundo: reparem na velocidade dos bots agora!
> *(Aguarde o bot agir)*
> Viram como a resposta foi rápida? No vídeo passado os bots demoravam até 7 ou 8 segundos para dar um simples call ou check. Para testes e gravação de vídeo, ficava muito parado.
> 
> Então nós criamos um arquivo de configuração centralizado que eu documentei aqui:
> *(Mostrar rapidamente na tela o arquivo `docs/tempos_e_dinamica_de_jogo.md`)*
> Agora a IA usa uma distribuição probabilística muito mais realista:
> * **83% das vezes:** o bot responde em **1 a 3 segundos**. É uma ação rápida, natural, como um humano em mesas online.
> * **10% das vezes:** ele pensa entre **3 e 6 segundos** quando o pote aperta ou tem um raise.
> * **2% das vezes:** apenas em situações raras e extremas ele faz o 'tanking' de 6 a 9 segundos.
> * E **5% das vezes:** é aquele 'snap check' ou 'snap fold' imediato em menos de 1 segundo!
>
> E olhem quando rola uma situação de All-in:
> *(Se conseguir forçar ou demonstrar uma rodada de all-in)*
> Nós colocamos uma pausa dramática de 1.8 segundos entre o Flop, o Turn e o River! Nada de cuspir 5 cartas em 0 milissegundos. E no Showdown, a mesa congela por 3.5 segundos com as cartas abertas dos bots para que você consiga ver quem fez dois pares, quem fez trinca e quem levou o pote!"

---

### Bloco 5: O Pulo do Gato: Botão "Levantar da Mesa" e Modo Espectador (09:45 - 12:30)

**[O que mostrar na tela]:**
* *Demonstre o clique no botão `↑ Levantar`.*
* *Se estiver com cartas, mostre o modal de aviso de Fold e confirme.*
* *Veja as fichas sumindo da mesa e o badge `👁️ Modo Espectador` aparecendo no topo.*
* *Deixe os bots jogarem uma mão completa sozinhos na tela.*

**[Fala sugerida]:**
> "Agora vem o recurso que eu mais tinha vontade de implementar e que deixa esse projeto com cara de software profissional de verdade: **O Botão de Levantar da Mesa**.
>
> Imagine a cena: você está jogando, acumulou fichas, mas quer parar de jogar por alguns minutos para tomar uma água ou simplesmente quer ficar assistindo a Inteligência Artificial disputar entre si para analisar como os bots jogam.
> Em jogos simples, ou você joga ou é chutado pro menu. Aqui não!
>
> Vejam aqui no topo esquerdo esse botão com uma seta para cima: **`↑ Levantar`**.
> Vou clicar nele:
> *(Se estiver no meio de uma mão, mostre o modal de alerta: 'Você está disputando a rodada atual! Se levantar agora, você dará FOLD...').*
> O sistema te protege contra cliques acidentais! Se você confirmar:
> *(Clique em 'Sim, Levantar')*
> 
> Olha o que aconteceu!
> 1. Minhas fichas da mesa foram imediatamente transferidas de volta para o meu saldo no banco de dados SQLite.
> 2. No topo da tela apareceu o badge azul neon: **`👁️ Modo Espectador`**.
> 3. E olhem para a mesa agora! **A partida NÃO parou!** 
> Os bots estão disputando as mãos autonomamente, trocando apostas, virando flop, turn, river e dividindo potes, enquanto eu estou tranquilamente como espectador assistindo o show da IA!"

---

### Bloco 6: O Assento Livre Interativo & O Retorno à Partida (12:30 - 14:45)

**[O que mostrar na tela]:**
* *Aponte para a posição inferior da mesa (posição 0).*
* *Passe o cursor sobre a moldura tracejada dourada e mostre a seta animada `⬇`.*
* *Clique no assento livre, abra o modal de entrada, escolha novo buy-in e confirme.*
* *Aguarde o início da próxima mão e receba cartas.*

**[Fala sugerida]:**
> "E olhem para onde ficava o meu jogador na mesa:
> Ao invés de ficar um card fantasma ou uma tela quebrada, nós criamos um asset de **Assento Vago** em CSS e Framer Motion:
> É essa moldura VIP tracejada em dourado fosco, com uma seta animada pulsando para baixo e o convite: **`⬇ LUGAR LIVRE - CLIQUE PARA SENTAR`**.
> 
> E tudo centralizado perfeitamente, sem nenhum salto ou bug de layout.
> Agora, imagine que eu assisti algumas mãos e decidi voltar para o jogo. O que eu faço?
> Eu simplesmente clico em cima da cadeira vazia!
> *(Clique no assento vago)*
> 
> Imediatamente abre o modal **'🎰 Sentar na Mesa'**!
> Ele consulta o meu saldo atual no cofre, me dá o slider de 10 a 1000 BBs com presets rápidos, e eu posso escolher entrar, por exemplo, com $5.000 ou $15.000.
> Vou escolher **$10.000** e clicar em 'SENTAR NA MESA ▶'.
>
> Vejam a mensagem no chat da transmissão:
> *'Você sentou na mesa com $10.000! Você entrará na próxima rodada.'*
> O sistema não quebra a mão que os bots já estavam jogando. Ele aguarda a mão dos bots terminar e, assim que o dealer distribui a próxima rodada...
> *(Espere a mão começar)*
> **BUM!** Eu recebo duas cartas fechadas, o meu stack está ativo na mesa e eu voltei a disputar como jogador normalmente!"

---

### Bloco 7: Rebuy Inteligente & Saída com Saldo Protegido (14:45 - 16:30)

**[O que mostrar na tela]:**
* *Explique o que acontece se o jogador perder tudo (All-in).*
* *Mostre o botão `← Sair para o Menu`.*
* *Clique em sair e mostre a transição de volta para o Lobby Principal com o saldo recalculado perfeitamente.*

**[Fala sugerida]:**
> "E tem mais: o que acontece se você der um All-in e perder todas as suas fichas na mesa?
> Antigamente, dava um alert tosco do navegador e o jogo congelava.
> Agora não:
> 1. A mesa aguarda o showdown e mostra quem ganhou.
> 2. Se o seu stack zerar, abre um **Modal VIP de Rebuy** na sua frente.
> 3. Se você quiser comprar mais fichas, escolhe o valor e reentra na próxima mão.
> 4. E se você recusar o Rebuy e clicar em 'Voltar ao Menu', ele encerra a sessão com elegância e te leva direto para o Lobby Principal, sem travar nada!
>
> Agora vamos testar o Cash Out total:
> Vou clicar em **'← Sair para o Menu'**:
> *(Clique em sair)*
> Vejam: a sessão é encerrada em 0 milissegundos, as fichas da mesa foram transferidas para o perfil e estamos de volta ao Lobby VIP com cada centavo 100% preservado no nosso banco de dados SQLite!"

---

### Bloco 8: Testes de Borda, Próximo Passo & Encerramento (16:30 - 18:00)

**[O que mostrar na tela]:**
* *Abra o terminal do VS Code e rode os testes unitários:*
  ```powershell
  python -m unittest tests/test_perfil.py tests/test_servidor_rotas.py tests/test_bordas.py
  ```
* *Mostre os 24 testes passando com OK.*
* *Volte para a câmera frontal com a tela do jogo ao fundo.*

**[Fala sugerida]:**
> "E para os apaixonados por qualidade de código e engenharia de software como eu: nada disso foi feito no improviso.
> Dá uma olhada no nosso terminal de testes:
> *(Execute os testes)*
> São **24 testes unitários e de casos de borda** cobrindo:
> * Conservação econômica estrita (Stack + Bankroll = Constante).
> * Jogador levantando no meio de mão com aposta ativa e fold seguro.
> * Tentativas de sentar com valores abaixo do mínimo ou acima do teto da mesa.
> * Débito no limite exato do saldo.
> * E concorrência de eventos de socket com locks de thread.
> Todos os 24 testes passando redondos em menos de 1 segundo!
>
> Agora o nosso Cash Game está **100% finalizado, robusto e com qualidade comercial**.
> E isso abre as portas para o nosso próximo grande desafio no Canal:
> **O Modo Torneio Sit & Go Mata-Mata!**
> No próximo vídeo, nós vamos implementar:
> * Buy-In único com stacks idênticos para todos os 4 jogadores.
> * Estrutura periódica de subida de Blinds (a cada 3 ou 5 minutos a mesa aperta!).
> * Eliminação direta ao zerar as fichas (sem rebuy).
> * E um pódio glorioso com troféu para o sobrevivente da mesa final!
>
> Me digam aqui nos comentários: o que acharam dessa nova cara do jogo? O que você gostaria de ver nos bots para o modo torneio?
> Não esquece de deixar o seu like, compartilhar com a galera de tecnologia e Python, e até o próximo vídeo!"

---

