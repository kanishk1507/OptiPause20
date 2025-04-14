import os
import threading
import time
from pathlib import Path
from typing import Optional, List, Dict

try:
    import pygame
except ImportError:
    pygame = None

class AudioPlayer:
    """
    Audio player for focus and relaxation sounds.
    Uses pygame for audio playback.
    """
    def __init__(self, sound_dir: Optional[Path] = None):
        self.is_initialized = False
        self.currently_playing = None
        self.is_playing = False
        self.volume = 0.5  # 50% volume by default
        
        # Dictionary to store available sounds
        self.sounds: Dict[str, Dict] = {}
        
        if pygame is None:
            print("Warning: pygame not available. Audio playback disabled.")
            return
            
        try:
            pygame.mixer.init()
            self.is_initialized = True
            
            # Set up sound directory
            if sound_dir is None:
                # Default to resources/sounds in the application directory
                app_dir = Path(__file__).parents[2]  # Go up to app root
                self.sound_dir = app_dir / "resources" / "sounds"
            else:
                self.sound_dir = sound_dir
                
            # Load available sounds
            self._load_sounds()
            
        except Exception as e:
            print(f"Error initializing audio player: {e}")
            self.is_initialized = False
    
    def _load_sounds(self):
        """Load available sound files from the sound directory."""
        if not self.is_initialized or not self.sound_dir.exists():
            return
        
        sound_categories = {
            "focus": ["deep_focus", "concentration", "productivity"],
            "relax": ["nature", "ambient", "meditation"],
            "white_noise": ["white_noise", "brown_noise", "pink_noise"]
        }
        
        # Clear existing sounds
        self.sounds.clear()
        
        # Scan for sound files
        for sound_file in self.sound_dir.glob("*.mp3"):
            # Basic categorization based on filename
            category = "other"
            name = sound_file.stem.lower().replace("_", " ").title()
            
            for cat, keywords in sound_categories.items():
                if any(keyword in sound_file.stem.lower() for keyword in keywords):
                    category = cat
                    break
            
            # Add to sounds dictionary
            if category not in self.sounds:
                self.sounds[category] = {}
                
            self.sounds[category][name] = {
                "path": str(sound_file),
                "name": name,
                "duration": None  # We'll get this when loading the sound
            }
    
    def get_available_sounds(self) -> Dict:
        """Get a dictionary of available sounds by category."""
        return self.sounds
    
    def play(self, sound_name: str, loop: bool = True) -> bool:
        """
        Play a sound by name.
        
        Args:
            sound_name: The name of the sound to play
            loop: Whether to loop the sound
            
        Returns:
            bool: True if playback started successfully, False otherwise
        """
        if not self.is_initialized:
            return False
            
        # Stop any currently playing sound
        self.stop()
        
        # Find the sound
        sound_info = None
        for category in self.sounds.values():
            if sound_name in category:
                sound_info = category[sound_name]
                break
                
        if not sound_info:
            print(f"Sound '{sound_name}' not found")
            return False