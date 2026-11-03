# Dessin de la miniature de l'épisode 4 : UNE SEULE pièce (le cylindre et sa fente), sans nommer l'objet.
def dessin(c):
    cx, cy, R = 540, 1232, 235
    c.circle((cx + 8, cy + 10), R, fill=(214, 214, 210))
    c.circle((cx, cy), R, fill=(205, 205, 200), outline=INK, w=11)
    c.circle((cx, cy), R * 0.84, fill=(242, 242, 238), outline=INK, w=6)
    c.poly([(cx - 22, cy - 140), (cx + 22, cy - 140), (cx + 22, cy + 20), (cx - 22, cy + 20)], fill=INK)
    c.poly([(cx - 62, cy + 20), (cx + 62, cy + 20), (cx + 62, cy + 62), (cx - 62, cy + 62)], fill=INK)
    c.circle((cx, cy - 175), 11, fill=RED)
