# ================= LA CHASSE D EAU (épisode 7 · devine ce que je construis) =================
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

T1 = wt("première"); T2 = wt("deuxième"); T3 = wt("troisième"); T4 = wt("quatrième"); T_G = wt("tu"); T_AP = wt("appuie")
T_UP = wt("soulève"); T_FL = wt("séchappe"); T_LOW = wt("baisse"); T_REO = wt("rouvre"); T_FULL = wt("plein"); T_REF = wt("referme")
T_R = wt("chasse"); T_L = WORDS[widx("réservoir", 1) - 2][1]; T_N = wt("abonnetoi"); T_CK = we("abonnetoi") + 0.1
BEATS = [0.0, T1, T2, T3, T4, T_G, T_AP, T_R, T_L, T_N, 999.0]
EMPH = {nrm(x) for x in ["Devine", "construis.", "Réponse", "réservoir,", "clapet", "tube", "sécurité.", "flotteur,", "ferme", "deviné", "chasse", "toilettes.", "chaîne",
                          "baisse,", "plein,", "référme", "secret", "objet.", "Abonne-toi", "d'eau,", "monte,"]}

TX0, TX1, TOPY, FLOORY = 220, 860, 640, 1140
WATER = (206, 226, 222)
FULL_Y, EMPTY_Y = 730, 1020
def level(t):
    if t < T_FL: return FULL_Y
    if t < T_REO - 0.2: return FULL_Y + (EMPTY_Y - FULL_Y) * eio(prog(t, T_FL, T_FL + 1.4))
    return EMPTY_Y - (EMPTY_Y - FULL_Y) * eio(prog(t, T_REO - 0.2, T_REF + 0.1))
def flap_angle(t):
    return 55 * eo(prog(t, T_UP, T_UP + 0.35)) * (1 - eio(prog(t, T_FL + 1.3, T_FL + 1.8)))

def tank(c, t, show=True):
    a1 = eob(prog(t, T1, T1 + 0.5)); a2 = eob(prog(t, T2, T2 + 0.5)); a3 = eob(prog(t, T3, T3 + 0.5)); a4 = eob(prog(t, T4, T4 + 0.5))
    if t < T1 - 0.05: return
    S_ = level(t)
    wl = max(S_, TOPY + 30)
    # eau
    aw = eo(prog(t, T1 + 0.2, T1 + 0.9))
    c.poly([(TX0 + 5, wl), (TX1 - 5, wl), (TX1 - 5, FLOORY - 4), (TX0 + 5, FLOORY - 4)], fill=mix(BG, WATER, aw))
    c.line([(TX0 + 5, wl), (TX1 - 5, wl)], 4, mix(BG, GM, aw))
    # parois du réservoir (ouvert en haut) et sol percé
    ink = mix(BG, INK, a1)
    c.line([(TX0, TOPY), (TX0, FLOORY), (320, FLOORY)], 10, ink)
    c.line([(400, FLOORY), (TX1, FLOORY), (TX1, TOPY)], 10, ink)
    if t < T2:
        c.line([(320, FLOORY), (400, FLOORY)], 10, ink)
    # trou + clapet + tuyau de sortie
    if a2 > 0.03:
        c.line([(320, FLOORY), (320, FLOORY + 70)], 8, mix(BG, INK, a2)); c.line([(400, FLOORY), (400, FLOORY + 70)], 8, mix(BG, INK, a2))
        ang = math.radians(flap_angle(t)); hx, hy = 320, FLOORY - 8
        ex, ey = hx + 90 * math.cos(ang), hy - 90 * math.sin(ang)
        c.line([(hx, hy), (ex, ey)], 16, mix(BG, (90, 90, 96), a2)); c.circle((hx, hy), 10, fill=mix(BG, INK, a2))
        # bouton et chaîne
        if t >= T_AP - 0.1:
            pr = 16 * math.sin(math.pi * cl(prog(t, T_AP, T_AP + 0.5))) if t < T_UP else 0
            bx, by = 360, TOPY - 60 + pr
            c.poly(rrect(bx, by, 90, 36, 10), fill=mix(BG, (222, 222, 218), 1), outline=mix(BG, INK, 1), w=6)
            c.line([(bx, by + 18), (ex + 45 * 0, ey - 6)], 4, mix(BG, GM, 1))
    # tube de trop-plein (ouvert en haut)
    if a3 > 0.03:
        top = FLOORY - (FLOORY - 690) * a3
        c.line([(502, top), (502, FLOORY), (538, FLOORY), (538, top)], 8, mix(BG, INK, a3))
    # arrivée d'eau, levier et flotteur
    if a4 > 0.03:
        px, py = 780, 700
        c.line([(px, 560), (px, py - 6)], 12, mix(BG, INK, a4)); c.line([(px - 26, 560), (px + 26, 560)], 10, mix(BG, INK, a4))
        fy = min(S_ - 30, FLOORY - 60)
        fx = 640
        c.line([(px, py), (fx, fy)], 8, mix(BG, INK, a4)); c.circle((px, py), 9, fill=mix(BG, INK, a4))
        c.circle((fx, fy), 40, fill=mix(BG, (245, 245, 240), a4), outline=mix(BG, INK, a4), w=7)
        if T_FL + 1.1 <= t < T_REF:
            for k in range(4):
                yy = py + 8 + ((t * 260 + k * 60) % 240)
                if yy < S_ - 4: c.line([(px + 2, yy), (px + 2, yy + 26)], 7, mix(BG, RED, 1))
    if t > T_FL and t < T_FL + 1.5:                         # chasse : filet d'eau sous le trou
        for k in range(4):
            yy = FLOORY + 10 + ((t * 420 + k * 50) % 120); c.line([(360, yy), (360, yy + 28)], 8, mix(BG, RED, 1))

def sc_hook(c, t):
    rich(c, 520, [("DEVINE CE QUE", INK)], 92, eo(prog(t, 0.05, 0.5)))
    rich(c, 660, [("JE CONSTRUIS", RED)], 112, eo(prog(t, 0.3, 0.8)))
    label(c, CX, 1300, "?", 400, GF, eo(prog(t, 0.6, 1.1)))
    label(c, CX, 790, "RÉPONSE À LA FIN", 64, INK, eo(prog(t, T1 * 0.4, T1 * 0.4 + 0.4)))

def piece(num, txt):
    def f(c, t):
        t0 = BEATS[num]
        rich(c, 520, [("PIÈCE %d" % num, RED)], 84, eo(prog(t, t0, t0 + 0.4)))
        tank(c, t); label(c, CX, 1290, txt, 52, INK, eo(prog(t, t0 + 0.4, t0 + 0.8)))
    return f
sc_p1 = piece(1, "UN GRAND RÉSERVOIR D'EAU")
sc_p2 = piece(2, "UN TROU FERMÉ PAR UN CLAPET")
sc_p3 = piece(3, "UN TUBE OUVERT : LA SÉCURITÉ")
sc_p4 = piece(4, "UN FLOTTEUR AU BOUT D'UN LEVIER")

def sc_guess(c, t):
    rich(c, 520, [("TU AS ", INK), ("DEVINÉ ?", RED)], 92, eo(prog(t, T_G, T_G + 0.4)))
    tank(c, t); label(c, CX, 1330, "?", 150, RED, eo(prog(t, T_G + 0.4, T_G + 0.8)))

def sc_act(c, t):
    rich(c, 520, [("ON ", INK), ("APPUIE", RED)], 84, eo(prog(t, T_AP, T_AP + 0.4)))
    tank(c, t)
    if t < T_LOW - 0.2: lab = "LA CHAÎNE SOULÈVE LE CLAPET"
    elif t < T_REO - 0.3: lab = "LE NIVEAU BAISSE, LE FLOTTEUR AUSSI"
    elif t < T_REF: lab = "L'EAU REVIENT"
    else: lab = "PLEIN : LE FLOTTEUR FERME"
    label(c, CX, 1290, lab, 46, RED if t >= T_REF - 0.1 or t < T_LOW - 0.2 else INK, 1.0)

def sc_reveal(c, t):
    t0 = T_R
    tank(c, t)
    box(c, 90, 1215, 990, 1350, (255, 255, 255), 8, RED, eo(prog(t, t0 - 0.2, t0 + 0.2)), 20)
    label(c, CX, 1310, "UNE CHASSE D'EAU", 86, RED, eo(prog(t, t0 - 0.1, t0 + 0.3)))
    rich(c, 520, [("TES TOILETTES", INK)], 76, eo(prog(t, wt("toilettes"), wt("toilettes") + 0.4)))

def sc_loop(c, t):
    t0 = T_L
    rich(c, 520, [("LE RÉSERVOIR DU DÉBUT", INK)], 62, eo(prog(t, t0, t0 + 0.4)))
    ink = mix(BG, INK, 1)
    c.poly([(TX0 + 5, 730), (TX1 - 5, 730), (TX1 - 5, FLOORY - 4), (TX0 + 5, FLOORY - 4)], fill=WATER)
    c.line([(TX0, TOPY), (TX0, FLOORY), (TX1, FLOORY), (TX1, TOPY)], 10, ink)
    checkmark(c, CX, 930, eob(prog(t, t0 + 0.5, t0 + 0.9)) * 1.6)
    label(c, CX, 1290, "L'EAU PRÊTE POUR LA SUITE", 52, INK, eo(prog(t, wt("garde"), wt("garde") + 0.4)))

def sc_next(c, t):
    t0 = T_N
    a = eo(prog(t, t0 - 0.1, t0 + 0.4))
    c.poly([(TX0 + 200, 640), (TX1 - 200, 640), (TX1 - 200, 800), (TX0 + 200, 800)], fill=mix(BG, WATER, a), outline=mix(BG, INK, a), w=8)
    last = lambda w: WORDS[max(i for i, x in enumerate(NW) if x == nrm(w))][1]
    ts, td = last("secret"), last("dans")
    label(c, CX, 990, "UN SECRET D'INGÉNIEUR", 58, INK, eo(prog(t, ts - 0.1, ts + 0.3)))
    label(c, CX, 1085, "DANS CHAQUE OBJET", 58, RED, eo(prog(t, td - 0.1, td + 0.3)))
    subscribe_button(c, t, t0, T_CK)

SCENES = [sc_hook, sc_p1, sc_p2, sc_p3, sc_p4, sc_guess, sc_act, sc_reveal, sc_loop, sc_next]
beat_of = beat_of_f(BEATS, SCENES)
CUR = [(0.0, 540, 1300), (1.2, 700, 800), (T1, 540, 900), (T2, 360, 1100), (T3, 520, 800), (T4, 700, 800), (T_G, 540, 700), (T_AP, 360, 600), (T_UP, 360, 700),
       (T_LOW, 640, 900), (T_REF, 700, 850), (T_R, 540, 1300), (T_L, 540, 930), (T_N - 0.2, 700, 900), (T_CK - 0.25, 540, 1205), (DUR, 540, 1205)]
CLICKS = [T_AP, T_CK]
draw_cursor = cursor_factory(CUR, CLICKS)
caption = caption_factory(EMPH)

def cam(t):
    b = beat_of(t); a0, a1 = BEATS[b], min(BEATS[b + 1], DUR)
    z = 1.0 + 0.04 * eio(prog(t, a0, a1)) * (b not in (0, 9))
    for tp in BEATS[1:-1]:
        if t >= tp: z *= 1 + 0.03 * math.exp(-(t - tp) * 9)
    return z, 540, 910

def header(c, t):
    Y = 330
    c.text((80, Y), "ÉPISODE 7", FM, 34, RED)
    c.text((80 + tw("ÉPISODE 7  ", FM, 34), Y), "· DEVINE CE QUE JE CONSTRUIS", FM, 34, GREY)
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
