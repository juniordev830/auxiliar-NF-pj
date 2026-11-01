# Controle de Gastos Residenciais

Projeto planejado para registrar receitas e despesas de uma residência, relacionar transações a pessoas e gerar resumos financeiros.

## Estado atual do repositório

**A versão atualmente publicada contém documentação, mas não inclui o código da aplicação descrito em alguns documentos antigos.** Portanto, as instruções de execução, telas e funcionalidades abaixo não podem ser reproduzidas a partir deste repositório até que os projetos de backend e frontend sejam versionados.

## Escopo funcional planejado

- Cadastro de pessoas da residência.
- Registro de receitas e despesas.
- Regra de negócio para limitar o tipo de transação de menores de idade.
- Relatórios de receitas, despesas e saldo.
- Persistência de dados em banco local.

Esses itens representam o escopo documentado, não uma declaração de que a aplicação esteja atualmente implementada.

## Stack planejada

- Backend: ASP.NET Core / C#
- Frontend: React e TypeScript
- Persistência: SQLite

## Documentação disponível

- [DOCUMENTACAO.md](DOCUMENTACAO.md): descrição detalhada do projeto e das regras de negócio.
- [GUIA_RAPIDO.md](GUIA_RAPIDO.md): referência resumida.

## Próximos passos para tornar o projeto executável

1. Adicionar o projeto backend com arquivo `.csproj` e código-fonte.
2. Adicionar o frontend com `package.json` e código-fonte.
3. Incluir exemplos de configuração sem segredos.
4. Documentar os comandos reais de instalação, execução e testes.
5. Implementar e testar as regras de negócio no backend; a validação visual sozinha não é suficiente.
6. Atualizar este README após validar os comandos em uma instalação limpa.

## Segurança e privacidade

Não publique planilhas reais de orçamento doméstico, nomes completos, informações financeiras pessoais, credenciais ou bancos de dados com informações identificáveis. Use apenas dados fictícios nos exemplos.

## Autor

João Junior — [GitHub](https://github.com/juniordev830)
