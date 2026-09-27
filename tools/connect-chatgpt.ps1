param(
    [Parameter(Mandatory=$true)][ValidatePattern('^tunnel_[a-zA-Z0-9]+$')][string]$TunnelId,
    [Parameter(Mandatory=$true)][string]$ImageModel,
    [Parameter(Mandatory=$true)][string]$ReviewModel
)
$ErrorActionPreference = 'Stop'
$repoRoot = Split-Path -Parent $PSScriptRoot
$client = Join-Path $repoRoot '.harness/runtime/tunnel-client-0.0.14/tunnel-client.exe'
if (-not (Test-Path -LiteralPath $client -PathType Leaf)) { throw 'Install the official tunnel client first.' }
foreach ($keyName in @('OPENAI_API_KEY','CONTROL_PLANE_API_KEY')) {
    if (-not [Environment]::GetEnvironmentVariable($keyName,'Process')) {
        $secret = Read-Host "Enter $keyName locally (not saved to disk)" -AsSecureString
        $credential = New-Object System.Management.Automation.PSCredential('runtime',$secret)
        [Environment]::SetEnvironmentVariable($keyName,$credential.GetNetworkCredential().Password,'Process')
        $credential = $null
        $secret = $null
    }
    if (-not [Environment]::GetEnvironmentVariable($keyName,'Process')) { throw "Missing $keyName" }
}
$env:AGENTIC_IMAGE_MODEL = $ImageModel
$env:AGENTIC_REVIEW_MODEL = $ReviewModel
# Reuse the same launcher and configuration as local diagnostics; no second server setup.
& (Join-Path $PSScriptRoot 'start-local.ps1') -Mode doctor -AIBackend api
$profiles = Join-Path $repoRoot '.harness/tunnel-profiles'
$profile = 'landing-' + $TunnelId
$profileFile = Join-Path $profiles ($profile + '.yaml')
$shellExe = (Get-Process -Id $PID).Path
$launcher = Join-Path $PSScriptRoot 'start-local.ps1'
$command = '"' + $shellExe + '" -NoProfile -File "' + $launcher + '" -Mode stdio -AIBackend api'
if (-not (Test-Path -LiteralPath $profileFile)) {
    & $client init --sample sample_mcp_stdio_local --profile $profile --profile-dir $profiles --tunnel-id $TunnelId --mcp-command $command
    if ($LASTEXITCODE -ne 0) { throw 'Tunnel profile initialization failed' }
}
& $client doctor --profile $profile --profile-dir $profiles --explain
if ($LASTEXITCODE -ne 0) { throw 'Tunnel diagnostics failed; connection not started' }
& $client run --profile $profile --profile-dir $profiles
if ($LASTEXITCODE -ne 0) { throw 'Tunnel stopped with an error' }
