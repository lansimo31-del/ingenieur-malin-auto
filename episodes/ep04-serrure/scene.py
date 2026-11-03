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
T_C1 = wt("première");  T_H = wt("trous");  T_S = wt("ressort");  T_D = wt("goupille");  T_KP = wt("seconde")
T_G = wt("tu");  T_K = wt("glisse");  T_UP = we("hauteur");  T_SH = wt("coupure");  T_TURN = wt("tourne")
T_R = wt("cest", 2) if False else wt("serrure");  T_L = wt("première", 1);  T_N = wt("abonnetoi");  T_CK = we("abonnetoi") + 0.1
BEATS = [0.0, T_C1, T_H, T_G, T_K, T_R, T_L, T_N, 999.0]
EMPH = {nrm(x) for x in ["Devine", "construis.", "Réponse", "cylindre,", "ressort", "goupille", "deviné", "serrure,", "coupure", "tourne", "enfin.", "secret", "objet.", "Abonne-toi", "dents"]}

PX = [290, 415, 540, 665, 790]; SHEAR = 900; FLOOR = 1060
HK = [120, 80, 150, 100, 60]          # longueurs des goupilles du bas (en contact avec la clé)
DRV = 90; TOP = 690                    # goupille du haut, haut de la cavité

def key_profile(d):
    pts = [(-1, 1135), (0, 1135)]
    for j in range(4, -1, -1):
        dj = 50 + (4 - j) * 125; b = SHEAR + HK[j]
        pts += [(dj - 16, b), (dj + 16, b)]
        if j: pts.append((dj + 62, 1068))
    pts += [(560, 1068), (900, 1068)]
    xs, ys = zip(*pts); return float(_np.interp(d, xs, ys))

def tip_x(t):
    return 100 + (840 - 100) * eio(prog(t, T_K + 0.3, T_UP + 0.1))

def cyl_front(c, cx, cy, R, a=1.0):
    c.circle((cx, cy), R, fill=mix(BG, (214, 214, 210), a), outline=mix(BG, INK, a), w=10)
    c.circle((cx, cy), R * 0.84, fill=mix(BG, STF, a), outline=mix(BG, INK, a), w=5)
    c.poly(rrect(cx, cy - R * 0.12, R * 0.22, R * 0.62, 6), fill=mix(BG, INK, a))
    c.poly(rrect(cx, cy + R * 0.2, R * 0.5, R * 0.14, 6), fill=mix(BG, INK, a))

def sc_hook(c, t):
    rich(c, 520, [("DEVINE CE QUE", INK)], 92, eo(prog(t, 0.05, 0.5)))
    rich(c, 660, [("JE CONSTRUIS", RED)], 112, eo(prog(t, 0.3, 0.8)))
    label(c, CX, 1300, "?", 400, GF, eo(prog(t, 0.6, 1.1)))
    label(c, CX, 790, "RÉPONSE À LA FIN", 64, INK, eo(prog(t, T_C1 * 0.4, T_C1 * 0.4 + 0.4)))

def sc_cyl(c, t):
    t0 = T_C1
    rich(c, 520, [("PIÈCE 1", RED)], 84, eo(prog(t, t0, t0 + 0.4)))
    cyl_front(c, CX, 930, 250 * eob(prog(t, t0 + 0.1, t0 + 0.6)) + 1, 1.0)
    label(c, CX, 1262, "UN CYLINDRE ET SA FENTE", 56, INK, eo(prog(t, t0 + 0.8, t0 + 1.2)))

def cross(c, t, stage_label=None):
    ts = T_H - 0.0
    a0 = eo(prog(t, ts, ts + 0.4))
    # boîtier (haut) et cylindre (bas)
    box(c, 200, TOP - 10, 880, SHEAR, STF, 8, INK, a0, 6)
    box(c, 200, SHEAR, 880, 1135, (222, 222, 218), 8, INK, a0, 6)
    c.line([(200, SHEAR), (880, SHEAR)], 3, mix(BG, GM, a0))
    if t >= T_SH:
        ps = eo(prog(t, T_SH, T_SH + 0.5)); dashed(c, [(170, SHEAR), (910, SHEAR)], 22, 12, 7, mix(BG, RED, ps))
        label(c, 150, SHEAR - 14, "COUPURE", 34, RED, ps, FM)
    for i, x in enumerate(PX):
        ph = eob(prog(t, T_H + 0.1 + i * 0.1, T_H + 0.4 + i * 0.1))
        if ph < 0.03: continue
        hole = [(x - 28, TOP * 1 + 0), (x + 28, TOP), (x + 28, FLOOR), (x - 28, FLOOR)]
        c.poly([(x - 28 * ph, TOP), (x + 28 * ph, TOP), (x + 28 * ph, FLOOR), (x - 28 * ph, FLOOR)], fill=mix(BG, BG, 1), outline=mix(BG, INK, 1), w=4)
    for i, x in enumerate(PX):
        d = tip_x(t) - x if t >= T_K else -999
        lift = min(FLOOR, key_profile(d)) if d > -300 else FLOOR
        ybot = lift if t >= T_K else FLOOR
        # clé ou non : position des goupilles
        kt = ybot - HK[i]; dt = kt - DRV
        pk = eob(prog(t, T_KP + 0.05, T_KP + 0.4)) if i == 0 else eob(prog(t, T_KP + 0.05 + 0.18 * i, T_KP + 0.4 + 0.18 * i)) if t < T_G else 1.0
        pd = eob(prog(t, T_D + 0.05 + 0.12 * i, T_D + 0.35 + 0.12 * i)) if t < T_KP else 1.0
        ps = eo(prog(t, T_S + 0.05 + 0.1 * i, T_S + 0.4 + 0.1 * i))
        if t >= T_S: c.line(zig(x, TOP + 6, dt if t >= T_D else dt - DRV, 6, 15), 5, mix(BG, INK, ps))
        if t >= T_D and pd > 0.03: box(c, x - 22, dt, x + 22, kt, (250, 240, 215), 5, INK, pd, 3)
        if t >= T_KP and pk > 0.03: box(c, x - 22, kt, x + 22, ybot, (255, 255, 255), 5, RED if t >= T_UP else INK, pk, 3)
    if t >= T_K:
        tx = tip_x(t); xs = list(range(int(tx) - 700, int(tx) + 1, 14))
        top = [(x, key_profile(tx - x)) for x in xs if x > 215 and 0 <= tx - x]
        if len(top) > 2:
            bot = [(top[-1][0], 1128), (top[0][0], 1128)]
            c.poly(top + bot, fill=(236, 214, 120), outline=mix(BG, INK, 1), w=5)
    # étiquettes
    if stage_label: label(c, CX, 1262, stage_label, 56, INK, 1.0)

def sc_cross1(c, t):          # trous, ressorts, goupilles
    rich(c, 520, [("PIÈCES 2 · 3 · 4", RED)], 72, eo(prog(t, T_H, T_H + 0.4)))
    if t < T_S: lab = "DES PETITS TROUS"
    elif t < T_D: lab = "DES RESSORTS"
    elif t < T_KP: lab = "UNE GOUPILLE"
    else: lab = "UNE SECONDE, PLUS LONGUE"
    cross(c, t, lab)

def sc_guess(c, t):
    rich(c, 520, [("TU AS ", INK), ("DEVINÉ ?", RED)], 92, eo(prog(t, T_G, T_G + 0.4)))
    cross(c, t, None)
    label(c, CX, 1262, "?", 150, RED, eo(prog(t, T_G + 0.4, T_G + 0.8)))

def sc_key(c, t):
    rich(c, 520, [("UNE PIÈCE PLATE ", INK), ("À DENTS", RED)], 64, eo(prog(t, T_K, T_K + 0.4)))
    cross(c, t, None)
    if t >= T_SH: label(c, CX, 1262, "TOUT S'ALIGNE : ÇA TOURNE", 56, RED, eo(prog(t, T_SH, T_SH + 0.4)))
    if t >= T_TURN:
        p = eo(prog(t, T_TURN, T_TURN + 0.5)); cx_, cy_ = 930, 1010
        c.line(circ_pts(cx_, cy_, 60, 40, -2.4, -2.4 + 4.6 * p), 9, mix(BG, RED, 1))

def sc_reveal(c, t):
    t0 = T_R
    cross(c, t, None)
    box(c, 90, 1180, 990, 1340, (255, 255, 255), 8, RED, eo(prog(t, t0 - 0.2, t0 + 0.2)), 20)
    label(c, CX, 1290, "UNE SERRURE", 96, RED, eo(prog(t, t0 - 0.1, t0 + 0.3)))
    rich(c, 520, [("LA PORTE D'ENTRÉE", INK)], 64, eo(prog(t, wt("porte"), wt("porte") + 0.4)))

def sc_loop(c, t):
    t0 = T_L
    rich(c, 520, [("LA PREMIÈRE PIÈCE", INK)], 70, eo(prog(t, t0, t0 + 0.4)))
    cyl_front(c, CX, 930, 250, 1.0)
    if t > wt("tourne", 1): c.line(circ_pts(CX, 930, 300, 40, -2.4, -2.4 + 4.6 * eo(prog(t, wt("tourne", 1), wt("tourne", 1) + 0.5))), 10, mix(BG, RED, 1))
    checkmark(c, CX + 210, 760, eob(prog(t, t0 + 0.4, t0 + 0.7)) * 1.3)
    label(c, CX, 1262, "ELLE TOURNE ET OUVRE LA PORTE", 52, INK, eo(prog(t, wt("tourne", 1), wt("tourne", 1) + 0.4)))

def sc_next(c, t):
    t0 = T_N
    cyl_front(c, CX, 735, 150 * eo(prog(t, t0 - 0.1, t0 + 0.4)) + 1)
    last = lambda w: WORDS[max(i for i, x in enumerate(NW) if x == nrm(w))][1]
    ts, td = last("secret"), last("dans")
    label(c, CX, 990, "UN SECRET D'INGÉNIEUR", 58, INK, eo(prog(t, ts - 0.1, ts + 0.3)))
    label(c, CX, 1085, "DANS CHAQUE OBJET", 58, RED, eo(prog(t, td - 0.1, td + 0.3)))
    subscribe_button(c, t, t0, T_CK)

SCENES = [sc_hook, sc_cyl, sc_cross1, sc_guess, sc_key, sc_reveal, sc_loop, sc_next]
beat_of = beat_of_f(BEATS, SCENES)
CUR = [(0.0, 540, 1300), (1.2, 700, 800), (T_C1, 540, 900), (T_H, 300, 800), (T_S, 540, 800), (T_D, 700, 850), (T_G, 540, 700), (T_K, 200, 1090),
       (T_UP, 700, 1000), (T_R, 540, 1280), (T_L, 540, 930), (T_N - 0.2, 700, 900), (T_CK - 0.25, 540, 1205), (DUR, 540, 1205)]
CLICKS = [T_H, T_S, T_D, T_K, T_CK]
draw_cursor = cursor_factory(CUR, CLICKS)
caption = caption_factory(EMPH)

def cam(t):
    b = beat_of(t); a0, a1 = BEATS[b], min(BEATS[b + 1], DUR)
    z = 1.0 + 0.05 * eio(prog(t, a0, a1)) * (b not in (0, 7))
    for tp in BEATS[1:-1]:
        if t >= tp: z *= 1 + 0.04 * math.exp(-(t - tp) * 9)
    return z, 540, 910

def header(c, t):
    Y = 330
    c.text((80, Y), "ÉPISODE 4", FM, 34, RED)
    c.text((80 + tw("ÉPISODE 4  ", FM, 34), Y), "· DEVINE CE QUE JE CONSTRUIS", FM, 34, GREY)
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
