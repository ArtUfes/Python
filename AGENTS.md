# Regras do Projeto (Workspace Rules)

## 1. Regras Estritas de Git e Fluxo de Commit
- **NUNCA executar `git push` sob nenhuma circunstância.** O comando `git push` fica travado esperando autenticação ou permissão em segundo plano e bloqueia a execução. O envio remoto é estritamente manual pelo usuário no terminal.
- **NÃO comitar imediatamente após terminar o código:** O assistente NUNCA deve fazer `git commit` de forma precipitada logo ao finalizar alterações.
- **Fluxo Obrigatório de Validação:**
  1. O assistente implementa o código e cria/atualiza os testes unitários.
  2. Executa a suíte de testes automatizados no terminal para garantir que não há regressões.
  3. Apresenta o resultado e resumo das alterações ao usuário.
  4. **Aguardar a validação e teste prático pelo usuário.**
  5. Somente após a confirmação/aprovação explícita do usuário, o assistente realiza o `git commit` local atômico e semântico (`feat:`, `fix:`, `test:`, `docs:`, `style:`, `refactor:`).

## 2. Bateria de Testes Automatizados (Criação e Execução Obrigatória)
- **Foco no Backend:** O motor de regras e economia reside no Python (`core/`). Todos os testes automatizados devem ser mantidos e centralizados na pasta `tests/`.
- **Testes para Novas Features:** Sempre que uma nova regra de aposta, lógica de pote ou mecânica de jogo for adicionada, criar testes unitários correspondentes validando os cenários esperados e casos de borda.
- **Política Anti-Regressão (Bugs):** Para cada bug corrigido, criar obrigatoriamente um teste que reproduza a falha corrigida.
- **Execução Obrigatória:** O assistente DEVE executar a suite de testes no terminal (`python -m unittest discover tests` ou arquivos específicos) após qualquer alteração no motor do jogo para garantir 100% de sucesso antes de dar a tarefa por concluída.
- **Determinismo e Seeds:** Qualquer teste que envolva embaralhamento, cartas aleatórias ou simulação DEVE definir semente estática (ex: `random.seed(...)`) para garantir total reprodutibilidade e evitar testes intermitentes (*flaky tests*).

## 3. Princípio da Conservação de Fichas (Soma Zero)
- Em qualquer transação de apostas ou divisão de potes:
  $$\sum \text{Stacks dos Jogadores} + \text{Potes} + \text{Apostas na Mesa} = \text{Constante (Soma Zero)}$$
- Nenhuma ficha pode surgir do nada ou sumir do jogo sem motivo econômico rastreado (como um rebuy intencional).

## 4. Isolamento do Motor (Core Puro)
- O pacote `core/` (mesa, jogador, baralho, avaliador) NUNCA deve importar bibliotecas de rede ou interface (`flask`, `socketio`, etc.).
- O motor deve permanecer determinístico, isolado e testável em milissegundos sem necessidade de servidor web ativo.

## 5. Padrões do Frontend (Interface Web)
- O frontend reside na pasta `frontend/`, desenvolvido em React + Vite utilizando Vanilla CSS puro (sem Tailwind ou frameworks de terceiros).
- Qualquer modificação visual deve preservar a identidade visual existente (tons escuros, feltro verde, detalhes dourados) e a proporção da mesa.
- Nunca sobrepor elementos de controle (botões de aposta/ação, avatares) ou badges regulatórias (disclaimer anti-restrição de idade / sem dinheiro real).

## 6. Documentação Viva
- Ao concluir recursos importantes ou marcos do projeto (e após aprovação do usuário), atualizar o `CHANGELOG.md` e sincronizar o status no `docs/roadmap.md`.
