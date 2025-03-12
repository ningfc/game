import json
import math
import pygame
import shapefile  # added import
import threading  # added import

filename = "/Users/fangchaoning/Code/GISData/shaanxi.geojson"
filename = '/Users/fangchaoning/Code/GISData/taiwan-latest-free.shp/gis_osm_waterways_free_1.shp'

def load_geojson(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

# 新增：将地理坐标（经纬度）转换为平面坐标（Mercator 投影）
def geo_to_plane(lon, lat):
    R = 6378137  # 地球半径（单位：米）
    x = math.radians(lon) * R
    y = math.log(math.tan(math.pi/4 + math.radians(lat)/2)) * R
    return x, y

# 修改绘图函数，先将地理坐标转换为平面坐标，再映射到屏幕
def draw_map(screen, sf, min_x, max_x, min_y, max_y, window_width, window_height, zoom, pan_x, pan_y):
    base_scale = min(window_width / (max_x - min_x), window_height / (max_y - min_y))
    scale = base_scale * zoom
    offset_x = (window_width - (max_x - min_x) * scale) / 2 + pan_x
    offset_y = (window_height - (max_y - min_y) * scale) / 2 + pan_y
    def transform(coord):
        # coord: (lon, lat)，先投影到平面坐标
        proj_x, proj_y = geo_to_plane(coord[0], coord[1])
        x = (proj_x - min_x) * scale + offset_x
        y = window_height - ((proj_y - min_y) * scale + offset_y)
        return int(x), int(y)
    
    for shape in sf.shapes():
        if pygame.mouse.get_pressed()[0]:  # Abort drawing if left mouse button is pressed
            return
        parts = list(shape.parts) + [len(shape.points)]
        for i in range(len(shape.parts)):
            segment = shape.points[parts[i]:parts[i+1]]
            line = [transform(pt) for pt in segment]
            if len(line) > 1:
                pygame.draw.lines(screen, (0, 255, 0), False, line, 2)

def main():
    # 加载SHP数据
    sf = shapefile.Reader(filename)
    
    pygame.init()
    info = pygame.display.Info()  # 获取当前屏幕信息
    screen = pygame.display.set_mode((info.current_w, info.current_h), pygame.RESIZABLE)
    pygame.display.set_caption("SHP Map")
    clock = pygame.time.Clock()
    # 将所有点从地理坐标转换到平面坐标
    all_points = []
    for shape in sf.shapes():
        for pt in shape.points:
            all_points.append(geo_to_plane(pt[0], pt[1]))
    min_x = min(pt[0] for pt in all_points)
    max_x = max(pt[0] for pt in all_points)
    min_y = min(pt[1] for pt in all_points)
    max_y = max(pt[1] for pt in all_points)
    
    zoom_factor = 1.0  # 控制缩放
    pan_x, pan_y = 0, 0  # 用于拖动平移的偏移
    dragging = False
    drag_start = (0, 0)
    drag_delta = (0, 0)
    cached_surface = None  # 用于缓存重绘效果
    draw_thread = None  # track asynchronous drawing thread
    last_draw_params = None  # 记录上次绘制参数
    
    pygame.font.init()
    font = pygame.font.Font(None, 24)
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.VIDEORESIZE:
                screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
            elif event.type == pygame.MOUSEWHEEL:
                zoom_factor *= 1.1 ** event.y
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # 左键按下开始拖动
                    dragging = True
                    drag_start = event.pos
                    drag_delta = (0, 0)
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1 and dragging:  # 左键释放停止拖动
                    dragging = False
                    pan_x += drag_delta[0]
                    pan_y += drag_delta[1]
                    drag_delta = (0, 0)
            elif event.type == pygame.MOUSEMOTION:
                if dragging:
                    drag_delta = (event.pos[0] - drag_start[0], event.pos[1] - drag_start[1])
        
        window_width, window_height = screen.get_size()
        if not dragging:
            current_params = (zoom_factor, pan_x, pan_y, window_width, window_height)
            if current_params != last_draw_params:
                if draw_thread is None or not draw_thread.is_alive():
                    new_surface = pygame.Surface((window_width, window_height))
                    draw_thread = threading.Thread(target=draw_map, args=(
                        new_surface, sf, min_x, max_x, min_y, max_y,
                        window_width, window_height, zoom_factor, pan_x, pan_y))
                    draw_thread.start()
                    cached_surface = new_surface
                    last_draw_params = current_params
        
        screen.fill((0,0,0))
        if cached_surface:
            if dragging:
                # 拖动时只移动缓存图像
                screen.blit(cached_surface, drag_delta)
            else:
                screen.blit(cached_surface, (0, 0))
        
        surface = font.render(f'FPS:{int(clock.get_fps())}', True, (255, 255, 255))
        screen.blit(surface, (50, 50))

        pygame.display.flip()
        clock.tick(30)
    
    pygame.quit()

if __name__ == "__main__":
    main()

