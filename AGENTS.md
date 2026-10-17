# Regras do Projeto (Workspace Rules)

## 1. Regras Estritas de Git e Operações Remotas
- **NUNCA executar `git push` sob nenhuma circunstância.** O comando `git push` fica travado esperando autenticação ou permissão em segundo plano e bloqueia a execução.
- O assistente NUNCA deve rodar `git push` por conta própria.
- Fazer commits locais atômicos e semânticos (ex: `feat:`, `fix:`, `docs:`, `style:`) e apenas informar o usuário para que ele mesmo faça o `git push` no terminal quando desejar.

## 2. Bateria de Testes Automatizados (Criação e Execução Obrigatória)
- **Foco no Backend:** O motor de regras e economia reside no Python (`core/`). Todos os testes automatizados devem ser mantidos e centralizados na pasta `tests/`.
- **Testes para Novas Features:** Sempre que uma nova regra de aposta, lógica de pote ou mecânica de jogo for adicionada, criar testes unitários correspondentes validando os cenários esperados e casos de borda.
- **Política Anti-Regressão (Bugs):** Para cada bug corrigido, criar obrigatoriamente um teste que reproduza a falha corrigida.
- **Execução Obrigatória:** O assistente DEVE executar a suite de testes no terminal (`python -m unittest discover tests` ou arquivos específicos) após qualquer alteração no motor do jogo para garantir 100% de sucesso antes de dar a tarefa por concluída.

## 3. Princípio da Conservação de Fichas (Soma Zero)
- Em qualquer transação de apostas ou divisão de potes:
  $$\sum \text{Stacks dos Jogadores} + \text{Potes} + \text{Apostas na Mesa} = \text{Constante (Soma Zero)}$$
- Nenhuma ficha pode surgir do nada ou sumir do jogo sem motivo econômico rastreado (como um rebuy intencional).

## 4. Isolamento do Motor (Core Puro)
- O pacote `core/` (mesa, jogador, baralho, avaliador) NUNCA deve importar bibliotecas de rede ou interface (`flask`, `socketio`, etc.).
- O motor deve permanecer determinístico, isolado e testável em milissegundos sem necessidade de servidor web ativo.

## 5. Documentação Viva
- Ao concluir recursos importantes ou marcos do projeto, atualizar o `CHANGELOG.md` e sincronizar o status no `docs/roadmap.md`.
