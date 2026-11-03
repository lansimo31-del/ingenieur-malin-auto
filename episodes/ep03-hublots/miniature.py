# Dessin de la miniature de l'épisode 3 : un hublot d'avion (forme arrondie, trois épaisseurs, petit trou vert).
# Utilise les outils de render/engine/head.py (C, mix, INK, RED = accent vert, BG, circ_pts).
def rrect(cx, cy, w, h, r, n=14):
    pts = []
    for (ox, oy, a0) in ((w/2 - r, -h/2 + r, -90), (w/2 - r, h/2 - r, 0), (-w/2 + r, h/2 - r, 90), (-w/2 + r, -h/2 + r, 180)):
        for i in range(n + 1):
            a = math.radians(a0 + 90 * i / n); pts.append((cx + ox + r * math.cos(a), cy + oy + r * math.sin(a)))
    return pts

def dessin(c):
    cx, cy = 540, 1232
    c.poly(rrect(cx + 8, cy + 10, 430, 500, 150), fill=(214, 214, 210))                       # ombre portée
    c.poly(rrect(cx, cy, 430, 500, 150), fill=(205, 205, 200), outline=INK, w=11)            # cadre extérieur
    c.poly(rrect(cx, cy, 350, 420, 120), fill=(242, 242, 238), outline=INK, w=6)             # cadre intérieur
    c.poly(rrect(cx, cy - 6, 296, 360, 100), fill=(226, 234, 232), outline=INK, w=5)         # vitre
    for k, (x0, y0, x1, y1) in enumerate(((-90, -110, -20, -190), (-60, -40, 40, -150))):     # reflets
        c.line([(cx + x0, cy + y0), (cx + x1, cy + y1)], 9 - 2 * k, (250, 250, 248))
    c.circle((cx, cy + 142), 12, fill=RED)                                                    # le petit trou, en vert
    c.line([(cx - 120, cy + 215), (cx + 120, cy + 215)], 5, mix(BG, GREY, 0.8))               # ligne de volet
