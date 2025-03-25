import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.patches import Circle
from dataclasses import dataclass
from typing import List, Tuple

@dataclass
class AnimationConfig:
    """动画配置类"""
    n_circles: int = 10
    figsize: Tuple[float, float] = (16, 6)
    xlim: Tuple[float, float] = (-3, 13)
    ylim: Tuple[float, float] = (-3, 3)
    update_interval: int = 100
    time_step: float = 0.05
    wave_points: int = 1000
    wave_x_range: Tuple[float, float] = (0, 10)

class FourierAnimation:
    def __init__(self, config: AnimationConfig = AnimationConfig()):
        self.config = config
        self.setup_plot()
        self.setup_animation_objects()
        self.wave_y = np.zeros(self.config.wave_points)
        self.is_paused = False
        
    def setup_plot(self):
        """设置绘图环境"""
        plt.style.use('dark_background')
        self.fig, self.ax = plt.subplots(figsize=self.config.figsize)
        self.ax.set_xlim(*self.config.xlim)
        self.ax.set_ylim(*self.config.ylim)
        self.ax.set_aspect('equal')
        self.ax.axis('off')
        
    def setup_animation_objects(self):
        """初始化动画对象"""
        # 傅立叶级数参数
        self.freqs = np.arange(1, self.config.n_circles + 1)
        self.radii = 4 / (np.pi * self.freqs)
        self.phases = np.random.uniform(0, 2*np.pi, self.config.n_circles)
        
        # 初始化圆和线
        self.circles = []
        self.lines = []
        self.centers = []
        
        for i in range(self.config.n_circles):
            circle = Circle((0, 0), self.radii[i], fill=False, color='cyan', alpha=0.8)
            self.ax.add_patch(circle)
            self.circles.append(circle)
            
            line, = self.ax.plot([], [], 'white', lw=1)
            self.lines.append(line)
            
            center, = self.ax.plot([], [], 'ro', markersize=2)
            self.centers.append(center)
            
        # 初始化波形线和连接线
        self.wave_line, = self.ax.plot([], [], 'yellow', lw=2)
        self.connector_line, = self.ax.plot([], [], 'white', lw=2, alpha=0.5)
        self.wave_x = np.linspace(*self.config.wave_x_range, self.config.wave_points)
        
    def update(self, frame):
        """更新动画帧"""
        if self.is_paused:
            return self.circles + self.lines + self.centers + [self.wave_line, self.connector_line]
            
        time = frame * self.config.time_step
        
        # 使用向量化操作计算圆的位置
        x_coords = np.zeros(self.config.n_circles + 1)
        y_coords = np.zeros(self.config.n_circles + 1)
        
        for i in range(self.config.n_circles):
            freq = self.freqs[i]
            radius = self.radii[i]
            phase = self.phases[i]
            
            x_coords[i+1] = x_coords[i] + radius * np.cos(freq * time + phase)
            y_coords[i+1] = y_coords[i] + radius * np.sin(freq * time + phase)
            
            # 更新圆和线
            self.circles[i].center = (x_coords[i], y_coords[i])
            self.lines[i].set_data([x_coords[i], x_coords[i+1]], 
                                 [y_coords[i], y_coords[i+1]])
            self.centers[i].set_data([x_coords[i+1]], [y_coords[i+1]])
        
        # 更新波形
        self.wave_y = np.roll(self.wave_y, -1)
        self.wave_y[-1] = y_coords[-1]
        
        # 更新波形线
        xs = (np.array(self.wave_x[-len(self.wave_y):]))[::-1]
        self.wave_line.set_data(xs - 6 + len(xs) / 100, self.wave_y)
        
        # 更新连接线
        self.connector_line.set_data([x_coords[-1], 4], [y_coords[-1], y_coords[-1]])
        
        return self.circles + self.lines + self.centers + [self.wave_line, self.connector_line]
    
    def toggle_pause(self, event):
        """切换暂停状态"""
        if event.key == ' ':
            self.is_paused = not self.is_paused
            
    def run(self):
        """运行动画"""
        self.fig.canvas.mpl_connect('key_press_event', self.toggle_pause)
        ani = FuncAnimation(self.fig, self.update, frames=None, 
                          interval=self.config.update_interval, blit=True)
        plt.tight_layout()
        plt.show()

if __name__ == "__main__":
    # 创建自定义配置（可选）
    custom_config = AnimationConfig(
        n_circles=15,  # 增加圆的数量
        update_interval=50,  # 更快的更新速度
        time_step=0.03  # 更小的时间步长
    )
    
    # 创建并运行动画
    animation = FourierAnimation(custom_config)
    animation.run()
