import threading
import time
import platform
import psutil
from typing import Callable
import ctypes

class SystemMonitor:
    """
    Monitors system state to detect when to pause/resume the timer.
    Checks for lock screen, screensaver, and system sleep states.
    """
    def __init__(self, on_system_idle: Callable = None, on_system_active: Callable = None):
        self.on_system_idle = on_system_idle
        self.on_system_active = on_system_active
        self.is_running = False
        self.monitor_thread = None
        self.system_was_idle = False
        self.check_interval = 2  # seconds
        
    def start(self):
        """Start the system monitor."""
        if self.is_running:
            return

        self.is_running = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        
    def stop(self):
        """Stop the system monitor."""
        self.is_running = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=self.check_interval + 1)

    @staticmethod
    def _get_idle_duration():
        """Return system idle time in seconds (Windows only)."""
        class LASTINPUTINFO(ctypes.Structure):
            _fields_ = [("cbSize", ctypes.c_uint), ("dwTime", ctypes.c_uint)]

        last_input_info = LASTINPUTINFO()
        last_input_info.cbSize = ctypes.sizeof(LASTINPUTINFO)

        if ctypes.windll.user32.GetLastInputInfo(ctypes.byref(last_input_info)):
            millis = ctypes.windll.kernel32.GetTickCount() - last_input_info.dwTime
            return millis / 1000.0  # return seconds
        else:
            return 0
        
    def _is_system_idle(self):
        """Check if the system is currently idle (locked/screensaver/sleep)."""
        os_name = platform.system()

        if os_name == "Windows":
            try:
                idle_seconds = self._get_idle_duration()
                return idle_seconds > 300  # Consider idle after 5 minutes
            except Exception as e:
                print(f"[ERROR] Idle check failed on Windows: {e}")
                return False

        elif os_name == "Darwin":  # macOS
            # Placeholder for macOS implementation
            return False

        elif os_name == "Linux":
            # Placeholder for Linux implementation
            return False

        # Fallback method for unknown systems: check CPU usage
        try:
            cpu_percent = psutil.cpu_percent(interval=0.5)
            return cpu_percent < 1.0
        except Exception:
            return False
            
    def _monitor_loop(self):
        """Main monitoring loop running in a separate thread."""
        while self.is_running:
            try:
                is_idle_now = self._is_system_idle()

                # State transition from active to idle
                if is_idle_now and not self.system_was_idle:
                    if self.on_system_idle:
                        self.on_system_idle()

                # State transition from idle to active
                elif not is_idle_now and self.system_was_idle:
                    if self.on_system_active:
                        self.on_system_active()

                self.system_was_idle = is_idle_now

            except Exception as e:
                print(f"Error in system monitor: {e}")

            time.sleep(self.check_interval)
