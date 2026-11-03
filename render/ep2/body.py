# ================= STYLO À BILLE =================
import json, re
DUR = 53.4
WORDS = json.load(open('/tmp/claude-0/work/stylo2/a/words.json'))
CHUNKS = []; i = 0
while i < len(WORDS):
    j = i
    while j < len(WORDS) - 1 and j - i < 3 and not re.search(r"[.,?:]$", WORDS[j][0]) and sum(len(WORDS[k][0]) + 1 for k in range(i, j + 2)) <= 22: j += 1
    CHUNKS.append((i, j)); i = j + 1
EMPH = {"bille", "bille.", "millimètre.", "roule", "tomberait.", "douille,", "encre.", "grasse", "visqueuse", "lubrifie", "tube,", "réserve.", "clic,", "ressort", "came.", "sort.", "rentre.", "corps,", "clip,", "poche.", "Sept", "éléments.", "bille.", "Abonne-toi.", "ronds."}
FILL1 = (222, 222, 218); STF = (240, 240, 236)
BX, BY, R = 540, 1205, 20
ZC = [1.0]
def stxt(c, x, y, s_, px, col, a=1.0):
    c.text((x, y), s_, FM, px / ZC[0], mix(BG, col, a), anchor='ms')

def checkmark(c, x, y, sc=1.0, a=1.0):
    col = mix(BG, RED, a)
    c.rline([(x - 26 * sc, y + 2 * sc), (x - 8 * sc, y + 22 * sc), (x + 28 * sc, y - 24 * sc)], 13 * sc, col)
def drop(t, t0, dur=0.55, dist=280):
    p = prog(t, t0, t0 + dur)
    return -dist * (1 - eob(p)) if p < 1 else 0.0, p
def ring(c, t, t0, x, y, r0=30, r1=110):
    u = t - t0
    if 0 <= u < 0.5:
        p = eo(u / 0.5); c.circle((x, y), r0 + (r1 - r0) * p, outline=mix(BG, RED, 1 - p), w=6)
def pulse(t, t0, w=0.4):
    u = t - t0
    return math.sin(math.pi * u / w) if 0 <= u < w else 0.0

PRESS = [30.9, 33.6, 35.45]
def sd(t): return 36 * eio(prog(t, 33.7, 34.3)) - 36 * eio(prog(t, 35.55, 36.15))
def press_amt(t): return max(pulse(t, p, 0.45) for p in PRESS)
def cam_phase(t):
    ph = 0.0
    for p in PRESS: ph += eio(prog(t, p + 0.1, p + 0.4))
    return ph

def poly_in(c, pts, fill=None, w=6):
    c.poly(pts, fill=fill, outline=INK, w=w)

# ---- pièces (rendu plus réaliste : ombrages hachurés, reflets) ----
LGREY = (200, 200, 196); MGREY = (150, 150, 148)
def hatch_side(c, yt, yb, xr_f, band=14, step=11, w=2.6, col=None, right=True, a=1.0):
    col = col or INK
    y = yt
    while y < yb:
        x = xr_f(y)
        if right: c.line([(x - band, y + 9), (x - 1, y)], w, mix(BG, col, a))
        else: c.line([(x + band, y + 9), (x + 1, y)], w, mix(BG, col, a))
        y += step
def shade_poly(c, pts, col=LGREY): c.poly(pts, fill=col)

def draw_ball(c, t, off=0.0, a=1.0, sc=1.0, x=None, y0=None):
    x = BX if x is None else x; y = (BY if y0 is None else y0) + off; r = R * sc
    ang = (t * 3.0 if t < 10.3 else 0.0)
    c.circle((x, y), r, fill=mix(BG, MGREY, a))                       # métal sombre
    c.circle((x - r * 0.12, y - r * 0.14), r * 0.86, fill=mix(BG, (246, 246, 244), a))  # lumière
    c.circle((x + r * 0.18, y + r * 0.2), r * 0.42, fill=mix(BG, LGREY, a * 0.9))      # demi-teinte
    c.circle((x, y), r, outline=mix(BG, INK, a), w=3.5)
    c.circle((x - r * 0.4, y - r * 0.42), r * 0.2, fill=mix(BG, (255, 255, 255), a))   # reflet
    c.rline([(x + r * 0.55 * math.cos(ang), y + r * 0.55 * math.sin(ang)), (x + r * 0.8 * math.cos(ang), y + r * 0.8 * math.sin(ang))], 2.2, mix(BG, INK, a * 0.55))

def draw_socket(c, t, dy):
    L = lambda y: 505 + 19 * (y - 1105) / 87
    Rr = lambda y: 575 - 19 * (y - 1105) / 87
    pts = [(505, 1105 + dy), (575, 1105 + dy), (556, 1192 + dy), (524, 1192 + dy)]
    c.poly(pts, fill=(246, 246, 244))
    c.poly([(Rr(1105) - 22, 1105 + dy), (575, 1105 + dy), (556, 1192 + dy), (Rr(1192) - 17, 1192 + dy)], fill=LGREY)   # côté ombré
    hatch_side(c, 1112, 1186, lambda y: Rr(y) , band=15, step=10, w=2.4, col=INK)
    c.line([(L(1115) + 9, 1114 + dy), (L(1180) + 9, 1178 + dy)], 5, (255, 255, 255))   # reflet
    for yy in (1128, 1150):   # gorges d'usinage
        c.line([(L(yy), yy + dy), (Rr(yy), yy + dy)], 3.4, INK)
    poly_in(c, pts, fill=None, w=6)
    c.poly([(520, 1192 + dy), (560, 1192 + dy), (555, 1203 + dy), (525, 1203 + dy)], fill=(246, 246, 244), outline=INK, w=5)   # lèvre qui sertit la bille

def draw_ink_socket(c, f, dy):
    if f <= 0.01: return
    ytop = 1186 - f * 74
    xl = lambda y: 512 + 17 * (y - 1112) / 74
    xr = lambda y: 568 - 17 * (y - 1112) / 74
    c.poly([(xl(ytop), ytop + dy), (xr(ytop), ytop + dy), (551, 1186 + dy), (529, 1186 + dy)], fill=RED)
    c.line([(xl(ytop) + 3, ytop + dy + 3), (xr(ytop) - 3, ytop + dy + 3)], 3, mix(RED, (255, 255, 255), 0.5))   # ménisque

def draw_tube(c, t, dy, fill_f):
    c.poly([(520, 830 + dy), (560, 830 + dy), (560, 1105 + dy), (520, 1105 + dy)], fill=(250, 250, 248), outline=INK, w=6)
    c.poly([(548, 832 + dy), (558, 832 + dy), (558, 1103 + dy), (548, 1103 + dy)], fill=(222, 222, 218))      # ombre du tube
    if fill_f > 0.01:
        yt = 1099 - fill_f * (1099 - 880)
        c.poly([(526, yt + dy), (556, yt + dy), (556, 1099 + dy), (526, 1099 + dy)], fill=RED)
        c.poly([(526, yt + dy), (556, yt + dy), (556, yt + 5 + dy), (526, yt + 5 + dy)], fill=mix(RED, (255, 255, 255), 0.45))
    c.line([(527, 840 + dy), (527, 1095 + dy)], 4, (255, 255, 255))    # reflet plastique
    c.poly([(516, 822 + dy), (564, 822 + dy), (564, 834 + dy), (516, 834 + dy)], fill=LGREY, outline=INK, w=5)   # bague haute

def draw_spring(c, dy, comp=0.0):
    y0, y1 = 925 + dy + comp * 0.5, 1090 + dy
    n = 9
    for k in range(n):
        ya = y0 + (y1 - y0) * k / n; yb = y0 + (y1 - y0) * (k + 0.5) / n; yc = y0 + (y1 - y0) * (k + 1) / n
        c.line([(582, yb), (498, yc)], 3, MGREY)           # fil arrière
        c.line([(498, ya), (582, yb)], 6.5, INK)           # fil avant
        c.line([(499, ya + 2), (581, yb + 2)], 2, (255, 255, 255))
    c.line([(520, y0), (498, y0)], 5, INK); c.line([(560, y1), (582, y1)], 5, INK)

def draw_cam(c, dy, phase):
    c.poly([(506, 760 + dy), (574, 760 + dy), (574, 830 + dy), (506, 830 + dy)], fill=(246, 246, 244), outline=INK, w=6)
    c.poly([(552, 762 + dy), (572, 762 + dy), (572, 828 + dy), (552, 828 + dy)], fill=LGREY)
    for i in range(-1, 5):
        x = 506 + ((i * 20 + phase * 20) % 80)
        if 508 < x < 572: c.line([(x, 772 + dy), (x, 822 + dy)], 3.2, INK)
    c.line([(512, 765 + dy), (512, 825 + dy)], 4, (255, 255, 255))
    zig = [(506 + 8 * k, 830 + dy + (9 if k % 2 else 0)) for k in range(9)]
    c.line(zig, 4.5, INK)         # dents de la came

def draw_button(c, dy, pr):
    d = dy + 26 * pr
    c.poly([(524, 690 + d), (556, 690 + d), (556, 760 + dy), (524, 760 + dy)], fill=(250, 250, 248), outline=INK, w=6)
    c.poly([(546, 692 + d), (555, 692 + d), (555, 758 + dy), (546, 758 + dy)], fill=LGREY)
    c.poly([(506, 650 + d), (574, 650 + d), (574, 690 + d), (506, 690 + d)], fill=(246, 246, 244), outline=INK, w=6)
    c.poly([(556, 652 + d), (572, 652 + d), (572, 688 + d), (556, 688 + d)], fill=LGREY)
    for x in (522, 534, 546, 558): c.line([(x, 656 + d), (x, 684 + d)], 2.2, MGREY)       # stries du poussoir
    c.line([(510, 654 + d), (570, 654 + d)], 3, (255, 255, 255))

def body_pts(): return [(500, 640), (480, 640), (480, 1010), (528, 1214), (552, 1214), (600, 1010), (600, 640), (580, 640)]
def draw_body(c, p, ghost=0.0):
    pts = body_pts()
    if ghost > 0.01:
        for a, b in zip(pts[:-1], pts[1:]):
            L = math.dist(a, b); n = max(2, int(L / 22))
            for k in range(0, n, 2):
                u0, u1 = k / n, min(1, (k + 1) / n)
                c.line([(a[0] + (b[0] - a[0]) * u0, a[1] + (b[1] - a[1]) * u0), (a[0] + (b[0] - a[0]) * u1, a[1] + (b[1] - a[1]) * u1)], 5, mix(BG, GREY, ghost))
    if p > 0.01:
        left = [(528, 1214), (480, 1010), (480, 640), (500, 640)]
        right = [(552, 1214), (600, 1010), (600, 640), (580, 640)]
        for side in (left, right):
            L = [math.dist(side[i], side[i + 1]) for i in range(3)]; tot = sum(L); tgt = tot * cl(p); acc = 0; out = [side[0]]
            for i, l in enumerate(L):
                if acc + l <= tgt: out.append(side[i + 1]); acc += l
                else:
                    u = (tgt - acc) / l; out.append((side[i][0] + (side[i + 1][0] - side[i][0]) * u, side[i][1] + (side[i + 1][1] - side[i][1]) * u)); break
            c.line(out, 9, INK)
        # ombrage par hachures (bord droit) et reflet (bord gauche), qui suivent l'avancement
        ytip = 1214 - p * (1214 - 640)
        xr_f = lambda y: 600 if y < 1010 else 600 - 48 * (y - 1010) / 204
        xl_f = lambda y: 480 if y < 1010 else 480 + 48 * (y - 1010) / 204
        hatch_side(c, max(760, ytip + 6), 1190, xr_f, band=15, step=12, w=2.6, col=INK)
        y = max(660, ytip + 8)
        c.line([(xl_f(y) + 8, y), (xl_f(1000) + 8, 1000)], 5, (255, 255, 255)) if y < 1000 else None
        if p > 0.95:
            c.poly([(481, 700), (599, 700), (599, 745), (481, 745)], fill=mix(BG, RED, 0.9))
            c.line([(486, 708), (594, 708)], 3, mix(RED, (255, 255, 255), 0.5))
            c.poly([(528, 1196), (552, 1196), (554, 1214), (526, 1214)], fill=LGREY, outline=INK, w=4)      # embout conique
def draw_clip(c, p):
    dx = 160 * (1 - eob(p))
    pts = [(603 + dx, 655), (626 + dx, 655), (626 + dx, 905), (614 + dx, 935)]
    c.poly([(603 + dx, 655), (626 + dx, 655), (626 + dx, 905), (614 + dx, 935), (606 + dx, 905), (606 + dx, 665), (603 + dx, 665)], fill=LGREY, outline=INK, w=5)
    c.line([(616 + dx, 664), (616 + dx, 898)], 3, (255, 255, 255))
    c.line([(603 + dx, 670), (626 + dx, 670)], 3, INK)
    c.circle((614 + dx, 937), 7, fill=INK)

# ---- étapes (overlay) ----
STEPS = [(0.1, "", "STYLO À BILLE", "TOUT PART D'UNE SEULE PIÈCE"), (3.3, "1", "LA BILLE", "ELLE ROULE ET DÉPOSE L'ENCRE"), (12.3, "2", "LA DOUILLE", "ELLE RETIENT LA BILLE"),
         (17.3, "3", "L'ENCRE", "GRASSE : ELLE LUBRIFIE ET NE COULE PAS"), (24.6, "4", "LE TUBE", "LA RÉSERVE D'ENCRE"), (27.3, "5", "LE CLIC", "UN RESSORT ET UNE CAME"),
         (37.3, "6", "LE CORPS", "POUR LE TENIR EN MAIN"), (39.9, "7", "LE CLIP", "POUR L'ACCROCHER À LA POCHE"), (42.8, "", "7 ÉLÉMENTS", "TOUT PART D'UNE PETITE BILLE"), (46.8, "", "PROCHAIN OBJET", "")]
def step_overlay(c, t):
    k = None
    for i, s in enumerate(STEPS):
        if t >= s[0]: k = i
    if k is None: return
    s = STEPS[k]; p = eob(prog(t, s[0], s[0] + 0.35)); a = eo(prog(t, s[0], s[0] + 0.25))
    if k == len(STEPS) - 1: return
    y = 470 + (1 - p) * 30
    parts = ([(s[1] + " · ", GREY)] if s[1] else []) + [(s[2], INK)]
    size = 86
    tot = sum(tw(x, FA, size) for x, _ in parts); x0 = 540 - tot / 2
    for txt, col in parts:
        c.text((x0, y), txt, FA, size, mix(BG, col, a), anchor="ls"); x0 += tw(txt, FA, size)
    sz = 52
    while tw(s[3], FM, sz) > 900: sz -= 2
    c.text((540, 548 + (1 - p) * 20), s[3], FM, sz, mix(BG, RED, a), anchor="ms")

def step_dots(c, t):
    for k in range(7):
        x = 700 + 42 * k; done = t >= STEPS[k + 1][0] + 0.8
        c.circle((x, 318), 14, fill=RED if done else None, outline=INK, w=4)

# ---- scène stylo ----
def ballpos(t):
    # position "papier" de la bille (le décor défile pour garder la bille au centre)
    if t < 10.0:
        u = max(0.0, t - 0.4)
        return BX - 70 + 14.5 * u, BY + 14 * math.sin(u * 2.2) - 6
    x0, y0 = BX - 70 + 14.5 * 9.6, BY + 14 * math.sin(9.6 * 2.2) - 6
    return x0, y0

def pen_scene(c, t):
    # trace d'encre : la bille écrit une petite ligne cursive (pas de sol)
    bpx, bpy = ballpos(t if t < 10.0 else 10.0)
    if 0.4 < t < 11.4:
        al = 1 - prog(t, 10.4, 11.3)
        tt_end = min(t, 10.0)
        pp = [ballpos(0.4 + k * 0.1) for k in range(int((tt_end - 0.4) / 0.1) + 1)] + [(bpx, bpy)]
        pts = [(BX + (px - bpx), BY + (py - bpy)) for px, py in pp]
        if len(pts) > 1 and al > 0.02: c.line(pts, 6, mix(BG, RED, al))
    dy = sd(t)
    # --- bille ---
    a_ball = 1.0; off = 0.0; sc = 1.0
    if 10.4 <= t < 12.9:
        u = t - 10.4; off = 70 * min(1, u / 0.6) ** 2; a_ball = 1 - prog(t, 10.8, 11.3)
        if t > 11.6: a_ball = 0
    elif t >= 12.9 and t < 13.4: sc = eob(prog(t, 12.9, 13.35)); off = 0
    ball_args = (off + (dy if t > 33 else 0) if t >= 12.9 else off, a_ball, sc)
    if t < 10.4:
        draw_ball(c, t, 0.0, 1.0, 1.0, BX, BY)
    elif t < 12.9:
        if a_ball > 0.02: draw_ball(c, t, *ball_args)
    if 10.7 <= t < 12.1:
        al = eo(prog(t, 10.7, 11.0)) * (1 - prog(t, 11.8, 12.1))
        stxt(c, BX + 25, BY - 55, "ELLE TOMBE !", 50, RED, al)
    # --- douille ---
    if t >= 12.4:
        o, p = drop(t, 12.4, 0.65, 260)
        draw_socket(c, t, o + dy)
        ring(c, t, 13.05, BX, 1150, 40, 130)
    # --- encre dans la douille ---
    f = eio(prog(t, 17.4, 19.2))
    if t >= 17.4: draw_ink_socket(c, f, dy)
    if 19.9 <= t < 21.5:   # lubrifie : petits éclats autour de la bille
        al = eo(prog(t, 19.9, 20.2)) * (1 - prog(t, 21.1, 21.5))
        for k in range(5):
            an = math.radians(200 + k * 35)
            c.rline([(BX + 30 * math.cos(an), BY + dy + 30 * math.sin(an)), (BX + 52 * math.cos(an), BY + dy + 52 * math.sin(an))], 5, mix(BG, RED, al))
    if 21.7 <= t < 24.3:   # ne coule pas : goutte qui reste
        gp = eob(prog(t, 21.7, 22.2))
        c.circle((BX, BY + 28 + dy), 8 * gp, fill=RED)
        if t > 22.6: checkmark(c, BX + 90, BY - 20, eob(prog(t, 22.6, 22.9)) * 0.9)
    if 23.0 <= t < 24.3:
        al = eo(prog(t, 23.0, 23.3)) * (1 - prog(t, 24.0, 24.3))
        stxt(c, BX - 40, BY + 70, "SÈCHE VITE", 40, RED, al)
    if t >= 12.9 and a_ball > 0.02: draw_ball(c, t, *ball_args)
    # --- tube ---
    if t >= 24.8:
        o, p = drop(t, 24.8, 0.6, 300)
        draw_tube(c, t, o + dy, eio(prog(t, 25.9, 27.0)))
        ring(c, t, 25.4, BX, 970, 30, 130)
    # --- ressort, came, bouton ---
    if t >= 28.4:
        o, p = drop(t, 28.4, 0.6, 280)
        draw_spring(c, o + dy, 10 * press_amt(t))
        ring(c, t, 28.95, BX, 1005, 30, 120)
    if t >= 29.3:
        o, p = drop(t, 29.3, 0.6, 300)
        draw_cam(c, o + dy, cam_phase(t))
        ring(c, t, 29.85, BX, 795, 30, 120)
    if t >= 29.7:
        o, p = drop(t, 29.7, 0.5, 300)
        draw_button(c, o + dy, press_amt(t))
    # fantôme du corps pendant le clic
    gh = eo(prog(t, 33.2, 33.6)) * (1 - eo(prog(t, 36.9, 37.3)))
    if gh > 0.01: draw_body(c, 0, ghost=gh)
    if 33.7 <= t < 35.4:
        al = eo(prog(t, 33.9, 34.2)) * (1 - prog(t, 35.1, 35.4))
        stxt(c, BX + 150, BY + 10, "ELLE SORT", 40, RED, al)
    if 35.6 <= t < 37.0:
        al = eo(prog(t, 35.7, 36.0)) * (1 - prog(t, 36.7, 37.0))
        stxt(c, BX + 150, BY + 10, "ELLE RENTRE", 40, RED, al)
    # flèche de rotation de la came
    if 31.8 <= t < 33.3:
        al = eo(prog(t, 31.8, 32.1)) * (1 - prog(t, 33.0, 33.3))
        c.line(circ_pts(BX, 795, 52, 24, math.radians(200), math.radians(340)), 6, mix(BG, RED, al))
        c.rline([(BX + 51, 773), (BX + 40, 792)], 6, mix(BG, RED, al))
    # --- corps ---
    if t >= 37.5: draw_body(c, eio(prog(t, 37.5, 38.8)))
    # --- clip ---
    if t >= 40.4: draw_clip(c, prog(t, 40.4, 41.2)); ring(c, t, 41.1, 612, 700, 20, 90)
    # --- finale ---
    if t >= 44.8 and t < 47.0:
        pr = 0.5 + 0.5 * math.sin((t - 44.8) * 9) if t < 46.0 else 0
    # anneau de repère autour de la bille (base du stylo)
    if 12.9 <= t < 47.0:
        a = eo(prog(t, 12.9, 13.3))
        pr = 1.0 + 0.10 * pulse(t, 3.9, 0.5) + 0.12 * pulse(t, 45.2, 0.6)
        c.circle((BX, BY + (dy if t > 33 else 0)), 38 * pr, outline=mix(BG, RED, 0.35 * a), w=3)
    if t >= 45.0 and t < 47.0:
        ring(c, t, 45.2, BX, BY, 30, 140)
    if 38.9 <= t < 40.0 and False: pass
    if t > 22.9 and False: pass
    # coche finale (7 éléments)
    if 43.4 <= t < 47.0: checkmark(c, 680, 700, eob(prog(t, 43.4, 43.7)) * 1.5)

# ---- scène suivante ----
def sc_next(c, t):
    a = eo(prog(t, 47.1, 47.5))
    c.text((540, 540), "PROCHAIN OBJET", FA, 78, mix(BG, GREY, a), anchor="ms")
    p = prog(t, 47.5, 48.6)
    cx, cy = 540, 830
    pts = circ_pts(cx, cy, 150, 80, -math.pi / 2, -math.pi / 2 + 2 * math.pi * cl(p))
    if len(pts) > 1 and p > 0: c.line(pts, 9, INK)
    pts2 = circ_pts(cx, cy, 112, 80, -math.pi / 2, -math.pi / 2 + 2 * math.pi * cl(prog(t, 48.0, 48.8)))
    if len(pts2) > 1 and t > 48.0: c.line(pts2, 6, INK)
    if t > 48.4: c.text((540, 1090), "LES HUBLOTS D'AVION", FA, 70, mix(BG, INK, eo(prog(t, 48.4, 48.8))), anchor="ms")
    if t > 48.6: c.text((cx + 235, 800), "?", FA, int(160 * max(0.02, eob(prog(t, 48.6, 48.95)))), RED, anchor="ms")
    if t > 50.1:
        pp = eob(prog(t, 50.1, 50.45)); clicked = t >= 50.6
        pulse_ = 1.0
        if clicked: pulse_ = 1 + 0.08 * math.exp(-(t - 50.6) * 9) * math.cos((t - 50.6) * 25)
        if 50.6 <= t < 50.72: pulse_ = 0.93
        w, h = (500 if not clicked else 400) * pp * pulse_, 84 * pp * pulse_
        if w > 4:
            c.d.rounded_rectangle([(540 - w / 2) * S, (1190 - h / 2) * S, (540 + w / 2) * S, (1190 + h / 2) * S], radius=h / 2 * S, fill=INK if clicked else RED)
            if pp > 0.6: c.text((540, 1204), "ABONNÉ  ✓" if clicked else "@ingenieur.malin", FM, 38, (255, 255, 255), anchor="ms")

# ---- caméra ----
KEYS = [(0, 6.0, 960), (10.0, 5.6, 960), (12.0, 4.4, 1000), (14.0, 3.8, 1010), (17.0, 3.6, 1030), (23.8, 3.4, 1040), (24.75, 1.6, 1230), (27.2, 1.5, 1230),
        (28.8, 1.1, 1210), (37.0, 1.1, 1210), (38.5, 1.0, 1205), (44.9, 1.0, 1205), (45.5, 3.0, 1000), (46.5, 3.0, 1000), (47.0, 1.0, 1205), (53.4, 1.0, 1205)]
PUNCH = [(13.0, 0.04), (25.4, 0.04), (28.9, 0.04), (29.8, 0.04), (30.9, 0.03), (33.6, 0.03), (35.45, 0.03), (38.0, 0.03), (41.1, 0.04)]
def cam(t):
    z = ys = None
    for i in range(len(KEYS) - 1):
        a, b = KEYS[i], KEYS[i + 1]
        if a[0] <= t <= b[0]:
            u = eio(prog(t, a[0], b[0]))
            if b[0] - a[0] < 0.8 and b[1] > a[1] * 1.6: u = eio(u)
            z = a[1] + (b[1] - a[1]) * u; ys = a[2] + (b[2] - a[2]) * u
    if z is None: z, ys = KEYS[-1][1:]
    for tp, amp in PUNCH:
        if t >= tp: z *= 1 + amp * math.exp(-(t - tp) * 9)
    return z, ys
def world2screen(x, y, z, ys):
    bw, bh = W / z, H / z
    x0 = max(0, min(W - bw, 540 - bw / 2)); y0 = max(0, min(H - bh, BY - ys / z))
    return (x - x0) * z, (y - y0) * z
CURW = [(0, 720, 1150), (3.4, 600, 1200), (6.0, 470, 1215), (9.5, 420, 1215), (12.6, 600, 1120), (14.0, 610, 1150), (17.6, 560, 1130), (19.6, 540, 1195), (22.2, 560, 1215),
        (24.9, 600, 1000), (26.4, 560, 900), (28.5, 610, 1010), (29.6, 600, 800), (30.5, 560, 730), (31.0, 540, 670), (32.5, 600, 790), (33.8, 560, 1100), (35.6, 600, 1100),
        (37.6, 640, 900), (38.6, 640, 700), (40.6, 660, 700), (41.9, 640, 860), (43.3, 620, 760), (45.0, 590, 1180), (46.4, 580, 1200), (47.2, 640, 700), (48.6, 700, 830),
        (50.1, 540, 1150), (50.6, 540, 1190), (52.0, 700, 1280), (53.4, 880, 1400)]
CLICKS = [13.0, 25.45, 28.95, 29.85, 30.95, 33.65, 35.5, 38.0, 41.15, 50.6]
def cur_scene(t):
    for i in range(len(CURW) - 1):
        a, b = CURW[i], CURW[i + 1]
        if a[0] <= t <= b[0]:
            u = eio(prog(t, a[0], b[0])); dx, dy = b[1] - a[1], b[2] - a[2]
            return a[1] + dx * u, a[2] + dy * u
    return CURW[-1][1:]
def draw_cursor(c, t, z, ys):
    if t >= 47.0: x, y = cur_scene(t); x, y = world2screen(x, y, 1.0, 1205)
    else: x, y = world2screen(*cur_scene(t), z, ys)
    for ck in CLICKS:
        u = t - ck
        if 0 <= u < 0.45:
            p = eo(u / 0.45); c.circle((x, y), 8 + 40 * p, outline=mix(BG, RED, 1 - p), w=5)
    press = 0.86 if any(0 <= t - ck < 0.12 for ck in CLICKS) else 1.0
    k = 1.25 * press
    pts = [(0, 0), (0, 27), (7, 21), (12, 32), (17, 30), (12, 19), (21, 19)]
    c.poly([(x + 4 + px * k, y + 6 + py * k) for px, py in pts], fill=GM)
    c.poly([(x + px * k, y + py * k) for px, py in pts], fill=(255, 255, 255), outline=INK, w=3.2)

# ---- overlays ----
def header(c, t):
    Y = 330
    c.text((80, Y), "ÉPISODE 2", FM, 34, RED)
    c.text((80 + tw("ÉPISODE 2  ", FM, 34), Y), "· STYLO", FM, 34, GREY)
    c.line([(80, Y + 38), (1000, Y + 38)], 4, GM)
    c.line([(80, Y + 38), (80 + 920 * min(1, t / (DUR - 0.5)), Y + 38)], 8, RED)
CAP_Y = 1400
def caption(c, t):
    idx = None
    for i, (a, b) in enumerate(CHUNKS):
        start = WORDS[a][1]
        nxt = WORDS[CHUNKS[i + 1][0]][1] if i + 1 < len(CHUNKS) else 99
        end = min(WORDS[b][2] + 0.3, nxt)
        if start - 0.02 <= t < end: idx = i
    if idx is None: return
    a, b = CHUNKS[idx]; ws = WORDS[a:b + 1]
    size, lh, maxw = 98, 110, 960
    sp = tw(" ", FA, size)
    lines, cur, curw = [], [], 0
    for k, (w, s0, s1) in enumerate(ws):
        ww = tw(w, FA, size)
        if cur and curw + sp + ww > maxw: lines.append((cur, curw)); cur, curw = [], 0
        curw += (sp if cur else 0) + ww; cur.append((w, s0, s1, ww))
    lines.append((cur, curw))
    cy = CAP_Y - (len(lines) - 1) * lh / 2
    for ln, lw in lines:
        x = 540 - lw / 2
        for w, s0, s1, ww in ln:
            if t >= s0 - 0.01:
                p = prog(t, s0, s0 + 0.10); off = (1 - eo(p)) * 18
                now = s0 <= t < s1 + 0.04
                col = RED if (now or w in EMPH) else INK
                sz = int(size * (1 + 0.08 * (1 - prog(t, s0, s0 + 0.18)))) if now else size
                c.text((x + ww / 2, cy + off), w, FA, sz, mix(BG, col, eo(p)), anchor="ms")
            x += ww + sp
        cy += lh

def frame(i):
    t = i / FPS
    im = GRID.crop((0, 0, W * S, H * S))
    c = C(im)
    z, ys = cam(t); ZC[0] = z
    if t < 47.0: pen_scene(c, t)
    else: sc_next(c, t)
    zz = z if t < 47.0 else 1.0
    bw, bh = W / zz, H / zz
    x0 = max(0, min(W - bw, 540 - bw / 2)); y0 = max(0, min(H - bh, BY - (ys if t < 47.0 else 1205) / zz))
    im2 = im.crop((int(x0 * S), int(y0 * S), int((x0 + bw) * S), int((y0 + bh) * S))).resize((W * S, H * S), Image.LANCZOS)
    c2 = C(im2)
    header(c2, t)
    if t < 46.8: step_dots(c2, t)
    if t < 45.2 or (46.9 <= t < 46.95): step_overlay(c2, t)
    draw_cursor(c2, t, z, ys)
    caption(c2, t)
    # balayage de transition vers la scène suivante
    if 46.75 <= t <= 47.1:
        xf = eio(prog(t, 46.75, 46.92)) * W; xb = eio(prog(t, 46.92, 47.1)) * W
        c2.d.rectangle([xb * S, 0, xf * S, H * S], fill=RED)
    return im2.resize((W, H), Image.LANCZOS)

if __name__ == "__main__":
    for t in [float(x) for x in sys.argv[2:]]:
        frame(int(round(t * FPS))).save(f"/tmp/claude-0/work/stylo2/v/t_{t:05.2f}.png")
