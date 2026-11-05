# Vínculo explícito entre recurso financeiro e residência (modelo preparatório)

Esta etapa amplia **apenas** o banco separado de autorização introduzido nos PRs #16, #17 e #18. A API financeira existente em `Program.cs` continua com rotas legadas e dados demonstrativos; **nenhuma rota atual usa estes vínculos**.

## Implementação

- `VinculoRecursoResidencia`: um único vínculo `(TipoRecurso, RecursoId) → ResidenciaId`, com chave primária composta, vínculo obrigatório à residência e verificação de ID positivo no SQLite.
- `TipoRecursoFinanceiro`: separa IDs de pessoas e transações, que podem numericamente coincidir.
- `ConsultaPermissaoRecurso.ResolverResidenciaAsync`: obtém a residência do recurso já persistido na tabela `acesso_recursos`. Não confia numa residência vinda de parâmetro de requisição.
- `ConsultaPermissaoRecurso.PermiteAsync`: obtém a residência desse vínculo e verifica conta validada e papel da residência no banco, **negando acesso** quando o vínculo não existe, a identidade é desconhecida ou a ação não é permitida.

Testes com SQLite em memória cobrem duas residências, dois papéis, acesso cruzado proibido, transações e pessoas com IDs numéricos potencialmente iguais, IDs inválidos, ausência de mapeamento e unicidade no banco.

```bash
dotnet test ControladorGastos.Tests/ControladorGastos.Tests.csproj --configuration Release
```

## Importantes limitações de segurança

1. **Não foi implementado login real:** os métodos de identidade aceitam `iss` + `sub` somente após validação criptográfica por um provedor confiável, ainda inexistente nesta API.
2. **Não existe FK entre o banco de autorização e o banco financeiro legado:** por isso, esta modelagem ainda não prova que a pessoa ou transação referenciada existe. Um ID legado **pode ser reciclado após exclusão**; a migração deverá adotar identificadores estáveis não reutilizáveis e limpar as associações excluídas. Nunca use apenas um ID de requisição como prova de propriedade.
3. **Não existe migração nem atribuição automática de propriedade** aos dados anteriores. Associar retroativamente dados existentes sem comprovar titularidade pode causar vazamento entre residências.
4. **Não existe filtro no SQL financeiro**: qualquer futura rota de listagem, totais, gravação e exclusão deverá buscar e validar o escopo autenticado, filtrar no próprio banco e verificar coerência entre a transação e sua pessoa, preferencialmente num mesmo modelo de dados transacional.
5. As tabelas de `AcessoResidencialContext` **não foram registradas** em `Program.cs`. `EnsureCreatedAsync` aparece apenas nos testes SQLite isolados. Nada é inicializado ou migrado na inicialização da API atual.

## Integração segura (trabalho ainda pendente)

- Configurar autenticação (OIDC/JWT) e exigir `iss`, `aud`, assinatura e expiração válidos.
- Migrar os registros financeiros com uma identidade estável por recurso e `ResidenciaId`/FKs reais, com plano de backup, migrações versionadas e rollback.
- Impedir que o cliente escolha o dono ou o papel ao inserir/editar recursos.
- Autorização nas consultas do banco, não apenas pós-filtragem ou checagem por ID.
- Testar na API real tentativas entre residências, revogações, recursos ausentes, totalizadores e exclusões.

**Não usar em produção nem fechar a issue de autenticação individual com base apenas nesta etapa.** PR empilhado sobre #18, que depende de #17, que depende de #16. Nenhum merge automático na `main`.
