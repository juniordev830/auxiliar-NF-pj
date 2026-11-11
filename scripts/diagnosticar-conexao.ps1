# Diagnostico da API local no Windows (PowerShell)
# Execute na raiz do repositorio: .\scripts\diagnosticar-conexao.ps1

$ErrorActionPreference = "Stop"
$baseUrl = "http://127.0.0.1:5000"

if (-not (Get-Command dotnet -ErrorAction SilentlyContinue)) {
    Write-Host "ERRO: .NET SDK nao encontrado. Instale o SDK .NET 8." -ForegroundColor Red
    exit 1
}

Write-Host ("SDK instalado: " + (& dotnet --version))
Write-Host "Testando a API em $baseUrl/api/health ..."

try {
    $health = Invoke-RestMethod -Uri "$baseUrl/api/health" -TimeoutSec 5
    if ($health.status -ne "ok") {
        throw "A API respondeu, mas o estado informado nao foi 'ok'."
    }
    Write-Host "OK: API conectada localmente." -ForegroundColor Green
} catch {
    Write-Host "FALHA: servidor indisponivel na porta 5000." -ForegroundColor Red
    Write-Host "Na raiz do repositorio, rode:"
    Write-Host "  dotnet restore ControladorGastos/ControladorGastos.csproj"
    Write-Host "  dotnet run --project ControladorGastos/ControladorGastos.csproj"
    Write-Host "Deixe esse terminal aberto e execute novamente este diagnostico em outro."
    Write-Host "Detalhes: $($_.Exception.Message)"
    exit 1
}

try {
    $page = Invoke-WebRequest -Uri "$baseUrl/" -TimeoutSec 5 -UseBasicParsing
    if ($page.Content -notmatch "Controle de Gastos") {
        throw "A resposta da pagina inicial nao corresponde ao painel esperado."
    }
    Write-Host "OK: painel web local disponivel em $baseUrl/" -ForegroundColor Green
    Write-Host "Abra no navegador: $baseUrl/"
} catch {
    Write-Host "A API funciona, mas o painel web nao foi encontrado." -ForegroundColor Yellow
    Write-Host "Atualize a branch, pare e reinicie a API para servir os arquivos web."
    Write-Host "Detalhes: $($_.Exception.Message)"
    exit 1
}
