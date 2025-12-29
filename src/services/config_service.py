# Configuration service for managing app settings
import json
import os
from pathlib import Path


class ConfigService:
    def __init__(self, config_file_path="config/app_config.json"):
        self.config_file_path = Path(config_file_path)
        self.config_dir = self.config_file_path.parent
        self.config_dir.mkdir(exist_ok=True)
        
        # Initialize with default values
        self.default_config = {
            "tts_params": {
                "rate": 1.0,
                "pitch": 1.0,
                "volume": 1.0,
                "voice_model": ""  # Default to empty, user needs to specify
            },
            "last_positions": {}
        }
    
    def load_config(self):
        """Load configuration from file"""
        if self.config_file_path.exists():
            try:
                with open(self.config_file_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    # Merge with defaults to ensure all keys exist
                    return self._merge_defaults(config)
            except (json.JSONDecodeError, IOError):
                # Return default config if file is corrupted
                return self.default_config.copy()
        else:
            # Return default config if file doesn't exist
            return self.default_config.copy()
    
    def save_config(self, config_data):
        """Save configuration to file"""
        try:
            # Create directory if it doesn't exist
            self.config_dir.mkdir(parents=True, exist_ok=True)
            
            with open(self.config_file_path, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)
        except IOError as e:
            raise IOError(f"Could not save configuration: {e}")
    
    def _merge_defaults(self, config):
        """Merge loaded config with defaults to ensure all keys exist"""
        merged = self.default_config.copy()
        
        # Merge TTS params
        if "tts_params" in config:
            merged["tts_params"].update(config["tts_params"])
        
        # Merge last positions
        if "last_positions" in config:
            merged["last_positions"].update(config["last_positions"])
        
        return merged
    
    def get_last_position(self, file_path):
        """Get the last reading position for a specific file"""
        config = self.load_config()
        file_path_str = str(Path(file_path).resolve())
        return config.get("last_positions", {}).get(file_path_str)
    
    def set_last_position(self, file_path, position):
        """Set the last reading position for a specific file"""
        config = self.load_config()
        file_path_str = str(Path(file_path).resolve())
        config["last_positions"][file_path_str] = position
        self.save_config(config)
    
    def remove_last_position(self, file_path):
        """Remove the last reading position for a specific file"""
        config = self.load_config()
        file_path_str = str(Path(file_path).resolve())
        if file_path_str in config.get("last_positions", {}):
            del config["last_positions"][file_path_str]
            self.save_config(config)
    
    def update_tts_params(self, **params):
        """Update TTS parameters"""
        config = self.load_config()
        config["tts_params"].update(params)
        self.save_config(config)
    
    def get_tts_params(self):
        """Get current TTS parameters"""
        config = self.load_config()
        return config.get("tts_params", {})