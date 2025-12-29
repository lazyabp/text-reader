# Test script for the main controller
import sys
import os
import time
from threading import Event
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from services.file_service import FileService
from services.tts_service import TTSService
from services.config_service import ConfigService
from controllers.main_controller import MainController


def test_controller():
    print("Testing MainController...")
    
    # Create a test file if it doesn't exist
    test_file = "controller_test.txt"
    if not os.path.exists(test_file):
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write("This is a test file for the controller.\nIt has multiple lines.\nAnd different sentences! Does it work? Yes, it should work.")
    
    # Initialize services
    file_service = FileService()
    tts_service = TTSService()
    
    # Mock the TTS service to avoid actual audio synthesis during test
    original_speak_text = tts_service.speak_text
    def mock_speak_text(text):
        print(f"TTS would speak: '{text[:50]}...'")
        time.sleep(0.1)  # Simulate some processing time
    
    tts_service.speak_text = mock_speak_text
    
    config_service = ConfigService()
    
    # Initialize controller
    controller = MainController(file_service, tts_service, config_service)
    
    # Test loading a file
    controller.load_file(test_file)
    print("File loaded successfully.")
    
    # Test position tracking
    pos = controller.get_current_position()
    print(f"Current position: {pos}")
    
    # Test starting playback (will be mocked)
    print("Starting playback from position 0...")
    controller.start_playback(0)
    
    # Wait a bit for the playback to start
    time.sleep(2)
    
    # Check if it's playing
    is_playing = controller.is_playing()
    print(f"Is playing: {is_playing}")
    
    # Pause playback
    controller.pause()
    print("Playback paused.")
    
    # Wait to ensure it's paused
    time.sleep(1)
    
    is_playing = controller.is_playing()
    print(f"Is playing after pause: {is_playing}")
    
    # Test setting position
    controller.set_position(50)
    print("Position set to 50.")
    
    # Get current position
    pos = controller.get_current_position()
    print(f"Current position after setting: {pos}")
    
    print("MainController test completed.\n")


def main():
    print("Running MainController Test\n")
    
    test_controller()
    
    print("All tests completed!")


if __name__ == "__main__":
    main()