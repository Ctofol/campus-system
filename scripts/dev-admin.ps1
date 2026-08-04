[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"
$repoRoot = Split-Path -Parent $PSScriptRoot
Push-Location (Join-Path $repoRoot "admin/frontend")
try {
    npm run dev
}
finally {
    Pop-Location
}
