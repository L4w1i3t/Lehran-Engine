#include "GameStateManager.hpp"
#include "SaveManager.hpp"
#include "SceneManager.hpp"
#include "DialogueSystem.hpp"
#include "SaveSlotScreen.hpp"
#include <fstream>
#include <iostream>
#include <ctime>

namespace Lehran {

GameStateManager::GameStateManager()
    : currentState(GameState::STATE_SPLASH), 
      selectedMenuItem(0),
      selectedSettingsItem(0),
      settingsScrollOffset(0),
      splashTimer(0.0f),
      saveScreenMode(SaveScreenMode::NEW_GAME),
      currentSaveSlot(-1) {
}

GameStateManager::~GameStateManager() {
}

void GameStateManager::SetSaveScreenMode(int mode) {
    if (mode >= 0 && mode <= 3) {
        saveScreenMode = static_cast<SaveScreenMode>(mode);
    }
}

void GameStateManager::AdjustSettingsScrollOffset(int delta) {
    if (delta > 0) {
        // Scroll up
        settingsScrollOffset -= 50;
        if (settingsScrollOffset < 0) settingsScrollOffset = 0;
    } else if (delta < 0) {
        // Scroll down
        settingsScrollOffset += 50;
        if (settingsScrollOffset > 600) settingsScrollOffset = 600;
    }
}

void GameStateManager::UpdateSplashTimer(float deltaTime) {
    splashTimer += deltaTime;
}

void GameStateManager::StartGameFromSlot(int slotNumber, SaveManager* saveManager, const json& gameFlow) {
    std::cout << "Starting game from slot " << slotNumber << std::endl;
    currentSaveSlot = slotNumber;

    // Load or create save data
    if (saveScreenMode == SaveScreenMode::LOAD_GAME) {
        SaveData data;
        if (saveManager->load(slotNumber, data)) {
            std::cout << "Loaded save: " << data.slot_name << ", Chapter " << data.current_chapter << std::endl;
            // TODO: Load actual game state from save data
        }
    } else {
        // New game - create initial save data
        SaveData newSave;
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
        saveManager->save(newSave, slotNumber, false); // Change this to 'true' to use JSON in debug builds. DISABLE THIS IN RELEASE BUILDS.
        std::cout << "Created new save in slot " << slotNumber << std::endl;
    }

    // Get starting scene from game_flow.json
    if (gameFlow.contains("game_start") && gameFlow["game_start"].contains("new_game_scene")) {
        currentSceneId = gameFlow["game_start"]["new_game_scene"];
        // Note: LoadScene will be called by the main engine after this returns
    } else {
        std::cerr << "ERROR: No starting scene defined in game_flow.json!" << std::endl;
        currentState = GameState::STATE_TITLE;
    }
}

void GameStateManager::LoadScene(const std::string& sceneId, SceneManager* sceneManager, 
                                  DialogueSystem* dialogueSystem) {
    std::cout << "Loading scene: " << sceneId << std::endl;

    // Special case: return to title
    if (sceneId == "return_to_title") {
        EndScene(sceneManager, dialogueSystem);
        return;
    }

    // Load scene JSON file
    std::string scenePath = "data/scenes/" + sceneId + ".json";
    json sceneData;

    try {
        std::ifstream sceneFile(scenePath);
        if (!sceneFile.is_open()) {
            std::cerr << "ERROR: Scene file not found: " << scenePath << std::endl;
            currentState = GameState::STATE_TITLE;
            return;
        }
        sceneFile >> sceneData;
        sceneFile.close();
    } catch (const std::exception& e) {
        std::cerr << "ERROR: Failed to load scene: " << e.what() << std::endl;
        currentState = GameState::STATE_TITLE;
        return;
    }

    // Transition to scene
    currentState = GameState::STATE_SCENE;
    sceneManager->StartTransition(SceneManager::TransitionType::FADE_FROM_BLACK, 1.0f);

    // Set background from scene data
    if (sceneData.contains("background")) {
        std::string bgPath = "assets/" + sceneData["background"].get<std::string>();
        sceneManager->SetBackground(bgPath);
    }

    // Load scene music
    if (sceneData.contains("music") && onLoadSceneMusic) {
        onLoadSceneMusic(sceneData["music"]);
    }

    // Prepare dialogue
    if (sceneData.contains("dialogue")) {
        PrepareDialogueFromJSON(sceneData["dialogue"], dialogueSystem);
    }

    // Store next scene ID
    if (sceneData.contains("next_scene")) {
        currentSceneId = sceneData["next_scene"];
    } else {
        currentSceneId = "return_to_title";
    }
}

void GameStateManager::EndScene(SceneManager* sceneManager, DialogueSystem* dialogueSystem) {
    // Scene complete - check if there's a next scene or return to title
    std::cout << "Scene complete" << std::endl;

    dialogueSystem->Stop();
    sceneManager->ClearBackground();

    // Load next scene or return to title
    if (!currentSceneId.empty() && currentSceneId != "return_to_title") {
        LoadScene(currentSceneId, sceneManager, dialogueSystem);
    } else {
        std::cout << "Returning to title screen" << std::endl;
        currentState = GameState::STATE_TITLE;
        // Restart title music
        if (onLoadTitleMusic) {
            onLoadTitleMusic();
        }
    }
}

void GameStateManager::PrepareDialogueFromJSON(const json& dialogueArray, DialogueSystem* dialogueSystem) {
    std::vector<DialogueSystem::DialogueLine> dialogueLines;

    for (const auto& line : dialogueArray) {
        DialogueSystem::DialogueLine dialogueLine;
        dialogueLine.speakerName = line.value("speaker", "");
        dialogueLine.text = line.value("text", "");
        dialogueLine.portraitPath = line.value("portrait", "");
        dialogueLine.spriteLeft = line.value("sprite_left", "");
        dialogueLine.spriteRight = line.value("sprite_right", "");
        dialogueLine.flipSpriteLeft = line.value("flip_sprite_left", false);
        dialogueLine.flipSpriteRight = line.value("flip_sprite_right", false);

        // TODO: Handle save_prompt flag

        dialogueLines.push_back(dialogueLine);
    }

    dialogueSystem->LoadDialogue(dialogueLines);
    std::cout << "Loaded " << dialogueLines.size() << " dialogue lines from scene data" << std::endl;
    
    // Dialogue will be started by the Update loop after transition completes
}

} // namespace Lehran
