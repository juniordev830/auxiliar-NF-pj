# Edição e histórico PJ

PUT /api/pj/lancamentos/{id} recebe o mesmo JSON de criação. DELETE aplica exclusão lógica; lançamentos excluídos não aparecem nas consultas, totais ou exportações. GET /api/pj/lancamentos/{id}/historico aceita page e limit e retorna snapshots JSON antes/depois, ação e data UTC. O token leitor tem acesso ao histórico, assim como aos dados financeiros. O histórico começa após a atualização; não reconstrói ações antigas. O token compartilhado não identifica pessoas. A migração cria novas colunas e tabela de histórico; faça backup antes de atualizar. Não execute rollback da migração com dados reais sem plano de recuperação.

## Controle de versão de lançamento
GET /api/pj/lancamentos/{id} retorna o lançamento ativo com versao. PUT de edição e pagamento aceitam versao no JSON; DELETE aceita ?versao=N. Se fornecida e divergente da versão atual, a API retorna 409 sem alterar dados ou histórico. O painel envia a versão lida ao editar e registrar pagamento. Clientes antigos ainda podem omitir esse campo (compatibilidade); devem adotá-lo para impedir sobrescrita por dados desatualizados.
