# Revisão de segurança — integração PJ

## Controles introduzidos

- API restrita ao loopback, tokens distintos e obrigatórios; autorização de leitura/escrita preservada.
- Cache-Control no-store nas respostas da API, proteção contra enquadramento, nosniff e política de conteúdo restritiva (scripts locais; estilos inline ainda permitidos).
- Sessão web apenas em memória, limpeza de dados no logout/401 e temporizador local. Respostas de consultas obsoletas são descartadas.
- Histórico PJ transacional, exclusão lógica, concorrência otimista durante operações simultâneas e paginação no SQL.
- Escape de HTML e de campos CSV, centavos inteiros nos totais e diagnóstico de entradas inválidas.
- Backup em diretório novo, verificação de integridade SQLite e hashes; restauração não substitui os originais.

## Limitações e riscos remanescentes

- Tokens compartilhados não identificam pessoas, não expiram no servidor e não são revogados pelo logout; não há isolamento por empresa.
- Histórico não é imutável contra acesso direto ao banco, não inclui ações anteriores à migração e contém dados financeiros; precisa de retenção e acesso apropriados. Não representa auditoria contábil formal.
- Concorrência otimista protege alterações simultâneas durante a requisição, mas não impede toda edição baseada em formulário desatualizado. Considerar versionamento HTTP/If-Match.
- Backups não são criptografados nem agendados, e o hash não protege contra alguém que altera o manifesto e os dados juntos. Pare a aplicação antes de copiar os dois bancos.
- Ainda não há teste E2E de navegador, análise dinâmica de segurança, teste de carga, MFA, HTTPS ou identidade individual. Não publicar na internet nem usar dados financeiros reais.
- A política CSP depende da versão do frontend sem scripts inline. Testar o conjunto integrado, não aplicar isoladamente ao painel legado.

## Validação

CI: build e auditoria NuGet, autenticação, migração SQLite, ciclo PJ, testes Python/Swift e regressões JS/backup em workflows separados. Revisar resultados no GitHub Actions antes de qualquer integração à main. A revisão é estática e não certifica ausência de vulnerabilidades.
