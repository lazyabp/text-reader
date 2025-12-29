# TTS service for converting text to speech using Piper TTS
import subprocess
import tempfile
import threading
import queue
import time
import os
import sys
from pathlib import Path
from datetime import datetime
import io

# Add the src directory to the path to enable imports
sys.path.append(str(Path(__file__).parent.parent))

from utils.text_processing import split_text_by_sentences, sanitize_for_tts
import pygame  # For better audio playback


class TTSService:
    def __init__(self):
        self.rate = 1.0  # Speed multiplier (1.0 = normal speed)
        self.pitch = 1.0  # Pitch multiplier (1.0 = normal pitch)
        self.volume = 1.0  # Volume multiplier (1.0 = normal volume)
        self.voice_model = None  # Path to the voice model
        self.audio_queue = queue.Queue()
        self.playback_thread = None
        self.is_playing_flag = False
        self.stop_signal = threading.Event()

        # Initialize pygame mixer for audio playback
        pygame.mixer.init()
    
    def set_parameters(self, rate=1.0, pitch=1.0, volume=1.0, voice_model=None):
        """Set TTS parameters"""
        self.rate = rate
        self.pitch = pitch
        self.volume = volume
        if voice_model:
            self.voice_model = voice_model
    
    def synthesize_text_to_memory(self, text):
        """Convert text to speech using Piper TTS and return audio data in memory"""
        try:
            # Check if voice model is set
            if not self.voice_model:
                raise RuntimeError("No voice model specified. Please set a voice model before synthesizing text.")

            # Create a temporary file to receive the audio output from Piper
            with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_audio:
                temp_audio_path = temp_audio.name

            # Prepare the Piper TTS command
            cmd = [
                'piper',
                '--model', self.voice_model,  # Model is now required
                '--output_file', temp_audio_path  # Directly specify output file
            ]

            # Add rate parameter if supported by Piper
            # Note: Piper doesn't have a direct rate parameter, but we can achieve
            # similar effect with --length-scale
            length_scale = 1.0 / self.rate if self.rate != 0 else 1.0
            cmd.extend(['--length-scale', str(length_scale)])

            # Execute Piper TTS with the text
            proc = subprocess.run(
                cmd,
                input=text,
                stderr=subprocess.PIPE,
                text=True,
                check=True  # This will raise an exception if the command fails
            )

            # Read the audio data from the temporary file into memory
            with open(temp_audio_path, 'rb') as f:
                audio_data = f.read()

            # Clean up the temporary file immediately after reading
            os.remove(temp_audio_path)

            # Verify that we have audio data
            if not audio_data or len(audio_data) == 0:
                raise RuntimeError("Piper TTS generated empty audio data")

            return audio_data
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Piper TTS failed: {e.stderr}")
        except FileNotFoundError:
            raise RuntimeError("Piper TTS not found. Please install Piper TTS from https://github.com/rhasspy/piper")
        except Exception as e:
            raise RuntimeError(f"TTS synthesis failed: {str(e)}")

    def play_audio_from_memory(self, audio_data):
        """Play the synthesized audio data from memory"""
        try:
            # Create a BytesIO object from the audio data
            audio_buffer = io.BytesIO(audio_data)

            # Create a temporary Sound object from the buffer
            # We'll use pygame's Sound class which can work with file-like objects
            sound = pygame.mixer.Sound(audio_buffer)

            # Play the sound
            sound.play()

            # Wait for the audio to finish playing
            while sound.get_num_channels() > 0 and not self.stop_signal.is_set():
                pygame.time.wait(100)  # Check every 100ms if playback should stop

        except Exception as e:
            raise RuntimeError(f"Failed to play audio from memory: {e}")

    def speak_text(self, text, source_file_path=None, sync_playback=True):
        """Synthesize and play text directly"""
        if not text.strip():
            return

        # Sanitize text for TTS
        sanitized_text = sanitize_for_tts(text)

        # Split text into smaller chunks for better TTS processing
        text_chunks = split_text_by_sentences(sanitized_text)

        for chunk in text_chunks:
            if self.stop_signal.is_set():
                break

            if chunk.strip():
                # Synthesize the text chunk to audio data in memory
                audio_data = self.synthesize_text_to_memory(chunk)
                # Play the audio from memory
                self.play_audio_from_memory(audio_data)

                # Wait for the audio to finish playing before continuing if sync_playback is True
                if sync_playback:
                    # Wait for the audio to finish playing before continuing
                    # This ensures proper synchronization with the playback
                    while pygame.mixer.get_busy() and not self.stop_signal.is_set():
                        pygame.time.wait(100)  # Check every 100ms if playback should stop
    
    def start_streaming_speech(self, text_generator, source_file_path=None):
        """Start streaming speech from a text generator"""
        if self.playback_thread and self.playback_thread.is_alive():
            self.stop_signal.set()
            self.playback_thread.join(timeout=2)

        self.stop_signal.clear()
        self.is_playing_flag = True

        self.playback_thread = threading.Thread(
            target=self._streaming_worker,
            args=(text_generator, source_file_path)
        )
        self.playback_thread.daemon = True
        self.playback_thread.start()
    
    def _streaming_worker(self, text_generator, source_file_path=None):
        """Worker thread for streaming speech"""
        for text_chunk in text_generator:
            if self.stop_signal.is_set():
                break

            # Synthesize and play the text chunk
            try:
                if text_chunk.strip():
                    audio_data = self.synthesize_text_to_memory(text_chunk)
                    self.play_audio_from_memory(audio_data)

                    # Wait for the audio to finish playing before continuing
                    while pygame.mixer.get_busy() and not self.stop_signal.is_set():
                        pygame.time.wait(100)  # Check every 100ms if playback should stop
            except Exception as e:
                print(f"Error during speech synthesis/playback: {e}")
                break
    
    def stop_speech(self):
        """Stop ongoing speech"""
        self.is_playing_flag = False
        if self.stop_signal:
            self.stop_signal.set()
        
        if self.playback_thread and self.playback_thread.is_alive():
            self.playback_thread.join(timeout=2)
    
    def is_speaking(self):
        """Check if the TTS is currently speaking"""
        return self.is_playing_flag or (
            self.playback_thread and self.playback_thread.is_alive()
        )