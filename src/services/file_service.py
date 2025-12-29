# File service for handling text files efficiently
import os
from pathlib import Path


class FileService:
    def __init__(self):
        self.file_path = None
        self.file_handle = None
        self.file_size = 0
        self._buffer_size = 8192  # 8KB buffer

    def load_file(self, file_path):
        """Load a text file for reading"""
        if self.file_handle:
            self.file_handle.close()

        self.file_path = file_path
        self.file_handle = open(file_path, 'r', encoding='utf-8')
        self.file_size = os.path.getsize(file_path)
    
    def is_file_loaded(self):
        """Check if a file is currently loaded"""
        return self.file_path is not None and self.file_handle is not None
    
    def get_file_size(self):
        """Get the size of the currently loaded file"""
        return self.file_size
    
    def read_chunk_at_position(self, position, chunk_size=4096):
        """Read a chunk of text at the specified position"""
        if not self.file_handle:
            return ""

        # Seek to the specified position
        self.file_handle.seek(position)

        # Read the chunk
        chunk = self.file_handle.read(chunk_size)

        # Also check for the end of the file
        remaining = self.file_size - position
        if remaining < chunk_size:
            # Ensure we return only the remaining text
            chunk = chunk[:remaining]

        return chunk

    def read_text_in_chunks(self, start_pos, chunk_size=8192, max_text_size=20000):
        """
        Read text in chunks starting from start_pos up to max_text_size
        This is more efficient for large reads without loading entire file into memory
        """
        if not self.file_handle:
            return ""

        self.file_handle.seek(start_pos)
        text_read = ""
        total_read = 0

        while total_read < max_text_size:
            remaining = max_text_size - total_read
            current_chunk_size = min(chunk_size, remaining)

            chunk = self.file_handle.read(current_chunk_size)

            if not chunk:
                # End of file reached
                break

            text_read += chunk
            total_read += len(chunk)

        return text_read
    
    def read_text_between_positions(self, start_pos, end_pos):
        """Read text between two positions"""
        if not self.file_handle:
            return ""
        
        # Calculate the size to read
        size_to_read = min(end_pos - start_pos, self.file_size - start_pos)
        
        if size_to_read <= 0:
            return ""
        
        # Seek to start position and read
        self.file_handle.seek(start_pos)
        text = self.file_handle.read(size_to_read)
        
        return text
    
    def close_file(self):
        """Close the currently opened file"""
        if self.file_handle:
            self.file_handle.close()
            self.file_handle = None
            self.file_path = None
            self.file_size = 0
    
    def get_line_at_position(self, position):
        """Get the full line at the given position"""
        if not self.file_handle:
            return ""

        # Go backwards to find the start of the line
        self.file_handle.seek(position)

        # If position is at the beginning of the file
        if position == 0:
            return self.file_handle.readline()

        # Search backward for newline character
        while position > 0:
            self.file_handle.seek(position - 1)
            char = self.file_handle.read(1)
            if char == '\n':
                break
            position -= 1

        # Now read the line
        line = self.file_handle.readline()
        return line

    def get_text_around_position(self, position, context_size=1024):
        """
        Get text around a specific position with context on both sides
        This helps to find sentence boundaries for more natural reading
        """
        if not self.file_handle:
            return ""

        # Calculate start position (with boundary check)
        start_pos = max(0, position - context_size)
        end_pos = min(self.file_size, position + context_size)

        # Read the context
        self.file_handle.seek(start_pos)
        context_text = self.file_handle.read(end_pos - start_pos)

        # Adjust position to be relative to the context text
        relative_pos = position - start_pos

        return context_text, relative_pos
    
    def get_line_number_at_position(self, position):
        """Get the line number at the given position"""
        if not self.file_handle or position < 0:
            return 0
        
        self.file_handle.seek(0)
        content = self.file_handle.read(position)
        return content.count('\n') + 1  # Line numbers start at 1