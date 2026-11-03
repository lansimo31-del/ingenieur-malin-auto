"""Mixage voix + ambiance + « pop » + musique. Usage : python mix.py voice.wav music.wav durée_s cues.json mix.wav
cues.json (optionnel) : liste de secondes où placer un petit « pop » de transition."""
import json, os, subprocess, sys, wave
import numpy as np
voice, music, D, cues, out = sys.argv[1], sys.argv[2], float(sys.argv[3]), sys.argv[4], sys.argv[5]
sr = 44100; N = int(D * sr)
vo = out + ".vo.wav"
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", voice, "-ar", str(sr), "-ac", "1", "-t", str(D), vo], check=True)
def rd(p):
    w = wave.open(p); a = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768
    return np.pad(a, (0, max(0, N - len(a))))[:N]
v = rd(vo); os.remove(vo); mu = rd(music)
rng = np.random.default_rng(3); n = rng.standard_normal(N)
amb = np.convolve(n, np.ones(400) / 400, mode="same"); amb = np.convolve(amb, np.ones(60) / 60, mode="same")
amb = amb / np.abs(amb).max() * 0.05
t = np.arange(N) / sr
amb *= np.clip(t / 1.5, 0, 1) * np.clip((D - t) / 1.5, 0, 1)
env = np.convolve(np.abs(v), np.ones(2205) / 2205, mode="same"); duck = 1 - 0.6 * np.clip(env * 8, 0, 1)
bed = amb * duck
def tick(at, f=880, g=0.05):
    a = int(at * sr); m = int(0.09 * sr)
    if a + m < N: bed[a:a + m] += g * np.sin(2 * np.pi * f * np.arange(m) / sr) * np.exp(-np.arange(m) / sr * 45)
if cues and os.path.exists(cues):
    for i, tm in enumerate(json.load(open(cues))): tick(tm + 0.05, 660 + 80 * (i % 6))
res = np.clip(v + bed + mu * 0.17 * duck, -1, 1)          # gain musique 0,17, sous la voix
with wave.open(out, "wb") as o:
    o.setnchannels(1); o.setsampwidth(2); o.setframerate(sr); o.writeframes((res * 32767).astype(np.int16).tobytes())
