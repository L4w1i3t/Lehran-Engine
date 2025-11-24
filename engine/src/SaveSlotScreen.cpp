#include "SaveSlotScreen.hpp"
#include <sstream>
#include <iomanip>

SaveSlotScreen::SaveSlotScreen(SDL_Renderer* renderer, TTF_Font* fontLarge, 
                               TTF_Font* fontMedium, TTF_Font* fontSmall,
                               Lehran::SaveManager* saveManager)
    : renderer(renderer), fontLarge(fontLarge), fontMedium(fontMedium),
      fontSmall(fontSmall), saveManager(saveManager),
      currentMode(Mode::NEW_GAME), selectedSlot(0), 
      shouldReturn(false), selectedSlotToStart(-1) {
    slots.resize(5);
    LoadSlotInfo();
}

void SaveSlotScreen::SetMode(Mode mode) {
    currentMode = mode;
    LoadSlotInfo();
}

void SaveSlotScreen::Reset() {
    selectedSlot = 0;
    shouldReturn = false;
    selectedSlotToStart = -1;
    LoadSlotInfo();
}

void SaveSlotScreen::LoadSlotInfo() {
    for (int i = 0; i < 5; i++) {
        slots[i].slotNumber = i;
        slots[i].hasData = false;
        
        Lehran::SaveData data;
        if (saveManager->load(i, data) && !data.slot_name.empty()) {
            slots[i].hasData = true;
            slots[i].characterName = data.slot_name;
            slots[i].chapter = data.current_chapter;
            // Format timestamp from time_t
            char timeStr[64];
            strftime(timeStr, sizeof(timeStr), "%Y-%m-%d %H:%M", localtime(&data.timestamp));
            slots[i].timestamp = timeStr;
            slots[i].playtime = data.turn_count; // Using turn_count as a proxy for playtime for now
        } else {
            slots[i].characterName = "Empty";
            slots[i].chapter = 0;
            slots[i].timestamp = "";
            slots[i].playtime = 0;
        }
    }
}

void SaveSlotScreen::HandleInput(SDL_Keycode key) {
    if (key == SDLK_UP) {
        selectedSlot = (selectedSlot - 1 + 5) % 5;
    } else if (key == SDLK_DOWN) {
        selectedSlot = (selectedSlot + 1) % 5;
    } else if (key == SDLK_RETURN || key == SDLK_SPACE) {
        // If loading, only allow selecting slots with data
        if (currentMode == Mode::LOAD_GAME && !slots[selectedSlot].hasData) {
            return; // Can't load empty slot
        }
        selectedSlotToStart = selectedSlot;
    } else if (key == SDLK_ESCAPE) {
        shouldReturn = true;
    }
}

void SaveSlotScreen::Render() {
    // Dark blue gradient background
    for (int y = 0; y < 600; y++) {
        int colorValue = 10 + (y * 30 / 600);
        SDL_SetRenderDrawColor(renderer, colorValue, colorValue, colorValue + 10, 255);
        SDL_RenderDrawLine(renderer, 0, y, 800, y);
    }
    
    // Title
    const char* title = (currentMode == Mode::NEW_GAME) ? "Select Save Slot" : "Load Game";
    RenderText(title, 400, 80, fontLarge, {255, 255, 255, 255});
    
    // Render each slot
    for (int i = 0; i < 5; i++) {
        int yPos = 180 + i * 80;
        bool isSelected = (i == selectedSlot);
        
        // Slot background
        SDL_Rect slotRect = {100, yPos - 30, 600, 70};
        if (isSelected) {
            SDL_SetRenderDrawColor(renderer, 80, 80, 120, 255);
        } else {
            SDL_SetRenderDrawColor(renderer, 40, 40, 60, 255);
        }
        SDL_RenderFillRect(renderer, &slotRect);
        
        // Slot border
        SDL_SetRenderDrawColor(renderer, 150, 150, 180, 255);
        SDL_RenderDrawRect(renderer, &slotRect);
        
        // Selection arrow
        if (isSelected) {
            RenderText(">", 80, yPos, fontMedium, {255, 255, 100, 255});
        }
        
        // Slot number
        std::string slotLabel = "Slot " + std::to_string(i + 1);
        RenderText(slotLabel, 140, yPos - 10, fontMedium, {200, 200, 255, 255}, false);
        
        if (slots[i].hasData) {
            // Character name
            RenderText(slots[i].characterName, 140, yPos + 15, fontSmall, {255, 255, 255, 255}, false);
            
            // Chapter
            std::string chapterText = "Chapter " + std::to_string(slots[i].chapter);
            RenderText(chapterText, 400, yPos, fontSmall, {200, 200, 200, 255}, false);
            
            // Playtime
            std::string playtimeText = FormatPlaytime(slots[i].playtime);
            RenderText(playtimeText, 600, yPos, fontSmall, {200, 200, 200, 255}, false);
        } else {
            // Empty slot
            SDL_Color emptyColor = (currentMode == Mode::LOAD_GAME) 
                ? SDL_Color{100, 100, 100, 255} // Grayed out for load mode
                : SDL_Color{150, 150, 150, 255};
            RenderText("- Empty -", 400, yPos, fontMedium, emptyColor);
        }
    }
    
    // Instructions
    std::string instructions = "Arrow Keys: Select | Enter: Confirm | Escape: Back";
    RenderText(instructions, 400, 560, fontSmall, {150, 150, 150, 255});
}

void SaveSlotScreen::RenderText(const std::string& text, int x, int y, TTF_Font* font, 
                                SDL_Color color, bool centered) {
    if (!font || text.empty()) return;
    
    SDL_Surface* surface = TTF_RenderText_Blended(font, text.c_str(), color);
    if (!surface) return;
    
    SDL_Texture* texture = SDL_CreateTextureFromSurface(renderer, surface);
    if (!texture) {
        SDL_FreeSurface(surface);
        return;
    }
    
    SDL_Rect destRect;
    destRect.w = surface->w;
    destRect.h = surface->h;
    
    if (centered) {
        destRect.x = x - surface->w / 2;
        destRect.y = y - surface->h / 2;
    } else {
        destRect.x = x;
        destRect.y = y - surface->h / 2;
    }
    
    SDL_RenderCopy(renderer, texture, nullptr, &destRect);
    
    SDL_DestroyTexture(texture);
    SDL_FreeSurface(surface);
}

std::string SaveSlotScreen::FormatPlaytime(int seconds) {
    int hours = seconds / 3600;
    int minutes = (seconds % 3600) / 60;
    
    std::ostringstream oss;
    oss << std::setfill('0') << std::setw(2) << hours << ":" 
        << std::setfill('0') << std::setw(2) << minutes;
    return oss.str();
}
