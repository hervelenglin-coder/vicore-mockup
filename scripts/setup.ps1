# VICORE Web Application - Setup Script (PowerShell)
# ================================================

Write-Host "=== VICORE Setup Script ===" -ForegroundColor Cyan

# Check Python version
Write-Host "`n[1/6] Checking Python version..." -ForegroundColor Yellow
$pythonVersion = python --version 2>&1
Write-Host "  Installed: $pythonVersion"
Write-Host "  Required: Python 3.10-3.12" -ForegroundColor Gray

# Check/Install Poetry
Write-Host "`n[2/6] Checking Poetry..." -ForegroundColor Yellow
$poetryInstalled = Get-Command poetry -ErrorAction SilentlyContinue
if (-not $poetryInstalled) {
    Write-Host "  Poetry not found. Installing..." -ForegroundColor Red
    pip install poetry
} else {
    Write-Host "  Poetry is installed: $(poetry --version)" -ForegroundColor Green
}

# Install dependencies
Write-Host "`n[3/6] Installing Python dependencies..." -ForegroundColor Yellow
poetry install --no-interaction 2>&1 | Out-Null
if ($LASTEXITCODE -eq 0) {
    Write-Host "  Dependencies installed successfully" -ForegroundColor Green
} else {
    Write-Host "  Warning: Some dependencies may have failed" -ForegroundColor Red
}

# Check PostgreSQL
Write-Host "`n[4/6] Checking PostgreSQL..." -ForegroundColor Yellow
$psqlInstalled = Get-Command psql -ErrorAction SilentlyContinue
if (-not $psqlInstalled) {
    Write-Host "  PostgreSQL client not found" -ForegroundColor Red
    Write-Host "  Install from: https://www.postgresql.org/download/windows/" -ForegroundColor Gray
} else {
    Write-Host "  PostgreSQL client found" -ForegroundColor Green
}

# Check Redis
Write-Host "`n[5/6] Checking Redis..." -ForegroundColor Yellow
$redisInstalled = Get-Command redis-cli -ErrorAction SilentlyContinue
if (-not $redisInstalled) {
    Write-Host "  Redis not found" -ForegroundColor Red
    Write-Host "  Install from: https://github.com/microsoftarchive/redis/releases" -ForegroundColor Gray
    Write-Host "  Or use Docker: docker run -d -p 6379:6379 redis" -ForegroundColor Gray
} else {
    Write-Host "  Redis found" -ForegroundColor Green
}

# Check .env file
Write-Host "`n[6/6] Checking configuration..." -ForegroundColor Yellow
$envFile = ".env"
if (Test-Path $envFile) {
    Write-Host "  .env file exists" -ForegroundColor Green
} else {
    Write-Host "  .env file not found. Creating template..." -ForegroundColor Red
    @"
# Database Configuration
export DB_HOST="localhost"
export DB_PORT="5432"
export DB="euro_tunnel_dev"
export DB_USER="your_user"
export DB_PASSWORD="your_password"

# Web Server Configuration
export WEB_HOST="127.0.0.1"
export WEB_PORT="5000"
export WEB_DEBUG="True"

# Image Directory
export WHEEL_IMG_DIR="C:/path/to/wheel/images"
"@ | Out-File -FilePath ".env.template" -Encoding UTF8
    Write-Host "  Created .env.template - copy to .env and fill in values" -ForegroundColor Yellow
}

# Summary
Write-Host "`n=== Setup Summary ===" -ForegroundColor Cyan
Write-Host "To run the application:"
Write-Host "  1. Ensure PostgreSQL is running with the eurotunnel database"
Write-Host "  2. Ensure Redis is running on localhost:6379"
Write-Host "  3. Configure .env with your database credentials"
Write-Host "  4. Run: poetry run python -m eurotunnel_web.app"
Write-Host "`nTo run tests:"
Write-Host "  poetry run pytest tests/ -v"
