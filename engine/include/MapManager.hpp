#pragma once

#include <SDL.h>
#include <SDL_mixer.h>
#include <SDL_ttf.h>
#include "TextureManager.hpp"
#include "json.hpp"
#include <string>
#include <vector>

using json = nlohmann::json;

namespace Lehran {

struct TileType {
    int id;
    std::string name;
    std::string texturePath;
    bool passable;
    int moveCost;
    int avoidBonus;
    int defenseBonus;
    SDL_Texture* texture;
    
    TileType() : id(0), passable(true), moveCost(1), avoidBonus(0), 
                 defenseBonus(0), texture(nullptr) {}
};

struct MapLayer {
    std::string name;
    bool visible;
    std::vector<int> data;  // Tile IDs in row-major order
    
    MapLayer() : visible(true) {}
};

struct WeaponData {
    std::string id;
    std::string name;
    std::string type;  // sword, axe, lance, tome, etc.
    int might;
    int hit;
    int crit;
    int weight;
    int durability;  // -1 for infinite
    std::vector<int> range;
    std::string user;  // For PRF weapons
    bool isPRF;
    
    WeaponData() : might(0), hit(0), crit(0), weight(0), durability(0), isPRF(false) {}
};

struct MapUnit {
    std::string type;        // "player" or "enemy"
    std::string unitId;      // ID to lookup in units.json
    std::string name;        // Unit name from data
    std::string className;   // Class name from data
    int level;               // Current level
    std::string spritePath;
    int x, y;                // Grid position
    
    // Stats
    int hp, maxHp;
    int str, mag, skl, spd, lck, def, res, con, mov;
    
    // Inventory
    std::vector<std::string> inventory;  // Item IDs
    int equippedItemIndex;               // Index of equipped item, -1 if none
    
    // State
    bool hasMoved;           // Has unit moved this turn
    SDL_Texture* texture;
    
    MapUnit() : x(0), y(0), level(1), hp(20), maxHp(20), 
                str(5), mag(5), skl(5), spd(5), lck(5), def(5), res(5), con(5), mov(5),
                equippedItemIndex(-1), hasMoved(false), texture(nullptr) {}
};

class MapManager {
private:
    SDL_Renderer* renderer;
    TextureManager* textureManager;
    class ConfigManager* configManager;
    TTF_Font* font;
    
    // Atlas data
    std::string atlasPath;
    int tileSize;
    std::vector<TileType> tileTypes;
    
    // Map data
    std::string mapName;
    std::string mapMusic;
    int mapWidth;
    int mapHeight;
    std::vector<MapLayer> layers;
    std::vector<MapUnit> units;
    
    // Weapon and class data
    json weaponsData;
    json classesData;
    
    // Camera
    int cameraX;
    int cameraY;
    
    // Display scaling
    float scale;
    
    // Cursor
    int cursorX;
    int cursorY;
    SDL_Texture* cursorTexture;
    Mix_Chunk* cursorSound;
    bool showCursor;
    
    // Unit selection and movement
    int selectedUnitIndex;   // Index of selected unit, -1 if none
    std::vector<std::pair<int, int>> moveRangeTiles;  // Tiles within move range
    std::vector<std::pair<int, int>> attackRangeTiles; // Tiles within attack range
    SDL_Texture* moveRangeTexture;
    SDL_Texture* attackRangeTexture;
    
    // Action menu after movement
    bool showActionMenu;
    int selectedActionIndex;  // 0=Inventory, 1=Wait
    int originalUnitX;  // Original X position before move (for cancellation)
    int originalUnitY;  // Original Y position before move (for cancellation)
    
    // Inventory menu
    bool showInventoryMenu;
    int selectedInventoryIndex;
    int inventoryUnitIndex;  // Unit whose inventory is being shown
    bool showDropConfirmation;  // Showing confirmation dialog for dropping
    std::vector<std::string> originalInventory;  // Backup for cancellation
    int originalEquippedIndex;  // Backup equipped index
    
    // Unit info panel
    bool showUnitInfo;
    int unitInfoIndex;  // Unit whose info is being shown
    
    void ClearAtlas();
    void ClearMap();
    void CalculateMovementRange();
    void CalculateAttackRange();
    int GetUnitAtPosition(int x, int y) const;
    WeaponData GetWeaponData(const std::string& weaponId) const;
    bool CanUnitWieldWeapon(const MapUnit& unit, const WeaponData& weapon) const;
    std::string GetClassDisplayName(const std::string& classId) const;
    
public:
    MapManager(SDL_Renderer* renderer, TextureManager* textureManager, class ConfigManager* configManager, TTF_Font* font);
    ~MapManager();
    
    // Load atlas and map
    bool LoadAtlas(const std::string& atlasFile);
    bool LoadMap(const std::string& mapFile);
    
    // Get map music
    std::string GetMapMusic() const { return mapMusic; }
    
    // Rendering
    void Render();
    
    // Camera control
    void SetCamera(int x, int y);
    void MoveCamera(int dx, int dy);
    
    // Cursor control
    void MoveCursor(int dx, int dy);
    void SetCursorPosition(int x, int y);
    void SetCursorVisible(bool visible) { showCursor = visible; }
    bool IsCursorVisible() const { return showCursor; }
    int GetCursorX() const { return cursorX; }
    int GetCursorY() const { return cursorY; }
    
    // Unit selection and movement
    void SelectUnit();
    void CancelSelection();
    void ConfirmMove();
    bool HasSelectedUnit() const { return selectedUnitIndex >= 0; }
    bool IsInMoveRange(int x, int y) const;
    
    // Action menu
    void MoveActionSelection(int delta);
    void ConfirmAction();
    void CancelActionMenu();
    bool IsShowingActionMenu() const { return showActionMenu; }
    int GetSelectedAction() const { return selectedActionIndex; }
    
    // Inventory menu
    void OpenInventory();
    void CloseInventory();
    void MoveInventorySelection(int delta);
    void ConfirmInventoryAction();
    void CancelDropConfirmation();
    bool IsShowingInventory() const { return showInventoryMenu; }
    bool IsShowingDropConfirmation() const { return showDropConfirmation; }
    
    // Unit info panel
    void ToggleUnitInfo();
    bool IsShowingUnitInfo() const { return showUnitInfo; }
    
    // Getters
    std::string GetMapName() const { return mapName; }
    int GetMapWidth() const { return mapWidth; }
    int GetMapHeight() const { return mapHeight; }
    int GetTileSize() const { return tileSize; }
    int GetScaledTileSize() const { return static_cast<int>(tileSize * scale); }
};

} // namespace Lehran
