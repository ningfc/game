import socket
import numpy as np
import sounddevice as sd
import matplotlib.pyplot as plt
from scipy.signal import spectrogram

# 配置
UDP_IP = "0.0.0.0"  # 监听所有网络接口
UDP_PORT = 5000     # 监听端口
SAMPLE_RATE = 44100 # 音频采样率
CHANNELS = 1        # 单声道
CHUNK_SIZE = 4096   # 每次读取的音频块大小（字节数）

# 初始化 UDP 套接字
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))

print(f"Listening on UDP {UDP_IP}:{UDP_PORT}")

# 初始化 Matplotlib 图形
plt.ion()
fig, ax = plt.subplots()
x_data, y_data, spec_data = [], [], None

# 图形更新函数
def update_spectrogram(audio_data):
    global spec_data
    freqs, times, Sxx = spectrogram(audio_data, SAMPLE_RATE, nperseg=1024)
    ax.clear()
    spec_data = ax.pcolormesh(times, freqs, 10 * np.log10(Sxx), shading='gouraud', cmap='viridis')
    ax.set_xlabel('Time (s)')
    ax.set_ylabel('Frequency (Hz)')
    ax.set_ylim(0, 8000)  # 显示 0-8kHz
    plt.pause(0.001)

# 音频播放流
def audio_callback(indata, frames, time, status):
    pass  # 无需处理，实时播放

# 打开音频播放
with sd.OutputStream(samplerate=SAMPLE_RATE, channels=CHANNELS, dtype='int16', callback=audio_callback):
    while True:
        data, addr = sock.recvfrom(CHUNK_SIZE)
        audio_data = np.frombuffer(data, dtype=np.int16)
        sd.play(audio_data)  # 播放音频
        update_spectrogram(audio_data)  # 更新频谱