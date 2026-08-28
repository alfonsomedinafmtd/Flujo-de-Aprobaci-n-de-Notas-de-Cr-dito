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
            throw "$Label fallo con codigo $LASTEXITCODE."
        }
    }
    finally {
        Pop-Location
    }
}

if (-not (Test-Path -LiteralPath $pythonExecutable -PathType Leaf)) {
    throw "No se encontro el entorno Python en $pythonExecutable. Crealo e instala backend\requirements-dev.txt."
}

Invoke-CheckedCommand `
    -Label "Integridad de dependencias Python" `
    -FilePath $pythonExecutable `
    -Arguments @("-m", "pip", "check") `
    -WorkingDirectory $projectRoot

Invoke-CheckedCommand `
    -Label "Analisis estatico de seguridad del backend" `
    -FilePath $pythonExecutable `
    -Arguments @("-m", "bandit", "-r", "app", "-q") `
    -WorkingDirectory $backendDirectory

Invoke-CheckedCommand `
    -Label "Vulnerabilidades conocidas de dependencias Python" `
    -FilePath $pythonExecutable `
    -Arguments @("-m", "pip_audit", "-r", "requirements-dev.txt") `
    -WorkingDirectory $backendDirectory

$gitCommand = Get-Command git.exe -CommandType Application -ErrorAction SilentlyContinue
if (-not $gitCommand) {
    $gitCommand = Get-Command git -CommandType Application -ErrorAction SilentlyContinue
}
if (-not $gitCommand) {
    throw "No se encontro Git para revisar patrones sensibles en archivos versionados."
}

Write-Host "`n==> Patrones sensibles en archivos versionados"
$sensitivePattern = "AKIA[0-9A-Z]{16}|gh[pousr]_[A-Za-z0-9_]{20,}|-----BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY-----"
& $gitCommand.Source -C $projectRoot grep -n -I -E $sensitivePattern -- .
$secretScanExitCode = $LASTEXITCODE
if ($secretScanExitCode -eq 0) {
    throw "Se detecto un posible secreto en un archivo versionado. Revisa la salida anterior."
}
if ($secretScanExitCode -gt 1) {
    throw "La revision de patrones sensibles fallo con codigo $secretScanExitCode."
}
Write-Host "Sin coincidencias de claves, tokens de GitHub ni llaves privadas."

if ($BackendOnly) {
    Write-Host "`nAuditoria de seguridad backend finalizada. npm se omitio mediante -BackendOnly."
    exit 0
}

$packageLock = Join-Path $frontendDirectory "package-lock.json"
if (-not (Test-Path -LiteralPath $packageLock -PathType Leaf)) {
    throw "Falta frontend\package-lock.json. npm audit debe ejecutarse desde frontend y requiere ese archivo."
}

$npmCommand = Get-Command npm.cmd -ErrorAction SilentlyContinue
if (-not $npmCommand) {
    throw "No se encontro npm.cmd en PATH. Instala Node.js LTS y abre una nueva terminal."
}

$previousNodeUseSystemCa = $env:NODE_USE_SYSTEM_CA
$env:NODE_USE_SYSTEM_CA = "1"
try {
    Invoke-CheckedCommand `
        -Label "Vulnerabilidades conocidas de dependencias npm" `
        -FilePath $npmCommand.Source `
        -Arguments @("audit", "--audit-level=moderate", "--no-fund") `
        -WorkingDirectory $frontendDirectory
}
finally {
    if ($null -eq $previousNodeUseSystemCa) {
        Remove-Item Env:NODE_USE_SYSTEM_CA -ErrorAction SilentlyContinue
    }
    else {
        $env:NODE_USE_SYSTEM_CA = $previousNodeUseSystemCa
    }
}

Write-Host "`nAuditoria de seguridad finalizada correctamente."
