
import random
def stone(c, cx, cy, r, seed, fill):
    rnd = random.Random(seed); n = rnd.choice([6, 7, 8])
    pts = []
    for k in range(n):
        a = 2 * math.pi * k / n + rnd.uniform(-0.25, 0.25)
        rr = r * rnd.uniform(0.72, 1.12)
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a) * 0.82))
    c.poly(pts, fill=fill, outline=INK, w=5)
    # arête interne pour le côté "cassé"
    c.line([pts[0], (cx + (pts[0][0] - cx) * 0.2, cy + (pts[0][1] - cy) * 0.2), pts[n // 2]], 3, GREY)

def rail_section(c, x, ytop):
    c.poly([(x - 48, ytop), (x + 48, ytop), (x + 48, ytop + 30), (x - 48, ytop + 30)], fill=(255, 255, 255), outline=INK, w=6)
    c.poly([(x - 12, ytop + 30), (x + 12, ytop + 30), (x + 12, ytop + 100), (x - 12, ytop + 100)], fill=(255, 255, 255), outline=INK, w=6)
    c.poly([(x - 60, ytop + 100), (x + 60, ytop + 100), (x + 60, ytop + 124), (x - 60, ytop + 124)], fill=(255, 255, 255), outline=INK, w=6)

def thumb():
    im = Image.new("RGB", (W * S, H * S), BG); c = C(im)
    c.text((540, 330), "POURQUOI C'EST CONÇU COMME ÇA ?", FM, 34, GREY, anchor="ms")
    c.line([(150, 362), (930, 362)], 5, GM)
    c.text((540, 560), "POURQUOI DES", FA, 100, INK, anchor="ms")
    c.text((540, 720), "CAILLOUX", FA, 160, RED, anchor="ms")
    c.text((540, 870), "SOUS LES RAILS ?", FA, 92, INK, anchor="ms")
    # coupe de voie
    ys = 1060
    for x in (330, 750): rail_section(c, x, ys)
    c.poly([(150, ys + 124), (930, ys + 124), (930, ys + 184), (150, ys + 184)], fill=(255, 255, 255), outline=INK, w=7)
    c.text((540, ys + 166), "TRAVERSE", FM, 30, GREY, anchor="ms")
    rnd = random.Random(4)
    row = 0
    for y in (ys + 232, ys + 300, ys + 366):
        x = 130 + (row % 2) * 45
        while x < 960:
            r = rnd.uniform(36, 48)
            stone(c, x, y, r, rnd.randint(0, 9999), HOLE)
            x += 90
        row += 1
    # curseur qui pointe une pierre
    px, py = 640, ys + 318
    pts = [(0, 0), (0, 27), (7, 21), (12, 32), (17, 30), (12, 19), (21, 19)]
    k = 1.8
    c.poly([(px + 5 + a * k, py + 8 + b * k) for a, b in pts], fill=GM)
    c.poly([(px + a * k, py + b * k) for a, b in pts], fill=(255, 255, 255), outline=INK, w=4)
    c.text((540, 1560), "L'INGÉNIEUR MALIN EXPLIQUE", FM, 34, GREY, anchor="ms")
    return im.resize((W, H), Image.LANCZOS)
