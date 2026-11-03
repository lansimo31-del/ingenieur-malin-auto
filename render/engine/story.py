"""Stories Instagram 1080x1920 de l'épisode (même DA que les miniatures : papier Seyès, encre noire, accent vert).
Usage : python render/engine/story.py episodes/ep03-hublots
L'épisode fournit stories.yaml (liste de 2 stories) et miniature.py (dessin(c), réutilisé au centre de l'image).
Chaque story : {id, heure, entete, question: [lignes], mot_vert, choix: [..] (optionnel), pied}.
Les stickers interactifs ne passent pas par l'API : la question et les choix sont écrits dans l'image.
Zones réservées par l'interface Instagram : rien d'important au-dessus de y = 250 ni sous y = 1700.
Sorties : work/<episode>/story-<id>.png"""
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
W_, H_ = 1080, 1920
work = ROOT / "work" / EP.name; work.mkdir(parents=True, exist_ok=True)
stories = yaml.safe_load(open(EP / "stories.yaml", encoding="utf-8"))["stories"]

# Dessin de l'épisode (identique à la miniature), réduit et remonté pour laisser la place aux choix
src = work / "story_src.py"
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
# zone du dessin (y 985-1480) ramenée à 70 % et centrée vers y = 1010
def shrink(a, sc=0.70, cy_src=1232, cy_dst=1010):
    im = Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8))
    sm = im.resize((int(W_ * sc), int(H_ * sc)), Image.LANCZOS)
    out = Image.new(im.mode, (W_, H_), 0)
    out.paste(sm, (int((W_ - W_ * sc) / 2), int(cy_dst - cy_src * sc))); return np.asarray(out).astype(np.float32) / 255
al_s, pr_s = shrink(al), shrink(pr)

ink = (20, 20, 24); gr = (18, 150, 100); gy = (95, 95, 100); rule = (150, 160, 190)
for s in stories:
    paper = paper_img(seed=7) / 255
    im = Image.fromarray((np.clip(paper, 0, 1) * 255).astype(np.uint8)); d = ImageDraw.Draw(im)
    def ctext(t, y, size, fill, font=CAV):
        f = ImageFont.truetype(font, size)
        while d.textlength(t, font=f) > 920 and size > 40: size -= 4; f = ImageFont.truetype(font, size)
        d.text(((W_ - d.textlength(t, font=f)) / 2, y), t, font=f, fill=fill)
    ctext(s["entete"], 290, 46, gy, PAT)
    d.line([(150, 355), (930, 355)], fill=rule, width=4)
    y = 400
    for ln in s["question"]:
        big = ln == s.get("mot_vert")
        ctext(ln, y, 150 if big else 105, gr if big else ink); y += 165 if big else 118
    a = np.asarray(im).astype(np.float32) / 255
    im = Image.fromarray((np.clip(a * (1 - al_s[..., None]) + pr_s, 0, 1) * 255).astype(np.uint8)); d = ImageDraw.Draw(im)
    choix = s.get("choix") or []
    y = 1290
    for k, c_ in enumerate(choix):                       # cases dessinées, lettre A/B/C en vert
        d.rounded_rectangle([170, y, 910, y + 105], radius=26, outline=ink, width=5, fill=(252, 250, 244))
        f = ImageFont.truetype(CAV, 64); d.text((205, y + 14), "ABC"[k], font=f, fill=gr)
        f2 = ImageFont.truetype(PAT, 50); t = c_
        while d.textlength(t, font=f2) > 620: f2 = ImageFont.truetype(PAT, f2.size - 2)
        d.text((280, y + 26), t, font=f2, fill=ink); y += 125
    ctext(s["pied"], max(y + 15, 1560), 52, gy, PAT)
    dest = work / f"story-{s['id']}.png"; im.save(dest); print("story ->", dest)
