import math
import io
import pyglet
import skia
import shapefile  # 使用与原文件相同的 shapefile 数据加载

# 使用的SHP数据文件路径，与原文件一致
filename = '/Users/fangchaoning/Code/GISData/taiwan-latest-free.shp/gis_osm_waterways_free_1.shp'

def geo_to_plane(lon, lat):
    # Mercator 投影
    R = 6378137  # 地球半径（米）
    x = math.radians(lon) * R
    y = math.log(math.tan(math.pi/4 + math.radians(lat)/2)) * R
    return x, y

def draw_map_ski(canvas, sf, min_x, max_x, min_y, max_y, window_width, window_height, zoom, pan_x, pan_y):
    base_scale = min(window_width / (max_x - min_x), window_height / (max_y - min_y))
    scale = base_scale * zoom
    offset_x = (window_width - (max_x - min_x) * scale) / 2 + pan_x
    offset_y = (window_height - (max_y - min_y) * scale) / 2 + pan_y
    paint = skia.Paint(
        AntiAlias=True,
        Color=skia.ColorGREEN,
        StrokeWidth=2,
        Style=skia.Paint.kStroke_Style
    )
    for shape in sf.shapes():
        parts = list(shape.parts) + [len(shape.points)]
        for i in range(len(shape.parts)):
            pts = []
            for pt in shape.points[parts[i]:parts[i+1]]:
                proj_x, proj_y = geo_to_plane(pt[0], pt[1])
                x = (proj_x - min_x) * scale + offset_x
                y = window_height - ((proj_y - min_y) * scale + offset_y)
                pts.append(skia.Point(x, y))
            if len(pts) > 1:
                path = skia.Path()
                path.moveTo(pts[0])
                for p in pts[1:]:
                    path.lineTo(p)
                canvas.drawPath(path, paint)

class SkiaMapWindow(pyglet.window.Window):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 加载SHP数据
        self.sf = shapefile.Reader(filename)
        # 预计算所有点的投影坐标
        all_points = []
        for shape in self.sf.shapes():
            for pt in shape.points:
                all_points.append(geo_to_plane(pt[0], pt[1]))
        self.min_x = min(x for x, y in all_points)
        self.max_x = max(x for x, y in all_points)
        self.min_y = min(y for x, y in all_points)
        self.max_y = max(y for x, y in all_points)
        self.zoom = 1.0
        self.pan_x = 0
        self.pan_y = 0
        self.dragging = False
        self.drag_start = (0, 0)
    
    def on_draw(self):
        self.clear()
        # 创建 Skia Surface 与 Canvas（使用当前窗口尺寸）
        info = skia.ImageInfo.Make(self.width, self.height, 
                                   skia.ColorType.kN32_ColorType, 
                                   skia.AlphaType.kPremul_AlphaType)
        surface = skia.Surface.MakeRaster(info)
        canvas = surface.getCanvas()
        canvas.clear(skia.ColorWHITE)
        draw_map_ski(canvas, self.sf, self.min_x, self.max_x, self.min_y, self.max_y,
                     self.width, self.height, self.zoom, self.pan_x, self.pan_y)
        # 获取 PNG 数据并通过 pyglet 加载
        img = surface.makeImageSnapshot()
        png_data = img.encodeToData()
        bio = io.BytesIO(png_data)
        pyg_img = pyglet.image.load('map.png', file=bio)
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

if __name__ == "__main__":
    display = pyglet.canvas.Display()
    screen = display.get_default_screen()
    width, height = screen.width, screen.height
    window = SkiaMapWindow(width, height, "Skia Map", resizable=True)
    pyglet.app.run()
