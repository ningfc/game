import pygame
import math
from typing import List, Tuple, Optional
import numpy as np
from dataclasses import dataclass
from tkinter import *
from tkinter import messagebox
from numba import njit
Tk().wm_withdraw() #to hide the main window

# 初始化 Pygame
pygame.init()
clock = pygame.time.Clock()

# 设置窗口
WINDOW_WIDTH = 900
WINDOW_HEIGHT = 900
WIDTH = 800
HEIGHT = 800
pygame.display.set_caption("Multiple Wave Reflection")
try:
    icon = pygame.image.load("simple_wave_reflection.png")
    pygame.display.set_icon(icon)
except Exception as ex:
    messagebox.showinfo("Error", f"Failed to load icon: {str(ex)}")
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))

cursor_surface = pygame.image.load('crosshair.png').convert_alpha()
cursor_rect = cursor_surface.get_rect()
hotspot = (cursor_rect.width // 2, cursor_rect.height // 2)
cursor = pygame.cursors.Cursor(hotspot, cursor_surface)
pygame.mouse.set_cursor(cursor)

# 颜色定义
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)

@dataclass
class WaveConfig:
    WAVE_COUNT = 10      # 每次点击产生的波数
    RADIUS_GAP = 40     # 波之间的半径间隔
    WAVE_SPEED = 1      # 波的扩散速度
    ANGLE_STEP = 1      # 角度步进（越小越平滑）

@njit
def calculate_reflection_numba(coord, min_bound, max_bound):
    total_range = max_bound - min_bound
    relative_pos = coord - min_bound
    n = relative_pos // total_range
    remainder = relative_pos % total_range
    if int(n) % 2 == 0:
        return min_bound + remainder
    else:
        return max_bound - remainder

class Wave:
    color_index = 0
    def __init__(self, x: float, y: float, start_x: float, start_y: float):
        self.type = 0
        self.center_x = x
        self.center_y = y
        self.start_x = start_x
        self.start_y = start_y
        self.radius = 0
        color_index = Wave.color_index
        Wave.color_index = (Wave.color_index + 1) % 3
        self.color = BLUE if color_index == 0 else GREEN if color_index == 1 else RED
        self.speed = 1
        self.points: List[Tuple[float, float]] = []
        # 预计算角度
        # self.angles = np.radians(np.arange(0, 360, WaveConfig.ANGLE_STEP))
        # self.cos_angles = np.cos(self.angles)
        # self.sin_angles = np.sin(self.angles)
        
    def update(self, top_y: float, bottom_y: float, left_x: float, right_x: float):
        self.radius += self.speed
        # if self.radius >= 2400 or self.radius <= 0 :
        #     self.speed *= -1

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
        return calculate_reflection_numba(coord, min_bound, max_bound)
            
    def draw(self, screen):
        # 绘制波前
        if len(self.points) > 1:
            # 平移变换
            translated_points = [(x + self.center_x, y + self.center_y) for x, y in self.points]
            if self.type == 0:
                pygame.draw.lines(screen, self.color, closed=True, points=translated_points, width=3)
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
        self.border = pygame.Rect(-1 * WIDTH//2, -1 * HEIGHT//2, WIDTH, HEIGHT)
        self.waves: List[Wave] = []
        self.paused = False
        self.last_wave_pos = (0, 0)
        self._last_key_time = None
        
    def create_waves(self, x: float, y: float, start_x: float, start_y: float):
        """创建多个同心波"""
        self.waves.clear()  # 清除现有的波
        for i in range(WaveConfig.WAVE_COUNT):
            initial_radius = i * WaveConfig.RADIUS_GAP
            self.waves.append(Wave(x, y, start_x, start_y))
        self.last_wave_pos = (x, y)
        
    def handle_input(self) -> bool:
            
        # current_time = pygame.time.get_ticks()
        # KEY_INTERVAL = 200  # milliseconds interval between get_pressed reads

        # keys = pygame.key.get_pressed()
        # if any(keys):
        #     if self._last_key_time == None or (current_time - self._last_key_time >= KEY_INTERVAL):
        #         self._last_key_time = current_time
        #         x, y = pygame.mouse.get_pos()
        #         if keys[pygame.K_LEFT]:
        #             x = x - 1
        #         if keys[pygame.K_RIGHT]:
        #             x = x + 1
        #         if keys[pygame.K_UP]:
        #             y = y - 1
        #         if keys[pygame.K_DOWN]:
        #             y = y + 1
        #         x = 50 if x < 50 else 850 if x > 850 else x 
        #         y = 50 if y < 50 else 850 if y > 850 else y
        #         pygame.mouse.set_pos(x, y)
        #         print(f'mouse pos = {x},{y}')

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
                
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                    
                elif event.key == pygame.K_SPACE:
                    self.paused = not self.paused
                    
                elif event.key == pygame.K_a:
                    self.waves.clear()
                    x, y = pygame.mouse.get_pos()
                    self.last_wave_pos = (x - WINDOW_WIDTH // 2, y - WINDOW_HEIGHT // 2)
                    self.waves.append(Wave(WINDOW_WIDTH//2, WINDOW_HEIGHT//2, *self.last_wave_pos))
                elif event.key == pygame.K_RETURN:
                    if self.last_wave_pos:
                        self.waves.clear()
                        self.wave = Wave(WINDOW_WIDTH//2, WINDOW_HEIGHT//2, *self.last_wave_pos)
                        self.waves.append(self.wave)
                elif event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT or event.key == pygame.K_UP  or event.key == pygame.K_DOWN:
                    x, y = pygame.mouse.get_pos()
                    if event.key == pygame.K_LEFT:
                        x = x - 1
                    if event.key == pygame.K_RIGHT:
                        x = x + 1
                    if event.key == pygame.K_UP:
                        y = y - 1
                    if event.key == pygame.K_DOWN:
                        y = y + 1
                    pygame.mouse.set_pos(x, y)
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
                    self.waves.append(self.wave)
                    self.last_wave_pos = (pos[0] - WINDOW_WIDTH // 2, pos[1] - WINDOW_HEIGHT // 2)

        return True
        
    def update(self):
        if len(self.waves) > 0 and not self.paused:
            for wave in self.waves:
                wave.update(
                    self.border.top,
                    self.border.bottom,
                    self.border.left,
                    self.border.right
                )
            if len(self.waves) < WaveConfig.WAVE_COUNT and self.waves[-1].radius > WaveConfig.RADIUS_GAP:
                self.waves.append(Wave(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2, *self.last_wave_pos))
            if len(self.waves) >= WaveConfig.WAVE_COUNT and self.waves[0].radius > 1600:
                if self.waves[0].radius > 2400:
                    self.waves.pop(0)
                elif len(self.waves) < WaveConfig.WAVE_COUNT * 2 and self.waves[-1].radius > WaveConfig.RADIUS_GAP:
                    self.waves.append(Wave(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2, *self.last_wave_pos))
            
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
        
        # 绘制所有波
        i = 0
        for wave in self.waves:
            wave.draw(screen)
            i += 1
            
        # 绘制状态信息
        self._draw_status(screen)
        
    def _draw_status(self, screen):
        font = pygame.font.Font(None, 24)

        x, y = 10, 10
        status_texts = [
            "Esc - Exit",
            f'FPS:{int(clock.get_fps())}'
        ]
        for text in status_texts:
            surface = font.render(text, True, GRAY)
            screen.blit(surface, (x, y))
            y += 25

        mouse_x, mouse_y = pygame.mouse.get_pos()
        status_texts = [
            f"Status: {'Paused' if self.paused else 'Running'}",
            f"Mouse: ({mouse_x-50:03d}, {mouse_y-50:03d})"
        ]
        x, y = 100, 10
        for text in status_texts:
            surface = font.render(text, True, GRAY)
            screen.blit(surface, (x, y))
            y += 25

        status_texts = [
            f"Waves: {len(self.waves)}/{WaveConfig.WAVE_COUNT}",
            f"Radius: {0 if len(self.waves) == 0 else self.waves[0].radius}"
        ]
        x, y = 260, 10
        for text in status_texts:
            surface = font.render(text, True, GRAY)
            screen.blit(surface, (x, y))
            y += 25

        status_texts = [
            "Num 0-1 - Type",
            "Click - Start new wave",
        ]
        x, y = 400, 10
        for text in status_texts:
            surface = font.render(text, True, GRAY)
            screen.blit(surface, (x, y))
            y += 25

        status_texts = [
            "Space - Pause/Resume",
            "Enter - Restart last waves",
        ]
        x, y = 600, 10
        for text in status_texts:
            surface = font.render(text, True, GRAY)
            screen.blit(surface, (x, y))
            y += 25

def main():
    simulation = WaveSimulation()
    
    running = True
    while running:
        running = simulation.handle_input()
        simulation.update()
        simulation.draw(screen)
        pygame.display.flip()
        clock.tick(240)

    pygame.quit()

if __name__ == "__main__":
    main()
