import pygame
import sys
import random
import colorsys   # 新增：用于HSV转换

# 初始化Pygame
pygame.mixer.pre_init(frequency=44100, size=-16, channels=2, buffer=4096)
pygame.init()

# 设置窗口大小
minimum_window_size = (800, 600)
window_size = minimum_window_size
screen = pygame.display.set_mode(window_size, pygame.RESIZABLE)
pygame.display.set_caption("Ping Pong Bounce")
damping_factor = 0.98  # 阻尼系数，建议取值范围：(0, 1] 表示每次碰撞后的速度衰减
fps = 60  # 帧率
gravity = 9.8 / fps  # 重力加速度，建议取值范围：[0, 1] 表示每次垂直运动的速度增加

# 新增：返回随机非灰度颜色
def get_random_color():
    while True:
        r, g, b = random.randint(0,255), random.randint(0,255), random.randint(0,255)
        if not (r == g == b):
            return (r, g, b)

# 设置球的属性
ball_radius = 10

# 设置木板的属性
paddle_width = 800
paddle_height = 20
paddle_color = (0, 100, 0)  # 修改为深绿色
paddle_speed = 10

# 新增弹簧的属性
spring_width = 50
spring_height = 20
spring_color = (192, 192, 192)  # 修改为银色
spring_x = (window_size[0] - spring_width) // 2
spring_y = window_size[1] - paddle_height - 10

# 设置声音
pygame.mixer.init()
bounce_sound = pygame.mixer.Sound('pingpang.wav')

# 设置游戏时钟
clock = pygame.time.Clock()

# 定义木板的初始位置
paddle_x = (window_size[0] - paddle_width) // 2
paddle_y = window_size[1] - paddle_height - 10

# 初始化球列表，初始1个球
ball_init_x = paddle_width / 4
ball_init_y = paddle_y - 200
maxballs = 5
balls = [{
    "x": ball_init_x,
    "y": ball_init_y,
    "speed": [random.uniform(1, 3), random.uniform(1, 3)],
    "color": get_random_color(),
    "trail": [],
    "counter": 0
}]

trail_time = 2500  # 轨迹保留时间

# 在主循环开始处（绘制前）新增：按钮配置
button_radius = 20
# 计算左（减号）和右（加号）按钮中心位置，位于屏幕顶端中间（随窗口尺寸调整）
decrease_button_center = (window_size[0]//2 - button_radius - 10, 10 + button_radius)
increase_button_center = (window_size[0]//2 + button_radius + 10, 10 + button_radius)
# 初始化字体
font = pygame.font.Font(None, 30)

# 游戏循环
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        # 新增：处理窗口尺寸改变事件
        if event.type == pygame.VIDEORESIZE:
            window_size = event.size
            screen = pygame.display.set_mode(window_size, pygame.RESIZABLE)
            # 更新地板和弹簧位置及尺寸
            paddle_width = window_size[0]
            paddle_x = (window_size[0] - paddle_width) // 2   # will be 0 if paddle_width equals window width
            paddle_y = window_size[1] - paddle_height - 10
            spring_x = (window_size[0] - spring_width) // 2
            spring_y = window_size[1] - paddle_height - 10
            decrease_button_center = (window_size[0]//2 - button_radius - 10, 10 + button_radius)
            increase_button_center = (window_size[0]//2 + button_radius + 10, 10 + button_radius)

        # 新增：按钮点击检测
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            # 检查点击是否落在圆形增加按钮内
            dx_inc = mouse_pos[0] - increase_button_center[0]
            dy_inc = mouse_pos[1] - increase_button_center[1]
            if (dx_inc*dx_inc + dy_inc*dy_inc) <= button_radius*button_radius and len(balls) < maxballs:
                balls.append({
                    "x": ball_init_x,
                    "y": ball_init_y,
                    "speed": [random.uniform(1, 3), random.uniform(1, 3)],
                    "color": get_random_color(),
                    "trail": [],
                    "counter": 0
                })
            # 检查点击是否落在圆形减少按钮内
            dx_dec = mouse_pos[0] - decrease_button_center[0]
            dy_dec = mouse_pos[1] - decrease_button_center[1]
            if (dx_dec*dx_dec + dy_dec*dy_dec) <= button_radius*button_radius and len(balls) > 1:
                balls.pop()
        # 新增：快捷键支持 Ctrl + '-' 和 Ctrl + '+'
        if event.type == pygame.KEYDOWN:
            if event.mod & pygame.KMOD_CTRL:
                # 控制减少
                if event.key in (pygame.K_MINUS, pygame.K_KP_MINUS):
                    if len(balls) > 1:
                        balls.pop()
                # 控制增加；部分键盘上 '+'可能是 '=' (需 Shift)，也支持数字键盘加号
                elif event.key in (pygame.K_PLUS, pygame.K_KP_PLUS, pygame.K_EQUALS):
                    if len(balls) < maxballs:
                        balls.append({
                            "x": ball_init_x,
                            "y": ball_init_y,
                            "speed": [random.uniform(1, 3), random.uniform(1, 3)],
                            "color": get_random_color(),
                            "trail": [],
                            "counter": 0
                        })

    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] and paddle_x > 0:
        paddle_x -= paddle_speed
    if keys[pygame.K_RIGHT] and paddle_x < window_size[0] - paddle_width:
        paddle_x += paddle_speed

    # 更新每个球的位置和物理状态
    current_time = pygame.time.get_ticks()
    for ball in balls:
        ball["x"] += ball["speed"][0]
        # 更新垂直运动及模拟重力和阻尼，每个球独立计数
        if not (abs(ball["speed"][1]) < 2 and (paddle_y - ball["y"]) < 22):
            ball["speed"][1] += gravity
            ball["y"] += ball["speed"][1]
            ball["counter"] += 1
            if ball["counter"] == 60:
                ball["speed"][1] *= damping_factor
                ball["counter"] = 0
        else:
            ball["speed"][1] = 0
            ball["y"] = paddle_y - ball_radius

        # 球与墙的碰撞检测
        if ball["x"] - ball_radius < 0 or ball["x"] + ball_radius > window_size[0]:
            ball["speed"][0] = -ball["speed"][0]
            bounce_sound.play()
        if ball["y"] - ball_radius < 0:
            ball["speed"][1] = -ball["speed"][1]
            bounce_sound.play()

        # 弹簧碰撞检测
        spring_speed = 5
        if spring_x <= ball["x"] <= spring_x + spring_width and (ball["y"] + ball_radius >= spring_y) and (ball["y"] + ball_radius <= spring_y + spring_height):
            if ball["trail"] and ball["trail"][-1][1] <= spring_y:
                ball["speed"][1] += spring_speed
            else:
                ball["speed"][1] += max(abs(ball["speed"][1]) * 1.2, spring_speed)
            bounce_sound.play()

        # 球与木板的碰撞检测
        if (ball["speed"][1] > 0 and
            paddle_x <= ball["x"] <= paddle_x + paddle_width and
            paddle_y <= ball["y"] + ball_radius):
            ball["speed"][1] = -ball["speed"][1]
            bounce_sound.play()

        # 记录并清理每个球的轨迹（5秒内）
        ball["trail"].append((ball["x"], ball["y"], current_time))
        ball["trail"] = [pt for pt in ball["trail"] if current_time - pt[2] <= trail_time]

    # 绘制场景
    screen.fill((50, 50, 50))  # 修改为深灰色背景
    # 获取鼠标状态以实现按钮按下效果
    mouse_pressed = pygame.mouse.get_pressed()[0]
    current_mouse = pygame.mouse.get_pos()
    eff_increase_radius = button_radius
    eff_decrease_radius = button_radius
    dx_inc = current_mouse[0] - increase_button_center[0]
    dy_inc = current_mouse[1] - increase_button_center[1]
    if mouse_pressed and (dx_inc*dx_inc + dy_inc*dy_inc <= button_radius*button_radius):
        eff_increase_radius = button_radius - 4
    dx_dec = current_mouse[0] - decrease_button_center[0]
    dy_dec = current_mouse[1] - decrease_button_center[1]
    if mouse_pressed and (dx_dec*dx_dec + dy_dec*dy_dec <= button_radius*button_radius):
        eff_decrease_radius = button_radius - 4

    # 绘制圆形按钮及文字（代替原来的矩形按钮）
    pygame.draw.circle(screen, (0, 200, 0), increase_button_center, eff_increase_radius)
    pygame.draw.circle(screen, (200, 0, 0), decrease_button_center, eff_decrease_radius)
    # 绘制文字，水平、垂直居中
    plus_text = font.render("+", True, (255, 255, 255))
    minus_text = font.render("-", True, (255, 255, 255))
    plus_rect = plus_text.get_rect(center=increase_button_center)
    minus_rect = minus_text.get_rect(center=decrease_button_center)
    screen.blit(plus_text, plus_rect)
    screen.blit(minus_text, minus_rect)

    # 新增：绘制每个球的轨迹（彩虹色，越旧越淡）
    for ball in balls:
        tail_eldest = ball["trail"][0][2]  # 最旧的轨迹时间
        tail_newest = ball["trail"][-1][2]   # 最新的轨迹时间
        tail_length = tail_newest - tail_eldest
        # 绘制改为使用彩虹色
        if tail_length > 0:
            for tx, ty, t in ball["trail"]:
                age = current_time - t
                progress = min(1, age / trail_time)
                alpha = int(255 * (1 - progress))
                # 用progress作为hue[0,1]，转换为RGB
                rgb = colorsys.hsv_to_rgb(progress, 1, 1)
                rainbow_color = (int(rgb[0]*255), int(rgb[1]*255), int(rgb[2]*255), alpha)
                trail_surface = pygame.Surface((ball_radius*2, ball_radius*2), pygame.SRCALPHA)
                pygame.draw.circle(trail_surface, rainbow_color, (ball_radius, ball_radius), ball_radius)
                screen.blit(trail_surface, (int(tx)-ball_radius, int(ty)-ball_radius))

    # 绘制每个球
    for ball in balls:
        pygame.draw.circle(screen, ball["color"], (int(ball["x"]), int(ball["y"])), ball_radius)

    pygame.draw.rect(screen, paddle_color, (paddle_x, paddle_y, paddle_width, paddle_height))
    pygame.draw.rect(screen, spring_color, (spring_x, spring_y, spring_width, spring_height))

    pygame.display.flip()

    # 控制帧率
    clock.tick(fps)

