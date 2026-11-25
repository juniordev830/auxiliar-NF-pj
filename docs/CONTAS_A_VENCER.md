# Contas a vencer e vencidas

GET /api/pj/contas-a-vencer?referencia=2026-05-10 exige token de leitura ou administração. A data de referência é obrigatória no formato ISO (AAAA-MM-DD), entre 2000 e 2200. A escolha explícita evita ambiguidades de fuso horário. Soma todos os lançamentos ativos não pagos, independentemente da competência.

As seis faixas são: ATRASADO (anterior à referência), HOJE, ATE_7_DIAS (1 a 7), ATE_30_DIAS (8 a 30), MAIS_DE_30_DIAS (31 ou mais), SEM_VENCIMENTO. Retorna valores a pagar/receber, saldo previsto por faixa e quantidade. Os totais são decimais exatos; não são saldo bancário nem projeção de receitas não cadastradas. Lançamentos excluídos e pagos não entram na consulta.
