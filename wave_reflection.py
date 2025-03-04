import pygame
import math
import numpy as np

# 初始化 Pygame
pygame.init()

# 设置窗口
WIDTH = 800
HEIGHT = 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Wave Reflection Animation")

# 颜色定义
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)

class WavePoint:
    def __init__(self, x, y, center_x, center_y, angle, intensity=255):
        self.x = x
        self.y = y
        self.center_x = center_x  # 波源中心点
        self.center_y = center_y
        self.angle = angle  # 传播方向
        self.intensity = intensity
        self.speed = 2
        self.reflection_count = 0

    def update(self):
        # 计算到波源的距离
        radius = math.sqrt((self.x - self.center_x)**2 + (self.y - self.center_y)**2)
        # 更新位置，保持圆形波前
        self.x = self.center_x + (radius + self.speed) * math.cos(self.angle)
        self.y = self.center_y + (radius + self.speed) * math.sin(self.angle)
        self.intensity = max(0, self.intensity - 0.1)

    def reflect(self, bounds):
        # 计算新的波源位置（镜像位置）
        if self.x <= bounds.left:
            self.center_x = 2 * bounds.left - self.center_x
        elif self.x >= bounds.right:
            self.center_x = 2 * bounds.right - self.center_x
        
        if self.y <= bounds.top:
            self.center_y = 2 * bounds.top - self.center_y
        elif self.y >= bounds.bottom:
            self.center_y = 2 * bounds.bottom - self.center_y
            
        self.reflection_count += 1
        self.intensity *= 0.95

class Wave:
    def __init__(self, x, y):
        self.center_x = x
        self.center_y = y
        self.points = []
        self.create_wave_points()
        
    def create_wave_points(self, num_points=360):
        for i in range(num_points):
            angle = math.radians(i * (360 / num_points))
            x = self.center_x + math.cos(angle)
            y = self.center_y + math.sin(angle)
            self.points.append(WavePoint(x, y, self.center_x, self.center_y, angle))

    def update(self, bounds):
        for point in self.points:
            if point.intensity <= 0:
                continue

            old_x, old_y = point.x, point.y
            point.update()
            
            # 检查边界碰撞
            if (point.x <= bounds.left or point.x >= bounds.right or 
                point.y <= bounds.top or point.y >= bounds.bottom):
                point.reflect(bounds)
                
                # 将点位置限制在边界内
                point.x = max(bounds.left, min(bounds.right, point.x))
                point.y = max(bounds.top, min(bounds.bottom, point.y))

        # 移除强度为0的点
        self.points = [p for p in self.points if p.intensity > 0]

    def draw(self, screen):
        points = [(int(p.x), int(p.y)) for p in self.points if p.intensity > 0]
        if len(points) > 2:
            for i in range(len(points)):
                intensity = self.points[i].intensity
                reflection_count = self.points[i].reflection_count
                color = (
                    min(255, intensity * (reflection_count % 3) / 2),
                    min(255, intensity * ((reflection_count + 1) % 3) / 2),
                    min(255, intensity * ((reflection_count + 2) % 3) / 2)
                )
                next_i = (i + 1) % len(points)
                pygame.draw.line(screen, color, points[i], points[next_i], 2)

def main():
    clock = pygame.time.Clock()
    running = True
    
    # 创建边界矩形
    border = pygame.Rect(50, 50, WIDTH-100, HEIGHT-100)
    
    # 创建初始波
    wave = Wave(WIDTH/2, HEIGHT/2)
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                if border.collidepoint(pos):
                    wave = Wave(pos[0], pos[1])
        
        wave.update(border)
        
        screen.fill(BLACK)
        pygame.draw.rect(screen, WHITE, border, 2)
        wave.draw(screen)
        
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()
