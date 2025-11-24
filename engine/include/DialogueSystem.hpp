#pragma once

#include <SDL.h>
#include <SDL_ttf.h>
#include "TextureManager.hpp"
#include <string>
#include <vector>

class DialogueSystem {
public:
    struct DialogueLine {
        std::string speakerName;
        std::string text;
        std::string portraitPath; // Optional portrait image
    };
    
    struct Choice {
        std::string text;
        int nextDialogueId; // For branching dialogue
    };
    
private:
    SDL_Renderer* renderer;
    TTF_Font* fontMedium;
    TTF_Font* fontSmall;
    TextureManager* textureManager;
    
    std::vector<DialogueLine> dialogueLines;
    int currentLineIndex;
    bool isActive;
    bool waitingForInput;
    
    // For text scrolling effect (optional)
    std::string displayedText;
    float textRevealTimer;
    size_t revealedChars;
    bool instantText; // If true, show all text immediately
    
    // For choices
    std::vector<Choice> currentChoices;
    int selectedChoice;
    bool showingChoices;
    
    // UI constants
    static const int DIALOGUE_BOX_HEIGHT = 150;
    static const int DIALOGUE_BOX_Y = 450;
    static const int PORTRAIT_SIZE = 120;
    
    void RenderText(const std::string& text, int x, int y, TTF_Font* font, SDL_Color color, bool centered = false);
    std::vector<std::string> WrapText(const std::string& text, TTF_Font* font, int maxWidth);
    
public:
    DialogueSystem(SDL_Renderer* renderer, TTF_Font* fontMedium, 
                   TTF_Font* fontSmall, TextureManager* textureManager);
    
    // Load dialogue from a vector
    void LoadDialogue(const std::vector<DialogueLine>& lines);
    
    // Control
    void Start();
    void Stop();
    void Update(float deltaTime);
    void HandleInput(SDL_Keycode key);
    
    // Render dialogue box
    void Render();
    
    // State checks
    bool IsActive() const { return isActive; }
    bool IsComplete() const { return currentLineIndex >= (int)dialogueLines.size(); }
    
    // Choice handling
    void ShowChoices(const std::vector<Choice>& choices);
    bool HasSelectedChoice() const;
    int GetSelectedChoice() const { return selectedChoice; }
    
    // Advance to next line
    void NextLine();
};
