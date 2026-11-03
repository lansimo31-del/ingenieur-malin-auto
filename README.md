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
| Médias | **Supabase Storage**, bucket public, suppression des anciens fichiers une fois publiés |
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
- **Hébergement des médias** : Metricool demande une URL publique pour chaque vidéo et chaque
  image. Les fichiers sont déposés dans un bucket public Supabase Storage, puis supprimés une
  fois publiés.
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
- [ ] **3. Voix** : Gemini TTS, voix Enzo (en attente de la clé API dans les secrets)
- [ ] **4. Rendu** : rendre le moteur générique (chemins, timeline par épisode) et le faire tourner dans le cloud
- [ ] **5. Miniatures et légendes** selon les règles du doc dédié
- [ ] **6. Hébergement des médias** : bucket public Supabase Storage
- [ ] **7. Tableau de bord** (page publiée, alimentée par `tableau-de-bord/etat.json`)
- [ ] **8. Essai à blanc** : un épisode complet produit, **validé par Ilan**, sans programmation
- [ ] **9. Activation** des Routines du soir et du matin, puis première programmation Metricool
