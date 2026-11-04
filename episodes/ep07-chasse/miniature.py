# Dessin de la miniature de l'épisode 7 : UNE SEULE pièce, le réservoir plein d'eau (sans nommer l'objet).
def dessin(c):
    x0, x1, y0, y1 = 300, 780, 1010, 1470
    c.poly([(x0 + 8, 1130 + 10), (x1 + 8, 1130 + 10), (x1 + 8, y1 + 10), (x0 + 8, y1 + 10)], fill=(214, 214, 210))
    c.poly([(x0 + 6, 1130), (x1 - 6, 1130), (x1 - 6, y1 - 4), (x0 + 6, y1 - 4)], fill=(206, 226, 222))
    c.line([(x0, y0), (x0, y1), (x1, y1), (x1, y0)], 11, INK)
    c.line([(x0 + 6, 1130), (x1 - 6, 1130)], 5, RED)
