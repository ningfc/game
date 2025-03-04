import pygame
import math
from typing import List, Tuple, Optional
import numpy as np

# 初始化 Pygame
pygame.init()

# 设置窗口
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 800
WIDTH = 600
HEIGHT = 600
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Simple Wave Reflection")

# 颜色定义
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)

class Wave:
    def __init__(self, x: float, y: float, start_x: float, start_y: float):
        self.type = 0
        self.center_x = x
        self.center_y = y
        self.start_x = start_x
        self.start_y = start_y
        self.radius = 0
        self.speed = 1
        self.points: List[Tuple[float, float]] = []
        # 预计算角度，避免重复计算
        self.angles = np.radians(np.arange(0, 360, 1))
        self.cos_angles = np.cos(self.angles)
        self.sin_angles = np.sin(self.angles)
        
    def update(self, top_y, bottom_y, left_x, right_x):
        self.radius += self.speed
        if self.radius >= 2400 or self.radius <= 0 :
            self.speed *= -1
        
        # 使用numpy进行向量化计算
        if self.type == 0:
            num_points = max(360, self.radius)
            angles = np.radians(np.arange(0, 360, 1 / (num_points / 360)))
        else:
            angles = [angle for angle in range(0, max(360, self.radius), 1)] ## 直接用角，有另一种效果
        x_coords = self.start_x + self.radius * np.cos(angles)
        y_coords = self.start_y + self.radius * np.sin(angles)
        
        # 向量化处理反射
        self.points = []
        for x, y in zip(x_coords, y_coords):
            actual_x = self._calculate_reflection(x, left_x, right_x)
            actual_y = self._calculate_reflection(y, top_y, bottom_y)
            self.points.append((actual_x, actual_y))
    
    def _calculate_reflection(self, coord: float, min_bound: float, max_bound: float) -> float:
        """优化的反射计算"""
        total_range = max_bound - min_bound
        relative_pos = coord - min_bound
        
        # 计算在边界范围内的等效位置
        n = relative_pos // total_range
        remainder = relative_pos % total_range
        
        if int(n) % 2 == 0:
            return min_bound + remainder
        else:
            return max_bound - remainder
            
    def draw(self, screen):
        # 绘制波前
        if len(self.points) > 1:
            # 平移变换
            translated_points = [(x + self.center_x, y + self.center_y) for x, y in self.points]
            if self.type == 0:
                pygame.draw.lines(screen, WHITE, closed=True, points=translated_points, width=1)
            elif len(translated_points) >= 7:
                # 创建彩虹色
                rainbow_colors = [
                    (255, 0, 0),    # 红
                    (255, 127, 0),  # 橙
                    (255, 255, 0),  # 黄
                    (0, 255, 0),    # 绿
                    (0, 0, 255),    # 蓝
                    (75, 0, 130),   # 靛
                    (143, 0, 255)   # 紫
                ]
                # 绘制彩虹色线条
                for i in range(len(translated_points) - 1):
                    pygame.draw.line(screen, rainbow_colors[i % len(rainbow_colors)], translated_points[i], translated_points[i + 1], width=2)

                # 连接最后一个点和第一个点
                pygame.draw.line(screen, rainbow_colors[-1], translated_points[-1], translated_points[0], width=2)

class WaveSimulation:
    def __init__(self):
        self.border = pygame.Rect(-300, -300, WIDTH, HEIGHT)
        self.wave: Optional[Wave] = None
        self.paused = False
        self.last_wave_pos = (0,0)
        
    def handle_input(self) -> bool:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
                
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                    
                elif event.key == pygame.K_SPACE:
                    self.paused = not self.paused
                    
                elif event.key == pygame.K_RETURN:
                    if self.last_wave_pos:
                        self.wave = Wave(WINDOW_WIDTH//2, WINDOW_HEIGHT//2, *self.last_wave_pos)
                elif event.key == pygame.K_0:
                    self.wave.type = 0
                elif event.key == pygame.K_1:
                    self.wave.type = 1
                        
            elif event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                translated_border = pygame.Rect(
                    self.border.x + WINDOW_WIDTH // 2,
                    self.border.y + WINDOW_HEIGHT // 2,
                    self.border.width,
                    self.border.height
                )
                if translated_border.collidepoint(pos):
                    self.wave = Wave(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2, pos[0] - WINDOW_WIDTH // 2, pos[1] - WINDOW_HEIGHT // 2)
                    self.last_wave_pos = (pos[0] - WINDOW_WIDTH // 2, pos[1] - WINDOW_HEIGHT // 2)
        
        return True
        
    def update(self):
        if not self.paused and self.wave:
            self.wave.update(
                self.border.top,
                self.border.bottom,
                self.border.left,
                self.border.right
            )
            
    def draw(self, screen):
        # 清屏
        screen.fill(BLACK)
        
        # 绘制边界
        translated_border = pygame.Rect(
            self.border.x + WINDOW_WIDTH // 2,
            self.border.y + WINDOW_HEIGHT // 2,
            self.border.width,
            self.border.height
        )
        pygame.draw.rect(screen, WHITE, translated_border, 2)
        
        # 绘制波
        if self.wave:
            self.wave.draw(screen)
            
        # 绘制状态信息
        self._draw_status(screen)
        
    def _draw_status(self, screen):
        font = pygame.font.Font(None, 24)
        status_texts = [
            "Num 0-1 - Type",
            "Click - Start new wave",
            "Space - Pause/Resume",
            "Enter - Restart last wave",
        ]
        
        surface = font.render("Esc - Exit", True, GRAY)
        x = 10
        y = 10
        screen.blit(surface, (x, y))

        x = 100
        for text in status_texts:
            surface = font.render(text, True, GRAY)
            screen.blit(surface, (x, y))
            y += 25

        surface = font.render(f"Status: {'Paused' if self.paused else 'Running'}", True, GRAY)
        screen.blit(surface, (300, 10))

def main():
    clock = pygame.time.Clock()
    simulation = WaveSimulation()
    
    running = True
    while running:
        # 处理输入
        running = simulation.handle_input()
        
        # 更新
        simulation.update()
        
        # 绘制
        simulation.draw(screen)
        
        # 刷新显示
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()
