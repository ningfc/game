import skia

surface = skia.Surface(256, 256)
with surface as canvas:
    paint = skia.Paint(Color=skia.ColorRED)
    canvas.drawRect(skia.Rect(50, 50, 200, 200), paint)
surface.toarray().save("output.png")