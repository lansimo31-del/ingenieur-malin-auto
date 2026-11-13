# ================= MOTEUR COMMUN =================
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






# ================= LE TIRE-BOUCHON À AILES (épisode 19 · devine ce que je construis) =================
# L'objet n'est nommé qu'à la chute. Une pièce = un indice, apparue au mot-repère.
T_Vis = wt("vis"); T_Tige = wt("tige"); T_Corps = wt("corps"); T_Bras = wt("bras."); T_Dev = wt("tu"); T_Tourne = wt("tourne")
T_Rabat = wt("rabat"); T_Rev = wt("tire-bouchon"); T_Ret = wt("retour"); T_N = wt("abonnetoi"); T_CK = we("abonnetoi") + 0.1
T_Roue = wt("roue"); T_R = T_Rev
BEATS = [0.0, T_Vis, T_Tige, T_Corps, T_Bras, T_Dev, T_Tourne, T_Rabat, T_Rev, T_Ret, T_N, 999.0]
EMPH = {nrm(x) for x in ["construis.", "fin.", "vis", "spirale,", "crémaillère.", "crémaillère", "bras.", "deviné", "tourne", "rabat", "ailes.", "brevet", "spirale", "secret", "objet.", "tire-bouchon"]}

def arm_angle(t):  # 0 = bras vers le bas, 100° = bras levés (ailes)
    a = 15.0
    if t > T_Tourne: a = 15 + 90 * eio(prog(t, T_Tourne, T_Tourne + 2.0))
    if t > T_Rabat: a = 105 - 100 * eio(prog(t, T_Rabat, T_Rabat + 1.8))
    return a
def rack_dy(t): return 70 * (arm_angle(t) - 5) / 100.0 - 7

def bar(c, a, b, w=14, col=None, p=1.0):
    pen_poly(c, [a, b], p, w, col or INK)
def spiral(c, cx, y0, y1, phase, w=11, col=None, amp=34, n=7):
    pts = []
    for k in range(n * 8 + 1):
        u = k / (n * 8); y = y0 + (y1 - y0 - (y1 - y0) * 0.12 * u) * u if False else y0 + (y1 - y0) * u
        half = amp * (1 - 0.82 * max(0, u - 0.82) / 0.18)
        pts.append((cx + half * math.sin(2 * math.pi * (n * u) + phase), y))
    c.line(pts, w, col or INK)

def gear(c, cx, cy, r, ang, a=1.0, col=None):
    pts = []
    for k in range(48):
        th = 2 * math.pi * k / 48 + ang; rr = r + (9 if (k // 2) % 2 == 0 else -4)
        pts.append((cx + rr * math.cos(th), cy + rr * math.sin(th)))
    c.poly(pts, fill=mix(BG, (232, 232, 228), a), outline=mix(BG, col or INK, a), w=5)
    c.circle((cx, cy), 8, fill=mix(BG, INK, a))

def object19(c, t, mini=False):
    dy = rack_dy(t); ph = (rack_dy(t) / 70.0) * 2 * math.pi * 3
    pv = lambda tt: eo(prog(t, tt, tt + 0.5))
    # bouteille (après la question)
    if t > T_Tourne - 0.3:
        b = pv(T_Tourne - 0.3)
        for x in (490, 590): c.line([(x, 1140), (x, 1260)], 8, mix(BG, INK, b))
        c.line([(480, 1128), (600, 1128)], 10, mix(BG, INK, b))
        cork_y0 = 1075 + dy * 0.0
        box(c, 508, 1075 + dy - 6, 572, 1200 + dy - 6, (222, 196, 160), 6, INK, b, 8)
    # crémaillère
    if t > T_Tige - 0.1 and not mini:
        p = pv(T_Tige)
        box(c, 522, 640 + dy, 558, 960 + dy, (242, 242, 238), 6, INK, p, 4)
        for y in range(650, 950, 22):
            c.line([(514, y + dy), (522, y + dy)], 6, mix(BG, INK, p)); c.line([(558, y + dy), (566, y + dy)], 6, mix(BG, INK, p))
    # vis (spirale)
    if t > T_Vis - 0.1:
        p = pv(T_Vis)
        col = RED if (T_Ret <= t < T_N) else INK
        y0 = 960 + dy if t > T_Tige - 0.1 else 800
        spiral(c, 540, y0, y0 + 215, ph, 12, mix(BG, col, p))
    # corps creux
    if t > T_Corps - 0.1 and not mini:
        p = pv(T_Corps); box(c, 490, 880, 590, 1010, None, 8, INK, p, 10)
    # bras + roues dentées
    if t > T_Roue - 0.2 and not mini:
        p = pv(T_Roue - 0.1); a = math.radians(arm_angle(t))
        for s in (-1, 1):
            gx, gy = 540 + s * 62, 740
            dx, dy2 = s * math.sin(a), math.cos(a)
            bar(c, (gx, gy), (gx + dx * 250 * p, gy + dy2 * 250 * p), 22, INK)
            c.circle((gx + dx * 250 * p, gy + dy2 * 250 * p), 16, fill=mix(BG, RED, p), outline=INK, w=5)
            gear(c, gx, gy, 40, (rack_dy(t) / 40.0) * s, p)

def sc_hook(c, t):
    rich(c, 520, [("DEVINE CE QUE", INK)], 82, eo(prog(t, 0.05, 0.5)))
    rich(c, 640, [("JE CONSTRUIS", RED)], 88, eo(prog(t, 0.35, 0.85)))
    label(c, CX, 1000, "?", 380, RED, eo(prog(t, 0.6, 1.2)))
    label(c, CX, 1290, "RÉPONSE À LA FIN", 50, INK, eo(prog(t, wt("réponse") - 0.1, wt("réponse") + 0.3)), FM)
def mk(txt_parts, t0, size=62):
    def f(c, t):
        rich(c, 520, txt_parts, size, eo(prog(t, t0, t0 + 0.4))); object19(c, t)
    return f
sc_p1 = mk([("PIÈCE 1 : ", INK), ("UNE VIS", RED)], T_Vis)
sc_p2 = mk([("PIÈCE 2 : ", INK), ("UNE CRÉMAILLÈRE", RED)], T_Tige, 56)
sc_p3 = mk([("PIÈCE 3 : ", INK), ("UN CORPS CREUX", RED)], T_Corps, 56)
sc_p4 = mk([("PIÈCE 4 : ", INK), ("DEUX BRAS", RED)], T_Bras - 1.8, 62)
def sc_guess(c, t):
    rich(c, 520, [("TU AS ", INK), ("DEVINÉ ?", RED)], 90, eo(prog(t, T_Dev, T_Dev + 0.4))); object19(c, t)
def sc_turn(c, t):
    rich(c, 520, [("ON ", INK), ("TOURNE", RED), (" LA VIS", INK)], 70, eo(prog(t, T_Tourne - 0.1, T_Tourne + 0.4))); object19(c, t)
def sc_fold(c, t):
    rich(c, 520, [("ON ", INK), ("RABAT", RED), (" LES BRAS", INK)], 70, eo(prog(t, T_Rabat - 0.1, T_Rabat + 0.4))); object19(c, t)
def sc_reveal(c, t):
    object19(c, t)
    box(c, 70, 430, 1010, 580, (255, 255, 255), 8, RED, eo(prog(t, T_Rev - 0.2, T_Rev + 0.2)), 20)
    label(c, CX, 530, "UN TIRE-BOUCHON À AILES", 48, RED, eo(prog(t, T_Rev - 0.1, T_Rev + 0.3)))
    b = eo(prog(t, wt("mille") - 0.2, wt("mille") + 0.3))
    label(c, CX, 680, "BREVET US · 1930 · ROSATI", 46, INK, b, FM)
def sc_loop(c, t):
    object19(c, t)
    rich(c, 520, [("RETOUR À ", INK), ("LA SPIRALE", RED)], 70, eo(prog(t, T_Ret - 0.1, T_Ret + 0.4)))
def sc_next(c, t):
    next_scene_factory(lambda c, t, mini=True: spiral(c, 540, 640, 840, 0, 12, RED))(c, t)
SCENES = [sc_hook, sc_p1, sc_p2, sc_p3, sc_p4, sc_guess, sc_turn, sc_fold, sc_reveal, sc_loop, sc_next]
beat_of = beat_of_f(BEATS, SCENES)
CUR = [(0.0, 540, 1300)] + [(b, 540 + 60 * ((i % 3) - 1), 1000) for i, b in enumerate(BEATS[1:-2])] + [(T_N - 0.2, 700, 900), (T_CK - 0.25, 540, 1205), (DUR, 540, 1205)]
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
    c.text((80, Y), "ÉPISODE 19", FM, 34, RED)
    c.text((80 + tw("ÉPISODE 19  ", FM, 34), Y), "· DEVINE CE QUE JE CONSTRUIS", FM, 34, GREY)
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
