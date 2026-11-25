# Relatórios do Auxiliar PJ

Esta pasta incorpora e adapta o gerador Python desenvolvido no repositório
[`relatorio-altomatizado-de-contas-`](https://github.com/juniordev830/relatorio-altomatizado-de-contas-).
O código original permanece no outro repositório para preservar o histórico.

## Gerar com dados demonstrativos

```bash
python -m pip install -r relatorios/requirements.txt
python relatorios/gerar_relatorio.py relatorios/exemplo-pj.csv --saida relatorio-pj.html
```

Abra `relatorio-pj.html` no navegador.

## Gerar com os lançamentos da API

1. Inicie a aplicação ASP.NET Core com os dois tokens obrigatórios, seguindo o [README principal](../README.md). Use somente dados fictícios.
2. Acesse `http://127.0.0.1:5000`, informe o token de administração, cadastre lançamentos e escolha o mês.
3. Clique em **Exportar CSV** (ou chame `/api/pj/exportar.csv?ano=2026&mes=11`).
4. Salve o arquivo como `lancamentos-pj.csv` e execute:

```bash
python relatorios/gerar_relatorio.py lancamentos-pj.csv --saida relatorio-pj.html
```

O relatório mostra volume, receitas, despesas, saldo previsto, categorias e evolução temporal.
A soma de receitas e despesas é calculada por **competência**, não por data efetiva de pagamento.
A distribuição por categoria representa valores brutos, não resultado líquido.

## Dados e privacidade

- Não versione CSV exportado com dados reais, nem relatórios HTML que os contenham.
- O gerador aceita CSV com delimitador ponto e vírgula (`;`) exportado pelo projeto ou planilhas Excel com as colunas
  `Data`, `Categoria`, `Valor` e, opcionalmente, `Tipo`.
- O relatório é gerencial e não substitui apuração de tributos ou a contabilidade formal.
- Execute os testes com `python -m pytest relatorios/tests -q`.

Os totais e a tabela financeira usam centavos inteiros; valores fracionários, tipos inválidos e categorias ausentes são rejeitados e descritos no HTML. Datas ausentes ou inválidas são excluídas do gráfico temporal e sinalizadas. Os gráficos usam projeção numérica para visualização; a formatação monetária dos totais é pt-BR.
