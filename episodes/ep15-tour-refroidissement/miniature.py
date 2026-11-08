# Dessin de la miniature de l'épisode 15 : tour de refroidissement hyperboloïde, col marqué en vert.
def profil(cy, k):
    # demi-largeur de la tour à la hauteur relative k (0 haut, 1 bas), col vers k = 0,65
    return 150 + 110 * ((k - 0.65) / 0.65) ** 2 if k < 0.65 else 150 + 95 * ((k - 0.65) / 0.35) ** 2

def dessin(c):
    cx, top, bot = 540, 1000, 1470
    L = [(cx - profil(0, k / 40) , top + (bot - top) * k / 40) for k in range(41)]
    R = [(cx + profil(0, k / 40) , top + (bot - top) * k / 40) for k in range(41)]
    c.poly([(x + 10, y + 12) for x, y in L + R[::-1]], fill=(214, 214, 210))
    c.poly(L + R[::-1], fill=(236, 236, 232), outline=INK, w=10)
    gy = top + (bot - top) * 0.65
    c.line([(cx - profil(0, 0.65), gy), (cx + profil(0, 0.65), gy)], 9, RED)
