# ================= LA POUTRE EN I (épisode 6 · forme contre-intuitive) =================
# Exécuté après render/engine/head.py. Tous les instants viennent de words.json. L'objet n'est nommé qu'à la chute.
import json, os, re
import numpy as _np
CX = 540
STF = (240, 240, 236); LG = (205, 205, 200)
WORDS = json.load(open(os.path.join(os.environ['EP_DIR'], 'words.json')))
for i in range(len(WORDS) - 1):
    WORDS[i][2] = max(WORDS[i][1] + 0.08, min(WORDS[i][2], WORDS[i + 1][1]))
def nrm(w): return re.sub(r"[^a-zàâäçéèêëîïôöùûüÿœ0-9]", "", w.lower())
NW = [nrm(w[0]) for w in WORDS]
def widx(word, nth=0): return [i for i, x in enumerate(NW) if x == nrm(word)][nth]
def wt(word, nth=0): return WORDS[widx(word, nth)][1]
def we(word, nth=0): return WORDS[widx(word, nth)][2]
CHUNKS = []; i = 0
while i < len(WORDS):
    j = i
    while j < len(WORDS) - 1 and j - i < 3 and not re.search(r"[.,?:]$", WORDS[j][0]) and sum(len(WORDS[k][0]) + 1 for k in range(i, j + 2)) <= 22: j += 1
    CHUNKS.append((i, j)); i = j + 1
def label(c, x, y, s, size=64, col=None, a=1.0, font_=None):
    c.text((x, y), s, font_ or FA, size, mix(BG, col or INK, a), anchor="ms")
def rich(c, y, parts, size=76, a=1.0, dy=0):
    tot = sum(tw(t, FA, size) for t, _ in parts); x = CX - tot / 2
    for t, col in parts:
        c.text((x, y + dy), t, FA, size, mix(BG, col, a), anchor="ls"); x += tw(t, FA, size)
def pen_poly(c, pts, p, w, col):
    L = [math.hypot(pts[i + 1][0] - pts[i][0], pts[i + 1][1] - pts[i][1]) for i in range(len(pts) - 1)]
    tgt = sum(L) * cl(p); acc = 0; out = [pts[0]]
    for i, l in enumerate(L):
        if acc + l <= tgt: out.append(pts[i + 1]); acc += l
        else:
            u = (tgt - acc) / l if l else 0
            out.append((pts[i][0] + (pts[i + 1][0] - pts[i][0]) * u, pts[i][1] + (pts[i + 1][1] - pts[i][1]) * u)); break
    if len(out) > 1 and p > 0: c.line(out, w, col)
def arrow(c, a, b, w, col, hs=26):
    c.rline([a, b], w, col)
    ang = math.atan2(b[1] - a[1], b[0] - a[0])
    for s in (-1, 1): c.rline([b, (b[0] - hs * math.cos(ang + s * 0.5), b[1] - hs * math.sin(ang + s * 0.5))], w, col)
def rrect(cx, cy, w, h, r, n=10):
    r = max(1.0, min(r, w / 2 - 0.5, h / 2 - 0.5)); pts = []
    for (ox, oy, a0) in ((w/2 - r, -h/2 + r, -90), (w/2 - r, h/2 - r, 0), (-w/2 + r, h/2 - r, 90), (-w/2 + r, -h/2 + r, 180)):
        for k in range(n + 1):
            a = math.radians(a0 + 90 * k / n); pts.append((cx + ox + r * math.cos(a), cy + oy + r * math.sin(a)))
    return pts
def box(c, x0, y0, x1, y1, fill=None, w=6, col=None, a=1.0, r=4):
    c.poly(rrect((x0 + x1) / 2, (y0 + y1) / 2, x1 - x0, y1 - y0, r), fill=mix(BG, fill, a) if fill else None, outline=mix(BG, col or INK, a), w=w)


def beat_of_f(BEATS, SCENES):
    def f(t):
        for i in range(len(SCENES)):
            if BEATS[i] <= t < BEATS[i + 1]: return i
        return len(SCENES) - 1
    return f

def caption_factory(EMPH):
    def caption(c, t):
        idx = None
        for i, (a, b) in enumerate(CHUNKS):
            nxt = WORDS[CHUNKS[i + 1][0]][1] if i + 1 < len(CHUNKS) else 99
            if WORDS[a][1] - 0.02 <= t < min(WORDS[b][2] + 0.3, nxt): idx = i
        if idx is None: return
        a, b = CHUNKS[idx]; ws = WORDS[a:b + 1]
        size, lh, maxw = 98, 110, 960
        sp = tw(" ", FA, size); lines, cur, curw = [], [], 0
        for (w, s0, s1) in ws:
            ww = tw(w, FA, size)
            if cur and curw + sp + ww > maxw: lines.append((cur, curw)); cur, curw = [], 0
            curw += (sp if cur else 0) + ww; cur.append((w, s0, s1, ww))
        lines.append((cur, curw)); cy = 1470 - (len(lines) - 1) * lh / 2
        for ln, lw in lines:
            x = 540 - lw / 2
            for w, s0, s1, ww in ln:
                if t >= s0 - 0.01:
                    p = prog(t, s0, s0 + 0.10); off = (1 - eo(p)) * 18; now = s0 <= t < s1 + 0.04
                    col = RED if (now or nrm(w) in EMPH) else INK
                    sz = int(size * (1 + 0.08 * (1 - prog(t, s0, s0 + 0.18)))) if now else size
                    c.text((x + ww / 2, cy + off), w, FA, sz, mix(BG, col, eo(p)), anchor="ms")
                x += ww + sp
            cy += lh
    return caption

def cursor_factory(CUR, CLICKS):
    def cursor_pos(t):
        for a, b in zip(CUR[:-1], CUR[1:]):
            if a[0] <= t <= b[0]:
                u = eio(prog(t, a[0], b[0])); return a[1] + (b[1] - a[1]) * u, a[2] + (b[2] - a[2]) * u
        return CUR[-1][1], CUR[-1][2]
    def draw_cursor(c, t):
        x, y = cursor_pos(t)
        for ck in CLICKS:
            u = t - ck
            if 0 <= u < 0.45:
                px, py = cursor_pos(ck); p = eo(u / 0.45); c.circle((px, py), 8 + 40 * p, outline=mix(BG, RED, 1 - p), w=5)
        k = 1.25 * (0.86 if any(0 <= t - ck < 0.12 for ck in CLICKS) else 1.0)
        pts = [(0, 0), (0, 27), (7, 21), (12, 32), (17, 30), (12, 19), (21, 19)]
        c.poly([(x + 4 + px * k, y + 6 + py * k) for px, py in pts], fill=GM)
        c.poly([(x + px * k, y + py * k) for px, py in pts], fill=(255, 255, 255), outline=INK, w=3.2)
    return draw_cursor

def subscribe_button(c, t, t0, t_ck, y=1205):
    tb = t0 + 0.05; clicked = t >= t_ck
    if t > tb:
        pp = eob(prog(t, tb, tb + 0.35)); pulse = 1.0
        if clicked: pulse = 1 + 0.08 * math.exp(-(t - t_ck) * 9) * math.cos((t - t_ck) * 25)
        if t_ck <= t < t_ck + 0.12: pulse = 0.93
        w, h = (500 if not clicked else 400) * pp * pulse, 84 * pp * pulse
        if w > 4:
            c.d.rounded_rectangle([(CX - w / 2) * S, (y - h / 2) * S, (CX + w / 2) * S, (y + h / 2) * S], radius=h / 2 * S, fill=INK if clicked else RED)
            if pp > 0.6: c.text((CX, y + 14), "ABONNÉ  ✓" if clicked else "@ingenieur.malin", FM, 38, (255, 255, 255), anchor="ms")

# ---------- repères de la voix ----------
T_RULE = wt("prends"); T_PLAT = wt("plat"); T_TR = wt("tranche"); T_X = wt("cent")
T_SEC = wt("secret"); T_LOIN = wt("loin"); T_CTR = wt("centre", 1)
T_MOVE = wt("alors"); T_SEM = wt("semelles"); T_AME = wt("âme")
T_ARB = WORDS[widx("poutre", 1) - 1][1]; T_BAR = wt("barre"); T_29 = wt("vingtneuf")
T_PAS = wt("pas"); T_N = wt("abonnetoi"); T_CK = we("abonnetoi") + 0.1
BEATS = [0.0, T_RULE, T_SEC, T_MOVE, T_ARB, T_PAS, T_N, 999.0]
EMPH = {nrm(x) for x in ["absurde.", "règle.", "résiste.", "vingt-cinq", "secret", "loin", "centre.", "rien.", "semelles,", "âme", "mince.",
                          "vingt-neuf", "mieux", "placé.", "secret", "objet.", "Abonne-toi", "rigide.", "rigide,"]}

# I réel : IPE 200 (hauteur 200, largeur 100, semelle 8,5, âme 5,6 mm) à l'échelle k px/mm
def i_poly(cx, cy, k, fy=1.0):
    h, w, tf, tw_ = 200 * k, 100 * k, 8.5 * k, 5.6 * k
    top = cy - h / 2 * fy; bot = cy + h / 2 * fy
    return [(cx - w / 2, top), (cx + w / 2, top), (cx + w / 2, top + tf), (cx + tw_ / 2, top + tf), (cx + tw_ / 2, bot - tf), (cx + w / 2, bot - tf),
            (cx + w / 2, bot), (cx - w / 2, bot), (cx - w / 2, bot - tf), (cx - tw_ / 2, bot - tf), (cx - tw_ / 2, top + tf), (cx - w / 2, top + tf)]

def sc_hook(c, t):
    rich(c, 520, [("CETTE FORME", INK)], 92, eo(prog(t, 0.05, 0.5)))
    rich(c, 640, [("A L'AIR ABSURDE", RED)], 100, eo(prog(t, 0.3, 0.8)))
    a = eo(prog(t, 0.4, 0.9))
    c.poly(i_poly(CX, 1000, 3.0), fill=mix(BG, (222, 222, 218), a), outline=mix(BG, INK, a), w=8)
    if t > wt("enlever"): label(c, CX, 1000 + 14, "?", 150, RED, eob(prog(t, wt("enlever"), wt("enlever") + 0.4)))

def beam(c, x0, x1, y0, h, d, col=INK, a=1.0):
    n = 40; top = []; bot = []
    for k in range(n + 1):
        u = k / n; x = x0 + (x1 - x0) * u; y = y0 + d * 4 * u * (1 - u)
        top.append((x, y)); bot.append((x, y + h))
    c.poly(top + bot[::-1], fill=mix(BG, (205, 205, 200), a), outline=mix(BG, col, a), w=7)

def support(c, x, y):
    c.poly([(x, y), (x - 34, y + 60), (x + 34, y + 60)], fill=mix(BG, (222, 222, 218), 1), outline=mix(BG, INK, 1), w=6)

def sc_rule(c, t):
    t0 = T_RULE
    rich(c, 520, [("PRENDS UNE ", INK), ("RÈGLE", RED)], 80, eo(prog(t, t0, t0 + 0.4)))
    x0, x1, y0 = 170, 910, 960
    edge = t >= T_TR - 0.1
    flat_h, edge_h = 16, 110
    load = eio(prog(t, T_PLAT, T_PLAT + 1.0)) if not edge else eio(prog(t, T_TR, T_TR + 1.0))
    d = (130 if not edge else 7) * load
    h = edge_h if edge else flat_h
    yy = y0 + (flat_h - h) / 2 * 0 - (h - flat_h) * (1 if edge else 0)       # le dessus de la règle reste au même niveau
    support(c, x0, y0 + flat_h - 4); support(c, x1, y0 + flat_h - 4)
    beam(c, x0, x1, yy, h, d, INK, 1.0)
    # poids : flèche verte sur le milieu
    mid_y = yy + d
    arrow(c, (CX, mid_y - 150), (CX, mid_y - 18), 10, mix(BG, RED, 1), 28)
    label(c, CX + 120, mid_y - 100, "POIDS", 44, RED, 1.0, FM)
    lab = "SUR LA TRANCHE" if edge else "À PLAT"
    label(c, CX, 1295, lab, 62, INK, 1.0)
    if edge and t >= T_X:
        label(c, CX, 1165, "×225", 130, RED, eob(prog(t, T_X, T_X + 0.4)))
        label(c, CX, 1215, "RÈGLE DE 30 mm SUR 2 mm", 36, GREY, eo(prog(t, wt("trois"), wt("trois") + 0.4)), FM)

def sc_secret(c, t):
    t0 = T_SEC; cy = 930; hw = 150
    rich(c, 520, [("LE ", INK), ("SECRET", RED)], 84, eo(prog(t, t0, t0 + 0.4)))
    c.poly([(CX - hw, cy - hw), (CX + hw, cy - hw), (CX + hw, cy + hw), (CX - hw, cy + hw)], fill=mix(BG, (222, 222, 218), 1), outline=mix(BG, INK, 1), w=8)
    dashed(c, [(CX - 230, cy), (CX + 230, cy)], 22, 12, 5, mix(BG, GM, 1))
    label(c, CX + 330, cy - 14 + 22, "CENTRE", 36, GREY, eo(prog(t, t0 + 0.3, t0 + 0.7)), FM)
    pa = eo(prog(t, T_LOIN - 0.1, T_LOIN + 0.8))
    for k, dy in enumerate((-135, -90, -45, 45, 90, 135)):
        L = 40 + 150 * abs(dy) / 135
        if pa > 0.02:
            xa = CX - hw - 30
            arrow(c, (xa - L * pa, cy + dy), (xa, cy + dy), 8, mix(BG, RED, 1), 20)
    if t >= T_CTR:
        a = eo(prog(t, T_CTR, T_CTR + 0.5))
        c.poly([(CX - hw + 4, cy - 38), (CX + hw - 4, cy - 38), (CX + hw - 4, cy + 38), (CX - hw + 4, cy + 38)], fill=mix((222, 222, 218), (150, 150, 146), a * 0.7))
        label(c, CX, cy + 12, "PRESQUE RIEN", 32, INK, a)
    if t < T_CTR: label(c, CX, 1262, "LOIN DU CENTRE : ÇA TRAVAILLE", 54, INK, eo(prog(t, T_LOIN, T_LOIN + 0.4)))
    else: label(c, CX, 1262, "AU CENTRE : PRESQUE INUTILE", 54, RED, eo(prog(t, T_CTR, T_CTR + 0.4)))

def sc_move(c, t):
    t0 = T_MOVE; k = 2.2; cy = 930
    rich(c, 520, [("ON DÉPLACE ", INK), ("L'ACIER", RED)], 76, eo(prog(t, t0, t0 + 0.4)))
    u = eob(prog(t, t0 + 0.2, T_SEM + 0.6))
    tf = 8.5 * k; wdt = 100 * k; h = 200 * k * (0.35 + 0.65 * u)
    web = 5.6 * k * 1.0
    top = cy - h / 2; bot = cy + h / 2
    c.poly([(CX - web / 2 - 2, top), (CX + web / 2 + 2, top), (CX + web / 2 + 2, bot), (CX - web / 2 - 2, bot)], fill=mix(BG, (222, 222, 218), 1), outline=mix(BG, INK, 1), w=6)
    c.poly([(CX - wdt / 2, top), (CX + wdt / 2, top), (CX + wdt / 2, top + tf), (CX - wdt / 2, top + tf)], fill=mix(BG, (222, 222, 218), 1), outline=mix(BG, INK, 1), w=6)
    c.poly([(CX - wdt / 2, bot - tf), (CX + wdt / 2, bot - tf), (CX + wdt / 2, bot), (CX - wdt / 2, bot)], fill=mix(BG, (222, 222, 218), 1), outline=mix(BG, INK, 1), w=6)
    if t >= T_SEM:
        a = eo(prog(t, T_SEM, T_SEM + 0.4)); label(c, CX + 330, top + 30, "SEMELLES", 44, RED, a)
        label(c, CX + 330, bot - 6, "SEMELLES", 44, RED, a)
    if t >= T_AME: label(c, CX + 330, cy + 12, "ÂME MINCE", 44, INK, eo(prog(t, T_AME, T_AME + 0.4)))
    label(c, CX, 1295, "DE LA MATIÈRE LOIN DU CENTRE", 48, INK, eo(prog(t, T_SEM, T_SEM + 0.5)))

def sc_compare(c, t):
    t0 = T_ARB; k = 1.9; cy = 930
    rich(c, 520, [("MÊME ", INK), ("SURFACE", RED)], 80, eo(prog(t, t0, t0 + 0.4)))
    side = 53.4 * k; xs = 300; xi = 720
    pa = eob(prog(t, t0 + 0.2, t0 + 0.7))
    c.poly([(xs - side / 2, cy - side / 2), (xs + side / 2, cy - side / 2), (xs + side / 2, cy + side / 2), (xs - side / 2, cy + side / 2)], fill=mix(BG, (222, 222, 218), pa), outline=mix(BG, INK, pa), w=7)
    c.poly(i_poly(xi, cy, k), fill=mix(BG, (222, 222, 218), pa), outline=mix(BG, INK, pa), w=7)
    label(c, xs, 1215, "BARRE PLEINE", 40, GREY, eo(prog(t, T_BAR, T_BAR + 0.4)), FM)
    label(c, xi, 1215, "POUTRE EN I · 20 cm", 40, GREY, eo(prog(t, t0 + 0.4, t0 + 0.8)), FM)
    if t >= T_29: label(c, CX, 1310, "×29", 120, RED, eob(prog(t, T_29, T_29 + 0.4)))
    else: label(c, CX, 1300, "MÊME POIDS", 56, INK, eo(prog(t, t0 + 0.6, t0 + 1.0)))

def sc_end(c, t):
    t0 = T_PAS
    c.poly(i_poly(CX, 900, 2.6), fill=mix(BG, (222, 222, 218), 1), outline=mix(BG, INK, 1), w=7)
    checkmark(c, CX + 250, 700, eob(prog(t, t0 + 0.4, t0 + 0.8)) * 1.4)
    rich(c, 520, [("PAS PLUS D'ACIER", INK)], 70, eo(prog(t, t0, t0 + 0.4)))
    rich(c, 1230, [("DE L'ACIER ", INK), ("MIEUX PLACÉ", RED)], 64, eo(prog(t, wt("juste"), wt("juste") + 0.4)))

def sc_next(c, t):
    t0 = T_N
    c.poly(i_poly(CX, 735, 1.4), fill=mix(BG, (222, 222, 218), eo(prog(t, t0 - 0.1, t0 + 0.4))), outline=mix(BG, INK, eo(prog(t, t0 - 0.1, t0 + 0.4))), w=6)
    last = lambda w: WORDS[max(i for i, x in enumerate(NW) if x == nrm(w))][1]
    ts, td = last("secret"), last("dans")
    label(c, CX, 990, "UN SECRET D'INGÉNIEUR", 58, INK, eo(prog(t, ts - 0.1, ts + 0.3)))
    label(c, CX, 1085, "DANS CHAQUE OBJET", 58, RED, eo(prog(t, td - 0.1, td + 0.3)))
    subscribe_button(c, t, t0, T_CK)

SCENES = [sc_hook, sc_rule, sc_secret, sc_move, sc_compare, sc_end, sc_next]
beat_of = beat_of_f(BEATS, SCENES)
CUR = [(0.0, 540, 1300), (1.2, 700, 800), (T_RULE, 540, 900), (T_PLAT, CX, 800), (T_TR, CX, 760), (T_X, 540, 1000), (T_SEC, 540, 800), (T_LOIN, 300, 930),
       (T_MOVE, 540, 930), (T_SEM, 640, 760), (T_ARB, 540, 930), (T_29, 540, 1200), (T_PAS, 540, 900), (T_N - 0.2, 700, 900), (T_CK - 0.25, 540, 1205), (DUR, 540, 1205)]
CLICKS = [T_TR, T_SEM, T_CK]
draw_cursor = cursor_factory(CUR, CLICKS)
caption = caption_factory(EMPH)

def cam(t):
    b = beat_of(t); a0, a1 = BEATS[b], min(BEATS[b + 1], DUR)
    z = 1.0 + 0.05 * eio(prog(t, a0, a1)) * (b not in (0, 6))
    for tp in BEATS[1:-1]:
        if t >= tp: z *= 1 + 0.04 * math.exp(-(t - tp) * 9)
    return z, 540, 910

def header(c, t):
    Y = 330
    c.text((80, Y), "ÉPISODE 6", FM, 34, RED)
    c.text((80 + tw("ÉPISODE 6  ", FM, 34), Y), "· FORME CONTRE-INTUITIVE", FM, 34, GREY)
    c.line([(80, Y + 38), (1000, Y + 38)], 4, GM)
    c.line([(80, Y + 38), (80 + 920 * min(1, t / (DUR - 0.5)), Y + 38)], 8, RED)

def frame(i):
    t = i / FPS
    im = GRID.crop((0, 0, W * S, H * S)); c = C(im)
    SCENES[beat_of(t)](c, t)
    draw_cursor(c, t)
    z, fx, fy = cam(t); bw, bh = W / z, H / z
    x0 = max(0, min(W - bw, fx - bw / 2)); y0 = max(0, min(H - bh, fy - bh / 2))
    im2 = im.crop((int(x0 * S), int(y0 * S), int((x0 + bw) * S), int((y0 + bh) * S))).resize((W * S, H * S), Image.LANCZOS)
    c2 = C(im2); header(c2, t); caption(c2, t)
    return im2.resize((W, H), Image.LANCZOS)
