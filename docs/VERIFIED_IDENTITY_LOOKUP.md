# Identidade validada → conta persistida → permissão por residência

Esta branch fornece um elo de **domínio e persistência**, não uma solução de login.
A API atualmente usa tokens de operador local e **não autentica pessoas individualmente**.

## Novo componente

`ConsultaIdentidadeValidada.ResolverContaAsync` resolve uma conta já cadastrada pela combinação exata `Emissor + SujeitoExterno`. Se a combinação for desconhecida, nula, vazia ou maior que os limites do esquema, a resposta é `null`. Nunca cria automaticamente contas, vínculos ou residência.

`ConsultaIdentidadeValidada.PermiteAsync` resolve essa conta e invoca `ConsultaAcessoResidencia.PermiteAsync`, que lê as permissões persistidas para a residência do **recurso** e aplica a política de acesso existente. Sujeitos iguais vindos de emissores diferentes permanecem contas distintas.

## Fronteira de confiança obrigatória

**Não use esses métodos com valores digitados pelo cliente, cabeçalhos arbitrários, query strings ou claims obtidos de JWT não validado.** O código chamador precisa primeiro configurar um provedor confiável e validar criptograficamente assinatura, `iss`, `aud`, `exp` e demais requisitos do protocolo. Somente os valores obtidos de uma identidade autenticada e validada podem ser enviados à consulta.

A residência usada na autorização deve ser determinada a partir do recurso persistido no banco, não de um papel ou residência afirmados pelo cliente. O escopo financeiro atual ainda não tem associação de residência validada e não chama esse helper.

## Testes

```bash
dotnet test ControladorGastos.Tests/ControladorGastos.Tests.csproj --configuration Release
```

O teste em SQLite em memória verifica dois emissores que reutilizam o mesmo `subject`, permissões de leitura/escrita/exclusão, negação de acesso entre residências, claims vazios ou inválidos, identidade desconhecida e `Guid.Empty`.

## Próximas etapas antes de uma API multiusuária real

1. Definir e validar um provedor de identidade (OIDC/JWT) e obter `Emissor + SujeitoExterno` apenas do principal autenticado.
2. Criar migrações versionadas com backups e rollback para o banco de acesso.
3. Relacionar cada pessoa e transação ao escopo correto sem atribuir automaticamente dados legados a uma residência.
4. Integrar as verificações a **todas** as rotas e consultar recursos já filtrados pela residência antes de somar, editar ou excluir.
5. Testar ponta a ponta contas distintas em rotas reais com HTTP 401/403/404; auditar permissões, revogações e operações.

**Nenhuma dessas etapas de implantação está concluída nesta branch.** O protótipo continua destinado ao loopback. Não fazer merge automático na `main`.

## PRs de base

- [Política por residência — PR #16](https://github.com/juniordev830/controle-gastos-residenciais/pull/16)
- [Persistência das permissões — PR #17](https://github.com/juniordev830/controle-gastos-residenciais/pull/17)

Esta PR foi empilhada sobre a branch da PR #17; primeiro revisar e integrar a política e a persistência em ordem.
