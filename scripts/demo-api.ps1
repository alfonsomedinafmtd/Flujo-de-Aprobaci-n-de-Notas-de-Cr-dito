[CmdletBinding()]
param(
    [ValidateNotNullOrEmpty()]
    [string]$BaseUrl = "http://localhost:8000/api",

    [ValidateSet("approve", "reject")]
    [string]$Decision = "approve",

    [string]$Comment
)

Set-StrictMode -Version 2.0
$ErrorActionPreference = "Stop"
$collaborator = $null
$approver = $null

function Get-ApiErrorText {
    param(
        [Parameter(Mandatory = $true)]
        [System.Management.Automation.ErrorRecord]$ErrorRecord
    )

    if ($ErrorRecord.ErrorDetails -and $ErrorRecord.ErrorDetails.Message) {
        return $ErrorRecord.ErrorDetails.Message
    }

    return $ErrorRecord.Exception.Message
}

function Connect-DemoApi {
    param(
        [Parameter(Mandatory = $true)]
        [string]$ApiBaseUrl,

        [Parameter(Mandatory = $true)]
        [System.Management.Automation.PSCredential]$Credential
    )

    $session = New-Object Microsoft.PowerShell.Commands.WebRequestSession
    $plainPassword = $null
    $loginBody = $null

    try {
        $plainPassword = $Credential.GetNetworkCredential().Password
        $loginBody = @{
            username = $Credential.UserName
            password = $plainPassword
        } | ConvertTo-Json

        $login = Invoke-RestMethod `
            -Method Post `
            -Uri "$ApiBaseUrl/auth/login" `
            -ContentType "application/json" `
            -Body $loginBody `
            -WebSession $session

        return [PSCustomObject]@{
            User = $login.user
            CsrfToken = $login.csrf_token
            Session = $session
        }
    }
    finally {
        $loginBody = $null
        $plainPassword = $null
    }
}

try {
    $BaseUrl = $BaseUrl.TrimEnd("/")
    $parsedBaseUrl = $null

    if (-not [Uri]::TryCreate($BaseUrl, [UriKind]::Absolute, [ref]$parsedBaseUrl)) {
        throw "BaseUrl must be an absolute HTTP or HTTPS URL."
    }

    if ($parsedBaseUrl.Scheme -notin @("http", "https")) {
        throw "BaseUrl must use HTTP or HTTPS."
    }

    if ($Decision -eq "reject" -and [string]::IsNullOrWhiteSpace($Comment)) {
        throw "Comment is required when Decision is reject."
    }

    Write-Host "Checking API health at $BaseUrl/health ..."
    $health = Invoke-RestMethod -Method Get -Uri "$BaseUrl/health"
    if ($health.status -ne "ok") {
        throw "The API health endpoint did not return status ok."
    }
    Write-Host "API health: ok"

    Write-Host "Enter COLLABORATOR credentials. The password will not be saved or displayed."
    $collaboratorCredential = Get-Credential -Message "Credit note demo - collaborator"
    if ($null -eq $collaboratorCredential) {
        throw "Collaborator credentials were not provided."
    }

    Write-Host "Enter DEPARTMENT_HEAD or ADMIN credentials. The password will not be saved or displayed."
    $approverCredential = Get-Credential -Message "Credit note demo - approver"
    if ($null -eq $approverCredential) {
        throw "Approver credentials were not provided."
    }

    Write-Host "Signing in with separate sessions ..."
    $collaborator = Connect-DemoApi -ApiBaseUrl $BaseUrl -Credential $collaboratorCredential
    $approver = Connect-DemoApi -ApiBaseUrl $BaseUrl -Credential $approverCredential

    if ($collaborator.User.role -ne "COLLABORATOR") {
        throw "The first account must have the COLLABORATOR role."
    }

    if ($approver.User.role -notin @("DEPARTMENT_HEAD", "ADMIN")) {
        throw "The second account must have the DEPARTMENT_HEAD or ADMIN role."
    }

    if (
        $approver.User.role -eq "DEPARTMENT_HEAD" -and
        $approver.User.department_id -ne $collaborator.User.department_id
    ) {
        throw "The department head must belong to the collaborator department."
    }

    Write-Host ("Collaborator: {0} ({1})" -f $collaborator.User.username, $collaborator.User.department_name)
    Write-Host ("Approver: {0} ({1})" -f $approver.User.username, $approver.User.role)

    $catalog = Invoke-RestMethod `
        -Method Get `
        -Uri "$BaseUrl/credit-notes/catalog" `
        -WebSession $collaborator.Session

    $stores = @($catalog.stores)
    $companies = @($catalog.companies)
    if ($stores.Count -eq 0 -or $companies.Count -eq 0) {
        throw "The active store and company catalogs must contain at least one item."
    }

    $createBody = @{
        amount = "1250.50"
        currency = "USD"
        reason = "Automated demo adjustment for billing difference"
        store_id = $stores[0].id
        company_id = $companies[0].id
    } | ConvertTo-Json

    Write-Host "Creating a pending credit note ..."
    $createdNote = Invoke-RestMethod `
        -Method Post `
        -Uri "$BaseUrl/credit-notes" `
        -ContentType "application/json" `
        -Body $createBody `
        -WebSession $collaborator.Session `
        -Headers @{ "X-CSRF-Token" = $collaborator.CsrfToken }

    Write-Host ("Created note: id={0}, status={1}, version={2}" -f $createdNote.id, $createdNote.status, $createdNote.version)

    Write-Host "Reading the note with the approver session ..."
    $pendingNote = Invoke-RestMethod `
        -Method Get `
        -Uri "$BaseUrl/credit-notes/$($createdNote.id)" `
        -WebSession $approver.Session

    if ($pendingNote.status -ne "PENDING") {
        throw "The newly created note is not pending."
    }

    $decisionBody = @{
        expected_version = $pendingNote.version
        comment = if ([string]::IsNullOrWhiteSpace($Comment)) { $null } else { $Comment.Trim() }
    } | ConvertTo-Json

    Write-Host ("Applying decision: {0} ..." -f $Decision)
    $decidedNote = Invoke-RestMethod `
        -Method Post `
        -Uri "$BaseUrl/credit-notes/$($pendingNote.id)/$Decision" `
        -ContentType "application/json" `
        -Body $decisionBody `
        -WebSession $approver.Session `
        -Headers @{ "X-CSRF-Token" = $approver.CsrfToken }

    $finalNote = Invoke-RestMethod `
        -Method Get `
        -Uri "$BaseUrl/credit-notes/$($decidedNote.id)" `
        -WebSession $approver.Session

    $summary = Invoke-RestMethod `
        -Method Get `
        -Uri "$BaseUrl/credit-notes/summary" `
        -WebSession $approver.Session

    Write-Host ""
    Write-Host "Demo completed successfully."
    Write-Host ("Note id: {0}" -f $finalNote.id)
    Write-Host ("Final status: {0}" -f $finalNote.status)
    Write-Host ("Final version: {0}" -f $finalNote.version)

    Write-Host ""
    Write-Host "Audit events:"
    @($finalNote.events) |
        Select-Object action, previous_status, new_status, actor_username, actor_role, occurred_at, comment |
        Format-Table -AutoSize

    Write-Host "Approver scope summary:"
    [PSCustomObject]@{
        total = $summary.total
        pending = $summary.pending
        approved = $summary.approved
        rejected = $summary.rejected
    } | Format-List
}
catch {
    $message = Get-ApiErrorText -ErrorRecord $_
    Write-Error ("API demo failed: {0}" -f $message)
    exit 1
}
finally {
    foreach ($connection in @($collaborator, $approver)) {
        if ($null -ne $connection) {
            try {
                Invoke-RestMethod `
                    -Method Post `
                    -Uri "$BaseUrl/auth/logout" `
                    -WebSession $connection.Session `
                    -Headers @{ "X-CSRF-Token" = $connection.CsrfToken } |
                    Out-Null
            }
            catch {
                Write-Warning "A demo session could not be revoked and will expire automatically."
            }
        }
    }
    $collaboratorCredential = $null
    $approverCredential = $null
}
