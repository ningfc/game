import pygame
import math
import random
import imageio

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

FPS = 60
drone_pos = {
    'x': 0, #WIDTH // 2,
    'y': 0, #HEIGHT // 2
}

DRONE_SPEED = 5  # 新增：无人机移动步长

path = []  # 存储无人机的运动轨迹

scan_coverage = None
planner = None
trees = []

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

# 修改后的 DronePathPlanner 类：使用贪心算法生成连接扫描区域内所有树木的最短路径
class DronePathPlanner:
    def __init__(self, center_x, center_y, trees):
        self.center_x = center_x
        self.center_y = center_y
        self.planned_path = []
        self.generate_path(trees)
    
    def generate_path(self, trees):
        # 计算扫描区域边界
        scan_start_x = (WIDTH - SCAN_SIZE) // 2
        scan_start_y = (HEIGHT - SCAN_SIZE) // 2
        scan_end_x = scan_start_x + SCAN_SIZE
        scan_end_y = scan_start_y + SCAN_SIZE
        # 筛选扫描区域内的树木（取树的坐标）
        candidate_trees = [(x, y) for (x, y, r) in trees if scan_start_x <= x <= scan_end_x and scan_start_y <= y <= scan_end_y]
        # 生成初始贪心路径
        current = (self.center_x, self.center_y)
        path = []
        while candidate_trees:
            next_tree = min(candidate_trees, key=lambda point: math.hypot(point[0]-current[0], point[1]-current[1]))
            path.append(next_tree)
            candidate_trees.remove(next_tree)
            current = next_tree
        # 应用2-opt算法对路径进行优化
        self.planned_path = self.two_opt(path)
    
    def two_opt(self, path):
        improved = True
        best = path[:]
        while improved:
            improved = False
            for i in range(1, len(best) - 1):
                for j in range(i + 1, len(best)):
                    if j - i == 1:
                        continue
                    new_path = best[:]
                    new_path[i:j] = best[i:j][::-1]
                    if self.path_distance(new_path) < self.path_distance(best):
                        best = new_path
                        improved = True
            # 若无改善，则退出
        return best

    def path_distance(self, path):
        total = 0.0
        current = (self.center_x, self.center_y)
        for point in path:
            total += math.hypot(point[0]-current[0], point[1]-current[1])
            current = point
        return total

def update_drone_position():
    global drone_pos, path, planner
    current = (drone_pos['x'], drone_pos['y'])
    if planner.planned_path:
        next_point = planner.planned_path[0]
        dx = next_point[0] - current[0]
        dy = next_point[1] - current[1]
        distance = math.hypot(dx, dy)
        if distance > DRONE_SPEED:
            candidate = (current[0] + dx/distance * DRONE_SPEED, current[1] + dy/distance * DRONE_SPEED)
        else:
            candidate = next_point
            planner.planned_path.pop(0)
    else:
        candidate = current
    drone_pos['x'], drone_pos['y'] = candidate
    path.append(candidate)
    if len(path) > 2000:
        path.pop(0)

def reset_scan():
    global path, drone_pos
    path.clear()
    drone_pos['x'] = WIDTH // 2
    drone_pos['y'] = HEIGHT // 2

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
                if (self.grid[i][j]):
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
    
    scan_coverage = ScanCoverage(WIDTH, HEIGHT, SCAN_SIZE, cell_size=10)
    planner = DronePathPlanner(WIDTH // 2, HEIGHT // 2, trees)
    
    reset_scan()
    
    writer = imageio.get_writer('drone_forest_scanner.mp4', fps=30)

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    trees = generate_forest()
                    scan_coverage = ScanCoverage(WIDTH, HEIGHT, SCAN_SIZE, cell_size=10)
                    planner = DronePathPlanner(WIDTH // 2, HEIGHT // 2, trees)
                    reset_scan()
        
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
        
        # 绘制规划路径
        if len(planner.planned_path) > 1:
            pygame.draw.lines(screen, GRAY, False, planner.planned_path, 5)
            for point in planner.planned_path:
                pygame.draw.circle(screen, BLUE, (int(point[0]), int(point[1])), 3)
        
        # 绘制覆盖网格及网格线
        scan_coverage.draw_coverage(screen)
        for i in range(WIDTH // GRID_SIZE + 1):
            pygame.draw.line(screen, GRAY, (i * GRID_SIZE, 0), (i * GRID_SIZE, HEIGHT))
        for i in range(HEIGHT // GRID_SIZE + 1):
            pygame.draw.line(screen, GRAY, (0, i * GRID_SIZE), (WIDTH, i * GRID_SIZE))
        
        # 绘制轨迹
        if len(path) > 1:
            pygame.draw.lines(screen, GREEN, False, path, 2)
        
        # 绘制所有树木
        for x, y, radius in trees:
            pygame.draw.circle(screen, GREEN, (int(x), int(y)), int(radius))
        
        # 绘制无人机
        pygame.draw.circle(screen, DRONE_COLOR, (int(drone_pos['x']), int(drone_pos['y'])), DRONE_RADIUS)
        
        font = pygame.font.Font(None, 36)
        fps_text = font.render(f"FPS: {int(clock.get_fps())}", True, BLACK)
        screen.blit(fps_text, (10, 10))
        coverage_text = font.render(f"Coverage: {scan_coverage.get_coverage_percentage():.1f}%", True, BLACK)
        screen.blit(coverage_text, (100, 10))
        
        pygame.display.flip()
        clock.tick(FPS)
    
    pygame.quit()

if __name__ == '__main__':
    main()
