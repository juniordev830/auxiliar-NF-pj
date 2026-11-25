# Validação técnica — Auxiliar PJ

O projeto inclui API residencial, módulo PJ e gerador Python. Não emite nota fiscal. Use apenas dados fictícios.

## Validação local

1. Siga o [guia rápido](../GUIA_RAPIDO.md) para instalar .NET 8, restaurar dependências, gerar tokens e iniciar o servidor.
2. Confirme GET http://127.0.0.1:5000/api/health e abra o painel.
3. Teste uma receita e uma despesa na mesma competência, inclusive saldo negativo e mês vazio.
4. Marque pagamento, reabra-o e teste vencimentos e paginação.
5. Exporte CSV e confira os campos Data, Categoria, Valor, Tipo, Descricao, Status, Contraparte, Vencimento e Pagamento.
6. Verifique acesso anônimo (401), leitura autorizada (200) e tentativa de escrita com leitor (403).
7. Teste valores inválidos, datas fora do intervalo, categorias vazias e textos com caracteres especiais.

Na raiz, com dependências instaladas:

```bash
dotnet build ControladorGastos/ControladorGastos.csproj
python -m pip install -r relatorios/requirements.txt
python -m pytest relatorios/tests -q
python relatorios/gerar_relatorio.py relatorios/exemplo-pj.csv --saida relatorio-pj.html
```

O cliente Swift tem testes próprios: `cd swift-client && swift test` em ambiente Swift compatível.

## Migrações e regressão

As migrações EF Core são aplicadas na inicialização para ambos os bancos. O arquivo [test_sqlite_upgrade.py](../tests/test_sqlite_upgrade.py) é utilizado no CI para verificar atualização de instalações legadas. Faça backup com a aplicação parada antes de atualizar; confira contagens, totais e exportações depois. Nunca apague arquivos de dados para resolver falhas.

O [workflow principal](../.github/workflows/ci.yml) executa build, auditoria NuGet, teste de migração, verificações básicas de API/autenticação e testes Python. O [workflow Swift](../.github/workflows/swift-client.yml) valida o cliente. Consulte os resultados no GitHub Actions; a presença de testes não garante segurança de produção.

## Pendências antes de produção

- Cobertura de integração mais ampla para operações PJ, paginação e exportação.
- Identidade individual e autorização por empresa e recurso; não existe isolamento multiusuário.
- Backup/recuperação automatizados, auditoria, HTTPS, revisão de segurança e retenção de dados.
- Validação contábil antes de qualquer cadastro fiscal, cálculo de tributos ou emissão de notas.
