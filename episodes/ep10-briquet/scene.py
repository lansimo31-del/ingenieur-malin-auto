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


# ================= LE BRIQUET À PIERRE (épisode 10 · devine ce que je construis) =================
T_C1 = wt("première"); T_V = wt("deuxième"); T_P = wt("troisième"); T_W = wt("enfin"); T_G = wt("deviné")
T_B = wt("appuie"); T_SP = wt("étincelles"); T_R = wt("briquet"); T_OFF = wt("relâche"); T_L = wt("première", 1)
T_N = wt("abonnetoi"); T_CK = we("abonnetoi") + 0.1
BEATS = [0.0, T_C1, T_V, T_P, T_W, T_G, T_B, T_R, T_OFF, T_L, T_N, 999.0]
EMPH = {nrm(x) for x in ["Devine", "construis.", "Réponse", "réservoir,", "valve,", "pierre,", "roue", "striée,", "deviné", "étincelles", "briquet,", "gaz.", "secret", "objet.", "Abonne-toi", "ressort."]}
NZ = (415, 812); WH = (600, 790)

def obj(c, t, mini=False):
    ox, oy, k = (0, 0, 1.0)
    def P(x, y): return (x, y)
    on = T_B <= t < T_OFF
    tank = 1.0 if mini else eob(prog(t, T_C1 + 0.05, T_C1 + 0.5))
    if tank > 0.03:
        box(c, 300, 900, 530, 900 + 300 * tank, (240, 240, 236), 7, INK, 1.0, 14)
        if tank > 0.9:
            lvl = 960
            c.poly([(308, lvl), (522, lvl), (522, 1192), (308, 1192)], fill=(236, 214, 150))
            c.line([(308, lvl), (522, lvl)], 4, GM)
            label(c, 415, 1085, "GAZ LIQUIDE", 34, INK, 1.0, FM)
    va = 1.0 if mini else eob(prog(t, T_V + 0.05, T_V + 0.5))
    if va > 0.03:
        open_ = 1.0 if on else 0.0
        box(c, 380, 845, 450, 900, (255, 255, 255), 6, RED if on else INK, va, 6)
        c.line([(415, 845), (415, 812 - 6 * open_)], 7 if not on else 4, mix(BG, INK, va))
        c.circle((415, 812), 6, fill=mix(BG, RED if on else INK, va))
    st = 1.0 if mini else eob(prog(t, T_P + 0.05, T_P + 0.5))
    if st > 0.03:
        box(c, 575, 840 + (1 - st) * 160, 625, 950, (120, 120, 128), 6, INK, 1.0, 4)
        sp = 1.0 if mini else eo(prog(t, T_P + 0.5, T_P + 1.0))
        if sp > 0.03: c.line(zig(600, 955, 955 + 150 * sp, 7, 18), 5, mix(BG, INK, sp))
        box(c, 560, 1105, 640, 1125, (214, 214, 210), 5, INK, sp if not mini else 1.0, 3)
    wa = 1.0 if mini else eob(prog(t, T_W + 0.05, T_W + 0.5))
    if wa > 0.03:
        rot = (t - T_B) * 14 if on else (0 if t < T_B else 0.0)
        r = 50 * wa
        c.circle(WH, r, fill=mix(BG, (230, 230, 226), 1), outline=mix(BG, INK, 1), w=7)
        for kk in range(12):
            a = rot + kk * math.pi / 6
            c.line([(WH[0] + r * 0.8 * math.cos(a), WH[1] + r * 0.8 * math.sin(a)), (WH[0] + r * 1.12 * math.cos(a), WH[1] + r * 1.12 * math.sin(a))], 5, mix(BG, INK, 1))
        c.circle(WH, 8, fill=INK)
    if on:
        for kk in range(6):                                        # gaz qui sort
            u = ((t - T_B) * 1.2 + kk / 6) % 1
            c.circle((NZ[0] + 14 * math.sin(kk * 2 + t * 5), NZ[1] - 12 - 70 * u), 7 * (1 - u * 0.4), outline=mix(BG, GM, 1 - u), w=3)
        if t >= T_SP - 0.3:
            for kk in range(7):                                    # étincelles de la roue vers la buse
                u = ((t * 3.2) + kk * 0.37) % 1
                x = WH[0] - 40 - (WH[0] - 40 - NZ[0]) * u * 0.95; y = WH[1] - 35 - 30 * math.sin(u * 3.14) + 40 * u
                c.circle((x, y), 6 * (1 - 0.4 * u), fill=RED)
        if t >= T_SP + 0.5:
            fa = eo(prog(t, T_SP + 0.5, T_SP + 0.8))
            fl = 1 + 0.08 * math.sin(t * 28)
            c.poly([(NZ[0] - 26, NZ[1] - 10), (NZ[0], NZ[1] - 150 * fa * fl), (NZ[0] + 26, NZ[1] - 10), (NZ[0], NZ[1] + 4)], fill=(250, 190, 60), outline=INK, w=5)
            c.poly([(NZ[0] - 11, NZ[1] - 8), (NZ[0], NZ[1] - 70 * fa * fl), (NZ[0] + 11, NZ[1] - 8)], fill=(255, 235, 150))

def sc_hook(c, t):
    rich(c, 520, [("DEVINE CE QUE", INK)], 92, eo(prog(t, 0.05, 0.5)))
    rich(c, 660, [("JE CONSTRUIS", RED)], 112, eo(prog(t, 0.3, 0.8)))
    label(c, CX, 1300, "?", 400, GF, eo(prog(t, 0.6, 1.1)))
    label(c, CX, 790, "RÉPONSE À LA FIN", 64, INK, eo(prog(t, T_C1 * 0.4, T_C1 * 0.4 + 0.4)))

def piece(n, txt, t0):
    def f(c, t):
        rich(c, 520, [("PIÈCE %d", RED)] if False else [("PIÈCE " + str(n), RED)], 80, eo(prog(t, t0, t0 + 0.4)))
        obj(c, t)
        label(c, CX, 1330, txt, 52, INK, eo(prog(t, t0 + 0.5, t0 + 0.9)))
    return f
sc_p1 = piece(1, "UN RÉSERVOIR DE GAZ LIQUIDE", T_C1)
sc_p2 = piece(2, "UNE VALVE QUI DOSE LE GAZ", T_V)
sc_p3 = piece(3, "UNE PIERRE ET SON RESSORT", T_P)
sc_p4 = piece(4, "UNE ROUE STRIÉE", T_W)

def sc_guess(c, t):
    rich(c, 520, [("TU AS ", INK), ("DEVINÉ ?", RED)], 92, eo(prog(t, T_G, T_G + 0.4)))
    obj(c, t)
    label(c, CX, 1330, "?", 150, RED, eo(prog(t, T_G + 0.4, T_G + 0.8)))

def sc_press(c, t):
    rich(c, 520, [("ON APPUIE", RED)], 84, eo(prog(t, T_B, T_B + 0.4)))
    obj(c, t)
    if t < T_SP: lab = "LA VALVE S'OUVRE, LA ROUE TOURNE"
    else: lab = "LA PIERRE ÉTINCELLE : LE GAZ S'ALLUME"
    label(c, CX, 1330, lab, 42, INK, eo(prog(t, T_B + 0.4, T_B + 0.8)), FM)

def sc_reveal(c, t):
    t0 = T_R
    obj(c, t)
    box(c, 90, 1250, 990, 1400, (255, 255, 255), 8, RED, eo(prog(t, t0 - 0.2, t0 + 0.2)), 20)
    label(c, CX, 1355, "UN BRIQUET", 96, RED, eo(prog(t, t0 - 0.1, t0 + 0.3)))

def sc_off(c, t):
    rich(c, 520, [("ON RELÂCHE : ", INK), ("PLUS DE GAZ", RED)], 66, eo(prog(t, T_OFF, T_OFF + 0.4)))
    obj(c, t)
    label(c, CX, 1330, "LA VALVE SE FERME, LA FLAMME S'ÉTEINT", 42, INK, eo(prog(t, T_OFF + 0.4, T_OFF + 0.8)), FM)

def sc_loop(c, t):
    t0 = T_L
    rich(c, 520, [("LA PREMIÈRE PIÈCE", INK)], 70, eo(prog(t, t0, t0 + 0.4)))
    box(c, 380, 760, 700, 1160, (240, 240, 236), 9, INK, 1.0, 20)
    c.poly([(388, 860), (692, 860), (692, 1152), (388, 1152)], fill=(236, 214, 150))
    label(c, CX, 1030, "GAZ", 70, INK, 1.0)
    checkmark(c, CX + 200, 740, eob(prog(t, t0 + 0.4, t0 + 0.7)) * 1.3)
    label(c, CX, 1262, "LE RÉSERVOIR GARDE LE GAZ", 52, INK, eo(prog(t, wt("garde"), wt("garde") + 0.4)))

sc_next = next_scene_factory(obj)
SCENES = [sc_hook, sc_p1, sc_p2, sc_p3, sc_p4, sc_guess, sc_press, sc_reveal, sc_off, sc_loop, sc_next]
beat_of = beat_of_f(BEATS, SCENES)
CUR = [(0.0, 540, 1300), (1.2, 700, 800), (T_C1, 415, 1000), (T_V, 415, 850), (T_P, 600, 950), (T_W, 600, 790), (T_G, 540, 700), (T_B, 415, 812),
       (T_R, 540, 1300), (T_OFF, 415, 830), (T_L, 540, 930), (T_N - 0.2, 700, 900), (T_CK - 0.25, 540, 1205), (DUR, 540, 1205)]
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
    c.text((80, Y), "ÉPISODE 10", FM, 34, RED)
    c.text((80 + tw("ÉPISODE 10  ", FM, 34), Y), "· DEVINE CE QUE JE CONSTRUIS", FM, 34, GREY)
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
