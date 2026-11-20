# Guia rápido — Auxiliar PJ e Controle de Gastos

## O que está disponível

- API ASP.NET Core (.NET 8) com tokens obrigatórios para rotas protegidas.
- Painel HTML local do módulo Auxiliar PJ, servido pela mesma aplicação em `http://127.0.0.1:5000/`.
- O módulo residencial continua disponível por API; não há um painel residencial independente nesta versão.

## Executar

Na raiz do repositório:

```powershell
dotnet restore ControladorGastos/ControladorGastos.csproj
$env:GASTOS_READ_TOKEN = [Convert]::ToHexString([Security.Cryptography.RandomNumberGenerator]::GetBytes(32))
$env:GASTOS_ADMIN_TOKEN = [Convert]::ToHexString([Security.Cryptography.RandomNumberGenerator]::GetBytes(32))
dotnet run --project ControladorGastos/ControladorGastos.csproj
```

Mantenha o servidor em execução e abra `http://127.0.0.1:5000/`.

## Diagnóstico no Windows

Em outro terminal, execute:

```powershell
.\scripts\diagnosticar-conexao.cmd
```

O arquivo CMD funciona sem executar scripts PowerShell. Ele verifica o SDK .NET, a API em `/api/health` e a página inicial. Se o comando `dotnet` não for encontrado, instale o **SDK .NET 8**, abra um novo terminal e tente novamente.

## Rotas principais

- `GET /api/health`
- `GET /api/pessoas`
- `POST /api/pessoas`
- `GET /api/transacoes`
- `POST /api/transacoes`
- `GET /api/transacoes/totais/resumo`

As rotas protegidas exigem `Authorization: Bearer <token>`. Não coloque tokens em HTML, JavaScript, histórico do navegador ou repositórios.

## Segurança

Use somente em ambiente local. O painel PJ não oferece identidade individual por usuário e não deve ser publicado na internet. Não utilize dados financeiros reais antes de implementar autenticação individual, autorização por recurso, HTTPS, backups e migrações versionadas.
