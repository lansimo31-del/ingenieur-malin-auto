# Dessin de la miniature de l'épisode 14 : deux touches de clavier, F et J, avec leur petite bosse verte.
def touche(c, cx, cy, lettre, bosse=True):
    c.poly([(cx - 150 + 9, cy - 135 + 11), (cx + 150 + 9, cy - 135 + 11), (cx + 150 + 9, cy + 135 + 11), (cx - 150 + 9, cy + 135 + 11)], fill=(214, 214, 210))
    c.poly([(cx - 150, cy - 135), (cx + 150, cy - 135), (cx + 150, cy + 135), (cx - 150, cy + 135)], fill=(242, 242, 238), outline=INK, w=10)
    c.poly([(cx - 118, cy - 105), (cx + 118, cy - 105), (cx + 118, cy + 85), (cx - 118, cy + 85)], fill=(250, 250, 247), outline=INK, w=4)
    c.text((cx, cy - 8), lettre, FA, 150, INK, anchor="mm")
    if bosse: c.circle((cx, cy + 58), 13, fill=RED)

def dessin(c):
    cy = 1232
    touche(c, 340, cy, "F"); touche(c, 740, cy, "J")
