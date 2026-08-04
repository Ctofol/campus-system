[CmdletBinding()]
param(
    [switch]$SkipAdminBuild,
    [switch]$SkipStudentBuild
)

$ErrorActionPreference = "Stop"
$repoRoot = Split-Path -Parent $PSScriptRoot
$pytestTemp = Join-Path $repoRoot ".pytest-tmp"

Push-Location $repoRoot
try {
    # 先为本轮工程基础设施建立绿色基线；旧业务代码告警另行渐进清理。
    python -m ruff check backend/app/config.py backend/app/database.py backend/app/main.py backend/app/router_registry.py backend/app/modules backend/alembic backend/tests/test_config.py
    if (-not $?) { throw "Ruff check failed" }

    python -m pytest --basetemp $pytestTemp
    if (-not $?) { throw "Backend tests failed" }

    Push-Location (Join-Path $repoRoot "backend")
    try {
        python scripts/preflight.py
        if (-not $?) { throw "Preflight check failed" }
    }
    finally {
        Pop-Location
    }

    if (-not $SkipAdminBuild) {
        Push-Location (Join-Path $repoRoot "admin/frontend")
        try {
            npm run build
            if (-not $?) { throw "Admin build failed" }
        }
        finally {
            Pop-Location
        }
    }

    if (-not $SkipStudentBuild) {
        Push-Location (Join-Path $repoRoot "fronted")
        try {
            npm run build:h5
            if (-not $?) { throw "Student/teacher H5 build failed" }
        }
        finally {
            Pop-Location
        }
    }
}
finally {
    Pop-Location
}
