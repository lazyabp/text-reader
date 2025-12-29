# Main controller for coordinating the text-to-speech application
import threading
import sys
from pathlib import Path

# Add the src directory to the path to enable imports
sys.path.append(str(Path(__file__).parent.parent))

from utils.text_processing import split_text_by_sentences


class MainController:
    def __init__(self, file_service, tts_service, config_service):
        self.file_service = file_service
        self.tts_service = tts_service
        self.config_service = config_service
        self.playback_thread = None
        self.is_playing_flag = False
        self.stop_playback_event = threading.Event()
    
    def load_file(self, file_path):
        """Load a text file through the file service"""
        self.file_service.load_file(file_path)
    
    def is_playing(self):
        """Check if the application is currently playing audio"""
        return self.is_playing_flag
    
    def start_playback(self, start_position=0):
        """Start playback from a specific position"""
        if not self.file_service.is_file_loaded():
            raise ValueError("No file is currently loaded")
        
        # Stop any ongoing playback
        self.pause()
        
        # Set up threading event
        self.stop_playback_event.clear()
        self.is_playing_flag = True
        
        # Start playback in a separate thread
        self.playback_thread = threading.Thread(
            target=self._playback_worker,
            args=(start_position,)
        )
        self.playback_thread.daemon = True
        self.playback_thread.start()
    
    def _playback_worker(self, start_position):
        """Worker thread for handling audio playback"""
        try:
            # Start from the specified position
            current_pos = start_position
            chunk_size = 4096  # Read in 4KB chunks

            while not self.stop_playback_event.is_set():
                # Read a chunk of text from the current position
                text_chunk = self.file_service.read_chunk_at_position(current_pos, chunk_size)

                # If we've reached the end of the file, exit
                if not text_chunk:
                    break

                # Split the chunk into sentences for more natural reading
                sentence_chunks = split_text_by_sentences(text_chunk)

                for sentence_chunk in sentence_chunks:
                    if self.stop_playback_event.is_set():
                        break

                    if sentence_chunk.strip():
                        # Calculate the new position after processing this sentence
                        sentence_bytes = len(sentence_chunk.encode('utf-8'))

                        # Update the last known position in config service
                        current_file = self.file_service.file_path
                        if current_file:
                            self.config_service.set_last_position(current_file, current_pos)

                        # Speak the sentence chunk with source file path
                        self.tts_service.speak_text(sentence_chunk, self.file_service.file_path)

                        # Update position for next iteration
                        current_pos += sentence_bytes

                # Check if playback should stop
                if self.stop_playback_event.is_set():
                    break

        except Exception as e:
            print(f"Playback error: {e}")
        finally:
            self.is_playing_flag = False
    
    def pause(self):
        """Pause ongoing playback"""
        if self.is_playing_flag:
            self.stop_playback_event.set()
            
            if self.playback_thread and self.playback_thread.is_alive():
                self.playback_thread.join(timeout=2)
            
            self.is_playing_flag = False
    
    def stop(self):
        """Stop ongoing playback completely"""
        self.pause()
        # Reset the stop event for future playback
        self.stop_playback_event.clear()
    
    def get_current_position(self):
        """Get the current reading position"""
        # Since position is updated during playback, we'd need to track it differently
        # For now, we're relying on the UI to manage and update positions
        current_file = self.file_service.file_path
        if current_file:
            return self.config_service.get_last_position(current_file)
        return 0
    
    def set_position(self, position):
        """Set the reading position"""
        if not self.file_service.is_file_loaded():
            raise ValueError("No file is currently loaded")
        
        # Pause current playback if active
        if self.is_playing_flag:
            self.pause()
        
        # Update position in config service
        current_file = self.file_service.file_path
        if current_file:
            self.config_service.set_last_position(current_file, position)