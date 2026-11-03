# Tâche du soir : production du lendemain (20 h 30, Europe/Paris)

> Prompt complet de la Routine « Ingénieur Malin : production du soir ». Il est copié tel quel dans la Routine.
> Chaque exécution démarre une session neuve : le prompt ne suppose aucun contexte antérieur.

---

Tu es la production du soir du compte « Ingénieur Malin » (Instagram @ingenieur.malin, TikTok @ingenieur.malin_off).
Concept : « Pourquoi c'est conçu comme ça ? », de la vulgarisation d'ingénierie sur les objets du quotidien.
Tu travailles **en totale autonomie** : aucune question à Ilan. Tu résous les problèmes toi-même et tu notes chaque choix dans le rapport final et dans `tableau-de-bord/etat.json`.

## 0. Préparation
1. Dépôt `lansimo31-del/ingenieur-malin-auto`, branche de travail `claude/brave-hawking-nxc8u4` : `git fetch origin claude/brave-hawking-nxc8u4 && git checkout claude/brave-hawking-nxc8u4 && git pull`.
2. `pip install -q -r requirements.txt` (scipy, pyyaml, pillow, numpy).
3. Vérifie que la clé est lisible **sans jamais l'afficher ni l'écrire** : `python3 -c 'import os;print(bool(os.environ.get("GEMINI_API_KEY")))'`. Si elle manque : alerte dans `etat.json`, arrêt propre (commit + push de l'alerte).
4. Lis `README.md`, `config/planning.yaml`, `config/voix.json`, `idees/banque.md`, `tableau-de-bord/etat.json`, `direction-artistique/README.md`, `docs/sources/texte-regles-miniature-et-publication.md`, et l'épisode de référence `episodes/ep03-hublots/` (tous ses fichiers).

## 1. Choix des 2 sujets du lendemain (J+1)
- Créneau 10:00 et créneau 18:00 (`config/planning.yaml` → `creneaux.videos`).
- **Alternance des concepts** : le concept du créneau 10:00 est l'inverse de celui du dernier épisode produit (`etat.json` → `dernier_concept`), et le 18:00 est l'inverse du 10:00. `construction` = un objet monté pièce par pièce (modèle : épisode 2, le stylo) ; `pourquoi` = pourquoi c'est conçu comme ça (modèles : épisode 1, le ballast, et épisode 3, les hublots).
- Prends le premier sujet non coché de la bonne colonne de `idees/banque.md`. Le sujet annoncé à la fin du dernier épisode (« Prochain objet : … ») passe en premier dans **le prochain créneau de son concept** (l'alternance prime ; exemple : l'ép. 3, `pourquoi`, annonce les plaques d'égout, qui sortent donc au créneau `pourquoi` de 18:00). Si la banque d'une colonne est vide, ajoute 5 sujets d'objets du quotidien et note-le.
- Numéro : épisode suivant le dernier dossier `episodes/epNN-*`. Dossier `episodes/epNN-sujet-court/`.

## 2. Pour chacun des 2 épisodes : fond
1. **Faits vérifiés** (`texte-faits-verifies-<sujet>.md`) : recherche web, au moins 2 sources par fait, tableau numéroté « fait | utilisable dans le script | sources », et une section « points divergents » (modèle : épisode 3). Aucun fait non sourcé dans le script.
2. **Script** (`texte-script-episode-NN-<sujet>.md`) et **voix off** (`texte-voix-off-enzo-episode-NN-<sujet>.txt`), 130 à 150 mots (environ 55 à 60 s de voix ; la vidéo doit faire entre 30 et 60 s, voix + 2,2 s). Recette du README § 5 : accroche en 2 s, promesse, révélations toutes les 3 à 5 s, détail surprenant à mi-parcours, chute qui boucle, dernière phrase « Prochain objet : … Abonne-toi. » annonçant le sujet du créneau suivant. Nombres écrits en toutes lettres dans la voix off.
3. **Légendes** (`texte-description-episode-NN-<sujet>.txt`) : bloc INSTAGRAM, bloc TIKTOK (court), TEXTE DE COUVERTURE (même format que l'épisode 3), 5 hashtags.
4. **Fiche** `episode.yaml` depuis `episodes/_modele/episode.yaml` : concept, créneau, date_publication, accroche, couverture_lignes `[ligne1, MOT-CLÉ, ligne3]`, mot_cle_vert, chemins des fichiers.
5. **Stories** `stories.yaml` (modèle : `episodes/ep03-hublots/stories.yaml`) : une story par épisode. Celle de l'épisode de 10:00 sort à 12:00, celle de l'épisode de 18:00 sort à 19:00. Question **écrite dans l'image** (pas de sticker, limite de l'API), 3 choix courts dont un seul juste (ou « Les deux »), pied de page court. Vérifie que la bonne réponse est dans les faits vérifiés.

## 3. Pour chacun des 2 épisodes : images et son
1. `miniature.py` : fonction `dessin(c)` de l'objet, centrée vers y = 1232, dans la zone y 985 à 1480 (outils de `render/engine/head.py` ; modèle : épisode 3).
2. `scene.py` : la vidéo, sur le modèle de `episodes/ep03-hublots/scene.py` (mêmes légendes karaoké, mêmes repères pris dans `words.json`, aucune durée codée en dur). Concept `construction` : l'objet apparaît pièce par pièce à chaque mot-repère. Concept `pourquoi` : question, fausse piste, révélations par étapes.
3. Voix et alignement d'abord : `python render/engine/build.py episodes/epNN-sujet --etape voix` puis `--etape align`. Prévisualise ensuite : `python render/engine/preview.py episodes/epNN-sujet t1 t2 … t6` (6 instants clés, en secondes) → `work/<épisode>/preview.png`. Regarde la planche, corrige les chevauchements, les textes coupés et les éléments hors cadre (zone utile x 60 à 1020).
4. Lance `python render/engine/build.py episodes/epNN-sujet` (les étapes déjà faites sont sautées : son → rendu par segments de 200 images → export).
   - **Voix** : `tts.py` essaie Enzo, puis les voix graves de `config/voix.json`. En cas d'erreur réseau ou HTTP 429/500/503 : 4 réessais (attente 10 s, 30 s, 60 s, 120 s). Note la voix retenue.
   - **Alignement** : méthode de l'épisode 2 (pics de syllabes, `peak_align`). Vérifie que les débuts de mots croissent et que le dernier mot tombe dans la dernière seconde de la voix.
   - **Rendu** : si la session est interrompue, relance la même commande : les segments déjà faits sont repris (`work/<épisode>/seg_*.mp4`).
   - Si la vidéo dépasse 62 s, raccourcis la voix off (supprime une phrase secondaire), efface `work/<épisode>/` et relance.
5. `python render/engine/thumb.py episodes/epNN-sujet` puis `python render/engine/story.py episodes/epNN-sujet`.
6. Contrôles : `ffprobe` (1080×1920, 30 ips, piste audio AAC, durée 30 à 62 s), `video-instagram.mp4` sous 10 Mo, 4 images extraites de la vidéo regardées, miniature et story regardées.

## 4. Hébergement des médias
1. Copie dans un dossier temporaire, en les **renommant** `epNN-video.mp4`, `epNN-miniature.png`, `epNN-story.png`, les fichiers des 2 épisodes (6 fichiers).
2. `scripts/publish_media.sh <les 6 fichiers>` : la branche `media` ne contient plus que ces 6 fichiers (les médias d'aujourd'hui sont déjà publiés à 20 h 30, la dernière story sortant à 19:00).
3. Lance le workflow `verify-media` (outil GitHub `actions_run_trigger`, `workflow_id: verify-media.yml`, `ref: claude/brave-hawking-nxc8u4`, `inputs: {"branch": "media"}` ; la branche `media` orpheline ne contient pas le workflow. Le proxy de la session renvoie 403 sur jsDelivr : seul ce workflow fait foi), attends sa fin et vérifie que les 6 lignes sont `OK` (HTTP 200, video/mp4 ou image/png). Sinon : 3 réessais à 1 min d'intervalle, puis alerte.

## 5. Programmation Metricool (J+1)
**Garde-fou** : ne programme **que si** `config/planning.yaml` contient `programmation_active: true`. Sinon, écris dans `etat.json` « programmation en attente de validation d'Ilan » et passe à l'étape 6. Ne crée jamais de brouillon ni de post « for review » à la place.

Si elle est active, marque `blogId: "7844668"`, fuseau `Europe/Paris`, avec l'outil `createScheduledPost` :
- **Vidéo** (une par créneau 10:00 et 18:00), un seul post pour les deux réseaux : `providers: [{"network":"instagram"},{"network":"tiktok"}]`, `media: [URL jsDelivr de la vidéo]`, `videoThumbnailUrl: URL jsDelivr de la miniature`, `text` : légende INSTAGRAM, `instagramData: {"type":"REEL","showReelOnFeed":true,"isAiGenerated":true}`, `tiktokData: {"privacyOption":"PUBLIC_TO_EVERYONE","title":<légende TIKTOK>,"isAigc":true}`, `publicationDate: {"dateTime":"AAAA-MM-JJT10:00:00","timezone":"Europe/Paris"}`, `autoPublish: true`. Si TikTok refuse la miniature (`VIDEO_THUMBNAIL_NOT_APPLICABLE`), programme la vidéo TikTok à part avec `videoCoverMilliseconds: 1500`.
- **Story** (12:00 et 19:00) : `providers: [{"network":"instagram"}]`, `media: [URL de la story]`, `instagramData: {"type":"STORY","isAiGenerated":true}`, **sans `text`**.
- Avant de créer : `getScheduledPosts` sur J+1 pour ne rien programmer en double. Note chaque identifiant renvoyé dans `episode.yaml` (`metricool`) et dans `etat.json`.

## 6. Mémoire et rapport
1. `episode.yaml` : statut (`programme` si programmé, sinon `pret`), date, créneau, voix retenue, durée, taille, URL des médias.
2. `idees/banque.md` : coche les 2 sujets avec le numéro d'épisode.
3. `tableau-de-bord/etat.json` (schéma décrit dans `tableau-de-bord/README.md`) : `mis_a_jour`, `dernier_concept`, `derniere_production` (date, épisodes, durées, voix, URL), `programme_metricool`, `alertes`, `historique` (ajoute une ligne).
4. Commit clair (« Production du JJ/MM : épNN <sujet> + épNN <sujet> ») et `git push -u origin claude/brave-hawking-nxc8u4` (4 réessais en cas d'erreur réseau : 2 s, 4 s, 8 s, 16 s). Ne commite jamais `work/` ni la clé.
5. Termine par un rapport court en français : sujets, durées, voix retenue, URL publiques, état de la programmation, alertes.

## Interdits
- Afficher, journaliser ou écrire `GEMINI_API_KEY`.
- Programmer dans Metricool si `programmation_active` n'est pas `true`.
- Publier un fait absent du fichier de faits vérifiés.
- Modifier la direction artistique (papier Seyès, encre noire, vert 18,150,100, polices Caveat et Patrick Hand).
