#!/usr/bin/env python3
"""
Startup script for Homepage Editor
Handles privilege elevation and configuration validation
"""

import sys
import os
import subprocess
import platform
from pathlib import Path

def check_privileges():
    """Check if we have sufficient privileges"""
    # Check if we can write to the current directory
    try:
        test_file = Path("test_write.tmp")
        test_file.touch()
        test_file.unlink()
        return True
    except (PermissionError, OSError):
        return False

def elevate_privileges():
    """Attempt to elevate privileges using sudo"""
    if platform.system() not in ['Linux', 'Darwin']:
        print("Privilege elevation not supported on this platform")
        return False
    
    try:
        # Get the current script path
        script_path = Path(__file__).resolve()
        
        # Try to run with sudo
        cmd = ['sudo', sys.executable, str(script_path)]
        print(f"Attempting to run with elevated privileges: {' '.join(cmd)}")
        
        # Run the script with sudo
        subprocess.run(cmd, check=True)
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"Failed to elevate privileges: {e}")
        return False
    except FileNotFoundError:
        print("sudo command not found")
        return False

def main():
    """Main startup function"""
    print("Homepage Editor - Starting...")
    
    # Check if we have sufficient privileges
    if not check_privileges():
        print("Insufficient privileges detected.")
        print("Attempting to elevate privileges...")
        
        if not elevate_privileges():
            print("Failed to elevate privileges.")
            print("Please run the application with appropriate permissions.")
            print("You may need to run: sudo python homepage_gui.py")
            sys.exit(1)
        else:
            # If we successfully elevated, exit this process
            sys.exit(0)
    
    # Import and run the main application
    try:
        from homepage_gui import HomepageGUI
        import tkinter as tk
        
        print("Starting GUI application...")
        app = HomepageGUI()
        app.mainloop()
        
    except ImportError as e:
        print(f"Failed to import required modules: {e}")
        print("Please install required dependencies:")
        print("pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"Error starting application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()