# Test script to verify the application starts correctly
import sys
sys.path.append('src')

import tkinter as tk
from main import TTSApp

print("Creating root window...")
root = tk.Tk()
print("Initializing TTSApp...")
app = TTSApp(root)
print("Application initialized successfully")

# Try to access a UI element to ensure it was created
if hasattr(app, 'file_path_var'):
    print(f"File path variable exists: {app.file_path_var.get()}")
else:
    print("File path variable not found")

print("Accessing other UI elements...")
elements = ['position_var', 'speed_var', 'pitch_var', 'volume_var', 'play_button']
for element in elements:
    if hasattr(app, element):
        print(f"  {element}: Found")
    else:
        print(f"  {element}: Not found")

print("Destroying root window...")
root.destroy()
print("Test completed successfully")