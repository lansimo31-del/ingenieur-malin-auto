# Dessin de la miniature de l'épisode 5 : le bec du pistolet et son petit trou, en vert.
def rrect(cx, cy, w, h, r, n=14):
    pts = []
    for (ox, oy, a0) in ((w/2 - r, -h/2 + r, -90), (w/2 - r, h/2 - r, 0), (-w/2 + r, h/2 - r, 90), (-w/2 + r, -h/2 + r, 180)):
        for i in range(n + 1):
            a = math.radians(a0 + 90 * i / n); pts.append((cx + ox + r * math.cos(a), cy + oy + r * math.sin(a)))
    return pts

def dessin(c):
    cx, cy = 540, 1232
    c.poly(rrect(cx + 8, cy + 10, 760, 190, 80), fill=(214, 214, 210))
    c.poly(rrect(cx, cy, 760, 190, 80), fill=(205, 205, 200), outline=INK, w=11)
    c.poly(rrect(cx - 10, cy + 20, 640, 70, 30), fill=(226, 234, 232), outline=INK, w=4)
    c.circle((cx + 270, cy - 95), 26, fill=RED, outline=INK, w=5)
    c.line([(cx + 270, cy - 190), (cx + 270, cy - 140)], 8, RED)
    c.line([(cx + 245, cy - 160), (cx + 270, cy - 138), (cx + 295, cy - 160)], 8, RED)
