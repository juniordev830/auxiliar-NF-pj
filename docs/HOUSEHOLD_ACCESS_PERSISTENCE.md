# Persistência isolada de contas e vínculos de acesso

Esta branch implementa o **modelo e a consulta de autorização** separados do SQLite financeiro local. É uma etapa de desenvolvimento e não disponibiliza login ou isolamento multiusuário na API atual.

## Estrutura

- `ContaAcesso`: identidade técnica com `Emissor` e `SujeitoExterno`; a combinação tem índice único. Não representa `Pessoa` cadastrada na residência.
- `ResidenciaAcesso`: escopo administrativo independente dos registros financeiros existentes.
- `VinculoAcesso`: associação única `UsuarioId + ResidenciaId` com `Leitor`, `Editor` ou `Administrador`.
- `AcessoResidencialContext`: EF Core separado, com tabelas `acesso_*`, não injetado no `Program.cs` e não iniciado automaticamente.
- `ConsultaAcessoResidencia.PermiteAsync`: busca vínculo persistido usando identificadores de usuário/residência **fornecidos por autenticação e contexto de recurso validados**, depois aplica a política existente.

## Validação

```bash
dotnet test ControladorGastos.Tests/ControladorGastos.Tests.csproj --configuration Release
```

Testes em SQLite `:memory:` verificam vínculos entre duas residências e duas contas, leitura/administração, tentativa de acesso cruzado, ausência de identidade, índice único de identidade externa e isolamento do esquema financeiro.

O `EnsureCreatedAsync` aparece **somente no código de testes da persistência**. O banco financeiro original não foi migrado nem alterado por esta branch.

## Próxima implementação necessária antes de qualquer API multiusuária

1. Definir provedor confiável, validar emissão, público-alvo e expiração do token e derivar a conta autenticada.
2. Criar migrações versionadas para a persistência de acesso, com backup e rollback.
3. Relacionar `Pessoa` e `Transacao` ao escopo de residência de forma compatível com registros existentes, sem atribuição automática de dados legados.
4. Consultar permissões na base antes de cada operação e filtrar recursos e totais na consulta SQL.
5. Testar duas contas acessando as rotas reais (401, 403, 404 e proteção de acesso cruzado).

**Segurança:** esta branch não ativa conta, token ou rota novos; mantenha a aplicação em loopback e use apenas dados demonstrativos. Não é prontidão para produção.

**Revisão em pilha:** esta mudança se apoia na branch `feature/household-access-policy-20261104` ([PR #16](https://github.com/juniordev830/controle-gastos-residenciais/pull/16)), não diretamente na `main`. Revisar a política primeiro; não integrar nenhuma das duas automaticamente.
