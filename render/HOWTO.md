# Code de rendu des épisodes 1 (ballast) et 2 (stylo) — comment ça marche

Rendu 100 % Python : Pillow (supersampling x2) -> images -> ffmpeg (libx264, crf 17, 30 ips, 1080x1920).
- pal/stylo.py : look "stylo" (rendu en deux passes papier/noir -> alpha, composé sur un papier Seyès procédural ; variables d'environnement NOIR=1 ACC=18,150,100 MARG=150,205,180 ; polices Caveat x1.32 et Patrick Hand x1.18 ; champ de déplacement statique, aucun tremblement). Il faut PYTHONPATH=render/pal quand on lance un script ailleurs. Les chemins de polices sont à adapter vers render/fonts.
- pal/v3_head.py : fonctions communes (assemblées avec le corps de chaque épisode : `cat head body > ep.py`).
- ep1/ et ep2/ : body.py de chaque épisode (timeline des pièces, légendes karaoké, caméra, curseur), music.py (musique synthétisée 104 bpm), mix (voix + ambiance + ticks + musique sous la voix, gain musique 0.17), align (timing des mots avec faster-whisper "small" int8 sur tableau numpy 16 kHz, alignement difflib sur le script).
- Rendu par segments de 200 images (pal/seg_render.py + ep2/runall.sh, reprise possible) puis `ffmpeg -f concat -c copy`, mixage `-af loudnorm=I=-14:TP=-1.5:LRA=11`, AAC 192k.
- Miniature : thumb/mini_template.py (voir docs/sources/texte-regles-miniature-et-publication.md pour la mise en page, zone utile y 240 à 1680).
- Voix : Google AI Studio Gemini TTS, voix "Enzo" (les épisodes 1 et 2), style calme et clair ; en cloud il faudra une clé API Gemini enregistrée dans les secrets de l'environnement par Ilan lui-même.
