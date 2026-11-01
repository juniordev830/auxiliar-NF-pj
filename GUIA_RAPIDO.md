# Guia rápido — Controle de Gastos Residenciais

## Estado atual

O backend ASP.NET Core com SQLite está disponível. O frontend React citado em documentos anteriores ainda não foi implementado; por isso, use a API por enquanto.

## Executar

```bash
dotnet restore ControladorGastos/ControladorGastos.csproj
dotnet run --project ControladorGastos/ControladorGastos.csproj
```

Use a URL local exibida no terminal. Em geral, a API responde em `/api/health`.

## Rotas principais

- `GET /api/pessoas`
- `POST /api/pessoas` — JSON: `{"nome":"Ana","idade":30}`
- `DELETE /api/pessoas/{id}`
- `GET /api/transacoes`
- `POST /api/transacoes` — JSON: `{"descricao":"Mercado","valor":125.90,"tipo":"DESPESA","pessoaId":1}`
- `GET /api/transacoes/totais/resumo`

Tipos permitidos: `RECEITA` e `DESPESA`. O servidor bloqueia receitas para pessoas menores de 18 anos.

## Segurança

Esta versão ainda não tem autenticação/autorização nem frontend. Execute somente em ambiente local de desenvolvimento; não publique a API nem insira dados financeiros reais. Antes de produção, implemente login, autorização, migrations e testes de integração.
