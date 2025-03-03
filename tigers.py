import numpy as np
import wave
import struct
import simpleaudio as sa  # added for audio playback

sample_rate = 44100
amplitude = 32767

def generate_tone(frequency, duration, sample_rate):
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    wave_data = amplitude * np.sin(2 * np.pi * frequency * t)
    return wave_data.astype(np.int16)

# 定义“两只老虎”这首歌的旋律和节奏 (重写版本)
song = [
    # 两只老虎
    ('C', 0.5), ('D', 0.5), ('E', 0.5), ('C', 1.0),
    # 两只老虎重复
    ('C', 0.5), ('D', 0.5), ('E', 0.5), ('C', 1.0),
    # 跑得快
    ('E', 0.5), ('F', 0.5), ('G', 1.0),
    # 跑得快重复
    ('E', 0.5), ('F', 0.5), ('G', 1.0),
    # 一只没有耳朵
    ('G', 0.5), ('A', 0.5), ('G', 0.5), ('F', 0.5), ('E', 0.5), ('C', 0.5),
    # 一只没有尾巴
    ('G', 0.5), ('A', 0.5), ('G', 0.5), ('F', 0.5), ('E', 0.5), ('C', 0.5),
    #真奇怪
    #真奇怪
    ('C', 0.5), ('B', 0.5), ('A', 0.5), ('G', 1.0),
    ('C', 0.5), ('B', 0.5), ('A', 0.5), ('G', 1.0)
]

# 使用4th octave频率
note_frequencies = {
    'C': 261.63,
    'D': 293.66,
    'E': 329.63,
    'F': 349.23,
    'G': 392.00,
    'A': 440.00,
    'B': 493.88
}

# 依次生成所有音符的tone并合成完整曲子
tones = []
for note, dur in song:
    freq = note_frequencies.get(note)
    if not freq:
        continue
    tones.append(generate_tone(freq, dur, sample_rate))
melody = np.concatenate(tones)

# 生成音频文件 (two_tigers.wav)
output_filename = "two_tigers.wav"
with wave.open(output_filename, "w") as wav_file:
    wav_file.setparams((1, 2, sample_rate, len(melody), "NONE", "not compressed"))
    for sample in melody:
        wav_file.writeframes(struct.pack("<h", int(sample)))
print(f"WAV file generated: {output_filename}")

# 播放生成的音频文件
play_obj = sa.WaveObject(melody.tobytes(), 1, 2, sample_rate).play()
play_obj.wait_done()



