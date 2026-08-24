[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"

$scriptDirectory = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = (Resolve-Path -LiteralPath (Join-Path $scriptDirectory "..")).Path
$results = New-Object System.Collections.Generic.List[object]

function Add-AuditResult {
    param(
        [Parameter(Mandatory = $true)]
        [ValidateSet("PASS", "WARN", "FAIL")]
        [string]$Level,

        [Parameter(Mandatory = $true)]
        [string]$Area,

        [Parameter(Mandatory = $true)]
        [string]$Message
    )

    $results.Add([PSCustomObject]@{
        Level = $Level
        Area = $Area
        Message = $Message
    })

    $color = switch ($Level) {
        "PASS" { "Green" }
        "WARN" { "Yellow" }
        "FAIL" { "Red" }
    }

    Write-Host ("[{0}] {1}: {2}" -f $Level, $Area, $Message) -ForegroundColor $color
}

function Get-GitExecutable {
    $pathGit = Get-Command git.exe -CommandType Application -ErrorAction SilentlyContinue
    if (-not $pathGit) {
        $pathGit = Get-Command git -CommandType Application -ErrorAction SilentlyContinue
    }

    if ($pathGit) {
        return $pathGit.Source
    }

    $fallbackGit = Join-Path $projectRoot ".tools\mingit\cmd\git.exe"
    if (Test-Path -LiteralPath $fallbackGit -PathType Leaf) {
        return $fallbackGit
    }

    return $null
}

function Invoke-ReadOnlyGit {
    param(
        [Parameter(Mandatory = $true)]
        [string[]]$Arguments
    )

    $previousErrorActionPreference = $ErrorActionPreference
    $ErrorActionPreference = "Continue"
    try {
        $output = @(& $script:gitExecutable --no-optional-locks -C $projectRoot @Arguments 2>$null)
        $exitCode = $LASTEXITCODE
    }
    finally {
        $ErrorActionPreference = $previousErrorActionPreference
    }

    return [PSCustomObject]@{
        ExitCode = $exitCode
        Output = @($output | ForEach-Object { $_.ToString() })
    }
}

function Test-IsProhibitedTrackedPath {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Path
    )

    $normalizedPath = $Path.Replace("\", "/")
    $leafName = [System.IO.Path]::GetFileName($normalizedPath)

    $isEnvFile = $leafName -eq ".env" -or $leafName -like ".env.*"
    $isEnvExample = $leafName -match '^\.env\.(example|sample|template)(\..+)?$'
    if ($isEnvFile -and -not $isEnvExample) {
        return $true
    }

    if ($normalizedPath -match '(?i)\.(db|sqlite|sqlite3)(-[^/]*)?$') {
        return $true
    }

    if ($normalizedPath -match '(?i)(^|/)(\.venv|\.tools|node_modules|dist)(/|$)') {
        return $true
    }

    return $false
}

Write-Host "Auditoria de entrega (solo lectura)"
Write-Host "Raiz: $projectRoot"
Write-Host ""

$gitExecutable = Get-GitExecutable
if (-not $gitExecutable) {
    Add-AuditResult -Level "WARN" -Area "Git" -Message "No se encontro Git en PATH ni en .tools; se omiten las comprobaciones Git."
}
else {
    Add-AuditResult -Level "PASS" -Area "Git" -Message "Ejecutable encontrado en $gitExecutable"

    $repositoryCheck = Invoke-ReadOnlyGit -Arguments @("rev-parse", "--is-inside-work-tree")
    if ($repositoryCheck.ExitCode -ne 0 -or ($repositoryCheck.Output -join "") -ne "true") {
        Add-AuditResult -Level "WARN" -Area "Repositorio" -Message "La raiz no pudo confirmarse como repositorio Git; se omiten sus comprobaciones."
    }
    else {
        $status = Invoke-ReadOnlyGit -Arguments @("status", "--porcelain=v1", "--untracked-files=all")
        if ($status.ExitCode -ne 0) {
            Add-AuditResult -Level "WARN" -Area "Worktree" -Message "No se pudo consultar el estado del arbol de trabajo."
        }
        elseif ($status.Output.Count -eq 0) {
            Add-AuditResult -Level "PASS" -Area "Worktree" -Message "El arbol de trabajo esta limpio."
        }
        else {
            Add-AuditResult -Level "WARN" -Area "Worktree" -Message ("Hay {0} cambio(s) pendiente(s) o archivo(s) no rastreado(s)." -f $status.Output.Count)
        }

        $userNameResult = Invoke-ReadOnlyGit -Arguments @("config", "--local", "--get", "user.name")
        $userEmailResult = Invoke-ReadOnlyGit -Arguments @("config", "--local", "--get", "user.email")
        $userName = ($userNameResult.Output -join "").Trim()
        $userEmail = ($userEmailResult.Output -join "").Trim()

        if ([string]::IsNullOrWhiteSpace($userName) -or [string]::IsNullOrWhiteSpace($userEmail)) {
            Add-AuditResult -Level "WARN" -Area "Identidad Git" -Message "Falta configurar user.name o user.email a nivel local."
        }
        elseif ($userEmail -ieq "candidato@example.invalid") {
            Add-AuditResult -Level "WARN" -Area "Identidad Git" -Message ("La identidad local sigue siendo temporal: {0} <{1}>." -f $userName, $userEmail)
        }
        else {
            Add-AuditResult -Level "PASS" -Area "Identidad Git" -Message ("Identidad local: {0} <{1}>." -f $userName, $userEmail)
        }

        $origin = Invoke-ReadOnlyGit -Arguments @("remote", "get-url", "origin")
        $originUrl = ($origin.Output -join "").Trim()
        if ($origin.ExitCode -ne 0 -or [string]::IsNullOrWhiteSpace($originUrl)) {
            Add-AuditResult -Level "WARN" -Area "Remote" -Message "No existe un remote origin configurado."
        }
        else {
            Add-AuditResult -Level "PASS" -Area "Remote" -Message "origin esta configurado."
        }

        $trackedFilesResult = Invoke-ReadOnlyGit -Arguments @("ls-files")
        if ($trackedFilesResult.ExitCode -ne 0) {
            Add-AuditResult -Level "WARN" -Area "Archivos rastreados" -Message "No se pudo revisar la lista de archivos versionados."
        }
        else {
            $prohibitedFiles = @(
                $trackedFilesResult.Output |
                    Where-Object { Test-IsProhibitedTrackedPath -Path $_ } |
                    Sort-Object -Unique
            )

            if ($prohibitedFiles.Count -eq 0) {
                Add-AuditResult -Level "PASS" -Area "Archivos sensibles" -Message "No hay archivos locales o sensibles prohibidos bajo seguimiento."
            }
            else {
                foreach ($prohibitedFile in $prohibitedFiles) {
                    Add-AuditResult -Level "FAIL" -Area "Archivo sensible" -Message ("Esta versionado y debe retirarse de la entrega: {0}" -f $prohibitedFile)
                }
            }
        }
    }
}

$requiredDocuments = @(
    "README.md",
    "docs\AI_USAGE.md",
    "docs\API_GUIDE.md",
    "docs\DECISIONS.md",
    "docs\DELIVERY_CHECKLIST.md",
    "docs\DEMO_GUIDE.md",
    "docs\ERD.md",
    "docs\PERMISSIONS.md",
    "docs\REQUIREMENTS_TRACEABILITY.md",
    "docs\TECHNICAL_DEFENSE.md"
)

$missingDocuments = @(
    $requiredDocuments | Where-Object {
        -not (Test-Path -LiteralPath (Join-Path $projectRoot $_) -PathType Leaf)
    }
)

if ($missingDocuments.Count -eq 0) {
    Add-AuditResult -Level "PASS" -Area "Documentacion" -Message ("Estan presentes los {0} documentos obligatorios." -f $requiredDocuments.Count)
}
else {
    foreach ($missingDocument in $missingDocuments) {
        Add-AuditResult -Level "FAIL" -Area "Documento obligatorio" -Message ("No se encontro {0}." -f $missingDocument)
    }
}

$packageLockPath = Join-Path $projectRoot "frontend\package-lock.json"
if (Test-Path -LiteralPath $packageLockPath -PathType Leaf) {
    Add-AuditResult -Level "PASS" -Area "Frontend npm" -Message "Existe frontend\package-lock.json."
}
else {
    Add-AuditResult -Level "WARN" -Area "Frontend npm" -Message "Falta package-lock.json; se generara cuando npm install pueda completarse."
}

$frontendDistPath = Join-Path $projectRoot "frontend\dist"
if (Test-Path -LiteralPath $frontendDistPath -PathType Container) {
    Add-AuditResult -Level "PASS" -Area "Build frontend" -Message "Existe frontend\dist."
}
else {
    Add-AuditResult -Level "WARN" -Area "Build frontend" -Message "Falta frontend\dist; sigue pendiente npm run build."
}

$passCount = @($results | Where-Object { $_.Level -eq "PASS" }).Count
$warnCount = @($results | Where-Object { $_.Level -eq "WARN" }).Count
$failCount = @($results | Where-Object { $_.Level -eq "FAIL" }).Count

Write-Host ""
Write-Host "Resumen"
Write-Host ("PASS: {0}  WARN: {1}  FAIL: {2}" -f $passCount, $warnCount, $failCount)

if ($failCount -gt 0) {
    Write-Host "Resultado: entrega bloqueada por fallos reales." -ForegroundColor Red
    exit 1
}

if ($warnCount -gt 0) {
    Write-Host "Resultado: sin fallos; revisa las advertencias antes de entregar." -ForegroundColor Yellow
}
else {
    Write-Host "Resultado: auditoria completada sin observaciones." -ForegroundColor Green
}

exit 0
