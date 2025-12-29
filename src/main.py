# Main application entry point for the Text-to-Speech Reader Application
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import json
import os
from pathlib import Path

# Import our modules
from services.file_service import FileService
from services.tts_service import TTSService
from services.config_service import ConfigService
from controllers.main_controller import MainController


class TTSApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Text-to-Speech Reader")
        self.root.geometry("800x600")
        
        # Initialize services
        self.config_service = ConfigService()
        self.file_service = FileService()
        self.tts_service = TTSService()

        # Initialize controller
        self.controller = MainController(
            self.file_service,
            self.tts_service,
            self.config_service
        )
        
        # Setup UI
        self.setup_ui()
        
        # Load saved configuration
        self.load_configuration()
    
    def setup_ui(self):
        # Create main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # File selection section
        file_frame = ttk.LabelFrame(main_frame, text="File Selection", padding="10")
        file_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        file_frame.columnconfigure(1, weight=1)
        
        ttk.Button(file_frame, text="Select File", command=self.select_file).grid(row=0, column=0, padx=5)
        self.file_path_var = tk.StringVar()
        file_entry = ttk.Entry(file_frame, textvariable=self.file_path_var, state="readonly")
        file_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5)
        
        # Position control section
        pos_frame = ttk.LabelFrame(main_frame, text="Reading Position", padding="10")
        pos_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        pos_frame.columnconfigure(0, weight=1)
        
        # Position label
        self.position_label = ttk.Label(pos_frame, text="Position: 0")
        self.position_label.grid(row=0, column=0, sticky=tk.W)
        
        # Position slider
        self.position_var = tk.IntVar()
        self.position_slider = ttk.Scale(
            pos_frame, 
            from_=0, 
            to=100, 
            orient=tk.HORIZONTAL, 
            variable=self.position_var,
            command=self.on_position_change
        )
        self.position_slider.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=5)
        
        # Position entry
        self.position_entry_var = tk.StringVar(value="0")
        pos_entry = ttk.Entry(pos_frame, textvariable=self.position_entry_var, width=10)
        pos_entry.grid(row=1, column=1, padx=5)
        pos_entry.bind("<Return>", lambda e: self.set_position_from_entry())
        
        # TTS Configuration section
        tts_frame = ttk.LabelFrame(main_frame, text="TTS Configuration", padding="10")
        tts_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)

        # Voice model selection
        ttk.Label(tts_frame, text="Voice Model:").grid(row=0, column=0, sticky=tk.W)
        self.voice_model_var = tk.StringVar()
        self.voice_model_entry = ttk.Entry(tts_frame, textvariable=self.voice_model_var)
        self.voice_model_entry.grid(row=0, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        # Add tooltip or placeholder text to indicate where to find voice models
        self.voice_model_entry.insert(0, "Enter path to voice model (.onnx file)")

        # Speed control
        ttk.Label(tts_frame, text="Speed:").grid(row=1, column=0, sticky=tk.W)
        self.speed_var = tk.DoubleVar(value=1.0)
        speed_scale = ttk.Scale(
            tts_frame,
            from_=0.5,
            to=2.0,
            orient=tk.HORIZONTAL,
            variable=self.speed_var,
            command=self.on_speed_change
        )
        speed_scale.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=5)
        self.speed_value_label = ttk.Label(tts_frame, text=f"{self.speed_var.get():.1f}")
        self.speed_value_label.grid(row=1, column=2, padx=5)

        # Pitch control
        ttk.Label(tts_frame, text="Pitch:").grid(row=2, column=0, sticky=tk.W)
        self.pitch_var = tk.DoubleVar(value=1.0)
        pitch_scale = ttk.Scale(
            tts_frame,
            from_=0.5,
            to=2.0,
            orient=tk.HORIZONTAL,
            variable=self.pitch_var,
            command=self.on_pitch_change
        )
        pitch_scale.grid(row=2, column=1, sticky=(tk.W, tk.E), padx=5)
        self.pitch_value_label = ttk.Label(tts_frame, text=f"{self.pitch_var.get():.1f}")
        self.pitch_value_label.grid(row=2, column=2, padx=5)

        # Volume control
        ttk.Label(tts_frame, text="Volume:").grid(row=3, column=0, sticky=tk.W)
        self.volume_var = tk.DoubleVar(value=1.0)
        volume_scale = ttk.Scale(
            tts_frame,
            from_=0.0,
            to=1.0,
            orient=tk.HORIZONTAL,
            variable=self.volume_var,
            command=self.on_volume_change
        )
        volume_scale.grid(row=3, column=1, sticky=(tk.W, tk.E), padx=5)
        self.volume_value_label = ttk.Label(tts_frame, text=f"{self.volume_var.get():.1f}")
        self.volume_value_label.grid(row=3, column=2, padx=5)
        
        # Playback controls
        ctrl_frame = ttk.Frame(main_frame)
        ctrl_frame.grid(row=3, column=0, columnspan=2, pady=10)
        
        self.play_button = ttk.Button(ctrl_frame, text="Play", command=self.toggle_playback)
        self.play_button.grid(row=0, column=0, padx=5)
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
    
    def load_configuration(self):
        """Load saved configuration"""
        config = self.config_service.load_config()

        # Load TTS parameters
        if 'tts_params' in config:
            params = config['tts_params']
            self.speed_var.set(params.get('rate', 1.0))
            self.pitch_var.set(params.get('pitch', 1.0))
            self.volume_var.set(params.get('volume', 1.0))
            # Load voice model if available
            voice_model = params.get('voice_model', '')
            self.voice_model_var.set(voice_model)

            self.update_tts_param_labels()

            # Apply parameters to TTS service
            self.tts_service.set_parameters(
                rate=params.get('rate', 1.0),
                pitch=params.get('pitch', 1.0),
                volume=params.get('volume', 1.0),
                voice_model=voice_model
            )
    
    def save_configuration(self):
        """Save current configuration"""
        config = {
            'tts_params': {
                'rate': self.speed_var.get(),
                'pitch': self.pitch_var.get(),
                'volume': self.volume_var.get(),
                'voice_model': self.voice_model_var.get()
            }
        }
        self.config_service.save_config(config)
    
    def select_file(self):
        """Open file dialog to select a text file"""
        file_path = filedialog.askopenfilename(
            title="Select a text file",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                self.controller.load_file(file_path)
                self.file_path_var.set(file_path)
                
                # Update position slider range based on file size
                file_size = self.file_service.get_file_size()
                self.position_slider.configure(to=file_size)
                
                # Restore last reading position if available
                last_pos = self.config_service.get_last_position(file_path)
                if last_pos is not None:
                    self.position_var.set(last_pos)
                    self.position_entry_var.set(str(last_pos))
                    self.on_position_change(last_pos)
                
                self.status_var.set(f"Loaded: {os.path.basename(file_path)}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load file: {str(e)}")
    
    def on_position_change(self, value):
        """Handle position slider change"""
        pos = int(float(value))
        self.position_label.config(text=f"Position: {pos}")
        self.position_entry_var.set(str(pos))
        
        # Save current position to config
        current_file = self.file_path_var.get()
        if current_file:
            self.config_service.set_last_position(current_file, pos)
    
    def set_position_from_entry(self):
        """Set position from entry field"""
        try:
            pos = int(self.position_entry_var.get())
            max_val = int(self.position_slider.cget('to'))
            if 0 <= pos <= max_val:
                self.position_var.set(pos)
                self.on_position_change(pos)
            else:
                messagebox.showwarning("Invalid Input", f"Position must be between 0 and {max_val}")
        except ValueError:
            messagebox.showwarning("Invalid Input", "Please enter a valid number")
    
    def on_speed_change(self, value):
        """Handle speed parameter change"""
        self.speed_value_label.config(text=f"{float(value):.1f}")
        self.update_tts_parameters()
    
    def on_pitch_change(self, value):
        """Handle pitch parameter change"""
        self.pitch_value_label.config(text=f"{float(value):.1f}")
        self.update_tts_parameters()
    
    def on_volume_change(self, value):
        """Handle volume parameter change"""
        self.volume_value_label.config(text=f"{float(value):.1f}")
        self.update_tts_parameters()
    
    def update_tts_param_labels(self):
        """Update all TTS parameter labels"""
        self.speed_value_label.config(text=f"{self.speed_var.get():.1f}")
        self.pitch_value_label.config(text=f"{self.pitch_var.get():.1f}")
        self.volume_value_label.config(text=f"{self.volume_var.get():.1f}")
    
    def update_tts_parameters(self):
        """Update TTS service with current parameters"""
        self.tts_service.set_parameters(
            rate=self.speed_var.get(),
            pitch=self.pitch_var.get(),
            volume=self.volume_var.get(),
            voice_model=self.voice_model_var.get()
        )
    
    def toggle_playback(self):
        """Toggle between play and pause states"""
        if self.controller.is_playing():
            self.controller.pause()
            self.play_button.config(text="Play")
            self.status_var.set("Paused")
        else:
            if self.file_service.is_file_loaded():
                # Start playback from current position
                pos = self.position_var.get()
                self.controller.start_playback(pos)
                self.play_button.config(text="Pause")
                self.status_var.set("Playing...")
            else:
                messagebox.showwarning("No File", "Please select a text file first")


def main():
    root = tk.Tk()
    app = TTSApp(root)
    
    # Save configuration when closing
    def on_closing():
        app.save_configuration()
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()


if __name__ == "__main__":
    main()