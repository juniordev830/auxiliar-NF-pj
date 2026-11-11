# Guia rápido — Controle de Gastos Residenciais

## Estado atual

O backend ASP.NET Core (.NET 8) com SQLite e um **painel web local** em HTML/CSS/JavaScript estão disponíveis na mesma aplicação. Não existe frontend React independente; não use `npm run dev` neste projeto.

## Requisitos e execução

Instale o **SDK .NET 8** (não apenas o runtime): https://dotnet.microsoft.com/download/dotnet/8.0. Depois de instalar, reinicie o terminal e confirme com `dotnet --version`.

Na raiz do repositório, execute:

```powershell
dotnet restore ControladorGastos/ControladorGastos.csproj
dotnet run --project ControladorGastos/ControladorGastos.csproj
```

Mantenha o terminal aberto e navegue até **http://127.0.0.1:5000/**. A API está em `http://127.0.0.1:5000/api/health`.

### Diagnóstico no Windows

Em outro terminal, na raiz do repositório, execute:

```powershell
.\scripts\diagnosticar-conexao.cmd
```

O comando verifica a presença do SDK, testa a API e o painel. **Não é um arquivo PowerShell**: funciona mesmo quando a política de execução do Windows bloqueia arquivos `.ps1`, sem alterar as configurações de segurança. Caso `dotnet` não seja reconhecido, instale o SDK, abra um novo terminal e reinicie `dotnet run`.

## Rotas principais

- `GET /api/health`
- `GET /api/pessoas`
- `POST /api/pessoas` — JSON: `{"nome":"Ana","idade":30}`
- `DELETE /api/pessoas/{id}`
- `GET /api/transacoes` — lista paginada
- `POST /api/transacoes` — JSON: `{"descricao":"Mercado","valor":125.90,"tipo":"DESPESA","pessoaId":1}`
- `GET /api/transacoes/totais/resumo`

Tipos permitidos: `RECEITA` e `DESPESA`. O servidor bloqueia receitas para pessoas menores de 18 anos.

## Segurança

O painel e a API são **exclusivamente locais** (`127.0.0.1`). Não publique portas para outras máquinas ou internet: ainda faltam autenticação individual, autorização por residência e proteção de dados para uso em produção. Há tokens opcionais apenas para clientes locais; veja o [README](README.md). Não insira informações financeiras reais neste protótipo.
