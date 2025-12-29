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
    
    def synthesize_text(self, text, source_file_path=None):
        """Convert text to speech using Piper TTS and return audio file path"""
        try:
            # Check if voice model is set
            if not self.voice_model:
                raise RuntimeError("No voice model specified. Please set a voice model before synthesizing text.")

            # Create voice directory structure
            voice_dir = Path("voice")
            voice_dir.mkdir(exist_ok=True)

            # Get the source file name without extension for directory name
            if source_file_path:
                source_file_name = Path(source_file_path).stem
            else:
                source_file_name = "default"

            # Create subdirectory for this specific text file
            file_voice_dir = voice_dir / source_file_name
            file_voice_dir.mkdir(exist_ok=True)

            # Generate filename with current date and time
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            # Ensure unique filename by adding a counter if needed
            counter = 1
            while True:
                audio_filename = f"{timestamp}{counter:02d}.wav"
                audio_file_path = file_voice_dir / audio_filename
                if not audio_file_path.exists():
                    break
                counter += 1

            # Prepare the Piper TTS command
            cmd = [
                'piper',
                '--model', self.voice_model,  # Model is now required
                '--output_file', str(audio_file_path)  # Directly specify output file
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
            if not os.path.exists(audio_file_path) or os.path.getsize(audio_file_path) == 0:
                raise RuntimeError("Piper TTS generated an empty audio file")

            return str(audio_file_path)
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
            # Only clean up if the file is in the temp directory (not in the voice directory)
            audio_path = Path(audio_file_path)
            if 'temp' in str(audio_path) and audio_path.exists():
                os.remove(audio_file_path)
    
    def speak_text(self, text, source_file_path=None):
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
                audio_file_path = self.synthesize_text(chunk, source_file_path)
                print("audio_file_path1", audio_file_path)
                # Play the audio
                self.play_audio(audio_file_path)
    
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
                    audio_file_path = self.synthesize_text(text_chunk, source_file_path)
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