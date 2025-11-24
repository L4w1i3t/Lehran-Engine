"""
Settings Manager for Lehran Engine GUI
Handles user preferences persistence
"""

import os
import json
import logging

logger = logging.getLogger(__name__)


class SettingsManager:
    """Manages application settings and preferences"""
    
    def __init__(self):
        # Get settings directory
        self.settings_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'settings')
        self.settings_file = os.path.join(self.settings_dir, 'preferences.json')
        
        # Default settings
        self.default_settings = {
            'theme': 'system',  # light, dark, or system
            'window': {
                'width': 1400,
                'height': 900,
                'x': 100,
                'y': 100
            }
        }
        
        # Load or create settings
        self.settings = self.load_settings()
    
    def load_settings(self) -> dict:
        """Load settings from file, or create default settings if not found"""
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    loaded_settings = json.load(f)
                    # Merge with defaults to ensure all keys exist
                    settings = self.default_settings.copy()
                    settings.update(loaded_settings)
                    logger.info("Settings loaded successfully")
                    return settings
            else:
                logger.info("No settings file found, using defaults")
                return self.default_settings.copy()
        except Exception as e:
            logger.error(f"Error loading settings: {e}")
            return self.default_settings.copy()
    
    def save_settings(self) -> bool:
        """Save settings to file"""
        try:
            # Create settings directory if it doesn't exist
            os.makedirs(self.settings_dir, exist_ok=True)
            
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=2)
            
            logger.info("Settings saved successfully")
            return True
        except Exception as e:
            logger.error(f"Error saving settings: {e}")
            return False
    
    def get(self, key: str, default=None):
        """Get a setting value"""
        return self.settings.get(key, default)
    
    def set(self, key: str, value):
        """Set a setting value"""
        self.settings[key] = value
    
    def get_theme(self) -> str:
        """Get the current theme setting"""
        return self.settings.get('theme', 'system')
    
    def set_theme(self, theme: str):
        """Set the theme setting"""
        self.settings['theme'] = theme
        self.save_settings()
    
    def get_window_geometry(self) -> dict:
        """Get window geometry settings"""
        return self.settings.get('window', self.default_settings['window'])
    
    def set_window_geometry(self, x: int, y: int, width: int, height: int):
        """Save window geometry"""
        self.settings['window'] = {
            'x': x,
            'y': y,
            'width': width,
            'height': height
        }
        self.save_settings()
