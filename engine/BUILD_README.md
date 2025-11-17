# Lehran Engine - Development Scripts

This folder contains utility scripts for engine development.

## Scripts

### `build_engine.ps1`
Builds the C++ engine and deploys it to the runtime folder.

**Usage:**
```powershell
# Build Release version (default)
.\build_engine.ps1

# Build Debug version
.\build_engine.ps1 -Config Debug
```

**What it does:**
1. Compiles the C++ engine with CMake
2. Copies the executable to `../runtime/LehranEngine.exe`
3. Verifies SDL2 DLLs are present (copies if missing)

### `quick_build.ps1` (Root folder)
Quick shortcut to rebuild the engine from anywhere.

**Usage:**
```powershell
# From the Lehran root directory
.\quick_build.ps1
```

This is useful when you make changes to `engine/main.cpp` and want to quickly rebuild and deploy.

## Workflow

1. **Make changes** to `engine/main.cpp` or other engine files
2. **Run the build script**: `.\engine\build_engine.ps1` or `.\quick_build.ps1`
3. **Test in editor**: Open the Lehran Editor and build/run your project
4. **The game** will use the newly compiled engine

## First Time Setup

If you haven't built the engine yet:

1. Run `.\engine\setup_sdl.ps1` to download SDL2 libraries
2. Download `json.hpp` and place it in `engine/include/`
3. Run `.\engine\build_engine.ps1` to build the engine

## Notes

- The build script uses the CMake that was downloaded by vcpkg
- Debug builds are larger but easier to debug with Visual Studio
- Release builds are optimized and smaller in size
- Always rebuild after changing C++ code for changes to take effect
