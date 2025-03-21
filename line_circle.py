import pygame
import sys
import math

# Initialize Pygame
pygame.display.init()

# Window settings
WIDTH, HEIGHT = 900, 900
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Centered Circle with Border")
clock = pygame.time.Clock()

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)

# Circle properties
circle_radius = 400
center = (WIDTH // 2, HEIGHT // 2)
border_thickness = 5

ball_radius = 20
ball_color = (0, 255, 0, 0)

# Initialize ball states
ball_states = []
num_balls = 16  # 小球数量
angle_step = 360 / num_balls  # 角度步进

for i in range(num_balls):
    angle = i * angle_step
    # 计算初始相位，使小球呈现正弦波分布
    initial_phase = (math.pi * 2 * i) / num_balls  # 在[0, 2π]范围内均匀分布初始相位
    
    ball_states.append({
        'phi': angle,          # 直径的角度
        'phase': initial_phase,  # 初始相位
        'frequency': 0.04,   # 振动频率
        'visible': True
    })

# 新增：定义一个函数，用于优雅地根据角度列表重置 ball_states
def reset_balls(angles):
    global ball_states
    if ball_states:
        for ball_stat in ball_states:
            ball_stat['visible'] = False
        for ball_stat in ball_states:
            if ball_stat['phi'] in angles:
                # ball_stat['phase'] = (math.pi * ball_stat['phi']) / 180
                ball_stat['visible'] = True
    else:
        ball_states = [
        {'phi': angle, 'phase': (math.pi * angle) / 360, 'frequency': 0.03}
        for i, angle in enumerate(angles)
    ]

# 新增：数字键与角度列表的映射
angles_map = {
    pygame.K_0: [0],
    pygame.K_1: [0, 90],
    pygame.K_2: [0, 45, 90],
    pygame.K_3: [0, 45, 90, 135],
    pygame.K_4: [0, 22.5, 45, 90, 135],
    pygame.K_5: [0, 22.5, 45, 67.5, 90, 135],
    pygame.K_6: [0, 22.5, 45, 67.5, 90, 112.5, 135],
    pygame.K_7: [0, 22.5, 45, 67.5, 90, 112.5, 135, 157.5],

    pygame.K_8: [0, 22.5, 45, 67.5, 90, 112.5, 135, 157.5, 180, ],
    pygame.K_9: [0, 22.5, 45, 67.5, 90, 112.5, 135, 157.5, 180, 270],
    pygame.K_a: [0, 22.5, 45, 67.5, 90, 112.5, 135, 157.5, 180, 225, 270],
    pygame.K_b: [0, 22.5, 45, 67.5, 90, 112.5, 135, 157.5, 180, 225, 270, 315],
    pygame.K_c: [0, 22.5, 45, 67.5, 90, 112.5, 135, 157.5, 180, 202.5, 225, 270, 315],
    pygame.K_d: [0, 22.5, 45, 67.5, 90, 112.5, 135, 157.5, 180, 202.5, 225, 247.5, 270, 315],
    pygame.K_e: [0, 22.5, 45, 67.5, 90, 112.5, 135, 157.5, 180, 202.5, 225, 247.5, 270, 292.5, 315],
    pygame.K_f: [0, 22.5, 45, 67.5, 90, 112.5, 135, 157.5, 180, 202.5, 225, 247.5, 270, 292.5, 315, 337.5],
}

# 初始化，默认设置为8个球
reset_balls(angles_map[pygame.K_f])
paused = False  # 新增：动画暂停状态标志

i = 0
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                paused = not paused  # 切换暂停状态
            else:
                new_angles = angles_map.get(event.key)
                if new_angles is not None:
                    reset_balls(new_angles)

    screen.fill(BLACK)
    # pygame.draw.rect(screen, WHITE, (0, 0, WIDTH, HEIGHT), border_thickness)
    pygame.draw.circle(screen, RED, center, circle_radius, 0)

    # Draw diameters
    for ball in ball_states:
        angle = ball['phi']
        rad = math.radians(angle)
        x_offset = circle_radius * math.cos(rad)
        y_offset = circle_radius * math.sin(rad)
        start = (center[0] - x_offset, center[1] - y_offset)
        end = (center[0] + x_offset, center[1] + y_offset)
        pygame.draw.line(screen, BLACK, start, end, 1)

    # Update and draw balls
    for ball in ball_states:
        rad = math.radians(ball['phi'])
        x_offset = circle_radius * math.cos(rad)
        y_offset = circle_radius * math.sin(rad)
        
        # 使用正弦函数计算位置参数 t (范围在 0 到 1 之间)
        t = (math.sin(ball['phase']) + 1) / 2
        # print(t)
        # 仅在未暂停时更新相位
        if not paused:
            ball['phase'] += ball['frequency']
        ball['phase'] = ball['phase'] % (math.pi * 2)

        # 计算球的实际位置
        color = ball_color
        if ball['phi'] >= 180:
            color = (0, 0, 255, 0)
            ball_x = center[0] + x_offset - 2 * x_offset * t
            ball_y = center[1] + y_offset - 2 * y_offset * t
        else: 
            ball_x = center[0] - x_offset + 2 * x_offset * t
            ball_y = center[1] - y_offset + 2 * y_offset * t
           
        if ball['visible']: 
            pygame.draw.circle(screen, color, (int(ball_x), int(ball_y)), ball_radius)

    # print(ball_states[0]['phase'])
    pygame.font.init()
    font = pygame.font.Font(None, 24)
    # surface = font.render(f'{ball_states[0]['phase']}', True, WHITE)
    surface = font.render(f'FPS:{int(clock.get_fps())}', True, WHITE)
    screen.blit(surface, (50, 50))
    if ball_states[0]['phase'] % (math.pi) <= ball_states[0]['frequency'] and i < 16:
        print(i)
        new_angles = sorted(angles_map.items())[i % 16][1]
        if new_angles is not None:
            reset_balls(new_angles)
        i = i + 1

    pygame.display.flip()
    clock.tick(60)
