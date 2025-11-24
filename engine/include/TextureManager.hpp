#pragma once

#include <SDL.h>
#include <SDL_image.h>
#include <string>
#include <unordered_map>
#include <memory>

class TextureManager {
private:
    SDL_Renderer* renderer;
    std::unordered_map<std::string, SDL_Texture*> textureCache;
    
public:
    explicit TextureManager(SDL_Renderer* renderer);
    ~TextureManager();
    
    // Load a texture from file (caches it for future use)
    SDL_Texture* LoadTexture(const std::string& filePath);
    
    // Render a texture at position with optional scaling
    void RenderTexture(SDL_Texture* texture, int x, int y, int width = -1, int height = -1);
    void RenderTexture(const std::string& filePath, int x, int y, int width = -1, int height = -1);
    
    // Clear a specific texture from cache
    void UnloadTexture(const std::string& filePath);
    
    // Clear all textures from cache
    void ClearCache();
    
    // Get texture dimensions
    bool GetTextureDimensions(SDL_Texture* texture, int& width, int& height);
};
