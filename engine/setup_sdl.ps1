# SDL2 Setup Script
# Downloads pre-built SDL2 libraries for Windows

$sdl2Url = "https://github.com/libsdl-org/SDL/releases/download/release-2.32.0/SDL2-devel-2.32.0-VC.zip"
$sdl2TtfUrl = "https://github.com/libsdl-org/SDL_ttf/releases/download/release-2.24.0/SDL2_ttf-devel-2.24.0-VC.zip"

$engineDir = $PSScriptRoot
$depsDir = Join-Path $engineDir "deps"

Write-Host "Setting up SDL2 dependencies..." -ForegroundColor Cyan

# Create deps directory
if (-not (Test-Path $depsDir)) {
    New-Item -ItemType Directory -Path $depsDir | Out-Null
}

# Download SDL2
Write-Host "Downloading SDL2..." -ForegroundColor Yellow
$sdl2Zip = Join-Path $depsDir "sdl2.zip"
Invoke-WebRequest -Uri $sdl2Url -OutFile $sdl2Zip
Expand-Archive -Path $sdl2Zip -DestinationPath $depsDir -Force
Remove-Item $sdl2Zip

# Download SDL2_ttf
Write-Host "Downloading SDL2_ttf..." -ForegroundColor Yellow
$sdl2TtfZip = Join-Path $depsDir "sdl2_ttf.zip"
Invoke-WebRequest -Uri $sdl2TtfUrl -OutFile $sdl2TtfZip
Expand-Archive -Path $sdl2TtfZip -DestinationPath $depsDir -Force
Remove-Item $sdl2TtfZip

# Rename folders for easier access
$sdl2Folder = Get-ChildItem -Path $depsDir -Filter "SDL2-*" | Select-Object -First 1
$sdl2TtfFolder = Get-ChildItem -Path $depsDir -Filter "SDL2_ttf-*" | Select-Object -First 1

if ($sdl2Folder) {
    Rename-Item -Path $sdl2Folder.FullName -NewName "SDL2" -Force
}
if ($sdl2TtfFolder) {
    Rename-Item -Path $sdl2TtfFolder.FullName -NewName "SDL2_ttf" -Force
}

Write-Host "`nSDL2 setup complete!" -ForegroundColor Green
Write-Host "Dependencies installed to: $depsDir" -ForegroundColor Cyan
