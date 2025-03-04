import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import random
import math
import numpy as np

class GameConfig:
    def __init__(self):
        self.WINDOW_SIZE = (800, 600)
        self.FPS = 60
        self.BOX_SIZE = 100.0  # 立方体盒子的大小
        self.BALL_RADIUS = 5.0
        self.MAX_BALLS = 5
        self.DAMPING = 0.99    # 碰撞后的能量损失
        self.GRAVITY = 9.8 / 60  # 重力加速度
        # 弹簧配置
        self.SPRING_WIDTH = 20.0
        self.SPRING_HEIGHT = 5.0
        self.SPRING_DEPTH = 20.0
        self.SPRING_SPEED = 15.0  # 与pingpang.py保持一致的弹跳速度

class Ball:
    def __init__(self, radius):
        self.radius = radius
        self.position = np.array([0.0, 0.0, 50.0])  # 从顶部开始
        self.velocity = np.array([
            random.uniform(-2, 2),
            random.uniform(-2, 2),
            random.uniform(-2, -1)
        ])
        self.color = (
            random.uniform(0.5, 1.0),
            random.uniform(0.5, 1.0),
            random.uniform(0.5, 1.0)
        )
        self.quadric = gluNewQuadric()
        
    def update(self, box_size, gravity, damping):
        # 更新位置
        self.position += self.velocity
        self.velocity[2] -= gravity  # 添加重力
        
        # 碰撞检测和处理
        for i in range(3):  # x, y, z轴
            if abs(self.position[i]) + self.radius > box_size/2:
                # 如果球超出边界
                self.position[i] = np.sign(self.position[i]) * (box_size/2 - self.radius)
                self.velocity[i] *= -damping  # 反弹并损失能量

    def draw(self):
        glPushMatrix()
        glTranslatef(*self.position)
        
        # 设置材质属性
        glMaterialfv(GL_FRONT, GL_AMBIENT, [*self.color, 1.0])
        glMaterialfv(GL_FRONT, GL_DIFFUSE, [*self.color, 1.0])
        glMaterialfv(GL_FRONT, GL_SPECULAR, [1.0, 1.0, 1.0, 1.0])
        glMaterialf(GL_FRONT, GL_SHININESS, 60.0)
        
        gluSphere(self.quadric, self.radius, 32, 32)
        glPopMatrix()

class Spring:
    def __init__(self, config):
        self.width = config.SPRING_WIDTH
        self.height = config.SPRING_HEIGHT
        self.depth = config.SPRING_DEPTH
        self.spring_speed = config.SPRING_SPEED
        # 放置在底部中心
        self.position = np.array([0.0, 0.0, -config.BOX_SIZE/2 + self.height/2])
        
    def draw(self):
        glPushMatrix()
        glTranslatef(*self.position)
        
        # 设置银色材质
        glMaterialfv(GL_FRONT, GL_AMBIENT, [0.75, 0.75, 0.75, 1.0])
        glMaterialfv(GL_FRONT, GL_DIFFUSE, [0.75, 0.75, 0.75, 1.0])
        glMaterialfv(GL_FRONT, GL_SPECULAR, [1.0, 1.0, 1.0, 1.0])
        glMaterialf(GL_FRONT, GL_SHININESS, 100.0)
        
        # 绘制弹簧
        w, h, d = self.width/2, self.height/2, self.depth/2
        glBegin(GL_QUADS)
        # 顶面
        glNormal3f(0, 0, 1)
        glVertex3f(-w, -d, h)
        glVertex3f(w, -d, h)
        glVertex3f(w, d, h)
        glVertex3f(-w, d, h)
        
        # 底面
        glNormal3f(0, 0, -1)
        glVertex3f(-w, -d, -h)
        glVertex3f(-w, d, -h)
        glVertex3f(w, d, -h)
        glVertex3f(w, -d, -h)
        
        # 四个侧面
        glNormal3f(0, -1, 0)
        glVertex3f(-w, -d, -h)
        glVertex3f(w, -d, -h)
        glVertex3f(w, -d, h)
        glVertex3f(-w, -d, h)
        
        glNormal3f(0, 1, 0)
        glVertex3f(-w, d, -h)
        glVertex3f(-w, d, h)
        glVertex3f(w, d, h)
        glVertex3f(w, d, -h)
        
        glNormal3f(-1, 0, 0)
        glVertex3f(-w, -d, -h)
        glVertex3f(-w, -d, h)
        glVertex3f(-w, d, h)
        glVertex3f(-w, d, -h)
        
        glNormal3f(1, 0, 0)
        glVertex3f(w, -d, -h)
        glVertex3f(w, d, -h)
        glVertex3f(w, d, h)
        glVertex3f(w, -d, h)
        glEnd()
        glPopMatrix()

    def check_collision(self, ball):
        # 获取球相对于弹簧的位置
        rel_pos = ball.position - self.position
        
        # 检查是否在弹簧的范围内
        if (abs(rel_pos[0]) < self.width/2 and 
            abs(rel_pos[1]) < self.depth/2 and 
            abs(rel_pos[2]) < self.height/2 + ball.radius):
            
            # 检查是否从上方接触（与pingpang.py类似）
            if ball.velocity[2] < 0:
                return True
        return False

class Box:
    def __init__(self, size):
        self.size = size
        
    def draw(self):
        glLineWidth(2.0)
        glBegin(GL_LINES)
        
        # 定义立方体的12条边
        edges = (
            # 前面
            (-1, -1, -1), (-1,  1, -1),
            (-1,  1, -1), ( 1,  1, -1),
            ( 1,  1, -1), ( 1, -1, -1),
            ( 1, -1, -1), (-1, -1, -1),
            
            # 后面
            (-1, -1,  1), (-1,  1,  1),
            (-1,  1,  1), ( 1,  1,  1),
            ( 1,  1,  1), ( 1, -1,  1),
            ( 1, -1,  1), (-1, -1,  1),
            
            # 连接前后面
            (-1, -1, -1), (-1, -1,  1),
            (-1,  1, -1), (-1,  1,  1),
            ( 1,  1, -1), ( 1,  1,  1),
            ( 1, -1, -1), ( 1, -1,  1)
        )
        
        half_size = self.size / 2
        for edge in edges:
            glColor3f(0.5, 0.5, 0.5)  # 灰色边框
            glVertex3f(edge[0] * half_size, edge[1] * half_size, edge[2] * half_size)
            
        glEnd()

class Game:
    def __init__(self):
        pygame.init()
        self.config = GameConfig()
        self.setup_display()
        self.setup_game_objects()
        self.setup_camera()
        self.clock = pygame.time.Clock()
        
    def setup_display(self):
        pygame.display.set_mode(self.config.WINDOW_SIZE, DOUBLEBUF | OPENGL)
        pygame.display.set_caption("3D Bouncing Balls")
        
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glEnable(GL_COLOR_MATERIAL)
        glEnable(GL_NORMALIZE)
        
        # 设置光照
        glLightfv(GL_LIGHT0, GL_POSITION, [1.0, 1.0, 1.0, 0.0])
        glLightfv(GL_LIGHT0, GL_AMBIENT, [0.2, 0.2, 0.2, 1.0])
        glLightfv(GL_LIGHT0, GL_DIFFUSE, [0.8, 0.8, 0.8, 1.0])
        glLightfv(GL_LIGHT0, GL_SPECULAR, [1.0, 1.0, 1.0, 1.0])

    def setup_game_objects(self):
        self.box = Box(self.config.BOX_SIZE)
        self.spring = Spring(self.config)
        self.balls = [Ball(self.config.BALL_RADIUS) for _ in range(3)]
        
    def setup_camera(self):
        self.camera_distance = 200.0
        self.camera_x_rotation = 30.0
        self.camera_y_rotation = 45.0
        
    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if len(self.balls) < self.config.MAX_BALLS:
                        self.balls.append(Ball(self.config.BALL_RADIUS))
                elif event.key == pygame.K_BACKSPACE:
                    if len(self.balls) > 1:
                        self.balls.pop()
                        
        # 处理按住的键
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.camera_y_rotation -= 1.0
        if keys[pygame.K_RIGHT]:
            self.camera_y_rotation += 1.0
        if keys[pygame.K_UP]:
            self.camera_x_rotation = min(89.0, self.camera_x_rotation + 1.0)
        if keys[pygame.K_DOWN]:
            self.camera_x_rotation = max(-89.0, self.camera_x_rotation - 1.0)
        if keys[pygame.K_q]:
            self.camera_distance = max(150.0, self.camera_distance - 2.0)
        if keys[pygame.K_e]:
            self.camera_distance = min(300.0, self.camera_distance + 2.0)
            
        return True

    def update(self):
        for ball in self.balls:
            # 更新球的位置
            ball.update(self.config.BOX_SIZE, self.config.GRAVITY, self.config.DAMPING)
            
            # 检查弹簧碰撞
            if self.spring.check_collision(ball):
                # 模拟pingpang.py中的弹簧效果
                if ball.velocity[2] < 0:  # 只在球向下运动时触发
                    ball.velocity[2] = max(abs(ball.velocity[2]) * 1.2, self.spring.spring_speed)
            
            # 球之间的碰撞检测
            for i, ball1 in enumerate(self.balls):
                for ball2 in self.balls[i+1:]:
                    diff = ball1.position - ball2.position
                    distance = np.linalg.norm(diff)
                    if distance < (ball1.radius + ball2.radius):
                        normal = diff / distance
                        relative_velocity = ball1.velocity - ball2.velocity
                        impulse = -2.0 * np.dot(relative_velocity, normal) / 2.0
                        ball1.velocity += normal * impulse * self.config.DAMPING
                        ball2.velocity -= normal * impulse * self.config.DAMPING
                        
                        # 防止球体重叠
                        overlap = (ball1.radius + ball2.radius - distance) / 2.0
                        ball1.position += normal * overlap
                        ball2.position -= normal * overlap

    def draw(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        
        # 设置相机
        gluPerspective(45, (self.config.WINDOW_SIZE[0]/self.config.WINDOW_SIZE[1]), 0.1, 500.0)
        
        camera_x = self.camera_distance * math.cos(math.radians(self.camera_x_rotation)) * math.cos(math.radians(self.camera_y_rotation))
        camera_y = self.camera_distance * math.cos(math.radians(self.camera_x_rotation)) * math.sin(math.radians(self.camera_y_rotation))
        camera_z = self.camera_distance * math.sin(math.radians(self.camera_x_rotation))
        
        gluLookAt(camera_x, camera_y, camera_z, 0, 0, 0, 0, 0, 1)
        
        # 绘制场景
        self.box.draw()
        self.spring.draw()
        for ball in self.balls:
            ball.draw()
        
        pygame.display.flip()

    def run(self):
        running = True
        while running:
            running = self.handle_input()
            self.update()
            self.draw()
            self.clock.tick(self.config.FPS)

def main():
    game = Game()
    game.run()

if __name__ == "__main__":
    main()
