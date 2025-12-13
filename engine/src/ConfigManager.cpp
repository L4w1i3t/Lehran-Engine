#include "ConfigManager.hpp"
#include <fstream>
#include <iostream>
#include <algorithm>

namespace Lehran {

// Screen dimensions (logical size)
const int SCREEN_WIDTH = 1920;
const int SCREEN_HEIGHT = 1080;

ConfigManager::ConfigManager() {
    // Default settings
    displaySettings.windowWidth = 1280;
    displaySettings.windowHeight = 720;
    displaySettings.windowMode = WindowMode::WINDOWED;
    displaySettings.nativeDisplayWidth = 1920;
    displaySettings.nativeDisplayHeight = 1080;
    displaySettings.renderScale = 0.6667f;
    displaySettings.selectedResolutionIndex = 0;

    audioSettings.masterVolume = 80;
    audioSettings.musicVolume = 70;
    audioSettings.sfxVolume = 80;
    audioSettings.voiceVolume = 80;
}

ConfigManager::~ConfigManager() {
}

bool ConfigManager::LoadEngineSettings(const std::string& configPath) {
    try {
        std::ifstream settingsFile(configPath);
        if (settingsFile.is_open()) {
            std::string line;
            while (std::getline(settingsFile, line)) {
                // Skip empty lines and comments
                if (line.empty() || line[0] == ';' || line[0] == '#') continue;

                // Parse key=value pairs
                size_t pos = line.find('=');
                if (pos != std::string::npos) {
                    std::string key = line.substr(0, pos);
                    std::string value = line.substr(pos + 1);

                    // Trim whitespace
                    key.erase(0, key.find_first_not_of(" \t"));
                    key.erase(key.find_last_not_of(" \t") + 1);
                    value.erase(0, value.find_first_not_of(" \t"));
                    value.erase(value.find_last_not_of(" \t") + 1);

                    // Parse settings
                    if (key == "window_width") {
                        displaySettings.windowWidth = std::stoi(value);
                    } else if (key == "window_height") {
                        displaySettings.windowHeight = std::stoi(value);
                    } else if (key == "window_mode") {
                        int modeValue = std::stoi(value);
                        if (modeValue >= 0 && modeValue <= 2) {
                            displaySettings.windowMode = static_cast<WindowMode>(modeValue);
                        }
                    } else if (key == "master_volume") {
                        audioSettings.masterVolume = std::stoi(value);
                    } else if (key == "music_volume") {
                        audioSettings.musicVolume = std::stoi(value);
                    } else if (key == "sfx_volume") {
                        audioSettings.sfxVolume = std::stoi(value);
                    } else if (key == "voice_volume") {
                        audioSettings.voiceVolume = std::stoi(value);
                    }
                }
            }
            settingsFile.close();

            // Calculate render scale based on window size
            CalculateRenderScale();

            // Set resolution index based on loaded dimensions
            if (displaySettings.windowWidth == 1280 && displaySettings.windowHeight == 720) {
                displaySettings.selectedResolutionIndex = 0;
            } else if (displaySettings.windowWidth == 1600 && displaySettings.windowHeight == 900) {
                displaySettings.selectedResolutionIndex = 1;
            } else if (displaySettings.windowWidth == 1920 && displaySettings.windowHeight == 1080) {
                displaySettings.selectedResolutionIndex = 2;
            } else {
                displaySettings.selectedResolutionIndex = 0; // Default to 720p if unknown
            }

            std::cout << "Engine settings loaded successfully" << std::endl;
            std::cout << "  Resolution: " << displaySettings.windowWidth << "x" 
                      << displaySettings.windowHeight << std::endl;
            std::cout << "  Render scale: " << displaySettings.renderScale << std::endl;
            return true;
        } else {
            std::cout << "No config file found, using defaults (720p windowed)" << std::endl;
            SaveEngineSettings(configPath); // Create default settings file
            return false;
        }
    } catch (const std::exception& e) {
        std::cerr << "Failed to load engine settings: " << e.what() << std::endl;
        std::cout << "Using default settings (720p windowed)" << std::endl;
        return false;
    }
}

void ConfigManager::SaveEngineSettings(const std::string& configPath) {
    try {
        std::ofstream settingsFile(configPath);
        if (settingsFile.is_open()) {
            settingsFile << "; Lehran Engine Configuration\n";
            settingsFile << "; Window modes: 0=Windowed, 1=Borderless, 2=Fullscreen\n";
            settingsFile << "\n[Display]\n";
            settingsFile << "window_width=" << displaySettings.windowWidth << "\n";
            settingsFile << "window_height=" << displaySettings.windowHeight << "\n";
            settingsFile << "window_mode=" << static_cast<int>(displaySettings.windowMode) << "\n";
            settingsFile << "vsync=1\n";
            settingsFile << "\n[Audio]\n";
            settingsFile << "master_volume=" << audioSettings.masterVolume << "\n";
            settingsFile << "music_volume=" << audioSettings.musicVolume << "\n";
            settingsFile << "sfx_volume=" << audioSettings.sfxVolume << "\n";
            settingsFile << "voice_volume=" << audioSettings.voiceVolume << "\n";
            settingsFile.close();
            std::cout << "Engine settings saved" << std::endl;
        }
    } catch (const std::exception& e) {
        std::cerr << "Failed to save engine settings: " << e.what() << std::endl;
    }
}

void ConfigManager::SetWindowSize(int width, int height) {
    displaySettings.windowWidth = width;
    displaySettings.windowHeight = height;
    CalculateRenderScale();
}

void ConfigManager::SetWindowMode(WindowMode mode) {
    displaySettings.windowMode = mode;
}

void ConfigManager::SetNativeDisplaySize(int width, int height) {
    displaySettings.nativeDisplayWidth = width;
    displaySettings.nativeDisplayHeight = height;
}

void ConfigManager::SetResolutionIndex(int index) {
    displaySettings.selectedResolutionIndex = index;
    int width, height;
    GetResolutionDimensions(index, width, height);
    SetWindowSize(width, height);
}

void ConfigManager::SetMasterVolume(int volume) {
    audioSettings.masterVolume = std::clamp(volume, 0, 100);
}

void ConfigManager::SetMusicVolume(int volume) {
    audioSettings.musicVolume = std::clamp(volume, 0, 100);
}

void ConfigManager::SetSFXVolume(int volume) {
    audioSettings.sfxVolume = std::clamp(volume, 0, 100);
}

void ConfigManager::SetVoiceVolume(int volume) {
    audioSettings.voiceVolume = std::clamp(volume, 0, 100);
}

void ConfigManager::ApplyAudioVolumes(bool audioInitialized) {
    if (!audioInitialized) {
        return;
    }

    // Calculate combined volume for music (master * music / 10000)
    // SDL_mixer music volume ranges from 0 to MIX_MAX_VOLUME (128)
    int musicVol = (MIX_MAX_VOLUME * audioSettings.masterVolume * audioSettings.musicVolume) / 10000;
    Mix_VolumeMusic(musicVol);

    // Calculate combined volume for SFX (master * sfx / 10000)
    // Set volume for all channels (-1 means all channels)
    int sfxVol = (MIX_MAX_VOLUME * audioSettings.masterVolume * audioSettings.sfxVolume) / 10000;
    Mix_Volume(-1, sfxVol);

    std::cout << "Applied audio volumes - Music: " << musicVol << "/" << MIX_MAX_VOLUME 
              << ", SFX: " << sfxVol << "/" << MIX_MAX_VOLUME << std::endl;
}

void ConfigManager::CycleResolutionForward() {
    displaySettings.selectedResolutionIndex = (displaySettings.selectedResolutionIndex + 1) % 3;
    int width, height;
    GetResolutionDimensions(displaySettings.selectedResolutionIndex, width, height);
    SetWindowSize(width, height);
}

void ConfigManager::CycleResolutionBackward() {
    displaySettings.selectedResolutionIndex = (displaySettings.selectedResolutionIndex + 2) % 3;
    int width, height;
    GetResolutionDimensions(displaySettings.selectedResolutionIndex, width, height);
    SetWindowSize(width, height);
}

void ConfigManager::GetResolutionDimensions(int index, int& width, int& height) const {
    const int resolutionWidths[] = {1280, 1600, 1920};
    const int resolutionHeights[] = {720, 900, 1080};
    
    if (index >= 0 && index < 3) {
        width = resolutionWidths[index];
        height = resolutionHeights[index];
    } else {
        width = 1280;
        height = 720;
    }
}

void ConfigManager::CalculateRenderScale() {
    displaySettings.renderScale = (float)displaySettings.windowHeight / (float)SCREEN_HEIGHT;
}

} // namespace Lehran
