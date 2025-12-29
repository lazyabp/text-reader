# Text-to-Speech Reader Application

A Python-based application for reading text files aloud with Piper TTS, featuring position tracking and adjustable parameters.

## Features

- Simple UI for selecting and reading text files
- Adjustable starting position with real-time tracking
- Persistent reading position across application restarts
- Configurable TTS parameters (speed, pitch, volume)
- Efficient handling of large text files
- Automatic saving of TTS parameter configuration

## Prerequisites

1. **Python 3.8 or higher**
2. **Piper TTS** - Install from: https://github.com/rhasspy/piper
   - Ensure `piper` is available in your PATH
3. **Voice Model** - Download a voice model file (.onnx) from Piper's releases
   - Visit https://github.com/rhasspy/piper/releases to download a voice model
   - Note the path to the model file as you'll need to enter it in the application UI

## Installation

1. Clone or download this repository
2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Install Piper TTS according to the official documentation
4. Download a voice model for Piper TTS from https://github.com/rhasspy/piper/releases

## Usage

1. Run the application:
   ```bash
   python src/main.py
   ```

2. In the "TTS Configuration" section, enter the path to your Piper voice model file (.onnx)

3. Click "Select File" to choose a text file to read

4. Adjust the reading position using the slider or by entering a value

5. Configure TTS parameters (speed, pitch, volume) as needed

6. Click "Play" to start reading from the selected position

## Configuration

The application automatically saves:
- Last reading position for each file
- TTS parameter settings

Configuration is stored in the `config/` directory.

## Troubleshooting

### Piper TTS Not Found

If you receive a "Piper TTS not found" error:
1. Verify that Piper TTS is installed
2. Ensure the `piper` command is available in your system PATH
3. Check that you have a voice model downloaded and accessible

### Large Files

The application handles large text files efficiently by reading in chunks, but very large files may take time to process initially.

## Project Structure

```
text-voice/
├── src/
│   ├── main.py                 # Main application entry point
│   ├── services/
│   │   ├── file_service.py     # Handles file operations
│   │   ├── tts_service.py      # Interfaces with Piper TTS
│   │   └── config_service.py   # Manages configuration
│   ├── controllers/
│   │   └── main_controller.py  # Main application logic
│   └── utils/
│       └── text_processing.py  # Text utilities
├── config/                     # Configuration and position storage
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

## Limitations

- Currently tested only on Windows OS
- Requires Piper TTS to be installed separately
- Audio playback may require additional setup on some systems