#include "DialogueSystem.hpp"
#include <iostream>
#include <sstream>

DialogueSystem::DialogueSystem(SDL_Renderer* renderer, TTF_Font* fontMedium,
                               TTF_Font* fontSmall, TextureManager* textureManager)
    : renderer(renderer), fontMedium(fontMedium), fontSmall(fontSmall),
      textureManager(textureManager), currentLineIndex(0), isActive(false),
      waitingForInput(true), textRevealTimer(0.0f), revealedChars(0),
      instantText(true), selectedChoice(0), showingChoices(false) {
}

void DialogueSystem::LoadDialogue(const std::vector<DialogueLine>& lines) {
    dialogueLines = lines;
    currentLineIndex = 0;
    showingChoices = false;
    std::cout << "Loaded " << dialogueLines.size() << " dialogue lines" << std::endl;
}

void DialogueSystem::Start() {
    isActive = true;
    currentLineIndex = 0;
    revealedChars = 0;
    textRevealTimer = 0.0f;
    waitingForInput = true;
    
    if (!dialogueLines.empty()) {
        displayedText = dialogueLines[0].text;
    }
    
    std::cout << "Dialogue started" << std::endl;
}

void DialogueSystem::Stop() {
    isActive = false;
    currentLineIndex = 0;
    showingChoices = false;
    std::cout << "Dialogue stopped" << std::endl;
}

void DialogueSystem::Update(float deltaTime) {
    if (!isActive || dialogueLines.empty()) return;
    
    // Text scrolling effect (if enabled)
    if (!instantText && revealedChars < displayedText.length()) {
        textRevealTimer += deltaTime;
        if (textRevealTimer >= 0.03f) { // Reveal one char every 0.03 seconds
            revealedChars++;
            textRevealTimer = 0.0f;
        }
    }
}

void DialogueSystem::HandleInput(SDL_Keycode key) {
    if (!isActive) return;
    
    if (showingChoices) {
        // Handle choice selection
        if (key == SDLK_UP) {
            selectedChoice = (selectedChoice - 1 + (int)currentChoices.size()) % (int)currentChoices.size();
        } else if (key == SDLK_DOWN) {
            selectedChoice = (selectedChoice + 1) % (int)currentChoices.size();
        } else if (key == SDLK_RETURN || key == SDLK_SPACE) {
            showingChoices = false;
            std::cout << "Selected choice: " << selectedChoice << std::endl;
        }
    } else {
        // Advance dialogue
        if (key == SDLK_RETURN || key == SDLK_SPACE || key == SDLK_z) {
            NextLine();
        }
    }
}

void DialogueSystem::NextLine() {
    currentLineIndex++;
    
    if (currentLineIndex < (int)dialogueLines.size()) {
        displayedText = dialogueLines[currentLineIndex].text;
        revealedChars = 0;
        textRevealTimer = 0.0f;
    } else {
        std::cout << "Dialogue complete" << std::endl;
    }
}

void DialogueSystem::Render() {
    if (!isActive || dialogueLines.empty() || currentLineIndex >= (int)dialogueLines.size()) {
        return;
    }
    
    const DialogueLine& currentLine = dialogueLines[currentLineIndex];
    
    // Render sprites (left and right)
    if (!currentLine.spriteLeft.empty()) {
        SDL_Texture* spriteLeft = textureManager->LoadTexture(currentLine.spriteLeft);
        if (spriteLeft) {
            // Get actual sprite dimensions
            int spriteWidth, spriteHeight;
            SDL_QueryTexture(spriteLeft, nullptr, nullptr, &spriteWidth, &spriteHeight);
            // Position on left side - bottom aligned
            SDL_Rect dstRect = {180, 1080 - spriteHeight, spriteWidth, spriteHeight};
            SDL_RendererFlip flip = currentLine.flipSpriteLeft ? SDL_FLIP_HORIZONTAL : SDL_FLIP_NONE;
            SDL_RenderCopyEx(renderer, spriteLeft, nullptr, &dstRect, 0.0, nullptr, flip);
        }
    }
    
    if (!currentLine.spriteRight.empty()) {
        SDL_Texture* spriteRight = textureManager->LoadTexture(currentLine.spriteRight);
        if (spriteRight) {
            // Get actual sprite dimensions
            int spriteWidth, spriteHeight;
            SDL_QueryTexture(spriteRight, nullptr, nullptr, &spriteWidth, &spriteHeight);
            // Position on right side - bottom aligned
            SDL_Rect dstRect = {1920 - 180 - spriteWidth, 1080 - spriteHeight, spriteWidth, spriteHeight};
            SDL_RendererFlip flip = currentLine.flipSpriteRight ? SDL_FLIP_HORIZONTAL : SDL_FLIP_NONE;
            SDL_RenderCopyEx(renderer, spriteRight, nullptr, &dstRect, 0.0, nullptr, flip);
        }
    }
    
    // Render dialogue box background
    SDL_Rect dialogueBox = {90, DIALOGUE_BOX_Y, 1740, DIALOGUE_BOX_HEIGHT};
    SDL_SetRenderDrawColor(renderer, 20, 20, 40, 230);
    SDL_RenderFillRect(renderer, &dialogueBox);
    
    // Dialogue box border
    SDL_SetRenderDrawColor(renderer, 150, 150, 180, 255);
    SDL_RenderDrawRect(renderer, &dialogueBox);
    
    // Render portrait (if available)
    if (!currentLine.portraitPath.empty()) {
        SDL_Texture* portrait = textureManager->LoadTexture(currentLine.portraitPath);
        if (portrait) {
            textureManager->RenderTexture(portrait, 108, DIALOGUE_BOX_Y + 27, PORTRAIT_SIZE, PORTRAIT_SIZE);
        }
    }
    
    // Render speaker name
    if (!currentLine.speakerName.empty()) {
        int nameX = currentLine.portraitPath.empty() ? 126 : 342;
        RenderText(currentLine.speakerName, nameX, DIALOGUE_BOX_Y + 36, fontMedium, 
                   {255, 255, 100, 255}, false);
    }
    
    // Render dialogue text (wrapped)
    int textX = currentLine.portraitPath.empty() ? 126 : 342;
    int textY = DIALOGUE_BOX_Y + (currentLine.speakerName.empty() ? 54 : 99);
    int maxWidth = 1400;
    
    std::vector<std::string> wrappedLines = WrapText(currentLine.text, fontSmall, maxWidth);
    for (size_t i = 0; i < wrappedLines.size(); i++) {
        RenderText(wrappedLines[i], textX, textY + (int)i * 45, fontSmall, 
                   {255, 255, 255, 255}, false);
    }
    
    // Render "Press Enter to continue" prompt
    if (!showingChoices && currentLineIndex < (int)dialogueLines.size() - 1) {
        RenderText("V", 960, DIALOGUE_BOX_Y + DIALOGUE_BOX_HEIGHT - 36, fontSmall, 
                   {200, 200, 200, 255}, true);
    }
    
    // Render choices (if showing)
    if (showingChoices) {
        int choiceY = DIALOGUE_BOX_Y - 108 * (int)currentChoices.size() - 36;
        
        for (size_t i = 0; i < currentChoices.size(); i++) {
            SDL_Rect choiceBox = {660, choiceY + (int)i * 108, 600, 90};
            
            if ((int)i == selectedChoice) {
                SDL_SetRenderDrawColor(renderer, 80, 80, 120, 230);
            } else {
                SDL_SetRenderDrawColor(renderer, 40, 40, 60, 230);
            }
            SDL_RenderFillRect(renderer, &choiceBox);
            
            SDL_SetRenderDrawColor(renderer, 150, 150, 180, 255);
            SDL_RenderDrawRect(renderer, &choiceBox);
            
            SDL_Color textColor = ((int)i == selectedChoice) ? 
                SDL_Color{255, 255, 100, 255} : SDL_Color{200, 200, 200, 255};
            
            RenderText(currentChoices[i].text, 960, choiceY + (int)i * 108 + 45, 
                       fontSmall, textColor, true);
        }
    }
}

void DialogueSystem::ShowChoices(const std::vector<Choice>& choices) {
    currentChoices = choices;
    selectedChoice = 0;
    showingChoices = true;
    std::cout << "Showing " << choices.size() << " choices" << std::endl;
}

bool DialogueSystem::HasSelectedChoice() const {
    return !showingChoices && !currentChoices.empty();
}

void DialogueSystem::RenderText(const std::string& text, int x, int y, TTF_Font* font,
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
        destRect.y = y;
    }
    
    SDL_RenderCopy(renderer, texture, nullptr, &destRect);
    
    SDL_DestroyTexture(texture);
    SDL_FreeSurface(surface);
}

std::vector<std::string> DialogueSystem::WrapText(const std::string& text, TTF_Font* font, int maxWidth) {
    std::vector<std::string> lines;
    std::istringstream words(text);
    std::string word;
    std::string currentLine;
    
    while (words >> word) {
        std::string testLine = currentLine.empty() ? word : currentLine + " " + word;
        
        int textWidth, textHeight;
        TTF_SizeText(font, testLine.c_str(), &textWidth, &textHeight);
        
        if (textWidth > maxWidth && !currentLine.empty()) {
            lines.push_back(currentLine);
            currentLine = word;
        } else {
            currentLine = testLine;
        }
    }
    
    if (!currentLine.empty()) {
        lines.push_back(currentLine);
    }
    
    return lines;
}
