# Dessin de la miniature de l'épisode 16 : UNE SEULE pièce (le disque du dessous, percé de deux trous), sans nommer l'objet.
def dessin(c):
    cx, cy = 540, 1232
    c.circle((cx + 9, cy + 11), 235, fill=(214, 214, 210))
    c.circle((cx, cy), 235, fill=(242, 242, 238), outline=INK, w=10)
    for dx in (-95, 95):
        c.circle((cx + dx, cy), 58, fill=INK)
    c.circle((cx + 95, cy), 22, fill=RED)
