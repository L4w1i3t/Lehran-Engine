#pragma once

#include <SDL.h>
#include <SDL_ttf.h>
#include <string>
#include "json.hpp"
#include "ConfigManager.hpp"

// Forward declarations
class SaveSlotScreen;

using json = nlohmann::json;

namespace Lehran {

class RenderManager {
public:
    RenderManager(SDL_Renderer* renderer, TTF_Font* fontLarge, TTF_Font* fontMedium, TTF_Font* fontSmall);
    ~RenderManager();

    // Main rendering functions
    void RenderSplash(float splashTimer);
    void RenderTitle(const std::string& gameName, int selectedMenuItem, const json& gameData);
    void RenderEasterEgg();
    void RenderSettings(const ConfigManager& config, int selectedSettingsItem, int settingsScrollOffset);

    // Helper for external systems to render text
    void RenderText(const char* text, int x, int y, TTF_Font* font, SDL_Color color, bool alignRight = false);
    void RenderText(const std::string& text, int x, int y, TTF_Font* font, SDL_Color color, bool alignRight = false);

    // Screen dimensions (for external use)
    static const int SCREEN_WIDTH = 1920;
    static const int SCREEN_HEIGHT = 1080;

private:
    SDL_Renderer* renderer;
    TTF_Font* fontLarge;
    TTF_Font* fontMedium;
    TTF_Font* fontSmall;

    // Helper methods
    void RenderGradientBackground();
};

} // namespace Lehran
