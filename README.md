# Ingénieur Malin : automatisation des publications

Comptes : Instagram **@ingenieur.malin**, TikTok **@ingenieur.malin_off**
Concept : **« Pourquoi c'est conçu comme ça ? »**, de la vulgarisation d'ingénierie sur les objets du quotidien.

Ce dépôt contient tout le système de production et de publication. Il tourne entièrement
dans le cloud. L'ordinateur d'Ilan n'est jamais nécessaire.

---

## 1. Décisions prises (Ilan)

| Sujet | Décision |
|---|---|
| Exécution | 100 % cloud, sans l'ordinateur d'Ilan |
| Volume | **2 vidéos/jour** (Reel Instagram + TikTok) et **2 stories/jour** (Instagram) |
| Programmation | Dans **Metricool**, **24 h à l'avance** : marque `ingenieur.malin`, id `7844668`, fuseau `Europe/Paris` |
| Horaires | Ceux que recommande Metricool (voir § 4) |
| Rythme | **Production chaque soir**, **vérification chaque matin** |
| Suivi | Un **tableau de bord** du projet |
| Direction artistique | La même que les **épisodes 1 (ballast)** et **2 (stylo)** |
| Concepts | En **alternance** : ① *construction* d'un objet pièce par pièce, ② *pourquoi c'est conçu comme ça* |
| Rétention | Des vidéos qui gardent en haleine jusqu'à la fin |
| Veille | Une **analyse du marché** des comptes similaires → [`analyse-marche/comptes.md`](analyse-marche/comptes.md) |
| Voix | **Enzo**, Google Gemini TTS, style calme et clair. Clé API Gemini enregistrée par Ilan dans les secrets de l'environnement (jamais dans le dépôt) |
| Médias | **GitHub** (ce dépôt public) : branche `media` + CDN jsDelivr, anciens fichiers supprimés à chaque mise en ligne. **Pas de Supabase** (le connecteur sert un autre projet) |
| Rendu | Moteur Python d'Ilan (Pillow + ffmpeg) dans [`render/`](render/HOWTO.md) |
| Objectif | **Zéro intervention manuelle** d'Ilan une fois le pipeline validé |

> ⚠️ Tant qu'Ilan n'a pas validé l'épisode d'essai, **rien n'est programmé dans Metricool** (`programmation_active: false` dans `config/planning.yaml`, Routines désactivées). Marche à suivre : § 8.

**Limites connues** (voir [`docs/sources/texte-plan-automatisation-cloud.md`](docs/sources/texte-plan-automatisation-cloud.md)) :
- Les stories TikTok ne sont pas programmables via Metricool : **stories sur Instagram seulement**.
- Les stickers « question » d'Instagram ne passent pas par l'API : la question est **écrite dans l'image** de la story.
- Instagram ne permet plus de changer la couverture depuis un ordinateur : la bonne miniature est envoyée **dès la programmation**.
- 2 vidéos par jour représentent beaucoup de rendu : la durée et le coût sont à surveiller la première semaine.

---

## 2. Architecture

```
                ┌──────────── CHAQUE SOIR (20 h 30) ────────────┐
idees/banque.md │ 01 idée → 02 script → 03 voix → 04 rendu →    │
                │ 05 miniature → 06 programmation Metricool J+1 │
                └───────────────────────────────────────────────┘
                ┌──────────── CHAQUE MATIN (7 h 30) ────────────┐
                │ 07 vérification : 2 vidéos + 2 stories du     │
                │ jour présentes dans Metricool ? stats J+1/J+7 │
                │ → tableau-de-bord/ + alertes                  │
                └───────────────────────────────────────────────┘
```

- **Déclencheurs** : deux Routines Claude Code planifiées (cron, fuseau Europe/Paris), chacune
  ouvre une session cloud sur ce dépôt. Rien ne tourne en local.
- **Rendu** : dans le conteneur cloud (Python, Pillow, ffmpeg), avec le moteur des épisodes 1 et 2
  (`render/`), rendu par segments de 200 images avec reprise possible.
- **Voix** : Gemini TTS, voix Enzo, via la clé API placée dans les secrets de l'environnement.
- **Hébergement des médias** : Metricool demande une URL publique pour chaque vidéo et chaque image.
  `scripts/publish_media.sh` remplace la branche `media` par **un seul commit orphelin** (push forcé) : les
  anciens fichiers disparaissent et le dépôt ne grossit pas. Les fichiers sont servis par jsDelivr, verrouillés
  sur le SHA du commit : `https://cdn.jsdelivr.net/gh/lansimo31-del/ingenieur-malin-auto@<sha>/<fichier>`.
  Le workflow `verify-media` contrôle ces URL depuis un vrai serveur (HTTP 200, `video/mp4`, `image/png`, lecture
  partielle). Testé le 3 nov. 2026. Les adresses `raw.githubusercontent.com` (mp4 en `application/octet-stream`)
  et les assets de Release (tout en `octet-stream`) ne conviennent pas. Limite connue de jsDelivr : 20 Mo par fichier ;
  les vidéos d'envoi font moins de 10 Mo.
- **Publication** : connecteur Metricool (`createScheduledPost`). Instagram et TikTok sont tous
  deux reliés à la marque 7844668.
- **Mémoire** : chaque épisode a sa fiche `episodes/epNN-sujet/episode.yaml`, et chaque exécution
  est commitée dans le dépôt, ce qui garde un historique.

## 3. Structure du dépôt

| Dossier | Rôle |
|---|---|
| `docs/sources/` | Plan d'automatisation et règles miniature/publication |
| `docs/reference/` | Scripts, voix off, faits vérifiés et légendes des ép. 1 et 2 |
| `render/` | Moteur de rendu Python des ép. 1 et 2, polices, miniature ([HOWTO](render/HOWTO.md)) |
| `config/planning.yaml` | Marque Metricool, cadence, créneaux, alternance des concepts, heures des tâches |
| `direction-artistique/` | Charte des ép. 1 et 2 (Seyès, encre noire, vert 18,150,100) |
| `episodes/` | Une fiche par épisode (modèle dans `_modele/`), ép. 1 et 2 comme référence |
| `idees/banque.md` | Réserve de sujets, classés par concept |
| `pipeline/01…07` | Les 7 étapes de production, avec un README pour chacune |
| `stories/` | Production des 2 stories quotidiennes (générateur : `render/engine/story.py`, contenu : `stories.yaml` de chaque épisode) |
| `tableau-de-bord/` | `etat.json` (état du pipeline, [schéma](tableau-de-bord/README.md)) et `index.html` (page qui l'affiche) |
| `analyse-marche/` | Comptes similaires, formats gagnants, créneaux libres |
| `scripts/` | `publish_media.sh` : hébergement des médias (branche `media` + jsDelivr) |
| `pipeline/taches/` | Prompts complets des Routines : [`soir.md`](pipeline/taches/soir.md) (20 h 30) et [`matin.md`](pipeline/taches/matin.md) (7 h 30) |
| `requirements.txt` | Dépendances Python du moteur (pillow, numpy, scipy, pyyaml) |

## 4. Créneaux Metricool (lus le 3 nov. 2026, semaine du 4 au 10 nov.)

Sur les deux réseaux, l'audience culmine à **10 h** et **18 h**, tous les jours. Le week-end,
elle est environ deux fois plus faible.

| Contenu | Créneau | Réseaux |
|---|---|---|
| Vidéo 1 | 10:00 | Instagram Reel + TikTok |
| Story 1 | 12:00 | Instagram |
| Vidéo 2 | 18:00 | Instagram Reel + TikTok |
| Story 2 | 19:00 | Instagram |

Les créneaux sont recalculés chaque semaine à partir de Metricool et mis à jour dans `config/planning.yaml`.

## 5. Recette d'une vidéo qui retient

1. **0–2 s : accroche.** Une question ou une image intrigante (« Pourquoi y a-t-il des cailloux sous les rails ? »).
2. **Promesse.** Ce qu'on va comprendre, sans le dire tout de suite.
3. **Révélations par étapes.** Une nouvelle info toutes les 3 à 5 s, avec une relance visuelle à chaque fois.
4. **Fausse piste ou détail surprenant** à mi-parcours, pour relancer l'attention.
5. **Chute.** La réponse complète, puis une dernière phrase qui renvoie au début (boucle).
6. Sous-titres incrustés et format vertical 1080×1920, entre 30 et 60 s.

Alternance : un créneau *construction* (« On construit un X pièce par pièce »), le suivant
*pourquoi* (« Pourquoi c'est conçu comme ça ? »).

## 6. Feuille de route

- [x] **0. Structure du dépôt et plan**
- [x] **1. Récupérer les sources** : docs, scripts, faits vérifiés, moteur de rendu et polices
- [x] **2. Analyse du marché** v1 → `analyse-marche/comptes.md`
- [x] **3. Voix** : Gemini TTS `gemini-3.8-flash-tts`, voix **Enzo acceptée par l'API** le 3 nov. (aucun repli nécessaire). Repli automatique sur Charon puis les autres voix graves de `config/voix.json` si l'API refuse un jour le nom
- [x] **4. Rendu** : moteur générique `render/engine/` (environ 1 à 2 min par segment de 200 images sur 4 cœurs, soit 12 à 20 min par vidéo d'une minute)
- [x] **5. Miniature, légendes et stories** de l'ép. 3 (`episodes/ep03-hublots/`)
- [x] **6. Hébergement des médias** : branche `media` + jsDelivr, vérifié (`verify-media`)
- [x] **7. Tableau de bord** : `tableau-de-bord/index.html`, alimenté par `etat.json`
- [x] **8. Essai à blanc** (ép. 3, hublots) : voix, alignement, rendu, export, miniature, 2 stories, hébergement faits le 3 nov. **Attend la validation d'Ilan** (adresses dans `tableau-de-bord/etat.json`)
- [ ] **9. Activation** : les 2 Routines existent, **désactivées** (voir § 8). Rien n'est programmé dans Metricool

## 7. Journal des choix (session autonome du 3 nov. 2026)

| Sujet | Choix | Raison |
|---|---|---|
| Clé Gemini | Lue dans `GEMINI_API_KEY` (présence et longueur vérifiées, valeur jamais affichée ni écrite) | Consigne d'Ilan |
| Voix | Enzo acceptée par `gemini-3.8-flash-tts`, 61,0 s de voix | Pas besoin du repli |
| Alignement | Méthode de l'ép. 2 : pics de syllabes et programmation dynamique (`peak_align`), faster-whisper non installé | Consigne ; 140 mots, débuts croissants, dernier mot à 60,1 s |
| Durée | 63,2 s (voix + 2,2 s de respiration finale), soit un peu plus que les 60 s visés | Script validé tel quel ; la tâche du soir raccourcit au-delà de 62 s |
| scipy | Ajouté à `requirements.txt` et installé dans la session | Nécessaire à l'alignement et aux effets d'encre |
| Installation auto | Le hook de démarrage `.claude/settings.json` n'a pas été ajouté (refusé par le contrôle de sécurité de la session). Les prompts des Routines lancent `pip install -r requirements.txt`. Pour l'avoir dans **toutes** les sessions, Ilan peut ajouter cette ligne au script d'installation de l'environnement (réglages de l'environnement cloud) | Ne pas contourner un refus |
| Stories | 2 par jour, Instagram seulement : 12:00 (question sur la vidéo de 10 h), 19:00 (question sur la vidéo de 18 h). Question et 3 choix écrits dans l'image, même papier, même encre, même vert, dessin de la miniature au centre ; rien au-dessus de y = 250 ni sous y = 1700 (interface Instagram) | API sans stickers |
| Programmation | Interrupteur `programmation_active: false` dans `config/planning.yaml` : la tâche du soir produit et héberge, mais ne programme rien tant qu'il est à `false` | Validation d'Ilan en un geste |
| Un post pour deux réseaux | Vidéo envoyée en un seul `createScheduledPost` Instagram Reel + TikTok, miniature par `videoThumbnailUrl`, contenu déclaré généré par IA (`isAiGenerated`, `isAigc`) | Moins d'appels ; obligation de déclaration |
| Hébergement | Chaque soir, la branche `media` ne garde que les 6 médias du lendemain (2 vidéos, 2 miniatures, 2 stories) | Les médias du jour sont tous sortis à 20 h 30 |
| Routines | Créées sans horaire, désactivées, puis horaire ajouté (aucun risque de déclenchement). Nouvelle session à chaque déclenchement, notification push | Consigne : désactivées |
| Vérification des URL | Le proxy de la session cloud renvoie 403 sur jsDelivr : les adresses sont vérifiées par le workflow `verify-media`, lancé depuis la branche de travail avec `branch=media` (la branche `media` orpheline ne contient pas le workflow). Run 41655847774 : 4 × OK | Seule vérification fiable |
| Connecteurs | Les Routines créées depuis cette session ne portent **aucun connecteur** (option refusée pour l'organisation) | Voir § 8, étape 2 |

## 8. Valider l'automatisation (Ilan)

1. **Regarder** la vidéo, la miniature et les 2 stories de l'ép. 3 (adresses dans `tableau-de-bord/etat.json` → `derniere_production`).
2. **Connecteurs des Routines** : sur claude.ai → Routines, ouvrir « Ingénieur Malin : production du soir (20 h 30) » et « Ingénieur Malin : vérification du matin (7 h 30) », ajouter le connecteur **Metricool** (et GitHub si proposé). Sans lui, la tâche du soir ne peut pas programmer et celle du matin ne peut pas vérifier.
3. **Le geste de validation** : passer `programmation_active: true` dans `config/planning.yaml` (commit), puis **activer** les 2 Routines.
4. Facultatif : ajouter `pip install -r requirements.txt` au script d'installation de l'environnement cloud.

Le premier soir après l'activation, la tâche du soir produit les ép. 4 et 5 pour le lendemain (concept `construction` à 10 h, le cadenas à goupilles ; `pourquoi` à 18 h, les plaques d'égout annoncées à la fin de l'ép. 3). L'ép. 3 lui-même n'est pas programmé automatiquement : à programmer à la main ou à demander dans une session.
