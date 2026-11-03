# ================= HUBLOTS D'AVION (épisode 3) =================
# Exécuté après render/engine/head.py (C, mix, eo, eio, eob, cl, prog, tw, FA, FM, INK, RED=vert d'accent, ...).
# Tous les instants viennent de words.json (mots du script alignés sur la voix) : rien n'est codé en dur.
import json, os, re
CX = 540
FILL1 = (222, 222, 218); STF = (240, 240, 236); LG = (205, 205, 200)
WORDS = json.load(open(os.path.join(os.environ['EP_DIR'], 'words.json')))
for i in range(len(WORDS) - 1):                       # fins de mots cohérentes
    WORDS[i][2] = max(WORDS[i][1] + 0.08, min(WORDS[i][2], WORDS[i + 1][1]))

def nrm(w): return re.sub(r"[^a-zàâäçéèêëîïôöùûüÿœ0-9]", "", w.lower())
NW = [nrm(w[0]) for w in WORDS]
def widx(word, nth=0): return [i for i, x in enumerate(NW) if x == nrm(word)][nth]
def wt(word, nth=0): return WORDS[widx(word, nth)][1]          # début du mot
def we(word, nth=0): return WORDS[widx(word, nth)][2]          # fin du mot

# ---------- repères de la voix ----------
T_Q = wt("pas")                                   # « Pas pour le style »
T_P = wt("un", 1)                                 # « Un : la pression »
T_A = wt("deux")                                  # « Deux : les angles »
T_F = wt("une")                                   # « Une fissure minuscule… »
T_H = WORDS[widx("petit") - 1][1]                 # « Trois : le petit trou… »
T_R = WORDS[widx("simple") - 4][1]                # « Trois secrets, pour une simple fenêtre »
T_N = wt("abonnetoi")                             # « Abonne-toi : il y a un secret d'ingénieur dans chaque objet. »
T_CK = we("abonnetoi") + 0.1                      # clic sur le bouton
BEATS = [0.0, T_Q, T_P, T_A, T_F, T_H, T_R, T_N, 999.0]
ROLE_T = [T_P, T_A, T_H]                          # les trois secrets

# ---------- légendes karaoké ----------
CHUNKS = []; i = 0
while i < len(WORDS):
    j = i
    while j < len(WORDS) - 1 and j - i < 3 and not re.search(r"[.,?:]$", WORDS[j][0]) and sum(len(WORDS[k][0]) + 1 for k in range(i, j + 2)) <= 22: j += 1
    CHUNKS.append((i, j)); i = j + 1
EMPH = {nrm(x) for x in ["arrondis", "céder", "trois", "secrets", "pression", "ballon", "angles", "concentre", "pointu,", "fissure",
                          "fatigue", "1954", "cinquante-quatre,", "Comet", "petit", "trou", "extérieure", "secours,", "buée.", "simple", "secret", "objet.", "Abonne-toi"]}

# ---------- éléments dessinés ----------
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
def rrect(cx, cy, w, h, r, n=14):
    r = max(1.0, min(r, w / 2 - 0.5, h / 2 - 0.5)); pts = []
    for (ox, oy, a0) in ((w/2 - r, -h/2 + r, -90), (w/2 - r, h/2 - r, 0), (-w/2 + r, h/2 - r, 90), (-w/2 + r, -h/2 + r, 180)):
        for k in range(n + 1):
            a = math.radians(a0 + 90 * k / n); pts.append((cx + ox + r * math.cos(a), cy + oy + r * math.sin(a)))
    return pts
def window(c, cx, cy, w, h, r, a=1.0, hole=False):
    """hublot vu de face : cadre, cadre intérieur, vitre ; r = rayon des coins (petit = carré, grand = arrondi)"""
    c.poly(rrect(cx, cy, w, h, r), fill=mix(BG, LG, a), outline=mix(BG, INK, a), w=10)
    c.poly(rrect(cx, cy, w * .82, h * .84, r * .8), fill=mix(BG, (242, 242, 238), a), outline=mix(BG, INK, a), w=5)
    c.poly(rrect(cx, cy - 4, w * .69, h * .72, r * .66), fill=mix(BG, (226, 234, 232), a), outline=mix(BG, INK, a), w=4)
    if hole: c.circle((cx, cy + h * .29), 9, fill=mix(BG, RED, a))
CRACK = [(0, 0), (22, -20), (36, -8), (66, -44), (88, -30), (124, -72), (146, -60), (190, -112)]
def crack(c, x0, y0, p, a=1.0, sx=1.0, sy=1.0):
    pen_poly(c, [(x0 + dx * sx, y0 + dy * sy) for dx, dy in CRACK], p, 8, mix(BG, INK, a))
def jet(c, cx, cy, sc=1.0, a=1.0):
    ink = mix(BG, INK, a); f = mix(BG, STF, a)
    c.poly(tf([(-250, -30), (-190, -30), (-250, -120)], cx, cy, 0, 1, 1, sc), fill=f, outline=ink, w=5)
    c.poly(tf([(40, 8), (-70, 8), (-160, 120), (-100, 120)], cx, cy, 0, 1, 1, sc), fill=f, outline=ink, w=5)
    c.poly(tf(rrect(0, 0, 540, 74, 37), cx, cy, 0, 1, 1, sc), fill=f, outline=ink, w=6)
    for k in range(9): c.poly(tf(rrect(-170 + k * 42, -6, 16, 20, 4, 4), cx, cy, 0, 1, 1, sc), fill=mix(BG, (226, 234, 232), a), outline=ink, w=2.5)

# ---------- scènes ----------
def sc_hook(c, t):            # hublot carré qui se fissure, puis arrondi
    rich(c, 505, [("HUBLOTS ARRONDIS :", INK)], 74, eo(prog(t, 0.1, 0.5)))
    rich(c, 635, [("ANTI-FISSURE", RED)], 96, eo(prog(t, 0.3, 0.7)))
    t1 = T_Q * 0.42; t2 = T_Q * 0.62                      # fissure (jusqu'à t1), puis arrondi (t1-t2)
    u = eio(prog(t, t1, t2)); r = 10 + 140 * u
    window(c, CX, 960, 400, 470, r, eo(prog(t, 0.05, 0.4)))
    if t < t2: crack(c, CX + 160, 960 - 215 + 18 * (1 - u), eio(prog(t, 0.9, t1)) * (1 - prog(t, t1, t2)), 1.0)
    if t > t2 + 0.15: checkmark(c, 880, 800, eob(prog(t, t2 + 0.15, t2 + 0.45)) * 1.4)

def sc_q(c, t):               # « pas pour le style » + trois cases
    t0 = T_Q; a = eo(prog(t, t0, t0 + 0.35))
    rich(c, 560, [("PAS POUR LE ", INK), ("STYLE", RED), (" ?", INK)], 80, a)
    for k in range(3):
        x = 240 + 300 * k; p = eob(prog(t, t0 + 0.5 + k * 0.18, t0 + 0.8 + k * 0.18))
        if p > 0.03:
            c.poly(rrect(x, 930, 210 * p, 210 * p, 40), fill=mix(BG, STF, 1), outline=mix(BG, INK, 1), w=7)
            label(c, x, 960, str(k + 1), 120, GF, 1.0, FA)
    if t > t0 + 1.3: rich(c, 1160, [("3 SECRETS", RED)], 110, eo(prog(t, t0 + 1.3, t0 + 1.7)))

def sc_pressure(c, t):        # 1 · la pression : le fuselage gonfle
    t0 = T_P; tb = wt("ballon")
    rich(c, 520, [("1 · ", RED), ("LA PRESSION", INK)], 84, eo(prog(t, t0, t0 + 0.4)))
    br = (1 + 0.075 * eio(prog(t, t0 + 0.6, tb + 0.5)) - 0.05 * eio(prog(t, tb + 1.3, tb + 2.1))) if t < tb + 2.1 else 1.0
    cy, R = 930, 250
    dashed(c, circ_pts(CX, cy, R, 120), 16, 12, 5, mix(BG, GM, 0.9))
    c.poly(circ_pts(CX, cy, R * br, 120), fill=mix(BG, STF, 1), outline=mix(BG, INK, 1), w=10)
    c.line(circ_pts(CX, cy, R * br - 28, 120), 4, mix(BG, GM, 1))
    for k in range(10):                                    # flèches de pression, du centre vers la paroi
        an = k * math.pi / 5 + 0.3; pu = prog(t, t0 + 0.4, t0 + 0.9)
        L0 = 125; L1 = R * br - 55
        if pu > 0.02: arrow(c, (CX + L0 * math.cos(an), cy + L0 * math.sin(an)),
                            (CX + (L0 + (L1 - L0) * pu) * math.cos(an), cy + (L0 + (L1 - L0) * pu) * math.sin(an)), 8, mix(BG, RED, 1), 22)
    label(c, CX, cy + 12, "CABINE", 56, GREY, eo(prog(t, t0 + 0.9, t0 + 1.3)))
    if t > tb: label(c, CX, 1262, "COMME UN BALLON", 62, INK, eo(prog(t, tb, tb + 0.4)))

def stream_y(x, d0, cx, cy, r):
    """ligne de force autour d'un trou de rayon r (analogie d'écoulement) : crowding au bord du trou"""
    dx = x - cx; y = abs(d0) + r * 0.0
    for _ in range(40): y = abs(d0) + r * r * y / (dx * dx + y * y + 1e-6)
    return cy + math.copysign(y, d0)
def sc_angles(c, t):          # 2 · les angles : concentration des contraintes
    t0 = T_A; t3 = wt("trois", 1); tp = wt("pointu"); cy = 930
    rich(c, 520, [("2 · ", RED), ("LES ANGLES", INK)], 84, eo(prog(t, t0, t0 + 0.4)))
    c.poly(rrect(CX, cy, 760, 440, 18), fill=mix(BG, STF, 1), outline=mix(BG, INK, 1), w=8)
    pa = eo(prog(t, t0 + 0.4, t0 + 0.9))
    arrow(c, (150, cy), (150 - 100 * pa, cy), 10, mix(BG, INK, 1), 26); arrow(c, (930, cy), (930 + 100 * pa, cy), 10, mix(BG, INK, 1), 26)
    sq = t >= tp - 0.05                                    # trou carré à partir de « pointu »
    r = 70; r_eff = 86 if sq else 70
    for k, d0 in enumerate([-190, -140, -105, -78, 78, 105, 140, 190]):
        if abs(d0) < r_eff + 2: continue
        pts = [(x, stream_y(x, d0, CX, cy, r_eff)) for x in range(170, 911, 10)]
        pen_poly(c, pts, prog(t, t0 + 0.8 + k * 0.05, t0 + 1.5 + k * 0.05), 6, mix(BG, RED, 0.9))
    if sq: c.poly([(CX - 70, cy - 70), (CX + 70, cy - 70), (CX + 70, cy + 70), (CX - 70, cy + 70)], fill=mix(BG, BG, 1), outline=mix(BG, INK, 1), w=8)
    else:  c.circle((CX, cy), r, fill=mix(BG, BG, 1), outline=mix(BG, INK, 1), w=8)
    if t >= t3 - 0.1 and not sq:
        for yy in (cy - r - 56, cy + r + 56): label(c, CX, yy + 22, "×3", 66, RED, eob(prog(t, t3 - 0.1, t3 + 0.25)))
    if sq:
        for (qx, qy) in ((-70, -70), (70, -70), (-70, 70), (70, 70)):
            u = prog(t, tp, tp + 0.4)
            for k in range(3):
                an = math.atan2(qy, qx) + (k - 1) * 0.35
                c.rline([(CX + qx + 14 * math.cos(an), cy + qy + 14 * math.sin(an)), (CX + qx + (14 + 34 * u) * math.cos(an), cy + qy + (14 + 34 * u) * math.sin(an))], 6, mix(BG, RED, 1))
        label(c, CX, 1262, "COIN POINTU : PIRE", 62, RED, eo(prog(t, tp, tp + 0.4)))
    else:
        label(c, CX, 1262, "FORCE QUI SE CONCENTRE", 58, INK, eo(prog(t, t0 + 1.8, t0 + 2.2)))

def sc_fatigue(c, t):         # la fatigue : une fissure grandit à chaque vol, 1954, Comet
    t0 = T_F; t54 = wt("cinquantequatre"); tc = wt("comet"); td = wt("depuis"); tpo = wt("pointus")
    rich(c, 500, [("LA FATIGUE ", INK), ("DU MÉTAL", RED)], 76, eo(prog(t, t0, t0 + 0.4)))
    if t < t54 - 0.1:
        cy = 900; window(c, CX - 120, cy, 330, 400, 8, 1.0)
        n = int(1 + max(0, t - t0) * 3.2)                  # compteur de vols
        grow = eio(prog(t, t0 + 0.2, t54 - 0.2))
        crack(c, CX - 120 + 130, cy - 185, grow, 1.0, 0.7, 0.7)
        c.poly(rrect(800, 900, 190, 120, 24), fill=mix(BG, STF, 1), outline=mix(BG, INK, 1), w=6)
        label(c, 800, 872, "VOL", 40, GREY, 1.0, FM); label(c, 800, 938, str(n), 62, INK, 1.0)
    elif t < td - 0.1:
        a = eo(prog(t, t54 - 0.1, t54 + 0.3))
        label(c, CX, 760, "1954", 190, RED, a)
        jet(c, CX, 980 - 18 * math.sin((t - t54) * 1.5), 1.0, a)
        if t > tc: label(c, CX, 1230, "DEUX COMET", 76, INK, eo(prog(t, tc, tc + 0.4)))
    else:
        a = eo(prog(t, td - 0.1, td + 0.3)); window(c, CX, 930, 400, 470, 10 + 140 * eio(prog(t, td + 0.1, tpo)), a)
        if t > tpo: checkmark(c, 880, 780, eob(prog(t, tpo, tpo + 0.3)) * 1.4)
        label(c, CX, 1262, "PLUS DE COINS POINTUS", 62, INK, eo(prog(t, td + 0.5, td + 0.9)))

def sc_hole(c, t):            # 3 · le petit trou : trois vitres, une seule encaisse
    t0 = T_H; tv = wt("vitres"); te = wt("lextérieure"); tm = wt("milieu"); tbu = wt("buée")
    rich(c, 500, [("3 · ", RED), ("LE PETIT TROU", INK)], 84, eo(prog(t, t0, t0 + 0.4)))
    X = [400, 540, 680]; y0, y1 = 700, 1100; names = ["EXTÉRIEURE", "MILIEU", "INTÉRIEURE"]
    label(c, 330, 1180, "DEHORS", 44, GREY, eo(prog(t, tv, tv + 0.4)), FM); label(c, 750, 1180, "CABINE", 44, GREY, eo(prog(t, tv, tv + 0.4)), FM)
    for k, x in enumerate(X):
        p = eob(prog(t, tv - 0.1 + k * 0.28, tv + 0.25 + k * 0.28))
        if p < 0.03: continue
        top, bot = y1 - (y1 - y0) * p, y1
        hl = (k == 0 and te - 0.1 <= t < tm - 0.1) or (k == 1 and t >= tm - 0.1 and t < tbu - 0.2)
        col = RED if hl else INK
        if k == 1:                                         # vitre du milieu : percée d'un petit trou près du bas
            c.poly(rrect(x, (top + 1030) / 2, 26, 1030 - top, 6), fill=mix(BG, STF, 1), outline=mix(BG, col, 1), w=6)
            c.poly(rrect(x, 1087, 26, 26, 6), fill=mix(BG, STF, 1), outline=mix(BG, col, 1), w=6)
        else: c.poly(rrect(x, (top + bot) / 2, 26, bot - top, 6), fill=mix(BG, STF, 1), outline=mix(BG, col, 1), w=6)
    if t > tv + 1.0:                                       # l'air de la cabine passe par le trou
        u = eio(prog(t, tv + 1.0, tv + 1.7))
        pen_poly(c, [(770, 1060), (700, 1060), (540, 1060), (470, 1060), (420, 1060)], u, 7, mix(BG, RED, 1))
        if u > 0.9: arrow(c, (440, 1060), (418, 1060), 7, mix(BG, RED, 1), 20)
    if te - 0.1 <= t < tbu - 0.2:
        pa = eo(prog(t, te, te + 0.4))
        for yy in (800, 880, 960): arrow(c, (700 - 90 * pa, yy), (700, yy), 8, mix(BG, RED, 1), 20) if False else arrow(c, (470, yy), (470 - 70 * pa, yy), 8, mix(BG, RED, pa), 20)
        label(c, 330, 660, "ENCAISSE", 46, RED, pa)
    if t >= tm - 0.1: label(c, 640, 660, "SECOURS", 46, RED if t < tbu - 0.2 else GREY, eo(prog(t, tm, tm + 0.4)))
    if tbu - 0.2 <= t < tbu + 1.6:                         # buée qui disparaît
        a = 1 - eo(prog(t, tbu + 0.5, tbu + 1.5))
        for k in range(7):
            x = 430 + 18 * (k % 3) + 40 * (k // 3); y = 930 + 30 * ((k * 5) % 4)
            c.circle((x + 3 * math.sin(t * 3 + k), y), 7, outline=mix(BG, GREY, a * eo(prog(t, tbu - 0.2, tbu + 0.1))), w=3)
        label(c, 540, 1262, "PAS DE BUÉE", 58, INK, eo(prog(t, tbu, tbu + 0.4)))
    elif t < tbu - 0.2: label(c, 540, 1262, "3 VITRES · 1 SEULE ENCAISSE", 56, INK, eo(prog(t, tv + 1.2, tv + 1.6)))

def sc_recap(c, t):           # trois secrets, retour au hublot arrondi (boucle)
    t0 = T_R; names = ["PRESSION", "ANGLES", "PETIT TROU"]
    window(c, CX, 960, 400, 470, 150, eo(prog(t, t0, t0 + 0.5)))
    for k, nme in enumerate(names):
        x = 240 + 300 * k; p = eob(prog(t, t0 + 0.3 + k * 0.2, t0 + 0.6 + k * 0.2))
        if p > 0.02:
            c.circle((x, 560), 62 * p, fill=mix(BG, STF, 1), outline=mix(BG, INK, 1), w=7); checkmark(c, x, 560, 1.0 * p)
            label(c, x, 690, nme, 34, GREY, 1.0, FM)
    label(c, CX, 1262, "3 SECRETS · UNE FENÊTRE", 60, INK, eo(prog(t, t0 + 0.8, t0 + 1.2)))

def sc_next(c, t):            # fin : retour au hublot du début + bouton « abonne-toi » (aucun prochain objet annoncé)
    t0 = T_N
    window(c, CX, 735, 300, 352, 110, eo(prog(t, t0 - 0.1, t0 + 0.4)), hole=True)
    if t > t0 + 0.4: checkmark(c, CX + 190, 615, eob(prog(t, t0 + 0.4, t0 + 0.7)) * 1.2)
    last = lambda w: WORDS[max(i for i, x in enumerate(NW) if x == nrm(w))][1]   # dernière occurrence (« dans » existe plus tôt)
    ts, td = last("secret"), last("dans")
    label(c, CX, 990, "UN SECRET D'INGÉNIEUR", 58, INK, eo(prog(t, ts - 0.1, ts + 0.3)))
    label(c, CX, 1085, "DANS CHAQUE OBJET", 58, RED, eo(prog(t, td - 0.1, td + 0.3)))
    tb = t0 + 0.05; clicked = t >= T_CK
    if t > tb:
        pp = eob(prog(t, tb, tb + 0.35)); pulse = 1.0
        if clicked: pulse = 1 + 0.08 * math.exp(-(t - T_CK) * 9) * math.cos((t - T_CK) * 25)
        if T_CK <= t < T_CK + 0.12: pulse = 0.93
        w, h = (500 if not clicked else 400) * pp * pulse, 84 * pp * pulse
        if w > 4:
            c.d.rounded_rectangle([(CX - w / 2) * S, (1205 - h / 2) * S, (CX + w / 2) * S, (1205 + h / 2) * S], radius=h / 2 * S, fill=INK if clicked else RED)
            if pp > 0.6: c.text((CX, 1219), "ABONNÉ  ✓" if clicked else "@ingenieur.malin", FM, 38, (255, 255, 255), anchor="ms")

SCENES = [sc_hook, sc_q, sc_pressure, sc_angles, sc_fatigue, sc_hole, sc_recap, sc_next]
def beat_of(t):
    for i in range(len(SCENES)):
        if BEATS[i] <= t < BEATS[i + 1]: return i
    return len(SCENES) - 1

# ---------- curseur ----------
CUR = [(0.0, 540, 1300), (1.2, 700, 800), (T_Q * 0.55, 560, 980), (T_Q + 0.4, 540, 900), (T_Q + 1.0, 240, 930), (T_Q + 1.6, 840, 930),
       (T_P + 0.6, 540, 700), (wt("ballon"), 700, 930), (T_A + 0.9, 150, 930), (wt("trois", 1), 540, 870), (wt("pointu"), 470, 860),
       (T_F + 0.5, 520, 740), (wt("cinquantequatre"), 540, 980), (T_H + 0.5, 540, 900), (wt("lextérieure"), 400, 880), (wt("milieu"), 540, 1060),
       (T_R + 0.5, 240, 560), (T_R + 1.1, 840, 560), (T_N - 0.2, 700, 900), (T_CK - 0.25, 540, 1205), (DUR, 540, 1205)]
CLICKS = [T_R + 0.6, T_R + 0.8, T_R + 1.0, T_CK]
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

# ---------- caméra : léger zoom par scène + petit coup à chaque début ----------
def cam(t):
    b = beat_of(t); a0, a1 = BEATS[b], min(BEATS[b + 1], DUR)
    z = 1.0 + 0.07 * eio(prog(t, a0, a1)) * (b not in (0, 7))
    for tp in BEATS[1:-1]:
        if t >= tp: z *= 1 + 0.045 * math.exp(-(t - tp) * 9)
    return z, 540, 910

# ---------- surimpressions ----------
def header(c, t):
    Y = 330
    c.text((80, Y), "ÉPISODE 3", FM, 34, RED)
    c.text((80 + tw("ÉPISODE 3  ", FM, 34), Y), "· HUBLOTS", FM, 34, GREY)
    c.line([(80, Y + 38), (1000, Y + 38)], 4, GM)
    c.line([(80, Y + 38), (80 + 920 * bar(t), Y + 38)], 8, RED)
# Barre de progression. La fin a été refaite seule (3 nov., retour d'Ilan) : avant l'image 1600 (53,33 s), la barre suit
# exactement l'ancienne durée (63,2 s) pour que les segments déjà rendus restent valables, puis rejoint la nouvelle fin.
DUR_V1, T_RACCORD = 63.2, 1600 / 30
def bar(t):
    v0 = T_RACCORD / (DUR_V1 - 0.5)
    if t < T_RACCORD: return t / (DUR_V1 - 0.5)
    return min(1, v0 + (1 - v0) * prog(t, T_RACCORD, DUR - 0.5))
def roles(c, t):
    if t < T_Q: return
    a = eo(prog(t, T_Q, T_Q + 0.4)) * (1 - eo(prog(t, T_N - 0.2, T_N + 0.1)))
    if a <= 0.02: return
    for k in range(3):
        x = 880 + 52 * k; done = t >= ROLE_T[k]
        c.circle((x, 318), 19, fill=mix(BG, RED, a) if done else None, outline=mix(BG, INK, a), w=5)
        if done: c.text((x, 327), str(k + 1), FM, 24, (255, 255, 255), anchor="ms")
CAP_Y = 1470
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
    lines.append((cur, curw)); cy = CAP_Y - (len(lines) - 1) * lh / 2
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

def frame(i):
    t = i / FPS
    im = GRID.crop((0, 0, W * S, H * S)); c = C(im)
    SCENES[beat_of(t)](c, t)
    draw_cursor(c, t)
    z, fx, fy = cam(t); bw, bh = W / z, H / z
    x0 = max(0, min(W - bw, fx - bw / 2)); y0 = max(0, min(H - bh, fy - bh / 2))
    im2 = im.crop((int(x0 * S), int(y0 * S), int((x0 + bw) * S), int((y0 + bh) * S))).resize((W * S, H * S), Image.LANCZOS)
    c2 = C(im2); header(c2, t); roles(c2, t); caption(c2, t)
    return im2.resize((W, H), Image.LANCZOS)
