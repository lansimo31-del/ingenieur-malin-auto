"""Planche de captures. Usage : python render/engine/preview.py episodes/ep03-hublots t1 t2 ...  -> work/<ep>/preview.png
Nécessite work/<ep>/words.json (et EP_DUR si besoin)."""
import os, sys
from pathlib import Path
ENG = Path(__file__).resolve().parent; ROOT = ENG.parents[1]
EP = (ROOT / sys.argv[1]).resolve(); WORK = ROOT / "work" / EP.name
os.environ.update(NOIR="1", ACC="18,150,100", MARG="150,205,180", EP_DIR=str(WORK))
TS = [float(x) for x in sys.argv[2:]]
sys.path.insert(0, str(ENG)); sys.argv = ["x", "none"]
import numpy as np
from PIL import Image
import stylo
from stylo import *
from scipy.ndimage import gaussian_filter, map_coordinates
src = WORK / "preview_src.py"; src.write_text((ENG / "head.py").read_text() + "\n" + (EP / "scene.py").read_text())
g = {"__name__": "s"}; exec(stylo.load(str(src)), g)
rng = np.random.default_rng(100); H_, W_ = 1920, 1080
dx = gaussian_filter(rng.standard_normal((H_, W_)), 26); dx = dx / dx.std() * 1.3
dy = gaussian_filter(rng.standard_normal((H_, W_)), 26); dy = dy / dy.std() * 1.3
yy, xx = np.mgrid[0:H_, 0:W_].astype(np.float32); co = [yy + dy, xx + dx]
paper = paper_img(seed=5) / 255; bgc = np.array(PAPER, np.float32) / 255
ims = []
for t in TS:
    imW, imB = run_layers(g, lambda: g["frame"](int(round(t * 30))))
    Wa, Ba = [np.asarray(x.resize((W_, H_), Image.LANCZOS)).astype(np.float32) / 255 for x in (imW, imB)]
    al = map_coordinates(np.clip(np.mean(1 - (Wa - Ba) / bgc, axis=2), 0, 1), co, order=1, mode="nearest")
    pr = np.stack([map_coordinates(Ba[..., c], co, order=1, mode="nearest") for c in range(3)], axis=2)
    ims.append(Image.fromarray((np.clip(paper * (1 - al[..., None]) + pr, 0, 1) * 255).astype(np.uint8)))
cols, w, h = min(4, len(ims)), 360, 640
rows = (len(ims) + cols - 1) // cols
sh = Image.new("RGB", (cols * w, rows * h), (255, 255, 255))
for k, im in enumerate(ims): sh.paste(im.resize((w, h), Image.LANCZOS), ((k % cols) * w, (k // cols) * h))
out = WORK / "preview.png"; sh.save(out); print(out)
