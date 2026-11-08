# ================= LES BOSSES DES TOUCHES F ET J (épisode 14 · fait exprès) =================
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

T_Reg = wt("regarde"); T_On = wt("on"); T_Mais = wt("mais"); T_Pq = wt("pourquoi"); T_Pose = wt("pose"); T_Mains = wt("mains")
T_Meme = wt("même"); T_R = wt("défaut", 1); T_N = wt("abonnetoi"); T_CK = we("abonnetoi") + 0.1
BEATS = [0.0, T_Reg, T_On, T_Mais, T_Pq, T_Pose, T_Mains, T_Meme, T_R, T_N, 999.0]
EMPH = {nrm(x) for x in ["défaut.", "défaut", "bosses,", "relief.", "index", "repère", "boussole", "doigts.", "secret", "objet.", "malvoyantes.", "erreur", "saleté."]}
HOME = "QSDFGHJKLM"

def keycap(c, cx, cy, s, ch, bump=False, a=1.0, hl=False, fa=None):
    fa = a if fa is None else fa
    box(c, cx - s / 2, cy - s / 2, cx + s / 2, cy + s / 2, fill=(242, 242, 238), w=max(3, int(s / 16)), col=INK, a=a, r=s * 0.12)
    if ch: label(c, cx, cy + s * 0.2, ch, int(s * 0.55), RED if hl else INK, a)
    if bump: c.circle((cx, cy + s * 0.36), s * 0.07, fill=mix(BG, RED, a))

def kx(i, s=88, gap=8, cx=CX): return cx + (i - 4.5) * (s + gap)

def home_row(c, cy, s=88, a=1.0, focus=False, bumps=True):
    for i, ch in enumerate(HOME):
        fj = ch in "FJ"
        keycap(c, kx(i, s), cy, s, ch, bump=bumps and fj, a=a * (0.35 if (focus and not fj) else 1.0), hl=fj and focus)

def finger(c, x, ytip, a=1.0, col=(240, 214, 188), w=46):
    c.poly(rrect(x, ytip - 80, w, 190, w / 2), fill=mix(BG, col, a), outline=mix(BG, INK, a), w=6)

def eye(c, x, y, a=1.0, slash=0.0):
    L = [(x + u, y - 52 * (1 - (u / 100) ** 2)) for u in range(-100, 101, 10)]
    Lo = [(x + u, y + 52 * (1 - (u / 100) ** 2)) for u in range(100, -101, -10)]
    c.poly(L + Lo, fill=mix(BG, (250, 250, 247), a), outline=mix(BG, INK, a), w=7)
    c.circle((x, y), 24, fill=mix(BG, INK, a))
    if slash > 0: pen_poly(c, [(x - 120, y + 90), (x + 120, y - 90)], slash, 14, RED)

def sc_hook(c, t):
    rich(c, 520, [("CE N'EST PAS", INK)], 92, eo(prog(t, 0.05, 0.5)))
    rich(c, 650, [("UN DÉFAUT", RED)], 92, eo(prog(t, 0.3, 0.8)))
    home_row(c, 1030, 88, eo(prog(t, 0.5, 1.0)), bumps=False)
    label(c, CX, 1230, "TON CLAVIER", 40, INK, eo(prog(t, 1.0, 1.5)), FM)

def sc_look(c, t):
    p = eo(prog(t, T_Reg, T_Reg + 0.5))
    keycap(c, 340, 960, 280, "F", True, p); keycap(c, 740, 960, 280, "J", True, p)
    rich(c, 520, [("DEUX PETITES ", INK), ("BOSSES", RED)], 76, eo(prog(t, wt("deux") - 0.1, wt("deux") + 0.4)))
    label(c, CX, 1230, "SUR LE F ET SUR LE J", 44, INK, eo(prog(t, wt("sur") - 0.1, wt("sur") + 0.3)), FM)

def sc_err(c, t):
    keycap(c, 340, 960, 240, "F", True); keycap(c, 740, 960, 240, "J", True)
    rich(c, 520, [("UN ", INK), ("DÉFAUT ?", RED)], 80, eo(prog(t, T_On, T_On + 0.4)))
    label(c, 340, 1210, "ERREUR ?", 52, RED, eo(prog(t, wt("erreur") - 0.1, wt("erreur") + 0.3)))
    label(c, 740, 1210, "SALETÉ ?", 52, RED, eo(prog(t, wt("saleté") - 0.1, wt("saleté") + 0.3)))

def sc_non(c, t):
    home_row(c, 960, 88, 1.0, focus=True)
    rich(c, 520, [("MAIS ", INK), ("NON", RED)], 90, eo(prog(t, T_Mais, T_Mais + 0.4)))
    label(c, CX, 1150, "LES SEULES LETTRES", 48, INK, eo(prog(t, wt("seules") - 0.1, wt("seules") + 0.3)))
    label(c, CX, 1230, "AVEC UN RELIEF", 52, RED, eo(prog(t, wt("relief") - 0.3, wt("relief") + 0.1)))

def sc_why(c, t):
    home_row(c, 900, 88, 1.0, focus=True)
    rich(c, 520, [("POURQUOI ", INK), ("ELLES ?", RED)], 80, eo(prog(t, T_Pq, T_Pq + 0.4)))
    label(c, CX, 1230, "?", 240, GF, eo(prog(t, T_Pq + 0.2, T_Pq + 0.7)))

def sc_index(c, t):
    p = eo(prog(t, T_Pose, T_Pose + 0.6))
    home_row(c, 1010, 88)
    iF, iJ = HOME.index("F"), HOME.index("J")
    finger(c, kx(iF), 1010 - 50 - 150 * (1 - p) + 20, p); finger(c, kx(iJ), 1010 - 50 - 150 * (1 - p) + 20, p)
    rich(c, 520, [("LES ", INK), ("INDEX", RED), (" DESSUS", INK)], 76, eo(prog(t, T_Pose, T_Pose + 0.4)))
    label(c, kx(iF) - 40, 1230, "INDEX GAUCHE", 34, INK, eo(prog(t, wt("gauche") - 0.1, wt("gauche") + 0.3)), FM)
    label(c, kx(iJ) + 40, 1290, "INDEX DROIT", 34, INK, eo(prog(t, wt("droit") - 0.1, wt("droit") + 0.3)), FM)
    q = eo(prog(t, wt("autres"), wt("autres") + 0.6))
    for i in (0, 1, 2, 6, 7, 8, 9):
        if q > 0: finger(c, kx(i), 1010 - 50 - 150 * (1 - q) + 20, q * 0.75, col=(244, 226, 208))

def sc_hands(c, t):
    home_row(c, 1010, 88)
    for i in (0, 1, 2, 3, 6, 7, 8, 9): finger(c, kx(i), 1010 - 30, 0.9 if i in (3, 6) else 0.7, col=(240, 214, 188) if i in (3, 6) else (244, 226, 208))
    rich(c, 520, [("MAINS ", INK), ("EN PLACE", RED)], 76, eo(prog(t, T_Mains, T_Mains + 0.4)))
    ey = eo(prog(t, wt("sans") - 0.1, wt("sans") + 0.3))
    if ey > 0: eye(c, CX, 720, ey, prog(t, wt("regardes"), wt("regardes") + 0.3))
    label(c, CX, 1290, "SANS REGARDER", 52, RED, eo(prog(t, wt("regardes") - 0.1, wt("regardes") + 0.3)))

def sc_pad(c, t):
    rich(c, 520, [("LE MÊME ", INK), ("REPÈRE", RED)], 80, eo(prog(t, T_Meme, T_Meme + 0.4)))
    nums = "789456123"
    for k, ch in enumerate(nums):
        r, q = divmod(k, 3)
        five = ch == "5"
        keycap(c, CX + (q - 1) * 140, 780 + r * 140, 120, ch, bump=five and t > wt("cinq") - 0.1, a=eo(prog(t, T_Meme + 0.1, T_Meme + 0.5)) if not five else 1.0, hl=five and t > wt("cinq") - 0.1)
    label(c, CX, 1280, "AIDE LES MALVOYANTS", 48, INK, eo(prog(t, wt("malvoyantes") - 0.6, wt("malvoyantes") - 0.2)), FM)

def sc_recap(c, t):
    t0 = T_R
    home_row(c, 930, 88, 1.0)
    checkmark(c, 850, 700, eob(prog(t, t0, t0 + 0.4)) * 1.4)
    rich(c, 520, [("PAS UN DÉFAUT :", INK)], 84, eo(prog(t, t0 - 0.2, t0 + 0.3)))
    rich(c, 1180, [("UNE BOUSSOLE", RED)], 62, eo(prog(t, wt("boussole") - 0.1, wt("boussole") + 0.3)))
    rich(c, 1260, [("POUR TES DOIGTS", INK)], 62, eo(prog(t, wt("doigts", 1) - 0.2, wt("doigts", 1) + 0.2)))

def sc_next(c, t):
    t0 = T_N
    a = eo(prog(t, t0 - 0.1, t0 + 0.4))
    keycap(c, CX - 90, 735, 150, "F", True, a); keycap(c, CX + 90, 735, 150, "J", True, a)
    last = lambda w: WORDS[max(i for i, x in enumerate(NW) if x == nrm(w))][1]
    ts, td = last("secret"), last("dans")
    label(c, CX, 990, "UN SECRET D'INGÉNIEUR", 58, INK, eo(prog(t, ts - 0.1, ts + 0.3)))
    label(c, CX, 1085, "DANS CHAQUE OBJET", 58, RED, eo(prog(t, td - 0.1, td + 0.3)))
    subscribe_button(c, t, t0, T_CK)

SCENES = [sc_hook, sc_look, sc_err, sc_non, sc_why, sc_index, sc_hands, sc_pad, sc_recap, sc_next]
beat_of = beat_of_f(BEATS, SCENES)
CUR = [(0.0, 540, 1300), (T_Reg, 340, 1000), (T_On, 740, 1000), (T_Mais, 540, 1000), (T_Pq, 640, 900), (T_Pose, 340, 1010), (T_Mains, 540, 1010),
       (T_Meme, 540, 900), (T_R, 700, 900), (T_N - 0.2, 700, 900), (T_CK - 0.25, 540, 1205), (DUR, 540, 1205)]
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
    c.text((80, Y), "ÉPISODE 14", FM, 34, RED)
    c.text((80 + tw("ÉPISODE 14  ", FM, 34), Y), "· CE N'EST PAS UN DÉFAUT", FM, 34, GREY)
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
