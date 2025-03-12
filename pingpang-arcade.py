import arcade
import random
import time
import colorsys

class GameConfig:
    def __init__(self):
        self.WINDOW_MIN_SIZE = (800, 600)
        self.FPS = 110
        self.DAMPING_FACTOR = 0.98
        self.GRAVITY = -9.8 / self.FPS
        self.BALL_RADIUS = 10
        self.PADDLE_HEIGHT = 20
        self.PADDLE_COLOR = arcade.color.DARK_GREEN
        self.PADDLE_SPEED = 10
        self.SPRING_WIDTH = 50
        self.SPRING_HEIGHT = 20
        self.SPRING_COLOR = arcade.color.LIGHT_GRAY
        self.BACKGROUND_COLOR = arcade.color.DARK_GRAY
        self.MAX_BALLS = 5
        self.TRAIL_TIME = 2.5  # in seconds
        self.BUTTON_RADIUS = 20

class Ball:
    def __init__(self, x, y, radius, config: GameConfig):
        self.x = x
        self.y = y
        self.radius = radius
        self.speed = [random.uniform(1, 3), random.uniform(1, 3)]
        self.color = self.get_random_color()
        self.trail = []  # list of (x, y, timestamp)
        self.game_config = config

    @staticmethod
    def get_random_color():
        while True:
            r, g, b = random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)
            if not (r == g == b):
                return (r, g, b)

    def update(self, delta_time):
        self.x += self.speed[0]
        self.y += self.speed[1]
        self.speed[1] += self.game_config.GRAVITY
        self.speed[1] *= self.game_config.DAMPING_FACTOR

    def update_trail(self):
        current_time = time.time()
        self.trail.append((self.x, self.y, current_time))
        self.trail = [pt for pt in self.trail if current_time - pt[2] <= self.game_config.TRAIL_TIME]

class Button:
    def __init__(self, center, radius, color, text):
        self.center = center
        self.radius = radius
        self.color = color
        self.text = text
        self.effective_radius = radius

    def is_clicked(self, x, y):
        dx = x - self.center[0]
        dy = y - self.center[1]
        return (dx * dx + dy * dy) <= self.radius * self.radius

    def update_effect(self, clicked, x, y):
        if clicked and self.is_clicked(x, y):
            self.effective_radius = self.radius - 4
        else:
            self.effective_radius = self.radius

class PingPongGame(arcade.Window):
    def __init__(self):
        self.game_config = GameConfig()
        width, height = self.game_config.WINDOW_MIN_SIZE
        super().__init__(width, height, "Ping Pong Bounce")
        arcade.set_background_color(self.game_config.BACKGROUND_COLOR)
        self.paddle_width = self.width
        self.paddle_x = 0
        self.paddle_y = 20
        self.spring_x = (self.width - self.game_config.SPRING_WIDTH) // 2
        self.spring_y = self.paddle_y
        ball_init_x = self.width / 4
        ball_init_y = self.paddle_y + 200
        self.balls = [Ball(ball_init_x, ball_init_y, self.game_config.BALL_RADIUS, self.game_config)]
        self.setup_buttons()
        self.left_pressed = False
        self.right_pressed = False

    def setup_buttons(self):
        self.increase_button = Button(
            (self.width // 2 + self.game_config.BUTTON_RADIUS + 10, self.height - self.game_config.BUTTON_RADIUS - 10),
            self.game_config.BUTTON_RADIUS, arcade.color.GREEN, "+"
        )
        self.decrease_button = Button(
            (self.width // 2 - self.game_config.BUTTON_RADIUS - 10, self.height - self.game_config.BUTTON_RADIUS - 10),
            self.game_config.BUTTON_RADIUS, arcade.color.RED, "-"
        )

    def on_draw(self):
        self.clear()
        # Draw buttons
        for button in [self.increase_button, self.decrease_button]:
            arcade.draw_circle_filled(button.center[0], button.center[1], button.effective_radius, button.color)
            arcade.draw_text(
                button.text, button.center[0], button.center[1],
                arcade.color.WHITE, 14, align="center", anchor_x="center", anchor_y="center"
            )
        # Draw ball trails
        current_time = time.time()
        for ball in self.balls:
            for (tx, ty, t) in ball.trail:
                progress = min(1, (current_time - t) / self.game_config.TRAIL_TIME)
                alpha = int(255 * (1 - progress))
                rgb = colorsys.hsv_to_rgb(progress, 1, 1)
                trail_color = (int(rgb[0]*255), int(rgb[1]*255), int(rgb[2]*255), alpha)
                arcade.draw_circle_filled(tx, ty, ball.radius, trail_color)
        # Draw balls
        for ball in self.balls:
            arcade.draw_circle_filled(ball.x, ball.y, ball.radius, ball.color)
        # Draw paddle and spring
        arcade.draw_lbwh_rectangle_filled(
            self.paddle_x, # + self.paddle_width / 2, 
            self.paddle_y + self.game_config.PADDLE_HEIGHT / 2,
            self.paddle_width, 
            self.game_config.PADDLE_HEIGHT, 
            self.game_config.PADDLE_COLOR
        )
        arcade.draw_lbwh_rectangle_filled(
            self.spring_x + self.game_config.SPRING_WIDTH / 2, 
            self.spring_y + self.game_config.SPRING_HEIGHT / 2,
            self.game_config.SPRING_WIDTH, 
            self.game_config.SPRING_HEIGHT, 
            self.game_config.SPRING_COLOR
        )

    def on_update(self, delta_time):
        if self.left_pressed and self.paddle_x > 0:
            self.paddle_x -= self.game_config.PADDLE_SPEED
        if self.right_pressed and self.paddle_x < self.width - self.paddle_width:
            self.paddle_x += self.game_config.PADDLE_SPEED
        for ball in self.balls:
            ball.update(delta_time)
            ball.update_trail()
            self.handle_collisions(ball)

    def handle_collisions(self, ball):
        # Wall collisions
        if ball.x - ball.radius < 0 or ball.x + ball.radius > self.width:
            ball.speed[0] *= -1
        if ball.y - ball.radius < 0 or ball.y + ball.radius > self.height:
            ball.speed[1] *= -1
        # Paddle collision
        paddle_bottom = self.paddle_y
        paddle_top = self.paddle_y + self.game_config.PADDLE_HEIGHT
        if (paddle_bottom <= ball.y - ball.radius <= paddle_top) and (self.paddle_x <= ball.x <= self.paddle_x + self.paddle_width) and ball.speed[1] < 0:
            ball.speed[1] *= -1
        # Spring collision
        spring_left = self.spring_x
        spring_right = self.spring_x + self.game_config.SPRING_WIDTH
        if (spring_left <= ball.x <= spring_right) and (ball.y - ball.radius <= self.spring_y + self.game_config.SPRING_HEIGHT):
            ball.speed[1] = -abs(ball.speed[1]) * 1.2
        # Ball-ball collisions (simplified)
        for other in self.balls:
            if other is ball:
                continue
            dx = ball.x - other.x
            dy = ball.y - other.y
            distance = (dx**2 + dy**2) ** 0.5
            if distance < ball.radius + other.radius:
                nx = dx / distance
                ny = dy / distance
                dvx = ball.speed[0] - other.speed[0]
                dvy = ball.speed[1] - other.speed[1]
                normal_vel = dvx * nx + dvy * ny
                if normal_vel > 0:
                    continue
                impulse = -normal_vel
                ball.speed[0] += impulse * nx
                ball.speed[1] += impulse * ny
                other.speed[0] -= impulse * nx
                other.speed[1] -= impulse * ny
                overlap = (ball.radius + other.radius - distance) / 2
                ball.x += overlap * nx
                ball.y += overlap * ny
                other.x -= overlap * nx
                other.y -= overlap * ny

    def on_key_press(self, key, modifiers):
        if key == arcade.key.LEFT:
            self.left_pressed = True
        elif key == arcade.key.RIGHT:
            self.right_pressed = True
        if modifiers & arcade.key.MOD_CTRL:
            if key == arcade.key.MINUS and len(self.balls) > 1:
                self.remove_ball()
            elif key in (arcade.key.PLUS, arcade.key.EQUAL) and len(self.balls) < self.game_config.MAX_BALLS:
                self.add_ball()

    def on_key_release(self, key, modifiers):
        if key == arcade.key.LEFT:
            self.left_pressed = False
        elif key == arcade.key.RIGHT:
            self.right_pressed = False

    def on_mouse_press(self, x, y, button, modifiers):
        clicked = True
        self.increase_button.update_effect(clicked, x, y)
        self.decrease_button.update_effect(clicked, x, y)
        if self.increase_button.is_clicked(x, y) and len(self.balls) < self.game_config.MAX_BALLS:
            self.add_ball()
        elif self.decrease_button.is_clicked(x, y) and len(self.balls) > 1:
            self.remove_ball()

    def add_ball(self):
        ball_init_x = self.width / 4
        ball_init_y = self.paddle_y + 200
        self.balls.append(Ball(ball_init_x, ball_init_y, self.game_config.BALL_RADIUS, self.game_config))

    def remove_ball(self):
        if self.balls:
            self.balls.pop()

def main():
    game = PingPongGame()
    arcade.run()

if __name__ == "__main__":
    main()

