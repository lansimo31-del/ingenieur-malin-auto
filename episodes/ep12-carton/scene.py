# ================= LE CARTON ONDULÉ (épisode 12 · forme contre-intuitive) =================
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

T_L = wt("dans"); T_Q = wt("pourquoi"); T_P = wt("parce"); T_AV = wt("avec"); T_E = wt("écartent"); T_A = wt("chaque")
T_H = wt("tout", 1); T_V = wt("vers"); T_R = wt("absurde", 1); T_N = wt("abonnetoi"); T_CK = we("abonnetoi") + 0.1
BEATS = [0.0, T_L, T_Q, T_P, T_AV, T_E, T_A, T_H, T_R, T_N, 999.0]
EMPH = {nrm(x) for x in ["absurde.", "absurde", "vagues.", "vagues,", "plat", "plie", "doigt.", "tient,", "poids", "égal.", "écartent", "loin", "centre.", "arche,", "charge.",
                          "chapeaux.", "vide,", "placé.", "secret", "objet.", "rigidité", "plates."]}

def wave_pts(cx, cy, w, n=7, amp=46, k0=0, k1=1.0):
    return [(cx - w / 2 + w * (k / 140) * 1.0, cy + amp * math.sin((k / 140) * n * 2 * math.pi)) for k in range(int(140 * k0), int(140 * k1) + 1)]

def sandwich(c, cx, cy, w, a=1.0, wave_col=None, hot=0, n=7, thick=1.0):
    amp = 46 * w / 720
    c.poly([(cx - w / 2, cy - 74 * thick * w / 720 * 1.0 - 20), (cx + w / 2, cy - 74 * thick * w / 720 - 20), (cx + w / 2, cy - 74 * thick * w / 720), (cx - w / 2, cy - 74 * thick * w / 720)], fill=mix(BG, (236, 214, 150), a), outline=mix(BG, INK, a), w=7)
    c.poly([(cx - w / 2, cy + 74 * thick * w / 720), (cx + w / 2, cy + 74 * thick * w / 720), (cx + w / 2, cy + 74 * thick * w / 720 + 20), (cx - w / 2, cy + 74 * thick * w / 720 + 20)], fill=mix(BG, (236, 214, 150), a), outline=mix(BG, INK, a), w=7)
    pts = [(cx - w / 2 + w * (k / 140), cy + amp * math.sin((k / 140) * n * 2 * math.pi)) for k in range(141)]
    c.line(pts, 8, mix(BG, INK, a))
    if hot:
        per = 140 / n
        for h in range(min(hot, n)):
            seg = [pts[k] for k in range(int(h * per + per / 2 * 0.0), int(h * per + per / 2) + 1)]
            # une arche = la moitié haute de l'ondulation (sinus négatif = vers le haut de l'écran)
            lo = int(h * per + per / 2); hi = int((h + 1) * per)
            c.line([pts[k] for k in range(lo, hi + 1)], 11, mix(BG, RED, a))

def sheet(c, cx, cy, w, sag, col=None, a=1.0, thick=10):
    pts = [(cx - w / 2 + w * k / 60, cy + sag * math.sin(math.pi * k / 60)) for k in range(61)]
    c.line(pts, thick, mix(BG, col or INK, a))
    for sx in (cx - w / 2, cx + w / 2):
        c.poly([(sx, cy + 8), (sx - 26, cy + 70), (sx + 26, cy + 70)], fill=mix(BG, (205, 205, 200), a), outline=mix(BG, INK, a), w=6)

def push_arrow(c, x, y, a=1.0):
    arrow(c, (x, y - 150), (x, y - 14), 10, mix(BG, RED, a), 28)

def hat(c, cx, cy, a=1.0):
    c.poly([(cx - 70, cy - 120), (cx + 70, cy - 120), (cx + 70, cy), (cx - 70, cy)], fill=mix(BG, (214, 214, 210), a), outline=mix(BG, INK, a), w=8)
    c.poly([(cx - 130, cy), (cx + 130, cy), (cx + 130, cy + 24), (cx - 130, cy + 24)], fill=mix(BG, (214, 214, 210), a), outline=mix(BG, INK, a), w=8)
    c.line([(cx - 70, cy - 28), (cx + 70, cy - 28)], 9, mix(BG, RED, a))

def sc_hook(c, t):
    rich(c, 520, [("CETTE FORME", INK)], 92, eo(prog(t, 0.05, 0.5)))
    rich(c, 650, [("A L'AIR ABSURDE", RED)], 92, eo(prog(t, 0.3, 0.8)))
    sandwich(c, CX, 1030, 760, eo(prog(t, 0.5, 1.0)))
    label(c, CX, 1390, "LE CARTON ONDULÉ", 40, INK, eo(prog(t, 1.0, 1.5)), FM)

def sc_look(c, t):
    sandwich(c, CX, 960, 800)
    rich(c, 520, [("UNE FEUILLE ", INK), ("EN VAGUES", RED)], 76, eo(prog(t, T_L, T_L + 0.4)))
    label(c, CX, 1190, "ENTRE DEUX FEUILLES PLATES", 44, INK, eo(prog(t, wt("entre") - 0.1, wt("entre") + 0.3)), FM)

def sc_why(c, t):
    sandwich(c, CX, 960, 800)
    rich(c, 520, [("POURQUOI PAS ", INK), ("TOUT PLAT ?", RED)], 76, eo(prog(t, T_Q, T_Q + 0.4)))
    label(c, CX, 1190, "?", 220, GF, eo(prog(t, T_Q + 0.2, T_Q + 0.7)))

def sc_flat(c, t):
    p = eo(prog(t, wt("plie") - 0.3, wt("plie") + 0.6))
    sheet(c, CX, 900, 760, 120 * p)
    push_arrow(c, CX, 900 + 120 * p - 20 + 6, eo(prog(t, T_P + 0.1, T_P + 0.5)))
    rich(c, 520, [("UNE FEUILLE ", INK), ("PLATE", RED)], 76, eo(prog(t, T_P, T_P + 0.4)))
    label(c, CX, 1250, "ELLE PLIE SOUS LE DOIGT", 48, INK, eo(prog(t, wt("plie") - 0.1, wt("plie") + 0.3)))

def sc_strong(c, t):
    p = eo(prog(t, T_AV, T_AV + 0.6))
    sandwich(c, CX, 1000, 760, eo(prog(t, T_AV, T_AV + 0.5)))
    for sx in (CX - 380, CX + 380):
        c.poly([(sx, 1000 + 74 + 20), (sx - 26, 1000 + 74 + 20 + 62), (sx + 26, 1000 + 74 + 20 + 62)], fill=(205, 205, 200), outline=INK, w=6)
    push_arrow(c, CX, 1000 - 74 - 20 + 6, eo(prog(t, T_AV + 0.2, T_AV + 0.6)))
    rich(c, 520, [("LE CARTON ", INK), ("TIENT", RED)], 80, eo(prog(t, T_AV, T_AV + 0.4)))
    if t > wt("poids"): label(c, CX, 1280, "À POIDS ÉGAL", 52, RED, eo(prog(t, wt("poids"), wt("poids") + 0.3)))

def sc_spacer(c, t):
    ar = eo(prog(t, T_E + 0.1, T_E + 0.8))
    sandwich(c, CX, 960, 700)
    arrow(c, (CX - 200, 960 - 100), (CX - 200, 960 - 100 - 90 * ar), 9, RED, 24)
    arrow(c, (CX - 200, 960 + 100), (CX - 200, 960 + 100 + 90 * ar), 9, RED, 24)
    arrow(c, (CX + 200, 960 - 100), (CX + 200, 960 - 100 - 90 * ar), 9, RED, 24)
    arrow(c, (CX + 200, 960 + 100), (CX + 200, 960 + 100 + 90 * ar), 9, RED, 24)
    c.line([(150, 960), (930, 960)], 3, mix(BG, GM, eo(prog(t, wt("centre") - 0.6, wt("centre") - 0.2))))
    rich(c, 520, [("LES VAGUES ", INK), ("ÉCARTENT", RED)], 76, eo(prog(t, T_E, T_E + 0.4)))
    if t > wt("loin"): label(c, CX, 1240, "LA MATIÈRE EST LOIN DU CENTRE", 44, INK, eo(prog(t, wt("loin"), wt("loin") + 0.3)), FM)

def sc_arch(c, t):
    hot = int(prog(t, T_A, T_A + 1.8) * 7.5)
    sandwich(c, CX, 960, 760, hot=hot)
    push_arrow(c, CX, 960 - 74 - 20, eo(prog(t, wt("porte") - 0.2, wt("porte") + 0.3)))
    rich(c, 520, [("CHAQUE VAGUE : ", INK), ("UNE ARCHE", RED)], 70, eo(prog(t, T_A, T_A + 0.4)))
    if t > wt("charge"): label(c, CX, 1250, "ELLE PORTE LA CHARGE", 48, INK, eo(prog(t, wt("charge"), wt("charge") + 0.3)))

def sc_hist(c, t):
    a1 = eo(prog(t, T_H, T_H + 0.4)); a2 = eo(prog(t, T_V, T_V + 0.4))
    hat(c, 300, 900, a1)
    label(c, 300, 1110, "1856", 52, RED, a1)
    label(c, 300, 1165, "DU PAPIER PLISSÉ", 32, INK, a1, FM)
    label(c, 300, 1205, "POUR RAIDIR DES CHAPEAUX", 28, INK, a1, FM)
    sandwich(c, 780, 920, 400, a2, n=5)
    label(c, 780, 1110, "VERS 1874", 52, RED, a2)
    label(c, 780, 1165, "UNE FEUILLE PLATE", 32, INK, a2, FM)
    label(c, 780, 1205, "COLLÉE DESSUS", 28, INK, a2, FM)
    rich(c, 520, [("L'IDÉE VIENT ", INK), ("DE LOIN", RED)], 72, eo(prog(t, T_H, T_H + 0.4)))

def sc_recap(c, t):
    t0 = T_R
    sandwich(c, CX, 960, 700)
    checkmark(c, 850, 700, eob(prog(t, t0, t0 + 0.4)) * 1.4)
    rich(c, 520, [("PAS ABSURDE :", INK)], 84, eo(prog(t, t0 - 0.2, t0 + 0.3)))
    rich(c, 1250, [("DU VIDE, BIEN PLACÉ", RED)], 58, eo(prog(t, wt("vide") - 0.1, wt("vide") + 0.3)))

def sc_next(c, t):
    t0 = T_N
    sandwich(c, CX, 735, 420, eo(prog(t, t0 - 0.1, t0 + 0.4)), n=5)
    last = lambda w: WORDS[max(i for i, x in enumerate(NW) if x == nrm(w))][1]
    ts, td = last("secret"), last("dans")
    label(c, CX, 990, "UN SECRET D'INGÉNIEUR", 58, INK, eo(prog(t, ts - 0.1, ts + 0.3)))
    label(c, CX, 1085, "DANS CHAQUE OBJET", 58, RED, eo(prog(t, td - 0.1, td + 0.3)))
    subscribe_button(c, t, t0, T_CK)

SCENES = [sc_hook, sc_look, sc_why, sc_flat, sc_strong, sc_spacer, sc_arch, sc_hist, sc_recap, sc_next]
beat_of = beat_of_f(BEATS, SCENES)
CUR = [(0.0, 540, 1300), (1.2, 760, 1100), (T_L, 700, 960), (T_Q, 600, 1000), (T_P, CX, 800), (T_AV, CX, 960), (T_E, 340, 960), (T_A, 540, 880), (T_H, 300, 1000),
       (T_R, 700, 900), (T_N - 0.2, 700, 900), (T_CK - 0.25, 540, 1205), (DUR, 540, 1205)]
CLICKS = [T_R, T_CK]
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
    c.text((80, Y), "ÉPISODE 12", FM, 34, RED)
    c.text((80 + tw("ÉPISODE 12  ", FM, 34), Y), "· FORME CONTRE-INTUITIVE", FM, 34, GREY)
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
