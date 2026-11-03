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
T_L = wt("regarde"); T_D = wt("dirait"); T_P = wt("pourtant"); T_A = wt("quand"); T_M = wt("mais"); T_BO = wt("bouche")
T_ME = wt("membrane", 1); T_LV = wt("levier"); T_CL = wt("clac"); T_NO = wt("aucun"); T_E = wt("ça"); T_R = wt("frein")
T_N = wt("abonnetoi"); T_CK = we("abonnetoi") + 0.1
BEATS = [0.0, T_L, T_P, T_A, T_NO, T_E, T_R, T_N, 999.0]
EMPH = {nrm(x) for x in ["défaut.", "trou", "minuscule.", "erreur", "plein.", "air", "membrane.", "aspire", "clac", "clapet", "aucun", "capteur,", "électronique.",
                          "éclaboussure", "mousse", "frein", "défaut", "secret", "objet.", "Abonne-toi", "bouche", "levier"]}
HOLE = (820, 950)
TUBE = [(820, 950), (820, 880), (330, 880)]

def spout(c, cx, cy, a=1.0, hole_r=14):
    c.poly(rrect(cx, cy, 640, 120, 50), fill=mix(BG, (214, 214, 210), a), outline=mix(BG, INK, a), w=9)
    c.circle((cx + 230, cy - 60), hole_r, fill=mix(BG, RED, a), outline=mix(BG, INK, a), w=3)

def sc_hook(c, t):
    rich(c, 520, [("CE N'EST PAS", INK)], 92, eo(prog(t, 0.05, 0.5)))
    rich(c, 650, [("UN DÉFAUT", RED)], 118, eo(prog(t, 0.3, 0.8)))
    spout(c, CX, 1000, eo(prog(t, 0.5, 1.0)))
    if t > 1.2:
        a = eo(prog(t, 1.2, 1.6)); arrow(c, (CX + 230, 880 - 20 * (1 - a)), (CX + 230, 925), 7, mix(BG, RED, a), 20)

def sc_look(c, t):
    spout(c, CX, 1000, 1.0, 14 + 10 * eo(prog(t, T_L + 0.4, T_L + 1.4)))
    rich(c, 520, [("UN TROU ", INK), ("MINUSCULE", RED)], 80, eo(prog(t, wt("trou"), wt("trou") + 0.4)))
    if t >= T_D: label(c, CX, 1262, "UNE ERREUR DE FABRICATION ?", 54, INK, eo(prog(t, T_D, T_D + 0.4)))

def diag(c, t, mode="plein"):
    # tuyau avec rétrécissement (effet Venturi)
    top = [(180, 950), (380, 950), (450, 995), (520, 995), (590, 950), (880, 950)]
    c.poly(top + [(880, 1070), (180, 1070)], fill=mix(BG, (214, 214, 210), 1), outline=mix(BG, INK, 1), w=8)
    c.circle(HOLE, 11, fill=mix(BG, RED, 1), outline=mix(BG, INK, 1), w=3)
    # tube de détection vers la chambre à membrane
    c.line(TUBE, 7, mix(BG, INK, 1))
    box(c, 250, 820, 410, 940, STF, 7, INK, 1.0, 8)
    bow = eo(prog(t, T_BO + 0.1, T_ME + 0.3)) if mode == "plein" else 0.0
    mem = [(330 - 26 * bow * math.sin(math.pi * k / 10), 830 + 100 * k / 10) for k in range(11)]
    c.line(mem, 6, mix(BG, RED if bow > 0.05 else INK, 1))
    # clapet : se ferme quand le levier tombe
    cl_ = eo(prog(t, T_LV, T_CL + 0.15)) if mode == "plein" else 0.0
    ytop = 835 + 120 * cl_
    c.line([(330, 930), (230, ytop + 10)], 6, mix(BG, INK, 1))
    box(c, 212, ytop, 250, ytop + 112, (255, 255, 255), 6, RED if cl_ > 0.5 else INK, 1.0, 4)
    # essence qui coule dans le tuyau
    if t < T_CL + 0.1 or mode != "plein":
        for k in range(8):
            x = 280 + ((t * 230 + k * 85) % 580)
            c.circle((x, 1010 + 14 * math.sin(k * 2.1)), 9, fill=mix(BG, (214, 160, 40), 1))
    # air aspiré
    air_on = (T_A + 0.5 <= t < T_BO) if mode == "plein" else (mode == "air")
    if air_on:
        L = [math.hypot(TUBE[i + 1][0] - TUBE[i][0], TUBE[i + 1][1] - TUBE[i][1]) for i in range(2)]
        for k in range(6):
            u = ((t * 0.7 + k / 6) % 1) * sum(L)
            if u < L[0]: p = (TUBE[0][0], TUBE[0][1] + (TUBE[1][1] - TUBE[0][1]) * u / L[0])
            else: p = (TUBE[1][0] + (TUBE[2][0] - TUBE[1][0]) * (u - L[0]) / L[1], TUBE[1][1])
            c.circle(p, 8, outline=mix(BG, RED, 1), w=4)
    # niveau d'essence dans le réservoir : monte jusqu'au trou
    if mode == "plein" and t >= T_M:
        lv = 1180 - 250 * eio(prog(t, T_M + 0.2, T_BO + 0.2))
        c.poly([(700, 1180), (940, 1180), (940, lv), (700, lv)], fill=mix(BG, (236, 205, 130), 1), outline=mix(BG, INK, 1), w=5)
        if t > T_BO + 0.3: label(c, 860, 1236, "PLUS D'AIR", 40, RED, eo(prog(t, T_BO + 0.3, T_BO + 0.7)), FM)
    if mode == "splash":
        for k, (dx, dy) in enumerate(((-22, -26), (4, -34), (26, -20), (-6, -12), (16, -8))):
            c.circle((HOLE[0] + dx, HOLE[1] + dy), 11, fill=mix(BG, (236, 205, 130), eo(prog(t, T_E + 0.3 + 0.1 * k, T_E + 0.6 + 0.1 * k))), outline=mix(BG, INK, 1), w=3)
    if t >= T_CL and mode == "plein":
        a = eob(prog(t, T_CL, T_CL + 0.25)); label(c, 560, 780, "CLAC !", int(120 * a) + 1, RED, 1.0)

def sc_why(c, t):
    spout(c, CX, 1000, 1.0, 24)
    rich(c, 520, [("C'EST LUI QUI ", INK), ("COUPE LE PLEIN", RED)], 66, eo(prog(t, T_P, T_P + 0.4)))

def sc_air(c, t):
    diag(c, t, "plein")
    if t < T_M: lab = "L'ESSENCE COULE : ELLE ASPIRE DE L'AIR"
    elif t < T_ME: lab = "LE RÉSERVOIR EST PLEIN : LE TROU SE BOUCHE"
    else: lab = "ASPIRATION FORTE : LE CLAPET SE FERME"
    label(c, CX, 1310, lab, 38, INK, eo(prog(t, T_A, T_A + 0.4)), FM)
    rich(c, 500, [("AIR ", RED), ("= PASSE", INK)] if t < T_M else [("PLUS D'AIR ", RED), ("= CLAC", INK)], 72, eo(prog(t, T_A, T_A + 0.4)))

def sc_none(c, t):
    t0 = T_NO
    rich(c, 560, [("AUCUN ", RED), ("CAPTEUR", INK)], 100, eo(prog(t, t0, t0 + 0.4)))
    rich(c, 700, [("AUCUNE ", RED), ("ÉLECTRONIQUE", INK)], 84, eo(prog(t, wt("aucune"), wt("aucune") + 0.4)))
    label(c, CX, 1050, "AIR + ASPIRATION", 80, INK, eo(prog(t, wt("juste"), wt("juste") + 0.4)))
    checkmark(c, 880, 800, eob(prog(t, wt("juste"), wt("juste") + 0.4)) * 1.4)

def sc_early(c, t):
    rich(c, 500, [("PARFOIS : ", INK), ("ARRÊT TROP TÔT", RED)], 66, eo(prog(t, T_E, T_E + 0.4)))
    diag(c, t, "splash")
    label(c, CX, 1300, "ÉCLABOUSSURE OU MOUSSE : LE TROU SE BOUCHE", 36, INK, eo(prog(t, T_E + 0.8, T_E + 1.2)), FM)

def sc_recap(c, t):
    t0 = T_R
    spout(c, CX, 960, 1.0, 20)
    checkmark(c, 860, 800, eob(prog(t, t0, t0 + 0.4)) * 1.4)
    rich(c, 560, [("PAS UN DÉFAUT :", INK)], 80, eo(prog(t, T_R - 1.6, T_R - 1.2)))
    rich(c, 1240, [("LE FREIN DU PLEIN", RED)], 84, eo(prog(t, t0, t0 + 0.4)))

def sc_next(c, t):
    t0 = T_N
    spout(c, CX, 735, eo(prog(t, t0 - 0.1, t0 + 0.4)), 14)
    last = lambda w: WORDS[max(i for i, x in enumerate(NW) if x == nrm(w))][1]
    ts, td = last("secret"), last("dans")
    label(c, CX, 990, "UN SECRET D'INGÉNIEUR", 58, INK, eo(prog(t, ts - 0.1, ts + 0.3)))
    label(c, CX, 1085, "DANS CHAQUE OBJET", 58, RED, eo(prog(t, td - 0.1, td + 0.3)))
    subscribe_button(c, t, t0, T_CK)

SCENES = [sc_hook, sc_look, sc_why, sc_air, sc_none, sc_early, sc_recap, sc_next]
beat_of = beat_of_f(BEATS, SCENES)
CUR = [(0.0, 540, 1300), (1.2, 770, 900), (T_L, 700, 960), (T_P, 770, 950), (T_A, 820, 900), (T_M, 330, 880), (T_BO, 820, 950), (T_CL, 230, 950),
       (T_NO, 540, 900), (T_E, 820, 950), (T_R, 560, 1000), (T_N - 0.2, 700, 900), (T_CK - 0.25, 540, 1205), (DUR, 540, 1205)]
CLICKS = [T_CL, T_CK]
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
    c.text((80, Y), "ÉPISODE 5", FM, 34, RED)
    c.text((80 + tw("ÉPISODE 5  ", FM, 34), Y), "· C'EST FAIT EXPRÈS", FM, 34, GREY)
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
