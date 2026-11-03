"""Alignement mot à mot. Usage : python align.py voice.wav texte.txt words.json
Sortie : [[mot_du_script, début_s, fin_s], ...]  (les mots gardent leur ponctuation).
Méthode : faster-whisper (modèle small, int8) puis alignement difflib sur le script ;
les mots non reconnus sont interpolés. Secours sans whisper : répartition par syllabes sur les zones de parole."""
import difflib, json, re, subprocess, sys, wave
import numpy as np

def norm(w): return re.sub(r"[^a-zàâäçéèêëîïôöùûüÿœ0-9]", "", w.lower())
def syl(w):
    x = norm(w); return max(1, len(re.findall(r"[aeiouyàâäéèêëîïôöùûüœ]+", x)))

def whisper_words(path):
    from faster_whisper import WhisperModel
    m = WhisperModel("small", device="cpu", compute_type="int8")
    segs, _ = m.transcribe(path, language="fr", word_timestamps=True, vad_filter=False)
    return [(w.word.strip(), w.start, w.end) for s in segs for w in s.words]

def speech_spans(path):
    out = subprocess.run(["ffmpeg", "-i", path, "-af", "silencedetect=n=-35dB:d=0.12", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    sil = [float(x) for x in re.findall(r"silence_(?:start|end): ([0-9.]+)", out)]
    w = wave.open(path); D = w.getnframes() / w.getframerate()
    spans, t = [], 0.0
    for i in range(0, len(sil), 2):
        s = sil[i]; e = sil[i + 1] if i + 1 < len(sil) else D
        if s - t > 0.06: spans.append((t, s))
        t = e
    if D - t > 0.06: spans.append((t, D))
    return spans, D


def peak_align(path, words):
    """Méthode de l'épisode 2 : pics de syllabes dans la voix + zones de parole, appariés au script par programmation dynamique."""
    from scipy.signal import butter, lfilter, find_peaks
    spans, D = speech_spans(path)
    w = wave.open(path); sr = w.getframerate()
    a = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16) / 32768.
    if w.getnchannels() > 1: a = a.reshape(-1, w.getnchannels()).mean(1)
    b, c = butter(3, [250 / (sr / 2), 3200 / (sr / 2)], "band"); x = lfilter(b, c, a)
    k = int(sr * 0.03); env = np.convolve(np.abs(x), np.ones(k) / k, "same")
    b2, c2 = butter(2, 12 / (sr / 2)); env = lfilter(b2, c2, env)
    p, _ = find_peaks(env, distance=int(sr * 0.07), prominence=0.02 * env.max()); pk = p / sr
    segs = spans; N = len(words); M = len(segs)
    wt = [syl(x) for x in words]; cum = np.cumsum([0] + wt)
    cnt = [int(((pk >= a_ - 0.04) & (pk <= b_ + 0.04)).sum()) for a_, b_ in segs]
    punct = [1 if re.search(r"[.?!:,;]$", x) else 0 for x in words]
    dp = np.full((M + 1, N + 1), 1e9); bk = {}; dp[0][0] = 0
    for m in range(1, M + 1):
        for j in range(N + 1):
            for i in range(max(0, j - 40), j + 1):
                if dp[m - 1][i] >= 1e9: continue
                nw = j - i; s_ = cum[j] - cum[i]
                cost = (s_ - 0.3 * nw - cnt[m - 1]) ** 2 if nw > 0 else 1.5
                if nw > 0 and j < N and not punct[j - 1]: cost += 2.0
                if dp[m - 1][i] + cost < dp[m][j]: dp[m][j] = dp[m - 1][i] + cost; bk[(m, j)] = i
    j = N; cuts = []
    for m in range(M, 0, -1): i = bk[(m, j)]; cuts.append((m, i, j)); j = i
    cuts.reverse(); st = [None] * N
    for m, i, j in cuts:
        if j <= i: continue
        a_, b_ = segs[m - 1]; pks = pk[(pk >= a_ - 0.04) & (pk <= b_ + 0.04)]; tot = sum(wt[i:j]); c_ = 0
        for kk in range(i, j):
            idx = min(max(len(pks) - 1, 0), int(round(c_ * len(pks) / tot))) if len(pks) else 0
            st[kk] = float(max(a_, (pks[idx] - 0.06) if len(pks) else a_)); c_ += wt[kk]
    return [[words[n], round(st[n], 3), round(min(st[n + 1] if n + 1 < N else D, st[n] + 0.9), 3)] for n in range(N)]

def fallback(path, words):
    spans, D = speech_spans(path)
    tot = sum(b - a for a, b in spans); wt = [syl(w) for w in words]; T = sum(wt)
    res, k, acc = [], 0, 0.0
    for w, n in zip(words, wt):
        a = acc / T * tot; b = (acc + n) / T * tot; acc += n
        def at(x):
            for s, e in spans:
                if x <= e - s: return s + x
                x -= e - s
            return spans[-1][1]
        res.append([w, round(at(a), 3), round(at(b), 3)])
    return res

def main(voice, texte, out):
    words = [w for w in open(texte, encoding="utf-8").read().split() if re.search(r"\w", w)]
    try:
        asr = whisper_words(voice); how = "whisper"
    except Exception as e:
        print("whisper indisponible (", type(e).__name__, ") -> secours par syllabes"); asr = None
    if not asr:
        try: res = peak_align(voice, words); print("alignement par pics de syllabes")
        except Exception as e: print("pics indisponibles (", type(e).__name__, e, ") -> répartition simple"); res = fallback(voice, words)
    else:
        a = [norm(w) for w in words]; b = [norm(w[0]) for w in asr]
        st = [None] * len(words); en = [None] * len(words)
        for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(None, a, b, autojunk=False).get_opcodes():
            if tag == "equal":
                for k in range(i2 - i1): st[i1 + k] = asr[j1 + k][1]; en[i1 + k] = asr[j1 + k][2]
        ok = [i for i, x in enumerate(st) if x is not None]
        print(f"alignement : {len(ok)}/{len(words)} mots reconnus")
        if len(ok) < 0.6 * len(words): raise SystemExit("alignement trop faible : vérifier la voix")
        w_ = wave.open(voice); D = w_.getnframes() / w_.getframerate()
        for i in range(len(words)):                       # interpolation des mots manquants
            if st[i] is None:
                p = max([j for j in ok if j < i], default=None); n = min([j for j in ok if j > i], default=None)
                t0 = en[p] if p is not None else 0.0; t1 = st[n] if n is not None else D
                gap = [k for k in range(i, len(words)) if st[k] is None and (n is None or k < n)]
                f = gap.index(i) / len(gap); st[i] = t0 + (t1 - t0) * f
        res = []
        for i, w in enumerate(words):
            e = en[i] if en[i] is not None else (st[i + 1] if i + 1 < len(words) else D)
            res.append([w, round(st[i], 3), round(min(e, st[i] + 0.9), 3)])
    json.dump(res, open(out, "w", encoding="utf-8"), ensure_ascii=False)
    print(f"{len(res)} mots -> {out}")

if __name__ == "__main__":
    main(*sys.argv[1:4])
