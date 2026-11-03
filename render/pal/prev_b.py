import sys
TS_ = [float(x) for x in sys.argv[3:]]
sys.argv = [sys.argv[0], sys.argv[1], sys.argv[2]]
exec(open('/tmp/claude-0/work/pal/stylo_render_v3.py').read().split('if __name__')[0])
from PIL import Image
ims = []
for t in TS_:
    imW, imB = run_layers(g, lambda: g['frame'](int(round(t * 30))))
    ims.append(Image.fromarray(comp(imW, imB, 0)))
cols = 4; w, h = 360, 640
rows = (len(ims) + cols - 1) // cols
sh = Image.new('RGB', (cols * w, rows * h), (255, 255, 255))
for k, im in enumerate(ims): sh.paste(im.resize((w, h), Image.LANCZOS), ((k % cols) * w, (k // cols) * h))
sh.save(OUT)
