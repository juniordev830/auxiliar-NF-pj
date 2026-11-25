# Fluxo de caixa realizado

GET /api/pj/fluxo-caixa?ano=2026&mes=9 exige token de leitura ou administração. O período é obrigatório. A consulta agrega receitas recebidas e despesas pagas pela data de pagamento, independentemente da competência original. Lançamentos não pagos ou excluídos ficam fora. Retorna receitas, despesas, saldo, quantidade e totais diários apenas para dias com movimento.

A soma usa decimal em C# e a consulta carrega somente campos necessários, iterando resultados sem criar lista de lançamentos. Não inclui saldo inicial, conciliação bancária ou projeções futuras. Não substitui contabilidade. Exemplo de teste: receitas de 0,10 e 0,20 e despesa de 0,01 resultam em saldo de R$ 0,29.
