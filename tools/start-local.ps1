param(
    [ValidateSet('doctor','stdio','http')][string]$Mode = 'doctor',
    [string]$PythonPath = $env:AGENTIC_PYTHON,
    [string]$NodePath = $env:AGENTIC_NODE,
    [string]$NpmCli = $env:AGENTIC_NPM_CLI,
    [string]$BlenderPath = $env:BLENDER_EXECUTABLE,
    [ValidateSet('session','api')][string]$AIBackend = 'session',
    [ValidateRange(1024,65535)][int]$Port = 8765
)
$ErrorActionPreference = 'Stop'
# Preserve MCP UTF-8 through PowerShell's native process input/output bridge.
$OutputEncoding = [System.Text.UTF8Encoding]::new($false)
[Console]::InputEncoding = $OutputEncoding
[Console]::OutputEncoding = $OutputEncoding
$repoRoot = Split-Path -Parent $PSScriptRoot
if (-not $BlenderPath) {
    $portableBlender = Join-Path $repoRoot '.harness/tools/blender-4.5.9/app/blender-4.5.9-windows-x64/blender.exe'
    if (Test-Path -LiteralPath $portableBlender -PathType Leaf) { $BlenderPath = $portableBlender }
}
if ($BlenderPath) {
    if (-not (Test-Path -LiteralPath $BlenderPath -PathType Leaf)) { throw "Missing Blender executable: $BlenderPath" }
    $env:BLENDER_EXECUTABLE = (Resolve-Path -LiteralPath $BlenderPath).Path
}
$bundled = Join-Path $env:USERPROFILE '.cache/codex-runtimes/codex-primary-runtime/dependencies'
if (-not $PythonPath) { $PythonPath = Join-Path $bundled 'python/python.exe' }
if (-not $NodePath) { $NodePath = Join-Path $bundled 'node/bin/node.exe' }
if (-not $NpmCli) { $NpmCli = Join-Path $repoRoot '.harness/runtime/npm-12.0.2/package/bin/npm-cli.js' }
foreach ($runtimeFile in @($PythonPath,$NodePath,$NpmCli)) {
    if (-not (Test-Path -LiteralPath $runtimeFile -PathType Leaf)) { throw "Missing runtime file: $runtimeFile" }
}
$env:AGENTIC_NODE = (Resolve-Path -LiteralPath $NodePath).Path
$env:AGENTIC_NPM_CLI = (Resolve-Path -LiteralPath $NpmCli).Path
$env:AGENTIC_BUILD_BACKEND = 'local'
$env:AGENTIC_AI_BACKEND = $AIBackend
$env:AGENTIC_ENABLE_BUILDS = '1'
$env:PATH = (Split-Path -Parent $env:AGENTIC_NODE) + [IO.Path]::PathSeparator + $env:PATH
if (-not $env:NODE_PATH) { $env:NODE_PATH = Join-Path $bundled 'node/node_modules' }
if (-not $env:AGENTIC_BROWSER_CHANNEL) { $env:AGENTIC_BROWSER_CHANNEL = 'msedge' }
Push-Location $repoRoot
try {
    if ($Mode -eq 'doctor') {
        & $PythonPath -c "import sys,json; sys.path.insert(0,'tools'); from harness_operations import runtime_status; print(json.dumps(runtime_status(None,{}),indent=2))"
    } elseif ($Mode -eq 'stdio') {
        & $PythonPath (Join-Path $PSScriptRoot 'harness_mcp_server.py') --transport stdio
    } else {
        & $PythonPath (Join-Path $PSScriptRoot 'harness_mcp_server.py') --transport http --host 127.0.0.1 --port $Port
    }
    if ($LASTEXITCODE -ne 0) { throw "Local runtime exited with code $LASTEXITCODE" }
} finally { Pop-Location }
