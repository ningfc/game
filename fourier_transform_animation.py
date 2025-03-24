import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.patches import Circle

plt.style.use('dark_background')

# 设置图形
fig, ax = plt.subplots(figsize=(16, 6))
ax.set_xlim(-3, 13)
ax.set_ylim(-3, 3)
ax.set_aspect('equal')
ax.axis('off')

# 添加连接线
connector_line, = ax.plot([], [], 'white', lw=2, alpha=0.5)

# 傅立叶级数参数
n_circles = 10
freqs = np.arange(1, n_circles+1)
radii = 4 / (np.pi * freqs)  # 方波的傅立叶系数
phases = np.random.uniform(0, 2*np.pi, n_circles)

# 初始化圆和线
circles = []
lines = []
centers = []
for i in range(n_circles):
    circle = Circle((0, 0), radii[i], fill=False, color='cyan', alpha=0.8)
    ax.add_patch(circle)
    circles.append(circle)
    
    line, = ax.plot([], [], 'white', lw=1)
    lines.append(line)
    
    center, = ax.plot([], [], 'ro', markersize=2)
    centers.append(center)

# 初始化波形线
wave_line, = ax.plot([], [], 'yellow', lw=2)
wave_x = np.linspace(0, 10, 1000)
wave_y = []

# 动画更新函数
def update(frame):
    time = frame * 0.05
    
    # 更新圆和线
    x, y = 0, 0
    for i in range(n_circles):
        freq = freqs[i]
        radius = radii[i]
        phase = phases[i]
        
        # 计算圆的位置
        prev_x, prev_y = x, y
        x += radius * np.cos(freq * time + phase)
        y += radius * np.sin(freq * time + phase)
        
        # 更新圆和线
        circles[i].center = (prev_x, prev_y)
        lines[i].set_data([prev_x, x], [prev_y, y])
        centers[i].set_data([x], [y])
    
    # 更新波形
    wave_y.append(y)
    if len(wave_y) > len(wave_x):
        wave_y.pop(0)
    # 这一行将 x 坐标向左偏移 5，从而决定了波的运动方向
    xs = (np.array(wave_x[-len(wave_y):]))[::-1]
    wave_line.set_data(xs - 6 + len(xs) / 100, wave_y)  # x反向
    
    # 更新连接线
    connector_line.set_data([x, 4], [y, y])
    
    return circles + lines + centers + [wave_line, connector_line]

# 创建动画
ani = FuncAnimation(fig, update, frames=None, interval=100, blit=True)
plt.tight_layout()
plt.show()
