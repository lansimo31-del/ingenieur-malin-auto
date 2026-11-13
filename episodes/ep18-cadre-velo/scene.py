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






# ================= LE CADRE DE VÉLO (épisode 18 · forme contre-intuitive) =================
T_Reg = wt("regarde"); T_Pq = wt("pourquoi"); T_Deux = wt("deux", 0); T_Faux = wt("fausse"); T_Pr = wt("prends")
T_Pous = wt("pousses"); T_Avec = wt("avec"); T_Aj = wt("ajoute"); T_Tr = wt("treillis"); T_Rov = wt("rover")
T_R = wt("plie") - 0.6; T_N = wt("abonnetoi"); T_CK = we("abonnetoi") + 0.1
BEATS = [0.0, T_Reg, T_Pq, T_Deux, T_Faux, T_Pr, T_Pous, T_Avec, T_Aj, T_Tr, T_Rov, T_R, T_N, 999.0]
EMPH = {nrm(x) for x in ["absurde.", "triangles.", "triangles", "triangle", "quadrilatère", "déforme", "losange.", "diagonale", "indéformable.", "treillis", "plie", "secret", "objet.", "pas."]}

def bar(c, a, b, w=14, col=None, p=1.0):
    pen_poly(c, [a, b], p, w, col or INK)
def pin(c, x, y, a=1.0): c.circle((x, y), 11, fill=mix(BG, RED, a), outline=INK, w=4)

R_, B_, S_, H1, H2, F_ = (300, 1090), (470, 1090), (420, 830), (700, 830), (723, 890), (800, 1090)
def bike(c, t, t0, hi=None, wheels=True):
    p = eo(prog(t, t0, t0 + 0.9))
    if wheels:
        for ctr in (R_, F_): c.circle(ctr, 150, outline=mix(BG, GM, p), w=10)
    segs = [(S_, H1), (S_, B_), (H2, B_), (H1, H2), (S_, R_), (B_, R_), (H1, F_)]
    for k, (a, b) in enumerate(segs):
        col = RED if hi == "front" and k < 4 else RED if hi == "rear" and k in (4, 5) else INK
        bar(c, a, b, 16, col, eo(prog(t, t0 + 0.12 * k, t0 + 0.12 * k + 0.6)))
    bar(c, (H1[0] - 10, H1[1]), (H1[0] + 20, H1[1] - 20), 12, INK, p)

def sc_hook(c, t):
    rich(c, 520, [("CETTE FORME", INK)], 88, eo(prog(t, 0.05, 0.5)))
    rich(c, 640, [("A L'AIR ", INK), ("ABSURDE", RED)], 88, eo(prog(t, 0.4, 0.9)))
    bike(c, t, 0.6)
def sc_look(c, t):
    rich(c, 520, [("UN CADRE DE ", INK), ("TUBES", RED)], 70, eo(prog(t, T_Reg, T_Reg + 0.4)))
    bike(c, t, 0, None)
def sc_why(c, t):
    rich(c, 520, [("POURQUOI PAS UNE ", INK), ("BOÎTE PLEINE", RED), (" ?", INK)], 56, eo(prog(t, T_Pq, T_Pq + 0.4)))
    a = eo(prog(t, wt("boîte") - 0.1, wt("boîte") + 0.4))
    c.poly([S_, H1, F_, (470, 1090), B_], fill=mix(BG, (214, 214, 210), a))
    bike(c, t, 0)
def sc_two(c, t):
    rich(c, 520, [("DEUX ", INK), ("TRIANGLES", RED)], 78, eo(prog(t, T_Deux, T_Deux + 0.4)))
    ta = wt("avant,") if False else WORDS[widx("lavant")][1]
    tb = WORDS[widx("larrière")][1]
    bike(c, t, 0, "front" if t < tb - 0.1 else "rear")
    label(c, 560, 1290, "AVANT", 40, RED, eo(prog(t, ta, ta + 0.3)), FM)
    label(c, 330, 1290, "ARRIÈRE", 40, RED, eo(prog(t, tb, tb + 0.3)), FM)
def sc_false(c, t):
    rich(c, 520, [("POUR FAIRE ", INK), ("JOLI ?", RED)], 80, eo(prog(t, T_Faux, T_Faux + 0.4)))
    bike(c, t, 0)
    q = eo(prog(t, wt("non") - 0.1, wt("non") + 0.3))
    if q > 0:
        pen_poly(c, [(120, 760), (960, 1240)], q, 18, RED); label(c, CX, 1330, "NON", 90, RED, q)

SQ = [(330, 800), (750, 800), (750, 1180), (330, 1180)]
def square_state(u):  # u=0 carré, 1 aplati en losange
    sh = 190 * u; dy = 380 * (1 - 0.22 * u)
    return [(330 + sh, 800 + (380 - dy) + 0), (750 + sh, 800 + (380 - dy)), (750, 1180), (330, 1180)]
def draw_quad(c, P, cols=None, a=1.0):
    for k in range(4): bar(c, P[k], P[(k + 1) % 4], 20, INK)
    for q in P: pin(c, q[0], q[1], a)
def sc_take(c, t):
    rich(c, 520, [("4 BANDES, ", INK), ("4 ATTACHES", RED)], 62, eo(prog(t, T_Pr, T_Pr + 0.4)))
    for k in range(4): bar(c, SQ[k], SQ[(k + 1) % 4], 20, INK, eo(prog(t, T_Pr + 0.3 * k, T_Pr + 0.3 * k + 0.5)))
    if t > T_Pr + 1.2:
        for q in SQ: pin(c, q[0], q[1], eo(prog(t, T_Pr + 1.2, T_Pr + 1.6)))
def sc_push(c, t):
    rich(c, 520, [("LE QUADRILATÈRE ", INK), ("SE DÉFORME", RED)], 56, eo(prog(t, T_Pous - 1.6, T_Pous - 1.2)))
    u = eio(prog(t, T_Pous - 0.2, T_Pous + 1.2)); draw_quad(c, square_state(u))
    arrow(c, (1000, 780 + 40), (790, 780 + 40), 12, RED) if u < 0.9 else None
def sc_tri(c, t):
    rich(c, 520, [("UN TRIANGLE ", INK), ("NE SE DÉFORME PAS", RED)], 48, eo(prog(t, T_Avec, T_Avec + 0.4)))
    P = [(540, 800), (800, 1180), (280, 1180)]
    for k in range(3): bar(c, P[k], P[(k + 1) % 3], 20, INK)
    for q in P: pin(c, q[0], q[1])
    s = math.sin(t * 25) * 10 * math.exp(-max(0, t - wt("rien")) * 2) if wt("rien") - 0.3 < t < wt("rien") + 1.2 else 0
    arrow(c, (1000, 900), (840 - abs(s), 900), 12, RED)
    label(c, CX, 1290, "RIEN NE BOUGE", 56, RED, eo(prog(t, wt("rien"), wt("rien") + 0.3)), FM)
def sc_diag(c, t):
    rich(c, 520, [("UNE ", INK), ("DIAGONALE", RED), (" ET C'EST FIGÉ", INK)], 56, eo(prog(t, T_Aj, T_Aj + 0.4)))
    draw_quad(c, SQ)
    bar(c, SQ[3], SQ[1], 20, RED, eo(prog(t, wt("diagonale") - 0.2, wt("diagonale") + 0.6)))
    label(c, CX, 1290, "IL NE BOUGE PLUS", 54, RED, eo(prog(t, wt("bouge") - 0.1, wt("bouge") + 0.3)), FM)
def sc_truss(c, t):
    rich(c, 520, [("UN ", INK), ("TREILLIS", RED)], 84, eo(prog(t, T_Tr, T_Tr + 0.4)))
    n = 5; x0, x1, yb, yt = 100, 980, 1180, 880; dx = (x1 - x0) / n
    k = 0
    for i in range(n):
        xa, xb = x0 + i * dx, x0 + (i + 1) * dx
        up = (xa + dx / 2, yt)
        for a, b in (((xa, yb), up), (up, (xb, yb)), ((xa, yb), (xb, yb))):
            bar(c, a, b, 12, INK, eo(prog(t, T_Tr + 0.12 * k, T_Tr + 0.12 * k + 0.5))); k += 1
    bar(c, (x0 + dx / 2, yt), (x1 - dx / 2, yt), 12, INK, eo(prog(t, T_Tr + 0.9, T_Tr + 1.5)))
    label(c, CX, 1290, "LÉGER MAIS INDÉFORMABLE", 44, RED, eo(prog(t, wt("indéformable") - 0.2, wt("indéformable") + 0.3)), FM)
def sc_rover(c, t):
    rich(c, 520, [("ROVER, ", INK), ("1885", RED)], 90, eo(prog(t, T_Rov - 0.1, T_Rov + 0.4)))
    bike(c, t, T_Rov - 0.6, None)
    label(c, CX, 1330, "CADRE EN LOSANGE : TOUJOURS LA RÉFÉRENCE", 36, RED, eo(prog(t, wt("référence") - 0.4, wt("référence") + 0.2)), FM)
def sc_reveal(c, t):
    bike(c, t, 0, None)
    box(c, 70, 430, 1010, 580, (255, 255, 255), 8, RED, eo(prog(t, T_R - 0.2, T_R + 0.2)), 20)
    label(c, CX, 530, "LE TRIANGLE NE PLIE PAS", 50, RED, eo(prog(t, T_R - 0.1, T_R + 0.3)))
def sc_next(c, t):
    next_scene_factory(lambda c, t, mini=True: [bar(c, a, b, 14, RED) for a, b in (((540, 640), (640, 820)), ((640, 820), (440, 820)), ((440, 820), (540, 640)))])(c, t)
SCENES = [sc_hook, sc_look, sc_why, sc_two, sc_false, sc_take, sc_push, sc_tri, sc_diag, sc_truss, sc_rover, sc_reveal, sc_next]
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
    c.text((80, Y), "ÉPISODE 18", FM, 34, RED)
    c.text((80 + tw("ÉPISODE 18  ", FM, 34), Y), "· FORME CONTRE-INTUITIVE", FM, 34, GREY)
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
