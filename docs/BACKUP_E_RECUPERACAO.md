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

Guarde backups fora do Git, em armazenamento protegido e preferencialmente criptografado. SHA-256 detecta corrupção acidental, não autentica um manifesto alterado por terceiro. O script não criptografa dados, não agenda backups e não controla se a aplicação está em execução. No Windows configure permissões do diretório pelo sistema. Faça testes periódicos de recuperação.

A restauração valida o tamanho e a estrutura do manifesto e recusa links simbólicos e arquivos auxiliares SQLite no diretório de cópia. Após recuperar uma cópia anterior, rotacione as credenciais individuais que estavam ativas no momento do backup. O banco recuperado contém o estado de revogação da data da cópia.
