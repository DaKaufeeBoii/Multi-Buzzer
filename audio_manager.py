import pygame
import os
import sys
import array
import math

class AudioManager:
    def __init__(self):
        try:
            # Use lower latency settings for buzzer response
            pygame.mixer.init(frequency=44100, size=-16, channels=1, buffer=512)
            self.initialized = True
        except Exception as e:
            print(f"Audio initialization failed: {e}")
            self.initialized = False
        
        self.sounds = {}
        self.volume = 0.5 # Default volume 50%
        # Handle path for PyInstaller bundled assets
        if hasattr(sys, '_MEIPASS'):
            self.asset_dir = os.path.join(sys._MEIPASS, "assets")
        else:
            self.asset_dir = os.path.abspath("assets")
            
        if self.initialized:
            self.refresh_sounds()

    def refresh_sounds(self):
        """Loads sounds dynamically from assets folder filenames."""
        if not os.path.exists(self.asset_dir):
            print(f"Warning: Asset directory {self.asset_dir} not found.")
            return

        # Scan directory for audio files
        self.sounds = {}
        found_files = os.listdir(self.asset_dir)
        
        for filename in found_files:
            name, ext = os.path.splitext(filename)
            if ext.lower() in [".mp3", ".wav"]:
                file_path = os.path.join(self.asset_dir, filename)
                try:
                    self.sounds[name] = pygame.mixer.Sound(file_path)
                    print(f"Dynamically loaded: {name} from {filename}")
                except Exception as e:
                    print(f"Failed to load {file_path}: {e}")
        
        # If no files found, add a default Red with a beep
        if not self.sounds:
            print("No audio assets found. Adding default 'Red' beep.")
            self.sounds["Red"] = self._generate_fallback_beep()

    def get_available_colors(self):
        """Returns a list of names for which audio files were found."""
        return sorted(list(self.sounds.keys()))

    def _generate_fallback_beep(self):
        """Generates a simple fallback beep if file is missing."""
        if not self.initialized:
            return None
        
        frequency = 440
        duration = 0.2
        sample_rate = 44100
        n_samples = int(sample_rate * duration)
        buf = array.array('h', [0] * n_samples)
        amplitude = 32767 // 4 # Soft beep
        
        for i in range(n_samples):
            t = float(i) / sample_rate
            buf[i] = int(amplitude * math.sin(2.0 * math.pi * frequency * t))
            
        return pygame.mixer.Sound(buffer=buf.tobytes())
            
    def play_sound(self, color):
        if not self.initialized:
            return
            
        if color in self.sounds and self.sounds[color] is not None:
            try:
                self.sounds[color].play()
            except Exception as e:
                print(f"Error playing sound for {color}: {e}")
        else:
            # Try one last refresh in case file was just added
            self.refresh_sounds()
            if color in self.sounds and self.sounds[color] is not None:
                self.sounds[color].set_volume(self.volume)
                self.sounds[color].play()

    def set_volume(self, volume):
        """Sets the volume (0.0 to 1.0) and updates all loaded sounds."""
        self.volume = max(0.0, min(1.0, float(volume)))
        for sound in self.sounds.values():
            if sound:
                sound.set_volume(self.volume)

# Singleton instance
audio_manager = AudioManager()
