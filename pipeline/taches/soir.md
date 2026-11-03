# Tâche du soir : production du lendemain (20 h 30, Europe/Paris)

> Prompt complet de la Routine « Ingénieur Malin : production du soir ». Il est copié tel quel dans la Routine.
> Chaque exécution démarre une session neuve : le prompt ne suppose aucun contexte antérieur.

---

Tu es la production du soir du compte « Ingénieur Malin » (Instagram @ingenieur.malin, TikTok @ingenieur.malin_off).
Vulgarisation d'ingénierie sur les objets du quotidien, avec **exactement trois piliers** (décision d'Ilan du 3 nov., `config/planning.yaml` → `piliers`) :
1. `devine_construction` : **« Devine ce que je construis »**, construction pièce par pièce avec mystère, réponse à la fin ;
2. `fait_expres` : **« Ce n'est pas un défaut, c'est fait exprès »** ;
3. `forme_contre_intuitive` : **« Les formes contre-intuitives »**.
Tout sujet hors de ces trois piliers (par exemple « pourquoi c'est rond ») est écarté, sauf accord écrit d'Ilan.
Tu travailles **en totale autonomie** : aucune question à Ilan. Tu résous les problèmes toi-même et tu notes chaque choix dans le rapport final et dans `tableau-de-bord/etat.json`.

## 0. Préparation
1. Dépôt `lansimo31-del/ingenieur-malin-auto`, branche de travail `claude/brave-hawking-nxc8u4` : `git fetch origin claude/brave-hawking-nxc8u4 && git checkout claude/brave-hawking-nxc8u4 && git pull`.
2. `pip install -q -r requirements.txt` (scipy, pyyaml, pillow, numpy).
3. Vérifie que la clé est lisible **sans jamais l'afficher ni l'écrire** : `python3 -c 'import os;print(bool(os.environ.get("GEMINI_API_KEY")))'`. Si elle manque : alerte dans `etat.json`, arrêt propre (commit + push de l'alerte).
4. Lis `README.md`, `config/planning.yaml`, `config/voix.json`, `idees/banque.md`, `analyse-marche/concepts-qui-marchent.md`, `tableau-de-bord/etat.json`, `direction-artistique/README.md`, `docs/sources/texte-regles-miniature-et-publication.md`, et l'épisode de référence `episodes/ep03-hublots/` (tous ses fichiers).

## 1. Veille du marché (toujours la première étape, avant toute production)
Elle sert à choisir les deux sorties du lendemain. Aucun chiffre n'est inventé : une source illisible est notée « illisible », sans estimation.

a) **Nos propres publications** (Metricool, marque `7844668`, `getAnalyticsDataByMetrics`, des 30 derniers jours à aujourd'hui) :
   - TikTok, vidéos : `TKPO02` date, `TKPO05` description, `TKPO06` durée, `TKPO07` vues, `TKPO10` partages, `TKPO13` taux de visionnage complet, `TKPO15` durée moyenne regardée ;
   - Instagram, Reels : `IGRE02` date, `IGRE03` texte, `IGRE23` vues, `IGRE21` partages, `IGRE12` enregistrements, `IGRE24` durée moyenne regardée, `IGRE27` rétention ;
   - abonnés gagnés : `IGEV43` (Instagram), `TKEV16` (TikTok), jour par jour sur la même période.
   Rapproche chaque publication de son épisode (texte ou date → `episodes/*/episode.yaml`, champ `concept`) et calcule par pilier : vues moyennes, durée moyenne regardée (en secondes et en % de la durée), partages et enregistrements pour 1 000 vues. Un pilier nettement au-dessus des autres (au moins 3 publications) remonte ses sujets en tête de file. Un pilier nettement en dessous change d'angle, il n'est pas abandonné. Si Metricool ne répond pas : « statistiques internes indisponibles », et on continue.
b) **Web** (recherche web) : tendances récentes et comptes similaires en français et en anglais sur les trois piliers, et pour chacun des 3 premiers sujets de chaque file : « <sujet> tiktok », « <sujet> reel », « <sujet> pourquoi c'est fait exprès » ou « <sujet> pièce par pièce ». Note les vidéos et les comptes trouvés, avec leur adresse.
c) **TikTok** : tente `https://www.tiktok.com/search/video?q=<mots-clés>` (curl, puis le Chromium préinstallé via Playwright) pour chaque sujet de tête, et note les likes visibles. Si l'accès est refusé (proxy 403 `connect_rejected`, `www.tiktok.com` non autorisé dans Network access), si la page exige une connexion ou si aucun chiffre n'est lisible : écris « TikTok illisible depuis le cloud le JJ/MM (raison) » dans le rapport et dans l'analyse, **sans aucun chiffre inventé**. Seuls les relevés faits à la main par Ilan, datés, font alors foi.
d) **Analyse et classement** : ajoute en tête de `analyse-marche/concepts-qui-marchent.md` une section « Veille du JJ/MM » (nos chiffres par pilier, ce que dit le web, l'état de TikTok, les décisions). Reclasse ensuite chaque file de `idees/banque.md` (`devine_construction`, `fait_expres`, `forme_contre_intuitive`). Pour chaque sujet, vérifie :
   - **saturé** ? (plusieurs vidéos récentes en français, au-delà de 10K likes, sur le même objet) ;
   - **déjà fait par un concurrent** ? (même objet et même angle chez un compte similaire). Si oui, le sujet descend en bas de file avec la mention, ou il passe à un angle vraiment différent, écrit dans la banque.
e) **Refus automatiques** : un sujet déjà publié chez nous (`episodes/*`, cases cochées de la banque) ; un sujet annoncé à la fin d'un épisode précédent (« Prochain objet : … » dans `episodes/*/texte-voix-off-*.txt` et `docs/reference/`), parce qu'Ilan ne veut plus d'annonces ; un sujet de la liste « Refusés ou non retenus par Ilan » ; un sujet hors des trois piliers.

## 2. Choix des 2 sujets du lendemain (J+1)
- Créneaux 10:00 et 18:00 (`config/planning.yaml` → `creneaux.videos`).
- **Rotation des piliers** (`config/planning.yaml` → `rotation`, ordre `devine_construction` → `fait_expres` → `forme_contre_intuitive` → …) :
  - 10:00 = le pilier qui suit `dernier_pilier` (`tableau-de-bord/etat.json`) ;
  - 18:00 = le pilier suivant.
  Le même pilier ne sort donc jamais deux fois d'affilée, et les deux vidéos d'un jour sont toujours de piliers différents. Mets ensuite `dernier_pilier` à jour avec le pilier de 18:00.
- Dans chaque pilier, prends le premier sujet de la file **après le reclassement de la veille**.
- **Format de chaque pilier** (accroche, en-tête de couverture, modèle : `config/planning.yaml` → `piliers`) :
  - `devine_construction` : l'objet est monté pièce par pièce **sans être nommé**. Accroche « Devine ce que je construis. Réponse à la fin. », une pièce = un indice, « Tu as deviné ? » vers les deux tiers, la réponse en chute, puis une boucle sur la première pièce. Ni la couverture, ni les légendes, ni le titre ne donnent la réponse. Modèle du dessin pièce par pièce : ép. 2 (stylo).
  - `fait_expres` : on montre le « défaut », on laisse croire à une erreur, puis on révèle pourquoi c'est voulu. Accroche « Ce n'est pas un défaut. » Modèle de rythme : ép. 1 (ballast : les pierres cassées exprès).
  - `forme_contre_intuitive` : la forme surprend, une fausse piste, puis un chiffre fort ou une expérience simple la justifie. Modèle de rythme : ép. 3 (hublots).
- Si une file est vide, ajoute 5 sujets du même pilier, vérifiés selon 1 d) et 1 e), et note-le.
- Numéro : épisode suivant le dernier dossier `episodes/epNN-*`. Dossier `episodes/epNN-sujet-court/`.

## 3. Pour chacun des 2 épisodes : fond
1. **Faits vérifiés** (`texte-faits-verifies-<sujet>.md`) : recherche web, au moins 2 sources par fait, tableau numéroté « fait | utilisable dans le script | sources », et une section « points divergents » (modèle : épisode 3). Aucun fait non sourcé dans le script.
2. **Script** (`texte-script-episode-NN-<sujet>.md`) et **voix off** (`texte-voix-off-enzo-episode-NN-<sujet>.txt`), 130 à 150 mots (environ 55 à 60 s de voix ; la vidéo doit faire entre 30 et 60 s, voix + 2,2 s). Recette du README § 5 : accroche en 2 s, promesse, révélations toutes les 3 à 5 s, détail surprenant à mi-parcours, chute qui boucle, dernière phrase = **un simple appel à s'abonner, sans jamais nommer de prochain objet** (décision d'Ilan du 3 nov. ; exemple : « Abonne-toi : il y a un secret d'ingénieur dans chaque objet. »). Nombres écrits en toutes lettres dans la voix off.
3. **Légendes** (`texte-description-episode-NN-<sujet>.txt`) : bloc INSTAGRAM, bloc TIKTOK (court), TEXTE DE COUVERTURE (même format que l'épisode 3), 5 hashtags.
4. **Fiche** `episode.yaml` depuis `episodes/_modele/episode.yaml` : concept, créneau, date_publication, accroche, couverture_lignes `[ligne1, MOT-CLÉ, ligne3]`, mot_cle_vert, chemins des fichiers. Champ `concept` = l'identifiant du pilier. `couverture_entete` = l'en-tête du pilier (`config/planning.yaml` → `piliers`). Pour `devine_construction`, la couverture ne nomme pas l'objet (ex. `["DEVINE CE QUE", "JE CONSTRUIS", "RÉPONSE À LA FIN"]`, mot vert `JE CONSTRUIS`) et `miniature.py` ne dessine qu'une seule pièce.
5. **Stories** `stories.yaml` (modèle : `episodes/ep03-hublots/stories.yaml`) : une story par épisode. Celle de l'épisode de 10:00 sort à 12:00, celle de l'épisode de 18:00 sort à 19:00. Question **écrite dans l'image** (pas de sticker, limite de l'API), 3 choix courts dont un seul juste (ou « Les deux »), pied de page court. Vérifie que la bonne réponse est dans les faits vérifiés.

## 4. Pour chacun des 2 épisodes : images et son
1. `miniature.py` : fonction `dessin(c)` de l'objet, centrée vers y = 1232, dans la zone y 985 à 1480 (outils de `render/engine/head.py` ; modèle : épisode 3).
2. `scene.py` : la vidéo, sur le modèle de `episodes/ep03-hublots/scene.py` (mêmes légendes karaoké, mêmes repères pris dans `words.json`, aucune durée codée en dur). `devine_construction` : l'objet apparaît pièce par pièce à chaque mot-repère, et son nom ne s'affiche qu'à la chute. `fait_expres` : le « défaut » d'abord, puis la fausse piste et la révélation. `forme_contre_intuitive` : la forme, la fausse piste, le chiffre ou l'expérience.
3. Voix et alignement d'abord : `python render/engine/build.py episodes/epNN-sujet --etape voix` puis `--etape align`. Prévisualise ensuite : `python render/engine/preview.py episodes/epNN-sujet t1 t2 … t6` (6 instants clés, en secondes) → `work/<épisode>/preview.png`. Regarde la planche, corrige les chevauchements, les textes coupés et les éléments hors cadre (zone utile x 60 à 1020).
4. Lance `python render/engine/build.py episodes/epNN-sujet` (les étapes déjà faites sont sautées : son → rendu par segments de 200 images → export).
   - **Voix** : `tts.py` essaie Enzo, puis les voix graves de `config/voix.json`. Il vérifie lui-même (transcription Gemini du début) que le modèle n'a pas lu la consigne de style à voix haute, et régénère sinon. Ne synthétise **jamais une phrase isolée** : sur un texte court, le modèle lit la consigne. Pour corriger une seule phrase, regénère la voix off complète et découpe la phrase dans les silences. En cas d'erreur réseau ou HTTP 429/500/503 : 4 réessais (attente 10 s, 30 s, 60 s, 120 s). Note la voix retenue.
   - **Alignement** : méthode de l'épisode 2 (pics de syllabes, `peak_align`). Vérifie que les débuts de mots croissent et que le dernier mot tombe dans la dernière seconde de la voix.
   - **Rendu** : si la session est interrompue, relance la même commande : les segments déjà faits sont repris (`work/<épisode>/seg_*.mp4`).
   - Si la vidéo dépasse 62 s, raccourcis la voix off (supprime une phrase secondaire), efface `work/<épisode>/` et relance.
5. `python render/engine/thumb.py episodes/epNN-sujet` puis `python render/engine/story.py episodes/epNN-sujet`.
6. Contrôles : `ffprobe` (1080×1920, 30 ips, piste audio AAC, durée 30 à 62 s), `video-instagram.mp4` sous 10 Mo, 4 images extraites de la vidéo regardées, miniature et story regardées.

## 5. Hébergement des médias
1. Copie dans un dossier temporaire, en les **renommant** `epNN-video.mp4`, `epNN-miniature.png`, `epNN-story.png`, les fichiers des 2 épisodes (6 fichiers).
2. `scripts/publish_media.sh <les 6 fichiers>` : la branche `media` ne contient plus que ces 6 fichiers (les médias d'aujourd'hui sont déjà publiés à 20 h 30, la dernière story sortant à 19:00).
3. Lance le workflow `verify-media` (outil GitHub `actions_run_trigger`, `workflow_id: verify-media.yml`, `ref: claude/brave-hawking-nxc8u4`, `inputs: {"branch": "media"}` ; la branche `media` orpheline ne contient pas le workflow. Le proxy de la session renvoie 403 sur jsDelivr : seul ce workflow fait foi), attends sa fin et vérifie que les 6 lignes sont `OK` (HTTP 200, video/mp4 ou image/png). Sinon : 3 réessais à 1 min d'intervalle, puis alerte.

## 6. Programmation Metricool (J+1)
**Garde-fou** : ne programme **que si** `config/planning.yaml` contient `programmation_active: true`. Sinon, écris dans `etat.json` « programmation en attente de validation d'Ilan » et passe à l'étape 7. Ne crée jamais de brouillon ni de post « for review » à la place.

Si elle est active, marque `blogId: "7844668"`, fuseau `Europe/Paris`, avec l'outil `createScheduledPost` :
- **Vidéo** (une par créneau 10:00 et 18:00), un seul post pour les deux réseaux : `providers: [{"network":"instagram"},{"network":"tiktok"}]`, `media: [URL jsDelivr de la vidéo]`, `videoThumbnailUrl: URL jsDelivr de la miniature`, `text` : légende INSTAGRAM, `instagramData: {"type":"REEL","showReelOnFeed":true,"isAiGenerated":true}`, `tiktokData: {"privacyOption":"PUBLIC_TO_EVERYONE","title":<légende TIKTOK>,"isAigc":true}`, `publicationDate: {"dateTime":"AAAA-MM-JJT10:00:00","timezone":"Europe/Paris"}`, `autoPublish: true`. Si TikTok refuse la miniature (`VIDEO_THUMBNAIL_NOT_APPLICABLE`), programme la vidéo TikTok à part avec `videoCoverMilliseconds: 1500`.
- **Story** (12:00 et 19:00) : `providers: [{"network":"instagram"}]`, `media: [URL de la story]`, `instagramData: {"type":"STORY","isAiGenerated":true}`, **sans `text`**.
- Avant de créer : `getScheduledPosts` sur J+1 pour ne rien programmer en double. Note chaque identifiant renvoyé dans `episode.yaml` (`metricool`) et dans `etat.json`.

## 7. Mémoire et rapport
1. `episode.yaml` : statut (`programme` si programmé, sinon `pret`), date, créneau, voix retenue, durée, taille, URL des médias.
2. `idees/banque.md` : coche les 2 sujets avec le numéro d'épisode (et garde le reclassement de la veille).
3. `tableau-de-bord/etat.json` (schéma décrit dans `tableau-de-bord/README.md`) : `mis_a_jour`, `dernier_pilier`, `derniere_veille` (date, sources lues ou illisibles, décisions), `derniere_production` (date, épisodes, durées, voix, URL), `programme_metricool`, `alertes`, `historique` (ajoute une ligne).
4. Commit clair (« Production du JJ/MM : épNN <sujet> + épNN <sujet> ») et `git push -u origin claude/brave-hawking-nxc8u4` (4 réessais en cas d'erreur réseau : 2 s, 4 s, 8 s, 16 s). Ne commite jamais `work/` ni la clé.
5. Termine par un rapport court en français : résumé de la veille (dont l'état de TikTok), sujets et piliers, durées, voix retenue, URL publiques, état de la programmation, alertes.

## Interdits
- Afficher, journaliser ou écrire `GEMINI_API_KEY`.
- Programmer dans Metricool si `programmation_active` n'est pas `true`.
- Publier un fait absent du fichier de faits vérifiés, ou un chiffre de veille qui n'a pas été lu.
- Produire un sujet hors des trois piliers, ou annoncer un prochain objet en fin de vidéo.
- Modifier la direction artistique (papier Seyès, encre noire, vert 18,150,100, polices Caveat et Patrick Hand).
