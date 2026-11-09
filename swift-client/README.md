# Cliente Swift para Controle de Gastos

Cliente **somente leitura** feito em Swift para a API ASP.NET Core local deste repositório. Funciona como ferramenta de terminal em macOS/Linux; não é um app iOS nem uma interface React.

## Requisitos

- Swift 5.9 ou superior.
- API .NET executando na **mesma máquina**, em `http://127.0.0.1:5000`.

Na raiz do repositório, abra um terminal e execute:

```bash
dotnet run --project ControladorGastos/ControladorGastos.csproj
```

Em outro terminal:

```bash
cd swift-client
swift run gastos-cli health
swift run gastos-cli pessoas
swift run gastos-cli resumo
swift run gastos-cli mensal 2026 11
swift run gastos-cli transacoes
swift run gastos-cli transacoes 2 10 DESPESA
swift run gastos-cli transacoes 1 20 RECEITA
swift run gastos-cli csv 1 100 DESPESA > despesas.csv
swift test
```

Para API com tokens ativados, exporte o token **somente de leitura** para o processo local:

```bash
export GASTOS_READ_TOKEN="seu-token-local-configurado-no-backend"
swift run gastos-cli pessoas
```

Evite salvar o token em arquivos versionados e logs. O cliente aceita apenas URL HTTP de loopback `localhost` ou `127.0.0.1` na porta 5000 e **não segue redirecionamentos HTTP**, para evitar encaminhamento acidental do token a serviços externos. As operações são GET e não modificam o banco. ### Exportar CSV

O comando `csv` exporta **uma página de transações por vez**. Por segurança, o resultado vai somente para a saída padrão, e pode ser redirecionado a um arquivo local:

```bash
swift run gastos-cli csv 1 100 > transacoes.csv
swift run gastos-cli csv 1 100 RECEITA > receitas.csv
```

O arquivo inclui cabeçalho, aspas e valores separados por vírgulas, com proteção de campos que começam com fórmulas de planilhas. **Não compartilhe o CSV sem verificar os dados pessoais ou financeiros exportados.** Cada chamada recupera no máximo 100 itens; não é um backup completo do banco.

O relatório mensal apresenta receitas, despesas, saldo, quantidade de registros e totais por pessoa, com validação de **ano (2000–2200)** e **mês (1–12)**. A listagem de transações aceita **página entre 1 e 100.000**, **limite de 1 a 100 itens** e filtro opcional `RECEITA` ou `DESPESA`. Esses limites também são conferidos antes do pedido HTTP.

## Estrutura

- `Sources/GastosClient/GastosClient.swift`: modelos e chamadas HTTP tipadas.
- `Sources/GastosCLI/main.swift`: comandos de terminal.
- `Tests/GastosClientTests`: testes de validade de URL, filtros, paginação e decodificação das respostas.

O CI valida compilação e testes do pacote Swift. O cliente ainda **não** tem teste de integração real contra servidor ASP.NET nem deve ser usado em produção com dados financeiros.
