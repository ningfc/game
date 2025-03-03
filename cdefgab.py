import numpy as np
import wave
import struct

# Parameters for audio
sample_rate = 44100
duration = 0.5  # duration of each note in seconds
amplitude = 32767  # max amplitude for 16-bit audio

# Sine wave generator for a given frequency
def generate_tone(frequency, duration, sample_rate):
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    wave_data = amplitude * np.sin(2 * np.pi * frequency * t)
    return wave_data.astype(np.int16)

# Note frequencies (approximate values for the 4th octave)
notes = {
    'c': 261.63,
    'd': 293.66,
    'e': 329.63,
    'f': 349.23,
    'g': 392.00,
    'a': 440.00,
    'b': 493.88
}

# Generate and save a separate WAV file for each note
for note, freq in notes.items():
    tone = generate_tone(freq, duration, sample_rate)
    output_filename = f"{note}.wav"
    with wave.open(output_filename, 'w') as wav_file:
        # 1 channel, 2 bytes per sample, sample rate, number of samples, no compression
        wav_file.setparams((1, 2, sample_rate, len(tone), "NONE", "not compressed"))
        for sample in tone:
            wav_file.writeframes(struct.pack('<h', int(sample)))
    print(f"WAV file generated: {output_filename}")
