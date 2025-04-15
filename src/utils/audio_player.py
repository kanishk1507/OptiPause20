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
        
        # Load and play the sound
        try:
            pygame.mixer.music.load(sound_info["path"])
            pygame.mixer.music.set_volume(self.volume)
            loops = -1 if loop else 0  # -1 means loop indefinitely
            pygame.mixer.music.play(loops)
            self.currently_playing = sound_name
            self.is_playing = True
            return True
        except Exception as e:
            print(f"Error playing sound: {e}")
            return False
    
    def stop(self):
        """Stop the currently playing sound."""
        if self.is_initialized and self.is_playing:
            pygame.mixer.music.stop()
            self.is_playing = False
            self.currently_playing = None
    
    def pause(self):
        """Pause the currently playing sound."""
        if self.is_initialized and self.is_playing:
            pygame.mixer.music.pause()
            self.is_playing = False
    
    def unpause(self):
        """Unpause the currently paused sound."""
        if self.is_initialized and not self.is_playing and self.currently_playing:
            pygame.mixer.music.unpause()
            self.is_playing = True
    
    def set_volume(self, volume: float):
        """
        Set the playback volume.
        
        Args:
            volume: Volume level between 0.0 and 1.0
        """
        if not self.is_initialized:
            return
            
        # Clamp volume between 0 and 1
        self.volume = max(0.0, min(1.0, volume))
        pygame.mixer.music.set_volume(self.volume)
    
    def get_volume(self) -> float:
        """Get the current volume level."""
        return self.volume
    
    def get_currently_playing(self) -> Optional[str]:
        """Get the name of the currently playing sound."""
        return self.currently_playing
    
    def is_sound_playing(self) -> bool:
        """Check if a sound is currently playing."""
        return self.is_playing
    
    def reload_sounds(self):
        """Reload sounds from the sound directory."""
        self._load_sounds()
    
    def set_sound_directory(self, sound_dir: Path):
        """
        Set a new sound directory and reload sounds.
        
        Args:
            sound_dir: Path to the directory containing sound files
        """
        self.sound_dir = sound_dir
        self.reload_sounds()


# Example usage
if __name__ == "__main__":
    # Create an AudioPlayer with custom sound directory
    custom_sound_dir = Path("./my_sounds")
    player = AudioPlayer(custom_sound_dir)
    
    # Get and print available sounds
    available_sounds = player.get_available_sounds()
    print("Available sounds:")
    for category, sounds in available_sounds.items():
        print(f"  {category.title()}:")
        for sound_name in sounds:
            print(f"    - {sound_name}")
    
    # Ask user which sound to play
    print("\nEnter the name of a sound to play:")
    sound_name = input("> ")
    
    # Play the selected sound
    if player.play(sound_name):
        print(f"Playing {sound_name}...")
        print("Press Ctrl+C to stop")
        try:
            while player.is_sound_playing():
                time.sleep(1)
        except KeyboardInterrupt:
            player.stop()
            print("\nStopped playback")
    else:
        print("Failed to play sound")