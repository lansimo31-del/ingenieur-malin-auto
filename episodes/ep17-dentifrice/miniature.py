# Dessin de la miniature de l'épisode 17 : le bout plat d'un tube de dentifrice avec son carré de couleur.
def dessin(c):
    cx, cy = 540, 1232
    c.poly([(cx - 200 + 9, cy - 200 + 11), (cx + 200 + 9, cy - 200 + 11), (cx + 200 + 9, cy + 200 + 11), (cx - 200 + 9, cy + 200 + 11)], fill=(214, 214, 210))
    c.poly([(cx - 200, cy - 200), (cx + 200, cy - 200), (cx + 200, cy + 200), (cx - 200, cy + 200)], fill=(242, 242, 238), outline=INK, w=10)
    for k in range(7):
        y = cy + 100 + k * 14
        c.line([(cx - 200, y), (cx + 200, y)], 4, GM)
    c.poly([(cx - 55, cy + 30), (cx + 55, cy + 30), (cx + 55, cy + 140), (cx - 55, cy + 140)], fill=RED)
