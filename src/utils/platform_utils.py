import platform
import sys
import os

def get_platform():
    """Get the current platform name."""
    system = platform.system()
    if system == "Windows":
        return "windows"
    elif system == "Darwin":
        return "macos"
    elif system == "Linux":
        return "linux"
    else:
        return "unknown"

def is_windows():
    """Check if the platform is Windows."""
    return platform.system() == "Windows"

def is_macos():
    """Check if the platform is macOS."""
    return platform.system() == "Darwin"

def is_linux():
    """Check if the platform is Linux."""
    return platform.system() == "Linux"

def get_app_data_dir():
    """Get the appropriate application data directory for the current platform."""
    if is_windows():
        # Use %APPDATA% on Windows
        return os.path.join(os.environ.get('APPDATA', ''), 'EyeCareApp')
    elif is_macos():
        # Use ~/Library/Application Support on macOS
        return os.path.join(os.path.expanduser('~'), 'Library', 'Application Support', 'EyeCareApp')
    else:
        # Use ~/.config on Linux/Unix
        return os.path.join(os.path.expanduser('~'), '.config', 'EyeCareApp')

def setup_autostart(enable=True):
    """Configure application to start automatically with the system."""
    app_path = sys.executable
    
    if is_windows():
        import winreg
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, 
                               winreg.KEY_SET_VALUE) as key:
                if enable:
                    winreg.SetValueEx(key, "EyeCareApp", 0, winreg.REG_SZ, f'"{app_path}"')
                else:
                    try:
                        winreg.DeleteValue(key, "EyeCareApp")
                    except FileNotFoundError:
                        pass
            return True
        except Exception as e:
            print(f"Error setting autostart: {e}")
            return False
            