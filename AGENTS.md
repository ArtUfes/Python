# Regras do Projeto (Workspace Rules)

## Regras Estritas de Git e Operações Remotas
- **NUNCA executar `git push` sob nenhuma circunstância.** O comando `git push` fica travado esperando autenticação ou permissão em segundo plano e bloqueia a execução.
- O assistente NUNCA deve rodar `git push` por conta própria.
- Quando arquivos forem alterados ou commitados, apenas informe o usuário para que ele mesmo execute `git push` no terminal quando desejar.
