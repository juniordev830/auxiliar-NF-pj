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
- O Kestrel limita o corpo de cada requisição a **16 KiB (16.384 bytes)**. Payloads maiores retornam HTTP 413; isto reduz abuso por requisições JSON excessivas, mas não substitui limites de taxa e autenticação individual.
- O valor deve ser positivo; valores monetários são representados como decimal.
- Menores de 18 anos não podem registrar receitas.
- A remoção de uma pessoa remove suas transações relacionadas.
- Esta versão não possui login individual nem frontend. Tokens de leitura/administração podem ser ativados apenas para uso local. Não exponha a API na internet nem a use com dados financeiros reais até implementar autenticação individual, autorização e demais controles.

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
- Envie somente um cabeçalho `Authorization`. Cabeçalhos duplicados, valores combinados e valores muito longos são rejeitados.
- As respostas de dados em `/api/*` recebem `Cache-Control: no-store`, inclusive no modo local, para evitar armazenamento em cache de informações financeiras.
- Não publique, registre em logs, versione ou exponha os segredos em JavaScript do navegador.

Para impedir a inicialização sem proteção por esquecimento de configuração, ative também `GASTOS_REQUIRE_AUTH=true` no ambiente. Nesse modo, a aplicação **falha ao iniciar** se os dois tokens não estiverem definidos, não forem suficientemente longos ou forem iguais:

```bash
export GASTOS_REQUIRE_AUTH=true
export GASTOS_READ_TOKEN="$(openssl rand -hex 32)"
export GASTOS_ADMIN_TOKEN="$(openssl rand -hex 32)"
dotnet run --project ControladorGastos/ControladorGastos.csproj
```

O parâmetro `GASTOS_REQUIRE_AUTH` aceita somente `true` ou `false`; outros valores impedem o início para evitar configuração acidental. Use esse modo ao exigir proteção local, mas **não o trate como substituto de login por usuário nem como autorização para publicar a API**.

Sem essas duas variáveis, o protótipo continua **sem autenticação** e somente em `127.0.0.1`, para preservar o uso local existente. Essa é uma medida inicial para um operador local, **não** um sistema completo de identidade e autorização por usuário. Não exponha a aplicação na internet antes de implementar contas de usuários, autorização por recurso, autenticação segura, HTTPS e migrações versionadas.

## Testes e CI

O GitHub Actions restaura, compila, audita dependências NuGet e realiza testes smoke da validação de API, paginação de transações, regra de menores, exclusão em cascata e acessos anônimo, leitor e administrador, além da falha de inicialização quando a autenticação obrigatória está sem tokens. Testes de integração mais completos ainda são necessários antes de considerar a API pronta para produção.
