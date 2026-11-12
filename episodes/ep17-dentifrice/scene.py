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





# ================= LE CARRÉ DU DENTIFRICE (épisode 17 · fait exprès) =================
T_Ret = wt("retourne"); T_Tache = wt("tache"); T_Rum = wt("rumeur"); T_Faux = wt("faux"); T_Rep = wt("repère"); T_Cap = wt("capteur")
T_Con = wt("contraster"); T_Box = wt("boîte"); T_R = wt("défaut", 1); T_N = wt("abonnetoi"); T_CK = we("abonnetoi") + 0.1
BEATS = [0.0, T_Ret, T_Tache, T_Rum, T_Rep, T_Cap, T_Con, T_Box, T_R, T_N, 999.0]
EMPH = {nrm(x) for x in ["défaut.", "défaut", "carré", "faux.", "repère", "machine.", "capteur", "couper", "souder", "contraster", "boîte.", "fabrication.", "secret", "objet.", "rumeur"]}
MARKS = [("NOIR", INK), ("VERT", RED), ("BLEU", (70, 110, 190)), ("ROUGE", (205, 60, 50))]

def tube(c, cx, ytop, w, h, mark=RED, ms=70, a=1.0, bgc=(242, 242, 238), crimp=True):
    box(c, cx - w / 2, ytop, cx + w / 2, ytop + h, bgc, 8, INK, a, 18)
    if crimp:
        for k in range(6):
            y = ytop + h - 100 + k * 16
            c.line([(cx - w / 2 + 6, y), (cx + w / 2 - 6, y)], 4, mix(BG, GM, a))
        c.poly([(cx - ms / 2, ytop + h - 70 - ms / 2 + 20), (cx + ms / 2, ytop + h - 70 - ms / 2 + 20), (cx + ms / 2, ytop + h - 70 + ms / 2 + 20), (cx - ms / 2, ytop + h - 70 + ms / 2 + 20)], fill=mix(BG, mark, a))

def sc_hook(c, t):
    rich(c, 520, [("CE N'EST PAS", INK)], 92, eo(prog(t, 0.05, 0.5)))
    rich(c, 650, [("UN DÉFAUT", RED)], 92, eo(prog(t, 0.3, 0.8)))
    a = eo(prog(t, 0.5, 1.0))
    tube(c, CX, 760, 300, 420, RED, 70, a)

def sc_look(c, t):
    p = eo(prog(t, T_Ret, T_Ret + 0.6))
    tube(c, CX, 640, 380, 480, RED, 100, p)
    rich(c, 520, [("TOUT AU BOUT : ", INK), ("UN CARRÉ", RED)], 66, eo(prog(t, T_Ret, T_Ret + 0.4)))
    # lettres des couleurs
    for k, (nm, col) in enumerate(MARKS):
        wd = nrm(nm)
        try: tt = wt(wd)
        except Exception: tt = T_Ret + 1.0 + 0.4 * k
        a = eo(prog(t, tt - 0.1, tt + 0.3))
        x = 150 + k * 260
        c.poly([(x - 36, 1215), (x + 36, 1215), (x + 36, 1287), (x - 36, 1287)], fill=mix(BG, col, a))
        label(c, x, 1175, nm, 30, INK, a, FM)

def sc_what(c, t):
    tube(c, CX, 700, 380, 520, RED, 100)
    rich(c, 520, [("UNE ", INK), ("TACHE ?", RED)], 80, eo(prog(t, T_Tache, T_Tache + 0.4)))
    label(c, 300, 1280, "?", 150, RED, eo(prog(t, wt("code") - 0.1, wt("code") + 0.3)))
    label(c, 780, 1280, "CODE ?", 70, RED, eo(prog(t, wt("code") - 0.1, wt("code") + 0.3)))

def sc_rumor(c, t):
    rich(c, 520, [("LA ", INK), ("RUMEUR", RED)], 84, eo(prog(t, T_Rum, T_Rum + 0.4)))
    a1 = eo(prog(t, wt("noir") - 0.1, wt("noir") + 0.3)); a2 = eo(prog(t, wt("vert") - 0.1, wt("vert") + 0.3))
    c.poly([(150, 800), (270, 800), (270, 920), (150, 920)], fill=mix(BG, INK, a1))
    label(c, 210, 1000, "CHIMIE", 38, INK, a1, FM)
    c.poly([(810, 800), (930, 800), (930, 920), (810, 920)], fill=mix(BG, RED, a2))
    label(c, 870, 1000, "NATUREL", 38, INK, a2, FM)
    label(c, CX, 880, "=", 120, GREY, min(a1, a2))
    q = eo(prog(t, T_Faux, T_Faux + 0.3))
    if q > 0:
        pen_poly(c, [(110, 760), (970, 1040)], q, 16, RED)
        pen_poly(c, [(110, 1040), (970, 760)], q, 16, RED)
        label(c, CX, 1230, "C'EST FAUX", 100, RED, q)

def machine(c, t, t0, beam=False, cut=False):
    tube(c, CX, 640, 340, 520, RED, 90)
    # capteur à gauche, faisceau vers le carré
    box(c, 90, 1010, 220, 1090, (200, 204, 212), 6, INK, 1.0, 8)
    label(c, 155, 1150, "CAPTEUR", 28, INK, 1.0, FM)
    if beam:
        u = eo(prog(t, t0, t0 + 0.5))
        c.line([(220, 1050), (220 + (CX - 45 - 220) * u, 1050)], 7, RED)
    if cut:
        v = eo(prog(t, t0 + 0.6, t0 + 1.0))
        c.line([(CX - 230, 1200), (CX - 230 + 460 * v, 1200)], 9, RED)
        label(c, CX, 1262, "COUPE ET SOUDE ICI", 36, RED, v, FM)

def sc_mark(c, t):
    rich(c, 520, [("UN ", INK), ("REPÈRE", RED), (" POUR LA MACHINE", INK)], 54, eo(prog(t, T_Rep, T_Rep + 0.4)))
    machine(c, t, 0)

def sc_sensor(c, t):
    rich(c, 520, [("UN ", INK), ("CAPTEUR", RED), (" LIT LE CARRÉ", INK)], 58, eo(prog(t, T_Cap, T_Cap + 0.4)))
    machine(c, t, wt("capteur"), True, t >= wt("couper") - 0.3)

def sc_contrast(c, t):
    rich(c, 520, [("LA COULEUR ", INK), ("CONTRASTE", RED)], 70, eo(prog(t, T_Con - 0.4, T_Con + 0.2)))
    a = eo(prog(t, T_Con - 0.2, T_Con + 0.4))
    tube(c, 300, 700, 300, 420, INK, 80, a, (242, 242, 238))
    tube(c, 780, 700, 300, 420, (240, 240, 236), 80, a, (60, 70, 90))
    label(c, 300, 1230, "SOMBRE SUR CLAIR", 30, INK, a, FM); label(c, 780, 1230, "CLAIR SUR SOMBRE", 30, INK, a, FM)
    b = eo(prog(t, wt("fabricant") - 0.1, wt("fabricant") + 0.3))
    label(c, CX, 1310, "CHAQUE FABRICANT CHOISIT", 38, RED, b, FM)

def sc_box(c, t):
    rich(c, 520, [("LES INGRÉDIENTS : ", INK), ("LA BOÎTE", RED)], 58, eo(prog(t, T_Box - 0.5, T_Box + 0.1)))
    a = eo(prog(t, T_Box - 0.3, T_Box + 0.3))
    box(c, 270, 700, 810, 1180, (242, 242, 238), 9, INK, a, 14)
    for k in range(6): c.line([(340, 800 + k * 55), (740 - (k % 3) * 60, 800 + k * 55)], 8, mix(BG, GM, a))
    label(c, CX, 770, "INGRÉDIENTS", 40, RED, a, FM)

def sc_reveal(c, t):
    t0 = T_R
    tube(c, CX, 640, 340, 480, RED, 90)
    box(c, 70, 1230, 1010, 1400, (255, 255, 255), 8, RED, eo(prog(t, t0 - 0.2, t0 + 0.2)), 20)
    label(c, CX, 1345, "UN REPÈRE DE FABRICATION", 56, RED, eo(prog(t, t0 - 0.1, t0 + 0.3)))

def sc_next(c, t):
    t0 = T_N; a = eo(prog(t, t0 - 0.1, t0 + 0.4))
    tube(c, CX, 640, 130, 180, RED, 36, a)
    last = lambda w: WORDS[max(i for i, x in enumerate(NW) if x == nrm(w))][1]
    ts, td = last("secret"), last("dans")
    label(c, CX, 990, "UN SECRET D'INGÉNIEUR", 58, INK, eo(prog(t, ts - 0.1, ts + 0.3)))
    label(c, CX, 1085, "DANS CHAQUE OBJET", 58, RED, eo(prog(t, td - 0.1, td + 0.3)))
    subscribe_button(c, t, t0, T_CK)
SCENES = [sc_hook, sc_look, sc_what, sc_rumor, sc_mark, sc_sensor, sc_contrast, sc_box, sc_reveal, sc_next]
# index des scènes : BEATS a 11 entrées -> on ajoute la scène "box" avant la révélation
beat_of = beat_of_f(BEATS, SCENES)
CUR = [(0.0, 540, 1300), (T_Ret, 540, 950), (T_Tache, 640, 900), (T_Rum, 540, 900), (T_Rep, 540, 1000), (T_Cap, 200, 1050), (T_Con, 540, 900), (T_Box, 540, 900),
       (T_R, 700, 900), (T_N - 0.2, 700, 900), (T_CK - 0.25, 540, 1205), (DUR, 540, 1205)]
CLICKS = [T_R, T_CK]
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
    c.text((80, Y), "ÉPISODE 17", FM, 34, RED)
    c.text((80 + tw("ÉPISODE 17  ", FM, 34), Y), "· CE N'EST PAS UN DÉFAUT", FM, 34, GREY)
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
