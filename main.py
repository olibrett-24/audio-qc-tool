import librosa

# Load the audio file
y, sr= librosa.load("sine_sweep_20-20k_10s_1.wav" , sr=None)

# Work out how long it is
duration = librosa.get_duration(y=y, sr=sr)

print(f"File loaded successfully!")
print(f"Duration: {duration:.2f} seconds")
print(f"Sample rate: {sr} Hz")
