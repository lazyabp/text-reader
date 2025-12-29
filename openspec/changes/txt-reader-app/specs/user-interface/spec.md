# Specification: User Interface for Text-to-Speech Reader

## User Interface

### ## ADDED Main Application Window
The application provides a clean, intuitive interface for controlling text-to-speech functionality.

#### Requirement: Window Layout
The application window shall contain sections for file selection, position control, TTS configuration, and playback controls arranged logically.

##### Scenario: Application Window Appears Correctly
Given the application starts,
When the main window opens,
Then it displays a title indicating its function,
And it contains labeled sections for file selection,
And it contains controls for position adjustment,
And it provides access to TTS configuration,
And it has playback control buttons (Play/Pause).

### ## ADDED File Selection UI
The application provides an intuitive way to select text files for reading.

#### Requirement: File Selection Button
The application shall provide a prominent button to initiate file selection.

##### Scenario: File Selection Button Functions
Given the application is running,
When the user clicks the 'Select File' button,
Then the button highlights or shows active state,
And a file selection dialog appears.

#### Requirement: File Path Display
The application shall clearly show the currently selected file path.

##### Scenario: File Path Is Visible
Given a file has been selected,
When the user looks at the application window,
Then the selected file's full path is clearly visible,
And the path display is readable even for long file paths.

### ## ADDED Position Control UI
The application provides intuitive controls for managing reading position.

#### Requirement: Position Slider
The application shall provide a slider control to adjust the starting reading position.

##### Scenario: Position Slider Functions
Given a text file is loaded,
When the user drags the position slider,
Then the position indicator updates in real-time,
And the displayed position corresponds to the slider position.

#### Requirement: Position Indicator
The application shall display the current reading position numerically.

##### Scenario: Position Indicator Updates
Given the application is tracking reading position,
When the reading position changes,
Then the numeric position indicator updates,
And the position is accurate to the character level.

### ## ADDED TTS Configuration UI
The application provides accessible controls for TTS parameters.

#### Requirement: Speed Control
The application shall provide a control to adjust speech speed/rate.

##### Scenario: Speed Control Functions
Given the application is running,
When the user adjusts the speed control,
Then the control provides clear indication of current value,
And subsequent text is read at the selected speed.

#### Requirement: Voice Selection
If multiple voices are available, the application shall allow voice selection.

##### Scenario: Voice Selection Available
Given Piper TTS has multiple voices installed,
When the user accesses the voice selection control,
Then the available voices are listed,
And the user can select a different voice,
And the new voice is applied to subsequent text.

### ## ADDED Playback Controls
The application provides essential playback functionality through dedicated controls.

#### Requirement: Play/Pause Toggle
The application shall provide a clear play/pause button that toggles between states.

##### Scenario: Play/Pause Button Toggles State
Given text is loaded but not playing,
When the user clicks the Play button,
Then the button changes to Pause state,
And text reading begins,
And when clicked again,
Then the button changes back to Play state,
And text reading pauses.