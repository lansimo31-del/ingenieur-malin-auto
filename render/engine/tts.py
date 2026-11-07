"""Voix off par Gemini TTS (Google). Usage : python tts.py texte.txt voice.wav
La clé est lue dans la variable d'environnement GEMINI_API_KEY (secrets de l'environnement cloud).
Elle n'est jamais affichée ni écrite dans un fichier.
Contrôle (ajouté le 3 nov.) : le modèle TTS lit parfois la consigne de style à voix haute (« Voix masculine française… »),
surtout sur un texte court, et systemInstruction est refusé par ce modèle. Chaque audio est donc transcrit (début) par un
modèle Gemini texte (config/voix.json : modele_controle) ; s'il commence par la consigne ou pas par le texte, il est régénéré."""
import base64, json, os, re, sys, time, wave, urllib.request, urllib.error
from pathlib import Path

API = "https://generativelanguage.googleapis.com/v1beta"
CFG = Path(__file__).resolve().parents[2] / "config" / "voix.json"

def call(path, body=None, key=None):
    for wait in (10, 30, 60, 120, None):          # réessais sur 429 / 5xx / erreur réseau
        req = urllib.request.Request(API + path, data=None if body is None else json.dumps(body).encode(),
                                     headers={"x-goog-api-key": key, "Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=180) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            msg = f"Gemini API : HTTP {e.code} {e.read().decode()[:300]}"
            if e.code not in (429, 500, 502, 503, 504) or wait is None: raise SystemExit(msg)
        except (urllib.error.URLError, TimeoutError) as e:
            msg = f"Gemini API : réseau {e}"
            if wait is None: raise SystemExit(msg)
        print(f"{msg[:80]}… nouvel essai dans {wait} s"); time.sleep(wait)

def norm(x): return re.sub(r"[^a-zàâäçéèêëîïôöùûüÿœ0-9 ]", " ", x.lower()).split()

def check_start(wav_path, text, cfg, key):
    """True si le début de l'audio est bien le texte (et pas la consigne). None si le contrôle est impossible."""
    model = cfg.get("modele_controle")
    if not model: return None
    import io
    w = wave.open(str(wav_path)); sr = w.getframerate(); fr = w.readframes(min(w.getnframes(), sr * 10))
    buf = io.BytesIO(); o = wave.open(buf, "wb"); o.setnchannels(1); o.setsampwidth(2); o.setframerate(sr); o.writeframes(fr); o.close()
    body = {"contents": [{"parts": [{"inlineData": {"mimeType": "audio/wav", "data": base64.b64encode(buf.getvalue()).decode()}},
                                    {"text": "Transcris mot à mot ce qui est dit dans cet audio, en français. Rien d'autre."}]}]}
    try:
        heard = norm(call(f"/models/{model}:generateContent", body, key)["candidates"][0]["content"]["parts"][-1]["text"])
    except (SystemExit, KeyError, IndexError) as e:
        print("contrôle de la voix impossible :", str(e)[:120]); return None
    style, want = norm(cfg["style"])[:4], norm(text)[:4]
    if heard[:4] == style or " ".join(style[:2]) in " ".join(heard[:8]): return False
    return sum(1 for x in want if x in heard[:10]) >= 3

def pick_model(key):
    names = [m["name"].split("/")[-1] for m in call("/models?pageSize=200", key=key).get("models", [])
             if "tts" in m["name"].lower()]
    if not names: raise SystemExit("Aucun modèle TTS disponible pour cette clé")
    names.sort(key=lambda n: (("flash" not in n), ("preview" in n), n))   # flash d'abord, stable avant preview
    return names[0]

def synth(text, out, cfg=None):
    key = os.environ.get("GEMINI_API_KEY")
    if not key: raise SystemExit("GEMINI_API_KEY absente de l'environnement (secret à ajouter, puis nouvelle session)")
    cfg = cfg or json.load(open(CFG))
    if os.environ.get("VOIX_STYLE"): cfg = dict(cfg, style=os.environ["VOIX_STYLE"])   # consigne courte de secours si le modèle lit le style (7 nov.)
    if cfg["voix_gemini"] == "A_CONFIRMER":
        raise SystemExit("config/voix.json : nom de la voix Gemini à confirmer par Ilan (voix « Enzo » = quelle voix prédéfinie ?)")
    model = cfg["modele"] if cfg["modele"] != "auto" else pick_model(key)
    # Voix « Enzo » d'abord ; si l'API refuse ce nom, voix prédéfinies graves de secours (config/voix.json)
    voices = [cfg["voix_gemini"]] + [v for v in cfg.get("voix_secours", []) if v != cfg["voix_gemini"]]
    for essai in range(1, 5):
        v = _synth_once(text, out, cfg, model, voices, key)
        ok = check_start(out, text, cfg, key)
        if ok is not False:
            print(f"voix retenue : {v}" + ("" if ok else " (contrôle du début non effectué)")); return v
        print(f"essai {essai} : l'audio commence par la consigne ou pas par le texte, nouvelle génération")
    raise SystemExit("voix : 4 essais, l'audio ne commence jamais par le texte attendu")

def _synth_once(text, out, cfg, model, voices, key):
    r = None
    for v in voices:
        body = {"contents": [{"parts": [{"text": f'{cfg["style"]}\n\n{text}'}]}],
                "generationConfig": {"responseModalities": ["AUDIO"],
                                     "speechConfig": {"voiceConfig": {"prebuiltVoiceConfig": {"voiceName": v}}}}}
        try:
            r = call(f"/models/{model}:generateContent", body, key); break
        except SystemExit as e:
            if "HTTP 400" not in str(e) or "oice" not in str(e): raise   # seule une voix inconnue fait passer à la suivante
            print(f"voix {v} refusée par l'API, essai suivant")
    if r is None: raise SystemExit("aucune voix acceptée")
    part = r["candidates"][0]["content"]["parts"][0]["inlineData"]
    pcm = base64.b64decode(part["data"])
    with wave.open(str(out), "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(24000); w.writeframes(pcm)
    print(f"voix : modèle {model}, voix {v}, {len(pcm)/48000:.1f} s -> {out}")
    return v

if __name__ == "__main__":
    synth(open(sys.argv[1], encoding="utf-8").read().strip(), sys.argv[2])
