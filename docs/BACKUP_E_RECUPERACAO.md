# Instalação local e recuperação de bancos

Windows: na raiz, execute `scripts\\iniciar-local.cmd` em CMD ou PowerShell. O script restaura dependências, exige SDK 8, cria tokens efêmeros com gerador criptográfico e inicia a API. Copie o token administrador do terminal privado para o painel. Nunca registre ou compartilhe o token. A execução não modifica a política PowerShell.

## Backup offline

Pare o servidor antes de criar o backup: os dois bancos são independentes e a consistência entre eles depende de não haver operações em curso. Localize os arquivos reais de ambos os bancos (normalmente na pasta ControladorGastos ou na localização configurada pelas connection strings). Exemplo com Python 3:

```bash
python scripts/backup_sqlite.py backup --residencial ControladorGastos/controlador-gastos.db --pj ControladorGastos/auxiliar-pj.db --destino backups/antes-da-atualizacao
python scripts/backup_sqlite.py restore --origem backups/antes-da-atualizacao --destino recuperacao/teste
```

O comando utiliza a API de backup SQLite, verifica integridade e grava manifesto SHA-256. A recuperação recusa arquivos alterados e destinos já existentes; os bancos originais nunca são substituídos automaticamente.

Para usar bancos recuperados: mantenha a API parada, preserve os arquivos originais e configure ConnectionStrings__DefaultConnection e ConnectionStrings__AuxiliarPj para os caminhos recuperados (Data Source=...). Inicie e confira totais com dados de teste. Não execute rollback destrutivo de migrações.

Guarde backups fora do Git, em armazenamento protegido. Cópias antigas e novas sem chave usam SHA-256 para detectar corrupção acidental. No Windows, restrinja o acesso ao diretório de backups e da chave pelas permissões do sistema. Faça testes periódicos de recuperação.

A restauração valida o tamanho e a estrutura do manifesto e recusa links simbólicos e arquivos auxiliares SQLite no diretório de cópia. Após recuperar uma cópia anterior, rotacione as credenciais individuais que estavam ativas no momento do backup. O banco recuperado contém o estado de revogação da data da cópia.


## Backup criptografado

Use uma chave aleatória de 32 bytes criada em um diretório privado, fora do Git. Guarde a chave separada da cópia, com recuperação testada. O arquivo de chave é criado sem sobrescrever um arquivo existente.

```bash
python -m pip install -r scripts/requirements-backup.txt
python scripts/backup_sqlite.py gerar-chave --destino /caminho/privado/pj-backup.key
python scripts/backup_sqlite.py backup --residencial ControladorGastos/controlador-gastos.db --pj ControladorGastos/auxiliar-pj.db --destino backups/seguro --chave-arquivo /caminho/privado/pj-backup.key
python scripts/backup_sqlite.py restore --origem backups/seguro --destino recuperacao/teste --chave-arquivo /caminho/privado/pj-backup.key
```

O modo criptografado usa AES-256-GCM em blocos de leitura e autentica o manifesto e cada banco. A recuperação só publica os arquivos após validar a autenticação, os hashes e a integridade SQLite. O trabalho temporário e o diretório de recuperação contêm dados em claro, portanto use um volume local protegido para as operações.
