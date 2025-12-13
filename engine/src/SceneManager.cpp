#include "SceneManager.hpp"
#include <iostream>

SceneManager::SceneManager(SDL_Renderer* renderer, TextureManager* textureManager)
    : renderer(renderer), textureManager(textureManager),
      backgroundTexture(nullptr), currentTransition(TransitionType::NONE),
      transitionProgress(0.0f), transitionSpeed(1.0f), isTransitioning(false) {
}

SceneManager::~SceneManager() {
    // TextureManager handles cleanup of textures
}

void SceneManager::SetBackground(const std::string& filePath) {
    currentBackground = filePath;
    backgroundTexture = textureManager->LoadTexture(filePath);
    
    if (!backgroundTexture) {
        std::cerr << "Failed to set background: " << filePath << std::endl;
    } else {
        std::cout << "Scene background set to: " << filePath << std::endl;
    }
}

void SceneManager::StartTransition(TransitionType type, float speed) {
    currentTransition = type;
    transitionProgress = 0.0f;
    transitionSpeed = speed;
    isTransitioning = true;
    
    std::cout << "Started transition: " << (int)type << std::endl;
}

void SceneManager::Update(float deltaTime) {
    if (!isTransitioning) return;
    
    transitionProgress += deltaTime * transitionSpeed;
    
    if (transitionProgress >= 1.0f) {
        transitionProgress = 1.0f;
        isTransitioning = false;
        std::cout << "Transition complete" << std::endl;
    }
}

void SceneManager::RenderBackground() {
    if (backgroundTexture) {
        // Render background scaled to screen size (1920x1080)
        textureManager->RenderTexture(backgroundTexture, 0, 0, 1920, 1080);
    } else {
        // Default black background
        SDL_SetRenderDrawColor(renderer, 0, 0, 0, 255);
        SDL_RenderClear(renderer);
    }
}

void SceneManager::RenderTransition() {
    if (!isTransitioning && currentTransition == TransitionType::NONE) return;
    
    int alpha = 0;
    
    switch (currentTransition) {
        case TransitionType::FADE_TO_BLACK:
            // Alpha increases from 0 to 255
            alpha = (int)(transitionProgress * 255.0f);
            break;
            
        case TransitionType::FADE_FROM_BLACK:
            // Alpha decreases from 255 to 0
            alpha = (int)((1.0f - transitionProgress) * 255.0f);
            break;
            
        case TransitionType::NONE:
            return;
    }
    
    // Render black overlay with alpha
    SDL_SetRenderDrawBlendMode(renderer, SDL_BLENDMODE_BLEND);
    SDL_SetRenderDrawColor(renderer, 0, 0, 0, alpha);
    SDL_Rect fullScreen = {0, 0, 1920, 1080};
    SDL_RenderFillRect(renderer, &fullScreen);
}

bool SceneManager::IsTransitionComplete() const {
    return !isTransitioning;
}

void SceneManager::ClearBackground() {
    currentBackground.clear();
    backgroundTexture = nullptr;
}
