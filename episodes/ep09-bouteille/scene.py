# ================= LE TROU DU PISTOLET À ESSENCE (épisode 5 · c'est fait exprès) =================
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
T_L = wt("regarde"); T_P = wt("parce"); T_H = wt("demisphère"); T_S = wt("sauf"); T_A = wt("alors"); T_AV = wt("début")
T_R = wt("absurde", 1); T_N = wt("abonnetoi"); T_CK = we("abonnetoi") + 0.1
BEATS = [0.0, T_L, T_P, T_H, T_S, T_A, T_AV, T_R, T_N, 999.0]
EMPH = {nrm(x) for x in ["absurde.", "absurde", "pieds", "pétales.", "plat", "pousse.", "gaz", "pression", "demi-sphère.", "rond", "debout.", "debout", "creux", "poussée",
                          "socle", "seconde", "bloc.", "secret", "objet.", "résiste", "cinq"]}
FLOOR = 1210

def pivot_rot(pts, pv, ang):
    ca, sa = math.cos(ang), math.sin(ang)
    return [(pv[0] + (x - pv[0]) * ca - (y - pv[1]) * sa, pv[1] + (x - pv[0]) * sa + (y - pv[1]) * ca) for x, y in pts]

def bottle(c, cx, cy, mode, sc=1.0, rot=0.0, a=1.0, nfeet=3, arrows=0.0):
    # bas d'une bouteille vu de côté (y = cy : début du fond). mode : 'flat' | 'round' | 'feet'
    R = 200 * sc; Hd = 170 * sc; side = 440 * sc
    pv = (cx, cy + Hd)
    n = 40
    if mode == "flat":
        prof = [(cx - R, cy - side), (cx - R, cy + Hd * 0.55), (cx + R, cy + Hd * 0.55), (cx + R, cy - side)]
    else:
        arc = [(cx - R * math.cos(math.pi * k / n), cy + Hd * math.sin(math.pi * k / n)) for k in range(n + 1)]
        prof = [(cx - R, cy - side)] + arc + [(cx + R, cy - side)]
    # remplissage + contour
    fillc = mix(BG, (226, 234, 232), a)
    pts = pivot_rot(prof, pv, rot)
    c.poly(pts, fill=fillc, outline=mix(BG, INK, a), w=8)
    if arrows > 0:
        ar = eo(arrows)
        for (x0, y0, dx, dy) in ((-60, -90, -1, 0), (60, -90, 1, 0), (-110, -150, -1, 0), (110, -150, 1, 0)):
            pass
        cols = [(-0.0, 0.8), (-0.5, 0.6), (0.5, 0.6), (-0.85, 0.2), (0.85, 0.2), (-0.85, -0.5), (0.85, -0.5)]
        for ux, uy in cols:
            if mode == "flat" and uy > 0.5: continue
            bx = cx + ux * R * 0.55; by = cy + uy * Hd * 0.45 - (0 if uy > 0.3 else 60 * (0.5 - uy))
            ex = bx + ux * 90 * ar if abs(ux) > 0.8 else bx + ux * 40 * ar; ey = by + (uy * 90 * ar if uy > 0.3 else 0)
            if abs(ex - bx) + abs(ey - by) > 6: arrow(c, (bx, by), (ex, ey), 7, mix(BG, RED, a), 22)
    if mode == "feet":
        xs = [(-140, 0), (140, 1), (0, 2)][:nfeet] if nfeet < 3 else [(-140, 0), (140, 1), (0, 2)]
        for x, k in xs:
            dome = Hd * math.sqrt(max(0.0, 1 - (x / R) ** 2))
            top = cy + dome - 14 * sc; bot = cy + Hd + 60 * sc
            leg = rrect(cx + x * sc / 1.0 if False else cx + x * sc, (top + bot) / 2, 84 * sc, bot - top, 30 * sc)
            c.poly(pivot_rot(leg, pv, rot), fill=mix(BG, (205, 205, 200), a), outline=mix(BG, INK, a), w=7)

def bottom_view(c, cx, cy, a=1.0, R=250, nfeet=5, hl=False):
    c.circle((cx, cy), R, fill=mix(BG, (226, 234, 232), a), outline=mix(BG, INK, a), w=9)
    for k in range(nfeet):
        ang = -math.pi / 2 + 2 * math.pi * k / 5
        c.circle((cx + R * 0.58 * math.cos(ang), cy + R * 0.58 * math.sin(ang)), R * 0.27, fill=mix(BG, (205, 205, 200), a), outline=mix(BG, INK, a), w=8)
    c.circle((cx, cy), R * 0.11, fill=mix(BG, RED, a))

def sc_hook(c, t):
    rich(c, 520, [("CETTE FORME", INK)], 92, eo(prog(t, 0.05, 0.5)))
    rich(c, 650, [("A L'AIR ABSURDE", RED)], 92, eo(prog(t, 0.3, 0.8)))
    bottom_view(c, CX, 1040, eo(prog(t, 0.5, 1.0)))
    label(c, CX, 1390, "LE FOND D'UNE BOUTEILLE DE SODA", 40, INK, eo(prog(t, 1.0, 1.5)), FM)

def sc_look(c, t):
    bottle(c, CX, 960, "flat", 0.9)
    c.line([(200, 960 + 170 * 0.9 * 0.55), (880, 960 + 170 * 0.9 * 0.55)], 5, mix(BG, INK, 1))
    rich(c, 520, [("CINQ ", RED), ("PIEDS", INK), (" BOMBÉS", INK)], 76, eo(prog(t, wt("cinq") - 0.2, wt("cinq") + 0.2)))
    label(c, CX, 1235, "POURQUOI PAS UN FOND PLAT ?", 52, INK, eo(prog(t, wt("pourquoi") - 0.1, wt("pourquoi") + 0.3)))

def sc_push(c, t):
    bottle(c, CX, 960, "flat", 0.95, arrows=prog(t, T_P + 0.3, T_P + 1.3))
    for k in range(9):
        c.circle((CX - 130 + (k % 3) * 130, 800 + (k // 3) * 55 + 8 * math.sin(t * 5 + k)), 9, outline=mix(BG, INK, 1), w=3)
    rich(c, 520, [("LE SODA ", INK), ("POUSSE", RED)], 84, eo(prog(t, T_P, T_P + 0.4)))
    label(c, CX, 1235, "LE GAZ APPUIE PARTOUT", 50, INK, eo(prog(t, wt("gaz") - 0.1, wt("gaz") + 0.3)))

def sc_half(c, t):
    bottle(c, CX, 960, "round", 0.95, arrows=prog(t, T_H, T_H + 0.8))
    rich(c, 520, [("LA ", INK), ("DEMI-SPHÈRE", RED)], 84, eo(prog(t, T_H - 0.1, T_H + 0.3)))
    if t > wt("encaisse"): 
        label(c, CX, 1235, "UN FOND ROND ENCAISSE", 50, INK, eo(prog(t, wt("encaisse"), wt("encaisse") + 0.3)))
        checkmark(c, 840, 700, eob(prog(t, wt("encaisse"), wt("encaisse") + 0.4)) * 1.3)

def sc_tilt(c, t):
    rot = 0.22 * math.sin((t - T_S) * 4.2) * math.exp(-(t - T_S) * 0.25)
    bottle(c, CX, 960, "round", 0.95, rot=rot)
    rich(c, 520, [("MAIS ELLE ", INK), ("BASCULE", RED)], 84, eo(prog(t, T_S, T_S + 0.4)))
    label(c, CX, 1235, "NE TIENT PAS DEBOUT", 52, RED, eo(prog(t, wt("tiendrait") - 0.1, wt("tiendrait") + 0.3)))

def sc_feet(c, t):
    nf = 1 + (t > wt("pieds", 1)) + (t > wt("pieds", 1) + 0.5)
    k = int(nf)
    bottle(c, CX, 960, "feet", 0.95, nfeet=min(3, k))
    c.line([(160, FLOOR - 30), (920, FLOOR - 30)], 5, mix(BG, INK, 1))
    label(c, 860, FLOOR + 10, "TABLE", 30, GREY, 1.0, FM)
    rich(c, 520, [("LE ROND ", INK), ("+ DES PIEDS", RED)], 78, eo(prog(t, T_A, T_A + 0.4)))
    if t > wt("creux"): label(c, CX, 1275, "LES CREUX RÉPARTISSENT LA POUSSÉE", 38, INK, eo(prog(t, wt("creux"), wt("creux") + 0.3)), FM)

def sc_before(c, t):
    a1 = eo(prog(t, T_AV, T_AV + 0.4)); a2 = eo(prog(t, wt("aujourdhui"), wt("aujourdhui") + 0.4))
    # avant : fond rond + socle séparé
    bottle(c, 300, 880, "round", 0.52, a=a1)
    sx, sy = 300, 880 + 170 * 0.52 + 20
    c.poly([(sx - 120, sy - 6), (sx + 120, sy - 6), (sx + 90, sy + 70), (sx - 90, sy + 70)], fill=mix(BG, (205, 205, 200), a1), outline=mix(BG, INK, a1), w=6)
    label(c, 300, 1180, "AVANT : 2 PIÈCES", 34, INK, a1, FM)
    label(c, 300, 1225, "SOCLE EN PLUS", 30, RED, a1, FM)
    bottle(c, 780, 880, "feet", 0.52, a=a2)
    label(c, 780, 1180, "AUJOURD'HUI :", 34, INK, a2, FM)
    label(c, 780, 1225, "1 SEUL BLOC", 30, RED, a2, FM)
    rich(c, 520, [("AVANT, ", INK), ("UN SOCLE", RED)], 80, eo(prog(t, T_AV, T_AV + 0.4)))

def sc_recap(c, t):
    t0 = T_R
    bottom_view(c, CX, 960, 1.0, 230)
    checkmark(c, 850, 700, eob(prog(t, t0, t0 + 0.4)) * 1.4)
    rich(c, 520, [("PAS ABSURDE :", INK)], 84, eo(prog(t, t0 - 0.2, t0 + 0.3)))
    rich(c, 1330, [("UN FOND ROND QUI TIENT DEBOUT", RED)], 50, eo(prog(t, wt("tient") - 0.1, wt("tient") + 0.3)))

def sc_next(c, t):
    t0 = T_N
    bottom_view(c, CX, 735, eo(prog(t, t0 - 0.1, t0 + 0.4)), 120)
    last = lambda w: WORDS[max(i for i, x in enumerate(NW) if x == nrm(w))][1]
    ts, td = last("secret"), last("dans")
    label(c, CX, 990, "UN SECRET D'INGÉNIEUR", 58, INK, eo(prog(t, ts - 0.1, ts + 0.3)))
    label(c, CX, 1085, "DANS CHAQUE OBJET", 58, RED, eo(prog(t, td - 0.1, td + 0.3)))
    subscribe_button(c, t, t0, T_CK)

SCENES = [sc_hook, sc_look, sc_push, sc_half, sc_tilt, sc_feet, sc_before, sc_recap, sc_next]
beat_of = beat_of_f(BEATS, SCENES)
CUR = [(0.0, 540, 1300), (1.2, 760, 1100), (T_L, 700, 1000), (T_P, 540, 1000), (T_H, 540, 1100), (T_S, 540, 1150), (T_A, 560, 1100), (T_AV, 540, 1000),
       (T_R, 700, 900), (T_N - 0.2, 700, 900), (T_CK - 0.25, 540, 1205), (DUR, 540, 1205)]
CLICKS = [T_R, T_CK]
draw_cursor = cursor_factory(CUR, CLICKS)
caption = caption_factory(EMPH)

def cam(t):
    b = beat_of(t); a0, a1 = BEATS[b], min(BEATS[b + 1], DUR)
    z = 1.0 + 0.04 * eio(prog(t, a0, a1)) * (b not in (0, 8))
    for tp in BEATS[1:-1]:
        if t >= tp: z *= 1 + 0.03 * math.exp(-(t - tp) * 9)
    return z, 540, 910

def header(c, t):
    Y = 330
    c.text((80, Y), "ÉPISODE 9", FM, 34, RED)
    c.text((80 + tw("ÉPISODE 9  ", FM, 34), Y), "· FORME CONTRE-INTUITIVE", FM, 34, GREY)
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
