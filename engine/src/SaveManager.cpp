/**
 * SaveManager.cpp
 * Implementation of save system with dual JSON/Binary support
 */

#include "SaveManager.hpp"
#include <fstream>
#include <sstream>
#include <cstring>
#include <filesystem>
#include <iostream>

#ifdef _WIN32
#include <windows.h>
#include <shlobj.h>
#else
#include <pwd.h>
#include <unistd.h>
#endif

namespace fs = std::filesystem;

namespace Lehran {

// ============================================================================
// SaveData Implementation
// ============================================================================

SaveData::SaveData()
    : version(1)
    , checksum(0)
    , timestamp(std::time(nullptr))
    , slot_name("New Save")
    , current_chapter(0)
    , turn_count(0)
    , difficulty(1)
    , permadeath_enabled(true)
    , casual_mode(false)
    , gold(0)
    , is_mid_battle(false)
{
}

json SaveData::to_json() const {
    json j;
    j["version"] = version;
    j["timestamp"] = timestamp;
    j["slot_name"] = slot_name;
    j["current_chapter"] = current_chapter;
    j["turn_count"] = turn_count;
    j["difficulty"] = difficulty;
    j["permadeath_enabled"] = permadeath_enabled;
    j["casual_mode"] = casual_mode;
    j["gold"] = gold;
    j["is_mid_battle"] = is_mid_battle;
    j["current_map"] = current_map;
    
    // Units
    j["units"] = json::array();
    for (const auto& unit : units) {
        j["units"].push_back(unit.to_json());
    }
    
    // Flags and variables
    j["event_flags"] = event_flags;
    j["variables"] = variables;
    j["support_levels"] = support_levels;
    
    // Convoy
    j["convoy"] = json::array();
    for (const auto& item : convoy) {
        j["convoy"].push_back(item.to_json());
    }
    
    // Unit positions
    j["unit_positions"] = json::array();
    for (const auto& pos : unit_positions) {
        j["unit_positions"].push_back({
            {"unit_id", pos.first},
            {"x", pos.second.first},
            {"y", pos.second.second}
        });
    }
    
    return j;
}

void SaveData::from_json(const json& j) {
    version = j.value("version", 1);
    timestamp = j.value("timestamp", std::time(nullptr));
    slot_name = j.value("slot_name", "");
    current_chapter = j.value("current_chapter", 0);
    turn_count = j.value("turn_count", 0);
    difficulty = j.value("difficulty", 1);
    permadeath_enabled = j.value("permadeath_enabled", true);
    casual_mode = j.value("casual_mode", false);
    gold = j.value("gold", 0);
    is_mid_battle = j.value("is_mid_battle", false);
    current_map = j.value("current_map", "");
    
    // Load units
    units.clear();
    if (j.contains("units")) {
        for (const auto& unit_json : j["units"]) {
            UnitSaveData unit;
            unit.from_json(unit_json);
            units.push_back(unit);
        }
    }
    
    // Load flags and variables
    if (j.contains("event_flags")) {
        event_flags = j["event_flags"].get<std::map<std::string, bool>>();
    }
    if (j.contains("variables")) {
        variables = j["variables"].get<std::map<std::string, int>>();
    }
    if (j.contains("support_levels")) {
        support_levels = j["support_levels"].get<std::map<std::string, int>>();
    }
    
    // Load convoy
    convoy.clear();
    if (j.contains("convoy")) {
        for (const auto& item_json : j["convoy"]) {
            ItemData item;
            item.from_json(item_json);
            convoy.push_back(item);
        }
    }
    
    // Load unit positions
    unit_positions.clear();
    if (j.contains("unit_positions")) {
        for (const auto& pos : j["unit_positions"]) {
            std::string unit_id = pos["unit_id"];
            int x = pos["x"];
            int y = pos["y"];
            unit_positions.push_back({unit_id, {x, y}});
        }
    }
}

// ============================================================================
// UnitSaveData Implementation
// ============================================================================

json UnitSaveData::to_json() const {
    json j;
    j["character_id"] = character_id;
    j["unit_name"] = unit_name;
    j["class_name"] = class_name;
    j["level"] = level;
    j["experience"] = experience;
    j["hp_current"] = hp_current;
    j["hp_max"] = hp_max;
    j["str"] = str;
    j["mag"] = mag;
    j["skl"] = skl;
    j["spd"] = spd;
    j["lck"] = lck;
    j["def"] = def;
    j["res"] = res;
    j["is_alive"] = is_alive;
    j["is_recruited"] = is_recruited;
    j["status_effects"] = status_effects;
    
    j["inventory"] = json::array();
    for (const auto& item : inventory) {
        j["inventory"].push_back(item.to_json());
    }
    
    return j;
}

void UnitSaveData::from_json(const json& j) {
    character_id = j.value("character_id", "");
    unit_name = j.value("unit_name", "");
    class_name = j.value("class_name", "");
    level = j.value("level", 1);
    experience = j.value("experience", 0);
    hp_current = j.value("hp_current", 20);
    hp_max = j.value("hp_max", 20);
    str = j.value("str", 5);
    mag = j.value("mag", 0);
    skl = j.value("skl", 5);
    spd = j.value("spd", 5);
    lck = j.value("lck", 0);
    def = j.value("def", 5);
    res = j.value("res", 0);
    is_alive = j.value("is_alive", true);
    is_recruited = j.value("is_recruited", false);
    
    if (j.contains("status_effects")) {
        status_effects = j["status_effects"].get<std::vector<std::string>>();
    }
    
    inventory.clear();
    if (j.contains("inventory")) {
        for (const auto& item_json : j["inventory"]) {
            ItemData item;
            item.from_json(item_json);
            inventory.push_back(item);
        }
    }
}

// ============================================================================
// ItemData Implementation
// ============================================================================

json ItemData::to_json() const {
    json j;
    j["item_id"] = item_id;
    j["uses_remaining"] = uses_remaining;
    j["is_equipped"] = is_equipped;
    return j;
}

void ItemData::from_json(const json& j) {
    item_id = j.value("item_id", "");
    uses_remaining = j.value("uses_remaining", 0);
    is_equipped = j.value("is_equipped", false);
}

// ============================================================================
// SaveManager Implementation
// ============================================================================

SaveManager::SaveManager() {
    ensure_save_directory();
}

SaveManager::~SaveManager() {
}

bool SaveManager::save(const SaveData& data, int slot_number, bool use_json) {
    // Determine format based on build type
#ifdef _DEBUG
    use_json = true; // Always use JSON in debug builds
#endif
    
    std::string path = get_slot_path(slot_number, use_json);
    
    // Create backup of existing save
    if (fs::exists(path)) {
        backup_slot(slot_number);
    }
    
    // Save in appropriate format
    bool success = use_json ? save_json(data, path) : save_binary(data, path);
    
    if (success) {
        std::cout << "Save successful: " << path << std::endl;
    } else {
        std::cerr << "Save failed: " << path << std::endl;
    }
    
    return success;
}

bool SaveManager::load(int slot_number, SaveData& data) {
    // Try JSON first (debug format)
    std::string json_path = get_slot_path(slot_number, true);
    if (fs::exists(json_path)) {
        return load_json(json_path, data);
    }
    
    // Try binary format
    std::string bin_path = get_slot_path(slot_number, false);
    if (fs::exists(bin_path)) {
        return load_binary(bin_path, data);
    }
    
    std::cerr << "No save file found for slot " << slot_number << std::endl;
    return false;
}

bool SaveManager::slot_exists(int slot_number) const {
    std::string json_path = get_slot_path(slot_number, true);
    std::string bin_path = get_slot_path(slot_number, false);
    return fs::exists(json_path) || fs::exists(bin_path);
}

bool SaveManager::get_slot_info(int slot_number, std::string& slot_name, time_t& timestamp) {
    SaveData data;
    if (!load(slot_number, data)) {
        return false;
    }
    slot_name = data.slot_name;
    timestamp = data.timestamp;
    return true;
}

bool SaveManager::delete_slot(int slot_number) {
    bool deleted = false;
    
    std::string json_path = get_slot_path(slot_number, true);
    if (fs::exists(json_path)) {
        fs::remove(json_path);
        deleted = true;
    }
    
    std::string bin_path = get_slot_path(slot_number, false);
    if (fs::exists(bin_path)) {
        fs::remove(bin_path);
        deleted = true;
    }
    
    return deleted;
}

bool SaveManager::backup_slot(int slot_number) {
    std::string json_path = get_slot_path(slot_number, true);
    std::string bin_path = get_slot_path(slot_number, false);
    std::string backup_path = get_backup_path(slot_number);
    
    try {
        if (fs::exists(json_path)) {
            fs::copy_file(json_path, backup_path + ".json", fs::copy_options::overwrite_existing);
            return true;
        }
        if (fs::exists(bin_path)) {
            fs::copy_file(bin_path, backup_path + ".sav", fs::copy_options::overwrite_existing);
            return true;
        }
    } catch (const std::exception& e) {
        std::cerr << "Backup failed: " << e.what() << std::endl;
    }
    
    return false;
}

bool SaveManager::restore_backup(int slot_number) {
    std::string backup_json = get_backup_path(slot_number) + ".json";
    std::string backup_bin = get_backup_path(slot_number) + ".sav";
    
    try {
        if (fs::exists(backup_json)) {
            std::string dest = get_slot_path(slot_number, true);
            fs::copy_file(backup_json, dest, fs::copy_options::overwrite_existing);
            return true;
        }
        if (fs::exists(backup_bin)) {
            std::string dest = get_slot_path(slot_number, false);
            fs::copy_file(backup_bin, dest, fs::copy_options::overwrite_existing);
            return true;
        }
    } catch (const std::exception& e) {
        std::cerr << "Restore failed: " << e.what() << std::endl;
    }
    
    return false;
}

bool SaveManager::export_to_json(int slot_number, const std::string& output_path) {
    SaveData data;
    if (!load(slot_number, data)) {
        return false;
    }
    return save_json(data, output_path);
}

bool SaveManager::import_from_json(const std::string& input_path, int slot_number) {
    SaveData data;
    if (!load_json(input_path, data)) {
        return false;
    }
    return save(data, slot_number, false); // Save as binary
}

std::string SaveManager::get_save_directory() const {
    return save_directory_;
}

// ============================================================================
// Private Methods
// ============================================================================

std::string SaveManager::get_slot_path(int slot_number, bool is_json) const {
    std::string filename;
    
    if (slot_number == -1) {
        filename = "autosave";
    } else if (slot_number == -2) {
        filename = "suspend";
    } else {
        filename = "save_slot_" + std::to_string(slot_number);
    }
    
    filename += is_json ? ".json" : ".sav";
    
    return save_directory_ + "/" + filename;
}

std::string SaveManager::get_backup_path(int slot_number) const {
    std::string filename;
    
    if (slot_number == -1) {
        filename = "autosave_backup";
    } else if (slot_number == -2) {
        filename = "suspend_backup";
    } else {
        filename = "save_slot_" + std::to_string(slot_number) + "_backup";
    }
    
    return save_directory_ + "/" + filename;
}

bool SaveManager::save_json(const SaveData& data, const std::string& path) {
    try {
        json j = data.to_json();
        
        std::ofstream file(path);
        if (!file.is_open()) {
            return false;
        }
        
        file << j.dump(2); // Pretty print with 2-space indent
        file.close();
        
        return true;
    } catch (const std::exception& e) {
        std::cerr << "JSON save error: " << e.what() << std::endl;
        return false;
    }
}

bool SaveManager::load_json(const std::string& path, SaveData& data) {
    try {
        std::ifstream file(path);
        if (!file.is_open()) {
            return false;
        }
        
        json j;
        file >> j;
        file.close();
        
        data.from_json(j);
        
        return true;
    } catch (const std::exception& e) {
        std::cerr << "JSON load error: " << e.what() << std::endl;
        return false;
    }
}

bool SaveManager::save_binary(const SaveData& data, const std::string& path) {
    try {
        std::vector<uint8_t> buffer;
        
        // Write magic number
        write_uint32(buffer, MAGIC_NUMBER);
        
        // Write version
        write_uint32(buffer, SAVE_VERSION);
        
        // Serialize data to JSON first, then convert to binary
        json j = data.to_json();
        std::string json_str = j.dump();
        
        // Write data
        write_string(buffer, json_str);
        
        // Calculate and write checksum
        uint32_t checksum = calculate_checksum(buffer);
        write_uint32(buffer, checksum);
        
        // Encrypt
        encrypt_data(buffer);
        
        // Write to file
        std::ofstream file(path, std::ios::binary);
        if (!file.is_open()) {
            return false;
        }
        
        file.write(reinterpret_cast<const char*>(buffer.data()), buffer.size());
        file.close();
        
        return true;
    } catch (const std::exception& e) {
        std::cerr << "Binary save error: " << e.what() << std::endl;
        return false;
    }
}

bool SaveManager::load_binary(const std::string& path, SaveData& data) {
    try {
        // Read file
        std::ifstream file(path, std::ios::binary | std::ios::ate);
        if (!file.is_open()) {
            return false;
        }
        
        size_t file_size = file.tellg();
        file.seekg(0, std::ios::beg);
        
        std::vector<uint8_t> buffer(file_size);
        file.read(reinterpret_cast<char*>(buffer.data()), file_size);
        file.close();
        
        // Decrypt
        decrypt_data(buffer);
        
        // Read and verify header
        size_t offset = 0;
        uint32_t magic = read_uint32(buffer.data(), offset);
        if (magic != MAGIC_NUMBER) {
            std::cerr << "Invalid save file: bad magic number" << std::endl;
            return false;
        }
        
        uint32_t version = read_uint32(buffer.data(), offset);
        if (version > SAVE_VERSION) {
            std::cerr << "Save file version too new" << std::endl;
            return false;
        }
        
        // Read data
        std::string json_str = read_string(buffer.data(), offset);
        
        // Verify checksum
        uint32_t stored_checksum = read_uint32(buffer.data(), offset);
        // Note: In full implementation, recalculate and verify checksum
        
        // Parse JSON
        json j = json::parse(json_str);
        data.from_json(j);
        
        return true;
    } catch (const std::exception& e) {
        std::cerr << "Binary load error: " << e.what() << std::endl;
        return false;
    }
}

void SaveManager::encrypt_data(std::vector<uint8_t>& data) {
    // Simple XOR encryption (can be replaced with AES or similar)
    size_t key_len = sizeof(XOR_KEY);
    for (size_t i = 0; i < data.size(); i++) {
        data[i] ^= XOR_KEY[i % key_len];
    }
}

void SaveManager::decrypt_data(std::vector<uint8_t>& data) {
    // XOR is symmetric
    encrypt_data(data);
}

uint32_t SaveManager::calculate_checksum(const std::vector<uint8_t>& data) {
    // Simple checksum (can be replaced with CRC32 or similar)
    uint32_t sum = 0;
    for (uint8_t byte : data) {
        sum += byte;
        sum = (sum << 1) | (sum >> 31); // Rotate left
    }
    return sum;
}

// Binary serialization helpers
void SaveManager::write_uint32(std::vector<uint8_t>& buffer, uint32_t value) {
    buffer.push_back((value >> 0) & 0xFF);
    buffer.push_back((value >> 8) & 0xFF);
    buffer.push_back((value >> 16) & 0xFF);
    buffer.push_back((value >> 24) & 0xFF);
}

void SaveManager::write_int32(std::vector<uint8_t>& buffer, int32_t value) {
    write_uint32(buffer, static_cast<uint32_t>(value));
}

void SaveManager::write_string(std::vector<uint8_t>& buffer, const std::string& str) {
    write_uint32(buffer, static_cast<uint32_t>(str.length()));
    buffer.insert(buffer.end(), str.begin(), str.end());
}

void SaveManager::write_bool(std::vector<uint8_t>& buffer, bool value) {
    buffer.push_back(value ? 1 : 0);
}

uint32_t SaveManager::read_uint32(const uint8_t* data, size_t& offset) {
    uint32_t value = 0;
    value |= static_cast<uint32_t>(data[offset++]) << 0;
    value |= static_cast<uint32_t>(data[offset++]) << 8;
    value |= static_cast<uint32_t>(data[offset++]) << 16;
    value |= static_cast<uint32_t>(data[offset++]) << 24;
    return value;
}

int32_t SaveManager::read_int32(const uint8_t* data, size_t& offset) {
    return static_cast<int32_t>(read_uint32(data, offset));
}

std::string SaveManager::read_string(const uint8_t* data, size_t& offset) {
    uint32_t length = read_uint32(data, offset);
    std::string str(reinterpret_cast<const char*>(data + offset), length);
    offset += length;
    return str;
}

bool SaveManager::read_bool(const uint8_t* data, size_t& offset) {
    return data[offset++] != 0;
}

void SaveManager::ensure_save_directory() {
#ifdef _WIN32
    // Windows: %APPDATA%/LehranEngine/saves
    char path[MAX_PATH];
    if (SUCCEEDED(SHGetFolderPathA(NULL, CSIDL_APPDATA, NULL, 0, path))) {
        save_directory_ = std::string(path) + "/LehranEngine/saves";
    }
#elif __APPLE__
    // macOS: ~/Library/Application Support/LehranEngine/saves
    const char* home = getenv("HOME");
    if (home) {
        save_directory_ = std::string(home) + "/Library/Application Support/LehranEngine/saves";
    }
#else
    // Linux: ~/.local/share/LehranEngine/saves
    const char* home = getenv("HOME");
    if (home) {
        save_directory_ = std::string(home) + "/.local/share/LehranEngine/saves";
    }
#endif
    
    // Create directory if it doesn't exist
    try {
        fs::create_directories(save_directory_);
    } catch (const std::exception& e) {
        std::cerr << "Failed to create save directory: " << e.what() << std::endl;
    }
}

bool SaveManager::detect_format(const std::string& path) {
    // Check file extension
    if (path.size() >= 5 && path.substr(path.size() - 5) == ".json") {
        return true; // JSON
    }
    return false; // Binary
}

} // namespace Lehran
