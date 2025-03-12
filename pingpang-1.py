import pygame
import sys
import random
import colorsys

class GameConfig:
    def __init__(self):
        self.WINDOW_MIN_SIZE = (800, 600)
        self.FPS = 120
        self.DAMPING_FACTOR = 0.98
        self.GRAVITY = 9.8 / self.FPS
        self.BALL_RADIUS = 10
        self.PADDLE_HEIGHT = 20
        self.PADDLE_COLOR = (0, 100, 0)
        self.PADDLE_SPEED = 10
        self.SPRING_WIDTH = 50
        self.SPRING_HEIGHT = 20
        self.SPRING_COLOR = (192, 192, 192)
        self.BACKGROUND_COLOR = (50, 50, 50)
        self.MAX_BALLS = 5
        self.TRAIL_TIME = 2500
        self.BUTTON_RADIUS = 20

class Ball:
    def __init__(self, x, y, radius):
        self.x = x
        self.y = y
        self.radius = radius
        self.speed = [random.uniform(1, 3), random.uniform(1, 3)]
        self.color = self.get_random_color()
        self.trail = []
        self.counter = 0
        # 新增缓存surface以提高性能
        self.trail_surface = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)

    @staticmethod
    def get_random_color():
        while True:
            r, g, b = random.randint(0,255), random.randint(0,255), random.randint(0,255)
            if not (r == g == b):
                return (r, g, b)

    def update(self, gravity, damping_factor):
        self.x += self.speed[0]
        self.y += self.speed[1]
        self.speed[1] += gravity
        self.counter += 1
        if self.counter >= 60:
            self.speed[1] *= damping_factor
            self.counter = 0

    def get_trail_surface(self, color):
        # 缓存trail surface而不是每次重新创建
        pygame.draw.circle(self.trail_surface, color, (self.radius, self.radius), self.radius)
        return self.trail_surface

class Button:
    def __init__(self, center, radius, color, text):
        self.center = center
        self.radius = radius
        self.color = color
        self.text = text
        self.effective_radius = radius

    def is_clicked(self, mouse_pos):
        dx = mouse_pos[0] - self.center[0]
        dy = mouse_pos[1] - self.center[1]
        return (dx*dx + dy*dy) <= self.radius*self.radius

    def update_effect(self, mouse_pressed, mouse_pos):
        if mouse_pressed and self.is_clicked(mouse_pos):
            self.effective_radius = self.radius - 4
        else:
            self.effective_radius = self.radius

class PingPongGame:
    def __init__(self):
        pygame.mixer.pre_init(frequency=44100, size=-16, channels=2, buffer=4096)
        pygame.init()
        self.config = GameConfig()
        self.setup_display()
        self.setup_game_objects()
        self.setup_sound()
        self.setup_controls()

    def setup_display(self):
        self.window_size = self.config.WINDOW_MIN_SIZE
        self.screen = pygame.display.set_mode(self.window_size, pygame.RESIZABLE)
        pygame.display.set_caption("Ping Pong Bounce")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 30)

    def setup_game_objects(self):
        self.paddle_width = self.window_size[0]
        self.paddle_x = 0
        self.paddle_y = self.window_size[1] - self.config.PADDLE_HEIGHT - 10
        
        self.spring_x = (self.window_size[0] - self.config.SPRING_WIDTH) // 2
        self.spring_y = self.paddle_y

        ball_init_x = self.paddle_width / 4
        ball_init_y = self.paddle_y - 200
        self.balls = [Ball(ball_init_x, ball_init_y, self.config.BALL_RADIUS)]

        self.setup_buttons()

    def setup_buttons(self):
        increase_center = (self.window_size[0]//2 + self.config.BUTTON_RADIUS + 10, 
                         10 + self.config.BUTTON_RADIUS)
        decrease_center = (self.window_size[0]//2 - self.config.BUTTON_RADIUS - 10, 
                         10 + self.config.BUTTON_RADIUS)
        
        self.increase_button = Button(increase_center, self.config.BUTTON_RADIUS, (0, 200, 0), "+")
        self.decrease_button = Button(decrease_center, self.config.BUTTON_RADIUS, (200, 0, 0), "-")

    def setup_sound(self):
        pygame.mixer.init()
        self.bounce_sound = pygame.mixer.Sound('pingpang.wav')
        pygame.mixer.music.set_volume(0.5)

    def setup_controls(self):
        self.keys = {
            "LEFT": pygame.K_LEFT,
            "RIGHT": pygame.K_RIGHT,
            "CTRL": pygame.KMOD_CTRL,
            "MINUS": [pygame.K_MINUS, pygame.K_KP_MINUS],
            "PLUS": [pygame.K_PLUS, pygame.K_KP_PLUS, pygame.K_EQUALS]
        }

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            self.handle_resize(event)
            self.handle_mouse_click(event)
            self.handle_keyboard(event)
        return True

    def handle_resize(self, event):
        if event.type == pygame.VIDEORESIZE:
            self.window_size = event.size
            self.screen = pygame.display.set_mode(self.window_size, pygame.RESIZABLE)
            self.update_positions()

    def update_positions(self):
        self.paddle_width = self.window_size[0]
        self.paddle_x = 0
        self.paddle_y = self.window_size[1] - self.config.PADDLE_HEIGHT - 10
        self.spring_x = (self.window_size[0] - self.config.SPRING_WIDTH) // 2
        self.spring_y = self.paddle_y
        self.setup_buttons()

    def handle_mouse_click(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            if self.increase_button.is_clicked(mouse_pos) and len(self.balls) < self.config.MAX_BALLS:
                self.add_ball()
            elif self.decrease_button.is_clicked(mouse_pos) and len(self.balls) > 1:
                self.remove_ball()

    def handle_keyboard(self, event):
        if event.type == pygame.KEYDOWN and event.mod & self.keys["CTRL"]:
            if event.key in self.keys["MINUS"] and len(self.balls) > 1:
                self.remove_ball()
            elif event.key in self.keys["PLUS"] and len(self.balls) < self.config.MAX_BALLS:
                self.add_ball()

    def update(self):
        self.handle_paddle_movement()
        self.update_balls()
        self.update_buttons()

    def handle_paddle_movement(self):
        keys = pygame.key.get_pressed()
        if keys[self.keys["LEFT"]] and self.paddle_x > 0:
            self.paddle_x -= self.config.PADDLE_SPEED
        if keys[self.keys["RIGHT"]] and self.paddle_x < self.window_size[0] - self.paddle_width:
            self.paddle_x += self.config.PADDLE_SPEED

    def update_balls(self):
        current_time = pygame.time.get_ticks()
        for ball in self.balls:
            ball.update(self.config.GRAVITY, self.config.DAMPING_FACTOR)
            self.handle_collisions(ball)
            self.update_trail(ball, current_time)

    def handle_collisions(self, ball):
        # 使用矩形碰撞检测来优化性能
        ball_rect = pygame.Rect(ball.x - ball.radius, 
                              ball.y - ball.radius,
                              ball.radius * 2, 
                              ball.radius * 2)
        
        paddle_rect = pygame.Rect(self.paddle_x, 
                                self.paddle_y,
                                self.paddle_width, 
                                self.config.PADDLE_HEIGHT)
        
        spring_rect = pygame.Rect(self.spring_x,
                                self.spring_y,
                                self.config.SPRING_WIDTH,
                                self.config.SPRING_HEIGHT)
        
        # 墙体碰撞
        if ball.x - ball.radius < 0 or ball.x + ball.radius > self.window_size[0]:
            ball.speed[0] = -ball.speed[0]
            self.bounce_sound.play()
        if ball.y - ball.radius < 0:
            ball.speed[1] = -ball.speed[1]
            self.bounce_sound.play()
            
        # 球拍碰撞
        if ball_rect.colliderect(paddle_rect) and ball.speed[1] > 0:
            # 根据击球位置计算反弹角度
            # hit_pos = (ball.x - self.paddle_x) / self.paddle_width
            # ball.speed[0] = (hit_pos - 0.25) * 10  # 根据击球位置调整水平速度
            ball.speed[1] = -ball.speed[1]
            self.bounce_sound.play()
            
        # 弹簧碰撞
        if ball_rect.colliderect(spring_rect):
            self.handle_spring_collision(ball)

        # 添加球与球之间的碰撞检测
        for other_ball in self.balls:
            if ball is other_ball:
                continue
            
            # 计算两球之间的距离
            dx = ball.x - other_ball.x
            dy = ball.y - other_ball.y
            distance = (dx * dx + dy * dy) ** 0.5
            
            # 如果两球相撞
            if distance < ball.radius + other_ball.radius:
                # 计算碰撞后的速度
                # 于动量守恒和能量守恒的弹性碰撞
                
                # 计算法向量（两球中心连线方向）
                nx = dx / distance
                ny = dy / distance
                
                # 计算相对速度
                dvx = ball.speed[0] - other_ball.speed[0]
                dvy = ball.speed[1] - other_ball.speed[1]
                
                # 计算法向相对速度
                normal_vel = dvx * nx + dvy * ny
                
                # 如果球正在远离，不需要处理碰撞
                if normal_vel > 0:
                    continue
                    
                # 计算冲量
                impulse = -(1 + 0.0) * normal_vel  # 0.8 是弹性系数
                
                # 更新速度
                ball.speed[0] += impulse * nx
                ball.speed[1] += impulse * ny
                other_ball.speed[0] -= impulse * nx
                other_ball.speed[1] -= impulse * ny
                
                # 阻止球重叠
                overlap = (ball.radius + other_ball.radius - distance) / 2
                ball.x += overlap * nx
                ball.y += overlap * ny
                other_ball.x -= overlap * nx
                other_ball.y -= overlap * ny
                
                self.bounce_sound.play()

    def handle_spring_collision(self, ball):
        spring_speed = 5
        if (self.spring_x <= ball.x <= self.spring_x + self.config.SPRING_WIDTH and 
            ball.y + ball.radius >= self.spring_y and 
            ball.y + ball.radius <= self.spring_y + self.config.SPRING_HEIGHT):
            if ball.trail and ball.trail[-1][1] <= self.spring_y:
                ball.speed[1] = -spring_speed
            else:
                ball.speed[1] = -max(abs(ball.speed[1]) * 1.2, spring_speed)
            self.bounce_sound.play()

    def update_trail(self, ball, current_time):
        ball.trail.append((ball.x, ball.y, current_time))
        ball.trail = [pt for pt in ball.trail if current_time - pt[2] <= self.config.TRAIL_TIME]

    def update_buttons(self):
        mouse_pressed = pygame.mouse.get_pressed()[0]
        current_mouse = pygame.mouse.get_pos()
        self.increase_button.update_effect(mouse_pressed, current_mouse)
        self.decrease_button.update_effect(mouse_pressed, current_mouse)

    def draw(self):
        self.screen.fill(self.config.BACKGROUND_COLOR)
        self.draw_buttons()
        self.draw_trails()
        self.draw_balls()
        self.draw_paddle_and_spring()
        pygame.display.flip()

    def draw_buttons(self):
        for button in [self.increase_button, self.decrease_button]:
            pygame.draw.circle(self.screen, button.color, button.center, button.effective_radius)
            text = self.font.render(button.text, True, (255, 255, 255))
            text_rect = text.get_rect(center=button.center)
            self.screen.blit(text, text_rect)

    def draw_trails(self):
        current_time = pygame.time.get_ticks()
        for ball in self.balls:
            if not ball.trail:
                continue
            for tx, ty, t in ball.trail:
                age = current_time - t
                progress = min(1, age / self.config.TRAIL_TIME)
                alpha = int(255 * (1 - progress))
                rgb = colorsys.hsv_to_rgb(progress, 1, 1)
                rainbow_color = (*[int(c*255) for c in rgb], alpha)
                trail_surface = ball.get_trail_surface(rainbow_color)
                self.screen.blit(trail_surface, (int(tx)-ball.radius, int(ty)-ball.radius))

    def draw_balls(self):
        for ball in self.balls:
            pygame.draw.circle(self.screen, ball.color, (int(ball.x), int(ball.y)), ball.radius)

    def draw_paddle_and_spring(self):
        pygame.draw.rect(self.screen, self.config.PADDLE_COLOR, 
                        (self.paddle_x, self.paddle_y, self.paddle_width, self.config.PADDLE_HEIGHT))
        pygame.draw.rect(self.screen, self.config.SPRING_COLOR,
                        (self.spring_x, self.spring_y, self.config.SPRING_WIDTH, self.config.SPRING_HEIGHT))

    def add_ball(self):
        ball_init_x = self.paddle_width / 4
        ball_init_y = self.paddle_y - 200
        self.balls.append(Ball(ball_init_x, ball_init_y, self.config.BALL_RADIUS))

    def remove_ball(self):
        self.balls.pop()

    def run(self):
        running = True
        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(self.config.FPS)

def main():
    game = PingPongGame()
    game.run()

if __name__ == "__main__":
    main()

