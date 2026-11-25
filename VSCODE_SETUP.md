# VS Code — Auxiliar PJ

Abra a pasta raiz de `auxiliar-NF-pj` no VS Code. Instale Git e SDK .NET 8 e confirme `git --version` e `dotnet --version` no terminal. Python e Swift são opcionais, para seus módulos específicos. Não há dependência de Node.js.

## Executar e testar

Execute `scripts\iniciar-local.cmd` ou siga o [guia rápido](GUIA_RAPIDO.md) para gerar os dois tokens e iniciar a aplicação. Abra http://127.0.0.1:5000/; o servidor serve a própria interface web.

Para verificar a conexão no Windows, execute `.\scripts\diagnosticar-conexao.cmd` em outro terminal. Não é necessário alterar a política de execução do PowerShell.

Consulte o [guia de validação](docs/GUIA_DE_VALIDACAO.md) para testes e o [README](README.md) para detalhes do projeto.

## Tarefas Git

Em Ctrl+Shift+P → Tasks: Run Task, estão disponíveis as tarefas de [.vscode/tasks.json](.vscode/tasks.json): consultar estado, pull --rebase, adicionar alterações, commit, push e salvar/enviar.

Antes de usar a tarefa que adiciona todas as alterações (git add -A), confira git status e revise o diff. Trabalhe em branch separada e abra PR antes da integração. Nunca versione tokens, bancos ou relatórios financeiros reais.

A configuração MCP opcional do workspace está em [.vscode/mcp.json](.vscode/mcp.json). Configure credenciais pela integração apropriada, não em arquivos versionados.
