#include "InputHandler.hpp"
#include "SaveSlotScreen.hpp"
#include <iostream>

namespace Lehran {

InputHandler::InputHandler()
    : saveSlotScreen(nullptr) {
}

InputHandler::~InputHandler() {
}

void InputHandler::HandleKeyDown(SDL_Keycode key, GameState currentState) {
    // Global hotkeys
    if (key == SDLK_RETURN && (SDL_GetModState() & KMOD_ALT)) {
        if (onWindowModeChange) {
            onWindowModeChange();
        }
        return;
    }

    switch (currentState) {
        case GameState::STATE_SPLASH:
            HandleSplashInput(key);
            break;
        case GameState::STATE_TITLE:
            HandleTitleInput(key);
            break;
        case GameState::STATE_SETTINGS:
            HandleSettingsInput(key);
            break;
        case GameState::STATE_SAVE_SELECT:
            HandleSaveSelectInput(key);
            break;
        case GameState::STATE_SCENE:
            HandleSceneInput(key);
            break;
        case GameState::STATE_DIALOGUE:
            HandleDialogueInput(key);
            break;
        case GameState::STATE_MAP:
            HandleMapInput(key);
            break;
        case GameState::STATE_EASTER_EGG:
            HandleEasterEggInput(key);
            break;
        default:
            break;
    }
}

void InputHandler::HandleMouseWheel(int wheelY, GameState currentState) {
    if (currentState == GameState::STATE_SETTINGS && onScroll) {
        onScroll(wheelY);
    }
}

void InputHandler::HandleSplashInput(SDL_Keycode key) {
    // Splash screen auto-transitions, no input needed
}

void InputHandler::HandleTitleInput(SDL_Keycode key) {
    int selectedMenuItem = getSelectedMenuItem ? getSelectedMenuItem() : 0;

    if (key == SDLK_UP) {
        selectedMenuItem = (selectedMenuItem - 1 + 6) % 6;
        if (onTitleMenuAction) onTitleMenuAction(selectedMenuItem);
    } else if (key == SDLK_DOWN) {
        selectedMenuItem = (selectedMenuItem + 1) % 6;
        if (onTitleMenuAction) onTitleMenuAction(selectedMenuItem);
    } else if (key == SDLK_RETURN || key == SDLK_SPACE) {
        if (onTitleMenuAction) {
            // Signal selection with negative index
            onTitleMenuAction(-(selectedMenuItem + 1));
        }
    }
}

void InputHandler::HandleSettingsInput(SDL_Keycode key) {
    int selectedSettingsItem = getSelectedSettingsItem ? getSelectedSettingsItem() : 0;

    if (key == SDLK_UP) {
        selectedSettingsItem = (selectedSettingsItem - 1 + 9) % 9;
        // Only update selection, don't trigger adjustment
        if (onSettingsAction) onSettingsAction(selectedSettingsItem, false);
    } else if (key == SDLK_DOWN) {
        selectedSettingsItem = (selectedSettingsItem + 1) % 9;
        // Only update selection, don't trigger adjustment
        if (onSettingsAction) onSettingsAction(selectedSettingsItem, false);
    } else if (key == SDLK_ESCAPE) {
        if (onStateChange) onStateChange(GameState::STATE_TITLE);
    } else if (key == SDLK_RETURN || key == SDLK_SPACE) {
        if (onSettingsAction) {
            // Signal selection with special value
            onSettingsAction(-(selectedSettingsItem + 100), false);
        }
    } else if (key == SDLK_LEFT) {
        // Signal adjustment with negative value to distinguish from navigation
        if (onSettingsAction) onSettingsAction(-(selectedSettingsItem + 200), true);
    } else if (key == SDLK_RIGHT) {
        // Signal adjustment with negative value to distinguish from navigation
        if (onSettingsAction) onSettingsAction(-(selectedSettingsItem + 200), false);
    }
}

void InputHandler::HandleSaveSelectInput(SDL_Keycode key) {
    if (saveSlotScreen) {
        saveSlotScreen->HandleInput(key);

        // Check if user selected a slot
        if (saveSlotSelectedChecker && saveSlotSelectedChecker()) {
            if (getSelectedSlot && getSaveScreenMode) {
                int selectedSlot = getSelectedSlot();
                int mode = getSaveScreenMode();
                std::cout << "Selected save slot: " << selectedSlot << std::endl;

                // Only transition to game if in NEW_GAME or LOAD_GAME mode (0 or 1)
                if (mode == 0 || mode == 1) {
                    // Signal to start game via callback
                    if (onTitleMenuAction) {
                        onTitleMenuAction(-1000 - selectedSlot); // Special signal for game start
                    }
                }
            }
        }

        // Check if user wants to return
        if (saveSlotReturnChecker && saveSlotReturnChecker()) {
            if (getSaveScreenMode) {
                int mode = getSaveScreenMode();
                // Return to settings if we came from copy/delete (2 or 3), otherwise title
                if (mode == 2 || mode == 3) {
                    if (onStateChange) onStateChange(GameState::STATE_SETTINGS);
                } else {
                    if (onStateChange) onStateChange(GameState::STATE_TITLE);
                }
            }
        }
    }
}

void InputHandler::HandleSceneInput(SDL_Keycode key) {
    // Scene automatically transitions to dialogue
}

void InputHandler::HandleDialogueInput(SDL_Keycode key) {
    if (dialogueInputHandler) {
        dialogueInputHandler(key);
    }

    // Check if dialogue is complete
    if (dialogueCompleteChecker && dialogueCompleteChecker()) {
        // Signal dialogue end via state change callback
        if (onStateChange) {
            onStateChange(GameState::STATE_SCENE); // Will be handled by main loop
        }
    }
}

void InputHandler::HandleMapInput(SDL_Keycode key) {
    if (onMapInventoryAction) {
        // Check if we're in inventory menu mode
        int inventoryState = onMapInventoryAction(-2000); // Query inventory state
        if (inventoryState == 1) {
            // Inventory is showing - handle menu navigation
            if (key == SDLK_UP || key == SDLK_w) {
                onMapInventoryAction(-1); // Move up
            } else if (key == SDLK_DOWN || key == SDLK_s) {
                onMapInventoryAction(1); // Move down
            } else if (key == SDLK_RETURN || key == SDLK_SPACE || key == SDLK_z) {
                onMapInventoryAction(100); // Equip/drop item
            } else if (key == SDLK_ESCAPE || key == SDLK_x) {
                onMapInventoryAction(-100); // Close inventory
            }
            return;
        }
    }
    
    if (onMapActionMenuAction) {
        // Check if we're in action menu mode
        int menuState = onMapActionMenuAction(-1000); // Query menu state
        if (menuState == 1) {
            // Action menu is showing - handle menu navigation
            if (key == SDLK_UP || key == SDLK_w) {
                onMapActionMenuAction(-1); // Move up
            } else if (key == SDLK_DOWN || key == SDLK_s) {
                onMapActionMenuAction(1); // Move down
            } else if (key == SDLK_RETURN || key == SDLK_SPACE || key == SDLK_z) {
                onMapActionMenuAction(100); // Confirm action
            } else if (key == SDLK_ESCAPE || key == SDLK_x) {
                onMapActionMenuAction(-100); // Cancel (back to unit selected state)
            }
            return;
        }
    }
    
    // Normal map controls
    if (key == SDLK_LEFT || key == SDLK_a) {
        if (onMapCursorMove) onMapCursorMove(-1, 0);
    } else if (key == SDLK_RIGHT || key == SDLK_d) {
        if (onMapCursorMove) onMapCursorMove(1, 0);
    } else if (key == SDLK_UP || key == SDLK_w) {
        if (onMapCursorMove) onMapCursorMove(0, -1);
    } else if (key == SDLK_DOWN || key == SDLK_s) {
        if (onMapCursorMove) onMapCursorMove(0, 1);
    } else if (key == SDLK_TAB) {
        // Toggle unit info panel
        if (onMapToggleUnitInfo) onMapToggleUnitInfo();
    } else if (key == SDLK_RETURN || key == SDLK_SPACE || key == SDLK_z) {
        // Select unit or confirm movement
        if (onMapSelectAction) onMapSelectAction();
    } else if (key == SDLK_x) {
        // Cancel selection (X only cancels, doesn't return to title)
        if (onMapCancelAction) {
            onMapCancelAction();
        }
    } else if (key == SDLK_ESCAPE) {
        // Cancel selection or return to title (ESC can exit to title)
        if (onMapCancelAction) {
            if (!onMapCancelAction()) {
                // If cancel returns false, no unit selected - return to title
                if (onStateChange) {
                    onStateChange(GameState::STATE_TITLE);
                }
            }
        }
    }
}

void InputHandler::HandleEasterEggInput(SDL_Keycode key) {
    // Any key returns to title
    if (onStateChange) {
        onStateChange(GameState::STATE_TITLE);
    }
}

} // namespace Lehran
