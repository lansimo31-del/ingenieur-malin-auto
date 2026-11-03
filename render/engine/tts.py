"""Voix off par Gemini TTS (Google). Usage : python tts.py texte.txt voice.wav
La clé est lue dans la variable d'environnement GEMINI_API_KEY (secrets de l'environnement cloud).
Elle n'est jamais affichée ni écrite dans un fichier."""
import base64, json, os, sys, wave, urllib.request, urllib.error
from pathlib import Path

API = "https://generativelanguage.googleapis.com/v1beta"
CFG = Path(__file__).resolve().parents[2] / "config" / "voix.json"

def call(path, body=None, key=None):
    req = urllib.request.Request(API + path, data=None if body is None else json.dumps(body).encode(),
                                 headers={"x-goog-api-key": key, "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=180) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        raise SystemExit(f"Gemini API : HTTP {e.code} {e.read().decode()[:300]}")

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
    if cfg["voix_gemini"] == "A_CONFIRMER":
        raise SystemExit("config/voix.json : nom de la voix Gemini à confirmer par Ilan (voix « Enzo » = quelle voix prédéfinie ?)")
    model = cfg["modele"] if cfg["modele"] != "auto" else pick_model(key)
    body = {"contents": [{"parts": [{"text": f'{cfg["style"]}\n\n{text}'}]}],
            "generationConfig": {"responseModalities": ["AUDIO"],
                                 "speechConfig": {"voiceConfig": {"prebuiltVoiceConfig": {"voiceName": cfg["voix_gemini"]}}}}}
    r = call(f"/models/{model}:generateContent", body, key)
    part = r["candidates"][0]["content"]["parts"][0]["inlineData"]
    pcm = base64.b64decode(part["data"])
    with wave.open(str(out), "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(24000); w.writeframes(pcm)
    print(f"voix : modèle {model}, {len(pcm)/48000:.1f} s -> {out}")

if __name__ == "__main__":
    synth(open(sys.argv[1], encoding="utf-8").read().strip(), sys.argv[2])
