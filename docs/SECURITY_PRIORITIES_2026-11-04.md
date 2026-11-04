# Próximas prioridades de segurança — Controle de Gastos

**Revisão:** 04/11/2026. **Estado:** plano validado contra `Program.cs`, `ControladorGastosContext.cs`, modelos e CI. Não significa que estas mudanças estejam implementadas.

## Evidências verificadas

- A entidade `Pessoa` guarda nome, idade e transações da residência. **Pessoa não é uma conta autenticada**; não usar `PessoaId` como identidade de login.
- A entidade `Transacao` referencia `PessoaId`, mas **não** possui proprietário/tenant autenticado.
- Os endpoints `GET /api/pessoas`, `GET /api/transacoes`, `GET /api/transacoes/totais/*` fazem leituras transversais.
- `GET/POST/DELETE` usam tokens compartilhados de operador quando configurados; sem `GASTOS_REQUIRE_AUTH=true`, o modo local ainda aceita uso sem autenticação.
- `EnsureCreated` cria banco de protótipo e não equivale a migrations versionadas.
- O servidor está restrito a `127.0.0.1`; isso diminui exposição direta, **não** corrige autorização quando publicado por proxy.

## Ordem confirmada por risco

### P0 — Identidade e isolamento por residência/usuário (bloqueador de publicação)

1. Introduzir `Usuario` (identidade autenticada) e `Residencia` (escopo dos dados), com `MembroResidencia` para permissões. Não confundir `Usuario` com `Pessoa`.
2. Associar cada `Pessoa` e `Transacao` à residência. `PessoaId` continua sendo vínculo do beneficiário, mas não a autorização.
3. Exigir sessão/token com assinatura e claims validados (issuer, audience, expiração), identificando usuário e residência autorizada. Preferir biblioteca/framework de autenticação, sem implementar protocolo criptográfico próprio.
4. Aplicar autorização no servidor **antes** de todas as operações: pessoa, transação, totais mensal/resumo e exclusão em cascata. Consultas devem ser filtradas na query pelo escopo autorizado, inclusive detalhes por ID.
5. Definir papéis mínimos: `leitor` (consulta), `editor` (cadastro/alteração autorizada) e `administrador` (gestão de membros/exclusão). Verificar residência + ação, não só papel global.
6. Dados legados do SQLite **não devem ser atribuídos automaticamente** ao primeiro usuário. Criar migração versionada com backup, mapeamento explícito e validação de integridade.

**Aceite automatizado obrigatório:** usuário A não lista, consulta por ID, cria em nome de, altera ou exclui registros de B; totais de A não incluem B; ID externo deve retornar 404 ou 403 conforme política uniforme; anônimo 401; credencial válida sem permissão 403; admin do escopo A não obtém dados do escopo B.

### P0 — Configuração segura antes de acesso externo

- Bloquear implantação externa até concluir P0. `GASTOS_REQUIRE_AUTH` e tokens de operador são uma **proteção local transitória**, não um sistema multiusuário.
- TLS, proxy confiável, CORS explícito, limites de taxa/payload, logs sem credenciais/PII e testes contra IDOR/BOLA.
- Proibir uso de dados financeiros reais durante testes; usar somente fixtures sintéticas.

### P1 — Gestão de segredos e operação

- Carregar segredos via ambiente/secret manager, nunca arquivos versionados ou JavaScript do navegador.
- Criar política documentada de emissão, rotação com sobreposição curta, revogação, auditoria e recuperação. Não registrar token integral em logs.
- Instalar migrations EF Core, backup com restauração testada, política de retenção e segregação dos ambientes.

### P1 — Testes e CI

- Testes de tabela para cada verbo/rota/role/residência, 401, 403 e acesso cruzado.
- Testes SQLite real em CI com duas residências e pelo menos dois usuários. Não depender apenas de teste de função de autorização.
- Monitorar análise de dependências NuGet, testes de resposta HTTP sem cache e de carga excessiva.

## Sequência mínima de PRs separados

1. **Design e contrato:** entidades, matriz de permissões e migração sem ativar endpoints externos.
2. **Migrations + isolamento:** relacionamentos/índices, consultas escopadas e testes de A vs B.
3. **Identidade:** autenticação real, políticas e testes de sessão/token. Desligar modo legado apenas quando migração e testes forem seguros.
4. **Deploy readiness:** revisão de TLS, segredos, observabilidade, backup e plano de rollback.

**Critério de liberação:** não publicar enquanto P0 não estiver implementado, revisado e validado. Nada foi integrado à `main` por este documento.
