# ================= LA TOUR DE REFROIDISSEMENT (épisode 15 · forme contre-intuitive) =================
# Exécuté après render/engine/head.py. Tous les instants viennent de words.json.
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

def zig(x, y0, y1, n=6, amp=14):
    pts = [(x, y0)]
    for k in range(n): pts.append((x + (amp if k % 2 == 0 else -amp), y0 + (y1 - y0) * (k + 0.5) / n))
    pts.append((x, y1)); return pts

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

T_Une = wt("une"); T_Cyl = wt("un"); T_Non = wt("eh"); T_P1 = wt("première"); T_P2 = wt("deuxième"); T_P3 = wt("troisième")
T_Ab = wt("absurde", 1); T_N = wt("abonnetoi"); T_CK = we("abonnetoi") + 0.1
BEATS = [0.0, T_Une, T_Cyl, T_Non, T_P1, T_P2, T_P3, T_Ab, T_N, 999.0]
EMPH = {nrm(x) for x in ["absurde.", "absurde", "pincée", "milieu.", "cylindre", "hyperboloïde,", "dix-huit,", "droites,", "col", "étroit", "vingtaine", "centimètres",
                          "papier.", "coque,", "solide.", "secret", "objet.", "six"]}

def half_w(k, R=1.0):
    # demi-largeur relative (k = 0 haut, 1 bas), col à 0,62
    return R * (150 + 105 * ((0.62 - k) / 0.62) ** 2) if k < 0.62 else R * (150 + 90 * ((k - 0.62) / 0.38) ** 2)

def tower(c, cx, top, bot, a=1.0, fill=(236, 236, 232), R=1.0, w=9, throat=0.0, ghost=False):
    N = 40
    L = [(cx - half_w(k / N, R), top + (bot - top) * k / N) for k in range(N + 1)]
    Rr = [(cx + half_w(k / N, R), top + (bot - top) * k / N) for k in range(N + 1)]
    c.poly(L + Rr[::-1], fill=mix(BG, fill, a), outline=mix(BG, INK, a), w=w)
    gy = top + (bot - top) * 0.62
    if throat > 0: pen_poly(c, [(cx - half_w(0.62, R), gy), (cx + half_w(0.62, R), gy)], throat, 9, RED)
    return gy

def sc_hook(c, t):
    rich(c, 520, [("CETTE FORME", INK)], 92, eo(prog(t, 0.05, 0.5)))
    rich(c, 650, [("A L'AIR ABSURDE", RED)], 92, eo(prog(t, 0.3, 0.8)))
    tower(c, CX, 760, 1300, eo(prog(t, 0.5, 1.0)), R=0.9)
    label(c, CX, 1340, "LA TOUR D'UNE CENTRALE", 36, INK, eo(prog(t, 1.2, 1.7)), FM)

def sc_pinch(c, t):
    p = eo(prog(t, T_Une + 0.2, T_Une + 0.9))
    gy = tower(c, CX, 760, 1300, 1.0, R=0.9, throat=prog(t, wt("pincée") - 0.2, wt("pincée") + 0.4))
    a = eo(prog(t, wt("milieu") - 0.3, wt("milieu") + 0.1))
    if a > 0:
        arrow(c, (CX - 330, gy), (CX - 250, gy), 10, mix(BG, RED, a), 24); arrow(c, (CX + 330, gy), (CX + 250, gy), 10, mix(BG, RED, a), 24)
    rich(c, 520, [("PINCÉE ", RED), ("AU MILIEU", INK)], 80, eo(prog(t, T_Une, T_Une + 0.4)))

def sc_cyl(c, t):
    a = eo(prog(t, T_Cyl, T_Cyl + 0.5))
    dashed(c, [(CX - 150, 760), (CX - 150, 1300), (CX + 150, 1300), (CX + 150, 760)], 22, 14, 6, mix(BG, GM, 0.9 * a), closed=True)
    tower(c, CX, 760, 1300, 1.0, R=0.9)
    rich(c, 520, [("UN ", INK), ("CYLINDRE ", RED), ("?", INK)], 80, eo(prog(t, T_Cyl, T_Cyl + 0.4)))
    label(c, CX, 1340, "PLUS SIMPLE À BÂTIR ?", 40, INK, eo(prog(t, wt("facile") - 0.2, wt("facile") + 0.2)), FM)

def sc_non(c, t):
    tower(c, CX, 820, 1300, 1.0, R=0.8, throat=prog(t, T_Non + 0.2, T_Non + 0.8))
    rich(c, 520, [("EH BIEN ", INK), ("NON", RED)], 90, eo(prog(t, T_Non, T_Non + 0.4)))
    label(c, CX, 690, "HYPERBOLOÏDE", 54, RED, eo(prog(t, wt("hyperboloïde") - 0.4, wt("hyperboloïde") - 0.05)))
    label(c, CX, 770, "BREVETÉE EN 1918 · PAYS-BAS", 36, INK, eo(prog(t, wt("brevetée") - 0.1, wt("brevetée") + 0.3)), FM)

def sc_lines(c, t):
    p = prog(t, wt("lignes") - 0.2, wt("lignes") + 1.6)
    tower(c, CX, 780, 1300, 1.0, R=0.9, fill=(246, 246, 243))
    n = 16
    for k in range(int(n * p + 0.999)):
        ph = 2 * math.pi * k / n
        x0 = CX + 140 * math.cos(ph); x1 = CX + 140 * math.cos(ph + 1.5)
        c.line([(x0, 780), (x1, 1300)], 4, mix(BG, RED, 0.9))
    rich(c, 520, [("DES LIGNES ", INK), ("DROITES", RED)], 80, eo(prog(t, wt("première") + 0.4, wt("première") + 0.9)))
    label(c, CX, 1340, "ÇA SIMPLIFIE LA CONSTRUCTION", 36, INK, eo(prog(t, wt("simplifie") - 0.1, wt("simplifie") + 0.3)), FM)

def sc_air(c, t):
    gy = tower(c, CX, 780, 1300, 1.0, R=0.9, throat=prog(t, wt("col") - 0.1, wt("col") + 0.4))
    ar = eo(prog(t, wt("accélère") - 0.1, wt("accélère") + 0.7))
    for dx, ln in ((-60, 40), (0, 56), (60, 40)):
        arrow(c, (CX + dx, gy + 70), (CX + dx, gy + 70 - ln - 70 * ar), 9, RED, 22)
    for dx in (-190, -100, 100, 190):
        arrow(c, (CX + dx, 1260), (CX + dx, 1260 - 40 - 20 * ar), 7, mix(BG, GM, 0.9), 18)
    rich(c, 520, [("LE COL ", RED), ("ÉTROIT", INK)], 80, eo(prog(t, T_P2, T_P2 + 0.4)))
    label(c, CX, 720, "L'AIR CHAUD ACCÉLÈRE", 40, INK, eo(prog(t, wt("accélère") - 0.1, wt("accélère") + 0.3)), FM)
    label(c, CX, 1340, "BASE LARGE : L'EAU SE REFROIDIT", 36, INK, eo(prog(t, wt("base") - 0.1, wt("base") + 0.3)), FM)

def sc_wall(c, t):
    # paroi d'environ 20 cm sur plus de 100 m ; à l'échelle d'une feuille A4 debout : environ six feuilles de papier
    tower(c, 300, 760, 1240, 1.0, R=0.42, w=7, throat=prog(t, wt("paroi") - 0.2, wt("paroi") + 0.3))
    rich(c, 520, [("PAROI : ", INK), ("ENV. 20 CM", RED)], 80, eo(prog(t, T_P3, T_P3 + 0.4)))
    label(c, 300, 1290, "PLUS DE 100 M", 36, INK, eo(prog(t, wt("cent") - 0.1, wt("cent") + 0.3)), FM)
    label(c, 300, 1332, "DE HAUT", 36, INK, eo(prog(t, wt("cent") - 0.1, wt("cent") + 0.3)), FM)
    a = eo(prog(t, wt("a4") - 0.3, wt("a4") + 0.2))
    if a > 0:
        box(c, 700, 790, 842, 1000, fill=(250, 250, 247), w=6, a=a, r=2)
        label(c, 771, 910, "A4", 54, INK, a)
        label(c, 771, 1050, "30 CM DE HAUT", 28, INK, a, FM)
    s = prog(t, wt("six") - 0.1, wt("six") + 0.8)
    for k in range(int(6 * s + 0.999)):
        c.line([(700 - 40, 1100 + k * 14), (700 - 40 + 130, 1100 + k * 14)], 6, INK)
    label(c, 771 + 20, 1260, "ENV. 6 FEUILLES", 44, RED, eo(prog(t, wt("six") + 0.2, wt("six") + 0.6)))

def sc_recap(c, t):
    t0 = T_Ab
    tower(c, CX, 840, 1260, 1.0, R=0.7, w=8)
    checkmark(c, 850, 700, eob(prog(t, t0, t0 + 0.4)) * 1.4)
    rich(c, 520, [("PAS ABSURDE :", INK)], 84, eo(prog(t, t0 - 0.2, t0 + 0.3)))
    rich(c, 1330, [("UNE COQUE FINE ET SOLIDE", RED)], 52, eo(prog(t, wt("coque") - 0.1, wt("coque") + 0.3)))

def sc_next(c, t):
    t0 = T_N
    tower(c, CX, 600, 880, eo(prog(t, t0 - 0.1, t0 + 0.4)), R=0.55, w=7)
    last = lambda w: WORDS[max(i for i, x in enumerate(NW) if x == nrm(w))][1]
    ts, td = last("secret"), last("dans")
    label(c, CX, 990, "UN SECRET D'INGÉNIEUR", 58, INK, eo(prog(t, ts - 0.1, ts + 0.3)))
    label(c, CX, 1085, "DANS CHAQUE OBJET", 58, RED, eo(prog(t, td - 0.1, td + 0.3)))
    subscribe_button(c, t, t0, T_CK)

SCENES = [sc_hook, sc_pinch, sc_cyl, sc_non, sc_lines, sc_air, sc_wall, sc_recap, sc_next]
beat_of = beat_of_f(BEATS, SCENES)
CUR = [(0.0, 540, 1300), (T_Une, 700, 1000), (T_Cyl, 640, 1000), (T_Non, 540, 1000), (T_P1, 440, 1000), (T_P2, 540, 1000), (T_P3, 300, 1000),
       (T_Ab, 700, 900), (T_N - 0.2, 700, 900), (T_CK - 0.25, 540, 1205), (DUR, 540, 1205)]
CLICKS = [T_Ab, T_CK]
draw_cursor = cursor_factory(CUR, CLICKS)
caption = caption_factory(EMPH)

def cam(t):
    b = beat_of(t); a0, a1 = BEATS[b], min(BEATS[b + 1], DUR)
    z = 1.0 + 0.04 * eio(prog(t, a0, a1)) * (b not in (0, len(BEATS) - 2))
    for tp in BEATS[1:-1]:
        if t >= tp: z *= 1 + 0.03 * math.exp(-(t - tp) * 9)
    return z, 540, 910

def header(c, t):
    Y = 330
    c.text((80, Y), "ÉPISODE 15", FM, 34, RED)
    c.text((80 + tw("ÉPISODE 15  ", FM, 34), Y), "· FORME CONTRE-INTUITIVE", FM, 34, GREY)
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
