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
T_L = wt("regarde"); T_D = wt("dirait"); T_P = wt("pourtant"); T_1 = wt("première"); T_2 = wt("deuxième"); T_Q = wt("pourquoi")
T_PA = wt("parce"); T_DG = wt("dégradé"); T_R = wt("bouclier"); T_N = wt("abonnetoi"); T_CK = we("abonnetoi") + 0.1
T_UV = wt("ultraviolets"); T_CO = wt("cordon")
BEATS = [0.0, T_L, T_P, T_1, T_2, T_Q, T_R, T_N, 999.0]
EMPH = {nrm(x) for x in ["défaut.", "défaut", "bande", "noire", "points", "saleté,", "céramique", "colle", "colle.", "polyuréthane,", "ultraviolets.", "cordon",
                          "dégradé", "douce.", "bouclier", "secret", "objet.", "brutal", "noir", "chauffe"]}

def glass_w(c, cx, cy, w=760, h=520, a=1.0, band=64, dots=True, hl=False):
    # pare-brise vu de face : verre clair, bande noire sur le pourtour, points qui s'espacent vers l'intérieur
    c.poly(rrect(cx, cy, w, h, 70), fill=mix(BG, (226, 234, 232), a), outline=mix(BG, INK, a), w=9)
    x0, x1, y0, y1 = cx - w / 2, cx + w / 2, cy - h / 2, cy + h / 2
    c.poly(rrect(cx, cy, w, h, 70), fill=None, outline=mix(BG, INK, a), w=band * 2)
    c.poly(rrect(cx, cy, w, h, 70), fill=None, outline=mix(BG, INK, a), w=9)
    if dots:
        for r in range(4):
            rr = 15 - r * 3.4
            off = band + 18 + r * 26
            for k in range(0, int(w - 2 * off), 34 + r * 6):
                x = x0 + off + k
                c.circle((x, y1 - off + 14 - r * 4 - 14), rr, fill=mix(BG, RED if hl else INK, a))
            for k in range(0, int(h - 2 * off - 90), 34 + r * 6):
                y = y0 + off + 45 + k
                c.circle((x0 + off - 10, y), rr, fill=mix(BG, RED if hl else INK, a))
                c.circle((x1 - off + 10, y), rr, fill=mix(BG, RED if hl else INK, a))

def sc_hook(c, t):
    rich(c, 520, [("CE N'EST PAS", INK)], 92, eo(prog(t, 0.05, 0.5)))
    rich(c, 650, [("UN DÉFAUT", RED)], 118, eo(prog(t, 0.3, 0.8)))
    glass_w(c, CX, 1040, 760, 520, eo(prog(t, 0.5, 1.0)))

def sc_look(c, t):
    glass_w(c, CX, 1040, 760, 520, 1.0, hl=(t > T_D))
    rich(c, 520, [("BANDE ", INK), ("NOIRE", RED), (" + POINTS", INK)], 76, eo(prog(t, T_L + 0.2, T_L + 0.6)))
    if t >= T_D: label(c, CX, 1400 - 70, "SALETÉ ? DÉCOR RATÉ ?", 56, INK, eo(prog(t, T_D, T_D + 0.4)))

def sc_why(c, t):
    glass_w(c, CX, 1040, 760, 520, 1.0)
    rich(c, 520, [("CÉRAMIQUE ", RED), ("NOIRE", INK)], 82, eo(prog(t, T_P, T_P + 0.4)))
    label(c, CX, 600, "CUITE DANS LE VERRE", 54, INK, eo(prog(t, wt("cuite") - 0.1, wt("cuite") + 0.3)))

def section(c, t, uv):
    # coupe : verre, bande noire, cordon de colle, carrosserie
    c.poly([(200, 1120), (880, 1120), (880, 1200), (200, 1200)], fill=mix(BG, (214, 214, 210), 1), outline=mix(BG, INK, 1), w=6)
    label(c, 280, 1250, "CARROSSERIE", 30, GREY, 1.0, FM)
    c.poly([(520, 1066), (800, 1066), (800, 1120), (520, 1120)], fill=mix(BG, (214, 160, 40), 1), outline=mix(BG, INK, 1), w=5)
    label(c, 660, 1170, "COLLE", 32, INK, 1.0, FM)
    c.poly([(200, 1020), (880, 1020), (880, 1066), (200, 1066)], fill=mix(BG, (226, 234, 232), 1), outline=mix(BG, INK, 1), w=6)
    c.poly([(520, 1046), (880, 1046), (880, 1066), (520, 1066)], fill=mix(BG, INK, 1))
    label(c, 340, 1010, "VERRE", 30, GREY, 1.0, FM)
    if uv:
        a = eo(prog(t, T_1 + 0.5, T_1 + 1.0))
        for k, x in enumerate((300, 400, 560, 660, 760)):
            blocked = x >= 520; y1 = 1000 if blocked else 1090
            c.rline([(x - 70, 780), (x, y1)], 6, mix(BG, RED, a))
            if blocked: c.rline([(x - 18, y1 - 22), (x + 18, y1 + 6)], 6, mix(BG, INK, a)); c.rline([(x + 18, y1 - 22), (x - 18, y1 + 6)], 6, mix(BG, INK, a))
        label(c, 560, 740, "UV (SOLEIL)", 38, RED, a, FM)

def sc_glue(c, t):
    section(c, t, True)
    rich(c, 520, [("LA ", INK), ("COLLE", RED), (" AIME PEU LES UV", INK)], 58, eo(prog(t, T_1, T_1 + 0.4)))
    if t >= T_UV: label(c, CX, 1360, "LA BANDE NOIRE FAIT ÉCRAN", 46, INK, eo(prog(t, T_UV, T_UV + 0.4)))

def sc_hide(c, t):
    a = eo(prog(t, T_CO, T_CO + 0.6))
    glass_w(c, CX, 960, 760, 520, 1.0, dots=False)
    # cordon de colle visible derrière, puis caché par la bande
    if t < T_CO + 0.6: c.poly(rrect(CX, 960, 700, 460, 60), fill=None, outline=mix(BG, (214, 160, 40), 1 - a), w=26)
    rich(c, 520, [("ELLE ", INK), ("CACHE", RED), (" LE CORDON", INK)], 72, eo(prog(t, T_2, T_2 + 0.4)))
    label(c, CX, 1360, "ET LUI DONNE PRISE", 52, INK, eo(prog(t, wt("surface") - 0.2, wt("surface") + 0.2)))

def sc_dots(c, t):
    rich(c, 500, [("MAIS POURQUOI ", INK), ("DES POINTS ?", RED)], 58, eo(prog(t, T_Q, T_Q + 0.4)))
    # bord net : noir plein contre verre clair
    c.poly([(180, 760), (480, 760), (480, 900), (180, 900)], fill=mix(BG, INK, 1))
    c.poly([(480, 760), (900, 760), (900, 900), (480, 900)], fill=mix(BG, (226, 234, 232), 1), outline=mix(BG, INK, 1), w=5)
    if t >= wt("brutal") - 0.3:
        a = eo(prog(t, wt("brutal") - 0.3, wt("brutal") + 0.2))
        c.rline(zig(480, 760, 900, 8, 16), 6, mix(BG, RED, a))
        label(c, 690, 950, "BORD NET : VUE DÉFORMÉE", 36, RED, a, FM)
    # dégradé de points
    if t >= T_DG - 0.3:
        a = eo(prog(t, T_DG - 0.3, T_DG + 0.3))
        c.poly([(180, 1040), (330, 1040), (330, 1180), (180, 1180)], fill=mix(BG, INK, a))
        c.poly([(330, 1040), (900, 1040), (900, 1180), (330, 1180)], fill=mix(BG, (226, 234, 232), a), outline=mix(BG, INK, a), w=5)
        for r in range(6):
            rr = 18 - r * 3
            for k in range(0, 3):
                c.circle((350 + r * 62, 1068 + k * 38 + (r % 2) * 19), max(2, rr), fill=mix(BG, INK, a))
        label(c, 600, 1250, "DÉGRADÉ : TRANSITION DOUCE", 36, INK, a, FM)

def sc_recap(c, t):
    t0 = T_R
    glass_w(c, CX, 960, 700, 470, 1.0)
    checkmark(c, 850, 720, eob(prog(t, t0, t0 + 0.4)) * 1.4)
    rich(c, 560, [("PAS UN DÉFAUT :", INK)], 80, eo(prog(t, T_R - 1.6, T_R - 1.2)))
    rich(c, 1350, [("LE BOUCLIER DE LA COLLE", RED)], 70, eo(prog(t, t0, t0 + 0.4)))

def sc_next(c, t):
    t0 = T_N
    glass_w(c, CX, 735, 420, 280, eo(prog(t, t0 - 0.1, t0 + 0.4)), band=38, dots=False)
    last = lambda w: WORDS[max(i for i, x in enumerate(NW) if x == nrm(w))][1]
    ts, td = last("secret"), last("dans")
    label(c, CX, 990, "UN SECRET D'INGÉNIEUR", 58, INK, eo(prog(t, ts - 0.1, ts + 0.3)))
    label(c, CX, 1085, "DANS CHAQUE OBJET", 58, RED, eo(prog(t, td - 0.1, td + 0.3)))
    subscribe_button(c, t, t0, T_CK)

SCENES = [sc_hook, sc_look, sc_why, sc_glue, sc_hide, sc_dots, sc_recap, sc_next]
beat_of = beat_of_f(BEATS, SCENES)
CUR = [(0.0, 540, 1300), (1.2, 740, 1120), (T_L, 700, 960), (T_P, 540, 1100), (T_1, 560, 1040), (T_2, 600, 1050), (T_Q, 480, 830),
       (T_R, 560, 1000), (T_N - 0.2, 700, 900), (T_CK - 0.25, 540, 1205), (DUR, 540, 1205)]
CLICKS = [T_R, T_CK]
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
    c.text((80, Y), "ÉPISODE 8", FM, 34, RED)
    c.text((80 + tw("ÉPISODE 8  ", FM, 34), Y), "· C'EST FAIT EXPRÈS", FM, 34, GREY)
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
