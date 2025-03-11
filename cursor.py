from PIL import Image
import pygame

size = 33
# 创建 16×16 像素的透明图像
img = Image.new('RGBA', (size, size), (0, 0, 0, 0))  # 透明背景
pixels = img.load()

# 绘制水平线（第 8 行）
for x in range(size):
    if x != size // 2:
        pixels[x, size // 2 - 1] = (255, 0, 0, 255)  # 黑色，不透明
        pixels[x, size // 2 + 1] = (255, 0, 0, 255)  # 黑色，不透明

# 绘制垂直线（第 8 列）
for y in range(size):
    if y != size // 2:
        pixels[size // 2 - 1, y] = (255, 0, 0, 255)  # 黑色，不透明
        pixels[size // 2 + 1, y] = (255, 0, 0, 255)  # 黑色，不透明

# 保存图像
img.save("crosshair.png")