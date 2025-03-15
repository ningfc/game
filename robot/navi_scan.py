import pygame
import math
import random

import pygame.display

# 初始化 Pygame
pygame.init()

# 设置窗口
WIDTH = 800
HEIGHT = 800
SCAN_SIZE = 400  # 扫描区域大小
GRID_SIZE = 50   # 每个方格的大小
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Drone Forest Scanner")

# 颜色定义
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
BLUE = (0, 0, 255)
RED = (255, 100, 100)  # 浅红色作为扫描区域底色
GREEN = (0, 255, 0)
DRONE_COLOR = (0, 150, 255)
YELLOW = (255, 255, 0)  # 新增颜色，用于预先绘制规划路径

# 无人机设置
DRONE_RADIUS = 8
SCAN_WIDTH = 60  # 增加扫描宽度，从20增加到60

# 计算起始半径，确保从区域边界开始
EXTEND_PERCENT = 10
START_RADIUS = math.sqrt(2) * SCAN_SIZE * (0.5 * (1 + (EXTEND_PERCENT / 100)))  # 从对角线长度的一半开始，确保覆盖角落

drone_pos = {
    'x': WIDTH // 2,
    'y': HEIGHT // 2
}

# 螺旋路径参数
spiral = {
    'angle': 0,
    'radius': START_RADIUS,
    'center_x': WIDTH // 2,
    'center_y': HEIGHT // 2,
    'speed': -1,        # 负值使其顺时针旋转
    'shrink_rate': (SCAN_WIDTH * 0.6) / 360,  # 根据扫描宽度计算收缩率
    'min_radius': 0    # 扫描到中心
}

path = []  # 存储无人机的运动轨迹
avoid_tree_path = []  # 新增：存储最近遇到树木的位置

scan_coverage = None
planner = None
trees = []
nearest_tree = []

class ForestConfig:
    WIDTH = 800
    HEIGHT = 800
    SCAN_SIZE = 400  # 样地大小
    GRID_SIZE = 50   # 网格大小
    MIN_TREE_SPACING = 20  # 树木最小间距
    TREE_SIZE_RANGE = (3, 6)  # 树木大小范围
    TREE_DENSITY = 0.7  # 树木密度系数 (0-1)

def generate_forest():
    """使用泊松分布生成更真实的森林分布"""
    trees = []
    attempts = 1000  # 最大尝试次数
    
    def is_valid_position(x, y, radius, existing_trees):
        # 检查与现有树木的距离
        for tx, ty, tr in existing_trees:
            dist = math.sqrt((x - tx)**2 + (y - ty)**2)
            if dist < (radius + tr + ForestConfig.MIN_TREE_SPACING):
                return False
        return True
    
    while len(trees) < (WIDTH * HEIGHT * ForestConfig.TREE_DENSITY) / (GRID_SIZE * GRID_SIZE):
        if attempts <= 0:
            break
            
        x = random.uniform(0, WIDTH)
        y = random.uniform(0, HEIGHT)
        radius = random.uniform(*ForestConfig.TREE_SIZE_RANGE)
        
        if is_valid_position(x, y, radius, trees):
            trees.append((x, y, radius))
        
        attempts -= 1
    
    return trees

class DronePathPlanner:
    def __init__(self, start_radius, center_x, center_y, speed, shrink_rate):
        self.start_radius = start_radius
        self.center_x = center_x
        self.center_y = center_y
        self.speed = speed
        self.shrink_rate = shrink_rate
        self.planned_path = []
        self.generate_spiral_path()
    
    def generate_spiral_path(self):
        """生成理想的螺旋路径"""
        angle = 0
        radius = self.start_radius
        while radius > DRONE_RADIUS * 3:
            x = self.center_x + math.cos(math.radians(angle)) * radius
            y = self.center_y + math.sin(math.radians(angle)) * radius
            self.planned_path.append((x, y))
            angle += self.speed
            radius -= self.shrink_rate * abs(self.speed)

    def find_avoidance_path(self, current_pos, target_pos, trees, avoid_radius=30):
        global nearest_tree
        """计算避障路径点"""
        # 检查是否需要避障
        if not self.check_collision_line(current_pos, target_pos, trees):
            return [target_pos]
            
        # 需要避障时,生成弧形避障路径
        # dx = target_pos[0] - current_pos[0]
        # dy = target_pos[1] - current_pos[1]
        # distance = math.sqrt(dx*dx + dy*dy)
        
        # 找到最近的障碍物
        nearest_tree = None
        min_dist = float('inf')
        forward_dx = target_pos[0] - current_pos[0]
        forward_dy = target_pos[1] - current_pos[1]
        mag = math.sqrt(forward_dx**2 + forward_dy**2)
        if mag != 0:
            forward = (forward_dx / mag, forward_dy / mag)
        else:
            forward = (0, 0)
        for tree in trees:
            diff_x = tree[0] - current_pos[0]
            diff_y = tree[1] - current_pos[1]
            projection = diff_x * forward[0] + diff_y * forward[1]
            if projection > 0:
                dist = self.point_to_point_distance(tree, current_pos)
                if dist < min_dist:
                    min_dist = dist
                    nearest_tree = tree
        
        if nearest_tree != None and min_dist < DRONE_RADIUS * 3:
            # 生成弧形避障路径点
            num_points = 9  # 弧形路径的点数
            avoid_points = []
            # 计算无人机当前位置和目标位置分别与障碍物的连线角度
            dx1 = current_pos[0] - nearest_tree[0]
            dy1 = current_pos[1] - nearest_tree[1]
            start_angle = math.atan2(dy1, dx1)

            dx2 = target_pos[0] - nearest_tree[0]
            dy2 = target_pos[1] - nearest_tree[1]
            end_angle = math.atan2(dy2, dx2)

            # 规范化角度差至 [-π, π]
            delta_angle = end_angle - start_angle
            while delta_angle > math.pi:
                delta_angle -= 2 * math.pi
            while delta_angle < -math.pi:
                delta_angle += 2 * math.pi

            # 使用障碍物到当前位置的距离作为圆弧半径
            arc_radius = math.sqrt(dx1 * dx1 + dy1 * dy1)

            # 生成弧形路径上的中间点
            step = delta_angle / (num_points + 1)
            for i in range(1, num_points + 1):
                theta = start_angle + step * i
                x = nearest_tree[0] + arc_radius * math.cos(theta)
                y = nearest_tree[1] + arc_radius * math.sin(theta)
                avoid_points.append((x, y))
                
            return avoid_points
        else:
            return [target_pos]

    def check_collision_line(self, start, end, trees):
        """检查路径是否与树木碰撞"""
        for tree in trees:
            if self.point_to_line_distance(tree, start, end) < tree[2] + DRONE_RADIUS + 10:
                return True
        return False
    
    def point_to_point_distance(self, point1, point2):
        return math.sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)

    def point_to_line_distance(self, point, line_start, line_end):
        """计算点到线段的距离"""
        x0, y0 = point[0], point[1]
        x1, y1 = line_start[0], line_start[1]
        x2, y2 = line_end[0], line_end[1]
        
        numerator = abs((x2-x1)*(y1-y0) - (x1-x0)*(y2-y1))
        denominator = math.sqrt((x2-x1)**2 + (y2-y1)**2)
        return numerator/denominator if denominator != 0 else 0
    
    def get_perpendicular_point(self, start, end, tree, avoid_radius):
        """获取垂直于路径方向的避障控制点"""
        dx = end[0] - start[0]
        dy = end[1] - start[1]
        dist = math.sqrt(dx*dx + dy*dy)
        if dist == 0:
            return start
            
        # 单位向量的垂直向量
        perpendicular_x = -dy/dist
        perpendicular_y = dx/dist
        
        # 根据树木在路径的哪一侧选择避障方向
        side = math.copysign(1, (tree[0]-start[0])*perpendicular_x + (tree[1]-start[1])*perpendicular_y)
        
        # 控制点位置
        mid_x = (start[0] + end[0])/2
        mid_y = (start[1] + end[1])/2
        control_x = mid_x + side * perpendicular_x * avoid_radius
        control_y = mid_y + side * perpendicular_y * avoid_radius
        
        return (control_x, control_y)

def update_drone_position():
    global drone_pos, spiral, path, avoid_tree_path, trees, planner
    prev_pos = (drone_pos['x'], drone_pos['y'])
    
    # 更新螺旋参数
    spiral['angle'] += spiral['speed']
    spiral['radius'] -= spiral['shrink_rate']
    
    # 计算候选新位置
    candidate = (
        spiral['center_x'] + math.cos(math.radians(spiral['angle'])) * spiral['radius'],
        spiral['center_y'] + math.sin(math.radians(spiral['angle'])) * spiral['radius']
    )
    
    # 检查路径是否与树木碰撞
    if planner.check_collision_line(prev_pos, candidate, trees):
        # 计算避障路径
        avoidance_path = planner.find_avoidance_path(prev_pos, candidate, trees)
        if avoidance_path:
            candidate = avoidance_path[-1]
            avoid_tree_path.extend(avoidance_path)
    
    # 更新无人机位置
    drone_pos['x'], drone_pos['y'] = candidate
    path.append(candidate)
    if len(path) > 2000:
        path.pop(0)
    
    # 检查是否完成一次扫描（到达中心）
    if spiral['radius'] <= spiral['min_radius']:
        reset_scan()

def reset_scan():
    global path, avoid_tree_path, scan_coverage
    spiral['radius'] = START_RADIUS
    spiral['angle'] = 0
    path.clear()
    if scan_coverage != None:
        scan_coverage.reset() 
    
    # 重置最近树木折线路径
    avoid_tree_path.clear()
    drone_pos['x'] = spiral['center_x'] + spiral['radius']
    drone_pos['y'] = spiral['center_y']

class ScanCoverage:
    def __init__(self, width, height, scan_size, cell_size=10):
        self.width = width
        self.height = height
        self.scan_size = scan_size
        self.cell_size = cell_size
        
        # 计算样地区域的网格大小
        self.grid_size = scan_size // cell_size
        self.total_cells = self.grid_size * self.grid_size
        # 初始化网格，False 表示未扫描，True 表示已扫描
        self.grid = [[False] * self.grid_size for _ in range(self.grid_size)]
        self.scanned_cells = 0
        
        # 计算样地区域的边界
        self.scan_start_x = (width - scan_size) // 2
        self.scan_start_y = (height - scan_size) // 2
        self.scan_end_x = self.scan_start_x + scan_size
        self.scan_end_y = self.scan_start_y + scan_size

    def update(self, x, y, scan_width):
        """更新扫描覆盖区域"""
        # 只有在样地区域内的点才计算
        if (x < self.scan_start_x or x > self.scan_end_x or 
            y < self.scan_start_y or y > self.scan_end_y):
            return

        # 转换为样地区域内的相对坐标
        relative_x = x - self.scan_start_x
        relative_y = y - self.scan_start_y
        
        # 转换为网格坐标
        cell_x = int(relative_x // self.cell_size)
        cell_y = int(relative_y // self.cell_size)
        radius = int(scan_width // (2 * self.cell_size))
        
        for dx in range(-radius, radius + 1):
            for dy in range(-radius, radius + 1):
                nx, ny = cell_x + dx, cell_y + dy
                if (0 <= nx < self.grid_size and 
                    0 <= ny < self.grid_size and 
                    not self.grid[nx][ny]):
                    # 计算实际距离，确保是圆形扫描区域
                    dist = math.sqrt(dx**2 + dy**2)
                    if dist <= radius:
                        self.grid[nx][ny] = True
                        self.scanned_cells += 1
    
    def get_coverage_percentage(self):
        """获取扫描覆盖率"""
        return (self.scanned_cells / self.total_cells) * 100

    def draw_coverage(self, screen):
        """绘制覆盖区域（用于调试）"""
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                if self.grid[i][j]:
                    rect = pygame.Rect(
                        self.scan_start_x + i * self.cell_size,
                        self.scan_start_y + j * self.cell_size,
                        self.cell_size,
                        self.cell_size
                    )
                    pygame.draw.rect(screen, (0, 200, 0), rect)
    def reset(self):
        self.grid = [[False] * self.grid_size for _ in range(self.grid_size)]
        self.scanned_cells = 0

def main():
    global planner, trees, scan_coverage

    trees = generate_forest()
    clock = pygame.time.Clock()
    running = True
    
    reset_scan()
    
    scan_coverage = ScanCoverage(WIDTH, HEIGHT, SCAN_SIZE, cell_size=10)
    planner = DronePathPlanner(START_RADIUS, WIDTH // 2, HEIGHT // 2, spiral['speed'], spiral['shrink_rate'])
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    trees = generate_forest()
                    reset_scan()
                    scan_coverage = ScanCoverage(WIDTH, HEIGHT, SCAN_SIZE, cell_size=10)
        
        update_drone_position()
        scan_coverage.update(drone_pos['x'], drone_pos['y'], SCAN_WIDTH)
        
        screen.fill(WHITE)
        
        # 绘制扫描区域底色
        scan_rect = pygame.Rect(
            (WIDTH - SCAN_SIZE) // 2,
            (HEIGHT - SCAN_SIZE) // 2,
            SCAN_SIZE,
            SCAN_SIZE
        )
        pygame.draw.rect(screen, RED, scan_rect)
        
        # 绘制预先规划的路径
        if len(planner.planned_path) > 1:
            pygame.draw.lines(screen, GRAY, False, planner.planned_path, 5)
        
        # 可选：绘制覆盖网格（调试用）
        scan_coverage.draw_coverage(screen)
        
        # 绘制网格
        for i in range(WIDTH // GRID_SIZE + 1):
            pygame.draw.line(screen, GRAY, (i * GRID_SIZE, 0), (i * GRID_SIZE, HEIGHT))
        for i in range(HEIGHT // GRID_SIZE + 1):
            pygame.draw.line(screen, GRAY, (0, i * GRID_SIZE), (WIDTH, i * GRID_SIZE))
        
        # 绘制轨迹
        if len(path) > 1:
            pygame.draw.lines(screen, GREEN, False, path, 2)
        
        # 绘制树木
        for x, y, radius in trees:
            pygame.draw.circle(screen, GREEN, (int(x), int(y)), int(radius))
        pygame.draw.circle(screen, RED, (nearest_tree[:2]), int(radius))
        
        # 绘制无人机
        pygame.draw.circle(screen, DRONE_COLOR, 
                         (int(drone_pos['x']), int(drone_pos['y'])), 
                         DRONE_RADIUS)
        
        # 新增：绘制连接最近遇到树木的折线
        if len(avoid_tree_path) > 1:
            pygame.draw.lines(screen, BLUE, False, avoid_tree_path, 2)
        
        font = pygame.font.Font(None, 36)

        fps_text = font.render(f"FPS: {int(clock.get_fps())}", True, BLACK)
        screen.blit(fps_text, (10, 10))

        # 显示扫描覆盖率
        coverage_text = font.render(f"Coverage: {scan_coverage.get_coverage_percentage():.1f}%", True, BLACK)
        screen.blit(coverage_text, (100, 10))
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()

if __name__ == '__main__':
    main()
