# Guia rápido — Auxiliar PJ

1. Instale o **SDK .NET 8** e o Git. Não é necessário instalar Node.js.
2. Clone ou abra este repositório no VS Code.
3. Na raiz, execute em PowerShell:

```powershell
dotnet restore ControladorGastos/ControladorGastos.csproj
$rng = [System.Security.Cryptography.RandomNumberGenerator]::Create()
$bytes = New-Object byte[] 32
$rng.GetBytes($bytes)
$env:GASTOS_READ_TOKEN = [Convert]::ToBase64String($bytes)
$rng.GetBytes($bytes)
$env:GASTOS_ADMIN_TOKEN = [Convert]::ToBase64String($bytes)
$rng.Dispose()
$env:GASTOS_ADMIN_TOKEN
dotnet run --project ControladorGastos/ControladorGastos.csproj
```

O comando que mostra o token deve ser usado somente em terminal privado. Copie o token administrador e não o compartilhe. Os comandos são compatíveis com Windows PowerShell 5.1. Para Linux/macOS, veja o [README](README.md).

4. Abra http://127.0.0.1:5000/ e informe o token no campo de acesso.
5. Cadastre uma receita e uma despesa **fictícias**, selecione a competência e confira o resumo.
6. Marque um lançamento como pago ou reabra-o. Exporte o CSV se desejar gerar um relatório.

O painel é servido pela API. O módulo residencial é acessível por API, não por uma interface própria.

## Diagnóstico

Em outro terminal, na raiz:

```powershell
.\scripts\diagnosticar-conexao.cmd
```

Se dotnet não estiver no PATH, instale o SDK .NET 8 e abra outro terminal. Se houver erro 401, confira o token; 403 indica falta de permissão de escrita. Se houver falha de migração, preserve os bancos e consulte a [documentação técnica](DOCUMENTACAO.md).

## Relatórios

Com Python instalado:

```powershell
python -m pip install -r relatorios/requirements.txt
python relatorios/gerar_relatorio.py relatorios/exemplo-pj.csv --saida relatorio-pj.html
```

Abra o HTML gerado no navegador. Consulte o [guia de relatórios](relatorios/README.md) para usar um CSV exportado.

**Atenção:** a aplicação é local, com migrações automáticas na inicialização e tokens obrigatórios. Não publique na internet, não use dados reais nesta fase e faça backup antes de atualizar. O projeto não emite notas fiscais.
