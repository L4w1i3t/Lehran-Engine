#pragma once

#include <string>
#include <functional>
#include "json.hpp"
#include "InputHandler.hpp"

using json = nlohmann::json;

// Forward declarations
class SceneManager;
class DialogueSystem;
class SaveSlotScreen;

namespace Lehran {

class SaveManager;

class GameStateManager {
public:
    GameStateManager();
    ~GameStateManager();

    // State management
    GameState GetCurrentState() const { return currentState; }
    void SetCurrentState(GameState state) { currentState = state; }
    
    // Menu state
    int GetSelectedMenuItem() const { return selectedMenuItem; }
    void SetSelectedMenuItem(int index) { selectedMenuItem = index; }
    int GetSelectedSettingsItem() const { return selectedSettingsItem; }
    void SetSelectedSettingsItem(int index) { selectedSettingsItem = index; }
    int GetSettingsScrollOffset() const { return settingsScrollOffset; }
    void SetSettingsScrollOffset(int offset) { settingsScrollOffset = offset; }
    void AdjustSettingsScrollOffset(int delta);

    // Save screen state
    int GetSaveScreenMode() const { return static_cast<int>(saveScreenMode); }
    void SetSaveScreenMode(int mode);
    int GetCurrentSaveSlot() const { return currentSaveSlot; }
    void SetCurrentSaveSlot(int slot) { currentSaveSlot = slot; }

    // Splash timer
    float GetSplashTimer() const { return splashTimer; }
    void UpdateSplashTimer(float deltaTime);
    bool ShouldTransitionFromSplash() const { return splashTimer >= 3.5f; }

    // Scene management
    void StartGameFromSlot(int slotNumber, SaveManager* saveManager, const json& gameFlow);
    void LoadScene(const std::string& sceneId, SceneManager* sceneManager, DialogueSystem* dialogueSystem);
    void EndScene(SceneManager* sceneManager, DialogueSystem* dialogueSystem);
    const std::string& GetCurrentSceneId() const { return currentSceneId; }

    // Callbacks for loading music
    void SetLoadTitleMusicCallback(std::function<void()> callback) { onLoadTitleMusic = callback; }
    void SetLoadSceneMusicCallback(std::function<void(const std::string&)> callback) { onLoadSceneMusic = callback; }
    void SetStartDialogueCallback(std::function<void()> callback) { onStartDialogue = callback; }

private:
    GameState currentState;
    int selectedMenuItem;
    int selectedSettingsItem;
    int settingsScrollOffset;
    float splashTimer;
    
    // Save screen state
    enum class SaveScreenMode {
        NEW_GAME = 0,
        LOAD_GAME = 1,
        COPY_DATA = 2,
        DELETE_DATA = 3
    };
    SaveScreenMode saveScreenMode;
    int currentSaveSlot;
    
    // Scene management
    std::string currentSceneId;
    
    // Callbacks
    std::function<void()> onLoadTitleMusic;
    std::function<void(const std::string&)> onLoadSceneMusic;
    std::function<void()> onStartDialogue;

    // Helper methods
    void PrepareDialogueFromJSON(const json& dialogueArray, DialogueSystem* dialogueSystem);
};

} // namespace Lehran
