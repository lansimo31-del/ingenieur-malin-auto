# Alignement par phrases : zones de parole (silencedetect) appariées aux phrases du script (ponctuation) par DP sur la durée, puis mots répartis par syllabes.
import sys, json, re, numpy as np
sys.path.insert(0, __import__("os").path.dirname(__import__("os").path.abspath(__file__)))
import align as A
voice, texte, out = sys.argv[1:4]
raw = open(texte, encoding="utf-8").read().split()
words = [w for w in raw if re.search(r"\w", w)]
# phrases : coupe après , . ? ! (et après un mot suivi d'un ':' isolé)
phr, cur = [], []
for t in raw:
    if not re.search(r"\w", t):
        if cur: pass
        continue
    cur.append(t)
    if re.search(r"[.?!,]$", t): phr.append(cur); cur = []
if cur: phr.append(cur)
spans, D = A.speech_spans(voice)
spans = [list(s) for s in spans]
syl = [sum(A.syl(w) for w in p) for p in phr]
tot = sum(b - a for a, b in spans); r = tot / sum(syl)
K, M = len(phr), len(spans); dur = [b - a for a, b in spans]
INF = 1e18; dp = np.full((K + 1, M + 1), INF); bk = {}; dp[0][0] = 0
for k in range(1, K + 1):
    for m in range(k, M + 1):
        for i in range(k - 1, m):
            if dp[k - 1][i] >= INF: continue
            c = (sum(dur[i:m]) - syl[k - 1] * r) ** 2 + 0.02 * (m - i - 1)
            if dp[k - 1][i] + c < dp[k][m]: dp[k][m] = dp[k - 1][i] + c; bk[(k, m)] = i
assert dp[K][M] < INF, "pas d'appariement"
m = M; asg = []
for k in range(K, 0, -1): i = bk[(k, m)]; asg.append((k - 1, i, m)); m = i
asg.reverse()
res = []
for k, i, m in asg:
    sp = spans[i:m]; ws = phr[k]; w_s = [A.syl(w) for w in ws]; T = sum(w_s); L = sum(b - a for a, b in sp)
    def at(x):
        for a, b in sp:
            if x <= b - a: return a + x
            x -= b - a
        return sp[-1][1]
    acc = 0
    for w, n in zip(ws, w_s):
        res.append([w, round(at(acc / T * L), 3), round(at((acc + n) / T * L), 3)]); acc += n
for n in range(len(res) - 1): res[n][2] = round(min(res[n][2], res[n + 1][1]) if res[n][2] > res[n + 1][1] else res[n][2], 3)
json.dump(res, open(out, "w", encoding="utf-8"), ensure_ascii=False)
print(len(res), len(words), "phrases", K, "zones", M)
