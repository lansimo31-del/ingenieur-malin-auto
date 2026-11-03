# ================= BALLAST =================
import json, random, re
DUR = 53.4
RAW = json.load(open('/tmp/claude-0/work/ballast/a/words.json'))
CX = 540
ENV = None
FILL1 = (222, 222, 218); STF = (240, 240, 236)

# ---------- timings de mots : lissage par phrase / sous-phrase ----------
SENT = ["Ces cailloux sous les rails empêchent les rails de se tordre, l'été.",
 "Tu croyais qu'ils servaient juste à tenir la voie?", "Ils font bien plus.",
 "Quand l'acier chauffe, il se dilate, et il pousse sur les côtés.",
 "Les pierres, imbriquées autour des traverses, l'empêchent de bouger.",
 "Mais seulement si elles sont cassées, donc pointues.",
 "Des pierres rondes, elles, rouleraient les unes sur les autres.",
 "Elles répartissent aussi le poids du train, jusqu'à vingt-deux tonnes par essieu, au lieu de l'écraser en un seul point.",
 "Elles laissent la pluie s'écouler.", "Elles étouffent les vibrations.",
 "Et quand la voie s'affaisse, une machine tasse les pierres pour la redresser.",
 "Cinq rôles, pour de simples cailloux.", "Cet été, quand il fera chaud, pense à eux.",
 "Prochain objet, pourquoi les hublots d'avion sont ronds.", "Abonne-toi."]
def build_words():
    words = []; idx = 0
    for s in SENT:
        toks = s.split(); n = len(toks)
        seg = RAW[idx:idx + n]; idx += n
        # sous-phrases (virgules)
        phr = []; cur = []
        for k, tk in enumerate(toks):
            cur.append(k)
            if tk.endswith(',') or tk.endswith(':') or k == n - 1: phr.append(cur); cur = []
        for pi, ph in enumerate(phr):
            st = seg[ph[0]][1]
            en = seg[ph[-1]][2]
            if pi + 1 < len(phr): en = min(en, seg[phr[pi + 1][0]][1])
            ch = sum(len(toks[k]) + 2 for k in ph)
            en = min(en, st + ch * 0.085 + 0.25)
            if en <= st + 0.1: en = st + 0.1 * len(ph)
            tot = ch; a = st
            for k in ph:
                d = (len(toks[k]) + 2) / tot * (en - st)
                words.append([toks[k], a, a + d]); a += d
    return words
WORDS = build_words()
# chunks de 2 à 5 mots, coupés aux ponctuations
CHUNKS = []; i = 0
while i < len(WORDS):
    j = i
    while j < len(WORDS) - 1 and j - i < 3 and not re.search(r"[.,?:]$", WORDS[j][0]) and sum(len(WORDS[k][0]) + 1 for k in range(i, j + 2)) <= 22: j += 1
    CHUNKS.append((i, j)); i = j + 1
EMPH = {"cailloux", "tordre,", "l'été.", "plus.", "dilate,", "pousse", "cassées,", "pointues.", "rondes,", "rouleraient", "vingt-deux", "pluie", "vibrations.", "tasse", "Cinq", "Abonne-toi.", "chaud,", "ronds."}

# ---------- éléments ----------
def stone_poly(cx, cy, r, seed, flat=0.82):
    rnd = random.Random(seed); n = rnd.choice([6, 7, 8]); pts = []
    for k in range(n):
        a = 2 * math.pi * k / n + rnd.uniform(-0.25, 0.25)
        rr = r * rnd.uniform(0.74, 1.1)
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a) * flat))
    return pts
def stone(c, cx, cy, r, seed, a=1.0, fill=None):
    pts = stone_poly(cx, cy, r, seed)
    c.poly(pts, fill=mix(BG, fill or STF, a), outline=mix(BG, INK, a), w=5)
def pen_poly(c, pts, p, w, col, closed=False):
    pp = pts + [pts[0]] if closed else pts
    L = [math.hypot(pp[i + 1][0] - pp[i][0], pp[i + 1][1] - pp[i][1]) for i in range(len(pp) - 1)]
    tot = sum(L); tgt = tot * cl(p); acc = 0; out = [pp[0]]
    for i, l in enumerate(L):
        if acc + l <= tgt: out.append(pp[i + 1]); acc += l
        else:
            u = (tgt - acc) / l if l else 0
            out.append((pp[i][0] + (pp[i + 1][0] - pp[i][0]) * u, pp[i][1] + (pp[i + 1][1] - pp[i][1]) * u)); break
    if len(out) > 1 and p > 0: c.line(out, w, col)
def arrow(c, a, b, w, col, hs=26):
    c.rline([a, b], w, col)
    ang = math.atan2(b[1] - a[1], b[0] - a[0])
    for s in (-1, 1):
        c.rline([b, (b[0] - hs * math.cos(ang + s * 0.5), b[1] - hs * math.sin(ang + s * 0.5))], w, col)
def checkmark(c, x, y, sc=1.0, a=1.0):
    col = mix(BG, RED, a)
    pts = [(x - 26 * sc, y + 2 * sc), (x - 8 * sc, y + 22 * sc), (x + 28 * sc, y - 24 * sc)]
    c.rline(pts, 13 * sc, col)
def label(c, x, y, s, size=64, col=None, a=1.0, font_=None):
    c.text((x, y), s, font_ or FA, size, mix(BG, col or INK, a), anchor="ms")
def rich(c, y, parts, size=76, a=1.0, dy=0):
    # parts: [(texte, col)] centré
    tot = sum(tw(t, FA, size) for t, _ in parts); x = CX - tot / 2
    for t, col in parts:
        w = tw(t, FA, size); c.text((x, y + dy), t, FA, size, mix(BG, col, a), anchor="ls"); x += w
def sun(c, x, y, a=1.0, r=44):
    c.circle((x, y), r, outline=mix(BG, INK, a), w=7)
    for k in range(10):
        an = k * math.pi / 5
        c.rline([(x + (r + 16) * math.cos(an), y + (r + 16) * math.sin(an)), (x + (r + 40) * math.cos(an), y + (r + 40) * math.sin(an))], 7, mix(BG, INK, a))

# ----- vue de dessus (plan) -----
PY1, PY2 = 760, 930
SLX = [150 + 100 * k for k in range(9)]  # traverses
def bump(x, A, c0=540, wd=250):
    d = (x - c0) / wd
    return A * math.exp(-d * d * 2.2)
STONES_TOP = []
_r = random.Random(11)
for k in range(8):
    for row in range(4):
        pass
def top_stone_positions():
    rnd = random.Random(5); out = []
    for gx in range(len(SLX) - 1):
        x0 = SLX[gx] + 36; x1 = SLX[gx + 1] - 36
        for (ya, yb) in [(650, 735), (958, 1050), (770, 920)]:
            for q in range(2 if ya == 770 else 3):
                out.append((rnd.uniform(x0, x1), rnd.uniform(ya, yb) if ya != 770 else rnd.choice([rnd.uniform(790, 815), rnd.uniform(880, 905)]), rnd.uniform(19, 26), rnd.randint(0, 99999)))
    return out
TOPS = top_stone_positions()
def rail_top(c, A, y0, col=INK, grow=0.0):
    pts = [(x, y0 + bump(x, A)) for x in range(90, 971, 20)]
    w = 22 + grow
    c.line(pts, w + 8, col); c.line(pts, w - 6, (255, 255, 255))
def top_view(c, t, A=0.0, stones=0.0, rails=1.0, sleep=1.0, t_st=0.0, a_all=1.0):
    # traverses
    for k, x in enumerate(SLX):
        p = eob(prog(sleep, k * 0.07, k * 0.07 + 0.5)) if sleep < 1.5 else 1
        h = 330 * cl(p)
        if h > 4: c.poly([(x - 24, 845 - h / 2), (x + 24, 845 - h / 2), (x + 24, 845 + h / 2), (x - 24, 845 + h / 2)], fill=FILL1, outline=INK, w=5)
    # pierres
    n = len(TOPS)
    for i, (x, y, r, sd) in enumerate(TOPS):
        u = prog(stones, i / n * 0.7, i / n * 0.7 + 0.3)
        if u > 0.02:
            ex = bump(x, A * 0.0)
            stone(c, x, y, r * eob(u), sd, 1.0)
    if rails > 0:
        for y0 in (PY1, PY2):
            pts_n = int(1 + 45 * cl(rails))
            xs = [90 + (970 - 90) * k / 45 for k in range(pts_n + 1)]
            pts = [(x, y0 + bump(x, A)) for x in xs]
            if len(pts) > 1:
                c.line(pts, 30, INK); c.line(pts, 18, (255, 255, 255))

# ----- vue de côté -----
RY = 760
SSL = [220, 540, 860]
SIDE = []
def side_stones():
    rnd = random.Random(21); out = []
    for row, (y, n) in enumerate([(925, 9), (990, 9), (1055, 9), (1115, 8)]):
        for k in range(n):
            out.append((100 + k * 100 + (row % 2) * 48 + rnd.uniform(-12, 12), y + rnd.uniform(-10, 10), rnd.uniform(30, 40), rnd.randint(0, 99999)))
    return out
SIDES = side_stones()
def side_view(c, t, t0, sag=0.0, press=0.0, dim_rail=1.0):
    u = prog(t, t0, t0 + 0.6)
    ys = lambda x: RY + sag * math.exp(-((x - 540) / 260) ** 2 * 2)
    # pierres (derrière)
    n = len(SIDES)
    for i, (x, y, r, sd) in enumerate(SIDES):
        pu = prog(t, t0 + 0.2 + 0.4 * i / n, t0 + 0.5 + 0.4 * i / n)
        if pu > 0.02:
            stone(c, x, y + sag * 0.6 * math.exp(-((x - 540) / 260) ** 2 * 2) * (1 if y < 1000 else 0.3), r * eob(pu), sd)
    # traverses
    for k, x in enumerate(SSL):
        pu = eob(prog(t, t0 + 0.1 + k * 0.1, t0 + 0.5 + k * 0.1))
        if pu > 0.02:
            h = 70 * pu; yy = RY + 44 + sag * math.exp(-((x - 540) / 260) ** 2 * 2)
            c.poly([(x - 90, yy), (x + 90, yy), (x + 90, yy + h), (x - 90, yy + h)], fill=FILL1, outline=INK, w=6)
    # rail
    p = eo(prog(t, t0, t0 + 0.5)) * dim_rail
    xs = [90 + 880 * p * k / 40 for k in range(41)]
    if p > 0.02:
        head = [(x, ys(x) - 6) for x in xs]
        c.line(head, 36, INK); c.line(head, 24, (255, 255, 255))
        foot = [(x, ys(x) + 24) for x in xs]
        c.line(foot, 14, INK)

# ----- curseur -----
CUR = [(0.0, 900, 1000), (0.7, 850, 640), (1.7, 540, 780), (3.1, 300, 700), (3.9, 640, 1000), (4.6, 540, 1000),
       (5.3, 420, 1040), (6.3, 700, 960), (7.1, 540, 880), (7.9, 190, 690), (9.5, 120, 860), (10.6, 800, 760), (12.0, 780, 760), (13.3, 540, 700),
       (14.5, 330, 1010), (16.0, 760, 1010), (17.4, 560, 850), (18.7, 540, 720), (20.4, 640, 840), (21.8, 500, 900), (23.4, 740, 930), (25.0, 330, 940),
       (25.9, 560, 560), (27.5, 540, 900), (29.5, 400, 1000), (30.6, 460, 500), (32.3, 740, 1000), (33.0, 300, 780), (35.3, 700, 1020),
       (36.4, 540, 800), (38.0, 380, 700), (39.4, 700, 820), (41.0, 560, 780), (41.9, 190, 780), (42.8, 880, 780), (43.8, 540, 840), (45.5, 640, 700),
       (47.2, 480, 960), (48.4, 540, 760), (49.8, 540, 770), (50.1, 540, 1000), (50.6, 540, 1012), (52.0, 700, 1080), (53.4, 880, 1200)]
CLICKS = [5.0, 6.43, 7.5, 13.9, 19.6, 25.9, 30.5, 32.7, 38.4, 41.9, 50.5]
def cursor_pos(t):
    for i in range(len(CUR) - 1):
        a, b = CUR[i], CUR[i + 1]
        if a[0] <= t <= b[0]:
            u = eio(prog(t, a[0], b[0])); dx, dy = b[1] - a[1], b[2] - a[2]; L = math.hypot(dx, dy) + 1e-6
            bow = math.sin(u * math.pi) * min(40, 0.06 * L)
            return (a[1] + dx * u - dy / L * bow, a[2] + dy * u + dx * 0 + dx / L * bow)
    return CUR[-1][1:]
def draw_cursor(c, t):
    x, y = cursor_pos(t)
    for ck in CLICKS:
        u = t - ck
        if 0 <= u < 0.45:
            px, py = cursor_pos(ck); p = eo(u / 0.45)
            c.circle((px, py), 8 + 40 * p, outline=mix(BG, RED, 1 - p), w=5)
    press = 0.86 if any(0 <= t - ck < 0.12 for ck in CLICKS) else 1.0
    k = 1.25 * press
    pts = [(0, 0), (0, 27), (7, 21), (12, 32), (17, 30), (12, 19), (21, 19)]
    c.poly([(x + 4 + px * k, y + 6 + py * k) for px, py in pts], fill=GM)
    c.poly([(x + px * k, y + py * k) for px, py in pts], fill=(255, 255, 255), outline=INK, w=3.2)

# ----- scènes -----
def sc_hook(c, t):   # 0 - 5.0
    ta = prog(t, 0.1, 0.5)
    rich(c, 500, [("CAILLOUX", RED), (" SOUS", INK)], 92, eo(ta))
    rich(c, 590, [("LES RAILS", INK)], 92, eo(prog(t, 0.25, 0.65)))
    # soleil
    sa = eo(prog(t, 0.7, 1.1)); 
    if sa > 0.02: sun(c, 860, 650, sa, 40)
    # état du rail
    A = 0.0
    if t < 3.0: A = 95 * eio(prog(t, 1.1, 2.3))
    else: A = 95 * (1 - eio(prog(t, 3.3, 4.1)))
    rails = eo(prog(t, 0.2, 0.9)); stones = prog(t, 2.9, 3.9)
    top_view(c, t, A=A, stones=stones, rails=rails, sleep=prog(t, 0.0, 0.9))
    if 1.9 < t < 3.2:
        al = eo(prog(t, 1.9, 2.2)) * (1 - eo(prog(t, 2.9, 3.2)))
        arrow(c, (440, 880), (440, 800 - 95 * 0.0), 8, mix(BG, RED, al)) if False else None
        for (xx, yy, d) in ((540, PY1 - 44, -1), (540, PY2 + 70, 1)):
            arrow(c, (xx, yy + (-d) * 6 if False else yy), (xx, yy + d * 70), 9, mix(BG, RED, al))
    if t > 4.2:
        checkmark(c, 860, 860, eob(prog(t, 4.2, 4.5)) * 1.4)

def sc_q(c, t):      # 5.0 - 7.44
    ta = eo(prog(t, 5.0, 5.35))
    sideon = 5.0
    side_view(c, t, 5.0)
    if t < 6.43:
        rich(c, 520, [("JUSTE POUR", INK)], 78, ta); rich(c, 610, [("TENIR LA VOIE ", INK), ("?", RED)], 78, ta)
    else:
        a = eo(prog(t, 6.43, 6.8))
        pen_poly(c, [(290, 640), (790, 640)], prog(t, 6.43, 6.7), 9, RED) if t < 6.9 else None
        rich(c, 590, [("5 RÔLES", RED)], 130, a, dy=(1 - a) * 20)

def sc_heat(c, t):   # 7.44 - 13.84
    A = 90 * eio(prog(t, 11.9, 13.2))
    # fond
    top_view(c, t, A=A, stones=0.0, rails=1.0, sleep=9)
    rich(c, 520, [("1 · ", GREY), ("LA CHALEUR", INK)], 74, eo(prog(t, 7.5, 7.9)))
    # thermomètre
    tx, ty0, ty1 = 160, 640, 1040
    ta = eo(prog(t, 7.6, 8.0))
    if ta > 0.02:
        c.line([(tx, ty0), (tx, ty1)], 40, mix(BG, INK, ta)); c.line([(tx, ty0), (tx, ty1)], 26, mix(BG, (255, 255, 255), ta))
        c.circle((tx, ty1 + 6), 36, fill=mix(BG, RED, ta), outline=mix(BG, INK, ta), w=7)
        fill = 0.05 + 0.95 * eio(prog(t, 8.0, 9.4))
        c.line([(tx, ty1), (tx, ty1 - (ty1 - ty0) * fill)], 18, mix(BG, RED, ta))
    if t > 8.1: sun(c, 860, 640, eo(prog(t, 8.1, 8.5)), 36)
    # dilatation (flèches aux extrémités)
    if 9.4 <= t < 11.8:
        al = eo(prog(t, 9.4, 9.8)) * (1 - eo(prog(t, 11.3, 11.8)))
        for y0 in (PY1, PY2):
            arrow(c, (118, y0), (96, y0) if False else (92, y0), 9, mix(BG, RED, al))
            arrow(c, (940, y0), (975, y0), 9, mix(BG, RED, al))
        label(c, 540, 1200, "L'ACIER S'ALLONGE", 66, RED, al)
    if t >= 11.9:
        al = eo(prog(t, 11.9, 12.3))
        for yy, d in ((PY1 - 56, -1), (PY2 + 56, 1)):
            arrow(c, (540, yy - d * (A * 0.0) if False else yy), (540, yy + d * 64), 9, mix(BG, RED, al))
        label(c, 540, 1200, "IL POUSSE SUR LES CÔTÉS", 62, RED, al)

def sc_lock(c, t):   # 13.84 - 18.44
    A = 90 * (1 - eio(prog(t, 16.9, 17.8)))
    top_view(c, t, A=A, stones=prog(t, 13.95, 15.9), rails=1.0, sleep=9)
    rich(c, 520, [("LES PIERRES ", INK), ("BLOQUENT", RED)], 74, 1.0)
    if t > 17.7:
        checkmark(c, 860, 650, eob(prog(t, 17.7, 18.0)) * 1.4)
    if 16.6 < t < 18.0:
        al = eo(prog(t, 16.6, 16.9))
        label(c, 540, 1200, "RAIL BLOQUÉ", 62, RED, al)

def sc_sharp(c, t):  # 18.44 - 21.6
    rich(c, 520, [("CASSÉES", RED), (" = POINTUES", INK)], 74, eo(prog(t, 18.5, 18.9)))
    # grosse pierre ronde qui se brise
    if t < 19.5:
        a = eo(prog(t, 18.5, 18.9))
        c.circle((CX, 830), 150 * eob(prog(t, 18.5, 18.9)), fill=mix(BG, STF, a), outline=mix(BG, INK, a), w=8)
    else:
        sp = eo(prog(t, 19.5, 20.2))
        zz = [(CX + 40, 680), (CX - 20, 760), (CX + 50, 820), (CX - 30, 890), (CX + 20, 980)]
        left = [(CX + 40, 680), (CX - 60, 700), (CX - 140, 770), (CX - 150, 860), (CX - 100, 950), (CX + 20, 980), (CX - 30, 890), (CX + 50, 820), (CX - 20, 760)]
        right = [(CX + 40, 680), (CX + 110, 710), (CX + 160, 800), (CX + 140, 910), (CX + 20, 980), (CX - 30, 890), (CX + 50, 820), (CX - 20, 760)]
        for pts, dx in ((left, -70), (right, 70)):
            c.poly([(x + dx * sp * 0.6, y) for x, y in pts], fill=STF, outline=INK, w=7)
        if t > 20.1:
            al = eo(prog(t, 20.1, 20.5))
            label(c, CX, 1130, "ARÊTES VIVES : ÇA S'EMBOÎTE", 58, RED, al)

def sc_round(c, t):  # 21.6 - 25.65
    rich(c, 520, [("PIERRES ", INK), ("RONDES", RED)], 74, eo(prog(t, 21.6, 22.0)))
    g = 960
    c.line([(90, g), (90 + 880 * eo(prog(t, 21.6, 22.1)), g)], 8, INK)
    R = 78
    roll = eio(prog(t, 23.0, 25.1))
    for k, (x0, dirn) in enumerate(((300, -1), (540, 0), (780, 1))):
        x = x0 + dirn * 150 * roll; ang = dirn * roll * 4.2
        pp = eob(prog(t, 21.8 + k * 0.12, 22.2 + k * 0.12))
        if pp > 0.02:
            c.circle((x, g - R * pp), R * pp, fill=STF, outline=INK, w=7)
            c.rline([(x, g - R), (x + R * 0.7 * math.cos(ang), g - R + R * 0.7 * math.sin(ang))], 6, INK)
    if t > 23.0:
        al = eo(prog(t, 23.0, 23.4))
        arrow(c, (300, 790), (210, 790), 9, mix(BG, RED, al)); arrow(c, (780, 790), (870, 790), 9, mix(BG, RED, al))
        label(c, CX, 1130, "ÇA ROULE", 70, RED, al)

def wheel(c, x, y, R, spin, a=1.0):
    c.circle((x, y), R, fill=mix(BG, (255, 255, 255), a), outline=mix(BG, INK, a), w=8)
    c.circle((x, y), R * 0.22, fill=mix(BG, INK, a))
    for k in range(4):
        an = spin + k * math.pi / 2
        c.rline([(x, y), (x + R * 0.8 * math.cos(an), y + R * 0.8 * math.sin(an))], 5, mix(BG, INK, a))

def sc_weight(c, t):  # 25.65 - 30.38
    side_view(c, t, 25.2 if False else 0.0 + 0.0)  # déjà en place
    rich(c, 445, [("2 · ", GREY), ("LE POIDS", INK)], 68, eo(prog(t, 25.7, 26.1)))
    # roue sur le rail
    R = 80; x = 540; y = RY - 6 - 18 - R + 2
    pa = eob(prog(t, 25.7, 26.2))
    if pa > 0.02:
        wheel(c, x, y, R * pa, t * 0.0)
        c.poly([(330, y - R - 120), (750, y - R - 120), (750, y - R + 10), (330, y - R + 10)], fill=(255, 255, 255), outline=INK, w=7) if False else None
    if t > 26.4:
        al = eo(prog(t, 26.4, 26.8))
        arrow(c, (540, 610), (540, y - R - 4 if False else 640), 12, mix(BG, RED, al))
        rich(c, 590, [("22,5 T", RED), (" PAR ESSIEU", INK)], 56, al) if False else None
    if t > 26.5:
        label(c, 540, 525, "22,5 T PAR ESSIEU", 60, RED, eo(prog(t, 26.5, 26.9)))
    if t > 27.8:
        al = eo(prog(t, 27.8, 28.4))
        cp = (540, RY + 30)
        for k, (ex, ey) in enumerate([(250, 1060), (400, 1100), (540, 1120), (680, 1100), (830, 1060)]):
            pr = prog(t, 27.8 + k * 0.08, 28.4 + k * 0.08)
            if pr > 0: c.rline([cp, (cp[0] + (ex - cp[0]) * eo(pr), cp[1] + (ey - cp[1]) * eo(pr))], 7, mix(BG, RED, 1.0))
        label(c, 540, 1190 if False else 1175, "LA CHARGE SE RÉPARTIT", 56, RED, al)

def sc_water(c, t):   # 30.38 - 32.6
    side_view(c, 99, 0.0)
    rich(c, 500, [("3 · ", GREY), ("L'EAU", INK)], 72, eo(prog(t, 30.4, 30.8)))
    for k in range(7):
        x = 160 + k * 120 + (k % 2) * 30
        ph = ((t - 30.5) * 1.15 + k * 0.17) % 1.0
        if t > 30.5 + k * 0.05:
            y = 600 + ph * 520
            if y < 760 or True:
                c.poly([(x, y - 48), (x - 22, y), (x, y + 14), (x + 22, y)], fill=RED)
    if t > 31.6:
        al = eo(prog(t, 31.6, 32.0))
        for xx in (150, 930):
            arrow(c, (xx - (0 if xx < 500 else 0), 1090), (xx - 70 if xx < 500 else xx + 40, 1090), 9, mix(BG, RED, al)) if False else None
        label(c, 540, 1235, "ELLE S'ÉCOULE", 60, RED, al)

def sc_vib(c, t):     # 32.6 - 35.9
    side_view(c, 99, 0.0)
    rich(c, 500, [("4 · ", GREY), ("LES VIBRATIONS", INK)], 72, eo(prog(t, 32.65, 33.05)))
    R = 70; x = 220; y = RY - 6 - 18 - R + 2
    wheel(c, x, y, R, 0)
    for k in range(4):
        ph = ((t - 33.1) * 0.85 + k * 0.25) % 1.0
        if t > 33.1:
            r = 60 + ph * 640; al = (1 - ph) * 0.9
            pts = circ_pts(x, RY + 20, r, 40, 0.15, math.pi - 0.15 if False else 0.9 * math.pi)
            pts = [(px, py) for px, py in pts if py > RY + 30 and px < 960]
            if len(pts) > 1: c.line(pts, 8, mix(BG, RED, al))
    if t > 34.2:
        label(c, 540, 1235, "ÉTOUFFÉES PAR LES PIERRES", 56, RED, eo(prog(t, 34.2, 34.6)))

def sc_tamp(c, t):    # 35.9 - 41.79
    sag = 46 * eio(prog(t, 36.0, 36.9)) * (1 - eio(prog(t, 40.6, 41.6)))
    side_view(c, 99, 0.0, sag=sag)
    rich(c, 500, [("5 · ", GREY), ("LE RÉGLAGE", INK)], 72, eo(prog(t, 35.95, 36.35)))
    # machine
    mx = 540
    p = eob(prog(t, 38.0, 38.6)); 
    if p > 0.02:
        w, h = 460 * p, 120 * p
        c.poly([(mx - w / 2, 600 - h / 2), (mx + w / 2, 600 - h / 2), (mx + w / 2, 600 + h / 2), (mx - w / 2, 600 + h / 2)], fill=(255, 255, 255), outline=INK, w=8)
        if p > 0.9:
            label(c, mx, 618, "BOURREUSE", 40, GREY, 1.0, FM)
        d = eio(prog(t, 39.0, 39.5)) * (1 - eio(prog(t, 40.3, 40.7)))
        for ax in (mx - 80, mx + 80):
            ya = 660; yb = 660 + 200 * d
            if d > 0.01:
                c.rline([(ax - 30 * (1 if ax > mx else -1) * 0, ya), (ax, yb)], 14, INK)
        if d > 0.5:
            arrow(c, (mx - 150, 940), (mx - 90, 940), 8, RED); arrow(c, (mx + 150, 940), (mx + 90, 940), 8, RED)
    if t > 40.9:
        checkmark(c, 860, 660, eob(prog(t, 40.9, 41.2)) * 1.4)
    if t > 39.4: label(c, 540, 1235, "ELLE TASSE LES PIERRES", 56, RED, eo(prog(t, 39.4, 39.8)))

def sc_five(c, t):    # 41.79 - 43.4
    rich(c, 560, [("5 RÔLES", RED)], 120, eo(prog(t, 41.8, 42.1)))
    names = ["CHALEUR", "POIDS", "EAU", "VIBRATIONS", "RÉGLAGE"]
    for k, nme in enumerate(names):
        x = 190 + 175 * k; t0 = 41.85 + k * 0.17
        p = eob(prog(t, t0, t0 + 0.3))
        if p > 0.02:
            c.circle((x, 800), 62 * p, fill=STF, outline=INK, w=7)
            checkmark(c, x, 800, 1.0 * p)
            label(c, x, 940, nme, 34, GREY, 1.0, FM)
    if t > 42.5: label(c, 540, 1100, "POUR DE SIMPLES CAILLOUX", 62, INK, eo(prog(t, 42.5, 42.9)))

def sc_end(c, t):     # 43.4 - 47.9  retour au rail droit
    a0 = eo(prog(t, 43.5, 44.0))
    top_view(c, t, A=0.0, stones=1.0, rails=1.0, sleep=9)
    rich(c, 520, [("CET ÉTÉ, PENSE ", INK), ("À EUX", RED)], 70, a0)
    sun(c, 860, 650, eo(prog(t, 43.6, 44.0)), 40)
    if t > 45.0: checkmark(c, 190, 650, eob(prog(t, 45.0, 45.3)) * 1.4)

def sc_next(c, t):    # 47.9 - 53.4
    a = eo(prog(t, 47.95, 48.4))
    label(c, 540, 540, "PROCHAIN OBJET", 66, GREY, a)
    p = prog(t, 48.4, 49.4)
    pen_poly(c, circ_pts(CX, 780, 150, 80, -math.pi / 2, -math.pi / 2 + 2 * math.pi), p, 9, INK)
    pen_poly(c, circ_pts(CX, 780, 112, 80, -math.pi / 2, -math.pi / 2 + 2 * math.pi), prog(t, 48.9, 49.6), 6, INK)
    if t > 49.4:
        label(c, CX, 1040, "LES HUBLOTS D'AVION", 66, INK, eo(prog(t, 49.4, 49.8)))
        c.text((CX + 190, 650), "?", FA, int(160 * max(0.02, eob(prog(t, 49.6, 49.95)))), RED, anchor="ms")
    # bouton abonne-toi
    if t > 50.0:
        pp = eob(prog(t, 50.0, 50.35)); clicked = t >= 50.5
        pulse = 1.0
        if clicked: pulse = 1 + 0.08 * math.exp(-(t - 50.5) * 9) * math.cos((t - 50.5) * 25)
        if 50.5 <= t < 50.62: pulse = 0.93
        w, h = (500 if not clicked else 400) * pp * pulse, 84 * pp * pulse
        if w > 4:
            c.d.rounded_rectangle([(CX - w / 2) * S, (1150 - h / 2) * S, (CX + w / 2) * S, (1150 + h / 2) * S], radius=h / 2 * S, fill=INK if clicked else RED)
            if pp > 0.6: c.text((CX, 1164), "ABONNÉ  ✓" if clicked else "@ingenieur.malin", FM, 38, (255, 255, 255), anchor="ms")

BEATS = [(0, 5.0, sc_hook), (5.0, 7.44, sc_q), (7.44, 13.84, sc_heat), (13.84, 18.44, sc_lock), (18.44, 21.6, sc_sharp), (21.6, 25.65, sc_round),
         (25.65, 30.38, sc_weight), (30.38, 32.6, sc_water), (32.6, 35.9, sc_vib), (35.9, 41.79, sc_tamp), (41.79, 43.4, sc_five), (43.4, 47.9, sc_end), (47.9, 99, sc_next)]
def beat_of(t):
    for i, (a, b, f) in enumerate(BEATS):
        if a <= t < b: return i
    return len(BEATS) - 1

# ----- caméra -----
KEYS = [(0, 1.0, 540, 960), (1.5, 1.12, 540, 880), (3.5, 1.10, 540, 900), (5.0, 1.0, 540, 940), (6.43, 1.1, 540, 800), (7.44, 1.0, 540, 900),
        (11.9, 1.14, 540, 860), (13.8, 1.0, 540, 900), (15.0, 1.12, 540, 880), (18.4, 1.0, 540, 900), (19.6, 1.12, 540, 860), (21.6, 1.0, 540, 900),
        (23.2, 1.1, 540, 880), (25.6, 1.0, 540, 900), (26.6, 1.12, 540, 760), (28.2, 1.08, 540, 900), (30.4, 1.0, 540, 900), (32.6, 1.05, 400, 880),
        (35.9, 1.0, 540, 900), (38.6, 1.1, 540, 820), (41.0, 1.0, 540, 900), (41.8, 1.08, 540, 780), (43.4, 1.0, 540, 900), (47.9, 1.0, 540, 900), (50.4, 1.0, 540, 940), (53.4, 1.0, 540, 940)]
PUNCH = [(5.0, 0.04), (6.43, 0.06), (7.44, 0.04), (13.84, 0.04), (19.5, 0.06), (25.7, 0.04), (30.4, 0.04), (32.65, 0.04), (35.95, 0.04), (41.8, 0.06), (50.5, 0.05)]
def cam(t):
    z = fx = fy = None
    for i in range(len(KEYS) - 1):
        a, b = KEYS[i], KEYS[i + 1]
        if a[0] <= t <= b[0]:
            u = eio(prog(t, a[0], b[0]))
            z = a[1] + (b[1] - a[1]) * u; fx = a[2] + (b[2] - a[2]) * u; fy = a[3] + (b[3] - a[3]) * u
    if z is None: z, fx, fy = KEYS[-1][1:]
    for tp, amp in PUNCH:
        if t >= tp: z *= 1 + amp * math.exp(-(t - tp) * 9)
    return z, fx, fy

# ----- overlays -----
def header(c, t):
    Y = 330
    c.text((80, Y), "ÉPISODE 1", FM, 34, RED)
    c.text((80 + tw("ÉPISODE 1  ", FM, 34), Y), "· BALLAST", FM, 34, GREY)
    c.line([(80, Y + 38), (1000, Y + 38)], 4, GM)
    c.line([(80, Y + 38), (80 + 920 * min(1, t / (DUR - 0.5)), Y + 38)], 8, RED)

ROLE_T = [7.44, 25.65, 30.38, 32.6, 35.9]
def roles(c, t):
    if t < 6.6: return
    a = eo(prog(t, 6.6, 7.0)) * (1 - eo(prog(t, 43.2, 43.5)))
    if a <= 0.02: return
    for k in range(5):
        x = 790 + 52 * k; y = 330
        done = t >= ROLE_T[k]
        c.circle((x, y - 12), 19, fill=mix(BG, RED, a) if done else None, outline=mix(BG, INK, a), w=5)
        if done: c.text((x, y - 3), str(k + 1), FM, 24, (255, 255, 255), anchor="ms")

CAP_Y = 1400
def caption(c, t):
    idx = None
    for i, (a, b) in enumerate(CHUNKS):
        start = WORDS[a][1]
        nxt = WORDS[CHUNKS[i + 1][0]][1] if i + 1 < len(CHUNKS) else 99
        end = min(WORDS[b][2] + 0.3, nxt)
        if start - 0.02 <= t < end: idx = i
    if idx is None: return
    a, b = CHUNKS[idx]; ws = WORDS[a:b + 1]
    size, lh, maxw = 98, 110, 960
    sp = tw(" ", FA, size)
    lines, cur, curw = [], [], 0
    for k, (w, s0, s1) in enumerate(ws):
        ww = tw(w, FA, size)
        if cur and curw + sp + ww > maxw: lines.append((cur, curw)); cur, curw = [], 0
        curw += (sp if cur else 0) + ww; cur.append((w, s0, s1, ww))
    lines.append((cur, curw))
    cy = CAP_Y - (len(lines) - 1) * lh / 2
    for ln, lw in lines:
        x = 540 - lw / 2
        for w, s0, s1, ww in ln:
            if t >= s0 - 0.01:
                p = prog(t, s0, s0 + 0.10); off = (1 - eo(p)) * 18
                now = s0 <= t < s1 + 0.04
                col = RED if (now or w in EMPH) else INK
                sz = int(size * (1 + 0.08 * (1 - prog(t, s0, s0 + 0.18)))) if now else size
                c.text((x + ww / 2, cy + off), w, FA, sz, mix(BG, col, eo(p)), anchor="ms")
            x += ww + sp
        cy += lh

def frame(i):
    t = i / FPS
    im = GRID.crop((0, 0, W * S, H * S))
    c = C(im)
    BEATS[beat_of(t)][2](c, t)
    draw_cursor(c, t)
    z, fx, fy = cam(t)
    bw, bh = W / z, H / z
    x0 = max(0, min(W - bw, fx - bw / 2)); y0 = max(0, min(H - bh, fy - bh / 2))
    im2 = im.crop((int(x0 * S), int(y0 * S), int((x0 + bw) * S), int((y0 + bh) * S))).resize((W * S, H * S), Image.LANCZOS)
    c2 = C(im2)
    header(c2, t); roles(c2, t); caption(c2, t)
    return im2.resize((W, H), Image.LANCZOS)

if __name__ == "__main__":
    for t in [float(x) for x in sys.argv[2:]]:
        frame(int(round(t * FPS))).save(f"/tmp/claude-0/work/ballast/v/t_{t:05.2f}.png")
