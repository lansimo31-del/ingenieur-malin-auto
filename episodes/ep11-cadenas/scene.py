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


# ================= LE PETIT TROU SOUS LE CADENAS (épisode 11 · c'est fait exprès) =================
T_L = wt("regarde"); T_D = wt("dirait"); T_E = wt("entrée"); T_P = wt("pourtant"); T_RAIN = wt("dehors"); T_SI = wt("sans")
T_RO = wt("rouille"); T_PI = wt("pire"); T_GE = wt("gèle"); T_LE = wt("laisse"); T_OIL = wt("goutte"); T_RI = wt("rien")
T_BO = wt("bouche"); T_EV = wt("évacuation"); T_N = wt("abonnetoi"); T_CK = we("abonnetoi") + 0.1
BEATS = [0.0, T_L, T_P, T_RAIN, T_PI, T_LE, T_RI, T_N, 999.0]
EMPH = {nrm(x) for x in ["défaut.", "trou", "petit", "raté,", "crocheter.", "exprès.", "pluie", "rouille,", "gripper.", "gèle.", "glace", "fissurer", "écouler.", "huile,",
                          "bouche", "jamais.", "évacuation.", "défaut", "secret", "objet.", "Abonne-toi", "l'eau"]}
WATER = (150, 195, 235); ICE = (205, 232, 246); RUST = (190, 105, 45)
IX0, IX1, IY0, IY1 = 372, 708, 940, 1146        # cavité intérieure
HX, HY = 540, 1162                               # le trou, sous le cadenas

def padlock(c, t, cut=False, mini=False):
    c.line(circ_pts(540, 880, 150, 40, math.pi, 2 * math.pi) + [(690, 900)], 22, mix(BG, (150, 150, 150), 1))
    c.line([(390, 900)] + circ_pts(540, 880, 150, 40, math.pi, 2 * math.pi)[1:] + [(690, 900)], 12, mix(BG, INK, 1))
    box(c, 330, 900, 750, 1170, (205, 205, 200), 10, INK, 1.0, 26)
    if not cut:
        c.circle((540, 1010), 26, fill=INK); c.poly([(530, 1020), (550, 1020), (556, 1080), (524, 1080)], fill=INK)
    c.circle((HX, HY), 11, fill=RED, outline=INK, w=3)

def interior(c, t, level, state):
    box(c, 330, 900, 750, 1170, (205, 205, 200), 10, INK, 1.0, 26)
    box(c, IX0, IX1 and IY0, IX1, IY1, (246, 246, 242), 5, INK, 1.0, 8)
    for x in (430, 540, 650):                                     # ressorts et goupilles
        c.line(zig(x, IY0 + 4, IY0 + 70, 5, 12), 5, INK)
        c.poly(rrect(x, IY0 + 105, 36, 60, 4), fill=(250, 240, 215), outline=INK, w=4)
    if level > 0:
        ly = IY1 - level
        col = ICE if state == "ice" else WATER
        c.poly([(IX0 + 3, ly), (IX1 - 3, ly), (IX1 - 3, IY1 - 3), (IX0 + 3, IY1 - 3)], fill=mix(BG, col, 0.85), outline=None) if False else c.poly([(IX0 + 3, ly), (IX1 - 3, ly), (IX1 - 3, IY1 - 3), (IX0 + 3, IY1 - 3)], fill=col)
        c.line([(IX0 + 3, ly), (IX1 - 3, ly)], 4, mix(BG, INK, 0.6))
    c.circle((HX, HY), 11, fill=RED, outline=INK, w=3)
    c.poly([(HX - 12, IY1 - 4), (HX + 12, IY1 - 4), (HX + 12, 1172), (HX - 12, 1172)], fill=BG if state != "closed" else INK)

def rain(c, t, t0, t1):
    if not (t0 <= t < t1): return
    for kk in range(9):
        u = ((t - t0) * 0.9 + kk / 9) % 1
        x = 360 + kk * 40; y = 600 + 380 * u
        c.line([(x, y), (x - 8, y + 30)], 5, mix(BG, WATER, 1))

def sc_hook(c, t):
    rich(c, 520, [("CE N'EST PAS", INK)], 92, eo(prog(t, 0.05, 0.5)))
    rich(c, 650, [("UN DÉFAUT", RED)], 118, eo(prog(t, 0.3, 0.8)))
    a = eo(prog(t, 0.5, 1.0)); padlock(c, t)
    if t > 1.0:
        a = eo(prog(t, 1.0, 1.4)); arrow(c, (HX, 1290 + 20 * (1 - a)), (HX, 1195), 7, mix(BG, RED, a), 20)

def sc_look(c, t):
    padlock(c, t)
    rich(c, 520, [("UN PETIT ", INK), ("TROU", RED)], 84, eo(prog(t, wt("petit"), wt("petit") + 0.4)))
    if t >= T_D: label(c, CX, 1250, "UN TROU RATÉ ?", 54, INK, eo(prog(t, T_D, T_D + 0.4)))
    if t >= T_E: label(c, CX, 1320, "UNE ENTRÉE POUR LE CROCHETER ?", 40, INK, eo(prog(t, T_E, T_E + 0.4)))

def sc_why(c, t):
    padlock(c, t)
    rich(c, 520, [("IL EST LÀ ", INK), ("EXPRÈS", RED)], 88, eo(prog(t, T_P, T_P + 0.4)))
    checkmark(c, 800, 780, eob(prog(t, wt("exprès"), wt("exprès") + 0.4)) * 1.4)

def sc_rain(c, t):
    lvl_t = eio(prog(t, T_SI, T_SI + 2.0))
    interior(c, t, 120 * lvl_t, "water")
    rain(c, t, T_RAIN, T_PI)
    if t < T_SI: lab = "LA PLUIE S'INFILTRE"
    elif t < T_RO: lab = "SANS ISSUE, L'EAU RESTE AU FOND"
    else: lab = "L'ACIER ROUILLE, LE MÉCANISME GRIPPE"
    label(c, CX, 1320, lab, 38, INK, eo(prog(t, T_RAIN, T_RAIN + 0.4)), FM)
    rich(c, 520, [("EAU ", RED), ("PIÉGÉE", INK)], 84, eo(prog(t, T_RAIN, T_RAIN + 0.4)))
    if t >= T_RO:
        for k_, (x, y) in enumerate(((430, 1060), (540, 1090), (650, 1050), (590, 1120))):
            a = eob(prog(t, T_RO + 0.1 * k_, T_RO + 0.4 + 0.1 * k_)); c.circle((x, y), 16 * a + 1, fill=RUST, outline=INK, w=3)

def sc_freeze(c, t):
    f = eo(prog(t, T_GE - 0.2, T_GE + 0.6))
    interior(c, t, 120 + 24 * f, "ice" if t >= T_GE else "water")
    rich(c, 520, [("EN HIVER : ", INK), ("ELLE GÈLE", RED)], 78, eo(prog(t, T_PI, T_PI + 0.4)))
    if t >= wt("fissurer"):
        a = eo(prog(t, wt("fissurer"), wt("fissurer") + 0.4))
        for pts in ([(450, 1000), (470, 1040), (448, 1075)], [(620, 990), (600, 1030), (625, 1060)], [(380, 1100), (330, 1130)]):
            c.line(pts, 7, mix(BG, RED, a))
        label(c, CX, 1320, "LA GLACE PREND PLUS DE PLACE : ÇA FISSURE", 36, INK, a, FM)
    elif t >= wt("glace"): label(c, CX, 1320, "LA GLACE PREND PLUS DE PLACE QUE L'EAU", 36, INK, eo(prog(t, wt("glace"), wt("glace") + 0.4)), FM)

def sc_drain(c, t):
    d = eio(prog(t, T_LE + 0.4, T_LE + 2.0))
    interior(c, t, 144 * (1 - d), "water" if d < 1 else "open")
    if 0.05 < d < 0.98:
        for k_ in range(5):
            u = ((t * 1.6) + k_ / 5) % 1; c.circle((HX, 1190 + 90 * u), 8 * (1 - 0.3 * u), fill=WATER, outline=INK, w=2)
    rich(c, 520, [("LE TROU ", RED), ("ÉVACUE L'EAU", INK)], 72, eo(prog(t, T_LE, T_LE + 0.4)))
    if t >= T_OIL:
        a = eo(prog(t, T_OIL, T_OIL + 0.4)); u = prog(t, T_OIL, T_OIL + 1.0)
        c.circle((HX, 1290 - 90 * u), 12, fill=(236, 190, 60), outline=INK, w=3)
        label(c, CX, 1360, "OU UNE GOUTTE D'HUILE POUR GRAISSER", 36, INK, a, FM)

def sc_final(c, t):
    padlock(c, t)
    rich(c, 520, [("NE LE BOUCHE ", INK), ("JAMAIS", RED)], 78, eo(prog(t, T_RI, T_RI + 0.4)))
    t2 = wt("défaut", 1)
    if t >= t2:
        a = eo(prog(t, t2, t2 + 0.4)); checkmark(c, 800, 780, eob(prog(t, t2, t2 + 0.4)) * 1.4)
        rich(c, 1290, [("UNE ÉVACUATION", RED)], 84, a)

def obj(c, t, mini=False): padlock(c, t)
sc_next = next_scene_factory(obj)
SCENES = [sc_hook, sc_look, sc_why, sc_rain, sc_freeze, sc_drain, sc_final, sc_next]
beat_of = beat_of_f(BEATS, SCENES)
CUR = [(0.0, 540, 1300), (1.2, 700, 1200), (T_L, 540, 1180), (T_P, 700, 1100), (T_RAIN, 540, 700), (T_SI, 540, 1100), (T_PI, 540, 1000), (T_LE, 540, 1170),
       (T_RI, 600, 1100), (T_N - 0.2, 700, 900), (T_CK - 0.25, 540, 1205), (DUR, 540, 1205)]
CLICKS = [T_L, T_P, T_LE, T_CK]
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
    c.text((80, Y), "ÉPISODE 11", FM, 34, RED)
    c.text((80 + tw("ÉPISODE 11  ", FM, 34), Y), "· C'EST FAIT EXPRÈS", FM, 34, GREY)
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
