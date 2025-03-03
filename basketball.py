import pybullet as p
import time
import pygame


pygame.display.set_caption("PyBullet with PyGame")

# 初始化PyBullet
p.connect(p.GUI)
p.setGravity(0, 0, -9.8)

# 创建地板
planeId = p.createCollisionShape(p.GEOM_PLANE)
floorId = p.createMultiBody(0, planeId)

# 创建篮球
ball_radius = 0.2
ballId = p.createCollisionShape(p.GEOM_SPHERE, radius=ball_radius)
ball_start_pos = [0, 0, 3]
ball_start_orientation = p.getQuaternionFromEuler([0, 0, 0])
ball_mass = 1
ball_visualId = -1
ballId = p.createMultiBody(ball_mass, ballId, ball_visualId, ball_start_pos, ball_start_orientation)

# 设置篮球初始速度
initial_velocity = [0, 0, -5]
p.resetBaseVelocity(ballId, linearVelocity=initial_velocity)

# 添加空气阻力和地面摩擦力
p.changeDynamics(ballId, -1, linearDamping=0.01, angularDamping=0.2, restitution=0.8)  # 设置反弹系数
p.changeDynamics(ballId, -1, mass=0.01)
p.changeDynamics(floorId, -1, lateralFriction=0.5)

# 初始化PyGame
pygame.init()
width, height = 800, 600
screen = pygame.display.set_mode((width, height))

# 主循环
clock = pygame.time.Clock()
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # 更新物理仿真
    p.stepSimulation()

    # 获取篮球的位置和速度
    pos, _ = p.getBasePositionAndOrientation(ballId)
    vel, _ = p.getBaseVelocity(ballId)
    print(vel)
    # 清空屏幕
    screen.fill((255, 255, 255))

    # 绘制篮球
    ball_screen_pos = (int(pos[0] * 100 + width / 2), int(-pos[1] * 100 + height / 2))
    pygame.draw.circle(screen, (0, 0, 255), ball_screen_pos, int(ball_radius * 100))

    # 更新屏幕
    pygame.display.flip()

    # 控制帧率
    clock.tick(60)

# 清理
pygame.quit()
p.disconnect()
