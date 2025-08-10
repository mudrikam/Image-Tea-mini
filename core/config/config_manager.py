"""
Config Manager

Simple config manager for handling application configuration.
This provides compatibility with the API keys manager while integrating with the main config system.
"""

import json
import os
from pathlib import Path
from core.utils.logger import log, debug, warning, error, exception

class ConfigManager:
    """Simple config manager class"""
    
    def __init__(self, config_file_path=None, base_dir=None):
        """Initialize config manager"""
        if config_file_path:
            self.config_file = Path(config_file_path)
        elif base_dir:
            self.config_file = Path(base_dir) / "config.json"
        else:
            # Default fallback
            self.config_file = Path(__file__).parent.parent.parent / "config.json"
        
        self._config = None
        self.load()
    
    def load(self):
        """Load configuration from file"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self._config = json.load(f)
            else:
                warning(f"Config file not found: {self.config_file}")
                self._config = {}
        except Exception as e:
            exception(e, "Error loading config")
            self._config = {}
    
    def save(self):
        """Save configuration to file"""
        try:
            # Ensure directory exists
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self._config, f, indent=4, ensure_ascii=False)
            
            debug(f"Config saved to {self.config_file}")
        except Exception as e:
            exception(e, "Error saving config")
    
    def get(self, key, default=None):
        """Get configuration value"""
        if self._config is None:
            self.load()
        
        # Support nested keys with dot notation
        keys = key.split('.')
        value = self._config
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key, value):
        """Set configuration value"""
        if self._config is None:
            self.load()
        
        # Support nested keys with dot notation
        keys = key.split('.')
        config = self._config
        
        # Navigate to the parent of the target key
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        # Set the final value
        config[keys[-1]] = value
    
    def get_all(self):
        """Get all configuration data"""
        if self._config is None:
            self.load()
        return self._config
    
    def update(self, data):
        """Update configuration with new data"""
        if self._config is None:
            self.load()
        
        if isinstance(data, dict):
            self._config.update(data)
        else:
            raise ValueError("Data must be a dictionary")
    
    def reload(self):
        """Reload configuration from file"""
        self.load()

# Create a global instance for backward compatibility
config_manager = None

def initialize_config_manager(base_dir=None):
    """Initialize the global config manager with base directory"""
    global config_manager
    if config_manager is None:
        config_manager = ConfigManager(base_dir=base_dir)
    return config_manager

def get_config_manager():
    """Get the global config manager instance"""
    return config_manager
