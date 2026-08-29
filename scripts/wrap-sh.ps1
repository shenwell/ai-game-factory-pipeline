param(
    [Parameter(Mandatory = $true, Position = 0)]
    [string]$ScriptPath,
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$Args
)

$bash = Get-Command bash -ErrorAction SilentlyContinue
if (-not $bash) {
    throw "bash not found; install Git for Windows to run vendored gamestudio shell scripts"
}

$repoRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$studio = Join-Path $repoRoot "vendor\gamestudio"
Push-Location $studio
try {
    & bash $ScriptPath @Args
    exit $LASTEXITCODE
} finally {
    Pop-Location
}
