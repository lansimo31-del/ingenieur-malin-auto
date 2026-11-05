# Dessin de la miniature de l'épisode 8 : un pare-brise vu de face, bande noire et points qui s'espacent, un point en vert.
def rrect(cx, cy, w, h, r, n=14):
    pts = []
    for (ox, oy, a0) in ((w/2 - r, -h/2 + r, -90), (w/2 - r, h/2 - r, 0), (-w/2 + r, h/2 - r, 90), (-w/2 + r, -h/2 + r, 180)):
        for i in range(n + 1):
            a = math.radians(a0 + 90 * i / n); pts.append((cx + ox + r * math.cos(a), cy + oy + r * math.sin(a)))
    return pts

def dessin(c):
    cx, cy, w, h = 540, 1232, 780, 500
    c.poly(rrect(cx + 8, cy + 10, w, h, 70, 14), fill=(214, 214, 210))
    c.poly(rrect(cx, cy, w, h, 70, 14), fill=(226, 234, 232), outline=INK, w=11)
    c.poly(rrect(cx, cy, w, h, 70, 14), fill=None, outline=INK, w=120)
    c.poly(rrect(cx, cy, w, h, 70, 14), fill=None, outline=INK, w=11)
    x0, y1 = cx - w / 2, cy + h / 2
    for r in range(4):
        rr = 17 - r * 3.6; off = 92 + r * 30
        for k in range(0, int(w - 2 * off), 36 + r * 6):
            c.circle((x0 + off + k, y1 - off), rr, fill=INK)
    c.circle((cx + 120, y1 - 92 - 30), 17 - 3.6, fill=RED)
