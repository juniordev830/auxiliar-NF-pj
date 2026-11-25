# Documentação técnica — Auxiliar PJ

## Arquitetura

A aplicação usa ASP.NET Core Minimal APIs em .NET 8. Não há controllers MVC, camada de services separada, frontend React ou servidor Node. O painel PJ em HTML/CSS/JavaScript utiliza fetch e é servido por arquivos estáticos na mesma origem da API.

- [Program.cs](ControladorGastos/Program.cs): inicialização, tokens, migrações, rotas residenciais e health.
- [AuxiliarPjEndpoints.cs](ControladorGastos/PJ/AuxiliarPjEndpoints.cs): rotas PJ, validações, resumo e CSV.
- [AuxiliarPjContext.cs](ControladorGastos/PJ/AuxiliarPjContext.cs): modelo PJ, precisão monetária e índice de competência.
- [ControladorGastosContext.cs](ControladorGastos/Data/ControladorGastosContext.cs): modelo residencial e relacionamento pessoa/transações.
- [index.html](ControladorGastos/wwwroot/index.html): painel PJ.
- [relatórios](relatorios/README.md): geração local de HTML com Python.
- [cliente Swift](swift-client/README.md): acesso somente leitura às rotas residenciais.

## Inicialização e configuração

Siga o [README](README.md) para configurar tokens e executar no Windows ou Linux/macOS. O único endereço de escuta configurado pelo código é http://127.0.0.1:5000. Não abra portas nem publique a API.

| Configuração | Finalidade |
| --- | --- |
| GASTOS_READ_TOKEN | Leitura GET/HEAD |
| GASTOS_ADMIN_TOKEN | Leitura e escrita |
| ConnectionStrings__DefaultConnection | Conexão SQLite residencial opcional |
| ConnectionStrings__AuxiliarPj | Conexão SQLite PJ opcional |

Os tokens são obrigatórios, distintos e têm no mínimo 32 bytes UTF-8. São comparados em tempo constante quando os tamanhos coincidem. O painel não os persiste. O servidor não inicia com configuração inválida.

## Contrato HTTP

Base: `http://127.0.0.1:5000`. Use JSON e o cabeçalho Authorization: Bearer com o token apropriado. Para POST e PUT envie Content-Type: application/json.

| Código HTTP | Significado |
| --- | --- |
| 200 | Consulta ou atualização bem-sucedida |
| 201 | Registro criado |
| 204 | Exclusão concluída |
| 400 | Dados ou filtros inválidos |
| 401 | Token ausente/inválido |
| 403 | Leitor sem permissão de escrita |
| 404 | Registro não encontrado nas operações por ID |

### API PJ

| Método e rota | Parâmetros / efeito |
| --- | --- |
| GET /api/pj/resumo | ano e mes opcionais; padrão mês/ano UTC atual |
| GET /api/pj/lancamentos | ano, mes, tipo, status, page, limit |
| POST /api/pj/lancamentos | Criar lançamento com corpo JSON |
| PUT /api/pj/lancamentos/{id}/pagamento | Atualizar dataPagamento; null reabre |
| DELETE /api/pj/lancamentos/{id} | Excluir definitivamente |
| GET /api/pj/exportar.csv | ano e mes opcionais; sem filtro retorna todos |

Ano: 2000–2200; mês: 1–12 (exige ano). Página: 1–100000, limite: 1–100 (padrões 1 e 50). A listagem retorna objeto com items, total, page e limit, em ordem decrescente de competência e ID. Tipo: RECEITA ou DESPESA. Status: PAGO, PENDENTE ou ATRASADO. As listagens e exportações filtram pela competência.

Corpo de exemplo para criação, com dados fictícios:

```json
{
  "descricao": "Serviço de desenvolvimento",
  "tipo": "RECEITA",
  "categoria": "Serviços",
  "contraparte": "Cliente exemplo",
  "valor": 1500.00,
  "competencia": "2026-11-12",
  "vencimento": "2026-11-20",
  "dataPagamento": null
}
```

Pagamento: `{"dataPagamento":"2026-11-20"}`. Reabertura: `{"dataPagamento":null}`.

Regras:
- Descrição obrigatória: 1–200 caracteres; categoria: 1–80; contraparte opcional: até 120.
- Valor positivo, até 100 milhões, com no máximo duas casas decimais.
- Datas de competência, vencimento e pagamento entre 2000 e 2200; as duas últimas são opcionais.
- PAGO quando há data de pagamento; ATRASADO se não pago e vencimento anterior ao dia UTC atual; demais são PENDENTE.
- Saldo previsto = receitas previstas − despesas previstas. Saldo realizado = receitas recebidas − despesas pagas, dentro da competência escolhida. Não equivale necessariamente ao fluxo bancário do mês.
- O resumo ainda informa aReceber, aPagar, quantidade e valor em atraso e agrupamento por categoria/tipo.
- CSV UTF-8 com BOM e delimitador ponto e vírgula; campos textuais recebem proteção contra fórmulas de planilha. O arquivo contém Data, Categoria, Valor, Tipo, Descricao, Status, Contraparte, Vencimento e Pagamento.

### API residencial

| Método e rota | Parâmetros / efeito |
| --- | --- |
| GET /api/pessoas | Lista de pessoas, ordenada por nome |
| POST /api/pessoas | nome e idade |
| DELETE /api/pessoas/{id} | Exclui pessoa e transações relacionadas |
| GET /api/transacoes | page, limit, tipo, pessoaId, de, ate (opcionais) |
| POST /api/transacoes | descricao, valor, tipo, pessoaId |
| GET /api/transacoes/totais/mensal | ano e mes obrigatórios |
| GET /api/transacoes/totais/resumo | Totais gerais e por pessoa |

Exemplos de corpos JSON:

```json
{"nome":"Pessoa exemplo","idade":30}
```

```json
{"descricao":"Mercado","valor":125.90,"tipo":"DESPESA","pessoaId":1}
```

Use o ID realmente retornado na criação de pessoa. Nome: 1–100 caracteres; idade: 0–120. Descrição: 1–200. Valores seguem os mesmos limites monetários do PJ. Pessoa deve existir; menores de 18 anos não podem registrar receitas (regra interna do aplicativo, não regra legal). A exclusão de pessoa é em cascata.

A listagem retorna array JSON, com paginação 1–100000 e limite 1–100 (padrão 50), ordenado por data de criação e ID decrescentes. Datas de filtro e totais mensais referem-se à data de criação, não à competência PJ. Ano do resumo mensal: 2000–2200; mês: 1–12.

Não há rotas GET por ID ou edição residencial, nem edição integral de lançamento PJ. O cliente Swift usa somente GET.

## Persistência e atualização

Os contextos residenciais e PJ utilizam arquivos SQLite independentes por padrão. As migrações versionadas em Data/Migrations e PJ/Migrations são aplicadas pelo startup com Database.Migrate(). As migrações iniciais registram o esquema legado, e há teste de regressão de atualização.

Antes de atualizar:
1. Pare a aplicação.
2. Copie os dois bancos e quaisquer arquivos auxiliares SQLite associados para local protegido.
3. Inicie a versão nova e confira totais, registros e exportações.
4. Se a migração falhar, preserve os arquivos, consulte os logs e valide a recuperação a partir da cópia. Não apague bancos para tentar corrigir erros.

Não há migração automática entre módulos, backup automatizado ou isolamento de dados por empresa.

## Validação e manutenção

Veja o [guia de validação](docs/GUIA_DE_VALIDACAO.md) para testes e cenários manuais. O CI compila .NET, audita NuGet, verifica migração SQLite e faz smoke tests de validação, autenticação e permissões, além dos testes do gerador Python. Há workflow separado para Swift.

## Limites atuais

Protótipo local. Antes de produção: identidade individual, autorização por empresa/recurso, HTTPS, trilha de auditoria, backup e recuperação, testes de integração, política de retenção e revisão de segurança. Não há emissão de nota fiscal, cálculo tributário, integração bancária, nem cadastro empresarial completo. O relatório é gerencial e não substitui contabilidade formal.
