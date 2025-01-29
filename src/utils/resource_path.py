import os
import sys

def get_resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    
    # If we're running from PyInstaller build
    if hasattr(sys, '_MEIPASS'):
        # Strip src/ prefix since PyInstaller puts files in root of temp directory
        return os.path.join(base_path, relative_path.replace("src/", "", 1))
    # If we're running in development
    return os.path.join(base_path, relative_path)
