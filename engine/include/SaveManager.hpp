/**
 * SaveManager.hpp
 * Handles save data serialization, encryption, and file I/O
 * Supports both JSON (debug) and encrypted binary (release) formats
 */

#pragma once

#include <string>
#include <vector>
#include <map>
#include <cstdint>
#include <ctime>
#include "json.hpp"

using json = nlohmann::json;

namespace Lehran {

// Forward declarations
struct UnitSaveData;
struct ItemData;

/**
 * Main save data structure
 */
struct SaveData {
    // Header information
    uint32_t version;                    // Save format version (for compatibility)
    uint32_t checksum;                   // Data integrity check
    time_t timestamp;                    // Last save time
    std::string slot_name;               // Display name (e.g., "Chapter 5 - Turn 12")
    
    // Game state
    int current_chapter;
    int turn_count;
    int difficulty;                      // 0=Easy, 1=Normal, 2=Hard, etc.
    bool permadeath_enabled;
    bool casual_mode;
    
    // Units (alive and dead)
    std::vector<UnitSaveData> units;
    
    // Event flags and variables
    std::map<std::string, bool> event_flags;      // Triggered events, recruitments, etc.
    std::map<std::string, int> variables;         // Numeric game variables
    std::map<std::string, int> support_levels;    // Character pair support levels
    
    // Inventory and resources
    std::vector<ItemData> convoy;        // Storage inventory
    int gold;
    
    // Battle state (for suspend saves)
    bool is_mid_battle;
    std::string current_map;
    std::vector<std::pair<std::string, std::pair<int, int>>> unit_positions; // unit_id -> (x, y)
    
    SaveData();
    json to_json() const;
    void from_json(const json& j);
};

/**
 * Individual unit save data
 */
struct UnitSaveData {
    std::string character_id;            // 8-digit character ID linking to story character
    std::string unit_name;
    std::string class_name;
    
    int level;
    int experience;
    
    // Current stats
    int hp_current;
    int hp_max;
    int str;
    int mag;
    int skl;
    int spd;
    int lck;
    int def;
    int res;
    
    // Status
    bool is_alive;                       // Critical for permadeath tracking
    bool is_recruited;
    std::vector<std::string> status_effects;
    
    // Inventory (item IDs)
    std::vector<ItemData> inventory;
    
    json to_json() const;
    void from_json(const json& j);
};

/**
 * Item/Weapon data in inventory
 */
struct ItemData {
    std::string item_id;                 // Weapon or item name
    int uses_remaining;                  // Durability
    bool is_equipped;                    // For weapons
    
    json to_json() const;
    void from_json(const json& j);
};

/**
 * Save file manager
 * Handles all save/load operations with format detection
 */
class SaveManager {
public:
    SaveManager();
    ~SaveManager();
    
    /**
     * Save data to file
     * @param data The save data to write
     * @param slot_number Save slot (0-4 for manual, -1 for autosave, -2 for suspend)
     * @param use_json Force JSON format (for debug builds)
     * @return true if successful
     */
    bool save(const SaveData& data, int slot_number, bool use_json = false);
    
    /**
     * Load data from file
     * @param slot_number Save slot to load from
     * @param data Output save data
     * @return true if successful
     */
    bool load(int slot_number, SaveData& data);
    
    /**
     * Check if a save slot exists
     */
    bool slot_exists(int slot_number) const;
    
    /**
     * Get save slot metadata without loading full data
     */
    bool get_slot_info(int slot_number, std::string& slot_name, time_t& timestamp);
    
    /**
     * Delete a save slot
     */
    bool delete_slot(int slot_number);
    
    /**
     * Create backup of current save
     */
    bool backup_slot(int slot_number);
    
    /**
     * Restore from backup
     */
    bool restore_backup(int slot_number);
    
    /**
     * Export save to JSON (for debugging)
     */
    bool export_to_json(int slot_number, const std::string& output_path);
    
    /**
     * Import save from JSON (for debugging)
     */
    bool import_from_json(const std::string& input_path, int slot_number);
    
    /**
     * Get save directory path
     */
    std::string get_save_directory() const;
    
private:
    std::string save_directory_;
    static constexpr uint32_t SAVE_VERSION = 1;
    static constexpr uint32_t MAGIC_NUMBER = 0x4C485246; // "LHRF" (Lehran Fire)
    
    // Encryption key (in real implementation, this should be more secure)
    static constexpr uint8_t XOR_KEY[] = {
        0x4C, 0x65, 0x68, 0x72, 0x61, 0x6E, 0x45, 0x6E,
        0x67, 0x69, 0x6E, 0x65, 0x46, 0x69, 0x72, 0x65
    };
    
    std::string get_slot_path(int slot_number, bool is_json) const;
    std::string get_backup_path(int slot_number) const;
    
    // Binary format operations
    bool save_binary(const SaveData& data, const std::string& path);
    bool load_binary(const std::string& path, SaveData& data);
    
    // JSON format operations
    bool save_json(const SaveData& data, const std::string& path);
    bool load_json(const std::string& path, SaveData& data);
    
    // Encryption/Decryption
    void encrypt_data(std::vector<uint8_t>& data);
    void decrypt_data(std::vector<uint8_t>& data);
    
    // Checksum calculation
    uint32_t calculate_checksum(const std::vector<uint8_t>& data);
    
    // Binary serialization helpers
    void write_uint32(std::vector<uint8_t>& buffer, uint32_t value);
    void write_int32(std::vector<uint8_t>& buffer, int32_t value);
    void write_string(std::vector<uint8_t>& buffer, const std::string& str);
    void write_bool(std::vector<uint8_t>& buffer, bool value);
    
    uint32_t read_uint32(const uint8_t* data, size_t& offset);
    int32_t read_int32(const uint8_t* data, size_t& offset);
    std::string read_string(const uint8_t* data, size_t& offset);
    bool read_bool(const uint8_t* data, size_t& offset);
    
    // Utility
    void ensure_save_directory();
    bool detect_format(const std::string& path);
};

} // namespace Lehran
