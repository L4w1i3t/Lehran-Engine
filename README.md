# Lehran Engine

A custom Fire Emblem game creation engine with a comprehensive GUI for designing story, gameplay, maps, and managing assets. Features a Python-based editor with a C++ game runtime for high performance.

## Features

### Timeline Editor
- **Node-Based Visualization**: Visual timeline with branching story paths
  - Drag-and-drop node positioning
  - Color-coded event types (Story, Battle, Support, Cutscene, etc.)
  - Connection lines showing sequential (solid) and choice branches (dashed gold)
- **Event Organization**: Plan and visualize the sequence of events chronologically
- **Event Details**: Track chapter, location, participants, and descriptions
- **Context Menu Actions**: 
  - Add Child Event (sequential progression)
  - Add Choice Branch (branching paths)
  - Delete nodes with confirmation
- **Zoom Controls**: Zoom in/out/reset for large timelines
- **Scrollable Interface**: Right panel with event details fits within window
- **Linked Content**: Connect timeline events to story chapters and gameplay

### Story & Narrative Editor
- **Chapters**: Create and manage game chapters with objectives, descriptions, and maps
  - Sequential chapter organization with up/down reordering
  - Chapter events organized into three categories:
    - **Pre-Chapter Story Events**: Cutscenes/dialogue before the mission
    - **Gameplay Events**: Triggers during battle (unit spawns, reinforcements, dialogue)
    - **Post-Chapter Story Events**: Cutscenes/dialogue after mission completion
- **Event System**: Comprehensive event editor with:
  - Event types (Cutscene, Dialogue, Narration, Unit Spawn, Reinforcements, etc.)
  - Trigger conditions (Auto, Turn, Position, Talk, Enemy Defeated, HP Threshold, Custom)
  - Background images and music per event
  - Sequential dialogue lines with speaker, portrait, and text
  - Visual indicator showing which event you're editing
  - Drag-and-drop reordering within each event category
- **Characters**: Design characters with:
  - Auto-generated 8-digit unique IDs
  - Names, titles, affiliations, and biographies
  - Optional portrait images
  - Multiple custom sprite variants (Idle, Attack, Promoted, etc.)
  - Generic units can have empty portraits/sprites
- **Support Conversations**: Framework for character support conversations (C/B/A/S ranks)

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

3. (Optional) C++ engine development:
   - The engine uses vcpkg for dependency management
   - Clone vcpkg into the Lehran directory:
     ```powershell
     cd Lehran
     git clone https://github.com/microsoft/vcpkg.git
     cd vcpkg
     .\bootstrap-vcpkg.bat
     ```
   - Then build the engine using `quick_build.ps1` - it will automatically install SDL2 dependencies
   - Subsequent builds don't require vcpkg setup

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

1. Go to the **Story** tab
2. **Chapters Sub-tab**:
   - Click "Add Chapter" to create a new chapter
   - Fill in chapter details (name, number, objective, description, map)
   - Use the three event category tabs:
     - **Pre-Chapter Story**: Events before the mission (cutscenes, dialogue)
     - **Gameplay Events**: Events during battle (spawns, reinforcements, dialogue)
     - **Post-Chapter Story**: Events after the mission (rewards, cutscenes)
   - For each event:
     - Set event type and trigger condition
     - Add background image and music (optional)
     - Add sequential dialogue lines with speaker/portrait/text
     - Use ↑↓ buttons to reorder events within each category
   - Visual indicator shows which event's dialogue you're editing
3. **Characters Sub-tab**:
   - Click "Add Character" (auto-generates unique 8-digit ID)
   - Fill in name, title, affiliation, description, and biography
   - Optionally add portrait image
   - Add multiple sprite variants with custom labels (Idle, Attack, Promoted, etc.)
   - Generic units can leave portraits/sprites empty
4. **Support Conversations Sub-tab**: (Framework for future implementation)

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
   - Copy the entire `data` folder from your project (includes game_flow.json and scenes/)
   - Export story data with pre/gameplay/post event structure
   - Export gameplay data (classes, units, weapons, items)
   - Export timeline data and audio assignments
   - Package the C++ game engine with your project data
   - Copy all 14 required DLLs (SDL2 + codecs) automatically
   - Copy all assets from your project's asset folders
   - Create a standalone executable in `Projects/[YourGame]/build/`
3. Run your built game with **Build > Run Game** or press `F5`
4. Your game will feature:
   - Custom splash screen with fade effects (3.5 seconds)
   - Title screen with your game's name and assigned music
   - Menu navigation (New Game/Load/Exit)
   - 5 save slots with JSON and binary backup formats
   - Data-driven scene system (loads from JSON files)
   - Background and music loading per scene
   - Dialogue system with speaker names and text wrapping
   - Platform-specific save directories (AppData on Windows)
   - Graceful handling of missing assets (no crashes)
5. The build folder contains:
   - Your game executable (renamed to your project name)
   - All 14 SDL2 and codec DLLs
   - data/ folder with all JSON files including scenes/
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
The engine exports project data to a data-driven C++ game runtime built with SDL2.

**Engine Components:**
- `engine/main.cpp` - Core game engine with modular architecture:
  - **TextureManager**: Centralized image loading with caching (PNG/JPG)
  - **SaveSlotScreen**: 5 save slots with New Game and Load Game modes
  - **SceneManager**: Background rendering with fade transitions
  - **DialogueSystem**: Text boxes with word wrapping, speaker names, portrait support
  - **SaveManager**: Dual-format saves (JSON + binary) with platform-specific directories
  - Data-driven scene system (loads from JSON files)
  - Splash screen with auto-fade transitions (3.5 seconds)
  - Title screen with menu system
  - SDL2 rendering and input handling
  - SDL_mixer audio system with OGG Vorbis support
  - Dynamic music/background loading from scene JSON
  - Graceful audio failure handling (continues if files missing)
  - No hardcoded assets - completely plug-and-play
- `engine/CMakeLists.txt` - Build configuration using vcpkg for all dependencies
- `engine/build_engine.ps1` - Automated build script with DLL management
- `quick_build.ps1` - Convenient engine rebuild wrapper
- `engine/include/` - Modular header files (TextureManager, SaveSlotScreen, SceneManager, DialogueSystem, SaveManager)
- `engine/src/` - Implementation files for all engine systems

**Dependency Management:**
- Uses vcpkg for all C++ libraries (SDL2, SDL2_ttf, SDL2_image, SDL2_mixer)
- vcpkg not included in repo - clone from https://github.com/microsoft/vcpkg.git
- Bootstrap vcpkg, then dependencies auto-install on first engine build via CMake
- All dependencies: SDL2, SDL2_ttf, SDL2_image, SDL2_mixer, libogg, libvorbis, wavpack, freetype, libpng, brotli, bzip2, zlib
- No manual dependency downloads required

**Runtime Structure:**
- `runtime/LehranEngine.exe` - Compiled game engine executable
- `runtime/*.dll` - All SDL2 libraries and codec DLLs (14 total):
  - SDL2.dll, SDL2_ttf.dll, SDL2_image.dll, SDL2_mixer.dll
  - Audio codecs: vorbis.dll, vorbisfile.dll, ogg.dll, wavpackdll.dll
  - Image codecs: libpng16.dll, brotlicommon.dll, brotlidec.dll, bz2.dll
  - Font rendering: freetype.dll, zlib1.dll
- Build system automatically copies all required DLLs

**Build Output (per project):**
```
Projects/[YourGame]/build/
├── [YourGame].exe          # Standalone game executable
├── *.dll (14 files)        # All SDL2 and codec libraries
├── data/
│   ├── manifest.json       # Project metadata
│   ├── story.json          # Chapters with pre/gameplay/post events, characters
│   ├── gameplay.json       # Classes, units, weapons, items
│   ├── timeline.json       # Event sequence and branches
│   ├── audio_assignments.json  # Audio role mappings
│   ├── game_flow.json      # Starting scene configuration
│   └── scenes/
│       └── *.json          # Individual scene definitions (dialogue, music, backgrounds)
├── assets/
│   ├── bgm/                # Background music files
│   ├── sfx/                # Sound effect files
│   ├── portraits/          # Character portraits
│   ├── sprites/            # Unit sprites
│   ├── backgrounds/        # Scene background images
│   ├── ui/                 # UI elements
│   └── animations/         # Battle animations
├── maps/                   # Tiled maps (if any)
└── README.txt              # How to run the game
```

## File Formats

### .lehran Project Files
JSON-based project files containing:
- Project metadata (name, version, timestamps)
- Timeline data (event sequence, branches, and node-based visualization)
- Story data:
  - Chapters with pre-chapter, gameplay, and post-chapter events
  - Characters with unique IDs, portraits, and sprite variants
  - Support conversations framework
- Gameplay data (classes, units, weapons, items with type-specific properties)
- Map references and configuration
- Audio assignments (music and SFX role mappings)

### Scene Format
Data-driven scene JSON files in `data/scenes/`:
```json
{
  "scene_id": "prologue_intro",
  "name": "Prologue - Castle Approach",
  "background": "backgrounds/castle.png",
  "music": "bgm/tension.ogg",
  "dialogue": [
    {
      "speaker": "Character Name",
      "portrait": "portraits/character.png",
      "text": "Dialogue line here..."
    }
  ],
  "next_scene": "next_scene_id"
}
```
- Scenes are completely data-driven (no hardcoding in engine)
- `game_flow.json` defines the starting scene
- Engine loads scenes dynamically from JSON files

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
- [x] Timeline editor with node-based visualization and branching paths
- [x] Story editor with comprehensive event system:
  - [x] Chapters with pre/gameplay/post event categories
  - [x] Sequential event ordering with visual reordering (↑↓)
  - [x] Event-based dialogue system (dialogue tied to specific events)
  - [x] Background and music per event
  - [x] Visual indicator showing current event context
  - [x] Scrollable interface preventing window overflow
- [x] Character system with unique IDs, portraits, and sprite variants
- [x] Gameplay editor (classes, units, weapons, items with conditional properties)
- [x] Drag-and-drop reordering for all gameplay elements
- [x] Type-specific item properties (Consumable, Stat Booster, Promotion, Key, Special)
- [x] Tiled integration for map editing
- [x] Asset Manager with browser and preview
- [x] Audio assignment system (link files to game events)
- [x] C++ game runtime with modular architecture:
  - [x] TextureManager (image loading with caching)
  - [x] SaveSlotScreen (5 slots, New Game/Load Game)
  - [x] SceneManager (backgrounds with fade transitions)
  - [x] DialogueSystem (text wrapping, speaker names, portraits)
  - [x] SaveManager (JSON + binary, platform-specific directories)
- [x] Data-driven scene system (no hardcoded assets)
- [x] SDL2, SDL2_ttf, SDL2_image, SDL2_mixer integration
- [x] vcpkg dependency management (automatic setup)
- [x] Dynamic scene loading from JSON files
- [x] game_flow.json for starting scene configuration
- [x] Build system with automatic DLL copying (all 14 libraries)
- [x] Graceful handling of missing assets (no crashes)
- [x] Splash screen and title screen
- [x] Console-free release builds
- [x] No fallback audio when "(None)" selected

### In Progress / Future
- [ ] Scene JSON export from GUI (currently manual)
- [ ] Portrait rendering in dialogue system
- [ ] Choice/branching dialogue with save prompts
- [ ] Scene chaining (next_scene navigation)
- [ ] Map rendering from Tiled files in game runtime
- [ ] Unit placement and movement system
- [ ] Combat system implementation
- [ ] Event scripting system
- [ ] Battle animations
- [ ] Character progression and stats
- [ ] AI for enemy units
- [ ] Additional game states (base, shop, battle prep)
- [ ] Volume controls in audio assignments
- [ ] Music crossfade and transition effects
- [ ] Testing and debugging tools

## License

This is a fan project. Fire Emblem is © Intelligent Systems/Nintendo.