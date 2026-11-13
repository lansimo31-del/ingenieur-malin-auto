# Dessin de la miniature de l'épisode 18 : un cadre de vélo (deux triangles), le triangle avant en vert.
def dessin(c):
    cx, cy = 540, 1232
    R, B, S, H1, H2, F = (cx - 240, cy + 130), (cx - 70, cy + 130), (cx - 120, cy - 130), (cx + 160, cy - 130), (cx + 140, cy - 70), (cx + 260, cy + 130)
    for ctr in (R, F): c.circle(ctr, 120, outline=GM, w=10)
    for a, b in ((S, R), (B, R), (H1, F)): c.line([a, b], 16, INK)
    for a, b in ((S, H1), (S, B), (H2, B)): c.line([a, b], 18, RED)
    for p in (S, H1, B, R): c.circle(p, 11, fill=BG, outline=INK, w=5)
