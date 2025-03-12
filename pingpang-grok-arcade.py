# pingpang-grok-arcade.py
import arcade
import random
import colorsys
import time  # added import for time module

class GameConfig:
    def __init__(self):
        self.WINDOW_MIN_SIZE = (800, 600)
        self.FPS = 110
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

    @staticmethod
    def get_random_color():
        while True:
            r, g, b = random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)
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
        return (dx * dx + dy * dy) <= self.radius * self.radius

    def update_effect(self, mouse_pressed, mouse_pos):
        if mouse_pressed and self.is_clicked(mouse_pos):
            self.effective_radius = self.radius - 4
        else:
            self.effective_radius = self.radius

class PingPongGame(arcade.Window):
    def __init__(self):
        super().__init__(*GameConfig().WINDOW_MIN_SIZE, "Ping Pong Bounce", resizable=True)
        self.game_config = GameConfig()
        arcade.set_background_color(self.game_config.BACKGROUND_COLOR)
        self.set_update_rate(1 / self.game_config.FPS)
        self.setup_game_objects()
        self.setup_sound()
        self.setup_controls()
        # Add attributes for mouse state
        self.mouse_pressed = False
        self.mouse_pos = (0, 0)

    def setup_game_objects(self):
        self.window_size = self.width, self.height
        self.paddle_width = self.window_size[0]
        self.paddle_x = 0
        self.paddle_y = self.window_size[1] - self.game_config.PADDLE_HEIGHT - 10
        self.spring_x = (self.window_size[0] - self.game_config.SPRING_WIDTH) // 2
        self.spring_y = self.paddle_y

        ball_init_x = self.paddle_width / 4
        ball_init_y = self.paddle_y - 200
        self.balls = [Ball(ball_init_x, ball_init_y, self.game_config.BALL_RADIUS)]

        self.setup_buttons()

    def setup_buttons(self):
        increase_center = (self.window_size[0] // 2 + self.game_config.BUTTON_RADIUS + 10,
                           10 + self.game_config.BUTTON_RADIUS)
        decrease_center = (self.window_size[0] // 2 - self.game_config.BUTTON_RADIUS - 10,
                           10 + self.game_config.BUTTON_RADIUS)
        self.increase_button = Button(increase_center, self.game_config.BUTTON_RADIUS, (0, 200, 0), "+")
        self.decrease_button = Button(decrease_center, self.game_config.BUTTON_RADIUS, (200, 0, 0), "-")

    def setup_sound(self):
        self.bounce_sound = arcade.Sound("pingpang.wav")

    def setup_controls(self):
        self.left_pressed = False
        self.right_pressed = False
        self.ctrl_pressed = False

    def on_resize(self, width, height):
        super().on_resize(width, height)
        self.window_size = (width, height)
        self.update_positions()

    def update_positions(self):
        self.paddle_width = self.window_size[0]
        self.paddle_x = 0
        self.paddle_y = self.window_size[1] - self.game_config.PADDLE_HEIGHT - 10
        self.spring_x = (self.window_size[0] - self.game_config.SPRING_WIDTH) // 2
        self.spring_y = self.paddle_y
        self.setup_buttons()

    def on_mouse_press(self, x, y, button, modifiers):
        self.mouse_pressed = True
        self.mouse_pos = (x, y)
        mouse_pos = (x, y)
        if button == arcade.MOUSE_BUTTON_LEFT:
            if self.increase_button.is_clicked(self.mouse_pos) and len(self.balls) < self.game_config.MAX_BALLS:
                self.add_ball()
            elif self.decrease_button.is_clicked(self.mouse_pos) and len(self.balls) > 1:
                self.remove_ball()

    def on_mouse_release(self, x, y, button, modifiers):
        self.mouse_pressed = False
        self.mouse_pos = (x, y)

    def on_mouse_motion(self, x, y, dx, dy):
        self.mouse_pos = (x, y)

    def on_key_press(self, key, modifiers):
        if key == arcade.key.LEFT:
            self.left_pressed = True
        elif key == arcade.key.RIGHT:
            self.right_pressed = True
        elif key == arcade.key.LCTRL or key == arcade.key.RCTRL:
            self.ctrl_pressed = True
        elif self.ctrl_pressed:
            if key in (arcade.key.MINUS, arcade.key.KEYPAD_MINUS) and len(self.balls) > 1:
                self.remove_ball()
            elif key in (arcade.key.PLUS, arcade.key.KEYPAD_PLUS, arcade.key.EQUALS) and len(self.balls) < self.game_config.MAX_BALLS:
                self.add_ball()

    def on_key_release(self, key, modifiers):
        if key == arcade.key.LEFT:
            self.left_pressed = False
        elif key == arcade.key.RIGHT:
            self.right_pressed = False
        elif key == arcade.key.LCTRL or key == arcade.key.RCTRL:
            self.ctrl_pressed = False

    def on_update(self, delta_time):
        self.handle_paddle_movement()
        self.update_balls()
        self.update_buttons()

    def handle_paddle_movement(self):
        if self.left_pressed and self.paddle_x > 0:
            self.paddle_x -= self.game_config.PADDLE_SPEED
        if self.right_pressed and self.paddle_x < self.window_size[0] - self.paddle_width:
            self.paddle_x += self.game_config.PADDLE_SPEED

    def update_balls(self):
        current_time = time.time() * 1000  # Arcade 时间单位为秒，转换为毫秒
        for ball in self.balls:
            ball.update(self.game_config.GRAVITY, self.game_config.DAMPING_FACTOR)
            self.handle_collisions(ball)
            self.update_trail(ball, current_time)

    def handle_collisions(self, ball):
        # 墙体碰撞
        if ball.x - ball.radius < 0 or ball.x + ball.radius > self.window_size[0]:
            ball.speed[0] = -ball.speed[0]
            self.bounce_sound.play()
        if ball.y - ball.radius < 0:
            ball.speed[1] = -ball.speed[1]
            self.bounce_sound.play()

        # 球拍碰撞
        paddle_rect = (self.paddle_x, self.paddle_y, self.paddle_width, self.game_config.PADDLE_HEIGHT)
        if (ball.x + ball.radius > paddle_rect[0] and ball.x - ball.radius < paddle_rect[0] + paddle_rect[2] and
            ball.y + ball.radius > paddle_rect[1] and ball.y - ball.radius < paddle_rect[1] + paddle_rect[3] and
            ball.speed[1] > 0):
            ball.speed[1] = -ball.speed[1]
            self.bounce_sound.play()

        # 弹簧碰撞
        spring_rect = (self.spring_x, self.spring_y, self.game_config.SPRING_WIDTH, self.game_config.SPRING_HEIGHT)
        if (ball.x + ball.radius > spring_rect[0] and ball.x - ball.radius < spring_rect[0] + spring_rect[2] and
            ball.y + ball.radius > spring_rect[1] and ball.y - ball.radius < spring_rect[1] + spring_rect[3]):
            self.handle_spring_collision(ball)

        # 球与球碰撞
        for other_ball in self.balls:
            if ball is other_ball:
                continue
            dx = ball.x - other_ball.x
            dy = ball.y - other_ball.y
            distance = (dx * dx + dy * dy) ** 0.5
            if distance < ball.radius + other_ball.radius:
                nx = dx / distance
                ny = dy / distance
                dvx = ball.speed[0] - other_ball.speed[0]
                dvy = ball.speed[1] - other_ball.speed[1]
                normal_vel = dvx * nx + dvy * ny
                if normal_vel > 0:
                    continue
                impulse = -(1 + 0.0) * normal_vel
                ball.speed[0] += impulse * nx
                ball.speed[1] += impulse * ny
                other_ball.speed[0] -= impulse * nx
                other_ball.speed[1] -= impulse * ny
                overlap = (ball.radius + other_ball.radius - distance) / 2
                ball.x += overlap * nx
                ball.y += overlap * ny
                other_ball.x -= overlap * nx
                other_ball.y -= overlap * ny
                self.bounce_sound.play()

    def handle_spring_collision(self, ball):
        spring_speed = 5
        if (self.spring_x <= ball.x <= self.spring_x + self.game_config.SPRING_WIDTH and
            ball.y + ball.radius >= self.spring_y and
            ball.y + ball.radius <= self.spring_y + self.game_config.SPRING_HEIGHT):
            if ball.trail and ball.trail[-1][1] <= self.spring_y:
                ball.speed[1] = -spring_speed
            else:
                ball.speed[1] = -max(abs(ball.speed[1]) * 1.2, spring_speed)
            self.bounce_sound.play()

    def update_trail(self, ball, current_time):
        ball.trail.append((ball.x, ball.y, current_time))
        ball.trail = [pt for pt in ball.trail if current_time - pt[2] <= self.game_config.TRAIL_TIME]

    def update_buttons(self):
        # Use stored mouse state instead of arcade.get_mouse_buttons() and arcade.get_mouse_position()
        self.increase_button.update_effect(self.mouse_pressed, self.mouse_pos)
        self.decrease_button.update_effect(self.mouse_pressed, self.mouse_pos)

    def on_draw(self):
        self.clear()
        self.draw_buttons()
        self.draw_trails()
        self.draw_balls()
        self.draw_paddle_and_spring()

    def draw_buttons(self):
        for button in [self.increase_button, self.decrease_button]:
            arcade.draw_circle_filled(button.center[0], button.center[1], button.effective_radius, button.color)
            arcade.draw_text(button.text, button.center[0], button.center[1], arcade.color.WHITE,
                             font_size=20, anchor_x="center", anchor_y="center")

    def draw_trails(self):
        current_time = time.time() * 1000  # replaced arcade.get_time() with time.time()
        for ball in self.balls:
            if not ball.trail:
                continue
            for tx, ty, t in ball.trail:
                age = current_time - t
                progress = min(1, age / self.game_config.TRAIL_TIME)
                alpha = int(255 * (1 - progress))
                rgb = colorsys.hsv_to_rgb(progress, 1, 1)
                rainbow_color = (*[int(c * 255) for c in rgb], alpha)
                arcade.draw_circle_filled(tx, ty, ball.radius, rainbow_color)

    def draw_balls(self):
        for ball in self.balls:
            arcade.draw_circle_filled(ball.x, ball.y, ball.radius, ball.color)

    def draw_paddle_and_spring(self):
        arcade.draw_lbwh_rectangle_filled(self.paddle_x + self.paddle_width / 2, self.paddle_y + self.game_config.PADDLE_HEIGHT / 2,
                                     self.paddle_width, self.game_config.PADDLE_HEIGHT, self.game_config.PADDLE_COLOR)
        arcade.draw_lbwh_rectangle_filled(self.spring_x + self.game_config.SPRING_WIDTH / 2, self.spring_y + self.game_config.SPRING_HEIGHT / 2,
                                     self.game_config.SPRING_WIDTH, self.game_config.SPRING_HEIGHT, self.game_config.SPRING_COLOR)

    def add_ball(self):
        ball_init_x = self.paddle_width / 4
        ball_init_y = self.paddle_y - 200
        self.balls.append(Ball(ball_init_x, ball_init_y, self.game_config.BALL_RADIUS))

    def remove_ball(self):
        self.balls.pop()

def main():
    game = PingPongGame()
    arcade.run()

if __name__ == "__main__":
    main()