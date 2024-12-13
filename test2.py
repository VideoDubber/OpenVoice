import librosa
import numpy as np
import soundfile as sf
import random

def jumble_audio(file_path, output_path):
    # Load the audio file
    y, sr = librosa.load(file_path, sr=None)
    
    # Duration of the audio in seconds
    duration = librosa.get_duration(y=y, sr=sr)
    
    # Number of samples per second
    samples_per_second = sr
    
    # Number of samples in each 1-second segment
    segment_length = samples_per_second
    
    # Calculate the total number of segments
    num_segments = int(np.ceil(duration))
    
    # Extract 1-second segments
    segments = []
    for i in range(num_segments):
        start = i * segment_length
        end = min((i + 1) * segment_length, len(y))
        segments.append(y[start:end])
    
    # Shuffle the segments
    random.shuffle(segments)
    
    # Concatenate the shuffled segments
    shuffled_audio = np.concatenate(segments)
    
    # Save the jumbled audio to a new file
    sf.write(output_path, shuffled_audio, sr)
    print(f"Jumbled audio saved to {output_path}")

# Example usage
jumble_audio('vocals.mp3', 'jumbled_output.mp3')
