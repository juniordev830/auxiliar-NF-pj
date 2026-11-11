@echo off
setlocal EnableExtensions
cd /d "%~dp0.."
set "BASE_URL=http://127.0.0.1:5000"

echo === Diagnostico local - Controle de Gastos ===
where dotnet >NUL 2>&1
if errorlevel 1 (
    echo AVISO: .NET SDK nao encontrado no PATH.
    echo Instale o SDK .NET 8 em https://dotnet.microsoft.com/download/dotnet/8.0
    echo Abra um novo terminal depois da instalacao.
) else (
    echo .NET encontrado:
    dotnet --version
)

where curl.exe >NUL 2>&1
if errorlevel 1 (
    echo ERRO: curl.exe nao encontrado. Execute no PowerShell:
    echo   Invoke-RestMethod http://127.0.0.1:5000/api/health
    exit /b 2
)

echo.
echo Verificando API em %BASE_URL%/api/health ...
curl.exe --silent --show-error --fail --connect-timeout 3 --max-time 6 "%BASE_URL%/api/health"
if errorlevel 1 (
    echo.
    echo FALHA: a API local nao esta respondendo.
    echo Na raiz do repositorio, execute:
    echo   dotnet restore ControladorGastos/ControladorGastos.csproj
    echo   dotnet run --project ControladorGastos/ControladorGastos.csproj
    echo Mantenha o terminal do servidor aberto e execute este diagnostico novamente.
    exit /b 1
)

echo.
echo OK: API local respondeu.
echo Verificando o painel em %BASE_URL%/ ...
curl.exe --silent --show-error --fail --connect-timeout 3 --max-time 6 --output NUL "%BASE_URL%/"
if errorlevel 1 (
    echo FALHA: a API responde, mas o painel nao foi encontrado.
    echo Atualize a branch e reinicie o servidor.
    exit /b 1
)
echo OK: painel disponivel.
echo Abra no navegador: %BASE_URL%/
exit /b 0
