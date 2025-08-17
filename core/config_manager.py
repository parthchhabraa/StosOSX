"""
Configuration Manager for StosOS
Handles application settings, API keys, and user preferences
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, Optional


class ConfigManager:
    """Manages application configuration and settings"""
    
    def __init__(self, config_dir: str = "config"):
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(exist_ok=True)
        
        self.config_file = self.config_dir / "stosos_config.json"
        self.logger = logging.getLogger(__name__)
        
        self._config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                self.logger.info("Configuration loaded successfully")
                return config
            except (json.JSONDecodeError, IOError) as e:
                self.logger.error(f"Failed to load config: {e}")
                return self._get_default_config()
        else:
            self.logger.info("No config file found, using defaults")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration values"""
        return {
            "app": {
                "name": "StosOS X",
                "version": "1.0.0",
                "debug": False
            },
            "display": {
                "brightness_levels": [20, 100],
                "idle_timeout_dim": 30,
                "idle_timeout_sleep": 60
            },
            "voice": {
                "wake_word": "hey stosos",
                "language": "en-US",
                "voice_speed": 150
            },
            "api_keys": {
                "google_calendar": "",
                "spotify_client_id": "",
                "spotify_client_secret": "",
                "openai_api_key": ""
            },
            "modules": {
                "calendar": {"enabled": True},
                "tasks": {"enabled": True},
                "smart_home": {"enabled": True},
                "voice_assistant": {"enabled": True},
                "idea_board": {"enabled": True},
                "study_tracker": {"enabled": True},
                "spotify": {"enabled": True}
            }
        }
    
    def save_config(self) -> bool:
        """Save current configuration to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self._config, f, indent=2)
            self.logger.info("Configuration saved successfully")
            return True
        except IOError as e:
            self.logger.error(f"Failed to save config: {e}")
            return False
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by dot-notation key"""
        keys = key.split('.')
        value = self._config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any) -> None:
        """Set configuration value by dot-notation key"""
        keys = key.split('.')
        config = self._config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
        self.logger.debug(f"Config updated: {key} = {value}")
    
    def get_api_key(self, service: str) -> Optional[str]:
        """Get API key for a specific service"""
        key = self.get(f"api_keys.{service}")
        return key if key else None
    
    def set_api_key(self, service: str, key: str) -> None:
        """Set API key for a specific service"""
        self.set(f"api_keys.{service}", key)
    
    def is_module_enabled(self, module_name: str) -> bool:
        """Check if a module is enabled"""
        return self.get(f"modules.{module_name}.enabled", False)