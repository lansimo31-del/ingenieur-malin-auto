# Dessin de la miniature de l'épisode 6 : le profil en I (poutre) avec un petit point vert au centre de l'âme.
def dessin(c):
    cx, cy, k = 540, 1232, 2.4
    h, w, tf, tw_ = 200 * k, 100 * k * 1.4, 8.5 * k * 1.8, 5.6 * k * 1.8
    def prof(dx, dy):
        top = cy - h / 2 + dy; bot = cy + h / 2 + dy; x = cx + dx
        return [(x - w / 2, top), (x + w / 2, top), (x + w / 2, top + tf), (x + tw_ / 2, top + tf), (x + tw_ / 2, bot - tf), (x + w / 2, bot - tf),
                (x + w / 2, bot), (x - w / 2, bot), (x - w / 2, bot - tf), (x - tw_ / 2, bot - tf), (x - tw_ / 2, top + tf), (x - w / 2, top + tf)]
    c.poly(prof(8, 10), fill=(214, 214, 210))
    c.poly(prof(0, 0), fill=(205, 205, 200), outline=INK, w=11)
    c.circle((cx, cy), 14, fill=RED)
