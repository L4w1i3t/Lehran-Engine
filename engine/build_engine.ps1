# Build Lehran Engine C++ Runtime
# This script compiles the C++ engine and copies it to the runtime folder

param(
    [string]$Config = "Release"
)

$ErrorActionPreference = "Stop"

# Paths (all relative to this script)
$engineDir = $PSScriptRoot
$buildDir = Join-Path $engineDir "build"
$runtimeDir = Join-Path (Split-Path $engineDir -Parent) "runtime"
$lehranRoot = Split-Path $engineDir -Parent
$vcpkgCmake = Join-Path $lehranRoot "vcpkg\downloads\tools\cmake-3.30.1-windows\cmake-3.30.1-windows-i386\bin\cmake.exe"

# Try to find CMake (check vcpkg first, then system PATH)
$cmakePath = $null
if (Test-Path $vcpkgCmake) {
    $cmakePath = $vcpkgCmake
} else {
    # Try to find cmake in PATH
    $cmakePath = (Get-Command cmake -ErrorAction SilentlyContinue).Source
}

if (-not $cmakePath) {
    Write-Host "ERROR: CMake not found" -ForegroundColor Red
    Write-Host "Please install CMake or run vcpkg setup first" -ForegroundColor Yellow
    exit 1
}

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Lehran Engine - Build Script" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Build the engine
Write-Host "[1/3] Building C++ engine ($Config)..." -ForegroundColor Yellow
Set-Location $buildDir

& $cmakePath --build . --config $Config

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Build failed!" -ForegroundColor Red
    exit 1
}

Write-Host "Build successful!" -ForegroundColor Green
Write-Host ""

# Step 2: Copy executable to runtime folder
Write-Host "[2/3] Copying executable to runtime folder..." -ForegroundColor Yellow

# Check both possible output locations
$exeSrcRelease = Join-Path $runtimeDir "LehranEngine.exe"
$exeSrcDebug = Join-Path $engineDir "runtime\Debug\LehranEngine.exe"
$exeDst = Join-Path $runtimeDir "LehranEngine.exe"

# If already in the right place, we're good
if (Test-Path $exeSrcRelease) {
    Write-Host "Executable already in runtime folder" -ForegroundColor Green
} elseif (Test-Path $exeSrcDebug) {
    # Copy from Debug build
    Copy-Item $exeSrcDebug $exeDst -Force
    Write-Host "Copied LehranEngine.exe (Debug)" -ForegroundColor Green
} else {
    Write-Host "ERROR: Compiled executable not found" -ForegroundColor Red
    exit 1
}

# Step 3: Copy DLLs to runtime folder
Write-Host "[3/3] Copying required DLLs..." -ForegroundColor Yellow

# SDL2 core DLLs
$sdl2Dll = Join-Path $engineDir "deps\SDL2\lib\x64\SDL2.dll"
$sdl2TtfDll = Join-Path $engineDir "deps\SDL2_ttf\lib\x64\SDL2_ttf.dll"

# SDL2_mixer and its dependencies from vcpkg
$vcpkgBinDir = Join-Path $lehranRoot "vcpkg\installed\x64-windows\bin"
$mixerDlls = @(
    "SDL2_mixer.dll",
    "vorbis.dll",
    "vorbisfile.dll",
    "ogg.dll",
    "wavpackdll.dll"
)

# Copy SDL2 core DLLs
if (Test-Path $sdl2Dll) {
    Copy-Item $sdl2Dll $runtimeDir -Force
    Write-Host "  Copied SDL2.dll" -ForegroundColor Green
}

if (Test-Path $sdl2TtfDll) {
    Copy-Item $sdl2TtfDll $runtimeDir -Force
    Write-Host "  Copied SDL2_ttf.dll" -ForegroundColor Green
}

# Copy SDL2_mixer and dependencies
foreach ($dll in $mixerDlls) {
    $srcPath = Join-Path $vcpkgBinDir $dll
    if (Test-Path $srcPath) {
        Copy-Item $srcPath $runtimeDir -Force
        Write-Host "  Copied $dll" -ForegroundColor Green
    } else {
        Write-Host "  Warning: $dll not found" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Build Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Runtime files are ready in: $runtimeDir" -ForegroundColor Cyan
Write-Host ""
