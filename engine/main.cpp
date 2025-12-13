/*
 * Lehran Engine - Fire Emblem Fan Game Engine
 * Main entry point
 */

#include <SDL.h>
#include <SDL_ttf.h>
#include <SDL_image.h>
#include <SDL2/SDL_mixer.h>
#include <iostream>
#include <string>
#include <fstream>
#include "json.hpp"
#include "SaveManager.hpp"
#include "TextureManager.hpp"
#include "SaveSlotScreen.hpp"
#include "SceneManager.hpp"
#include "DialogueSystem.hpp"
#include "ConfigManager.hpp"
#include "RenderManager.hpp"
#include "GameStateManager.hpp"
#include "InputHandler.hpp"
#include "MapManager.hpp"

using json = nlohmann::json;

// Screen dimensions
const int SCREEN_WIDTH = 1920;
const int SCREEN_HEIGHT = 1080;

class LehranEngine {
private:
    SDL_Window* window;
    SDL_Renderer* renderer;
    TTF_Font* fontLarge;
    TTF_Font* fontMedium;
    TTF_Font* fontSmall;
    Mix_Music* bgm;
    std::string currentMusicPath;  // Track currently playing music
    json gameData;
    json audioAssignments;
    json gameFlow;
    std::string gameName;
    bool audioInitialized;
    
    // Modular systems
    Lehran::ConfigManager* configManager;
    Lehran::RenderManager* renderManager;
    Lehran::GameStateManager* stateManager;
    Lehran::InputHandler* inputHandler;
    Lehran::SaveManager* saveManager;
    TextureManager* textureManager;
    SaveSlotScreen* saveSlotScreen;
    SceneManager* sceneManager;
    DialogueSystem* dialogueSystem;
    Lehran::MapManager* mapManager;
    
public:
    LehranEngine() : window(nullptr), renderer(nullptr), 
                     fontLarge(nullptr), fontMedium(nullptr), fontSmall(nullptr),
                     bgm(nullptr), currentMusicPath(""), audioInitialized(false),
                     configManager(nullptr), renderManager(nullptr), stateManager(nullptr),
                     inputHandler(nullptr), saveManager(nullptr), textureManager(nullptr),
                     saveSlotScreen(nullptr), sceneManager(nullptr),
                     dialogueSystem(nullptr), mapManager(nullptr) {}
    
    bool Initialize() {
        // Create modular systems first
        configManager = new Lehran::ConfigManager();
        stateManager = new Lehran::GameStateManager();
        inputHandler = new Lehran::InputHandler();
        
        // Load engine settings
        configManager->LoadEngineSettings();
        
        // Initialize SDL
        if (SDL_Init(SDL_INIT_VIDEO | SDL_INIT_AUDIO) < 0) {
            std::cerr << "SDL initialization failed: " << SDL_GetError() << std::endl;
            return false;
        }
        
        // Detect native display resolution
        SDL_DisplayMode displayMode;
        if (SDL_GetCurrentDisplayMode(0, &displayMode) == 0) {
            configManager->SetNativeDisplaySize(displayMode.w, displayMode.h);
            std::cout << "Detected native display: " << displayMode.w << "x" << displayMode.h << std::endl;
        } else {
            std::cerr << "Failed to detect display mode, using defaults" << std::endl;
        }
        
        // Initialize SDL_ttf
        if (TTF_Init() == -1) {
            std::cerr << "SDL_ttf initialization failed: " << TTF_GetError() << std::endl;
            return false;
        }
        
        // Initialize SDL_image
        int imgFlags = IMG_INIT_PNG | IMG_INIT_JPG;
        if (!(IMG_Init(imgFlags) & imgFlags)) {
            std::cerr << "SDL_image initialization failed: " << IMG_GetError() << std::endl;
            return false;
        }
        
        // Initialize SDL_mixer (graceful failure - audio is optional)
        if (Mix_OpenAudio(44100, MIX_DEFAULT_FORMAT, 2, 2048) < 0) {
            std::cerr << "SDL_mixer initialization failed: " << Mix_GetError() << std::endl;
            std::cerr << "Continuing without audio..." << std::endl;
            audioInitialized = false;
        } else {
            audioInitialized = true;
            std::cout << "Audio initialized successfully" << std::endl;
        }
        
        // Create window
        Uint32 windowFlags = SDL_WINDOW_SHOWN | SDL_WINDOW_RESIZABLE;
        
        int createWidth = configManager->GetWindowWidth();
        int createHeight = configManager->GetWindowHeight();
        Lehran::WindowMode windowMode = configManager->GetWindowMode();
        
        if (windowMode == Lehran::WindowMode::BORDERLESS) {
            windowFlags |= SDL_WINDOW_FULLSCREEN_DESKTOP;
        } else if (windowMode == Lehran::WindowMode::FULLSCREEN) {
            windowFlags |= SDL_WINDOW_FULLSCREEN;
            createWidth = configManager->GetNativeDisplayWidth();
            createHeight = configManager->GetNativeDisplayHeight();
        }
        
        window = SDL_CreateWindow("Lehran Engine",
                                  SDL_WINDOWPOS_CENTERED,
                                  SDL_WINDOWPOS_CENTERED,
                                  createWidth, createHeight,
                                  windowFlags);
        
        const char* modeStr = (windowMode == Lehran::WindowMode::WINDOWED) ? "Windowed" : 
                              (windowMode == Lehran::WindowMode::BORDERLESS) ? "Borderless" : "Fullscreen";
        std::cout << "Window created: " << createWidth << "x" << createHeight 
                  << " (" << modeStr << ")" << std::endl;
        
        if (!window) {
            std::cerr << "Window creation failed: " << SDL_GetError() << std::endl;
            return false;
        }
        
        // Create renderer
        renderer = SDL_CreateRenderer(window, -1, SDL_RENDERER_ACCELERATED | SDL_RENDERER_PRESENTVSYNC);
        if (!renderer) {
            std::cerr << "Renderer creation failed: " << SDL_GetError() << std::endl;
            return false;
        }
        
        // Set logical size for proper scaling
        SDL_RenderSetLogicalSize(renderer, SCREEN_WIDTH, SCREEN_HEIGHT);
        SDL_RenderSetIntegerScale(renderer, SDL_FALSE);
        std::cout << "Render logical size set to: " << SCREEN_WIDTH << "x" << SCREEN_HEIGHT << std::endl;
        
        // Load fonts
        fontLarge = TTF_OpenFont("C:\\Windows\\Fonts\\arial.ttf", 48);
        fontMedium = TTF_OpenFont("C:\\Windows\\Fonts\\arial.ttf", 32);
        fontSmall = TTF_OpenFont("C:\\Windows\\Fonts\\arial.ttf", 20);
        
        if (!fontLarge || !fontMedium || !fontSmall) {
            std::cerr << "Font loading failed: " << TTF_GetError() << std::endl;
            fontLarge = TTF_OpenFont("C:\\Windows\\Fonts\\segoeui.ttf", 48);
            fontMedium = TTF_OpenFont("C:\\Windows\\Fonts\\segoeui.ttf", 32);
            fontSmall = TTF_OpenFont("C:\\Windows\\Fonts\\segoeui.ttf", 20);
            
            if (!fontLarge || !fontMedium || !fontSmall) {
                std::cerr << "Alternate font also failed: " << TTF_GetError() << std::endl;
                return false;
            }
        }
        
        // Initialize render manager
        renderManager = new Lehran::RenderManager(renderer, fontLarge, fontMedium, fontSmall);
        
        // Initialize game systems
        saveManager = new Lehran::SaveManager();
        textureManager = new TextureManager(renderer);
        
        // Load game data
        LoadGameData();
        
        // Initialize remaining systems
        saveSlotScreen = new SaveSlotScreen(renderer, fontLarge, fontMedium, fontSmall, saveManager);
        sceneManager = new SceneManager(renderer, textureManager);
        dialogueSystem = new DialogueSystem(renderer, fontMedium, fontSmall, textureManager);
        mapManager = new Lehran::MapManager(renderer, textureManager, configManager, fontMedium);
        
        // Setup input handler callbacks
        SetupInputCallbacks();
        
        // Setup state manager callbacks
        SetupStateCallbacks();
        
        std::cout << "All systems initialized successfully" << std::endl;
        
        return true;
    }
    
    void SetupInputCallbacks() {
        inputHandler->SetSaveSlotScreen(saveSlotScreen);
        inputHandler->SetDialogueSystemHandleInput([this](SDL_Keycode key) {
            dialogueSystem->HandleInput(key);
        });
        inputHandler->SetDialogueCompleteCheck([this]() {
            return dialogueSystem->IsComplete();
        });
        inputHandler->SetSaveSlotSelectedCheck([this]() {
            return saveSlotScreen->HasSelectedSlot();
        });
        inputHandler->SetSaveSlotReturnCheck([this]() {
            return saveSlotScreen->ShouldReturnToTitle();
        });
        inputHandler->SetGetSelectedSlot([this]() {
            return saveSlotScreen->GetSelectedSlot();
        });
        inputHandler->SetGetSaveScreenMode([this]() {
            return stateManager->GetSaveScreenMode();
        });
        inputHandler->SetGetSelectedSettingsItem([this]() {
            return stateManager->GetSelectedSettingsItem();
        });
        inputHandler->SetGetSelectedMenuItem([this]() {
            return stateManager->GetSelectedMenuItem();
        });
        
        // State change callback
        inputHandler->SetStateChangeCallback([this](Lehran::GameState newState) {
            if (newState == Lehran::GameState::STATE_SCENE) {
                // Dialogue complete - end scene
                stateManager->EndScene(sceneManager, dialogueSystem);
            } else {
                // Check if returning to title screen - reload title music
                if (newState == Lehran::GameState::STATE_TITLE && 
                    stateManager->GetCurrentState() != Lehran::GameState::STATE_TITLE) {
                    LoadTitleMusic();
                }
                stateManager->SetCurrentState(newState);
            }
        });
        
        // Title menu callback
        inputHandler->SetTitleMenuCallback([this](int action) {
            if (action >= 0) {
                // Just navigation
                stateManager->SetSelectedMenuItem(action);
            } else if (action <= -100) {
                // Game start signal
                int slotNumber = -(action + 1000);
                stateManager->StartGameFromSlot(slotNumber, saveManager, gameFlow);
                if (!stateManager->GetCurrentSceneId().empty()) {
                    stateManager->LoadScene(stateManager->GetCurrentSceneId(), sceneManager, dialogueSystem);
                }
            } else {
                // Menu selection
                int selected = -(action + 1);
                HandleTitleSelection(selected);
            }
        });
        
        // Settings action callback
        inputHandler->SetSettingsActionCallback([this](int item, bool isLeft) {
            if (item < -199) {
                // Adjustment action (LEFT/RIGHT pressed)
                int actualItem = -(item + 200);
                HandleSettingsAdjustment(actualItem, isLeft);
            } else if (item < -99) {
                // Selection action (RETURN/SPACE pressed)
                int actualItem = -(item + 100);
                HandleSettingsSelection(actualItem);
            } else {
                // Navigation only (UP/DOWN pressed)
                stateManager->SetSelectedSettingsItem(item);
                
                // Auto-scroll to keep selected item in comfortable viewing zone
                // All coordinates relative to the logical 1920x1080 resolution
                float itemSpacing = 100.0f;
                float itemYPos = 350.0f + (item * itemSpacing); // Position without scroll
                float currentScroll = static_cast<float>(stateManager->GetSettingsScrollOffset());
                
                // Use thresholds slightly above/below center (relative to 1080p)
                float screenCenterY = SCREEN_HEIGHT / 2.0f; // 540
                float scrollThresholdUp = screenCenterY - 60.0f;    // ~480 - a bit above center
                float scrollThresholdDown = screenCenterY + 60.0f;  // ~600 - a bit below center
                
                // Calculate item's screen position with current scroll
                float screenY = itemYPos - currentScroll;
                
                // Adjust scroll if item crosses thresholds
                if (screenY < scrollThresholdUp) {
                    // Item is above threshold - scroll up to recenter
                    float newScroll = itemYPos - scrollThresholdUp;
                    stateManager->SetSettingsScrollOffset(static_cast<int>(newScroll));
                } else if (screenY > scrollThresholdDown) {
                    // Item is below threshold - scroll down to recenter
                    float newScroll = itemYPos - scrollThresholdDown;
                    stateManager->SetSettingsScrollOffset(static_cast<int>(newScroll));
                }
                
                // Clamp scroll to valid range (0 to maxScroll)
                // 9 items * 100px spacing = 900px total height
                // Visible area is roughly 650px, so max scroll = 900 - 650 = 250
                // But existing system uses 600 as max, so keep that
                int finalScroll = stateManager->GetSettingsScrollOffset();
                if (finalScroll < 0) stateManager->SetSettingsScrollOffset(0);
                if (finalScroll > 600) stateManager->SetSettingsScrollOffset(600);
            }
        });
        
        // Scroll callback
        inputHandler->SetScrollCallback([this](int wheelY) {
            stateManager->AdjustSettingsScrollOffset(wheelY);
        });
        
        // Window mode callback
        inputHandler->SetWindowModeCallback([this]() {
            CycleWindowMode();
        });
        
        // Map cursor callback
        inputHandler->SetMapCursorMoveCallback([this](int dx, int dy) {
            mapManager->MoveCursor(dx, dy);
        });
        
        inputHandler->SetMapSelectCallback([this]() {
            if (mapManager->HasSelectedUnit()) {
                // Unit already selected - try to confirm move
                mapManager->ConfirmMove();
            } else {
                // No unit selected - try to select one
                mapManager->SelectUnit();
            }
        });
        
        inputHandler->SetMapCancelCallback([this]() -> bool {
            if (mapManager->HasSelectedUnit()) {
                mapManager->CancelSelection();
                return true;  // Cancelled something
            }
            return false;  // Nothing to cancel
        });
        
        inputHandler->SetMapActionMenuCallback([this](int action) -> int {
            if (action == -1000) {
                // Query: is menu showing?
                return mapManager->IsShowingActionMenu() ? 1 : 0;
            } else if (action == -1 || action == 1) {
                // Navigation
                mapManager->MoveActionSelection(action);
                return 0;
            } else if (action == 100) {
                // Confirm
                mapManager->ConfirmAction();
                return 0;
            } else if (action == -100) {
                // Cancel action menu - restore unit position and return to movement selection
                mapManager->CancelActionMenu();
                return 0;
            }
            return 0;
        });
        
        inputHandler->SetMapInventoryCallback([this](int action) -> int {
            if (action == -2000) {
                // Query: is inventory showing?
                return mapManager->IsShowingInventory() ? 1 : 0;
            } else if (action == -1 || action == 1) {
                // Navigation (only if not in drop confirmation)
                if (!mapManager->IsShowingDropConfirmation()) {
                    mapManager->MoveInventorySelection(action);
                }
                return 0;
            } else if (action == 100) {
                // Confirm - equip/drop item or confirm drop
                mapManager->ConfirmInventoryAction();
                return 0;
            } else if (action == -100) {
                // Cancel - close inventory or cancel drop confirmation
                if (mapManager->IsShowingDropConfirmation()) {
                    mapManager->CancelDropConfirmation();
                } else {
                    mapManager->CloseInventory();
                }
                return 0;
            }
            return 0;
        });
        
        inputHandler->SetMapToggleUnitInfoCallback([this]() {
            mapManager->ToggleUnitInfo();
        });
    }
    
    void SetupStateCallbacks() {
        stateManager->SetLoadTitleMusicCallback([this]() {
            LoadTitleMusic();
        });
        stateManager->SetLoadSceneMusicCallback([this](const std::string& musicFile) {
            LoadSceneMusic(musicFile);
        });
        stateManager->SetStartDialogueCallback([this]() {
            dialogueSystem->Start();
        });
    }
    
    void LoadTitleMusic() {
        if (!audioInitialized) return;
        
        std::string musicPath = "";
        bool shouldPlayMusic = false;
        
        if (audioAssignments.contains("title_music")) {
            std::string assigned = audioAssignments["title_music"];
            if (!assigned.empty()) {
                musicPath = "assets/" + assigned;
                shouldPlayMusic = true;
            }
        }
        
        if (!shouldPlayMusic) {
            std::cout << "Title music set to (None) - running without music" << std::endl;
            currentMusicPath = "";
            return;
        }
        
        // Check if this music is already playing
        if (currentMusicPath == musicPath && Mix_PlayingMusic()) {
            std::cout << "Title music already playing, not restarting" << std::endl;
            return;
        }
        
        if (bgm) {
            Mix_FreeMusic(bgm);
            bgm = nullptr;
        }
        
        bgm = Mix_LoadMUS(musicPath.c_str());
        
        if (!bgm) {
            std::cerr << "Failed to load music: " << Mix_GetError() << std::endl;
            currentMusicPath = "";
        } else {
            std::cout << "Title music loaded successfully from: " << musicPath << std::endl;
            if (Mix_PlayMusic(bgm, -1) == -1) {
                std::cerr << "Failed to play music: " << Mix_GetError() << std::endl;
                currentMusicPath = "";
            } else {
                configManager->ApplyAudioVolumes(audioInitialized);
                currentMusicPath = musicPath;
            }
        }
    }
    
    void LoadGameData() {
        try {
            std::ifstream file("data/manifest.json");
            if (file.is_open()) {
                file >> gameData;
                gameName = gameData.value("name", "Untitled Game");
                file.close();
                
                if (saveManager) {
                    std::string saveSubdir = gameData.value("save_directory", "");
                    if (saveSubdir.empty()) {
                        saveSubdir = gameName;
                    }
                    saveManager->set_project_subdirectory(saveSubdir);
                }
            } else {
                gameName = "Untitled Game";
            }
        } catch (const std::exception& e) {
            gameName = "Untitled Game";
        }
        
        try {
            std::ifstream audioFile("data/audio_assignments.json");
            if (audioFile.is_open()) {
                audioFile >> audioAssignments;
                audioFile.close();
                std::cout << "Audio assignments loaded successfully" << std::endl;
            }
        } catch (const std::exception& e) {
            std::cerr << "Failed to load audio assignments: " << e.what() << std::endl;
        }
        
        try {
            std::ifstream flowFile("data/game_flow.json");
            if (flowFile.is_open()) {
                flowFile >> gameFlow;
                flowFile.close();
                std::cout << "Game flow loaded successfully" << std::endl;
            }
        } catch (const std::exception& e) {
            std::cerr << "Failed to load game flow: " << e.what() << std::endl;
        }
        
        if (window) {
            SDL_SetWindowTitle(window, gameName.c_str());
        }
    }
    
    void HandleTitleSelection(int selected) {
        if (selected == 0) {
            // New Game
            stateManager->SetSaveScreenMode(static_cast<int>(SaveSlotScreen::Mode::NEW_GAME));
            saveSlotScreen->SetMode(SaveSlotScreen::Mode::NEW_GAME);
            saveSlotScreen->Reset();
            stateManager->SetCurrentState(Lehran::GameState::STATE_SAVE_SELECT);
        } else if (selected == 1) {
            // Load Game
            stateManager->SetSaveScreenMode(static_cast<int>(SaveSlotScreen::Mode::LOAD_GAME));
            saveSlotScreen->SetMode(SaveSlotScreen::Mode::LOAD_GAME);
            saveSlotScreen->Reset();
            stateManager->SetCurrentState(Lehran::GameState::STATE_SAVE_SELECT);
        } else if (selected == 2) {
            // Settings
            stateManager->SetSelectedSettingsItem(0);
            stateManager->SetSettingsScrollOffset(0);
            stateManager->SetCurrentState(Lehran::GameState::STATE_SETTINGS);
        } else if (selected == 3) {
            // Map Test
            mapManager->LoadMap("maps/Battle/test_map.json");
            
            // Load map music if specified
            std::string mapMusic = mapManager->GetMapMusic();
            if (!mapMusic.empty()) {
                if (bgm) {
                    Mix_FreeMusic(bgm);
                    bgm = nullptr;
                }
                bgm = Mix_LoadMUS(mapMusic.c_str());
                if (bgm) {
                    Mix_PlayMusic(bgm, -1);
                    currentMusicPath = mapMusic;
                    std::cout << "Playing map music: " << mapMusic << std::endl;
                } else {
                    std::cerr << "Failed to load map music: " << mapMusic << std::endl;
                    currentMusicPath = "";
                }
            }
            
            stateManager->SetCurrentState(Lehran::GameState::STATE_MAP);
        } else if (selected == 4) {
            // VN Scene Test
            stateManager->LoadScene("vn_test", sceneManager, dialogueSystem);
        } else if (selected == 5) {
            stateManager->SetCurrentState(Lehran::GameState::STATE_QUIT);
        }
    }
    
    void HandleSettingsSelection(int item) {
        if (item == 0) {
            // Cycle window mode forward
            CycleWindowModeForward();
        } else if (item == 6) {
            // Copy Data
            stateManager->SetSaveScreenMode(static_cast<int>(SaveSlotScreen::Mode::COPY_DATA));
            saveSlotScreen->SetMode(SaveSlotScreen::Mode::COPY_DATA);
            saveSlotScreen->Reset();
            stateManager->SetCurrentState(Lehran::GameState::STATE_SAVE_SELECT);
        } else if (item == 7) {
            // Delete Data
            stateManager->SetSaveScreenMode(static_cast<int>(SaveSlotScreen::Mode::DELETE_DATA));
            saveSlotScreen->SetMode(SaveSlotScreen::Mode::DELETE_DATA);
            saveSlotScreen->Reset();
            stateManager->SetCurrentState(Lehran::GameState::STATE_SAVE_SELECT);
        } else if (item == 8) {
            // Back to title
            configManager->SaveEngineSettings();
            stateManager->SetCurrentState(Lehran::GameState::STATE_TITLE);
        }
    }
    
    void HandleSettingsAdjustment(int item, bool isLeft) {
        if (item == 0) {
            // Window mode
            if (isLeft) {
                CycleWindowModeBackward();
            } else {
                CycleWindowModeForward();
            }
        } else if (item == 1 && configManager->GetWindowMode() == Lehran::WindowMode::WINDOWED) {
            // Resolution
            if (isLeft) {
                configManager->CycleResolutionBackward();
            } else {
                configManager->CycleResolutionForward();
            }
            ApplyResolution();
        } else if (item >= 2 && item <= 5) {
            // Audio volumes
            int delta = isLeft ? -5 : 5;
            if (item == 2) {
                configManager->SetMasterVolume(configManager->GetMasterVolume() + delta);
                configManager->ApplyAudioVolumes(audioInitialized);
            } else if (item == 3) {
                configManager->SetMusicVolume(configManager->GetMusicVolume() + delta);
                configManager->ApplyAudioVolumes(audioInitialized);
            } else if (item == 4) {
                configManager->SetSFXVolume(configManager->GetSFXVolume() + delta);
                configManager->ApplyAudioVolumes(audioInitialized);
            } else if (item == 5) {
                configManager->SetVoiceVolume(configManager->GetVoiceVolume() + delta);
                configManager->ApplyAudioVolumes(audioInitialized);
            }
        }
    }
    
    void LoadSceneMusic(const std::string& musicFile) {
        if (!audioInitialized) return;
        
        if (bgm) {
            Mix_FreeMusic(bgm);
            bgm = nullptr;
        }
        
        std::string musicPath = "assets/" + musicFile;
        bgm = Mix_LoadMUS(musicPath.c_str());
        
        if (!bgm) {
            std::cerr << "Failed to load scene music: " << Mix_GetError() << std::endl;
            currentMusicPath = "";
        } else {
            std::cout << "Scene music loaded: " << musicPath << std::endl;
            if (Mix_PlayMusic(bgm, -1) == -1) {
                std::cerr << "Failed to play scene music: " << Mix_GetError() << std::endl;
                currentMusicPath = "";
            } else {
                configManager->ApplyAudioVolumes(audioInitialized);
                currentMusicPath = musicPath;
            }
        }
    }
    
    void CycleWindowMode() {
        CycleWindowModeForward();
    }
    
    void Run() {
        bool running = true;
        SDL_Event event;
        Uint32 lastTime = SDL_GetTicks();
        
        while (running && stateManager->GetCurrentState() != Lehran::GameState::STATE_QUIT) {
            Uint32 currentTime = SDL_GetTicks();
            float deltaTime = (currentTime - lastTime) / 1000.0f;
            lastTime = currentTime;
            
            // Handle events
            while (SDL_PollEvent(&event)) {
                if (event.type == SDL_QUIT) {
                    running = false;
                } else if (event.type == SDL_KEYDOWN) {
                    inputHandler->HandleKeyDown(event.key.keysym.sym, stateManager->GetCurrentState());
                } else if (event.type == SDL_MOUSEWHEEL) {
                    inputHandler->HandleMouseWheel(event.wheel.y, stateManager->GetCurrentState());
                }
            }
            
            Update(deltaTime);
            
            SDL_SetRenderDrawColor(renderer, 0, 0, 0, 255);
            SDL_RenderClear(renderer);
            Render();
            SDL_RenderPresent(renderer);
        }
    }
    
    void CycleWindowModeForward() {
        int currentMode = static_cast<int>(configManager->GetWindowMode());
        configManager->SetWindowMode(static_cast<Lehran::WindowMode>((currentMode + 1) % 3));
        ApplyWindowMode();
    }
    
    void CycleWindowModeBackward() {
        int currentMode = static_cast<int>(configManager->GetWindowMode());
        configManager->SetWindowMode(static_cast<Lehran::WindowMode>((currentMode + 2) % 3));
        ApplyWindowMode();
    }
    
    void ApplyWindowMode() {
        SDL_SetWindowFullscreen(window, 0);
        
        Lehran::WindowMode windowMode = configManager->GetWindowMode();
        if (windowMode == Lehran::WindowMode::WINDOWED) {
            SDL_SetWindowSize(window, configManager->GetWindowWidth(), configManager->GetWindowHeight());
            SDL_SetWindowPosition(window, SDL_WINDOWPOS_CENTERED, SDL_WINDOWPOS_CENTERED);
            std::cout << "Switched to windowed mode (" << configManager->GetWindowWidth() 
                      << "x" << configManager->GetWindowHeight() << ")" << std::endl;
        } else if (windowMode == Lehran::WindowMode::BORDERLESS) {
            SDL_SetWindowFullscreen(window, SDL_WINDOW_FULLSCREEN_DESKTOP);
            std::cout << "Switched to borderless fullscreen" << std::endl;
        } else if (windowMode == Lehran::WindowMode::FULLSCREEN) {
            SDL_DisplayMode displayMode;
            if (SDL_GetCurrentDisplayMode(0, &displayMode) == 0) {
                SDL_SetWindowDisplayMode(window, &displayMode);
            }
            SDL_SetWindowFullscreen(window, SDL_WINDOW_FULLSCREEN);
            std::cout << "Switched to fullscreen (" << configManager->GetNativeDisplayWidth() 
                      << "x" << configManager->GetNativeDisplayHeight() << ")" << std::endl;
        }
        
        configManager->SaveEngineSettings();
    }
    
    void ApplyResolution() {
        if (configManager->GetWindowMode() != Lehran::WindowMode::WINDOWED) return;
        
        SDL_SetWindowSize(window, configManager->GetWindowWidth(), configManager->GetWindowHeight());
        SDL_SetWindowPosition(window, SDL_WINDOWPOS_CENTERED, SDL_WINDOWPOS_CENTERED);
        configManager->SaveEngineSettings();
        
        std::cout << "Resolution changed to: " << configManager->GetWindowWidth() 
                  << "x" << configManager->GetWindowHeight() << std::endl;
    }
    
    void Update(float deltaTime) {
        Lehran::GameState currentState = stateManager->GetCurrentState();
        
        if (currentState == Lehran::GameState::STATE_SPLASH) {
            stateManager->UpdateSplashTimer(deltaTime);
            if (stateManager->ShouldTransitionFromSplash()) {
                stateManager->SetCurrentState(Lehran::GameState::STATE_TITLE);
                LoadTitleMusic();
            }
        } else if (currentState == Lehran::GameState::STATE_SCENE) {
            sceneManager->Update(deltaTime);
            
            if (sceneManager->IsTransitionComplete() && !dialogueSystem->IsActive()) {
                stateManager->SetCurrentState(Lehran::GameState::STATE_DIALOGUE);
                dialogueSystem->Start();
            }
        } else if (currentState == Lehran::GameState::STATE_DIALOGUE) {
            dialogueSystem->Update(deltaTime);
        }
    }
    
    void Render() {
        Lehran::GameState currentState = stateManager->GetCurrentState();
        
        switch (currentState) {
            case Lehran::GameState::STATE_SPLASH:
                renderManager->RenderSplash(stateManager->GetSplashTimer());
                break;
            case Lehran::GameState::STATE_TITLE:
                renderManager->RenderTitle(gameName, stateManager->GetSelectedMenuItem(), gameData);
                break;
            case Lehran::GameState::STATE_SAVE_SELECT:
                saveSlotScreen->Render();
                break;
            case Lehran::GameState::STATE_SETTINGS:
                renderManager->RenderSettings(*configManager, stateManager->GetSelectedSettingsItem(), 
                                            stateManager->GetSettingsScrollOffset());
                break;
            case Lehran::GameState::STATE_SCENE:
                sceneManager->RenderBackground();
                sceneManager->RenderTransition();
                break;
            case Lehran::GameState::STATE_DIALOGUE:
                sceneManager->RenderBackground();
                dialogueSystem->Render();
                break;
            case Lehran::GameState::STATE_MAP:
                mapManager->Render();
                break;
            case Lehran::GameState::STATE_EASTER_EGG:
                renderManager->RenderEasterEgg();
                break;
            default:
                break;
        }
    }
    
    void Cleanup() {
        delete mapManager;
        delete dialogueSystem;
        delete sceneManager;
        delete saveSlotScreen;
        delete textureManager;
        delete saveManager;
        delete inputHandler;
        delete stateManager;
        delete renderManager;
        delete configManager;
        
        if (bgm) {
            Mix_FreeMusic(bgm);
            bgm = nullptr;
        }
        if (audioInitialized) {
            Mix_CloseAudio();
        }
        if (fontLarge) TTF_CloseFont(fontLarge);
        if (fontMedium) TTF_CloseFont(fontMedium);
        if (fontSmall) TTF_CloseFont(fontSmall);
        if (renderer) SDL_DestroyRenderer(renderer);
        if (window) SDL_DestroyWindow(window);
        IMG_Quit();
        TTF_Quit();
        SDL_Quit();
    }
    
    ~LehranEngine() {
        Cleanup();
    }
};

int main(int argc, char* argv[]) {
    LehranEngine engine;
    
    if (!engine.Initialize()) {
        std::cerr << "Failed to initialize engine" << std::endl;
        return 1;
    }
    
    engine.Run();
    
    return 0;
}
