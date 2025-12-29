# TTS service for converting text to speech using Piper TTS
import subprocess
import tempfile
import threading
import queue
import time
import os
import sys
from pathlib import Path

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
    
    def synthesize_text(self, text):
        """Convert text to speech using Piper TTS and return audio file path"""
        try:
            # Check if voice model is set
            if not self.voice_model:
                raise RuntimeError("No voice model specified. Please set a voice model before synthesizing text.")

            # Create a temporary file for the audio output
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

            # Verify that the output file was created and has content
            if not os.path.exists(temp_audio_path) or os.path.getsize(temp_audio_path) == 0:
                raise RuntimeError("Piper TTS generated an empty audio file")

            return temp_audio_path
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Piper TTS failed: {e.stderr}")
        except FileNotFoundError:
            raise RuntimeError("Piper TTS not found. Please install Piper TTS from https://github.com/rhasspy/piper")
        except Exception as e:
            raise RuntimeError(f"TTS synthesis failed: {str(e)}")
    
    def play_audio(self, audio_file_path):
        """Play the synthesized audio file"""
        try:
            # Load and play the audio file with pygame
            pygame.mixer.music.load(audio_file_path)
            pygame.mixer.music.set_volume(self.volume)
            pygame.mixer.music.play()

            # Wait for the audio to finish playing
            while pygame.mixer.music.get_busy() and not self.stop_signal.is_set():
                pygame.time.wait(100)  # Check every 100ms if playback should stop

            # Stop the music if the stop signal was received
            if self.stop_signal.is_set():
                pygame.mixer.music.stop()

        except Exception as e:
            raise RuntimeError(f"Failed to play audio file: {e}")
        finally:
            # Clean up the temporary audio file after playing
            if os.path.exists(audio_file_path):
                os.remove(audio_file_path)
    
    def speak_text(self, text):
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
                # Synthesize the text chunk to audio
                audio_file_path = self.synthesize_text(chunk)
                print("audio_file_path1", audio_file_path)
                # Play the audio
                self.play_audio(audio_file_path)
    
    def start_streaming_speech(self, text_generator):
        """Start streaming speech from a text generator"""
        if self.playback_thread and self.playback_thread.is_alive():
            self.stop_signal.set()
            self.playback_thread.join(timeout=2)
        
        self.stop_signal.clear()
        self.is_playing_flag = True
        
        self.playback_thread = threading.Thread(
            target=self._streaming_worker,
            args=(text_generator,)
        )
        self.playback_thread.daemon = True
        self.playback_thread.start()
    
    def _streaming_worker(self, text_generator):
        """Worker thread for streaming speech"""
        for text_chunk in text_generator:
            if self.stop_signal.is_set():
                break
            
            # Synthesize and play the text chunk
            try:
                if text_chunk.strip():
                    audio_file_path = self.synthesize_text(text_chunk)
                    print("audio_file_path", audio_file_path)
                    self.play_audio(audio_file_path)
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