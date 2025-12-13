#include "SaveSlotScreen.hpp"
#include <sstream>
#include <iomanip>
#include <iostream>

SaveSlotScreen::SaveSlotScreen(SDL_Renderer* renderer, TTF_Font* fontLarge, 
                               TTF_Font* fontMedium, TTF_Font* fontSmall,
                               Lehran::SaveManager* saveManager)
    : renderer(renderer), fontLarge(fontLarge), fontMedium(fontMedium),
      fontSmall(fontSmall), saveManager(saveManager),
      currentMode(Mode::NEW_GAME), selectedSlot(0), 
      shouldReturn(false), selectedSlotToStart(-1),
      showingConfirmation(false), confirmationChoice(1),
      slotToModify(-1), targetSlot(-1) {
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
    showingConfirmation = false;
    confirmationChoice = 1;
    slotToModify = -1;
    targetSlot = -1;
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
    // Handle confirmation dialog input
    if (showingConfirmation) {
        if (key == SDLK_LEFT || key == SDLK_RIGHT) {
            confirmationChoice = 1 - confirmationChoice;  // Toggle Yes/No
        } else if (key == SDLK_RETURN || key == SDLK_SPACE) {
            if (confirmationChoice == 0) {  // Yes
                if (currentMode == Mode::COPY_DATA) {
                    // Copy from slotToModify to targetSlot
                    Lehran::SaveData data;
                    if (saveManager->load(slotToModify, data)) {
                        saveManager->save(data, targetSlot);
                        std::cout << "Copied slot " << slotToModify << " to slot " << targetSlot << std::endl;
                        LoadSlotInfo();  // Refresh slot display
                    }
                } else if (currentMode == Mode::DELETE_DATA) {
                    // Delete slotToModify
                    saveManager->delete_slot(slotToModify);
                    std::cout << "Deleted slot " << slotToModify << std::endl;
                    LoadSlotInfo();  // Refresh slot display
                }
            }
            // Close confirmation and reset
            showingConfirmation = false;
            confirmationChoice = 1;
            slotToModify = -1;
            targetSlot = -1;
        } else if (key == SDLK_ESCAPE) {
            showingConfirmation = false;
            confirmationChoice = 1;
            slotToModify = -1;
            targetSlot = -1;
        }
        return;  // Don't process other input while showing confirmation
    }
    
    // Normal slot selection input
    if (key == SDLK_UP) {
        selectedSlot = (selectedSlot - 1 + 5) % 5;
    } else if (key == SDLK_DOWN) {
        selectedSlot = (selectedSlot + 1) % 5;
    } else if (key == SDLK_RETURN || key == SDLK_SPACE) {
        if (currentMode == Mode::LOAD_GAME) {
            // Only allow selecting slots with data
            if (!slots[selectedSlot].hasData) {
                return; // Can't load empty slot
            }
            selectedSlotToStart = selectedSlot;
        } else if (currentMode == Mode::NEW_GAME) {
            selectedSlotToStart = selectedSlot;
        } else if (currentMode == Mode::DELETE_DATA) {
            // Only allow deleting slots with data
            if (!slots[selectedSlot].hasData) {
                return; // Can't delete empty slot
            }
            slotToModify = selectedSlot;
            showingConfirmation = true;
            confirmationChoice = 1;  // Default to No
        } else if (currentMode == Mode::COPY_DATA) {
            // First selection: source slot
            if (slotToModify == -1) {
                // Only allow copying FROM slots with data
                if (!slots[selectedSlot].hasData) {
                    return; // Can't copy from empty slot
                }
                slotToModify = selectedSlot;
                std::cout << "Selected slot " << slotToModify << " to copy from. Select destination..." << std::endl;
            } else {
                // Second selection: destination slot (can be any slot, including empty)
                targetSlot = selectedSlot;
                showingConfirmation = true;
                confirmationChoice = 1;  // Default to No
            }
        }
    } else if (key == SDLK_ESCAPE) {
        // If in copy mode and already selected source, cancel source selection
        if (currentMode == Mode::COPY_DATA && slotToModify != -1 && targetSlot == -1) {
            slotToModify = -1;
        } else {
            shouldReturn = true;
        }
    }
}

void SaveSlotScreen::Render() {
    // Dark blue gradient background
    for (int y = 0; y < 1080; y++) {
        int colorValue = 10 + (y * 30 / 1080);
        SDL_SetRenderDrawColor(renderer, colorValue, colorValue, colorValue + 10, 255);
        SDL_RenderDrawLine(renderer, 0, y, 1920, y);
    }
    
    // Title based on mode
    const char* title = "Select Save Slot";
    if (currentMode == Mode::LOAD_GAME) title = "Load Game";
    else if (currentMode == Mode::COPY_DATA) {
        if (slotToModify == -1) {
            title = "Copy Data - Select Source Slot";
        } else {
            title = "Copy Data - Select Destination Slot";
        }
    }
    else if (currentMode == Mode::DELETE_DATA) title = "Delete Data - Select Slot";
    
    RenderText(title, 960, 144, fontLarge, {255, 255, 255, 255});
    
    // Render each slot
    for (int i = 0; i < 5; i++) {
        int yPos = 324 + i * 144;
        bool isSelected = (i == selectedSlot);
        bool isSourceSlot = (currentMode == Mode::COPY_DATA && i == slotToModify);
        
        // Slot background
        SDL_Rect slotRect = {240, yPos - 54, 1440, 126};
        if (isSourceSlot) {
            SDL_SetRenderDrawColor(renderer, 60, 120, 80, 255);  // Green tint for source
        } else if (isSelected) {
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
            RenderText(">", 192, yPos, fontMedium, {255, 255, 100, 255});
        }
        
        // Source indicator for copy mode
        if (isSourceSlot) {
            RenderText("[SOURCE]", 1600, yPos, fontSmall, {100, 255, 100, 255});
        }
        
        // Slot number
        std::string slotLabel = "Slot " + std::to_string(i + 1);
        RenderText(slotLabel, 140, yPos - 10, fontMedium, {200, 200, 255, 255}, false);
        
        if (slots[i].hasData) {
            // Character name
            RenderText(slots[i].characterName, 140, yPos + 15, fontSmall, {255, 255, 255, 255}, false);
            
            // Chapter
            std::string chapterText = (slots[i].chapter == 0) ? "Prologue" : "Chapter " + std::to_string(slots[i].chapter);
            RenderText(chapterText, 400, yPos, fontSmall, {200, 200, 200, 255}, false);
            
            // Playtime
            std::string playtimeText = FormatPlaytime(slots[i].playtime);
            RenderText(playtimeText, 1440, yPos, fontSmall, {200, 200, 200, 255}, false);
        } else {
            // Empty slot
            SDL_Color emptyColor;
            if (currentMode == Mode::LOAD_GAME || currentMode == Mode::DELETE_DATA || currentMode == Mode::COPY_DATA) {
                emptyColor = {100, 100, 100, 255}; // Grayed out
            } else {
                emptyColor = {150, 150, 150, 255};
            }
            RenderText("- Empty -", 400, yPos, fontMedium, emptyColor);
        }
    }
    
    // Instructions
    std::string instructions = "Arrow Keys: Select | Enter: Confirm | Escape: Back";
    RenderText(instructions, 960, 980, fontSmall, {150, 150, 150, 255});
    
    // Render confirmation dialog if active
    if (showingConfirmation) {
        // Dim background
        SDL_SetRenderDrawBlendMode(renderer, SDL_BLENDMODE_BLEND);
        SDL_SetRenderDrawColor(renderer, 0, 0, 0, 180);
        SDL_Rect dimRect = {0, 0, 1920, 1080};
        SDL_RenderFillRect(renderer, &dimRect);
        
        // Dialog box
        int dialogWidth = 800;
        int dialogHeight = 300;
        int dialogX = (1920 - dialogWidth) / 2;
        int dialogY = (1080 - dialogHeight) / 2;
        
        SDL_Rect dialogBorder = {dialogX - 4, dialogY - 4, dialogWidth + 8, dialogHeight + 8};
        SDL_SetRenderDrawColor(renderer, 100, 100, 100, 255);
        SDL_RenderFillRect(renderer, &dialogBorder);
        
        SDL_Rect dialogBox = {dialogX, dialogY, dialogWidth, dialogHeight};
        SDL_SetRenderDrawColor(renderer, 30, 30, 40, 255);
        SDL_RenderFillRect(renderer, &dialogBox);
        
        // Confirmation message
        std::string message;
        if (currentMode == Mode::COPY_DATA) {
            message = "Copy Slot " + std::to_string(slotToModify + 1) + " to Slot " + std::to_string(targetSlot + 1) + "?";
            if (slots[targetSlot].hasData) {
                RenderText("This will overwrite existing data!", 960, dialogY + 120, fontSmall, {255, 100, 100, 255});
            }
        } else if (currentMode == Mode::DELETE_DATA) {
            message = "Delete Slot " + std::to_string(slotToModify + 1) + "?";
            RenderText("This cannot be undone!", 960, dialogY + 120, fontSmall, {255, 100, 100, 255});
        }
        
        RenderText(message, 960, dialogY + 80, fontMedium, {255, 255, 255, 255});
        
        // Yes/No options
        int optionY = dialogY + 180;
        SDL_Color yesColor = (confirmationChoice == 0) ? SDL_Color{100, 255, 100, 255} : SDL_Color{150, 150, 150, 255};
        SDL_Color noColor = (confirmationChoice == 1) ? SDL_Color{255, 100, 100, 255} : SDL_Color{150, 150, 150, 255};
        
        if (confirmationChoice == 0) {
            RenderText(">", 740, optionY, fontMedium, {100, 255, 100, 255});
        }
        RenderText("Yes", 810, optionY, fontMedium, yesColor);
        
        if (confirmationChoice == 1) {
            RenderText(">", 1000, optionY, fontMedium, {255, 100, 100, 255});
        }
        RenderText("No", 1070, optionY, fontMedium, noColor);
        
        SDL_SetRenderDrawBlendMode(renderer, SDL_BLENDMODE_NONE);
    }
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
