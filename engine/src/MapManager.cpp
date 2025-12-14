#include "MapManager.hpp"
#include "ConfigManager.hpp"
#include <iostream>
#include <fstream>

namespace Lehran {

MapManager::MapManager(SDL_Renderer* renderer, TextureManager* textureManager, ConfigManager* configManager, TTF_Font* font)
    : renderer(renderer), textureManager(textureManager), configManager(configManager), font(font),
      tileSize(32), mapWidth(0), mapHeight(0),
      cameraX(0), cameraY(0), scale(3.0f), cursorX(0), cursorY(0),
      cursorTexture(nullptr), cursorSound(nullptr), showCursor(true),
      selectedUnitIndex(-1), moveRangeTexture(nullptr), attackRangeTexture(nullptr),
      showActionMenu(false), selectedActionIndex(0), originalUnitX(0), originalUnitY(0),
      showInventoryMenu(false), selectedInventoryIndex(0), inventoryUnitIndex(-1),
      showDropConfirmation(false), originalEquippedIndex(-1),
      showUnitInfo(false), unitInfoIndex(-1) {
    // Load cursor texture
    cursorTexture = textureManager->LoadTexture("assets/ui/cursor.png");
    if (!cursorTexture) {
        std::cerr << "WARNING: Failed to load cursor texture" << std::endl;
    }
    
    // Load range textures
    moveRangeTexture = textureManager->LoadTexture("assets/ui/mov_range.png");
    if (!moveRangeTexture) {
        std::cerr << "WARNING: Failed to load movement range texture" << std::endl;
    }
    
    attackRangeTexture = textureManager->LoadTexture("assets/ui/attack_range.png");
    if (!attackRangeTexture) {
        std::cerr << "WARNING: Failed to load attack range texture" << std::endl;
    }
    
    // Load cursor sound effect
    cursorSound = Mix_LoadWAV("assets/sfx/cursor_move.ogg");
    if (!cursorSound) {
        std::cerr << "WARNING: Failed to load cursor sound: " << Mix_GetError() << std::endl;
    }
}

MapManager::~MapManager() {
    ClearAtlas();
    ClearMap();
    if (cursorSound) {
        Mix_FreeChunk(cursorSound);
        cursorSound = nullptr;
    }
}

void MapManager::ClearAtlas() {
    tileTypes.clear();
    atlasPath.clear();
}

void MapManager::ClearMap() {
    layers.clear();
    units.clear();
    mapName.clear();
    mapWidth = 0;
    mapHeight = 0;
}

bool MapManager::LoadAtlas(const std::string& atlasFile) {
    std::cout << "Loading tile atlas: " << atlasFile << std::endl;
    
    ClearAtlas();
    
    try {
        std::ifstream file(atlasFile);
        if (!file.is_open()) {
            std::cerr << "ERROR: Could not open atlas file: " << atlasFile << std::endl;
            return false;
        }
        
        json atlasData;
        file >> atlasData;
        file.close();
        
        atlasPath = atlasFile;
        tileSize = atlasData.value("tile_size", 32);
        
        // Load tile types
        if (atlasData.contains("tiles")) {
            for (const auto& tileJson : atlasData["tiles"]) {
                TileType tile;
                tile.id = tileJson.value("id", 0);
                tile.name = tileJson.value("name", "");
                tile.texturePath = tileJson.value("texture", "");
                tile.passable = tileJson.value("passable", true);
                tile.moveCost = tileJson.value("move_cost", 1);
                tile.avoidBonus = tileJson.value("avoid_bonus", 0);
                tile.defenseBonus = tileJson.value("defense_bonus", 0);
                
                // Load texture
                tile.texture = textureManager->LoadTexture(tile.texturePath);
                if (!tile.texture) {
                    std::cerr << "WARNING: Failed to load tile texture: " << tile.texturePath << std::endl;
                }
                
                tileTypes.push_back(tile);
                std::cout << "  Loaded tile: " << tile.name << " (ID: " << tile.id << ")" << std::endl;
            }
        }
        
        std::cout << "Atlas loaded: " << tileTypes.size() << " tile types" << std::endl;
        return true;
        
    } catch (const std::exception& e) {
        std::cerr << "ERROR: Failed to load atlas: " << e.what() << std::endl;
        return false;
    }
}

bool MapManager::LoadMap(const std::string& mapFile) {
    std::cout << "Loading map: " << mapFile << std::endl;
    
    ClearMap();
    
    // Reset cursor and camera to starting position
    cursorX = 0;
    cursorY = 0;
    cameraX = 0;
    cameraY = 0;
    
    // Reset all UI states
    selectedUnitIndex = -1;
    showActionMenu = false;
    selectedActionIndex = 0;
    showInventoryMenu = false;
    selectedInventoryIndex = 0;
    inventoryUnitIndex = -1;
    showDropConfirmation = false;
    showUnitInfo = false;
    unitInfoIndex = -1;
    moveRangeTiles.clear();
    attackRangeTiles.clear();
    originalInventory.clear();
    originalEquippedIndex = -1;
    
    try {
        std::ifstream file(mapFile);
        if (!file.is_open()) {
            std::cerr << "ERROR: Could not open map file: " << mapFile << std::endl;
            return false;
        }
        
        json mapData;
        file >> mapData;
        file.close();
        
        mapName = mapData.value("name", "Untitled Map");
        mapMusic = mapData.value("music", "");
        mapWidth = mapData.value("width", 0);
        mapHeight = mapData.value("height", 0);
        tileSize = mapData.value("tile_size", 32);
        
        // Load atlas if specified
        if (mapData.contains("atlas")) {
            std::string atlasFile = mapData["atlas"];
            if (!LoadAtlas(atlasFile)) {
                std::cerr << "ERROR: Failed to load atlas for map" << std::endl;
                return false;
            }
        }
        
        // Load layers
        if (mapData.contains("layers")) {
            for (const auto& layerJson : mapData["layers"]) {
                MapLayer layer;
                layer.name = layerJson.value("name", "");
                layer.visible = layerJson.value("visible", true);
                
                if (layerJson.contains("data") && layerJson["data"].is_array()) {
                    for (const auto& tileId : layerJson["data"]) {
                        layer.data.push_back(tileId);
                    }
                }
                
                layers.push_back(layer);
                std::cout << "  Loaded layer: " << layer.name << " (" << layer.data.size() << " tiles)" << std::endl;
            }
        }
        
        // Load units
        if (mapData.contains("units")) {
            // Load units.json, weapons.json, and classes.json for unit data
            json unitsData;
            try {
                std::ifstream unitsFile("data/units.json");
                if (unitsFile.is_open()) {
                    unitsFile >> unitsData;
                    unitsFile.close();
                }
            } catch (const std::exception& e) {
                std::cerr << "WARNING: Failed to load units.json: " << e.what() << std::endl;
            }
            
            try {
                std::ifstream weaponsFile("data/weapons.json");
                if (weaponsFile.is_open()) {
                    weaponsFile >> weaponsData;
                    weaponsFile.close();
                }
            } catch (const std::exception& e) {
                std::cerr << "WARNING: Failed to load weapons.json: " << e.what() << std::endl;
            }
            
            try {
                std::ifstream classesFile("data/classes.json");
                if (classesFile.is_open()) {
                    classesFile >> classesData;
                    classesFile.close();
                }
            } catch (const std::exception& e) {
                std::cerr << "WARNING: Failed to load classes.json: " << e.what() << std::endl;
            }
            
            for (const auto& unitJson : mapData["units"]) {
                MapUnit unit;
                unit.type = unitJson.value("type", "");
                unit.unitId = unitJson.value("unit_id", "");
                unit.spritePath = unitJson.value("sprite", "");
                unit.x = unitJson.value("x", 0);
                unit.y = unitJson.value("y", 0);
                
                // Load unit data from units.json if unit_id is specified
                // units.json is now organized as: { "player": { "alvis": {...} }, "enemy": {...} }
                json unitData;
                bool foundUnit = false;
                if (!unit.unitId.empty() && unitsData.contains(unit.type)) {
                    if (unitsData[unit.type].contains(unit.unitId)) {
                        unitData = unitsData[unit.type][unit.unitId];
                        foundUnit = true;
                    }
                }
                
                if (foundUnit) {
                    unit.name = unitData.value("name", "Unknown");
                    std::string classId = unitData.value("class", "");
                    unit.className = GetClassDisplayName(classId);
                    unit.level = unitData.value("level", 1);
                    
                    if (unitData.contains("stats")) {
                        const auto& stats = unitData["stats"];
                        unit.maxHp = stats.value("hp", 20);
                        unit.hp = unit.maxHp;
                        unit.str = stats.value("str", 5);
                        unit.mag = stats.value("mag", 5);
                        unit.skl = stats.value("skl", 5);
                        unit.spd = stats.value("spd", 5);
                        unit.lck = stats.value("lck", 5);
                        unit.def = stats.value("def", 5);
                        unit.res = stats.value("res", 5);
                        unit.con = stats.value("con", 5);
                        unit.mov = stats.value("mov", 5);
                    }
                    
                    // Load inventory
                    if (unitData.contains("current_inventory") && unitData["current_inventory"].is_array()) {
                        for (const auto& itemId : unitData["current_inventory"]) {
                            unit.inventory.push_back(itemId.get<std::string>());
                        }
                        // Equip first item by default
                        if (!unit.inventory.empty()) {
                            unit.equippedItemIndex = 0;
                        }
                    }
                } else {
                    // Default values if no unit data found
                    unit.name = "Unknown";
                    unit.mov = 5;
                }
                
                // Load unit texture
                unit.texture = textureManager->LoadTexture(unit.spritePath);
                if (!unit.texture) {
                    std::cerr << "WARNING: Failed to load unit sprite: " << unit.spritePath << std::endl;
                }
                
                units.push_back(unit);
                std::cout << "  Loaded " << unit.type << " unit '" << unit.name << "' at (" << unit.x << ", " << unit.y << ")" << std::endl;
            }
        }
        
        std::cout << "Map loaded: " << mapName << " (" << mapWidth << "x" << mapHeight << ")" << std::endl;
        return true;
        
    } catch (const std::exception& e) {
        std::cerr << "ERROR: Failed to load map: " << e.what() << std::endl;
        return false;
    }
}

void MapManager::Render() {
    if (layers.empty() || tileTypes.empty()) {
        return;
    }
    
    int scaledTileSize = static_cast<int>(tileSize * scale);
    
    // Render each layer
    for (const auto& layer : layers) {
        if (!layer.visible) continue;
        
        // Render tiles
        for (int y = 0; y < mapHeight; y++) {
            for (int x = 0; x < mapWidth; x++) {
                int index = y * mapWidth + x;
                if (index >= layer.data.size()) continue;
                
                int tileId = layer.data[index];
                
                // Find tile type
                SDL_Texture* texture = nullptr;
                for (const auto& tileType : tileTypes) {
                    if (tileType.id == tileId) {
                        texture = tileType.texture;
                        break;
                    }
                }
                
                if (texture) {
                    // Calculate screen position with scaling
                    int screenX = (x * scaledTileSize) - cameraX;
                    int screenY = (y * scaledTileSize) - cameraY;
                    
                    // Only render if on screen (1920x1080)
                    if (screenX + scaledTileSize >= 0 && screenX < 1920 &&
                        screenY + scaledTileSize >= 0 && screenY < 1080) {
                        textureManager->RenderTexture(texture, screenX, screenY, scaledTileSize, scaledTileSize);
                    }
                }
            }
        }
    }
    
    // Render movement range tiles
    if (selectedUnitIndex >= 0 && moveRangeTexture && !showActionMenu) {
        for (const auto& tile : moveRangeTiles) {
            int screenX = (tile.first * scaledTileSize) - cameraX;
            int screenY = (tile.second * scaledTileSize) - cameraY;
            
            if (screenX + scaledTileSize >= 0 && screenX < 1920 &&
                screenY + scaledTileSize >= 0 && screenY < 1080) {
                textureManager->RenderTexture(moveRangeTexture, screenX, screenY, scaledTileSize, scaledTileSize);
            }
        }
    }
    
    // Render attack range tiles
    if (selectedUnitIndex >= 0 && attackRangeTexture && !showActionMenu) {
        for (const auto& tile : attackRangeTiles) {
            int screenX = (tile.first * scaledTileSize) - cameraX;
            int screenY = (tile.second * scaledTileSize) - cameraY;
            
            if (screenX + scaledTileSize >= 0 && screenX < 1920 &&
                screenY + scaledTileSize >= 0 && screenY < 1080) {
                textureManager->RenderTexture(attackRangeTexture, screenX, screenY, scaledTileSize, scaledTileSize);
            }
        }
    }
    
    // Render units on top of tiles
    for (const auto& unit : units) {
        if (unit.texture) {
            int screenX = (unit.x * scaledTileSize) - cameraX;
            int screenY = (unit.y * scaledTileSize) - cameraY;
            
            // Only render if on screen
            if (screenX + scaledTileSize >= 0 && screenX < 1920 &&
                screenY + scaledTileSize >= 0 && screenY < 1080) {
                textureManager->RenderTexture(unit.texture, screenX, screenY, scaledTileSize, scaledTileSize);
            }
        }
    }
    
    // Render cursor on top of everything
    if (showCursor && cursorTexture) {
        int screenX = (cursorX * scaledTileSize) - cameraX;
        int screenY = (cursorY * scaledTileSize) - cameraY;
        textureManager->RenderTexture(cursorTexture, screenX, screenY, scaledTileSize, scaledTileSize);
    }
    
    // Render action menu if active
    if (showActionMenu && font) {
        // Draw menu box
        SDL_Rect menuBox = {1920 - 300, 100, 250, 150};
        SDL_SetRenderDrawColor(renderer, 30, 30, 50, 240);
        SDL_RenderFillRect(renderer, &menuBox);
        SDL_SetRenderDrawColor(renderer, 180, 180, 200, 255);
        SDL_RenderDrawRect(renderer, &menuBox);
        
        // Draw menu options
        SDL_Rect inventoryBox = {menuBox.x + 20, menuBox.y + 20, 210, 40};
        SDL_Rect waitBox = {menuBox.x + 20, menuBox.y + 80, 210, 40};
        
        if (selectedActionIndex == 0) {
            SDL_SetRenderDrawColor(renderer, 100, 150, 200, 255);
            SDL_RenderFillRect(renderer, &inventoryBox);
        }
        if (selectedActionIndex == 1) {
            SDL_SetRenderDrawColor(renderer, 100, 150, 200, 255);
            SDL_RenderFillRect(renderer, &waitBox);
        }
        
        SDL_SetRenderDrawColor(renderer, 180, 180, 200, 255);
        SDL_RenderDrawRect(renderer, &inventoryBox);
        SDL_RenderDrawRect(renderer, &waitBox);
        
        // Render text
        SDL_Color textColor = {255, 255, 255, 255};
        
        SDL_Surface* inventorySurface = TTF_RenderText_Blended(font, "Items", textColor);
        if (inventorySurface) {
            SDL_Texture* inventoryTexture = SDL_CreateTextureFromSurface(renderer, inventorySurface);
            if (inventoryTexture) {
                SDL_Rect textRect = {inventoryBox.x + 10, inventoryBox.y + 8, inventorySurface->w, inventorySurface->h};
                SDL_RenderCopy(renderer, inventoryTexture, nullptr, &textRect);
                SDL_DestroyTexture(inventoryTexture);
            }
            SDL_FreeSurface(inventorySurface);
        }
        
        SDL_Surface* waitSurface = TTF_RenderText_Blended(font, "Wait", textColor);
        if (waitSurface) {
            SDL_Texture* waitTexture = SDL_CreateTextureFromSurface(renderer, waitSurface);
            if (waitTexture) {
                SDL_Rect textRect = {waitBox.x + 10, waitBox.y + 8, waitSurface->w, waitSurface->h};
                SDL_RenderCopy(renderer, waitTexture, nullptr, &textRect);
                SDL_DestroyTexture(waitTexture);
            }
            SDL_FreeSurface(waitSurface);
        }
    }
    
    // Render inventory menu if active
    if (showInventoryMenu && font && inventoryUnitIndex >= 0) {
        const auto& unit = units[inventoryUnitIndex];
        
        // Draw inventory box
        int menuHeight = 150 + (unit.inventory.size() * 40);
        SDL_Rect inventoryMenuBox = {1920 - 450, 100, 400, menuHeight};
        SDL_SetRenderDrawColor(renderer, 30, 30, 50, 240);
        SDL_RenderFillRect(renderer, &inventoryMenuBox);
        SDL_SetRenderDrawColor(renderer, 180, 180, 200, 255);
        SDL_RenderDrawRect(renderer, &inventoryMenuBox);
        
        SDL_Color textColor = {255, 255, 255, 255};
        SDL_Color equippedColor = {100, 255, 100, 255};
        
        // Draw title
        SDL_Surface* titleSurface = TTF_RenderText_Blended(font, ("Inventory - " + unit.name).c_str(), textColor);
        if (titleSurface) {
            SDL_Texture* titleTexture = SDL_CreateTextureFromSurface(renderer, titleSurface);
            if (titleTexture) {
                SDL_Rect titleRect = {inventoryMenuBox.x + 10, inventoryMenuBox.y + 10, titleSurface->w, titleSurface->h};
                SDL_RenderCopy(renderer, titleTexture, nullptr, &titleRect);
                SDL_DestroyTexture(titleTexture);
            }
            SDL_FreeSurface(titleSurface);
        }
        
        // Draw inventory items
        for (size_t i = 0; i < unit.inventory.size(); i++) {
            SDL_Rect itemBox = {inventoryMenuBox.x + 20, inventoryMenuBox.y + 50 + (int)(i * 40), 360, 35};
            
            if ((int)i == selectedInventoryIndex) {
                SDL_SetRenderDrawColor(renderer, 100, 150, 200, 255);
                SDL_RenderFillRect(renderer, &itemBox);
            }
            
            SDL_SetRenderDrawColor(renderer, 180, 180, 200, 255);
            SDL_RenderDrawRect(renderer, &itemBox);
            
            // Get weapon data and check if unit can wield it
            WeaponData weaponData = GetWeaponData(unit.inventory[i]);
            bool canWield = CanUnitWieldWeapon(unit, weaponData);
            
            // Draw item name with proper capitalization
            bool isEquipped = ((int)i == unit.equippedItemIndex);
            std::string itemText = weaponData.name + (isEquipped ? " (E)" : "");
            
            // Use gray color if unit can't wield this weapon
            SDL_Color itemColor = canWield ? (isEquipped ? equippedColor : textColor) : SDL_Color{128, 128, 128, 255};
            
            SDL_Surface* itemSurface = TTF_RenderText_Blended(font, itemText.c_str(), itemColor);
            if (itemSurface) {
                SDL_Texture* itemTexture = SDL_CreateTextureFromSurface(renderer, itemSurface);
                if (itemTexture) {
                    SDL_Rect textRect = {itemBox.x + 10, itemBox.y + 5, itemSurface->w, itemSurface->h};
                    SDL_RenderCopy(renderer, itemTexture, nullptr, &textRect);
                    SDL_DestroyTexture(itemTexture);
                }
                SDL_FreeSurface(itemSurface);
            }
        }
        
        // Draw "Drop" option
        SDL_Rect dropBox = {inventoryMenuBox.x + 20, inventoryMenuBox.y + 50 + (int)(unit.inventory.size() * 40), 360, 35};
        
        if (selectedInventoryIndex == (int)unit.inventory.size()) {
            SDL_SetRenderDrawColor(renderer, 100, 150, 200, 255);
            SDL_RenderFillRect(renderer, &dropBox);
        }
        
        SDL_SetRenderDrawColor(renderer, 180, 180, 200, 255);
        SDL_RenderDrawRect(renderer, &dropBox);
        
        SDL_Surface* dropSurface = TTF_RenderText_Blended(font, "Drop Item", textColor);
        if (dropSurface) {
            SDL_Texture* dropTexture = SDL_CreateTextureFromSurface(renderer, dropSurface);
            if (dropTexture) {
                SDL_Rect textRect = {dropBox.x + 10, dropBox.y + 5, dropSurface->w, dropSurface->h};
                SDL_RenderCopy(renderer, dropTexture, nullptr, &textRect);
                SDL_DestroyTexture(dropTexture);
            }
            SDL_FreeSurface(dropSurface);
        }
        
        // Draw weapon info panel for selected item (if not on "Drop")
        if (selectedInventoryIndex < (int)unit.inventory.size()) {
            WeaponData weaponData = GetWeaponData(unit.inventory[selectedInventoryIndex]);
            bool canWield = CanUnitWieldWeapon(unit, weaponData);
            
            // Draw weapon info box to the left of inventory
            SDL_Rect weaponInfoBox = {inventoryMenuBox.x - 450, 100, 400, 400};
            SDL_SetRenderDrawColor(renderer, 30, 30, 50, 240);
            SDL_RenderFillRect(renderer, &weaponInfoBox);
            SDL_SetRenderDrawColor(renderer, 180, 180, 200, 255);
            SDL_RenderDrawRect(renderer, &weaponInfoBox);
            
            int yPos = weaponInfoBox.y + 15;
            int lineHeight = 35;
            SDL_Color whiteColor = {255, 255, 255, 255};
            
            auto renderInfoLine = [&](const std::string& text, const SDL_Color& color) {
                SDL_Surface* surface = TTF_RenderText_Blended(font, text.c_str(), color);
                if (surface) {
                    SDL_Texture* texture = SDL_CreateTextureFromSurface(renderer, surface);
                    if (texture) {
                        SDL_Rect rect = {weaponInfoBox.x + 15, yPos, surface->w, surface->h};
                        SDL_RenderCopy(renderer, texture, nullptr, &rect);
                        SDL_DestroyTexture(texture);
                    }
                    SDL_FreeSurface(surface);
                }
                yPos += lineHeight;
            };
            
            // Display weapon name and type
            SDL_Color nameColor = canWield ? whiteColor : SDL_Color{255, 100, 100, 255};
            renderInfoLine(weaponData.name, nameColor);
            renderInfoLine("Type: " + weaponData.type, whiteColor);
            
            if (!canWield) {
                renderInfoLine("Cannot Wield!", SDL_Color{255, 100, 100, 255});
            } else if (weaponData.isPRF) {
                renderInfoLine("PRF Weapon", SDL_Color{255, 215, 0, 255});
            }
            
            yPos += 10;
            
            // Display weapon stats
            renderInfoLine("Mt: " + std::to_string(weaponData.might), whiteColor);
            renderInfoLine("Hit: " + std::to_string(weaponData.hit), whiteColor);
            renderInfoLine("Crit: " + std::to_string(weaponData.crit), whiteColor);
            renderInfoLine("Wt: " + std::to_string(weaponData.weight), whiteColor);
            
            if (weaponData.durability == -1) {
                renderInfoLine("Dur: --", whiteColor);
            } else {
                renderInfoLine("Dur: " + std::to_string(weaponData.durability), whiteColor);
            }
            
            // Display range
            if (!weaponData.range.empty()) {
                std::string rangeStr = "Rng: ";
                for (size_t i = 0; i < weaponData.range.size(); i++) {
                    rangeStr += std::to_string(weaponData.range[i]);
                    if (i < weaponData.range.size() - 1) rangeStr += "-";
                }
                renderInfoLine(rangeStr, whiteColor);
            }
        }
        
        // Draw drop confirmation dialog if active
        if (showDropConfirmation && unit.equippedItemIndex >= 0 && unit.equippedItemIndex < (int)unit.inventory.size()) {
            WeaponData weaponData = GetWeaponData(unit.inventory[unit.equippedItemIndex]);
            
            // Draw confirmation box in center
            SDL_Rect confirmBox = {760, 400, 400, 200};
            SDL_SetRenderDrawColor(renderer, 40, 40, 60, 250);
            SDL_RenderFillRect(renderer, &confirmBox);
            SDL_SetRenderDrawColor(renderer, 200, 200, 220, 255);
            SDL_RenderDrawRect(renderer, &confirmBox);
            
            int yPos = confirmBox.y + 30;
            auto renderConfirmLine = [&](const std::string& text) {
                SDL_Surface* surface = TTF_RenderText_Blended(font, text.c_str(), textColor);
                if (surface) {
                    SDL_Texture* texture = SDL_CreateTextureFromSurface(renderer, surface);
                    if (texture) {
                        // Center the text
                        int textX = confirmBox.x + (confirmBox.w - surface->w) / 2;
                        SDL_Rect rect = {textX, yPos, surface->w, surface->h};
                        SDL_RenderCopy(renderer, texture, nullptr, &rect);
                        SDL_DestroyTexture(texture);
                    }
                    SDL_FreeSurface(surface);
                }
                yPos += 40;
            };
            
            renderConfirmLine("Drop " + weaponData.name + "?");
            yPos += 20;
            renderConfirmLine("Z/Enter: Confirm");
            renderConfirmLine("X/Esc: Cancel");
        }
    }
    
    // Render unit info panel if active
    if (showUnitInfo && font && unitInfoIndex >= 0) {
        const auto& unit = units[unitInfoIndex];
        
        // Draw info panel
        SDL_Rect infoBox = {50, 100, 400, 500};
        SDL_SetRenderDrawColor(renderer, 30, 30, 50, 240);
        SDL_RenderFillRect(renderer, &infoBox);
        SDL_SetRenderDrawColor(renderer, 180, 180, 200, 255);
        SDL_RenderDrawRect(renderer, &infoBox);
        
        SDL_Color textColor = {255, 255, 255, 255};
        int yPos = infoBox.y + 15;
        int lineHeight = 35;
        
        // Helper lambda to render text line
        auto renderLine = [&](const std::string& text) {
            SDL_Surface* surface = TTF_RenderText_Blended(font, text.c_str(), textColor);
            if (surface) {
                SDL_Texture* texture = SDL_CreateTextureFromSurface(renderer, surface);
                if (texture) {
                    SDL_Rect rect = {infoBox.x + 15, yPos, surface->w, surface->h};
                    SDL_RenderCopy(renderer, texture, nullptr, &rect);
                    SDL_DestroyTexture(texture);
                }
                SDL_FreeSurface(surface);
            }
            yPos += lineHeight;
        };
        
        // Render unit info
        renderLine(unit.name + " - Lv " + std::to_string(unit.level));
        renderLine("Class: " + unit.className);
        renderLine("HP: " + std::to_string(unit.hp) + "/" + std::to_string(unit.maxHp));
        renderLine("Str: " + std::to_string(unit.str) + "  Mag: " + std::to_string(unit.mag));
        renderLine("Skl: " + std::to_string(unit.skl) + "  Spd: " + std::to_string(unit.spd));
        renderLine("Lck: " + std::to_string(unit.lck) + "  Def: " + std::to_string(unit.def));
        renderLine("Res: " + std::to_string(unit.res) + "  Con: " + std::to_string(unit.con));
        renderLine("Mov: " + std::to_string(unit.mov));
        
        if (!unit.inventory.empty()) {
            yPos += 10;
            renderLine("Inventory:");
            for (int i = 0; i < (int)unit.inventory.size(); i++) {
                WeaponData weaponData = GetWeaponData(unit.inventory[i]);
                bool isEquipped = (i == unit.equippedItemIndex);
                std::string itemText = "  " + weaponData.name + (isEquipped ? " *" : "");
                renderLine(itemText);
            }
        } else {
            yPos += 10;
            renderLine("Inventory: Empty");
        }
    }
}

void MapManager::SetCamera(int x, int y) {
    cameraX = x;
    cameraY = y;
}

void MapManager::MoveCamera(int dx, int dy) {
    cameraX += dx;
    cameraY += dy;
    
    int scaledTileSize = static_cast<int>(tileSize * scale);
    
    // Clamp camera to map bounds
    int maxCameraX = (mapWidth * scaledTileSize) - 1920;
    int maxCameraY = (mapHeight * scaledTileSize) - 1080;
    
    if (cameraX < 0) cameraX = 0;
    if (cameraY < 0) cameraY = 0;
    if (cameraX > maxCameraX) cameraX = maxCameraX;
    if (cameraY > maxCameraY) cameraY = maxCameraY;
}

void MapManager::MoveCursor(int dx, int dy) {
    int oldX = cursorX;
    int oldY = cursorY;
    
    cursorX += dx;
    cursorY += dy;
    
    // Clamp cursor to map bounds
    if (cursorX < 0) cursorX = 0;
    if (cursorY < 0) cursorY = 0;
    if (cursorX >= mapWidth) cursorX = mapWidth - 1;
    if (cursorY >= mapHeight) cursorY = mapHeight - 1;
    
    // Play cursor sound if position actually changed
    if ((cursorX != oldX || cursorY != oldY) && cursorSound && configManager) {
        // Only play if SFX volume is not 0
        int masterVol = configManager->GetMasterVolume();
        int sfxVol = configManager->GetSFXVolume();
        if (masterVol > 0 && sfxVol > 0) {
            Mix_PlayChannel(-1, cursorSound, 0);
        }
    }
    
    int scaledTileSize = static_cast<int>(tileSize * scale);
    
    // Auto-scroll camera to keep cursor on screen
    int cursorScreenX = (cursorX * scaledTileSize) - cameraX;
    int cursorScreenY = (cursorY * scaledTileSize) - cameraY;
    
    // Camera scroll thresholds (keep cursor away from edges)
    const int scrollMargin = scaledTileSize * 2;
    
    if (cursorScreenX < scrollMargin) {
        MoveCamera(cursorScreenX - scrollMargin, 0);
    } else if (cursorScreenX > 1920 - scrollMargin - scaledTileSize) {
        MoveCamera(cursorScreenX - (1920 - scrollMargin - scaledTileSize), 0);
    }
    
    if (cursorScreenY < scrollMargin) {
        MoveCamera(0, cursorScreenY - scrollMargin);
    } else if (cursorScreenY > 1080 - scrollMargin - scaledTileSize) {
        MoveCamera(0, cursorScreenY - (1080 - scrollMargin - scaledTileSize));
    }
}

void MapManager::SetCursorPosition(int x, int y) {
    cursorX = x;
    cursorY = y;
    
    // Clamp to map bounds
    if (cursorX < 0) cursorX = 0;
    if (cursorY < 0) cursorY = 0;
    if (cursorX >= mapWidth) cursorX = mapWidth - 1;
    if (cursorY >= mapHeight) cursorY = mapHeight - 1;
}

int MapManager::GetUnitAtPosition(int x, int y) const {
    for (size_t i = 0; i < units.size(); i++) {
        if (units[i].x == x && units[i].y == y) {
            return static_cast<int>(i);
        }
    }
    return -1;
}

void MapManager::SelectUnit() {
    // Check if there's a player unit at cursor position
    int unitIndex = GetUnitAtPosition(cursorX, cursorY);
    if (unitIndex >= 0 && units[unitIndex].type == "player" && !units[unitIndex].hasMoved) {
        selectedUnitIndex = unitIndex;
        CalculateMovementRange();
        CalculateAttackRange();
        std::cout << "Selected unit at (" << cursorX << ", " << cursorY << ")" << std::endl;
    }
}

void MapManager::CancelSelection() {
    selectedUnitIndex = -1;
    moveRangeTiles.clear();
    attackRangeTiles.clear();
    showActionMenu = false;
    selectedActionIndex = 0;
    std::cout << "Selection cancelled" << std::endl;
}

void MapManager::ConfirmMove() {
    if (selectedUnitIndex < 0 || !IsInMoveRange(cursorX, cursorY)) {
        return;
    }
    
    // Store original position for potential cancellation
    originalUnitX = units[selectedUnitIndex].x;
    originalUnitY = units[selectedUnitIndex].y;
    
    // Move the unit
    units[selectedUnitIndex].x = cursorX;
    units[selectedUnitIndex].y = cursorY;
    
    // Clear movement ranges
    moveRangeTiles.clear();
    attackRangeTiles.clear();
    
    // Show action menu
    showActionMenu = true;
    selectedActionIndex = 0;
    
    std::cout << "Unit moved to (" << cursorX << ", " << cursorY << ")" << std::endl;
}

void MapManager::CalculateMovementRange() {
    moveRangeTiles.clear();
    
    if (selectedUnitIndex < 0) return;
    
    const MapUnit& unit = units[selectedUnitIndex];
    int range = unit.mov;
    
    // Simple flood fill for movement range (Manhattan distance)
    // Include current position (distance == 0) to allow staying in place
    for (int y = 0; y < mapHeight; y++) {
        for (int x = 0; x < mapWidth; x++) {
            int distance = abs(x - unit.x) + abs(y - unit.y);
            if (distance >= 0 && distance <= range) {
                // Check if tile is passable and no other unit (or current position)
                bool canMove = true;
                int otherUnit = GetUnitAtPosition(x, y);
                if (otherUnit >= 0 && otherUnit != selectedUnitIndex) {
                    canMove = false;
                }
                
                if (canMove) {
                    moveRangeTiles.push_back({x, y});
                }
            }
        }
    }
    
    std::cout << "Calculated " << moveRangeTiles.size() << " movement tiles" << std::endl;
}

void MapManager::CalculateAttackRange() {
    attackRangeTiles.clear();
    
    if (selectedUnitIndex < 0) return;
    
    const MapUnit& unit = units[selectedUnitIndex];
    int moveRange = unit.mov;
    int attackRange = 2; // Default attack range
    
    // Calculate attack range from edge of movement range (and current position)
    for (int my = 0; my < mapHeight; my++) {
        for (int mx = 0; mx < mapWidth; mx++) {
            int moveDist = abs(mx - unit.x) + abs(my - unit.y);
            
            // Skip if not within movement range (including current position)
            if (moveDist > moveRange) continue;
            
            // From this movement position, calculate attack range
            for (int ay = 0; ay < mapHeight; ay++) {
                for (int ax = 0; ax < mapWidth; ax++) {
                    int attackDist = abs(ax - mx) + abs(ay - my);
                    if (attackDist >= 1 && attackDist <= attackRange) {
                        // Check if this tile is in movement range (including current position)
                        int distFromUnit = abs(ax - unit.x) + abs(ay - unit.y);
                        bool inMoveRange = (distFromUnit >= 0 && distFromUnit <= moveRange);
                        if (!inMoveRange) {
                            // Check if already added
                            bool alreadyAdded = false;
                            for (const auto& tile : attackRangeTiles) {
                                if (tile.first == ax && tile.second == ay) {
                                    alreadyAdded = true;
                                    break;
                                }
                            }
                            if (!alreadyAdded) {
                                attackRangeTiles.push_back({ax, ay});
                            }
                        }
                    }
                }
            }
        }
    }
    
    std::cout << "Calculated " << attackRangeTiles.size() << " attack tiles" << std::endl;
}

bool MapManager::IsInMoveRange(int x, int y) const {
    // Check if it's in the movement range tiles
    for (const auto& tile : moveRangeTiles) {
        if (tile.first == x && tile.second == y) {
            return true;
        }
    }
    // Also allow staying at current position
    if (selectedUnitIndex >= 0) {
        const auto& unit = units[selectedUnitIndex];
        if (x == unit.x && y == unit.y) {
            return true;
        }
    }
    return false;
}

void MapManager::MoveActionSelection(int delta) {
    if (!showActionMenu) return;
    
    selectedActionIndex += delta;
    if (selectedActionIndex < 0) selectedActionIndex = 1;
    if (selectedActionIndex > 1) selectedActionIndex = 0;
}

void MapManager::ConfirmAction() {
    if (!showActionMenu) return;
    
    if (selectedActionIndex == 0) {
        // Inventory
        OpenInventory();
    } else if (selectedActionIndex == 1) {
        // Wait - finalize all inventory changes
        std::cout << "Unit waiting - inventory changes finalized" << std::endl;
        units[selectedUnitIndex].hasMoved = true;
        selectedUnitIndex = -1;
        showActionMenu = false;
        
        // Clear inventory backup so changes are permanent
        originalInventory.clear();
        originalEquippedIndex = -1;
    }
}

void MapManager::CancelActionMenu() {
    if (!showActionMenu || selectedUnitIndex < 0) return;
    
    // Restore unit to original position
    units[selectedUnitIndex].x = originalUnitX;
    units[selectedUnitIndex].y = originalUnitY;
    
    // Move cursor back to unit position
    cursorX = originalUnitX;
    cursorY = originalUnitY;
    
    // Hide action menu
    showActionMenu = false;
    selectedActionIndex = 0;
    
    // Restore movement ranges
    CalculateMovementRange();
    CalculateAttackRange();
    
    std::cout << "Cancelled action, unit returned to (" << originalUnitX << ", " << originalUnitY << ")" << std::endl;
}

void MapManager::OpenInventory() {
    if (selectedUnitIndex < 0) return;
    
    inventoryUnitIndex = selectedUnitIndex;
    
    // Backup current inventory state for potential cancellation
    const auto& unit = units[inventoryUnitIndex];
    originalInventory = unit.inventory;
    originalEquippedIndex = unit.equippedItemIndex;
    
    showInventoryMenu = true;
    showActionMenu = false;
    showDropConfirmation = false;
    selectedInventoryIndex = 0;
    std::cout << "Opening inventory for unit: " << units[inventoryUnitIndex].name << std::endl;
}

void MapManager::CloseInventory() {
    // Restore original inventory if backing out
    if (inventoryUnitIndex >= 0 && inventoryUnitIndex < (int)units.size()) {
        units[inventoryUnitIndex].inventory = originalInventory;
        units[inventoryUnitIndex].equippedItemIndex = originalEquippedIndex;
        std::cout << "Inventory changes cancelled, restored original state" << std::endl;
    }
    
    showInventoryMenu = false;
    showDropConfirmation = false;
    inventoryUnitIndex = -1;
    selectedInventoryIndex = 0;
    originalInventory.clear();
    
    // Return to action menu
    showActionMenu = true;
    selectedActionIndex = 0;
    std::cout << "Closed inventory, returning to action menu" << std::endl;
}

void MapManager::MoveInventorySelection(int delta) {
    if (!showInventoryMenu || inventoryUnitIndex < 0) return;
    
    const auto& unit = units[inventoryUnitIndex];
    int maxIndex = unit.inventory.size() + 1; // +2 for Equip/Drop actions, but showing 1-indexed
    
    selectedInventoryIndex += delta;
    if (selectedInventoryIndex < 0) selectedInventoryIndex = maxIndex - 1;
    if (selectedInventoryIndex >= maxIndex) selectedInventoryIndex = 0;
}

void MapManager::CancelDropConfirmation() {
    showDropConfirmation = false;
    std::cout << "Drop cancelled" << std::endl;
}

void MapManager::ConfirmInventoryAction() {
    if (!showInventoryMenu || inventoryUnitIndex < 0) return;
    
    auto& unit = units[inventoryUnitIndex];
    
    if (showDropConfirmation) {
        // User is confirming the drop - this persists even if they back out (only reverts on action menu cancel)
        if (unit.equippedItemIndex >= 0 && unit.equippedItemIndex < (int)unit.inventory.size()) {
            std::string droppedItem = unit.inventory[unit.equippedItemIndex];
            WeaponData weaponData = GetWeaponData(droppedItem);
            unit.inventory.erase(unit.inventory.begin() + unit.equippedItemIndex);
            
            // Try to equip the first wieldable weapon, or -1 if none
            unit.equippedItemIndex = -1;
            for (int i = 0; i < (int)unit.inventory.size(); i++) {
                WeaponData nextWeapon = GetWeaponData(unit.inventory[i]);
                if (CanUnitWieldWeapon(unit, nextWeapon)) {
                    unit.equippedItemIndex = i;
                    std::cout << "Auto-equipped: " << nextWeapon.name << std::endl;
                    break;
                }
            }
            
            std::cout << "Dropped: " << weaponData.name << " (persists until action menu cancel)" << std::endl;
            
            // Update backup so drop persists when closing inventory
            originalInventory = unit.inventory;
            originalEquippedIndex = unit.equippedItemIndex;
            
            // Adjust selection if needed
            if (selectedInventoryIndex >= (int)unit.inventory.size() + 1) {
                selectedInventoryIndex = unit.inventory.size();
            }
        }
        showDropConfirmation = false;
        return;
    }
    
    if (selectedInventoryIndex < (int)unit.inventory.size()) {
        // Check if unit can wield this weapon
        WeaponData weaponData = GetWeaponData(unit.inventory[selectedInventoryIndex]);
        if (CanUnitWieldWeapon(unit, weaponData)) {
            // Equip item - update backup immediately
            unit.equippedItemIndex = selectedInventoryIndex;
            originalEquippedIndex = selectedInventoryIndex;
            std::cout << "Equipped: " << weaponData.name << std::endl;
        } else {
            std::cout << "Cannot equip " << weaponData.name << " - " << unit.name << " cannot wield " << weaponData.type << "s" << std::endl;
        }
    } else if (selectedInventoryIndex == (int)unit.inventory.size()) {
        // Show drop confirmation
        if (unit.equippedItemIndex >= 0 && unit.equippedItemIndex < (int)unit.inventory.size()) {
            showDropConfirmation = true;
            std::cout << "Confirming drop..." << std::endl;
        }
    }
}

WeaponData MapManager::GetWeaponData(const std::string& weaponId) const {
    WeaponData weaponData;
    weaponData.id = weaponId;
    weaponData.name = weaponId;  // Default to ID if not found
    
    // New structure: { "generic": { "sword": [...], "axe": [...] }, "prf": { "sword": [...] } }
    // Search in generic weapons (organized by weapon type)
    if (weaponsData.contains("generic") && weaponsData["generic"].is_object()) {
        for (auto& [weaponType, weaponArray] : weaponsData["generic"].items()) {
            if (weaponArray.is_array()) {
                for (const auto& weapon : weaponArray) {
                    if (weapon.value("id", "") == weaponId) {
                        weaponData.name = weapon.value("name", weaponId);
                        weaponData.type = weaponType; // Type is the key (sword, axe, anima, etc.)
                        weaponData.might = weapon.value("might", 0);
                        weaponData.hit = weapon.value("hit", 0);
                        weaponData.crit = weapon.value("crit", 0);
                        weaponData.weight = weapon.value("weight", 0);
                        weaponData.durability = weapon.contains("durability") && weapon["durability"].is_null() ? -1 : weapon.value("durability", 0);
                        if (weapon.contains("range") && weapon["range"].is_array()) {
                            for (const auto& r : weapon["range"]) {
                                weaponData.range.push_back(r.get<int>());
                            }
                        }
                        weaponData.isPRF = false;
                        return weaponData;
                    }
                }
            }
        }
    }
    
    // Search in PRF weapons (organized by weapon type)
    if (weaponsData.contains("prf") && weaponsData["prf"].is_object()) {
        for (auto& [weaponType, weaponArray] : weaponsData["prf"].items()) {
            if (weaponArray.is_array()) {
                for (const auto& weapon : weaponArray) {
                    if (weapon.value("id", "") == weaponId) {
                        weaponData.name = weapon.value("name", weaponId);
                        weaponData.type = weaponType; // Type is the key (sword, dark, stone, etc.)
                        weaponData.might = weapon.value("might", 0);
                        weaponData.hit = weapon.value("hit", 0);
                        weaponData.crit = weapon.value("crit", 0);
                        weaponData.weight = weapon.value("weight", 0);
                        weaponData.durability = weapon.contains("durability") && weapon["durability"].is_null() ? -1 : weapon.value("durability", 0);
                        if (weapon.contains("range") && weapon["range"].is_array()) {
                            for (const auto& r : weapon["range"]) {
                                weaponData.range.push_back(r.get<int>());
                            }
                        }
                        weaponData.user = weapon.value("user", "");
                        weaponData.isPRF = true;
                        return weaponData;
                    }
                }
            }
        }
    }
    
    // Search in attributed weapons (if exists - organized by weapon type)
    if (weaponsData.contains("attributed") && weaponsData["attributed"].is_object()) {
        for (auto& [weaponType, weaponArray] : weaponsData["attributed"].items()) {
            if (weaponArray.is_array()) {
                for (const auto& weapon : weaponArray) {
                    if (weapon.value("id", "") == weaponId) {
                        weaponData.name = weapon.value("name", weaponId);
                        weaponData.type = weaponType;
                        weaponData.might = weapon.value("might", 0);
                        weaponData.hit = weapon.value("hit", 0);
                        weaponData.crit = weapon.value("crit", 0);
                        weaponData.weight = weapon.value("weight", 0);
                        weaponData.durability = weapon.contains("durability") && weapon["durability"].is_null() ? -1 : weapon.value("durability", 0);
                        if (weapon.contains("range") && weapon["range"].is_array()) {
                            for (const auto& r : weapon["range"]) {
                                weaponData.range.push_back(r.get<int>());
                            }
                        }
                        weaponData.isPRF = false;
                        return weaponData;
                    }
                }
            }
        }
    }
    
    return weaponData;
}

bool MapManager::CanUnitWieldWeapon(const MapUnit& unit, const WeaponData& weapon) const {
    // Check if it's a PRF weapon
    if (weapon.isPRF && !weapon.user.empty()) {
        return weapon.user == unit.unitId;
    }
    
    // Need to search by display name or store the class ID separately
    // For now, search through all classes to find one with matching display name
    for (auto& [classId, classArray] : classesData.items()) {
        if (classArray.is_array() && !classArray.empty()) {
            std::string displayName = classArray[0].value("name", "");
            if (displayName == unit.className && classArray[0].contains("weapon_types")) {
                const auto& weaponTypes = classArray[0]["weapon_types"];
                if (weaponTypes.is_array()) {
                    for (const auto& wType : weaponTypes) {
                        if (wType.get<std::string>() == weapon.type) {
                            return true;
                        }
                    }
                }
            }
        }
    }
    
    return false;
}

std::string MapManager::GetClassDisplayName(const std::string& classId) const {
    if (classesData.contains(classId) && classesData[classId].is_array()) {
        const auto& classArray = classesData[classId];
        if (!classArray.empty() && classArray[0].contains("name")) {
            return classArray[0]["name"].get<std::string>();
        }
    }
    return classId; // Fallback to ID if not found
}

void MapManager::ToggleUnitInfo() {
    if (showUnitInfo) {
        // Close info panel
        showUnitInfo = false;
        unitInfoIndex = -1;
    } else {
        // Open info panel for unit at cursor
        int unitIndex = GetUnitAtPosition(cursorX, cursorY);
        if (unitIndex >= 0) {
            showUnitInfo = true;
            unitInfoIndex = unitIndex;
            std::cout << "Showing info for: " << units[unitIndex].name << std::endl;
        }
    }
}

} // namespace Lehran
