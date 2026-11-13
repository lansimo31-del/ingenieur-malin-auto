# Dessin de la miniature de l'épisode 19 : une seule pièce, la vis en spirale (l'objet n'est pas nommé).
def dessin(c):
    cx, y0 = 540, 1010
    pts = []
    for k in range(7 * 10 + 1):
        u = k / 70; half = 80 * (1 - 0.82 * max(0, u - 0.82) / 0.18)
        pts.append((cx + half * math.sin(2 * math.pi * 7 * u), y0 + 440 * u))
    c.line([(x + 8, y + 9) for x, y in pts], 18, (214, 214, 210))
    c.line(pts, 18, INK)
    c.circle((cx, y0 - 20), 26, outline=RED, w=10)
