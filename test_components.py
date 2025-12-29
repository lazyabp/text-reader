# Test script to validate the text-to-speech application components
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from services.file_service import FileService
from services.config_service import ConfigService
from controllers.main_controller import MainController
from utils.text_processing import split_text_by_sentences, sanitize_for_tts

def test_file_service():
    print("Testing FileService...")
    
    # Create a test file
    test_file_path = "test_sample.txt"
    
    # Initialize file service
    fs = FileService()
    
    # Test loading the file
    fs.load_file(test_file_path)
    
    # Test reading at position
    chunk = fs.read_chunk_at_position(0, 100)
    print(f"Read first 100 chars: '{chunk[:50]}...'")
    
    # Test file size
    size = fs.get_file_size()
    print(f"File size: {size} bytes")
    
    # Test reading around position
    context, rel_pos = fs.get_text_around_position(50, 50)
    print(f"Text around pos 50: '{context}'")
    
    fs.close_file()
    print("FileService test completed.\n")


def test_config_service():
    print("Testing ConfigService...")
    
    cs = ConfigService()
    
    # Test loading default config
    config = cs.load_config()
    print(f"Default config loaded: {config}")
    
    # Test updating TTS params
    cs.update_tts_params(rate=1.2, pitch=0.9, volume=0.8)
    updated_params = cs.get_tts_params()
    print(f"Updated TTS params: {updated_params}")
    
    # Test setting last position
    cs.set_last_position("test.txt", 1234)
    last_pos = cs.get_last_position("test.txt")
    print(f"Last position for test.txt: {last_pos}")
    
    print("ConfigService test completed.\n")


def test_text_processing():
    print("Testing text processing utilities...")
    
    sample_text = "Hello world! This is a test sentence. How are you today?"
    
    # Test sentence splitting
    sentences = split_text_by_sentences(sample_text)
    print(f"Split sentences: {sentences}")
    
    # Test sanitization
    dirty_text = "Dr. Smith went to the U.S.A. last week."
    clean_text = sanitize_for_tts(dirty_text)
    print(f"Sanitized: '{dirty_text}' -> '{clean_text}'")
    
    print("Text processing test completed.\n")


def main():
    print("Running Text-to-Speech Application Component Tests\n")
    
    test_file_service()
    test_config_service()
    test_text_processing()
    
    print("All component tests completed!")


if __name__ == "__main__":
    main()