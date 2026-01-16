# =============================================================================
# VICORE - Script de Correction Automatique de la Qualité du Code (PowerShell)
# =============================================================================

Write-Host "=== VICORE Code Quality Fix ===" -ForegroundColor Cyan
Write-Host ""

# Check we're in the right directory
if (-not (Test-Path "pyproject.toml")) {
    Write-Host "Error: pyproject.toml not found. Run this script from the project root." -ForegroundColor Red
    exit 1
}

# 1. Install tools
Write-Host "[1/6] Installing tools..." -ForegroundColor Yellow
pip install black isort autoflake flake8 --quiet 2>$null
Write-Host "  OK Tools installed" -ForegroundColor Green

# 2. Remove unused imports
Write-Host "[2/6] Removing unused imports..." -ForegroundColor Yellow
python -m autoflake --in-place --remove-all-unused-imports --recursive eurotunnel_web/
Write-Host "  OK Unused imports removed" -ForegroundColor Green

# 3. Sort imports
Write-Host "[3/6] Sorting imports..." -ForegroundColor Yellow
python -m isort eurotunnel_web/ --profile black --line-length 120 --quiet
Write-Host "  OK Imports sorted" -ForegroundColor Green

# 4. Format with Black
Write-Host "[4/6] Formatting with Black..." -ForegroundColor Yellow
python -m black eurotunnel_web/ --line-length 120 --quiet
Write-Host "  OK Code formatted" -ForegroundColor Green

# 5. Info about remaining manual fixes
Write-Host "[5/6] Checking for manual fixes needed..." -ForegroundColor Yellow

# Check for == None patterns
$noneIssues = Select-String -Path "eurotunnel_web/*.py" -Pattern "== None|!= None" -List
if ($noneIssues) {
    Write-Host "  WARNING: Found '== None' patterns that need manual fixing:" -ForegroundColor Yellow
    foreach ($issue in $noneIssues) {
        Write-Host "    - $($issue.Filename)" -ForegroundColor Yellow
    }
}

# 6. Check with Flake8
Write-Host "[6/6] Checking with Flake8..." -ForegroundColor Yellow
$flake8Output = python -m flake8 eurotunnel_web/ --max-line-length=120 --ignore=E501,W503,E203 --count 2>&1
$flake8Count = ($flake8Output | Select-Object -Last 1)

if ($flake8Count -eq "0" -or [string]::IsNullOrEmpty($flake8Count)) {
    Write-Host "  OK No flake8 issues found!" -ForegroundColor Green
} else {
    Write-Host "  WARNING: $flake8Count remaining flake8 issues" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "=== Summary ===" -ForegroundColor Cyan
Write-Host "OK Automatic fixes applied" -ForegroundColor Green
Write-Host ""
Write-Host "Manual fixes still required:" -ForegroundColor Yellow
Write-Host "  1. Replace '== None' with 'is None'"
Write-Host "  2. Fix bare except in version.py"
Write-Host "  3. Security fixes (see PLAN_CORRECTION.md)"
Write-Host ""
Write-Host "=== Done ===" -ForegroundColor Cyan
