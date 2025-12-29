#!/usr/bin/env python3
# Entry point for the Text-to-Speech Reader Application
"""
Text-to-Speech Reader Application

A Python application for reading text files aloud with Piper TTS,
featuring position tracking and adjustable parameters.
"""

import sys
import subprocess
from pathlib import Path


def check_piper_tts():
    """Check if Piper TTS is available in the system"""
    try:
        result = subprocess.run(['piper', '--version'], 
                                capture_output=True, 
                                text=True)
        return result.returncode == 0
    except FileNotFoundError:
        return False


def main():
    # Check if Piper TTS is available
    if not check_piper_tts():
        print("Warning: Piper TTS not found.")
        print("Please install Piper TTS from: https://github.com/rhasspy/piper")
        print("The application will run but TTS functionality will not work.")
        input("Press Enter to continue anyway...")
    
    # Add the src directory to the path
    src_path = Path(__file__).parent / "src"
    sys.path.insert(0, str(src_path))
    
    try:
        from main import main as run_app
        run_app()
    except ImportError as e:
        print(f"Error importing main application: {e}")
        input("Press Enter to exit...")
    except Exception as e:
        print(f"An error occurred while running the application: {e}")
        input("Press Enter to exit...")


if __name__ == "__main__":
    main()