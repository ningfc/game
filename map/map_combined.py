import math
import json
import shapefile
# 分别导入pygame与pyglet/skia模块
import pygame
import pyglet
import skia
import io

# ...existing common code...

def geo_to_plane(lon, lat):
    # Mercator 投影，将经纬度转换为平面坐标
    R = 6378137  # 地球半径（米）
    x = math.radians(lon) * R
    y = math.log(math.tan(math.pi/4 + math.radians(lat)/2)) * R
    return x, y

# 抽象绘图接口
class MapRenderer:
    def run(self):
        raise NotImplementedError("Subclasses must implement run()")

# Pygame实现
class PygameRenderer(MapRenderer):
    def __init__(self, sf, min_x, max_x, min_y, max_y):
        self.sf = sf
        self.min_x = min_x
        self.max_x = max_x
        self.min_y = min_y
        self.max_y = max_y
        pygame.init()
        wm = pygame.display.get_wm_info()
        info = pygame.display.Info()
        self.screen = pygame.display.set_mode((info.current_w, info.current_h), pygame.RESIZABLE)
        pygame.display.set_caption("Pygame Map")
        self.clock = pygame.time.Clock()
        self.zoom = 1.0
        self.pan_x, self.pan_y = 0, 0
        self.dragging = False
        self.drag_start = (0, 0)
        self.drag_delta = (0, 0)
        self.cached_surface = None

    def draw_map(self, surface, w, h):
        base_scale = min(w / (self.max_x - self.min_x), h / (self.max_y - self.min_y))
        scale = base_scale * self.zoom
        offset_x = (w - (self.max_x - self.min_x) * scale) / 2 + self.pan_x
        offset_y = (h - (self.max_y - self.min_y) * scale) / 2 + self.pan_y
        def transform(coord):
            proj = geo_to_plane(coord[0], coord[1])
            x = (proj[0] - self.min_x) * scale + offset_x
            y = h - ((proj[1] - self.min_y) * scale + offset_y)
            return int(x), int(y)
        for shape in self.sf.shapes():
            parts = list(shape.parts) + [len(shape.points)]
            for i in range(len(shape.parts)):
                segment = shape.points[parts[i]:parts[i+1]]
                line = [transform(pt) for pt in segment]
                if len(line) > 1:
                    pygame.draw.lines(surface, (0, 255, 0), False, line, 2)

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.VIDEORESIZE:
                    self.screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
                elif event.type == pygame.MOUSEWHEEL:
                    self.zoom *= 1.1 ** event.y
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # 左键按下开始拖动
                        self.dragging = True
                        self.drag_start = event.pos
                        self.drag_delta = (0, 0)
                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1 and self.dragging:
                        self.dragging = False
                        self.pan_x += self.drag_delta[0]
                        self.pan_y += self.drag_delta[1]
                        self.drag_delta = (0, 0)
                elif event.type == pygame.MOUSEMOTION:
                    if self.dragging:
                        self.drag_delta = (event.pos[0] - self.drag_start[0],
                                           event.pos[1] - self.drag_start[1])
            w, h = self.screen.get_size()
            # 非拖动时更新缓存
            if not self.dragging:
                self.cached_surface = pygame.Surface((w, h))
                self.draw_map(self.cached_surface, w, h)
            self.screen.fill((0, 0, 0))
            if self.cached_surface:
                if self.dragging:
                    self.screen.blit(self.cached_surface, self.drag_delta)
                else:
                    self.screen.blit(self.cached_surface, (0, 0))
            pygame.display.flip()
            self.clock.tick(30)
        pygame.quit()

# Skia实现（基于 pyglet）
class SkiaRenderer(pyglet.window.Window, MapRenderer):
    def __init__(self, sf, min_x, max_x, min_y, max_y, width, height, caption):
        super().__init__(width, height, caption, resizable=True)
        self.sf = sf
        self.min_x = min_x
        self.max_x = max_x
        self.min_y = min_y
        self.max_y = max_y
        self.zoom = 1.0
        self.pan_x = 0
        self.pan_y = 0
        self.dragging = False
        self.drag_start = (0, 0)
        self.cached_surface = None  # 缓存 skia.Surface
        # 设置显式刷新，避免闪烁
        pyglet.clock.schedule_interval(lambda dt: self.dispatch_events() or self.on_draw(), 1/30.0)

    def draw_map_ski(self, canvas, w, h):
        base_scale = min(w / (self.max_x - self.min_x), h / (self.max_y - self.min_y))
        scale = base_scale * self.zoom
        offset_x = (w - (self.max_x - self.min_x) * scale) / 2 + self.pan_x
        offset_y = (h - (self.max_y - self.min_y) * scale) / 2 + self.pan_y
        paint = skia.Paint(
            AntiAlias=True,
            Color=skia.ColorGREEN,
            StrokeWidth=2,
            Style=skia.Paint.kStroke_Style
        )
        for shape in self.sf.shapes():
            parts = list(shape.parts) + [len(shape.points)]
            for i in range(len(shape.parts)):
                pts = []
                for pt in shape.points[parts[i]:parts[i+1]]:
                    proj = geo_to_plane(pt[0], pt[1])
                    x = (proj[0] - self.min_x) * scale + offset_x
                    y = h - ((proj[1] - self.min_y) * scale + offset_y)
                    pts.append(skia.Point(x, y))
                if len(pts) > 1:
                    path = skia.Path()
                    path.moveTo(pts[0])
                    for p in pts[1:]:
                        path.lineTo(p)
                    canvas.drawPath(path, paint)

    def on_draw(self):
        self.clear()
        w, h = self.get_size()
        if not self.dragging:
            # 更新缓存
            info = skia.ImageInfo.Make(w, h, skia.ColorType.kN32_ColorType, skia.AlphaType.kPremul_AlphaType)
            self.cached_surface = skia.Surface.MakeRaster(info)
            canvas = self.cached_surface.getCanvas()
            canvas.clear(skia.ColorWHITE)
            self.draw_map_ski(canvas, w, h)
        # 将缓存渲染到窗口（拖动时直接blit缓存）
        if self.cached_surface:
            img = self.cached_surface.makeImageSnapshot()
            png_data = img.encodeToData()
            bio = io.BytesIO(png_data)
            pyg_img = pyglet.image.load('cached.png', file=bio)
            pyg_img.blit(0, 0)

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        self.zoom *= 1.1 ** scroll_y

    def on_mouse_press(self, x, y, button, modifiers):
        if button == pyglet.window.mouse.LEFT:
            self.dragging = True
            self.drag_start = (x, y)

    def on_mouse_release(self, x, y, button, modifiers):
        if button == pyglet.window.mouse.LEFT:
            self.dragging = False

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        if buttons & pyglet.window.mouse.LEFT:
            self.pan_x += dx
            self.pan_y += dy

# 主程序入口
if __name__ == "__main__":
    # 加载SHP数据及计算投影坐标边界（公共部分）
    filename = '/Users/fangchaoning/Code/GISData/taiwan-latest-free.shp/gis_osm_waterways_free_1.shp'
    sf = shapefile.Reader(filename)
    all_points = []
    for shape in sf.shapes():
        for pt in shape.points:
            all_points.append(geo_to_plane(pt[0], pt[1]))
    min_x = min(x for x, y in all_points)
    max_x = max(x for x, y in all_points)
    min_y = min(y for x, y in all_points)
    max_y = max(y for x, y in all_points)
    
    # 选择渲染实现："pygame" 或 "skia"
    RENDERER = "skia"  # 修改为 "skia" 使用SkiaRenderer
    
    if RENDERER == "pygame":
        renderer = PygameRenderer(sf, min_x, max_x, min_y, max_y)
        renderer.run()
    elif RENDERER == "skia":
        # 修改：使用 pyglet.window.get_platform() 获取默认显示器
        display = pyglet.display.get_display()
        screen = display.get_default_screen()
        width, height = screen.width, screen.height
        window = SkiaRenderer(sf, min_x, max_x, min_y, max_y, width, height, "Skia Map")
        pyglet.app.run()
