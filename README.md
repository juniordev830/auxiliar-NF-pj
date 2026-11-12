# Auxiliar PJ

**Sistema local de apoio à gestão financeira para profissionais PJ, freelancers e pequenas empresas.**

Este repositório passa a reunir o módulo de receitas/despesas do `controle-gastos-residenciais` e o
gerador de relatórios do [`relatorio-altomatizado-de-contas-`](https://github.com/juniordev830/relatorio-altomatizado-de-contas-).
Os dois códigos foram integrados, mas o segundo repositório foi preservado sem arquivamento ou exclusão.

> **Status:** primeira versão de desenvolvimento, não pronta para produção.
> Não disponibilize na internet nem use dados financeiros sensíveis sem autenticação,
> autorização, backup e migrações de banco.

## Executar o Auxiliar PJ

Requisito: **.NET SDK 8**. Na raiz do repositório:

```bash
dotnet restore ControladorGastos/ControladorGastos.csproj
dotnet run --project ControladorGastos/ControladorGastos.csproj
```

Abra **http://127.0.0.1:5000**. O painel PJ é uma página HTML responsiva servida pela
API ASP.NET Core; não exige instalar Node ou iniciar frontend separado.

O módulo legado continua com seu banco `controlador-gastos.db`; os lançamentos PJ ficam em
`auxiliar-pj.db`, mantendo os dados residenciais separados. Não há migração automática
dos lançamentos do módulo residencial para o PJ.

## Funcionalidades implementadas

- Lançamentos de **receitas e despesas** com categoria, contraparte, competência, vencimento e valor;
- Pagamentos marcados como recebidos/pagos, pendentes ou atrasados;
- Painel mensal com saldos previsto e realizado (por competência);
- Listagem paginada, filtros por período e situação;
- Exportação CSV para o relatório HTML Python com indicadores e gráficos.

### API PJ

| Método | Endereço | Finalidade |
| --- | --- | --- |
| GET | `/api/pj/resumo?ano=2026&mes=11` | Indicadores do período |
| GET | `/api/pj/lancamentos?ano=2026&mes=11&page=1&limit=10` | Lançamentos |
| POST | `/api/pj/lancamentos` | Criar lançamento |
| PUT | `/api/pj/lancamentos/{id}/pagamento` | Registrar ou reabrir pagamento |
| DELETE | `/api/pj/lancamentos/{id}` | Excluir lançamento |
| GET | `/api/pj/exportar.csv?ano=2026&mes=11` | Baixar CSV |

Exemplo de lançamento:

```bash
curl -X POST http://127.0.0.1:5000/api/pj/lancamentos \
  -H "Content-Type: application/json" \
  -d '{"descricao":"Projeto web","tipo":"RECEITA","categoria":"Serviços","valor":1500.00,"competencia":"2026-11-12T00:00:00","vencimento":"2026-11-20T00:00:00","dataPagamento":null,"contraparte":"Cliente exemplo"}'
```

O resumo considera a **competência**, não a data do movimento bancário. O saldo realizado
soma somente os lançamentos da competência marcada que já têm data de pagamento.
O status atrasado usa o dia UTC do servidor. Não há cálculo automático de impostos, emissão
de notas ou declarações fiscais nesta fase.

## Relatórios migrados do projeto nº 2

```bash
python -m pip install -r relatorios/requirements.txt
python relatorios/gerar_relatorio.py relatorios/exemplo-pj.csv --saida relatorio-pj.html
python -m pytest relatorios/tests -q
```

Abra `relatorio-pj.html` no navegador. Para usar seus lançamentos, exporte CSV
pelo botão do painel e informe o arquivo no lugar de `relatorios/exemplo-pj.csv`.
Mais detalhes em [relatorios/README.md](relatorios/README.md).

## Antes de considerar uso profissional

São necessários autenticação e perfis de empresa, controle de acesso, migrações
versionadas, backup/recuperação, testes de integração e revisão de segurança.
Funções contábeis/fiscais exigem validação de profissional habilitado.

---

## Módulo original: Controle de Gastos Residenciais

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
- O valor deve ser positivo; valores monetários são representados como decimal.
- Menores de 18 anos não podem registrar receitas.
- A remoção de uma pessoa remove suas transações relacionadas.
- O módulo residencial ainda não possui frontend próprio nem login individual; o módulo PJ possui um painel HTML local. Tokens de leitura/administração podem ser ativados apenas para uso local. Não exponha a API na internet nem a use com dados financeiros reais até implementar autenticação individual, autorização e demais controles.

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
