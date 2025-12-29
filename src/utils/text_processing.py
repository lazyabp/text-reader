# Utility functions for the text-to-speech application
import re


def split_text_by_sentences(text, max_chunk_size=2048):
    """
    Split text into chunks by sentences, ensuring each chunk doesn't exceed max_chunk_size.
    This helps with more natural TTS reading.
    """
    # First, break the text into sentences
    sentences = re.split(r'[.!?]+\s+', text)
    
    chunks = []
    current_chunk = ""
    
    for sentence in sentences:
        # Check if adding this sentence would exceed the max size
        if len(current_chunk.encode('utf-8')) + len(sentence.encode('utf-8')) + 1 <= max_chunk_size:
            # Add the sentence to the current chunk
            if current_chunk:
                current_chunk += " " + sentence
            else:
                current_chunk = sentence
        else:
            # If the current chunk is not empty, save it and start a new one
            if current_chunk:
                chunks.append(current_chunk)
            
            # If the sentence itself is larger than max_chunk_size, split it by words
            if len(sentence.encode('utf-8')) > max_chunk_size:
                words = sentence.split()
                current_chunk = ""
                
                for word in words:
                    if len(current_chunk.encode('utf-8')) + len(word.encode('utf-8')) + 1 <= max_chunk_size:
                        if current_chunk:
                            current_chunk += " " + word
                        else:
                            current_chunk = word
                    else:
                        if current_chunk:
                            chunks.append(current_chunk)
                            current_chunk = word
                        else:
                            # Word is too large, force split by max_chunk_size
                            while len(word.encode('utf-8')) > max_chunk_size:
                                # Take as much as possible from the word
                                substring = word[:len(word)//2]
                                while len(substring.encode('utf-8')) > max_chunk_size and len(substring) > 1:
                                    substring = substring[:-1]
                                
                                chunks.append(substring)
                                word = word[len(substring):]
                            
                            if word:  # Remaining part of the word
                                current_chunk = word
            else:
                current_chunk = sentence
    
    # Add the last chunk if it exists
    if current_chunk:
        chunks.append(current_chunk)
    
    return chunks


def estimate_reading_time(text, words_per_minute=150):
    """
    Estimate the reading time for the given text based on average words per minute.
    """
    if not text:
        return 0
    
    # Count words in the text
    words = len(re.findall(r'\w+', text))
    
    # Calculate minutes and convert to seconds
    minutes = words / words_per_minute
    seconds = minutes * 60
    
    return int(seconds)


def sanitize_for_tts(text):
    """
    Sanitize text for TTS to handle common issues like abbreviations, numbers, etc.
    """
    # Replace common abbreviations with their spoken forms
    replacements = {
        r'\bMr\.\s': 'Mister ',
        r'\bMrs\.\s': 'Missus ',  # Or "Mizz" depending on dialect
        r'\bDr\.\s': 'Doctor ',
        r'\bProf\.\s': 'Professor ',
        r'\bst\s': 'saint ',  # street or saint
        r'\bave\s': 'avenue ',  # street abbreviation
        r'\betc\.\s': 'et cetera ',
        r'\bvs\.\s': 'versus ',
        r'\bJan\.\s': 'January ',
        r'\bFeb\.\s': 'February ',
        r'\bMar\.\s': 'March ',
        r'\bApr\.\s': 'April ',
        r'\bJun\.\s': 'June ',
        r'\bJul\.\s': 'July ',
        r'\bAug\.\s': 'August ',
        r'\bSep\.\s': 'September ',
        r'\bOct\.\s': 'October ',
        r'\bNov\.\s': 'November ',
        r'\bDec\.\s': 'December ',
    }
    
    sanitized_text = text
    for pattern, replacement in replacements.items():
        sanitized_text = re.sub(pattern, replacement, sanitized_text, flags=re.IGNORECASE)
    
    return sanitized_text