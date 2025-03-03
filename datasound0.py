import socket
import sounddevice as sd
import numpy as np

# 配置
UDP_IP = "0.0.0.0"  # 监听所有网络接口
UDP_PORT = 5000     # 监听端口
SAMPLE_RATE = 44100 # 音频采样率
CHANNELS = 2        # 双声道
CHUNK_SIZE = 1024   # 每次读取的音频块大小（字节数）

# 初始化 UDP 套接字
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))

print(f"Listening on UDP {UDP_IP}:{UDP_PORT}")

# 音频播放回调
def audio_callback(indata, frames, time, status):
    pass  # 实时播放无需处理额外逻辑

# 打开音频流
with sd.OutputStream(samplerate=SAMPLE_RATE, channels=CHANNELS, dtype='int16', callback=audio_callback):
    while True:
        data, addr = sock.recvfrom(CHUNK_SIZE)
        audio_data = np.frombuffer(data, dtype=np.int16)
        sd.play(audio_data)  # 播放音频块
        print("==")