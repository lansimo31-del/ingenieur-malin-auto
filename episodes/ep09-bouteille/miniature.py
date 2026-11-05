# Dessin de la miniature de l'épisode 9 : le fond d'une bouteille vu de dessous, cinq pieds en pétales, point d'injection en vert.
def dessin(c):
    cx, cy, R = 540, 1232, 245
    c.circle((cx + 8, cy + 10), R, fill=(214, 214, 210))
    c.circle((cx, cy), R, fill=(226, 234, 232), outline=INK, w=11)
    for k in range(5):
        ang = -math.pi / 2 + 2 * math.pi * k / 5
        c.circle((cx + R * 0.58 * math.cos(ang), cy + R * 0.58 * math.sin(ang)), R * 0.27, fill=(205, 205, 200), outline=INK, w=9)
    c.circle((cx, cy), R * 0.11, fill=RED)
