# Aita-Lagun — convenience runner
# Run: .\run.ps1

if (-not (Test-Path ".venv")) {
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    python -m venv .venv
}

$venvActivate = ".venv\Scripts\Activate.ps1"
if (Test-Path $venvActivate) {
    & $venvActivate
}

if (-not (Test-Path ".env")) {
    Write-Host "Copying .env.example to .env — edit with your API keys" -ForegroundColor Yellow
    Copy-Item ".env.example" ".env"
}

Write-Host "Starting Aita-Lagun..." -ForegroundColor Green
python -m agents.agent
