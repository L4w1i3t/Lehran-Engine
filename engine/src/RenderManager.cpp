#include "RenderManager.hpp"
#include <iostream>
#include <cstdio>

namespace Lehran {

RenderManager::RenderManager(SDL_Renderer* renderer, TTF_Font* fontLarge, 
                             TTF_Font* fontMedium, TTF_Font* fontSmall)
    : renderer(renderer), fontLarge(fontLarge), fontMedium(fontMedium), fontSmall(fontSmall) {
}

RenderManager::~RenderManager() {
}

void RenderManager::RenderSplash(float splashTimer) {
    // Dark blue background
    SDL_SetRenderDrawColor(renderer, 20, 20, 40, 255);
    SDL_RenderClear(renderer);

    // Calculate alpha based on timer
    // Fade in: 0.0 to 1.0 seconds (0 to 255)
    // Stay: 1.0 to 2.5 seconds (255)
    // Fade out: 2.5 to 3.5 seconds (255 to 0)
    int alpha = 255;
    if (splashTimer < 1.0f) {
        // Fade in
        alpha = (int)(splashTimer * 255.0f);
    } else if (splashTimer > 2.5f) {
        // Fade out
        float fadeOutProgress = (splashTimer - 2.5f) / 1.0f;  // 0.0 to 1.0
        alpha = (int)(255.0f * (1.0f - fadeOutProgress));
    }

    // Render "Lehran Engine" text with fade
    RenderText("LEHRAN ENGINE", SCREEN_WIDTH / 2, 450, fontLarge, {200, 200, 255, (Uint8)alpha});
}

void RenderManager::RenderTitle(const std::string& gameName, int selectedMenuItem, const json& gameData) {
    // Gradient background
    RenderGradientBackground();

    // Game title
    RenderText(gameName.c_str(), SCREEN_WIDTH / 2, 270, fontLarge, {255, 255, 255, 255});

    // Menu items
    const char* menuItems[] = {"New Game", "Load Game", "Settings", "Map Test", "VN Test", "Exit"};
    for (int i = 0; i < 6; i++) {
        SDL_Color color = (i == selectedMenuItem) ? SDL_Color{255, 255, 100, 255} : SDL_Color{200, 200, 200, 255};

        // Draw arrow for selected item
        if (i == selectedMenuItem) {
            RenderText(">", SCREEN_WIDTH / 2 - 200, 540 + i * 90, fontMedium, {255, 255, 100, 255});
        }

        RenderText(menuItems[i], SCREEN_WIDTH / 2, 540 + i * 90, fontMedium, color);
    }

    // Version info
    std::string version = "v" + gameData.value("version", "0.0") + " | Engine v0.1";
    RenderText(version.c_str(), SCREEN_WIDTH - 10, SCREEN_HEIGHT - 10, fontSmall, {100, 100, 100, 255}, true);
}

void RenderManager::RenderEasterEgg() {
    // Dark red background
    SDL_SetRenderDrawColor(renderer, 30, 10, 10, 255);
    SDL_RenderClear(renderer);

    // Multi-line message
    RenderText("...", SCREEN_WIDTH / 2, 360, fontLarge, {255, 200, 200, 255});
    RenderText("But there is no game to play.", SCREEN_WIDTH / 2, 468, fontMedium, {200, 200, 200, 255});
    RenderText("Seriously, did you even try?", SCREEN_WIDTH / 2, 576, fontMedium, {200, 200, 200, 255});
    RenderText("Press any key to return...", SCREEN_WIDTH / 2, 900, fontSmall, {150, 150, 150, 255});
}

void RenderManager::RenderSettings(const ConfigManager& config, int selectedSettingsItem, int settingsScrollOffset) {
    // Gradient background
    RenderGradientBackground();

    // Title
    RenderText("Settings", SCREEN_WIDTH / 2, 200, fontLarge, {255, 255, 255, 255});

    // Resolution options
    const char* resolutions[] = {"1280x720 (720p)", "1600x900", "1920x1080 (1080p)"};
    const char* windowModes[] = {"Windowed", "Borderless", "Fullscreen"};

    // Menu items with values
    int yStart = 350 - settingsScrollOffset;
    int spacing = 100;

    // Calculate visible region
    int visibleTop = 280;
    int visibleBottom = SCREEN_HEIGHT - 150;

    // Recalculate yStart with scroll
    yStart = 350 - settingsScrollOffset;

    // Window Mode selection
    SDL_Color color0 = (selectedSettingsItem == 0) ? SDL_Color{255, 255, 100, 255} : SDL_Color{200, 200, 200, 255};
    if (selectedSettingsItem == 0) {
        RenderText(">", SCREEN_WIDTH / 2 - 400, yStart, fontMedium, {255, 255, 100, 255});
    }
    RenderText("Window Mode:", SCREEN_WIDTH / 2 - 200, yStart, fontMedium, color0);

    // Arrow indicators for window mode
    if (selectedSettingsItem == 0) {
        RenderText("<", SCREEN_WIDTH / 2 + 50, yStart, fontMedium, {255, 255, 100, 255});
        RenderText(">", SCREEN_WIDTH / 2 + 380, yStart, fontMedium, {255, 255, 100, 255});
    }
    RenderText(windowModes[static_cast<int>(config.GetWindowMode())], SCREEN_WIDTH / 2 + 215, yStart, fontMedium, color0);

    // Resolution selection
    SDL_Color color1 = (selectedSettingsItem == 1) ? SDL_Color{255, 255, 100, 255} : SDL_Color{200, 200, 200, 255};
    if (selectedSettingsItem == 1) {
        RenderText(">", SCREEN_WIDTH / 2 - 400, yStart + spacing, fontMedium, {255, 255, 100, 255});
    }
    RenderText("Resolution:", SCREEN_WIDTH / 2 - 200, yStart + spacing, fontMedium, color1);

    // Arrow indicators for resolution (only in windowed mode)
    if (selectedSettingsItem == 1 && config.GetWindowMode() == WindowMode::WINDOWED) {
        RenderText("<", SCREEN_WIDTH / 2 + 50, yStart + spacing, fontMedium, {255, 255, 100, 255});
        RenderText(">", SCREEN_WIDTH / 2 + 450, yStart + spacing, fontMedium, {255, 255, 100, 255});
    }

    // Show current resolution or note for fullscreen
    if (config.GetWindowMode() == WindowMode::WINDOWED) {
        RenderText(resolutions[config.GetResolutionIndex()], SCREEN_WIDTH / 2 + 250, yStart + spacing, fontMedium, color1);
    } else {
        RenderText("(Uses native resolution)", SCREEN_WIDTH / 2 + 250, yStart + spacing, fontSmall, {150, 150, 150, 255});
    }

    // Audio Settings Section
    int audioYStart = yStart + spacing * 2 + 20;

    // Master Volume
    SDL_Color color2 = (selectedSettingsItem == 2) ? SDL_Color{255, 255, 100, 255} : SDL_Color{200, 200, 200, 255};
    if (selectedSettingsItem == 2) {
        RenderText(">", SCREEN_WIDTH / 2 - 400, audioYStart, fontMedium, {255, 255, 100, 255});
        RenderText("<", SCREEN_WIDTH / 2 + 50, audioYStart, fontMedium, {255, 255, 100, 255});
        RenderText(">", SCREEN_WIDTH / 2 + 450, audioYStart, fontMedium, {255, 255, 100, 255});
    }
    RenderText("Master Volume:", SCREEN_WIDTH / 2 - 200, audioYStart, fontMedium, color2);
    char volumeText[16];
    snprintf(volumeText, sizeof(volumeText), "%d%%", config.GetMasterVolume());
    RenderText(volumeText, SCREEN_WIDTH / 2 + 250, audioYStart, fontMedium, color2);

    // Music Volume
    SDL_Color color3 = (selectedSettingsItem == 3) ? SDL_Color{255, 255, 100, 255} : SDL_Color{200, 200, 200, 255};
    if (selectedSettingsItem == 3) {
        RenderText(">", SCREEN_WIDTH / 2 - 400, audioYStart + spacing, fontMedium, {255, 255, 100, 255});
        RenderText("<", SCREEN_WIDTH / 2 + 50, audioYStart + spacing, fontMedium, {255, 255, 100, 255});
        RenderText(">", SCREEN_WIDTH / 2 + 450, audioYStart + spacing, fontMedium, {255, 255, 100, 255});
    }
    RenderText("Music Volume:", SCREEN_WIDTH / 2 - 200, audioYStart + spacing, fontMedium, color3);
    snprintf(volumeText, sizeof(volumeText), "%d%%", config.GetMusicVolume());
    RenderText(volumeText, SCREEN_WIDTH / 2 + 250, audioYStart + spacing, fontMedium, color3);

    // SFX Volume
    SDL_Color color4 = (selectedSettingsItem == 4) ? SDL_Color{255, 255, 100, 255} : SDL_Color{200, 200, 200, 255};
    if (selectedSettingsItem == 4) {
        RenderText(">", SCREEN_WIDTH / 2 - 400, audioYStart + spacing * 2, fontMedium, {255, 255, 100, 255});
        RenderText("<", SCREEN_WIDTH / 2 + 50, audioYStart + spacing * 2, fontMedium, {255, 255, 100, 255});
        RenderText(">", SCREEN_WIDTH / 2 + 450, audioYStart + spacing * 2, fontMedium, {255, 255, 100, 255});
    }
    RenderText("SFX Volume:", SCREEN_WIDTH / 2 - 200, audioYStart + spacing * 2, fontMedium, color4);
    snprintf(volumeText, sizeof(volumeText), "%d%%", config.GetSFXVolume());
    RenderText(volumeText, SCREEN_WIDTH / 2 + 250, audioYStart + spacing * 2, fontMedium, color4);

    // Voice Volume
    SDL_Color color5 = (selectedSettingsItem == 5) ? SDL_Color{255, 255, 100, 255} : SDL_Color{200, 200, 200, 255};
    if (selectedSettingsItem == 5) {
        RenderText(">", SCREEN_WIDTH / 2 - 400, audioYStart + spacing * 3, fontMedium, {255, 255, 100, 255});
        RenderText("<", SCREEN_WIDTH / 2 + 50, audioYStart + spacing * 3, fontMedium, {255, 255, 100, 255});
        RenderText(">", SCREEN_WIDTH / 2 + 450, audioYStart + spacing * 3, fontMedium, {255, 255, 100, 255});
    }
    RenderText("Voice Volume:", SCREEN_WIDTH / 2 - 200, audioYStart + spacing * 3, fontMedium, color5);
    snprintf(volumeText, sizeof(volumeText), "%d%%", config.GetVoiceVolume());
    RenderText(volumeText, SCREEN_WIDTH / 2 + 250, audioYStart + spacing * 3, fontMedium, color5);

    // Data Management Section
    int dataYStart = audioYStart + spacing * 4 + 50;

    // Copy Data
    SDL_Color color6 = (selectedSettingsItem == 6) ? SDL_Color{255, 255, 100, 255} : SDL_Color{200, 200, 200, 255};
    if (selectedSettingsItem == 6) {
        RenderText(">", SCREEN_WIDTH / 2 - 400, dataYStart, fontMedium, {255, 255, 100, 255});
    }
    RenderText("Copy Data", SCREEN_WIDTH / 2, dataYStart, fontMedium, color6);

    // Delete Data
    SDL_Color color7 = (selectedSettingsItem == 7) ? SDL_Color{255, 255, 100, 255} : SDL_Color{200, 200, 200, 255};
    if (selectedSettingsItem == 7) {
        RenderText(">", SCREEN_WIDTH / 2 - 400, dataYStart + spacing, fontMedium, {255, 255, 100, 255});
    }
    RenderText("Delete Data", SCREEN_WIDTH / 2, dataYStart + spacing, fontMedium, color7);

    // Back button
    SDL_Color color8 = (selectedSettingsItem == 8) ? SDL_Color{255, 255, 100, 255} : SDL_Color{200, 200, 200, 255};
    if (selectedSettingsItem == 8) {
        RenderText(">", SCREEN_WIDTH / 2 - 400, dataYStart + spacing * 2 + 50, fontMedium, {255, 255, 100, 255});
    }
    RenderText("Back to Title", SCREEN_WIDTH / 2, dataYStart + spacing * 2 + 50, fontMedium, color8);

    // Draw scrollbar on the right side
    int scrollbarX = SCREEN_WIDTH - 60;
    int scrollbarY = 280;
    int scrollbarHeight = SCREEN_HEIGHT - 400;
    int scrollbarWidth = 12;

    // Scrollbar track (background)
    SDL_Rect scrollbarTrack = {scrollbarX, scrollbarY, scrollbarWidth, scrollbarHeight};
    SDL_SetRenderDrawColor(renderer, 50, 50, 50, 255);
    SDL_RenderFillRect(renderer, &scrollbarTrack);

    // Scrollbar thumb (indicator)
    int maxScroll = 600;
    float scrollRatio = (float)settingsScrollOffset / (float)maxScroll;
    int thumbHeight = 80;
    int thumbY = scrollbarY + (int)((scrollbarHeight - thumbHeight) * scrollRatio);

    SDL_Rect scrollbarThumb = {scrollbarX + 2, thumbY, scrollbarWidth - 4, thumbHeight};
    SDL_SetRenderDrawColor(renderer, 150, 150, 150, 255);
    SDL_RenderFillRect(renderer, &scrollbarThumb);

    // Instructions
    RenderText("Use Arrow Keys to navigate | Enter to select | ESC to go back", 
               SCREEN_WIDTH / 2, SCREEN_HEIGHT - 80, fontSmall, {150, 150, 150, 255});

    // Current window info
    const char* modeStr = (config.GetWindowMode() == WindowMode::WINDOWED) ? "Windowed" :
                          (config.GetWindowMode() == WindowMode::BORDERLESS) ? "Borderless" : "Fullscreen";
    char windowInfo[128];
    if (config.GetWindowMode() == WindowMode::WINDOWED) {
        snprintf(windowInfo, sizeof(windowInfo), "Current: %dx%d (%s)", 
                 config.GetWindowWidth(), config.GetWindowHeight(), modeStr);
    } else {
        snprintf(windowInfo, sizeof(windowInfo), "Current: %dx%d (%s)", 
                 config.GetNativeDisplayWidth(), config.GetNativeDisplayHeight(), modeStr);
    }
    RenderText(windowInfo, SCREEN_WIDTH / 2, SCREEN_HEIGHT - 40, fontSmall, {100, 100, 100, 255});
}

void RenderManager::RenderText(const char* text, int x, int y, TTF_Font* font, SDL_Color color, bool alignRight) {
    if (!font || !text) return;

    SDL_Surface* surface = TTF_RenderText_Blended(font, text, color);
    if (!surface) return;

    SDL_Texture* texture = SDL_CreateTextureFromSurface(renderer, surface);
    if (!texture) {
        SDL_FreeSurface(surface);
        return;
    }

    // Set texture alpha if color has alpha component
    if (color.a < 255) {
        SDL_SetTextureAlphaMod(texture, color.a);
    }

    SDL_Rect destRect;
    destRect.w = surface->w;
    destRect.h = surface->h;

    if (alignRight) {
        destRect.x = x - surface->w;
        destRect.y = y - surface->h;
    } else {
        destRect.x = x - surface->w / 2;
        destRect.y = y - surface->h / 2;
    }

    SDL_RenderCopy(renderer, texture, nullptr, &destRect);

    SDL_DestroyTexture(texture);
    SDL_FreeSurface(surface);
}

void RenderManager::RenderText(const std::string& text, int x, int y, TTF_Font* font, SDL_Color color, bool alignRight) {
    RenderText(text.c_str(), x, y, font, color, alignRight);
}

void RenderManager::RenderGradientBackground() {
    // Gradient background (simplified)
    for (int y = 0; y < SCREEN_HEIGHT; y++) {
        int colorValue = 20 + (y * 40 / SCREEN_HEIGHT);
        SDL_SetRenderDrawColor(renderer, colorValue, colorValue, colorValue + 20, 255);
        SDL_RenderDrawLine(renderer, 0, y, SCREEN_WIDTH, y);
    }
}

} // namespace Lehran
