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

using json = nlohmann::json;

// Screen dimensions
const int SCREEN_WIDTH = 800;
const int SCREEN_HEIGHT = 600;

// Game states
enum GameState {
    STATE_SPLASH,
    STATE_TITLE,
    STATE_SAVE_SELECT,
    STATE_SCENE,
    STATE_DIALOGUE,
    STATE_EASTER_EGG,
    STATE_QUIT
};

class LehranEngine {
private:
    SDL_Window* window;
    SDL_Renderer* renderer;
    TTF_Font* fontLarge;
    TTF_Font* fontMedium;
    TTF_Font* fontSmall;
    Mix_Music* bgm;
    GameState currentState;
    int selectedMenuItem;
    float splashTimer;
    json gameData;
    json audioAssignments;
    json gameFlow;
    std::string gameName;
    bool audioInitialized;
    std::string currentSceneId;
    
    // Modular systems
    Lehran::SaveManager* saveManager;
    TextureManager* textureManager;
    SaveSlotScreen* saveSlotScreen;
    SceneManager* sceneManager;
    DialogueSystem* dialogueSystem;
    
    // Game flow state
    int currentSaveSlot;
    SaveSlotScreen::Mode saveScreenMode;
    
public:
    LehranEngine() : window(nullptr), renderer(nullptr), 
                     fontLarge(nullptr), fontMedium(nullptr), fontSmall(nullptr),
                     bgm(nullptr), currentState(STATE_SPLASH), selectedMenuItem(0), 
                     splashTimer(0.0f), audioInitialized(false),
                     saveManager(nullptr), textureManager(nullptr),
                     saveSlotScreen(nullptr), sceneManager(nullptr),
                     dialogueSystem(nullptr), currentSaveSlot(-1),
                     saveScreenMode(SaveSlotScreen::Mode::NEW_GAME) {}
    
    bool Initialize() {
        // Initialize SDL
        if (SDL_Init(SDL_INIT_VIDEO | SDL_INIT_AUDIO) < 0) {
            std::cerr << "SDL initialization failed: " << SDL_GetError() << std::endl;
            return false;
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
        window = SDL_CreateWindow("Lehran Engine",
                                  SDL_WINDOWPOS_CENTERED,
                                  SDL_WINDOWPOS_CENTERED,
                                  SCREEN_WIDTH, SCREEN_HEIGHT,
                                  SDL_WINDOW_SHOWN);
        
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
        
        // Load fonts (using default system font for now)
        fontLarge = TTF_OpenFont("C:\\Windows\\Fonts\\arial.ttf", 48);
        fontMedium = TTF_OpenFont("C:\\Windows\\Fonts\\arial.ttf", 32);
        fontSmall = TTF_OpenFont("C:\\Windows\\Fonts\\arial.ttf", 20);
        
        if (!fontLarge || !fontMedium || !fontSmall) {
            std::cerr << "Font loading failed: " << TTF_GetError() << std::endl;
            // Try alternate font
            fontLarge = TTF_OpenFont("C:\\Windows\\Fonts\\segoeui.ttf", 48);
            fontMedium = TTF_OpenFont("C:\\Windows\\Fonts\\segoeui.ttf", 32);
            fontSmall = TTF_OpenFont("C:\\Windows\\Fonts\\segoeui.ttf", 20);
            
            if (!fontLarge || !fontMedium || !fontSmall) {
                std::cerr << "Alternate font also failed: " << TTF_GetError() << std::endl;
                return false;
            }
        }
        
        // Load game data
        LoadGameData();
        
        // Initialize modular systems
        saveManager = new Lehran::SaveManager();
        textureManager = new TextureManager(renderer);
        saveSlotScreen = new SaveSlotScreen(renderer, fontLarge, fontMedium, fontSmall, saveManager);
        sceneManager = new SceneManager(renderer, textureManager);
        dialogueSystem = new DialogueSystem(renderer, fontMedium, fontSmall, textureManager);
        
        std::cout << "All systems initialized successfully" << std::endl;
        
        return true;
    }
    
    void LoadTitleMusic() {
        if (!audioInitialized) {
            return; // Audio not available, skip silently
        }
        
        // Check if we have an assigned title music in audio_assignments.json
        std::string musicPath = "";
        bool shouldPlayMusic = false;
        
        if (audioAssignments.contains("title_music")) {
            // Audio assignments file exists and has title_music entry
            std::string assigned = audioAssignments["title_music"];
            if (!assigned.empty()) {
                musicPath = "assets/" + assigned;
                shouldPlayMusic = true;
            }
            // If assigned is empty, it means "(None)" was selected - don't play music
        }
        // If no audio assignments file or no title_music entry - don't play music
        
        if (!shouldPlayMusic) {
            std::cout << "Title music set to (None) - running without music" << std::endl;
            return;
        }
        
        bgm = Mix_LoadMUS(musicPath.c_str());
        
        if (!bgm) {
            std::cerr << "Failed to load music: " << Mix_GetError() << std::endl;
            std::cerr << "Game will run without title music" << std::endl;
        } else {
            std::cout << "Title music loaded successfully from: " << musicPath << std::endl;
            // Play music on loop (-1 = infinite loop)
            if (Mix_PlayMusic(bgm, -1) == -1) {
                std::cerr << "Failed to play music: " << Mix_GetError() << std::endl;
            } else {
                // Set volume to 50%
                Mix_VolumeMusic(MIX_MAX_VOLUME / 2);
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
            } else {
                gameName = "Untitled Game";
            }
        } catch (const std::exception& e) {
            gameName = "Untitled Game";
        }
        
        // Load audio assignments
        try {
            std::ifstream audioFile("data/audio_assignments.json");
            if (audioFile.is_open()) {
                audioFile >> audioAssignments;
                audioFile.close();
                std::cout << "Audio assignments loaded successfully" << std::endl;
            }
        } catch (const std::exception& e) {
            std::cerr << "Failed to load audio assignments: " << e.what() << std::endl;
            std::cerr << "Using default audio paths" << std::endl;
        }
        
        // Load game flow configuration
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
        
        // Update window title with game name
        if (window) {
            SDL_SetWindowTitle(window, gameName.c_str());
        }
    }
    
    void StartGameFromSlot(int slotNumber) {
        std::cout << "Starting game from slot " << slotNumber << std::endl;
        
        // Load or create save data
        if (saveScreenMode == SaveSlotScreen::Mode::LOAD_GAME) {
            Lehran::SaveData data;
            if (saveManager->load(slotNumber, data)) {
                std::cout << "Loaded save: " << data.slot_name << ", Chapter " << data.current_chapter << std::endl;
                // TODO: Load actual game state from save data
            }
        } else {
            // New game - create initial save data
            Lehran::SaveData newSave;
            newSave.version = 1;
            newSave.slot_name = "New Game";
            newSave.current_chapter = 0;
            newSave.turn_count = 0;
            newSave.gold = 0;
            newSave.difficulty = 1;
            newSave.permadeath_enabled = true;
            newSave.casual_mode = false;
            newSave.is_mid_battle = false;
            newSave.timestamp = time(nullptr);
            saveManager->save(newSave, slotNumber, true);
            std::cout << "Created new save in slot " << slotNumber << std::endl;
        }
        
        // Get starting scene from game_flow.json
        if (gameFlow.contains("game_start") && gameFlow["game_start"].contains("new_game_scene")) {
            currentSceneId = gameFlow["game_start"]["new_game_scene"];
            LoadScene(currentSceneId);
        } else {
            std::cerr << "ERROR: No starting scene defined in game_flow.json!" << std::endl;
            currentState = STATE_TITLE;
        }
    }
    
    void LoadScene(const std::string& sceneId) {
        std::cout << "Loading scene: " << sceneId << std::endl;
        
        // Special case: return to title
        if (sceneId == "return_to_title") {
            EndScene();
            return;
        }
        
        // Load scene JSON file
        std::string scenePath = "data/scenes/" + sceneId + ".json";
        json sceneData;
        
        try {
            std::ifstream sceneFile(scenePath);
            if (!sceneFile.is_open()) {
                std::cerr << "ERROR: Scene file not found: " << scenePath << std::endl;
                currentState = STATE_TITLE;
                return;
            }
            sceneFile >> sceneData;
            sceneFile.close();
        } catch (const std::exception& e) {
            std::cerr << "ERROR: Failed to load scene: " << e.what() << std::endl;
            currentState = STATE_TITLE;
            return;
        }
        
        // Transition to scene
        currentState = STATE_SCENE;
        sceneManager->StartTransition(SceneManager::TransitionType::FADE_FROM_BLACK, 1.0f);
        
        // Set background from scene data
        if (sceneData.contains("background")) {
            std::string bgPath = "assets/" + sceneData["background"].get<std::string>();
            sceneManager->SetBackground(bgPath);
        }
        
        // Load scene music
        if (sceneData.contains("music")) {
            LoadSceneMusic(sceneData["music"]);
        }
        
        // Prepare dialogue
        if (sceneData.contains("dialogue")) {
            PrepareDialogueFromJSON(sceneData["dialogue"]);
        }
        
        // Store next scene ID
        if (sceneData.contains("next_scene")) {
            currentSceneId = sceneData["next_scene"];
        } else {
            currentSceneId = "return_to_title";
        }
    }
    
    void LoadSceneMusic(const std::string& musicFile) {
        if (!audioInitialized) {
            return;
        }
        
        // Stop current music if playing
        if (bgm) {
            Mix_FreeMusic(bgm);
            bgm = nullptr;
        }
        
        // Load scene music
        std::string musicPath = "assets/" + musicFile;
        
        bgm = Mix_LoadMUS(musicPath.c_str());
        if (!bgm) {
            std::cerr << "Failed to load scene music: " << Mix_GetError() << std::endl;
        } else {
            std::cout << "Scene music loaded: " << musicPath << std::endl;
            Mix_PlayMusic(bgm, -1);
            Mix_VolumeMusic(MIX_MAX_VOLUME / 2);
        }
    }
    
    void PrepareDialogueFromJSON(const json& dialogueArray) {
        std::vector<DialogueSystem::DialogueLine> dialogueLines;
        
        for (const auto& line : dialogueArray) {
            DialogueSystem::DialogueLine dialogueLine;
            dialogueLine.speakerName = line.value("speaker", "");
            dialogueLine.text = line.value("text", "");
            dialogueLine.portraitPath = line.value("portrait", "");
            
            // TODO: Handle save_prompt flag
            
            dialogueLines.push_back(dialogueLine);
        }
        
        dialogueSystem->LoadDialogue(dialogueLines);
        std::cout << "Loaded " << dialogueLines.size() << " dialogue lines from scene data" << std::endl;
    }
    
    void StartDialogue() {
        dialogueSystem->Start();
        std::cout << "Started dialogue sequence" << std::endl;
    }
    
    void EndScene() {
        // Scene complete - check if there's a next scene or return to title
        std::cout << "Scene complete" << std::endl;
        
        dialogueSystem->Stop();
        sceneManager->ClearBackground();
        
        // Load next scene or return to title
        if (!currentSceneId.empty() && currentSceneId != "return_to_title") {
            LoadScene(currentSceneId);
        } else {
            std::cout << "Returning to title screen" << std::endl;
            currentState = STATE_TITLE;
            // Restart title music
            LoadTitleMusic();
        }
    }
    
    void Run() {
        bool running = true;
        SDL_Event event;
        Uint32 lastTime = SDL_GetTicks();
        
        while (running && currentState != STATE_QUIT) {
            // Calculate delta time
            Uint32 currentTime = SDL_GetTicks();
            float deltaTime = (currentTime - lastTime) / 1000.0f;
            lastTime = currentTime;
            
            // Handle events
            while (SDL_PollEvent(&event)) {
                if (event.type == SDL_QUIT) {
                    running = false;
                } else if (event.type == SDL_KEYDOWN) {
                    HandleInput(event.key.keysym.sym);
                }
            }
            
            // Update
            Update(deltaTime);
            
            // Render
            SDL_SetRenderDrawColor(renderer, 0, 0, 0, 255);
            SDL_RenderClear(renderer);
            Render();
            SDL_RenderPresent(renderer);
        }
    }
    
    void HandleInput(SDL_Keycode key) {
        switch (currentState) {
            case STATE_SPLASH:
                // Splash screen auto-transitions, no input needed
                break;
                
            case STATE_TITLE:
                if (key == SDLK_UP) {
                    selectedMenuItem = (selectedMenuItem - 1 + 3) % 3;
                } else if (key == SDLK_DOWN) {
                    selectedMenuItem = (selectedMenuItem + 1) % 3;
                } else if (key == SDLK_RETURN || key == SDLK_SPACE) {
                    if (selectedMenuItem == 0) {
                        // New Game - go to save slot selection
                        saveScreenMode = SaveSlotScreen::Mode::NEW_GAME;
                        saveSlotScreen->SetMode(saveScreenMode);
                        saveSlotScreen->Reset();
                        currentState = STATE_SAVE_SELECT;
                    } else if (selectedMenuItem == 1) {
                        // Load Game - go to save slot selection
                        saveScreenMode = SaveSlotScreen::Mode::LOAD_GAME;
                        saveSlotScreen->SetMode(saveScreenMode);
                        saveSlotScreen->Reset();
                        currentState = STATE_SAVE_SELECT;
                    } else if (selectedMenuItem == 2) {
                        currentState = STATE_QUIT;
                    }
                }
                break;
                
            case STATE_SAVE_SELECT:
                saveSlotScreen->HandleInput(key);
                
                // Check if user selected a slot
                if (saveSlotScreen->HasSelectedSlot()) {
                    currentSaveSlot = saveSlotScreen->GetSelectedSlot();
                    std::cout << "Selected save slot: " << currentSaveSlot << std::endl;
                    
                    // Transition to scene/gameplay
                    StartGameFromSlot(currentSaveSlot);
                }
                
                // Check if user wants to return to title
                if (saveSlotScreen->ShouldReturnToTitle()) {
                    currentState = STATE_TITLE;
                }
                break;
                
            case STATE_SCENE:
                // Scene automatically transitions to dialogue
                break;
                
            case STATE_DIALOGUE:
                dialogueSystem->HandleInput(key);
                
                // Auto-save at the save prompt (line 5 in our dialogue)
                // TODO: Make this more robust with proper dialogue IDs
                
                // Check if dialogue is complete
                if (dialogueSystem->IsComplete()) {
                    EndScene();
                }
                break;
                
            case STATE_EASTER_EGG:
                // Any key returns to title
                currentState = STATE_TITLE;
                break;
                
            default:
                break;
        }
    }
    
    void Update(float deltaTime) {
        if (currentState == STATE_SPLASH) {
            splashTimer += deltaTime;
            if (splashTimer >= 3.5f) {  // Total duration: 3.5 seconds (fade in + stay + fade out)
                currentState = STATE_TITLE;
                // Start title music when entering title screen
                LoadTitleMusic();
            }
        } else if (currentState == STATE_SCENE) {
            sceneManager->Update(deltaTime);
            
            // Check if transition is complete, then start dialogue
            if (sceneManager->IsTransitionComplete() && !dialogueSystem->IsActive()) {
                currentState = STATE_DIALOGUE;
                StartDialogue();
            }
        } else if (currentState == STATE_DIALOGUE) {
            dialogueSystem->Update(deltaTime);
        }
    }
    
    void Render() {
        switch (currentState) {
            case STATE_SPLASH:
                RenderSplash();
                break;
            case STATE_TITLE:
                RenderTitle();
                break;
            case STATE_SAVE_SELECT:
                saveSlotScreen->Render();
                break;
            case STATE_SCENE:
                sceneManager->RenderBackground();
                sceneManager->RenderTransition();
                break;
            case STATE_DIALOGUE:
                sceneManager->RenderBackground();
                dialogueSystem->Render();
                break;
            case STATE_EASTER_EGG:
                RenderEasterEgg();
                break;
            default:
                break;
        }
    }
    
    void RenderSplash() {
        // Dark blue background
        SDL_SetRenderDrawColor(renderer, 20, 20, 40, 255);
        SDL_RenderClear(renderer);
        
        // Calculate alpha based on timer
        // Fade in: 0.0 to 1.0 seconds (0 to 255)
        // Stay: 1.0 to 2.5 seconds (255)
        // Fade out: 2.5 to 3.5 seconds (255 to 0)
        int alpha = 255;
        if (splashTimer < 1.0f) {
            // Fade in
            alpha = (int)(splashTimer * 255.0f);
        } else if (splashTimer > 2.5f) {
            // Fade out
            float fadeOutProgress = (splashTimer - 2.5f) / 1.0f;  // 0.0 to 1.0
            alpha = (int)(255.0f * (1.0f - fadeOutProgress));
        }
        
        // Render "Lehran Engine" text with fade
        RenderText("LEHRAN ENGINE", SCREEN_WIDTH / 2, 250, fontLarge, {200, 200, 255, (Uint8)alpha});
    }
    
    void RenderTitle() {
        // Gradient background (simplified)
        for (int y = 0; y < SCREEN_HEIGHT; y++) {
            int colorValue = 20 + (y * 40 / SCREEN_HEIGHT);
            SDL_SetRenderDrawColor(renderer, colorValue, colorValue, colorValue + 20, 255);
            SDL_RenderDrawLine(renderer, 0, y, SCREEN_WIDTH, y);
        }
        
        // Game title
        RenderText(gameName.c_str(), SCREEN_WIDTH / 2, 150, fontLarge, {255, 255, 255, 255});
        
        // Menu items
        const char* menuItems[] = {"New Game", "Load Game", "Exit"};
        for (int i = 0; i < 3; i++) {
            SDL_Color color = (i == selectedMenuItem) ? SDL_Color{255, 255, 100, 255} : SDL_Color{200, 200, 200, 255};
            
            // Draw arrow for selected item
            if (i == selectedMenuItem) {
                RenderText(">", SCREEN_WIDTH / 2 - 100, 300 + i * 60, fontMedium, {255, 255, 100, 255});
            }
            
            RenderText(menuItems[i], SCREEN_WIDTH / 2, 300 + i * 60, fontMedium, color);
        }
        
        // Version info
        std::string version = "v" + gameData.value("version", "0.0") + " | Engine v0.1";
        RenderText(version.c_str(), SCREEN_WIDTH - 10, SCREEN_HEIGHT - 10, fontSmall, {100, 100, 100, 255}, true);
    }
    
    void RenderEasterEgg() {
        // Dark red background
        SDL_SetRenderDrawColor(renderer, 30, 10, 10, 255);
        SDL_RenderClear(renderer);
        
        // Multi-line message
        RenderText("...", SCREEN_WIDTH / 2, 200, fontLarge, {255, 200, 200, 255});
        RenderText("But there is no game to play.", SCREEN_WIDTH / 2, 260, fontMedium, {200, 200, 200, 255});
        RenderText("Seriously, did you even try?", SCREEN_WIDTH / 2, 320, fontMedium, {200, 200, 200, 255});
        RenderText("Press any key to return...", SCREEN_WIDTH / 2, 500, fontSmall, {150, 150, 150, 255});
    }
    
    void RenderText(const char* text, int x, int y, TTF_Font* font, SDL_Color color, bool alignRight = false) {
        if (!font || !text) return;
        
        SDL_Surface* surface = TTF_RenderText_Blended(font, text, color);
        if (!surface) return;
        
        SDL_Texture* texture = SDL_CreateTextureFromSurface(renderer, surface);
        if (!texture) {
            SDL_FreeSurface(surface);
            return;
        }
        
        // Set texture alpha if color has alpha component
        if (color.a < 255) {
            SDL_SetTextureAlphaMod(texture, color.a);
        }
        
        SDL_Rect destRect;
        destRect.w = surface->w;
        destRect.h = surface->h;
        
        if (alignRight) {
            destRect.x = x - surface->w;
            destRect.y = y - surface->h;
        } else {
            destRect.x = x - surface->w / 2;
            destRect.y = y - surface->h / 2;
        }
        
        SDL_RenderCopy(renderer, texture, nullptr, &destRect);
        
        SDL_DestroyTexture(texture);
        SDL_FreeSurface(surface);
    }
    
    void RenderText(const std::string& text, int x, int y, TTF_Font* font, SDL_Color color, bool alignRight = false) {
        RenderText(text.c_str(), x, y, font, color, alignRight);
    }
    
    void Cleanup() {
        // Clean up modular systems
        delete dialogueSystem;
        delete sceneManager;
        delete saveSlotScreen;
        delete textureManager;
        delete saveManager;
        
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
