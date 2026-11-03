"""Miniature 1080x1920 selon docs/sources/texte-regles-miniature-et-publication.md.
Usage : python render/engine/thumb.py episodes/ep03-hublots
L'épisode fournit miniature.py avec dessin(c) (coordonnées 1080x1920, centré vers y = 1232, zone y 985-1480)
et episode.yaml : couverture_lignes: [ligne1, MOT-CLÉ, ligne3]."""
import os, sys
from pathlib import Path
import numpy as np, yaml
from PIL import Image, ImageDraw, ImageFont
ENG = Path(__file__).resolve().parent; ROOT = ENG.parents[1]
EP = Path(sys.argv[1]).resolve() if Path(sys.argv[1]).is_absolute() else (ROOT / sys.argv[1]).resolve()
os.environ.update(NOIR="1", ACC="18,150,100", MARG="150,205,180", EP_DIR=str(ROOT / "work" / EP.name))
sys.path.insert(0, str(ENG)); sys.argv = ["x", "none"]
import stylo
from stylo import *
from scipy.ndimage import gaussian_filter, map_coordinates
cfg = yaml.safe_load(open(EP / "episode.yaml", encoding="utf-8")); lines = cfg["couverture_lignes"]
W_, H_ = 1080, 1920
work = ROOT / "work" / EP.name; work.mkdir(parents=True, exist_ok=True)
src = work / "thumb_src.py"
src.write_text((ENG / "head.py").read_text() + "\n" + (EP / "miniature.py").read_text())
g = {"__name__": "s"}; exec(stylo.load(str(src)), g)
def layer():
    im = g["GRID"].crop((0, 0, W_ * g["S"], H_ * g["S"])); g["dessin"](g["C"](im)); return im
imW, imB = run_layers(g, layer)
rng = np.random.default_rng(100)
dx = gaussian_filter(rng.standard_normal((H_, W_)), 26); dx = dx / dx.std() * 1.3
dy = gaussian_filter(rng.standard_normal((H_, W_)), 26); dy = dy / dy.std() * 1.3
yy, xx = np.mgrid[0:H_, 0:W_].astype(np.float32); co = [yy + dy, xx + dx]
Wa, Ba = [np.asarray(x.resize((W_, H_), Image.LANCZOS)).astype(np.float32) / 255 for x in (imW, imB)]
bgc = np.array(PAPER, np.float32) / 255
al = map_coordinates(np.clip(np.mean(1 - (Wa - Ba) / bgc, axis=2), 0, 1), co, order=1, mode="nearest")
pr = np.stack([map_coordinates(Ba[..., c], co, order=1, mode="nearest") for c in range(3)], axis=2)
paper = paper_img(seed=5) / 255
im = Image.fromarray((np.clip(paper, 0, 1) * 255).astype(np.uint8)); d = ImageDraw.Draw(im)
def ctext(t, y, size, fill, font=CAV):
    f = ImageFont.truetype(font, size); w = d.textlength(t, font=f); d.text(((W_ - w) / 2, y), t, font=f, fill=fill)
ink = (20, 20, 24); gr = (18, 150, 100); gy = (95, 95, 100)
ctext("POURQUOI C'EST CONÇU COMME ÇA ?", 295, 44, gy, PAT)
d.line([(150, 360), (930, 360)], fill=(150, 160, 190), width=4)
ctext(lines[0], 440, 125, ink); ctext(lines[1], 545, 200, gr); ctext(lines[2], 770, 125, ink)
ctext("L'INGÉNIEUR MALIN EXPLIQUE", 1530, 44, gy, PAT)
a = np.asarray(im).astype(np.float32) / 255
out = a * (1 - al[..., None]) + pr * al[..., None] * 0 + (pr * np.clip(0.90 + 0.0, 0, 1))[...] * 0
# composition : dessin prémultiplié (pr) sur le fond texte
out = a * (1 - al[..., None]) + pr
im = Image.fromarray((np.clip(out, 0, 1) * 255).astype(np.uint8))
dest = work / "miniature.png"; im.save(dest)
print("miniature ->", dest)
