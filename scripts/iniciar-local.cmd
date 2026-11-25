@echo off
setlocal EnableExtensions
cd /d "%~dp0.."
where dotnet >NUL 2>&1
if errorlevel 1 (
    echo Instale o SDK .NET 8 e abra um novo terminal.
    exit /b 1
)
dotnet --list-sdks | findstr /b "8." >NUL
if errorlevel 1 (
    echo SDK .NET 8 nao encontrado.
    exit /b 1
)
dotnet restore ControladorGastos/ControladorGastos.csproj
if errorlevel 1 exit /b 1
echo O token administrador sera mostrado somente neste terminal. Nao compartilhe.
powershell.exe -NoProfile -Command "$rng=[System.Security.Cryptography.RandomNumberGenerator]::Create(); $b=New-Object byte[] 32; $rng.GetBytes($b); $env:GASTOS_READ_TOKEN=[Convert]::ToBase64String($b); $rng.GetBytes($b); $env:GASTOS_ADMIN_TOKEN=[Convert]::ToBase64String($b); $rng.Dispose(); Write-Host ('Token administrador: '+$env:GASTOS_ADMIN_TOKEN); dotnet run --project ControladorGastos/ControladorGastos.csproj; exit $LASTEXITCODE"
exit /b %errorlevel%
