# Lehran Engine

A custom Fire Emblem game creation engine with a comprehensive GUI for designing story, gameplay, maps, and managing assets. Features a Python-based editor with a C++ game runtime for high performance.

## Features

### Timeline Editor
- **Event Organization**: Plan and visualize the sequence of events in your game chronologically
- **Event Types**: Story events, battles, cutscenes, character recruitment, support conversations, and more
- **Event Details**: Track chapter, location, participants, and descriptions for each event
- **Drag & Drop Reordering**: Easily reorganize events by dragging them in the list
- **Color Coding**: Visual distinction between different event types
- **Linked Content**: Connect timeline events to specific dialogue, maps, and characters

### Story & Narrative Editor
- **Chapters**: Create and manage game chapters with objectives, descriptions, and events
- **Characters**: Design characters with names, titles, affiliations, and biographies
- **Dialogue**: Build dialogue scenes with multiple speakers and branching options
- **Support Conversations**: Create character support conversations (C/B/A/S ranks)

### Gameplay & Units Editor
- **Classes**: Define character classes with base stats, movement, and types
  - Drag and drop to reorder classes
  - Customizable stat spreads and movement types
- **Units**: Create playable and enemy units with custom stats and equipment
  - Drag and drop to reorder units
  - Link units to character profiles
- **Weapons**: Design weapons with might, hit rate, crit, range, and durability
  - Drag and drop to reorder weapons
  - Multiple weapon types (Sword, Lance, Axe, Bow, Magic, etc.)
- **Items**: Create consumables, stat boosters, and special items
  - Drag and drop to reorder items
  - Type-specific properties:
    - **Consumable**: Healing amount (HP restored)
    - **Stat Booster**: Permanent stat increases (HP/Str/Mag/Skl/Spd/Lck/Def/Res)
    - **Promotion Item**: Target class for class changes
    - **Key Item**: Unique identifier for story/script integration
    - **Special**: Custom effects with text descriptions
- **Stats Configuration**: Customize the stat system for your game

### Asset Manager
- **Asset Browser**: Organized file browser with preview capabilities
  - Browse assets by category (BGM, SFX, Portraits, Sprites, Backgrounds, UI, Animations)
  - Image preview for PNG, JPG, BMP, GIF files
  - Audio playback for OGG, WAV, MP3 files
  - File information display (size, type, path)
  - Right-click folders to add new assets
  - Delete assets with confirmation
  - Open asset folders in File Explorer
- **Audio Assignments**: Link audio files to game events and roles
  - **Music Roles**: Title Screen, Main Menu, Battle Prep, Player/Enemy Phase, Battle Scene, Victory, Defeat, Shop, Cutscene
  - **SFX Roles**: Menu Cursor, Menu Select, Menu Cancel, Attack Hit/Miss, Critical Hit, Level Up
  - Dropdown selection
  - Automatic audio file detection from bgm/sfx folders
  - Export to JSON for C++ engine consumption

### Maps & Tiled Integration
- **Tiled Support**: Full integration with Tiled Map Editor
- **Map Import**: Import .tmx map files into your project
- **Map Management**: Organize and edit maps with descriptions and metadata
- **Direct Tiled Launch**: Open Tiled directly from the engine

### Project Management
- **Project Files**: Save/load projects in .lehran format (JSON-based)
- **Directory Structure**: Automatic project folder organization with asset subfolders
  - `assets/bgm/` - Background music
  - `assets/sfx/` - Sound effects
  - `assets/portraits/` - Character portraits
  - `assets/sprites/` - Unit sprites
  - `assets/backgrounds/` - Background images
  - `assets/ui/` - UI elements
  - `assets/animations/` - Battle animations
- **Build System**: Compile projects to standalone C++ game executables
- **One-Click Build**: Build and run your game directly from the editor (Ctrl+B to build, F5 to run)

### Audio System
- **SDL_mixer Integration**: High-quality audio playback in the C++ engine
- **OGG Vorbis Support**: Compressed audio format for efficient file sizes
- **Dynamic Audio Loading**: Audio assignments read from JSON at runtime
- **Graceful Fallback**: Game continues even if audio files are missing
- **State-Based Music**: Music plays on appropriate screens (title, battle, etc.)

## Installation

### Prerequisites
- **Python 3.8 or higher**
- **Tiled Map Editor**
- **For C++ Engine Development** (optional, only if modifying the engine):
  - CMake 3.15 or higher
  - **Windows Only:** Visual Studio 2022 Build Tools (with C++ support)
  - vcpkg (for managing C++ dependencies)

### Setup

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

Required Python packages:
- PyQt6 (GUI framework)
- pygame (audio preview in editor)

2. Download and install Tiled Map Editor:
   - Visit https://www.mapeditor.org/
   - Download the version for your OS
   - Note the installation path for configuration in the engine

3. (Optional) Set up C++ engine development environment:
   ```powershell
   cd engine
   .\setup_sdl.ps1
   ```
   This will set up vcpkg and install SDL2 libraries needed for engine development:
   - SDL2 (graphics and input)
   - SDL2_ttf (text rendering)
   - SDL2_mixer (audio playback)
   - Dependencies: libogg, libvorbis, wavpack, brotli, bzip2, freetype, libpng, zlib

## Running the Engine

Launch the Lehran Engine GUI:

```bash
python main.py
```

Or on Windows, double-click `Lehran GUI.bat`

## Usage

### Creating a New Project

1. Click **File > New Project** or use `Ctrl+N`
2. Enter a project name
3. Select a parent directory (defaults to `Lehran/Projects/`)
4. A new folder will be created with your project name containing:
   ```
   Projects/
   └── MyProject/
       ├── MyProject.lehran  (project file)
       ├── maps/             (Tiled map files)
       ├── assets/           (sprites, music, etc.)
       ├── scripts/          (custom scripts)
       └── data/             (exported game data)
   ```

### Planning Your Timeline

1. Go to the **Timeline** tab
2. Click **Add Event** to create a new timeline entry
3. Fill in event details:
   - Event name and type (Story Event, Battle, Cutscene, etc.)
   - Chapter number and location
   - Participants and description
4. Use **Move Up/Down** to reorder events chronologically
5. Color-coded event types help visualize your game's structure
6. Link events to specific content in other tabs for easy reference

### Working with Tiled Maps

1. Go to the **Maps & Tiled** tab
2. Set the path to your Tiled executable
3. Click **New in Tiled** to create a new map
4. Create your map in Tiled with:
   - Orthogonal orientation
   - 16x16 tile size (recommended)
   - Save as .tmx format in your project's maps folder
5. Click **Import Map** to add the map to your project

### Designing Story Content

1. Go to the **Story & Narrative** tab
2. Use the **Chapters** sub-tab to create game chapters
3. Add characters in the **Characters** sub-tab
4. Design dialogue scenes and support conversations

### Configuring Gameplay

1. Go to the **Gameplay & Units** tab
2. Define character classes with stats and movement
3. Create weapons with Fire Emblem-style properties
4. Configure items with type-specific effects:
   - **Consumables**: Set healing amount (0-99 HP)
   - **Stat Boosters**: Configure which stats to increase (0-30 per stat)
   - **Promotion Items**: Specify target class for promotion
   - **Key Items**: Assign unique IDs for script/story integration
   - **Special Items**: Write custom effect descriptions
5. Drag and drop to reorder any gameplay elements (classes, units, weapons, items)

### Managing Assets

1. Go to the **Assets** tab
2. In the **Asset Browser** sub-tab:
   - Browse existing assets by category
   - Right-click a folder (BGM, SFX, Portraits, etc.) and select "Add Asset to this folder..."
   - Select one or multiple files to import into your project
   - Click on assets to preview them:
     - Images display in the preview pane
     - Audio files show Play/Stop controls
   - Click "Open in File Explorer" to access asset folders directly
   - Use "Delete Asset" to remove unwanted files (with confirmation)
3. In the **Audio Assignments** sub-tab:
   - Click "Refresh Audio List" to load available audio files
   - Assign audio files to specific roles:
     - Music: Title Screen, Menu, Battle phases, Victory/Defeat, etc.
     - SFX: Menu sounds, Combat sounds, Level Up, etc.
   - Select "(None)" to explicitly disable audio for a role
   - Click "Save Audio Assignments" when finished
   - Save your project (Ctrl+S) to persist the assignments

### Audio File Guidelines

- **Recommended Format**: OGG Vorbis (best compatibility and compression)
- **Alternative Formats**: WAV (uncompressed), MP3 (widely supported)
- **File Size Tips**:
  - Music: Keep under 5MB per track
  - SFX: Keep under 500KB per effect
- **Organization**:
  - Place music in `assets/bgm/`
  - Place sound effects in `assets/sfx/`
- **Preview**: Use the Asset Browser to test audio before assigning roles

### Saving Your Work

- Use **File > Save Project** or `Ctrl+S` to save your progress
- Project data is stored in JSON format for easy editing

### Building Your Game

1. Use **Build > Build Project** or press `Ctrl+B` to compile your game
2. The build process will:
   - Export all your story, gameplay, and timeline data to JSON
   - Export audio assignments to `audio_assignments.json`
   - Package the C++ game engine with your project data
   - Copy required SDL2 libraries (including audio DLLs)
   - Copy all assets from your project's asset folders
   - Create a standalone executable in `Projects/[YourGame]/build/`
3. Run your built game with **Build > Run Game** or press `F5`
4. Your game will feature:
   - Custom splash screen with fade effects (3.5 seconds)
   - Title screen with your game's name and assigned music
   - Menu navigation (New Game/Load/Exit)
   - Audio playback based on your assignments
   - Graceful handling of missing audio files (no crashes)
5. The build folder contains:
   - Your game executable (renamed to your project name)
   - SDL2.dll, SDL2_ttf.dll, SDL2_mixer.dll
   - Audio codec DLLs (vorbis.dll, vorbisfile.dll, ogg.dll, wavpackdll.dll)
   - data/ folder with all JSON files
   - assets/ folder with all your game assets
   - README.txt with instructions for players

### Rebuilding the Engine (Advanced)

If you modify the C++ engine source code:

```powershell
.\quick_build.ps1
```

This will recompile the engine and update the runtime.

## Architecture

### GUI Layer (PyQt6)
- `main.py` - Application entry point
- `gui/main_window.py` - Main application window with Build/Run menus
- `gui/timeline_editor.py` - Timeline visualization with drag-and-drop event sequencing
- `gui/story_editor.py` - Story and narrative editing
- `gui/gameplay_editor.py` - Gameplay elements editing with conditional item properties
- `gui/map_editor.py` - Map management and Tiled integration
- `gui/project_manager.py` - Project file management and asset folder creation
- `gui/build_manager.py` - Build system and game packaging with audio DLL handling
- `gui/asset_manager.py` - Asset browser, preview, and audio assignment system

### Game Runtime (C++ with SDL2)
The engine exports project data to a C++ game runtime built with SDL2.

**Engine Components:**
- `engine/main.cpp` - Core game engine with state machine
  - Splash screen with auto-fade transitions (3.5 seconds)
  - Title screen with menu system
  - JSON data loading (manifest, gameplay, story, timeline, audio_assignments)
  - SDL2 rendering and input handling
  - SDL_mixer audio system with OGG Vorbis support
  - Dynamic music loading based on audio assignments
  - Graceful audio failure handling (continues without audio if files missing)
- `engine/CMakeLists.txt` - Build configuration with SDL2_mixer integration
- `engine/build_engine.ps1` - Automated build script with DLL copying
- `engine/setup_sdl.ps1` - vcpkg setup and SDL2 dependency installation
- `quick_build.ps1` - Convenient engine rebuild wrapper

**Runtime Structure:**
- `runtime/LehranEngine.exe` - Compiled game engine executable
- `runtime/SDL2.dll` - SDL2 graphics library
- `runtime/SDL2_ttf.dll` - SDL2 text rendering library
- `runtime/SDL2_mixer.dll` - SDL2 audio library
- `runtime/vorbis.dll` - OGG Vorbis decoder
- `runtime/vorbisfile.dll` - OGG file handling
- `runtime/ogg.dll` - OGG container format
- `runtime/wavpackdll.dll` - WavPack codec support

**Build Output (per project):**
```
Projects/[YourGame]/build/
├── [YourGame].exe          # Standalone game executable
├── SDL2.dll                # Graphics library
├── SDL2_ttf.dll            # Font rendering library
├── SDL2_mixer.dll          # Audio playback library
├── vorbis.dll              # Audio codec
├── vorbisfile.dll          # Audio codec
├── ogg.dll                 # Audio codec
├── wavpackdll.dll          # Audio codec
├── data/
│   ├── manifest.json       # Project metadata
│   ├── story.json          # Chapters, characters, dialogue
│   ├── gameplay.json       # Classes, units, weapons, items
│   ├── timeline.json       # Event sequence
│   └── audio_assignments.json  # Audio role mappings
├── assets/
│   ├── bgm/                # Background music files
│   ├── sfx/                # Sound effect files
│   ├── portraits/          # Character portraits
│   ├── sprites/            # Unit sprites
│   ├── backgrounds/        # Background images
│   ├── ui/                 # UI elements
│   └── animations/         # Battle animations
├── maps/                   # Tiled maps (if any)
└── README.txt              # How to run the game
```

## File Formats

### .lehran Project Files
JSON-based project files containing:
- Project metadata (name, version, timestamps)
- Timeline data (event sequence and organization)
- Story data (chapters, characters, dialogue)
- Gameplay data (classes, units, weapons, items with type-specific properties)
- Map references and configuration
- Audio assignments (music and SFX role mappings)

### Audio Assignments Format
The `audio_assignments.json` file maps game events to audio files:
```json
{
  "title_music": "bgm/title_theme.ogg",
  "battle_music": "bgm/battle_theme.ogg",
  "menu_cursor_sfx": "sfx/cursor.ogg",
  "menu_select_sfx": "sfx/select.ogg",
  "victory_music": "",
  ...
}
```
- Empty string `""` = explicitly no audio (user selected "(None)")
- Missing key = use engine defaults if available
- Path format: `"bgm/filename.ext"` or `"sfx/filename.ext"`

### Tiled Integration
- Supports .tmx (XML) map format
- Orthogonal maps with custom tile sizes
- Can include multiple layers, objects, and properties

## Development Roadmap

### Completed
- [x] Core GUI framework with PyQt6
- [x] Project management system with .lehran format
- [x] Timeline editor with drag-and-drop event visualization
- [x] Story editor (chapters, characters, dialogue, support conversations)
- [x] Gameplay editor (classes, units, weapons, items with conditional properties)
- [x] Drag-and-drop reordering for all gameplay elements
- [x] Type-specific item properties (Consumable, Stat Booster, Promotion, Key, Special)
- [x] Tiled integration for map editing
- [x] Asset Manager with browser and preview
- [x] Asset organization (automatic subfolder creation)
- [x] Image preview (PNG, JPG, BMP, GIF)
- [x] Audio preview with pygame (no ffmpeg required)
- [x] Audio assignment system (link files to game events)
- [x] C++ game runtime with SDL2
- [x] SDL_mixer audio integration (OGG Vorbis support)
- [x] Dynamic audio loading from JSON assignments
- [x] Graceful audio failure handling
- [x] Build and export system with one-click compilation
- [x] Automated build scripts (quick_build.ps1, build_engine.ps1)
- [x] DLL management for SDL2, SDL2_ttf, SDL2_mixer, and audio codecs
- [x] Splash screen with fade effects (3.5 seconds)
- [x] Title screen with menu system and assigned music
- [x] JSON-based data pipeline (Editor → JSON → C++ Runtime)
- [x] Standalone executable packaging with all dependencies
- [x] Window title displays game name
- [x] Console-free release builds
- [x] Audio timing control (music plays on title screen, not splash)
- [x] "(None)" audio option respected (no fallback when explicitly disabled)

### In Progress / Future
- [ ] Additional audio roles (gameplay sounds, ambient audio)
- [ ] Volume controls in audio assignments
- [ ] Music crossfade and transition effects
- [ ] Dialogue tree editor with branching logic
- [ ] Map rendering from Tiled files in game runtime
- [ ] Unit placement and movement system
- [ ] Combat system implementation
- [ ] Event scripting system
- [ ] Battle animations
- [ ] Character progression and stats
- [ ] AI for enemy units
- [ ] Game state persistence (save/load system)
- [ ] Testing and debugging tools

## Contributing

This is a fan project for educational and creative purposes. Contributions welcome!

## License

This is a fan project. Fire Emblem is © Intelligent Systems/Nintendo.

## Technical Details

### Technologies Used
- **PyQt6** - GUI framework for the editor
- **pygame** - Audio preview in Asset Manager (self-contained, no ffmpeg required)
- **Python 3.8+** - Editor scripting language
- **C++17** - Game runtime language
- **SDL2** - Graphics, input, and rendering
- **SDL2_ttf** - Text rendering with TrueType fonts
- **SDL2_mixer** - Audio playback and mixing
- **OGG Vorbis** - Audio compression codec (via libogg, libvorbis)
- **nlohmann/json** - JSON parsing in C++
- **CMake** - C++ build system
- **vcpkg** - C++ package manager for SDL2 dependencies
- **Tiled Map Editor** - Map creation tool

### Key Features
- **Portable Build System**: Uses relative paths for cross-user compatibility
- **Automated Compilation**: PowerShell scripts handle C++ build process
- **No Console Window**: Release builds run without debug console
- **Dynamic Window Title**: Shows your game's name, not "Lehran Engine"
- **JSON Data Pipeline**: Clean separation between editor and runtime
- **SDL2 Integration**: Hardware-accelerated rendering with vsync
- **Audio System**: Full SDL_mixer integration with multiple codec support
- **Self-Contained**: Built games include all necessary DLLs (no external dependencies)
- **Graceful Degradation**: Missing assets don't crash the game
- **Type-Safe Items**: Conditional UI shows only relevant properties per item type

### Audio Technical Details
- **Preview System**: Uses pygame.mixer in editor (no external codecs needed)
- **Runtime System**: Uses SDL_mixer in C++ engine (native performance)
- **Supported Formats**: OGG (recommended), WAV, MP3
- **Sample Rate**: 44.1kHz stereo
- **Buffer Size**: 2048 samples (low latency)
- **Volume Control**: Default 50% music volume (MIX_MAX_VOLUME / 2)
- **Looping**: Background music loops infinitely (-1 loop count)
- **Assignment System**: JSON-based mapping (editor saves, engine loads)
- **Fallback Logic**: 
  - Empty string = no audio (user choice)
  - Missing assignment = check defaults
  - Missing file = log warning, continue silently