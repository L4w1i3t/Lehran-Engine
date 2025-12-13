#pragma once

#include <SDL.h>
#include <functional>

// Forward declarations
class SaveSlotScreen;

namespace Lehran {

enum class GameState {
    STATE_SPLASH,
    STATE_TITLE,
    STATE_SAVE_SELECT,
    STATE_SETTINGS,
    STATE_SCENE,
    STATE_DIALOGUE,
    STATE_MAP,
    STATE_EASTER_EGG,
    STATE_QUIT
};

class InputHandler {
public:
    // Callback types
    using StateChangeCallback = std::function<void(GameState)>;
    using MenuActionCallback = std::function<void(int)>; // Takes menu item index
    using SettingsActionCallback = std::function<void(int, bool)>; // Item index, isLeftKey
    using ScrollCallback = std::function<void(int)>; // Scroll delta
    using WindowModeCallback = std::function<void()>;
    using MapCursorMoveCallback = std::function<void(int, int)>; // dx, dy in tiles

    InputHandler();
    ~InputHandler();

    // Main input processing
    void HandleKeyDown(SDL_Keycode key, GameState currentState);
    void HandleMouseWheel(int wheelY, GameState currentState);

    // Set callbacks
    void SetStateChangeCallback(StateChangeCallback callback) { onStateChange = callback; }
    void SetTitleMenuCallback(MenuActionCallback callback) { onTitleMenuAction = callback; }
    void SetSettingsActionCallback(SettingsActionCallback callback) { onSettingsAction = callback; }
    void SetScrollCallback(ScrollCallback callback) { onScroll = callback; }
    void SetWindowModeCallback(WindowModeCallback callback) { onWindowModeChange = callback; }
    void SetMapCursorMoveCallback(MapCursorMoveCallback callback) { onMapCursorMove = callback; }
    void SetMapSelectCallback(std::function<void()> callback) { onMapSelectAction = callback; }
    void SetMapCancelCallback(std::function<bool()> callback) { onMapCancelAction = callback; }
    void SetMapActionMenuCallback(std::function<int(int)> callback) { onMapActionMenuAction = callback; }
    void SetMapInventoryCallback(std::function<int(int)> callback) { onMapInventoryAction = callback; }
    void SetMapToggleUnitInfoCallback(std::function<void()> callback) { onMapToggleUnitInfo = callback; }

    // Set external systems for input forwarding
    void SetSaveSlotScreen(SaveSlotScreen* screen) { saveSlotScreen = screen; }
    void SetDialogueSystemHandleInput(std::function<void(SDL_Keycode)> handler) { 
        dialogueInputHandler = handler; 
    }
    void SetDialogueCompleteCheck(std::function<bool()> checker) { 
        dialogueCompleteChecker = checker; 
    }
    void SetSaveSlotSelectedCheck(std::function<bool()> checker) { 
        saveSlotSelectedChecker = checker; 
    }
    void SetSaveSlotReturnCheck(std::function<bool()> checker) { 
        saveSlotReturnChecker = checker; 
    }
    void SetGetSelectedSlot(std::function<int()> getter) { 
        getSelectedSlot = getter; 
    }
    void SetGetSaveScreenMode(std::function<int()> getter) { 
        getSaveScreenMode = getter; 
    }
    void SetGetSelectedSettingsItem(std::function<int()> getter) {
        getSelectedSettingsItem = getter;
    }
    void SetGetSelectedMenuItem(std::function<int()> getter) {
        getSelectedMenuItem = getter;
    }

private:
    // Callbacks
    StateChangeCallback onStateChange;
    MenuActionCallback onTitleMenuAction;
    SettingsActionCallback onSettingsAction;
    ScrollCallback onScroll;
    WindowModeCallback onWindowModeChange;
    MapCursorMoveCallback onMapCursorMove;
    std::function<void()> onMapSelectAction;
    std::function<bool()> onMapCancelAction;  // Returns true if something was cancelled
    std::function<int(int)> onMapActionMenuAction;  // Query/navigate action menu
    std::function<int(int)> onMapInventoryAction;   // Query/navigate inventory
    std::function<void()> onMapToggleUnitInfo;      // Toggle unit info panel

    // External systems
    SaveSlotScreen* saveSlotScreen;
    std::function<void(SDL_Keycode)> dialogueInputHandler;
    std::function<bool()> dialogueCompleteChecker;
    std::function<bool()> saveSlotSelectedChecker;
    std::function<bool()> saveSlotReturnChecker;
    std::function<int()> getSelectedSlot;
    std::function<int()> getSaveScreenMode;
    std::function<int()> getSelectedSettingsItem;
    std::function<int()> getSelectedMenuItem;

    // State-specific handlers
    void HandleSplashInput(SDL_Keycode key);
    void HandleTitleInput(SDL_Keycode key);
    void HandleSettingsInput(SDL_Keycode key);
    void HandleSaveSelectInput(SDL_Keycode key);
    void HandleSceneInput(SDL_Keycode key);
    void HandleDialogueInput(SDL_Keycode key);
    void HandleMapInput(SDL_Keycode key);
    void HandleEasterEggInput(SDL_Keycode key);
};

} // namespace Lehran
