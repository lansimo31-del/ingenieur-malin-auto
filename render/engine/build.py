"""Produit un épisode de bout en bout. Usage : python render/engine/build.py episodes/ep03-hublots [--etape x]
Dossier d'épisode attendu :
  texte-voix-off-*.txt   texte lu par la voix (voir episode.yaml : voix_off)
  scene.py               corps de la vidéo (fonction frame(i), DUR fourni par le moteur)
  cues.json              (optionnel) instants des « pop »
Sorties dans work/<episode>/ (hors dépôt) : voice.wav, words.json, mix.wav, video.mp4 (master),
  video-instagram.mp4 (moins de 10 Mo). La miniature est produite par thumb.py."""
import json, math, os, shutil, subprocess, sys, wave
from pathlib import Path
import yaml

ENG = Path(__file__).resolve().parent; ROOT = ENG.parents[1]
EP = (ROOT / sys.argv[1]).resolve() if not Path(sys.argv[1]).is_absolute() else Path(sys.argv[1])
cfg = yaml.safe_load(open(EP / "episode.yaml", encoding="utf-8"))
WORK = ROOT / "work" / EP.name; WORK.mkdir(parents=True, exist_ok=True)
only = sys.argv[sys.argv.index("--etape") + 1] if "--etape" in sys.argv else None
PY = sys.executable
env = dict(os.environ, EP_DIR=str(WORK), NOIR="1", ACC="18,150,100", MARG="150,205,180",
           PYTHONPATH=str(ENG))
def run(*a, **k): subprocess.run([str(x) for x in a], check=True, env=k.pop("env", env), **k)
def step(name): return only in (None, name)
def dur_of(p):
    w = wave.open(str(p)); return w.getnframes() / w.getframerate()

texte = EP / cfg["voix_off"]
voice, words = WORK / "voice.wav", WORK / "words.json"
if step("voix") and not voice.exists():
    run(PY, ENG / "tts.py", texte, voice)
if step("align") and not words.exists():
    shutil.copy(texte, WORK / "texte.txt"); run(PY, ENG / "align.py", voice, texte, words)

D = round(float(cfg.get("duree") or (dur_of(voice) + 2.2)), 1)       # voix + 2,2 s de respiration finale
env["EP_DUR"] = str(D); print("durée vidéo", D, "s")

if step("son"):
    run(PY, ENG / "music.py", D, WORK / "music.wav")
    run(PY, ENG / "mix.py", voice, WORK / "music.wav", D, EP / "cues.json", WORK / "mix.wav")

NF = int(round(D * 30))
# Son : loudnorm (cible -14 LUFS), puis 48 kHz et limiteur à -3 dBFS (le pic touchait 0 dB après l'encodage AAC, 3 nov.)
LIM = "alimiter=limit=0.708:attack=2:release=60:level=false"
AF_MASTER = f"loudnorm=I=-14:TP=-2:LRA=11,aresample=48000,{LIM}"
if step("rendu"):
    src = WORK / "ep.py"
    src.write_text((ENG / "head.py").read_text() + "\n" + (EP / "scene.py").read_text())
    seg = 200; files = []
    for a in range(0, NF, seg):
        b = min(a + seg, NF); f = WORK / f"seg_{a:05d}.mp4"; files.append(f)
        ok = f.exists() and subprocess.run(["ffprobe", "-v", "error", f], capture_output=True).returncode == 0
        if ok: continue                                              # reprise possible
        run(PY, ENG / "seg_render.py", src, f"{f}.tmp.mp4", a, b); os.replace(f"{f}.tmp.mp4", f)
    (WORK / "list.txt").write_text("".join(f"file '{f}'\n" for f in files))
    run("ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", WORK / "list.txt",
        "-c", "copy", WORK / "silent.mp4")
    run("ffmpeg", "-y", "-loglevel", "error", "-i", WORK / "silent.mp4", "-i", WORK / "mix.wav",
        "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-af", AF_MASTER,
        "-c:a", "aac", "-b:a", "192k", "-shortest", WORK / "video.mp4")

if step("export"):
    # version d'envoi : moins de 10 Mo, 9:16, débit calculé sur la durée
    vb = int((9.4e6 * 8) / D - 128_000)
    run("ffmpeg", "-y", "-loglevel", "error", "-i", WORK / "video.mp4", "-c:v", "libx264", "-preset", "slow",
        "-b:v", str(vb), "-maxrate", str(int(vb * 1.4)), "-bufsize", str(vb * 2), "-pix_fmt", "yuv420p",
        "-af", LIM, "-ar", "48000", "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", WORK / "video-instagram.mp4")
    mo = (WORK / "video-instagram.mp4").stat().st_size / 1e6
    print(f"video-instagram.mp4 : {mo:.2f} Mo"); assert mo < 10, "dépasse 10 Mo"
