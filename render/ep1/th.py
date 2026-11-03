import math, sys, wave, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont

W, H, S, FPS = 1080, 1920, 2, 30
DUR = 26.3
INK = (22, 22, 26); RED = (226, 52, 28); BG = (238, 234, 224)
GREY = (120, 115, 105); GF = (214, 209, 196); GM = (196, 190, 175); HOLE = (203, 198, 185)
FA = "/usr/share/texmf/fonts/opentype/public/tex-gyre/texgyreadventor-bold.otf"
FM = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"

# ---------- envelope de la voix ----------
def load_env():
    w = wave.open("/tmp/claude-0/work/voice.wav")
    sr = w.getframerate(); n = w.getnframes(); ch = w.getnchannels()
    a = np.frombuffer(w.readframes(n), dtype=np.int16).astype(np.float32) / 32768
    if ch > 1: a = a.reshape(-1, ch).mean(1)
    win = int(sr * 0.04)
    k = int(len(a) / (sr / FPS)) + 2
    e = np.zeros(k)
    for i in range(k):
        s = int(i * sr / FPS); seg = a[s:s + win]
        e[i] = np.sqrt((seg ** 2).mean()) if len(seg) else 0
    e = e / (np.percentile(e, 95) + 1e-6)
    e = np.clip(e, 0, 1)
    sm = np.convolve(e, [0.25, 0.5, 0.25], mode="same")
    return sm
ENV = load_env()
def env(t):
    x = t * FPS
    if x < 0: return 0.0
    i = int(x); f = x - i
    if i + 1 >= len(ENV): return 0.0
    return float(ENV[i] * (1 - f) + ENV[i + 1] * f)

# ---------- utils ----------
def cl(x): return max(0.0, min(1.0, x))
def prog(t, a, b): return cl((t - a) / (b - a))
def eo(x): return 1 - (1 - x) ** 3
def eio(x): return 4 * x ** 3 if x < .5 else 1 - (-2 * x + 2) ** 3 / 2
def eob(x):
    c1 = 1.70158; c3 = c1 + 1
    return 1 + c3 * (x - 1) ** 3 + c1 * (x - 1) ** 2
def mix(a, b, t): return tuple(int(a[i] * (1 - t) + b[i] * t) for i in range(3))
def fade(col, a): return mix(BG, col, cl(a))

_fc = {}
def font(path, size):
    k = (path, size)
    if k not in _fc: _fc[k] = ImageFont.truetype(path, int(size * S))
    return _fc[k]
def tw(s, path, size): return font(path, size).getlength(s) / S

class C:
    def __init__(self, im): self.im = im; self.d = ImageDraw.Draw(im)
    def P(self, p): return (p[0] * S, p[1] * S)
    def line(self, pts, w, col):
        self.d.line([self.P(p) for p in pts], fill=col, width=max(1, int(w * S)), joint="curve")
    def rline(self, pts, w, col):
        self.line(pts, w, col)
        for p in (pts[0], pts[-1]): self.circle(p, w / 2, fill=col)
    def poly(self, pts, fill=None, outline=None, w=0):
        pp = [self.P(p) for p in pts]
        if fill is not None: self.d.polygon(pp, fill=fill)
        if outline is not None:
            self.d.line(pp + pp[:2], fill=outline, width=max(1, int(w * S)), joint="curve")
    def circle(self, c, r, fill=None, outline=None, w=0):
        if r <= 0: return
        box = [(c[0] - r) * S, (c[1] - r) * S, (c[0] + r) * S, (c[1] + r) * S]
        self.d.ellipse(box, fill=fill, outline=outline, width=max(1, int(w * S)) if outline else 0)
    def text(self, xy, s, path, size, col, anchor="ls"):
        self.d.text((xy[0] * S, xy[1] * S), s, font=font(path, size), fill=col, anchor=anchor)

def dashed(c, pts, dash, gap, w, col, closed=False):
    pts = list(pts) + ([pts[0]] if closed else [])
    for a, b in zip(pts[:-1], pts[1:]):
        L = math.dist(a, b)
        if L == 0: continue
        ux, uy = (b[0] - a[0]) / L, (b[1] - a[1]) / L
        d = 0
        while d < L:
            e = min(d + dash, L)
            c.line([(a[0] + ux * d, a[1] + uy * d), (a[0] + ux * e, a[1] + uy * e)], w, col)
            d += dash + gap

def circ_pts(cx, cy, r, n=90, a0=0, a1=2 * math.pi):
    return [(cx + r * math.cos(a0 + (a1 - a0) * i / n), cy + r * math.sin(a0 + (a1 - a0) * i / n)) for i in range(n + 1)]

def tf(pts, cx, cy, rot=0, sx=1, sy=1, sc=1):
    ca, sa = math.cos(rot), math.sin(rot)
    out = []
    for x, y in pts:
        x, y = x * sx * sc, y * sy * sc
        out.append((cx + x * ca - y * sa, cy + x * sa + y * ca))
    return out

# ---------- fond ----------
def make_grid():
    gw, gh = (W + 450) * S, (H + 450) * S
    im = Image.new("RGB", (gw, gh), BG); d = ImageDraw.Draw(im)
    for i in range(0, W + 451, 90):
        col = GM if i % 450 == 0 else GF
        d.line([(i * S, 0), (i * S, gh)], fill=col, width=2 * S // 2 + 1)
    for j in range(0, H + 451, 90):
        col = GM if j % 450 == 0 else GF
        d.line([(0, j * S), (gw, j * S)], fill=col, width=2 * S // 2 + 1)
    return im
GRID = make_grid()

# ---------- elements ----------
def draw_hole_circle(c, cx, cy, r, a=1.0):
    c.circle((cx, cy), r, fill=mix(BG, HOLE, a))
    dashed(c, circ_pts(cx, cy, r, 120), 16, 12, 6, mix(BG, GREY, a))

def draw_hole_square(c, cx, cy, s, a=1.0):
    h = s / 2
    pts = [(cx - h, cy - h), (cx + h, cy - h), (cx + h, cy + h), (cx - h, cy + h)]
    c.poly(pts, fill=mix(BG, HOLE, a))
    dashed(c, pts, 16, 12, 6, mix(BG, GREY, a), closed=True)

def lid_circle(c, cx, cy, R, spin=0, rot=0, sy=1.0, sc=1.0, a=1.0, shadow=0):
    base = circ_pts(0, 0, R, 90)
    if shadow:
        c.poly(tf(base, cx + shadow, cy + shadow * 1.2, rot, 1, sy, sc), fill=mix(BG, GM, a))
    c.poly(tf(base, cx, cy, rot, 1, sy, sc), fill=mix(BG, BG, 1), outline=mix(BG, INK, a), w=9)
    c.line(tf(circ_pts(0, 0, R * 0.82, 90), cx, cy, rot, 1, sy, sc), 4, mix(BG, INK, a))
    cs, sn = math.cos(spin), math.sin(spin)
    for k in (-0.5, -0.25, 0, 0.25, 0.5):
        y = k * R
        x = math.sqrt(max(0, (R * 0.8) ** 2 - y ** 2))
        seg = [(-x * cs - y * sn, -x * sn + y * cs), (x * cs - y * sn, x * sn + y * cs)]
        c.line(tf(seg, cx, cy, rot, 1, sy, sc), 4, mix(BG, INK, a))
    mk = (0.64 * R * cs, 0.64 * R * sn)
    mp = tf([mk], cx, cy, rot, 1, sy, sc)[0]
    c.circle(mp, 11 * sc, fill=mix(BG, RED, a))

def lid_square(c, cx, cy, L, rot=0, sy=1.0, sc=1.0, a=1.0):
    h = L / 2
    sq = [(-h, -h), (h, -h), (h, h), (-h, h)]
    c.poly(tf(sq, cx, cy, rot, 1, sy, sc), fill=BG, outline=mix(BG, INK, a), w=9)
    k = h * 0.82
    c.poly(tf([(-k, -k), (k, -k), (k, k), (-k, k)], cx, cy, rot, 1, sy, sc), outline=mix(BG, INK, a), w=4)
    for q in (-0.5, -0.25, 0, 0.25, 0.5):
        y = q * L * 0.82
        c.line(tf([(-k * 0.92, y), (k * 0.92, y)], cx, cy, rot, 1, sy, sc), 4, mix(BG, INK, a))
    c.circle(tf([(0.26 * L, -0.26 * L)], cx, cy, rot, 1, sy, sc)[0], 11 * sc, fill=mix(BG, RED, a))

def checkmark(c, x, y, sc=1.0, a=1.0):
    col = mix(BG, RED, a)
    pts = [(x - 26 * sc, y + 2 * sc), (x - 8 * sc, y + 22 * sc), (x + 28 * sc, y - 24 * sc)]
    c.rline(pts, 13 * sc, col)

def stamp(c, s, center, angle, scale, alpha=1.0, size=64):
    f = font(FM, size)
    tw_ = int(f.getlength(s)); pad = 26 * S
    wd, ht = tw_ + 2 * pad, int(size * S * 1.0) + 2 * pad
    lay = Image.new("RGBA", (wd, ht), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    col = RED + (int(255 * alpha),)
    d.rectangle([0, 0, wd - 1, ht - 1], outline=col, width=9 * S // 2 + 1, fill=BG + (int(235 * alpha),))
    d.text((wd / 2, ht / 2), s, font=f, fill=col, anchor="mm")
    lay = lay.rotate(angle, expand=True, resample=Image.BICUBIC)
    nw, nh = max(1, int(lay.width * scale)), max(1, int(lay.height * scale))
    lay = lay.resize((nw, nh), Image.BICUBIC)
    c.im.paste(lay, (int(center[0] * S - nw / 2), int(center[1] * S - nh / 2)), lay)

# ---------- timeline (temps réels de la voix Enzo) ----------

import random
def stone(c, cx, cy, r, seed, fill):
    rnd = random.Random(seed); n = rnd.choice([6, 7, 8])
    pts = []
    for k in range(n):
        a = 2 * math.pi * k / n + rnd.uniform(-0.25, 0.25)
        rr = r * rnd.uniform(0.72, 1.12)
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a) * 0.82))
    c.poly(pts, fill=fill, outline=INK, w=5)
    # arête interne pour le côté "cassé"
    c.line([pts[0], (cx + (pts[0][0] - cx) * 0.2, cy + (pts[0][1] - cy) * 0.2), pts[n // 2]], 3, GREY)

def rail_section(c, x, ytop):
    c.poly([(x - 48, ytop), (x + 48, ytop), (x + 48, ytop + 30), (x - 48, ytop + 30)], fill=(255, 255, 255), outline=INK, w=6)
    c.poly([(x - 12, ytop + 30), (x + 12, ytop + 30), (x + 12, ytop + 100), (x - 12, ytop + 100)], fill=(255, 255, 255), outline=INK, w=6)
    c.poly([(x - 60, ytop + 100), (x + 60, ytop + 100), (x + 60, ytop + 124), (x - 60, ytop + 124)], fill=(255, 255, 255), outline=INK, w=6)

def thumb():
    im = Image.new("RGB", (W * S, H * S), BG); c = C(im)
    c.text((540, 330), "POURQUOI C'EST CONÇU COMME ÇA ?", FM, 34, GREY, anchor="ms")
    c.line([(150, 362), (930, 362)], 5, GM)
    c.text((540, 560), "POURQUOI DES", FA, 100, INK, anchor="ms")
    c.text((540, 720), "CAILLOUX", FA, 160, RED, anchor="ms")
    c.text((540, 870), "SOUS LES RAILS ?", FA, 92, INK, anchor="ms")
    # coupe de voie
    ys = 1060
    for x in (330, 750): rail_section(c, x, ys)
    c.poly([(150, ys + 124), (930, ys + 124), (930, ys + 184), (150, ys + 184)], fill=(255, 255, 255), outline=INK, w=7)
    c.text((540, ys + 166), "TRAVERSE", FM, 30, GREY, anchor="ms")
    rnd = random.Random(4)
    row = 0
    for y in (ys + 232, ys + 300, ys + 366):
        x = 130 + (row % 2) * 45
        while x < 960:
            r = rnd.uniform(36, 48)
            stone(c, x, y, r, rnd.randint(0, 9999), HOLE)
            x += 90
        row += 1
    # curseur qui pointe une pierre
    px, py = 640, ys + 318
    pts = [(0, 0), (0, 27), (7, 21), (12, 32), (17, 30), (12, 19), (21, 19)]
    k = 1.8
    c.poly([(px + 5 + a * k, py + 8 + b * k) for a, b in pts], fill=GM)
    c.poly([(px + a * k, py + b * k) for a, b in pts], fill=(255, 255, 255), outline=INK, w=4)
    c.text((540, 1560), "L'INGÉNIEUR MALIN EXPLIQUE", FM, 34, GREY, anchor="ms")
    return im.resize((W, H), Image.LANCZOS)
