import os, sys, subprocess, numpy as np
os.environ.setdefault('NOIR','1'); os.environ.setdefault('ACC','18,150,100'); os.environ.setdefault('MARG','150,205,180')
SRC, OUT = sys.argv[1], sys.argv[2]; A0, A1 = int(sys.argv[3]), int(sys.argv[4])
sys.argv = ['x','none']
import stylo
from stylo import *
g = {"__name__": "s"}; exec(stylo.load(SRC), g)
DURV = g['DUR']; FPS = 30
H_, W_ = 1920, 1080
K = 1
def mkfield(seed, amp=1.3):
    rng = np.random.default_rng(seed)
    dx = gaussian_filter(rng.standard_normal((H_, W_)), 26); dx = dx / dx.std() * amp
    dy = gaussian_filter(rng.standard_normal((H_, W_)), 26); dy = dy / dy.std() * amp
    dx += gaussian_filter(rng.standard_normal((H_, W_)), 5) * 0.5; dy += gaussian_filter(rng.standard_normal((H_, W_)), 5) * 0.5
    yy, xx = np.mgrid[0:H_, 0:W_].astype(np.float32)
    pen = np.clip(0.90 + 0.10 * gaussian_filter(rng.standard_normal((H_, W_)), 14) / 0.05 * 0.05, 0.82, 1.0)
    return [yy + dy, xx + dx], pen
FIELDS = [mkfield(100 + k) for k in range(K)]
PAPER_ARR = paper_img(seed=5) / 255
BGc = np.array(PAPER, np.float32) / 255
def comp(imW, imB, k):
    Wa, Ba = [np.asarray(x.resize((W_, H_), Image.LANCZOS)).astype(np.float32) / 255 for x in (imW, imB)]
    alpha = np.clip(np.mean(1 - (Wa - Ba) / BGc, axis=2), 0, 1)
    co, pen = FIELDS[k]
    al = map_coordinates(alpha, co, order=1, mode='nearest')
    pr = np.stack([map_coordinates(Ba[..., c], co, order=1, mode='nearest') for c in range(3)], axis=2)
    out = PAPER_ARR * (1 - al[..., None]) + pr * pen[..., None]
    return (np.clip(out, 0, 1) * 255).astype(np.uint8)
def work(i):
    imW, imB = run_layers(g, lambda: g['frame'](i))
    return comp(imW, imB, 0).tobytes()
if __name__ == "__main__":
    import multiprocessing as mp
    cmd = ["ffmpeg","-y","-loglevel","error","-f","rawvideo","-pix_fmt","rgb24","-s","1080x1920","-r","30","-i","-","-c:v","libx264","-preset","medium","-crf","17","-pix_fmt","yuv420p",OUT]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    with mp.Pool(2) as pool:
        for k, b in enumerate(pool.imap(work, range(A0, A1), chunksize=2)):
            p.stdin.write(b)
    p.stdin.close(); p.wait(); print("done", OUT)
