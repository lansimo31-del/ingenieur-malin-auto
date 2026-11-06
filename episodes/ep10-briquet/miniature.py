# Dessin de la miniature de l'épisode 10 : UNE SEULE pièce (le réservoir de gaz liquide), sans nommer l'objet.
def rrect(cx, cy, w, h, r, n=14):
    pts = []
    for (ox, oy, a0) in ((w/2 - r, -h/2 + r, -90), (w/2 - r, h/2 - r, 0), (-w/2 + r, h/2 - r, 90), (-w/2 + r, -h/2 + r, 180)):
        for i in range(n + 1):
            a = math.radians(a0 + 90 * i / n); pts.append((cx + ox + r * math.cos(a), cy + oy + r * math.sin(a)))
    return pts

def dessin(c):
    cx, cy = 540, 1232
    c.poly(rrect(cx + 8, cy + 10, 330, 470, 46), fill=(214, 214, 210))
    c.poly(rrect(cx, cy, 330, 470, 46), fill=(242, 242, 238), outline=INK, w=11)
    c.poly([(cx - 150, cy - 40), (cx + 150, cy - 40), (cx + 150, cy + 200), (cx - 150, cy + 200)], fill=(236, 214, 150))
    c.line([(cx - 150, cy - 40), (cx + 150, cy - 40)], 6, INK)
    c.circle((cx, cy + 75), 11, fill=RED)
