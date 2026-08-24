[CmdletBinding()]
param(
    [switch]$BackendOnly
)

$ErrorActionPreference = "Stop"
$scriptsDirectory = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = Split-Path -Parent $scriptsDirectory
$backendDirectory = Join-Path $projectRoot "backend"
$frontendDirectory = Join-Path $projectRoot "frontend"
$pythonExecutable = Join-Path $projectRoot ".venv\Scripts\python.exe"

function Invoke-CheckedCommand {
    param(
        [Parameter(Mandatory = $true)][string]$Label,
        [Parameter(Mandatory = $true)][string]$FilePath,
        [Parameter(Mandatory = $true)][string[]]$Arguments,
        [Parameter(Mandatory = $true)][string]$WorkingDirectory
    )

    Write-Host "`n==> $Label"
    Push-Location $WorkingDirectory
    try {
        & $FilePath @Arguments
        if ($LASTEXITCODE -ne 0) {
            throw "$Label falló con código $LASTEXITCODE."
        }
    }
    finally {
        Pop-Location
    }
}

if (-not (Test-Path -LiteralPath $pythonExecutable -PathType Leaf)) {
    throw "No se encontró el entorno Python en $pythonExecutable. Créalo e instala backend\requirements-dev.txt."
}

Invoke-CheckedCommand `
    -Label "Pruebas automatizadas del backend" `
    -FilePath $pythonExecutable `
    -Arguments @("-m", "pytest", "-p", "no:cacheprovider") `
    -WorkingDirectory $backendDirectory

Invoke-CheckedCommand `
    -Label "Sincronización de modelos y migraciones" `
    -FilePath $pythonExecutable `
    -Arguments @("-m", "alembic", "check") `
    -WorkingDirectory $backendDirectory

if ($BackendOnly) {
    Write-Host "`nVerificación backend completada. El frontend se omitió mediante -BackendOnly."
    exit 0
}

$nodeModulesDirectory = Join-Path $frontendDirectory "node_modules"
$packageLock = Join-Path $frontendDirectory "package-lock.json"
if (-not (Test-Path -LiteralPath $nodeModulesDirectory -PathType Container)) {
    throw "Falta frontend\node_modules. Ejecuta npm install desde la carpeta frontend."
}
if (-not (Test-Path -LiteralPath $packageLock -PathType Leaf)) {
    throw "Falta frontend\package-lock.json. Ejecuta npm install y conserva el lockfile generado."
}

$npmCommand = Get-Command npm.cmd -ErrorAction SilentlyContinue
if (-not $npmCommand) {
    throw "No se encontró npm.cmd en PATH. Instala Node.js LTS y abre una nueva terminal."
}

Invoke-CheckedCommand `
    -Label "Validación de tipos del frontend" `
    -FilePath $npmCommand.Source `
    -Arguments @("run", "typecheck") `
    -WorkingDirectory $frontendDirectory

Invoke-CheckedCommand `
    -Label "Pruebas automatizadas del frontend" `
    -FilePath $npmCommand.Source `
    -Arguments @("test") `
    -WorkingDirectory $frontendDirectory

Invoke-CheckedCommand `
    -Label "Build de producción del frontend" `
    -FilePath $npmCommand.Source `
    -Arguments @("run", "build") `
    -WorkingDirectory $frontendDirectory

Write-Host "`nVerificación completa finalizada correctamente."
