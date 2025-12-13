#pragma once

#include <SDL.h>
#include <SDL_ttf.h>
#include "SaveManager.hpp"
#include <string>
#include <vector>

class SaveSlotScreen {
public:
    enum class Mode {
        NEW_GAME,   // Selecting slot for new game
        LOAD_GAME,  // Selecting slot to load
        COPY_DATA,  // Selecting slot to copy from
        DELETE_DATA // Selecting slot to delete
    };
    
    struct SlotInfo {
        int slotNumber;
        bool hasData;
        std::string characterName;
        int chapter;
        std::string timestamp;
        int playtime; // in seconds
    };
    
private:
    SDL_Renderer* renderer;
    TTF_Font* fontLarge;
    TTF_Font* fontMedium;
    TTF_Font* fontSmall;
    Lehran::SaveManager* saveManager;
    
    Mode currentMode;
    int selectedSlot;
    std::vector<SlotInfo> slots;
    bool shouldReturn; // Return to title screen
    int selectedSlotToStart; // The slot chosen to begin/load
    
    // Confirmation dialog state
    bool showingConfirmation;
    int confirmationChoice;  // 0 = Yes, 1 = No
    int slotToModify;  // The slot being copied/deleted
    int targetSlot;  // For copy operation, the destination slot
    
    void LoadSlotInfo();
    void RenderText(const std::string& text, int x, int y, TTF_Font* font, SDL_Color color, bool centered = true);
    std::string FormatPlaytime(int seconds);
    
public:
    SaveSlotScreen(SDL_Renderer* renderer, TTF_Font* fontLarge, TTF_Font* fontMedium, 
                   TTF_Font* fontSmall, Lehran::SaveManager* saveManager);
    
    void SetMode(Mode mode);
    void HandleInput(SDL_Keycode key);
    void Render();
    
    // Check if user wants to return to title
    bool ShouldReturnToTitle() const { return shouldReturn; }
    
    // Check if user selected a slot to start/load
    bool HasSelectedSlot() const { return selectedSlotToStart != -1; }
    int GetSelectedSlot() const { return selectedSlotToStart; }
    
    // Reset state when entering screen
    void Reset();
};
