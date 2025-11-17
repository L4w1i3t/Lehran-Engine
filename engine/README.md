# Lehran Engine - C++ Runtime

This directory contains the C++ game engine source code.

## Requirements

- CMake 3.15 or higher
- C++17 compatible compiler (MSVC, GCC, or Clang)
- SDL2 and SDL2_ttf libraries
- nlohmann/json (header-only, included)

## Building on Windows

### Install Dependencies

1. **SDL2**: Download from https://www.libsdl.org/download-2.0.php
   - Download the development libraries (VC)
   - Extract to a known location (e.g., `C:\SDL2`)

2. **SDL2_ttf**: Download from https://www.libsdl.org/projects/SDL_ttf/
   - Download the development libraries (VC)
   - Extract to a known location (e.g., `C:\SDL2_ttf`)

3. **nlohmann/json**: Already included in `include/` folder

### Build Instructions

```powershell
# Create build directory
mkdir build
cd build

# Configure with CMake (adjust paths to your SDL2 installation)
cmake .. -DSDL2_DIR="C:/SDL2/cmake" -DSDL2_TTF_DIR="C:/SDL2_ttf/cmake"

# Build
cmake --build . --config Release

# The executable will be in ../runtime/LehranEngine.exe
```

## Quick Setup (Recommended)

For easier setup, you can use vcpkg:

```powershell
# Install vcpkg if you haven't
git clone https://github.com/Microsoft/vcpkg.git
cd vcpkg
.\bootstrap-vcpkg.bat

# Install SDL2 packages
.\vcpkg install sdl2:x64-windows
.\vcpkg install sdl2-ttf:x64-windows

# Build with vcpkg toolchain
cd path\to\Lehran\engine
mkdir build
cd build
cmake .. -DCMAKE_TOOLCHAIN_FILE="path\to\vcpkg\scripts\buildsystems\vcpkg.cmake"
cmake --build . --config Release
```

## Project Structure

```
engine/
├── main.cpp           # Main game engine code
├── CMakeLists.txt     # Build configuration
├── include/           # Header files (nlohmann/json)
└── README.md          # This file

runtime/              # Compiled executables go here
```

## How It Works

The engine loads game data from JSON files exported by the Lehran Editor (PyQt6 GUI):
- `data/manifest.json` - Game metadata
- `data/story.json` - Story data (chapters, characters, dialogue)
- `data/gameplay.json` - Gameplay data (classes, units, weapons)
- `data/timeline.json` - Event timeline

When you build a game project in the editor, it:
1. Exports all data to JSON
2. Copies the compiled engine executable
3. Packages everything together for distribution
