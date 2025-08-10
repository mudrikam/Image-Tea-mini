import json
from pathlib import Path
from typing import Dict, Any

class ConfigManager:
    _instance = None
    _config = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ConfigManager, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._config is None:
            self.load_config()
    
    def load_config(self):
        """Load configuration from JSON file"""
        config_path = Path(__file__).parent.parent.parent / "config.json"
        with open(config_path, 'r', encoding='utf-8') as f:
            self._config = json.load(f)
    
    def save_config(self):
        """Save configuration to file"""
        config_path = Path(__file__).parent.parent.parent / "config.json"
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(self._config, f, indent=4, ensure_ascii=False)
    
    @property
    def config(self) -> Dict[str, Any]:
        """Get the full configuration"""
        return self._config
    
    @property
    def app_config(self) -> Dict[str, Any]:
        """Get application configuration"""
        return self._config['application']
    
    @property
    def window_config(self) -> Dict[str, Any]:
        """Get window configuration"""
        return self._config['window']
    
    @property
    def resources_config(self) -> Dict[str, Any]:
        """Get resources configuration"""
        return self._config['resources']
    
    @property
    def prompting_config(self) -> Dict[str, Any]:
        """Get prompting configuration"""
        return self._config['prompting']
    
    @property
    def current_platform(self) -> str:
        """Get current AI platform"""
        return self._config['prompting']['platform']
    
    @property
    def current_model(self) -> str:
        """Get current AI model"""
        return self._config['prompting']['current_model']
    
    def get_platform_config(self, platform: str = None) -> Dict[str, Any]:
        """Get configuration for specific platform"""
        if platform is None:
            platform = self.current_platform
        return self._config['prompting']['platforms'].get(platform, {})
    
    def get_available_platforms(self) -> Dict[str, Any]:
        """Get all available platforms"""
        return self._config['prompting']['platforms']
    
    def get_models_for_platform(self, platform: str) -> list:
        """Get available models for a platform"""
        platform_config = self.get_platform_config(platform)
        return platform_config.get('models', [])
    
    def get_supported_formats(self, platform: str = None) -> Dict[str, list]:
        """Get supported file formats for platform"""
        platform_config = self.get_platform_config(platform)
        return platform_config.get('supported_formats', {'images': [], 'videos': []})
    
    def update_platform_settings(self, platform: str, settings: Dict[str, Any]):
        """Update settings for a specific platform"""
        if platform in self._config['prompting']['platforms']:
            self._config['prompting']['platforms'][platform].update(settings)
    
    def set_current_platform(self, platform: str):
        """Set current active platform"""
        if platform in self._config['prompting']['platforms']:
            self._config['prompting']['platform'] = platform
    
    def set_current_model(self, model: str):
        """Set current active model"""
        self._config['prompting']['current_model'] = model
    
    def get_icon_path(self, base_dir: Path) -> Path:
        """Get the full icon path"""
        return base_dir / self.resources_config['icon_path']
    
    def get_api_keys(self, platform: str = None) -> list:
        """Get API keys for specific platform"""
        if platform is None:
            platform = self.current_platform
        return self._config['prompting']['api_keys'].get(platform, [])
    
    def get_active_api_key(self, platform: str = None) -> str:
        """Get first available API key for platform"""
        api_keys = self.get_api_keys(platform)
        return api_keys[0] if api_keys else ''
    
    def add_api_key(self, platform: str, key: str):
        """Add new API key for platform"""
        if platform not in self._config['prompting']['api_keys']:
            self._config['prompting']['api_keys'][platform] = []
        
        if key and key not in self._config['prompting']['api_keys'][platform]:
            self._config['prompting']['api_keys'][platform].append(key)
            self.save_config()  # Auto-save when adding keys
            return True
        return False
    
    def get_api_key_status(self, platform: str = None) -> Dict[str, str]:
        """Get API key status for platform"""
        if platform is None:
            platform = self.current_platform
        
        if 'api_key_status' not in self._config['prompting']:
            self._config['prompting']['api_key_status'] = {}
        
        if platform not in self._config['prompting']['api_key_status']:
            self._config['prompting']['api_key_status'][platform] = {}
        
        return self._config['prompting']['api_key_status'][platform]
    
    def set_api_key_status(self, platform: str, api_key: str, status: str):
        """Set status for specific API key"""
        if 'api_key_status' not in self._config['prompting']:
            self._config['prompting']['api_key_status'] = {}
        
        if platform not in self._config['prompting']['api_key_status']:
            self._config['prompting']['api_key_status'][platform] = {}
        
        self._config['prompting']['api_key_status'][platform][api_key] = status
        self.save_config()
    
    def remove_api_key(self, platform: str, key: str):
        """Remove API key"""
        api_keys = self.get_api_keys(platform)
        if key in api_keys:
            api_keys.remove(key)
            
            # Also remove status
            if 'api_key_status' in self._config['prompting']:
                if platform in self._config['prompting']['api_key_status']:
                    if key in self._config['prompting']['api_key_status'][platform]:
                        del self._config['prompting']['api_key_status'][platform][key]
    def remove_api_key(self, platform: str, key: str):
        """Remove API key"""
        api_keys = self.get_api_keys(platform)
        if key in api_keys:
            api_keys.remove(key)
            
            # Also remove status
            if 'api_key_status' in self._config['prompting']:
                if platform in self._config['prompting']['api_key_status']:
                    if key in self._config['prompting']['api_key_status'][platform]:
                        del self._config['prompting']['api_key_status'][platform][key]
            
            self.save_config()
            return True
        return False
    
    def get_next_api_key(self, platform: str = None, current_key: str = None) -> str:
        """Get next API key for rotation"""
        api_keys = self.get_api_keys(platform)
        if not api_keys:
            return ''
        
        if current_key and current_key in api_keys:
            current_index = api_keys.index(current_key)
            next_index = (current_index + 1) % len(api_keys)
            return api_keys[next_index]
        
        return api_keys[0]
    
    def get_platform_info(self, platform: str = None) -> Dict[str, Any]:
        """Get comprehensive platform information including models and formats"""
        if platform is None:
            platform = self.current_platform
        
        platform_config = self.get_platform_config(platform)
        
        return {
            'key': platform,
            'name': platform_config.get('name', 'Unknown Platform'),
            'models': platform_config.get('models', []),
            'default_model': platform_config.get('default_model', ''),
            'supported_formats': platform_config.get('supported_formats', {'images': [], 'videos': []}),
            'api_keys_count': len(self.get_api_keys(platform))
        }
    
    def get_test_model(self, platform: str = None) -> str:
        """Get the best model to use for API testing"""
        if platform is None:
            platform = self.current_platform
        
        platform_config = self.get_platform_config(platform)
        models = platform_config.get('models', [])
        
        if not models:
            return ''
        
        # For testing, prefer smaller/faster models
        if platform == "gemini":
            # Prefer flash models for testing
            for model in models:
                if 'flash' in model.lower():
                    return model
            return models[0]
        elif platform == "openai":
            # Prefer mini models for testing
            for model in models:
                if 'mini' in model.lower():
                    return model
            return models[0]
        
        # Default to first model
        return models[0]
        return models[0]
    
    def get_prompt_settings(self) -> Dict[str, Any]:
        """Get prompt generation settings"""
        return self._config['prompting'].get('settings', {})
    
    def update_prompt_settings(self, settings: Dict[str, Any]):
        """Update prompt generation settings"""
        if 'settings' not in self._config['prompting']:
            self._config['prompting']['settings'] = {}
        self._config['prompting']['settings'].update(settings)
        self.save_config()
    
    def get_title_length_range(self) -> tuple:
        """Get title length range (min, max)"""
        settings = self.get_prompt_settings()
        return (
            settings.get('title_min_length', 0),
            settings.get('title_max_length', 0)
        )
    
    def get_tags_count(self) -> int:
        """Get desired number of tags"""
        settings = self.get_prompt_settings()
        return settings.get('tags_count', 0)
    
    def get_description_max_length(self) -> int:
        """Get maximum description length"""
        settings = self.get_prompt_settings()
        return settings.get('description_max_length', 0)
    
    def get_mandatory_prompt(self) -> str:
        """Get mandatory JSON format prompt"""
        prompts = self.prompting_config.get('prompts', {})
        return prompts.get('mandatory_prompt', '')
    
    def get_raw_prompt(self, prompt_type: str = 'default_prompt') -> str:
        """Get raw prompt without any processing"""
        prompts = self.prompting_config.get('prompts', {})
        return prompts.get(prompt_type, '')
    
    def get_dynamic_prompt(self, prompt_type: str = 'default_prompt') -> str:
        """Get prompt with dynamic settings values inserted"""
        prompt_text = self.get_raw_prompt(prompt_type)
        
        if not prompt_text:
            return ''
        
        # Get current settings
        settings = self.get_prompt_settings()
        title_min = settings.get('title_min_length', 0)
        title_max = settings.get('title_max_length', 0)
        tags_count = settings.get('tags_count', 0)
        description_max = settings.get('description_max_length', 0)
        
        # Replace dynamic placeholders with current settings
        processed = prompt_text
        
        # Replace placeholders with current settings values
        processed = processed.replace("TITLE_LENGTH_PLACEHOLDER", f"{title_min}-{title_max}")
        processed = processed.replace("KEYWORDS_COUNT_PLACEHOLDER", str(tags_count))
        processed = processed.replace("DESCRIPTION_MAX_PLACEHOLDER", str(description_max))
        
        return processed

    def build_final_prompt(self) -> str:
        """Build final prompt with all components and dynamic settings"""
        # Get all prompt components - use dynamic for base and default, raw for others
        base_prompt = self.get_dynamic_prompt('base_prompt')
        default_prompt = self.get_dynamic_prompt('default_prompt')
        custom_prompt = self.get_dynamic_prompt('custom_prompt').strip()
        negative_prompt = self.get_raw_prompt('negative_prompt').strip()
        exclude_prompt = self.get_raw_prompt('exclude_prompt').strip()
        mandatory_prompt = self.get_raw_prompt('mandatory_prompt').strip()
        
        # Build final prompt
        final_prompt_parts = []
        
        if base_prompt:
            final_prompt_parts.append(base_prompt)
        
        if default_prompt:
            final_prompt_parts.append(default_prompt)
        
        if custom_prompt:
            final_prompt_parts.append(f"Additional instructions: {custom_prompt}")
        
        if negative_prompt:
            final_prompt_parts.append(f"Avoid: {negative_prompt}")
        
        if exclude_prompt:
            final_prompt_parts.append(f"Exclude: {exclude_prompt}")
        
        if mandatory_prompt:
            final_prompt_parts.append(mandatory_prompt)
        
        return "\n\n".join(final_prompt_parts)
    
# Global instance
config_manager = ConfigManager()
