# Controle de Gastos Residenciais

API inicial executável para registrar pessoas da residência, receitas e despesas, com persistência local em SQLite.

## Estado real do projeto

O backend ASP.NET Core (.NET 8) está implementado nesta branch. A interface React ainda não está incluída; os documentos antigos descreviam uma aplicação planejada e não devem ser interpretados como prova de que o frontend existe.

## Requisitos

- .NET SDK 8

## Executar

Na raiz do repositório:

```bash
dotnet restore ControladorGastos/ControladorGastos.csproj
dotnet run --project ControladorGastos/ControladorGastos.csproj
```

A API informa as rotas em `http://localhost:5000` ou na URL local exibida pelo ASP.NET Core. O banco `controlador-gastos.db` é criado localmente no primeiro início. O protótipo usa `EnsureCreated`; antes de produção, crie migrations versionadas e configure backup e proteção dos dados financeiros.

## Endpoints

- `GET /api/health` — verificação de disponibilidade.
- `GET /api/pessoas` — lista pessoas.
- `POST /api/pessoas` — cria pessoa com `nome` e `idade` (0–120).
- `DELETE /api/pessoas/{id}` — remove pessoa e suas transações.
- `GET /api/transacoes` — lista transações com o nome da pessoa.
- `POST /api/transacoes` — cria transação com `descricao`, `valor`, `tipo` (`RECEITA` ou `DESPESA`) e `pessoaId`.
- `GET /api/transacoes/totais/resumo` — totais gerais e por pessoa.

Exemplo para criar pessoa:

```bash
curl -X POST http://localhost:5000/api/pessoas \\
  -H 'Content-Type: application/json' \\
  -d '{"nome":"Ana","idade":30}'
```

Exemplo para criar despesa:

```bash
curl -X POST http://localhost:5000/api/transacoes \\
  -H 'Content-Type: application/json' \\
  -d '{"descricao":"Mercado","valor":125.90,"tipo":"DESPESA","pessoaId":1}'
```

## Regras e limitações

- Nome e descrição são validados no servidor.
- O valor deve ser positivo; valores monetários são representados como decimal.
- Menores de 18 anos não podem registrar receitas.
- A remoção de uma pessoa remove suas transações relacionadas.
- Esta versão não possui login/autorização nem frontend; não exponha a API na internet nem a use com dados financeiros reais até implementar esses controles.

## Testes e CI

O GitHub Actions restaura e compila o backend em cada pull request. Testes automatizados de integração e da regra de menores são a próxima etapa antes de considerar a API pronta para uso real.
