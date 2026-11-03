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

> ⚠️ Tant qu'Ilan n'a pas validé l'épisode d'essai, **rien n'est programmé dans Metricool**.

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
| `stories/` | Production des 2 stories quotidiennes |
| `tableau-de-bord/etat.json` | État du pipeline lu par le tableau de bord |
| `analyse-marche/` | Comptes similaires, formats gagnants, créneaux libres |
| `scripts/` | Code exécutable (rendu, voix, programmation), à venir |

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

- [x] **0. Structure du dépôt et plan** (ce commit)
- [x] **1. Récupérer les sources** : docs, scripts, faits vérifiés, moteur de rendu et polices
- [x] **2. Analyse du marché** v1 → `analyse-marche/comptes.md`
- [ ] **3. Voix** : Gemini TTS (`render/engine/tts.py`, `config/voix.json`). **Bloqué** : (a) la clé `GEMINI_API_KEY` n'est lue qu'au démarrage d'une session, donc il faut une nouvelle session ; (b) le nom de la voix prédéfinie Gemini qui correspond à « Enzo » reste à confirmer
- [x] **4. Rendu** : moteur générique `render/engine/` (testé sur l'ép. 2 : environ 0,5 s par image sur 4 cœurs, soit environ 15 min par vidéo d'une minute)
- [x] **5. Miniature et légendes** de l'ép. 3 (`episodes/ep03-hublots/`)
- [x] **6. Hébergement des médias** : branche `media` + jsDelivr, vérifié (`verify-media`)
- [ ] **7. Tableau de bord** (page publiée, alimentée par `tableau-de-bord/etat.json`)
- [ ] **8. Essai à blanc** (ép. 3, hublots) : faits, script, miniature, légendes, scène et hébergement prêts ; reste voix → alignement → rendu → export → validation d'Ilan, sans programmation
  - Commande : `python render/engine/build.py episodes/ep03-hublots` (puis `scripts/publish_media.sh` et le workflow `verify-media`)
- [ ] **9. Activation** des Routines du soir et du matin, puis première programmation Metricool
