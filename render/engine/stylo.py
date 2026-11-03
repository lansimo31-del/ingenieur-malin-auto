import sys, math, numpy as np
from PIL import Image, ImageDraw
from scipy.ndimage import gaussian_filter, map_coordinates
PAPER = (252, 250, 244)
P = dict(INK=(24, 44, 150), RED=tuple(int(v) for v in __import__('os').environ.get('ACC','206,42,42').split(',')), GREY=(96, 108, 160), GF=(206, 218, 242), GM=(168, 188, 228), HOLE=(228, 233, 248), PAN=(255, 254, 250), WIN=(236, 239, 249), WHT=(255, 255, 255))
import os
if os.environ.get('NOIR'):
    P.update(INK=(22,22,26), GREY=(105,108,112), GF=(214,222,232), GM=(184,196,214), HOLE=(232,234,236), WIN=(238,240,238))
from pathlib import Path
FONTS = Path(__file__).resolve().parent.parent / "fonts"
CAV = str(FONTS / "caveat700.ttf"); PAT = str(FONTS / "patrick.ttf")
def load(path):
    src = open(path).read()
    hd = "INK = (22, 22, 26); RED = (226, 52, 28); BG = (238, 234, 224)\nGREY = (120, 115, 105); GF = (214, 209, 196); GM = (196, 190, 175); HOLE = (203, 198, 185)"
    assert hd in src
    new = f"INK = {P['INK']}; RED = {P['RED']}; BG = {PAPER}\nGREY = {P['GREY']}; GF = {P['GF']}; GM = {P['GM']}; HOLE = {P['HOLE']}"
    src = src.replace(hd, new).replace("(250, 248, 242)", str(P['PAN'])).replace("(228, 224, 212)", str(P['WIN'])).replace("(255, 255, 255)", str(P['WHT']))
    src = src.replace('FA = "/usr/share/texmf/fonts/opentype/public/tex-gyre/texgyreadventor-bold.otf"', f'FA = "{CAV}"')
    src = src.replace('FM = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"', f'FM = "{PAT}"')
    src = src.replace("_fc[k] = ImageFont.truetype(path, int(size * S))", "_fc[k] = ImageFont.truetype(path, int(size * S * (1.32 if 'caveat' in path else 1.18)))")
    src = src.replace("text((CX, 892), label, FM, 34, BG, anchor=\"ms\")", "text((CX, 892), label, FM, 34, (255, 255, 255), anchor=\"ms\")")
    return src.split("if __name__")[0]
def flat(col, S_=2, W=1080+500, H=1920+500): return Image.new("RGB", (W * S_, H * S_), col)
def run_layers(g, fn):
    outs = []
    for col in (PAPER, (0, 0, 0)):
        g['BG'] = col; g['GRID'] = flat(col)
        outs.append(fn())
    return outs
def paper_img(W=1080, H=1920, seed=3):
    rng = np.random.default_rng(seed)
    im = Image.new("RGB", (W, H), PAPER); d = ImageDraw.Draw(im)
    for y in range(0, H, 30): d.line([(0, y), (W, y)], fill=P['GM'] if y % 120 == 0 else P['GF'], width=2 if y % 120 == 0 else 1)
    for x in range(0, W, 120): d.line([(x, 0), (x, H)], fill=P['GM'], width=2)
    d.line([(66, 0), (66, H)], fill=tuple(int(v) for v in __import__('os').environ.get('MARG','238,150,150').split(',')), width=3)
    a = np.array(im).astype(np.float32)
    n = gaussian_filter(rng.standard_normal((H, W)), 1.1) * 4.0 + gaussian_filter(rng.standard_normal((H, W)), 30) * 9.0
    a += n[..., None]
    return a
def composite(imW, imB, seed=1, amp=2.4):
    W_, B_ = [np.asarray(x.resize((1080, 1920), Image.LANCZOS)).astype(np.float32) / 255 for x in (imW, imB)]
    bg = np.array(PAPER, np.float32) / 255
    alpha = np.clip(np.mean(1 - (W_ - B_) / bg, axis=2), 0, 1)
    prem = B_  # couleur * alpha
    rng = np.random.default_rng(seed)
    H, Wd = alpha.shape
    dx = gaussian_filter(rng.standard_normal((H, Wd)), 26); dx = dx / dx.std() * amp
    dy = gaussian_filter(rng.standard_normal((H, Wd)), 26); dy = dy / dy.std() * amp
    dx += gaussian_filter(rng.standard_normal((H, Wd)), 5) * 1.6; dy += gaussian_filter(rng.standard_normal((H, Wd)), 5) * 1.6
    yy, xx = np.mgrid[0:H, 0:Wd].astype(np.float32)
    co = [yy + dy, xx + dx]
    al = map_coordinates(alpha, co, order=1, mode='nearest')
    pr = np.stack([map_coordinates(prem[..., k], co, order=1, mode='nearest') for k in range(3)], axis=2)
    pen = 0.90 + 0.10 * gaussian_filter(rng.standard_normal((H, Wd)), 14) / 0.05 * 0.05
    pen = np.clip(pen, 0.82, 1.0)
    paper = paper_img(seed=seed + 7) / 255
    out = paper * (1 - al[..., None]) + pr * pen[..., None]
    return Image.fromarray((np.clip(out, 0, 1) * 255).astype(np.uint8))

if __name__ == "__main__":
    which = sys.argv[1]
    sys.argv = ['x', 'none']
    if which == "ep2f":
        g = {"__name__": "s"}; exec(load('/tmp/claude-0/work/ep2/ep2.py'), g)
        imW, imB = run_layers(g, lambda: g['frame'](int(15.8 * 30)))
    elif which == "ep3f":
        g = {"__name__": "s"}; exec(load('/tmp/claude-0/work/ep3/ep3.py'), g)
        imW, imB = run_layers(g, lambda: g['frame'](int(22.0 * 30)))
    else:
        g = {"__name__": "s"}; exec(load('/tmp/claude-0/work/ep2/ep2.py'), g)
        t = open('/tmp/claude-0/work/ep2/thumb2.py').read().split("exec(open('/tmp/claude-0/work/ep2/ep2.py').read().split('if __name__')[0])")[1]
        t = t.replace('im.resize((W, H), Image.LANCZOS).save("/tmp/claude-0/work/ep2/thumb.png")', 'OUTIM = im.resize((W, H), Image.LANCZOS)')
        t = t.replace('"COMMENT MARCHE"', '"COMMENT MARCHE"')
        def mk():
            exec(t, g); return g['OUTIM']
        imW, imB = run_layers(g, mk)
    composite(imW, imB).save(f"/tmp/claude-0/work/pal/stylo{__import__("os").environ.get("TAG","")}_{which}.png")
