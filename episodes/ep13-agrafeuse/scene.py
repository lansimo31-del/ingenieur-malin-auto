# ================= LA SERRURE À GOUPILLES (épisode 4 · devine ce que je construis) =================
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

def next_scene_factory(draw_obj):
    def sc_next(c, t):
        t0 = T_N
        draw_obj(c, t, mini=True)
        last = lambda w: WORDS[max(i for i, x in enumerate(NW) if x == nrm(w))][1]
        ts, td = last("secret"), last("dans")
        label(c, CX, 990, "UN SECRET D'INGÉNIEUR", 58, INK, eo(prog(t, ts - 0.1, ts + 0.3)))
        label(c, CX, 1085, "DANS CHAQUE OBJET", 58, RED, eo(prog(t, td - 0.1, td + 0.3)))
        subscribe_button(c, t, t0, T_CK)
    return sc_next



# ================= L'AGRAFEUSE (épisode 13 · devine ce que je construis) =================
T_C1 = wt("première"); T_V = wt("deuxième"); T_P = wt("troisième"); T_W = wt("enfin"); T_G = wt("deviné")
T_B = wt("appuie"); T_R = wt("agrafeuse"); T_OFF = wt("relève"); T_L = wt("première", 1)
T_N = wt("abonnetoi"); T_CK = we("abonnetoi") + 0.1
BEATS = [0.0, T_C1, T_V, T_P, T_W, T_G, T_B, T_R, T_OFF, T_L, T_N, 999.0]
EMPH = {nrm(x) for x in ["Devine", "construis.", "Réponse", "bande", "ressort", "lame", "plaque", "rainures.", "deviné", "agrafeuse,", "bureau.", "secret", "objet.", "Abonne-toi", "barres", "prises."]}
FX = 650            # abscisse de la barre de tête
GAP = 34
def barx(k, shift=0.0): return FX - GAP * k + shift

KZ = 1.5
def ZX(x): return 540 + (x - 475) * KZ
def ZY(y): return 930 + (y - 960) * KZ
class ZC:
    """Proxy de dessin : agrandit l'objet (centre du dessin -> x 540, y 930)."""
    def __init__(self, c): self.c = c; self.d = c.d
    def _p(self, pts): return [(ZX(x), ZY(y)) for x, y in pts]
    def line(self, pts, w, col): self.c.line(self._p(pts), w * KZ ** 0.7, col)
    def rline(self, pts, w, col): self.c.rline(self._p(pts), w * KZ ** 0.7, col)
    def poly(self, pts, fill=None, outline=None, w=0): self.c.poly(self._p(pts), fill=fill, outline=outline, w=w * KZ ** 0.7)
    def circle(self, c_, r, fill=None, outline=None, w=0): self.c.circle((ZX(c_[0]), ZY(c_[1])), r * KZ, fill=fill, outline=outline, w=w * KZ ** 0.7)
    def text(self, xy, s, path, size, col, anchor="ls"): self.c.text((ZX(xy[0]), ZY(xy[1])), s, path, size, col, anchor)

def obj(c, t, mini=False):
    c = ZC(c)
    on = T_B <= t
    press = 0.0 if mini else (eo(prog(t, T_B + 0.3, T_B + 0.8)) if t < T_OFF else 1.0 - eo(prog(t, T_OFF, T_OFF + 0.5)))
    stapled = (not mini) and t >= T_B + 0.8
    shift = 0.0 if mini else GAP * eo(prog(t, T_OFF + 0.2, T_OFF + 0.9))
    # pièce 1 : la bande de barres
    s1 = 1.0 if mini else eob(prog(t, T_C1 + 0.05, T_C1 + 0.5))
    if s1 > 0.03:
        n = 7 if not mini else 8
        for k in range(n):
            if k == 0 and (on and not mini and shift == 0.0): continue          # la barre de tête est partie dans le papier
            x = barx(k, shift if not mini else 0.0)
            if x > FX + 1: continue
            xx = x if not (k == 0 and False) else x
            box(c, xx - 13, 1000, xx + 13, 1000 + 42 * s1, (200, 204, 212), 5, INK, 1.0, 3)
        c.line([(barx(n - 1) - 20, 1050), (FX + 24, 1050)], 5, mix(BG, INK, s1))
        if (not mini) and s1 > 0.9 and t < T_V:
            label(c, 475, 1110, "BARRES COLLÉES", 30, INK, 1.0, FM)
    # pièce 2 : le ressort (horizontal) derrière la bande
    s2 = 1.0 if mini else eob(prog(t, T_V + 0.05, T_V + 0.5))
    if s2 > 0.03:
        xe = barx(6 if not mini else 7, shift if not mini else 0.0) - 22
        xs = 190
        pts = [(xs, 1020)]
        nz = 9
        for k in range(nz):
            pts.append((xs + (xe - xs) * (k + 0.5) / nz, 1020 + (22 if k % 2 == 0 else -22) * s2))
        pts.append((xe, 1020))
        c.line(pts, 6, mix(BG, INK, s2))
        c.line([(xs, 975), (xs, 1065)], 9, mix(BG, INK, s2))
    # pièce 3 : la lame fine
    s3 = 1.0 if mini else eob(prog(t, T_P + 0.05, T_P + 0.5))
    if s3 > 0.03:
        d = 85 * press
        top = 760 + (1 - s3) * -120 + d
        box(c, FX - 24, top, FX + 24, 995 + d, (130, 130, 138), 6, INK, 1.0, 3)
    # pièce 4 : la plaque à deux rainures
    s4 = 1.0 if mini else eob(prog(t, T_W + 0.05, T_W + 0.5))
    if s4 > 0.03:
        box(c, 560, 1124 + (1 - s4) * 140, 740, 1166 + (1 - s4) * 140, (214, 214, 210), 7, INK, 1.0, 5)
        if s4 > 0.9:
            for gx in (FX - 26, FX + 26):
                c.poly([(gx - 11, 1124), (gx + 11, 1124), (gx, 1146)], fill=INK)
    # les feuilles et l'agrafe
    if (not mini) and t >= T_B - 0.3:
        pa = eo(prog(t, T_B - 0.3, T_B + 0.2))
        box(c, 540, 1092, 760, 1118, (255, 255, 255), 6, INK, pa, 3)
        for yy in (1100, 1108): c.line([(542, yy), (758, yy)], 2, mix(BG, GM, pa))
    if (not mini) and on:
        d = 85 * press if t < T_OFF else 85
        cy_ = 1000 + d
        if not stapled and t < T_OFF:
            c.line([(FX - 24, cy_), (FX + 24, cy_)], 7, INK)
            c.line([(FX - 24, cy_), (FX - 24, cy_ + 35)], 7, INK); c.line([(FX + 24, cy_), (FX + 24, cy_ + 35)], 7, INK)
        else:
            cy_ = 1085
            c.line([(FX - 24, cy_), (FX + 24, cy_)], 8, RED)
            c.line([(FX - 24, cy_), (FX - 24, 1122)], 8, RED); c.line([(FX + 24, cy_), (FX + 24, 1122)], 8, RED)
            c.line([(FX - 24, 1122), (FX - 2, 1122)], 8, RED); c.line([(FX + 24, 1122), (FX + 2, 1122)], 8, RED)

def sc_hook(c, t):
    rich(c, 520, [("DEVINE CE QUE", INK)], 92, eo(prog(t, 0.05, 0.5)))
    rich(c, 660, [("JE CONSTRUIS", RED)], 112, eo(prog(t, 0.3, 0.8)))
    label(c, CX, 1300, "?", 400, GF, eo(prog(t, 0.6, 1.1)))
    label(c, CX, 790, "RÉPONSE À LA FIN", 64, INK, eo(prog(t, T_C1 * 0.4, T_C1 * 0.4 + 0.4)))

def piece(n, txt, t0):
    def f(c, t):
        rich(c, 520, [("PIÈCE " + str(n), RED)], 80, eo(prog(t, t0, t0 + 0.4)))
        obj(c, t)
        label(c, CX, 1318, txt, 52, INK, eo(prog(t, t0 + 0.5, t0 + 0.9)))
    return f
sc_p1 = piece(1, "UNE BANDE DE PETITES BARRES", T_C1)
sc_p2 = piece(2, "UN RESSORT QUI POUSSE LA BANDE", T_V)
sc_p3 = piece(3, "UNE LAME FINE", T_P)
sc_p4 = piece(4, "UNE PLAQUE À DEUX RAINURES", T_W)

def sc_guess(c, t):
    rich(c, 520, [("TU AS ", INK), ("DEVINÉ ?", RED)], 92, eo(prog(t, T_G, T_G + 0.4)))
    obj(c, t)
    label(c, CX, 1318, "?", 150, RED, eo(prog(t, T_G + 0.4, T_G + 0.8)))

def sc_press(c, t):
    rich(c, 520, [("ON APPUIE", RED)], 84, eo(prog(t, T_B, T_B + 0.4)))
    obj(c, t)
    lab = "LA LAME POUSSE LA BARRE À TRAVERS" if t < wt("plaque", 1) else "LA PLAQUE PLIE LES DEUX BOUTS"
    label(c, CX, 1318, lab, 42, INK, eo(prog(t, T_B + 0.4, T_B + 0.8)), FM)

def sc_reveal(c, t):
    t0 = T_R
    obj(c, t)
    box(c, 90, 1250, 990, 1400, (255, 255, 255), 8, RED, eo(prog(t, t0 - 0.2, t0 + 0.2)), 20)
    label(c, CX, 1355, "UNE AGRAFEUSE", 96, RED, eo(prog(t, t0 - 0.1, t0 + 0.3)))

def sc_off(c, t):
    rich(c, 520, [("ON RELÈVE : ", INK), ("LA BANDE AVANCE", RED)], 62, eo(prog(t, T_OFF, T_OFF + 0.4)))
    obj(c, t)
    label(c, CX, 1318, "LE RESSORT PLACE UNE NOUVELLE BARRE", 42, INK, eo(prog(t, T_OFF + 0.4, T_OFF + 0.8)), FM)

def sc_loop(c, t):
    t0 = T_L
    rich(c, 520, [("LA PREMIÈRE PIÈCE", INK)], 70, eo(prog(t, t0, t0 + 0.4)))
    for k in range(6):
        box(c, 215 + k * 100, 840, 285 + k * 100, 1120, (200, 204, 212), 8, INK, 1.0, 8)
    c.line([(200, 1135), (880, 1135)], 9, INK)
    checkmark(c, CX + 330, 760, eob(prog(t, t0 + 0.4, t0 + 0.7)) * 1.3)
    label(c, CX, 1262, "LA BANDE GARDE LES AGRAFES", 52, INK, eo(prog(t, wt("garde"), wt("garde") + 0.4)))

def sc_next(c, t):
    t0 = T_N; a = eo(prog(t, t0 - 0.1, t0 + 0.4))
    for k in range(6):
        box(c, 340 + k * 66, 690, 392 + k * 66, 790, (200, 204, 212), 6, INK, a, 6)
    c.line([(330, 802), (750, 802)], 7, mix(BG, INK, a))
    last = lambda w: WORDS[max(i for i, x in enumerate(NW) if x == nrm(w))][1]
    ts, td = last("secret"), last("dans")
    label(c, CX, 990, "UN SECRET D'INGÉNIEUR", 58, INK, eo(prog(t, ts - 0.1, ts + 0.3)))
    label(c, CX, 1085, "DANS CHAQUE OBJET", 58, RED, eo(prog(t, td - 0.1, td + 0.3)))
    subscribe_button(c, t, t0, T_CK)
SCENES = [sc_hook, sc_p1, sc_p2, sc_p3, sc_p4, sc_guess, sc_press, sc_reveal, sc_off, sc_loop, sc_next]
beat_of = beat_of_f(BEATS, SCENES)
CUR = [(0.0, 540, 1300), (1.2, 700, 800), (T_C1, 500, 1020), (T_V, 300, 1020), (T_P, FX, 860), (T_W, 650, 1150), (T_G, 540, 700), (T_B, FX, 800),
       (T_R, 540, 1300), (T_OFF, 500, 1020), (T_L, 540, 930), (T_N - 0.2, 700, 900), (T_CK - 0.25, 540, 1205), (DUR, 540, 1205)]
CLICKS = [T_C1, T_V, T_P, T_W, T_B, T_OFF, T_CK]
draw_cursor = cursor_factory(CUR, CLICKS)
caption = caption_factory(EMPH)

def cam(t):
    b = beat_of(t); a0, a1 = BEATS[b], min(BEATS[b + 1], DUR)
    z = 1.0 + 0.05 * eio(prog(t, a0, a1)) * (b not in (0, len(BEATS) - 2))
    for tp in BEATS[1:-1]:
        if t >= tp: z *= 1 + 0.04 * math.exp(-(t - tp) * 9)
    return z, 540, 910

def header(c, t):
    Y = 330
    c.text((80, Y), "ÉPISODE 13", FM, 34, RED)
    c.text((80 + tw("ÉPISODE 13  ", FM, 34), Y), "· DEVINE CE QUE JE CONSTRUIS", FM, 34, GREY)
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
