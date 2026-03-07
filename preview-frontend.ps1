$ErrorActionPreference = "Stop"

$frontendDir = Join-Path $PSScriptRoot "frontend"

if (!(Test-Path $frontendDir)) {
  throw "frontend directory not found: $frontendDir"
}

Set-Location $frontendDir

if (!(Test-Path (Join-Path $frontendDir "node_modules"))) {
  Write-Host "Installing frontend dependencies..."
  npm ci
}

Write-Host "Starting frontend live preview on http://localhost:5173 ..."
npm run dev:preview
