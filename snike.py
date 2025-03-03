
import pygame
import sys
import random
import time

pygame.init()

# 游戏窗口设置
WIDTH = 800
HEIGHT = 600
CELL_SIZE = 20
GRID_WIDTH = WIDTH // CELL_SIZE
GRID_HEIGHT = HEIGHT // CELL_SIZE
BOUND = 3

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Snake Game')
clock = pygame.time.Clock()

# 颜色定义
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

snake_positions = [(100, 100), (80, 100), (60, 100)]
food_position = (300, 300)
snake_direction = (CELL_SIZE, 0)

def draw_objects():
    for position in snake_positions:
        pygame.draw.rect(screen, GREEN, pygame.Rect(position[0], position[1], CELL_SIZE, CELL_SIZE))
    pygame.draw.rect(screen, RED, pygame.Rect(food_position[0], food_position[1], CELL_SIZE, CELL_SIZE))

def move_snake():
    global snake_positions, snake_direction

    head_x, head_y = snake_positions[0]
    new_head_position = (head_x + snake_direction[0], head_y + snake_direction[1])

    snake_positions = [new_head_position] + snake_positions[:-1]
    time.sleep(0.3)

def check_food_collision():
    global snake_positions, food_position

    if snake_positions[0] == food_position:
        food_position = (random.randint(BOUND, GRID_WIDTH - 1 - BOUND) * CELL_SIZE, random.randint(BOUND, GRID_HEIGHT - 1 - BOUND) * CELL_SIZE)
        snake_positions.append(snake_positions[-1])
        return True
    return False

def check_collision():
    head_x, head_y = snake_positions[0]

    # 检查自身碰撞
    if (head_x, head_y) in snake_positions[1:]:
        return True

    # 检查墙壁碰撞
    if head_x < 0 or head_x >= WIDTH or head_y < 0 or head_y >= HEIGHT:
        return True

    return False

def handle_input():
    global snake_direction

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP and snake_direction != (0, CELL_SIZE):
                snake_direction = (0, -CELL_SIZE)
            elif event.key == pygame.K_DOWN and snake_direction != (0, -CELL_SIZE):
                snake_direction = (0, CELL_SIZE)
            elif event.key == pygame.K_LEFT and snake_direction != (CELL_SIZE, 0):
                snake_direction = (-CELL_SIZE, 0)
            elif event.key == pygame.K_RIGHT and snake_direction != (-CELL_SIZE, 0):
                snake_direction = (CELL_SIZE, 0)

while True:
    handle_input()
    move_snake()
    if check_collision():
        break
    if check_food_collision():
        print("Yummy! The score is: ", len(snake_positions) - 3)

    screen.fill(WHITE)
    draw_objects()
    pygame.display.update()



