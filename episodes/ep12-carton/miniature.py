# Dessin de la miniature de l'épisode 12 : coupe d'un carton ondulé (feuille plate, vagues, feuille plate), un point vert.
def dessin(c):
    cx, cy = 540, 1232
    x0, x1, n = cx - 330, cx + 330, 6
    top, bot = cy - 130, cy + 130
    c.poly([(x0 + 8, top - 14 + 10), (x1 + 8, top - 14 + 10), (x1 + 8, bot + 24 + 10), (x0 + 8, bot + 24 + 10)], fill=(214, 214, 210))
    pts = []
    for k in range(121):
        u = k / 120
        pts.append((x0 + (x1 - x0) * u, cy + 110 * math.sin(u * n * 2 * math.pi)))
    c.line(pts, 10, INK)
    c.poly([(x0, top - 30), (x1, top - 30), (x1, top - 6), (x0, top - 6)], fill=(236, 214, 150), outline=INK, w=9)
    c.poly([(x0, bot + 6), (x1, bot + 6), (x1, bot + 30), (x0, bot + 30)], fill=(236, 214, 150), outline=INK, w=9)
    c.circle((cx, cy), 12, fill=RED)
