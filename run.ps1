# Runs the bookstore API on http://localhost:8000 (docs at /docs)
param([int]$Port = 8000)

Set-Location $PSScriptRoot

if (-not (Test-Path .venv)) {
    python -m venv .venv
}
& .\.venv\Scripts\Activate.ps1

pip install -q -r requirements.txt

if (-not (Test-Path .env)) {
    Copy-Item .env.example .env
    Write-Host "Created .env from .env.example - change SECRET_KEY before deploying."
}

uvicorn app.main:app --reload --port $Port
