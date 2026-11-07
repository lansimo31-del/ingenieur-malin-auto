# Dessin de la miniature de l'épisode 13 : UNE SEULE pièce (la bande de petites barres de métal), sans nommer l'objet.
def dessin(c):
    cx, cy = 540, 1232
    for k in range(7):
        x = cx - 270 + k * 90
        c.poly([(x + 8 + 6, cy - 150 + 10), (x + 8 + 76, cy - 150 + 10), (x + 8 + 76, cy + 150 + 10), (x + 8 + 6, cy + 150 + 10)], fill=(214, 214, 210))
    for k in range(7):
        x = cx - 270 + k * 90
        c.poly([(x + 6, cy - 150), (x + 76, cy - 150), (x + 76, cy + 150), (x + 6, cy + 150)], fill=(200, 204, 212), outline=INK, w=9)
    c.line([(cx - 270, cy + 150), (cx + 270 + 90 - 8, cy + 150)], 12, INK)
    c.circle((cx, cy - 60), 12, fill=RED)
