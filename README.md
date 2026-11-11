# Controle de Gastos Residenciais

API inicial executável para registrar pessoas da residência, receitas e despesas, com persistência local em SQLite.

## Estado real do projeto

O backend ASP.NET Core (.NET 8) está implementado. Há um painel web **HTML/CSS/JavaScript para uso local**, servido pelo mesmo processo .NET. Uma interface React independente ainda não está incluída; os documentos antigos descreviam uma aplicação planejada.

## Requisitos

- .NET SDK 8

## Executar

Na raiz do repositório:

```bash
dotnet restore ControladorGastos/ControladorGastos.csproj
dotnet run --project ControladorGastos/ControladorGastos.csproj
```

O servidor escuta **somente em `127.0.0.1:5000`** por segurança. Abra **http://127.0.0.1:5000/** no navegador para usar o painel local, sem instalar Node.js ou executar `npm run dev`. A API está em `http://127.0.0.1:5000/api/health` e nas demais rotas abaixo. O banco `controlador-gastos.db` é criado localmente no primeiro início. O protótipo usa `EnsureCreated`; antes de produção, crie migrations versionadas e configure backup e proteção dos dados financeiros.

## Problemas de conexão no VS Code / PowerShell (Windows)

1. Abra no VS Code **a pasta raiz do repositório**, não a pasta `C:\\Users` isoladamente.
2. No terminal integrado, execute `dotnet --version` para verificar se o SDK .NET 8 está instalado.
3. Execute `dotnet restore ControladorGastos/ControladorGastos.csproj` e `dotnet run --project ControladorGastos/ControladorGastos.csproj`. Mantenha o terminal aberto.
4. Abra `http://127.0.0.1:5000/` no navegador. **Não digite `Local:` ou `Network:` como comandos do PowerShell.**
5. Em **outro terminal PowerShell**, rode `Invoke-RestMethod http://127.0.0.1:5000/api/health`, ou execute `.\\scripts\\diagnosticar-conexao.ps1`.

Se o endpoint `/api/health` responder com `{"status":"ok"}`, a API local está alcançável. Se `/api/health` funcionar, mas `/` retornar 404, atualize este código e reinicie o processo `dotnet run`. Se ambos falharem, inspecione os erros do terminal do servidor e a porta 5000. Se o navegador exibir 401/403 ao carregar dados, foram configurados tokens de acesso: o painel **não coleta tokens**, e a API deverá ser usada por um cliente seguro conforme a seção de proteção abaixo.

**Importante:** `localhost` e `127.0.0.1` não são endereços públicos. Abrir o painel no navegador **não significa publicar o projeto na internet**. Esta versão guarda dados financeiros e **não deve** ser exposta diretamente a outras máquinas, à internet ou por link público/porta pública do Codespaces; faltam identidade individual, HTTPS e controles de autorização. A primeira restauração de pacotes (`dotnet restore`) pode precisar de acesso à internet, mas o uso local do sistema não requer internet depois que as dependências estiverem disponíveis.

## Endpoints

- `GET /api/health` — verificação de disponibilidade.
- `GET /api/pessoas` — lista pessoas.
- `POST /api/pessoas` — cria pessoa com `nome` e `idade` (0–120).
- `DELETE /api/pessoas/{id}` — remove pessoa e suas transações.
- `GET /api/transacoes?page=1&limit=50` — lista transações com o nome da pessoa, com paginação (página 1 a 100.000, limite 1 a 100, 50 por padrão). Retorna array JSON como antes, mas com limite de itens; entradas inválidas retornam HTTP 400.
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
- Esta versão não possui login individual nem frontend React independente (o painel HTML básico é local). Tokens de leitura/administração podem ser ativados apenas para uso local. Não exponha a API na internet nem a use com dados financeiros reais até implementar autenticação individual, autorização e demais controles.

## Proteção opcional por tokens (acesso local)

Para ativar proteção de todas as rotas `/api/*`, exceto `/api/health`, configure **os dois** segredos por variáveis de ambiente antes de iniciar:

```bash
# Gere valores aleatórios diferentes; não copie tokens de exemplos ou do CI.
export GASTOS_READ_TOKEN="$(openssl rand -hex 32)"
export GASTOS_ADMIN_TOKEN="$(openssl rand -hex 32)"
dotnet run --project ControladorGastos/ControladorGastos.csproj
```

Ambos precisam ter pelo menos 32 bytes e ser diferentes. Com a proteção ativa:

- O token de leitura permite `GET` e `HEAD` nas rotas `/api/*`.
- O token de administração permite leitura, criação e exclusão.
- Requisições sem token válido retornam **401**; um token de leitura tentando escrever retorna **403**.
- Envie o token em `Authorization: Bearer <seu-token>`. Exemplo: `curl -H "Authorization: Bearer $GASTOS_READ_TOKEN" http://127.0.0.1:5000/api/pessoas`.
- Não publique, registre em logs, versione ou exponha os segredos em JavaScript do navegador.

Sem essas duas variáveis, o protótipo continua **sem autenticação** e somente em `127.0.0.1`, para preservar o uso local existente. Essa é uma medida inicial para um operador local, **não** um sistema completo de identidade e autorização por usuário. Não exponha a aplicação na internet antes de implementar contas de usuários, autorização por recurso, autenticação segura, HTTPS e migrações versionadas.

## Testes e CI

O GitHub Actions restaura, compila, audita dependências NuGet e realiza testes smoke da validação de API, paginação de transações, regra de menores, exclusão em cascata e acessos anônimo, leitor e administrador. Testes de integração mais completos ainda são necessários antes de considerar a API pronta para produção.

## Cliente de terminal em Swift (nova linguagem)

O projeto também inclui um cliente **Swift** experimental em [`swift-client/`](swift-client/README.md). Ele lê disponibilidade, pessoas e resumo financeiro da API **local** (sem modificar registros):

```bash
cd swift-client
swift run gastos-cli health
swift run gastos-cli pessoas
swift run gastos-cli resumo
swift test
```

É necessário manter a API .NET em execução na mesma máquina. Para instâncias locais com autenticação por token, use `GASTOS_READ_TOKEN` como variável de ambiente. Veja o README do cliente para requisitos e limitações. Não é um aplicativo iOS.
