# Design: Text-to-Speech Reader Application

## Architecture Overview
The application follows a Model-View-Controller (MVC) pattern with additional service layers for file handling and TTS processing.

```
┌─────────────────┐    ┌──────────────────┐    ┌──────────────────┐
│     UI Layer    │◄──►│  Controller      │◄──►│     Services     │
│                 │    │                  │    │                  │
│ - File Selector │    │ - File Selection │    │ - FileService    │
│ - Offset Ctrl   │    │ - Play/Pause     │    │ - TTSService     │
│ - TTS Controls  │    │ - Position Mgmt  │    │ - ConfigService  │
│ - Playback UI   │    │ - Config Mgmt    │    │                  │
└─────────────────┘    └──────────────────┘    └──────────────────┘
```

## Component Design

### FileService
- Responsible for efficient file reading operations
- Implements streaming reader to handle large files
- Tracks current position in file
- Estimates progress percentage

### TTSService
- Integrates with Piper TTS engine
- Manages audio generation parameters
- Handles text chunking for efficient processing
- Manages audio output buffering

### ConfigService
- Stores/retrieves user preferences
- Manages TTS parameters
- Handles reading position persistence
- Uses JSON for storage format

### Main Controller
- Coordinates UI interactions
- Manages playback state
- Interfaces with services
- Handles error conditions

## Data Flow

### Initialization
1. ConfigService loads settings from config file
2. UI initializes with loaded settings
3. Application waits for file selection

### File Loading
1. User selects file via UI
2. Controller validates file
3. FileService creates stream reader
4. UI updates with file info

### Playback
1. Controller receives play command
2. FileService reads chunk at current position
3. TTSService converts text to audio
4. Audio plays while position is continuously tracked
5. Periodically save position to config

## Technology Choices

### UI Framework
- Option 1: tkinter (built-in, lightweight)
- Option 2: PyQt (feature-rich, cross-platform)
- Decision: Using tkinter for simplicity and reduced dependencies

### File Reading
- Use Python's built-in file streaming
- Implement buffered reading for efficiency
- Use seek/tell for position tracking

### TTS Engine
- Piper TTS via subprocess calls
- Handle parameter adjustments dynamically
- Manage audio output via system audio APIs

### Configuration Storage
- JSON file for user preferences
- Separate file for each book's position
- Automatic backup of previous settings

## Error Handling Strategy

### File Errors
- Invalid file format: Display user-friendly message
- File not found: Prompt for valid file
- Permission denied: Alert and suggest alternate file

### TTS Errors
- Engine unavailable: Fallback to OS TTS or alert user
- Parameter invalid: Reset to default values
- Audio device busy: Retry with delay

### State Persistence
- Failed to save position: Queue for next save attempt
- Corrupted config: Load defaults and warn user
- Missing config: Initialize with default settings