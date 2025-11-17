# Quick Build - Rebuild engine and deploy to runtime
# Usage: Just run this script from anywhere after making changes to main.cpp

# Get the directory where this script is located (Lehran root)
$lehranRoot = $PSScriptRoot
$engineDir = Join-Path $lehranRoot "engine"
$buildScript = Join-Path $engineDir "build_engine.ps1"

if (-not (Test-Path $buildScript)) {
    Write-Host "ERROR: Build script not found!" -ForegroundColor Red
    exit 1
}

& $buildScript -Config Release
