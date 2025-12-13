#pragma once

#include <string>
#include <SDL_mixer.h>

namespace Lehran {

enum class WindowMode {
    WINDOWED = 0,
    BORDERLESS = 1,
    FULLSCREEN = 2
};

struct DisplaySettings {
    int windowWidth;
    int windowHeight;
    WindowMode windowMode;
    int nativeDisplayWidth;
    int nativeDisplayHeight;
    float renderScale;
    int selectedResolutionIndex;
};

struct AudioSettings {
    int masterVolume;  // 0-100
    int musicVolume;   // 0-100
    int sfxVolume;     // 0-100
    int voiceVolume;   // 0-100
};

class ConfigManager {
public:
    ConfigManager();
    ~ConfigManager();

    // Load and save settings
    bool LoadEngineSettings(const std::string& configPath = "config.ini");
    void SaveEngineSettings(const std::string& configPath = "config.ini");

    // Display settings
    const DisplaySettings& GetDisplaySettings() const { return displaySettings; }
    void SetWindowSize(int width, int height);
    void SetWindowMode(WindowMode mode);
    void SetNativeDisplaySize(int width, int height);
    void SetResolutionIndex(int index);
    int GetWindowWidth() const { return displaySettings.windowWidth; }
    int GetWindowHeight() const { return displaySettings.windowHeight; }
    WindowMode GetWindowMode() const { return displaySettings.windowMode; }
    int GetNativeDisplayWidth() const { return displaySettings.nativeDisplayWidth; }
    int GetNativeDisplayHeight() const { return displaySettings.nativeDisplayHeight; }
    float GetRenderScale() const { return displaySettings.renderScale; }
    int GetResolutionIndex() const { return displaySettings.selectedResolutionIndex; }

    // Audio settings
    const AudioSettings& GetAudioSettings() const { return audioSettings; }
    void SetMasterVolume(int volume);
    void SetMusicVolume(int volume);
    void SetSFXVolume(int volume);
    void SetVoiceVolume(int volume);
    void ApplyAudioVolumes(bool audioInitialized);
    int GetMasterVolume() const { return audioSettings.masterVolume; }
    int GetMusicVolume() const { return audioSettings.musicVolume; }
    int GetSFXVolume() const { return audioSettings.sfxVolume; }
    int GetVoiceVolume() const { return audioSettings.voiceVolume; }

    // Resolution helpers
    void CycleResolutionForward();
    void CycleResolutionBackward();
    void GetResolutionDimensions(int index, int& width, int& height) const;

private:
    DisplaySettings displaySettings;
    AudioSettings audioSettings;

    void CalculateRenderScale();
};

} // namespace Lehran
