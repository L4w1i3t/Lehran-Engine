#pragma once

#include <SDL.h>
#include "TextureManager.hpp"
#include "json.hpp"
#include <string>

using json = nlohmann::json;

class SceneManager {
public:
    enum class TransitionType {
        NONE,
        FADE_TO_BLACK,
        FADE_FROM_BLACK
    };
    
private:
    SDL_Renderer* renderer;
    TextureManager* textureManager;
    
    std::string currentBackground;
    SDL_Texture* backgroundTexture;
    
    TransitionType currentTransition;
    float transitionProgress; // 0.0 to 1.0
    float transitionSpeed;     // Speed multiplier
    
    bool isTransitioning;
    
public:
    SceneManager(SDL_Renderer* renderer, TextureManager* textureManager);
    ~SceneManager();
    
    // Load a background image
    void SetBackground(const std::string& filePath);
    
    // Start a transition effect
    void StartTransition(TransitionType type, float speed = 1.0f);
    
    // Update transition state (call each frame)
    void Update(float deltaTime);
    
    // Render the current scene background
    void RenderBackground();
    
    // Render transition overlay (if active)
    void RenderTransition();
    
    // Check if transition is complete
    bool IsTransitionComplete() const;
    
    // Clear current background
    void ClearBackground();
};
