#include "TextureManager.hpp"
#include <iostream>

TextureManager::TextureManager(SDL_Renderer* renderer) 
    : renderer(renderer) {
}

TextureManager::~TextureManager() {
    ClearCache();
}

SDL_Texture* TextureManager::LoadTexture(const std::string& filePath) {
    // Check if already cached
    auto it = textureCache.find(filePath);
    if (it != textureCache.end()) {
        return it->second;
    }
    
    // Load image surface
    SDL_Surface* surface = IMG_Load(filePath.c_str());
    if (!surface) {
        std::cerr << "Failed to load image " << filePath << ": " << IMG_GetError() << std::endl;
        return nullptr;
    }
    
    // Create texture from surface
    SDL_Texture* texture = SDL_CreateTextureFromSurface(renderer, surface);
    SDL_FreeSurface(surface);
    
    if (!texture) {
        std::cerr << "Failed to create texture from " << filePath << ": " << SDL_GetError() << std::endl;
        return nullptr;
    }
    
    // Cache the texture
    textureCache[filePath] = texture;
    std::cout << "Loaded texture: " << filePath << std::endl;
    
    return texture;
}

void TextureManager::RenderTexture(SDL_Texture* texture, int x, int y, int width, int height) {
    if (!texture) return;
    
    SDL_Rect destRect;
    destRect.x = x;
    destRect.y = y;
    
    // If width/height not specified, use texture's natural dimensions
    if (width == -1 || height == -1) {
        SDL_QueryTexture(texture, nullptr, nullptr, &destRect.w, &destRect.h);
    } else {
        destRect.w = width;
        destRect.h = height;
    }
    
    SDL_RenderCopy(renderer, texture, nullptr, &destRect);
}

void TextureManager::RenderTexture(const std::string& filePath, int x, int y, int width, int height) {
    SDL_Texture* texture = LoadTexture(filePath);
    RenderTexture(texture, x, y, width, height);
}

void TextureManager::UnloadTexture(const std::string& filePath) {
    auto it = textureCache.find(filePath);
    if (it != textureCache.end()) {
        SDL_DestroyTexture(it->second);
        textureCache.erase(it);
        std::cout << "Unloaded texture: " << filePath << std::endl;
    }
}

void TextureManager::ClearCache() {
    for (auto& pair : textureCache) {
        SDL_DestroyTexture(pair.second);
    }
    textureCache.clear();
    std::cout << "Cleared texture cache" << std::endl;
}

bool TextureManager::GetTextureDimensions(SDL_Texture* texture, int& width, int& height) {
    if (!texture) return false;
    return SDL_QueryTexture(texture, nullptr, nullptr, &width, &height) == 0;
}
