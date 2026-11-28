# Edição e histórico PJ

PUT /api/pj/lancamentos/{id} recebe o mesmo JSON de criação. DELETE aplica exclusão lógica; lançamentos excluídos não aparecem nas consultas, totais ou exportações. GET /api/pj/lancamentos/{id}/historico aceita page e limit e retorna snapshots JSON antes/depois, ação e data UTC. O token leitor tem acesso ao histórico, assim como aos dados financeiros. O histórico começa após a atualização; não reconstrói ações antigas. O token compartilhado não identifica pessoas. A migração cria novas colunas e tabela de histórico; faça backup antes de atualizar. Não execute rollback da migração com dados reais sem plano de recuperação.

## Credenciais individuais

Para cada pessoa, gere um segredo aleatório de pelo menos 32 bytes, codifique-o em Base64 URL e monte o token como `identificador.segredo`. Use um identificador pseudônimo de até 64 caracteres ASCII, com letras, números, hífens ou sublinhados. Calcule o SHA-256 hexadecimal do token inteiro. Configure o hash, o papel e a validade em UTC no ambiente do servidor. Exemplo de nomes das variáveis para o identificador `operador-01`

- `GASTOS_CREDENCIAIS__operador-01__TokenHash`
- `GASTOS_CREDENCIAIS__operador-01__Role` com valor `admin` ou `read`
- `GASTOS_CREDENCIAIS__operador-01__ExpiresAt` no formato `AAAA-MM-DDTHH:mm:ssZ`

Envie o token completo como Bearer. O papel `read` permite consultas, e `admin` também permite alterações. A presença de credenciais individuais desativa os tokens compartilhados. Em implantações que exigem autenticação individual, configure `GASTOS_REQUIRE_INDIVIDUAL_CREDENTIALS=true` para impedir que uma configuração vazia volte ao modo de tokens compartilhados. O cliente pode revogar sua credencial com `POST /api/session/logout`. Para revogar administrativamente, retire a entrada correspondente da configuração e reinicie o serviço. Para rotacionar, gere outro segredo com o mesmo identificador. O histórico dos lançamentos PJ inclui `responsavel` para alterações feitas com credenciais individuais.
