# Validação técnica — Auxiliar PJ

O repositório passou a concentrar a API original de gastos, o módulo financeiro PJ e o gerador Python de relatórios. A denominação **NF** no nome do repositório não significa que ele emita notas fiscais: **essa função ainda não foi implementada**.

## Verificação local

1. Instalar o SDK .NET 8 e executar `dotnet restore ControladorGastos/ControladorGastos.csproj`.
2. Iniciar com `dotnet run --project ControladorGastos/ControladorGastos.csproj` e consultar `http://127.0.0.1:5000/api/health`.
3. Abrir o painel PJ na raiz do servidor. Registrar receita e despesa **fictícias**, verificar resumo por competência e marcar pagamento.
4. Exportar CSV pelo painel e conferir os campos `Data`, `Categoria`, `Valor`, `Tipo` e `Status`.
5. Instalar dependências do relatório: `python -m pip install -r relatorios/requirements.txt`.
6. Rodar `python -m pytest relatorios/tests -q` e gerar HTML com `python relatorios/gerar_relatorio.py relatorios/exemplo-pj.csv --saida relatorio-pj.html`.

## Casos a testar antes de liberar

- Receita e despesa na mesma competência, inclusive saldo negativo e mês sem lançamentos.
- Pagamento pendente, atrasado, quitado e reaberto; consulta por mês e paginação.
- Valor inválido, categorias vazias, data impossível e conteúdo hostil em campos de texto.
- Importação e exportação CSV com vírgulas, ponto e vírgula, acentos e fórmulas de planilha.
- Ausência de acesso indevido a lançamentos de outra empresa: **ainda falta isolamento multiusuário**.

## Riscos e próximos incrementos

A API é somente local e o módulo PJ usa `auxiliar-pj.db`, separado do banco residencial. O sistema ainda exige autenticação por usuário, autorização por empresa, migrations, backup, testes de integração e política de retenção. Planejar cadastro de CNPJ e documentos fiscais somente após validar o modelo de dados com especialista contábil. Não usar em produção com dados financeiros reais nesta fase.
