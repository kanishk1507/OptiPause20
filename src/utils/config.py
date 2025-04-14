import os
import json
from pathlib import Path

class Config:
    """Configuration manager for the application."""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        # Set up config directory
        self.config_dir = Path.home() / ".eyecare_app"
        os.makedirs(self.config_dir, exist_ok=True)
        
        self.config_file = self.config_dir / "config.json"
        
        # Default configuration
        self.defaults = {
            "work_duration": 1200,  # 20 minutes in seconds
            "break_duration": 20,    # 20 seconds
            "inactivity_threshold": 300,  # 5 minutes in seconds
            "notification_style": "center",
            "sound_enabled": False,
            "selected_sound": "none",
            "start_with_system": False,
            "minimize_to_tray": True
        }
        
        # Load config or create default
        self.config = self.load()
        self._initialized = True
    
    def load(self):
        """Load configuration from file."""
        if not self.config_file.exists():
            # Create default config
            self.save(self.defaults)
            return dict(self.defaults)
            
        try:
            with open(self.config_file, 'r') as f:
                config = json.load(f)
                
            # Ensure all default keys exist
            for key, value in self.defaults.items():
                if key not in config:
                    config[key] = value
                    
            return config
        except Exception as e:
            print(f"Error loading config: {e}")
            return dict(self.defaults)
    
    def save(self, config=None):
        """Save configuration to file."""
        if config is None:
            config = self.config
            
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def get(self, key, default=None):
        """Get a configuration value."""
        return self.config.get(key, default)
    
    def set(self, key, value):
        """Set a configuration value."""
        self.config[key] = value
        self.save()