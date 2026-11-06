# Dessin de la miniature de l'épisode 11 : le dessous d'un cadenas et son petit trou, en vert.
def rrect(cx, cy, w, h, r, n=14):
    pts = []
    for (ox, oy, a0) in ((w/2 - r, -h/2 + r, -90), (w/2 - r, h/2 - r, 0), (-w/2 + r, h/2 - r, 90), (-w/2 + r, -h/2 + r, 180)):
        for i in range(n + 1):
            a = math.radians(a0 + 90 * i / n); pts.append((cx + ox + r * math.cos(a), cy + oy + r * math.sin(a)))
    return pts

def dessin(c):
    cx, cy = 540, 1232
    c.poly(rrect(cx + 8, cy + 10, 560, 300, 60), fill=(214, 214, 210))
    c.poly(rrect(cx, cy, 560, 300, 60), fill=(205, 205, 200), outline=INK, w=11)
    c.poly(rrect(cx, cy - 20, 460, 190, 40), fill=(226, 226, 222), outline=INK, w=4)
    c.circle((cx, cy + 118), 22, fill=RED, outline=INK, w=5)
    c.line([(cx, cy + 215), (cx, cy + 170)], 8, RED)
    c.line([(cx - 25, cy + 190), (cx, cy + 168), (cx + 25, cy + 190)], 8, RED)
