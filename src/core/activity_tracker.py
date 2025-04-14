import threading
from pynput import mouse, keyboard
from typing import Callable

class ActivityTracker:
    """
    Tracks keyboard and mouse activity to determine if the user is active.
    """
    def __init__(self, on_activity: Callable = None):
        self.on_activity = on_activity
        self.mouse_listener = None
        self.keyboard_listener = None
        self.is_running = False
        
    def start(self):
        """Start tracking user activity."""
        if self.is_running:
            return
            
        self.is_running = True
        
        # Start mouse listener in a separate thread
        self.mouse_listener = mouse.Listener(
            on_move=self._on_mouse_move,
            on_click=self._on_mouse_click,
            on_scroll=self._on_mouse_scroll
        )
        self.mouse_listener.daemon = True
        self.mouse_listener.start()
        
        # Start keyboard listener in a separate thread
        self.keyboard_listener = keyboard.Listener(
            on_press=self._on_key_press,
            on_release=self._on_key_release
        )
        self.keyboard_listener.daemon = True
        self.keyboard_listener.start()
    
    def stop(self):
        """Stop tracking user activity."""
        self.is_running = False
        
        if self.mouse_listener:
            self.mouse_listener.stop()
            self.mouse_listener = None
            
        if self.keyboard_listener:
            self.keyboard_listener.stop()
            self.keyboard_listener = None
    
    def _on_mouse_move(self, x, y):
        """Callback for mouse movement."""
        if self.is_running and self.on_activity:
            self.on_activity()
    
    def _on_mouse_click(self, x, y, button, pressed):
        """Callback for mouse clicks."""
        if self.is_running and pressed and self.on_activity:
            self.on_activity()
    
    def _on_mouse_scroll(self, x, y, dx, dy):
        """Callback for mouse scrolling."""
        if self.is_running and self.on_activity:
            self.on_activity()
    
    def _on_key_press(self, key):
        """Callback for keyboard key press."""
        if self.is_running and self.on_activity:
            self.on_activity()
    
    def _on_key_release(self, key):
        """Callback for keyboard key release."""
        # We only care about key presses for activity detection
        pass