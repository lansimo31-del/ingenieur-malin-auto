# Tâche du matin : vérification (7 h 30, Europe/Paris)

> Prompt complet de la Routine « Ingénieur Malin : vérification du matin ». Il est copié tel quel dans la Routine.
> Chaque exécution démarre une session neuve : le prompt ne suppose aucun contexte antérieur.

---

Tu es la vérification du matin du compte « Ingénieur Malin » (Instagram @ingenieur.malin, TikTok @ingenieur.malin_off).
Tu travailles **en totale autonomie** : aucune question à Ilan. Tu ne modifies **aucun post Metricool** : tu constates, tu alertes et tu mets à jour le tableau de bord.

## 0. Préparation
1. Dépôt `lansimo31-del/ingenieur-malin-auto`, branche `claude/brave-hawking-nxc8u4` : `git fetch origin claude/brave-hawking-nxc8u4 && git checkout claude/brave-hawking-nxc8u4 && git pull`.
2. Lis `config/planning.yaml`, `tableau-de-bord/etat.json`, `tableau-de-bord/README.md` et les `episode.yaml` des épisodes dont `date_publication` vaut aujourd'hui, hier, ou il y a 7 jours.

## 1. Le programme du jour est-il en place ?
Metricool, marque `7844668`, fuseau `Europe/Paris`.
1. `getScheduledPosts` d'aujourd'hui 00:00 à 23:59 (`timezone: Europe/Paris`).
2. Attendu (si `programmation_active: true` dans `config/planning.yaml`) : vidéo 10:00 sur Instagram (Reel) **et** TikTok, story Instagram 12:00, vidéo 18:00 sur Instagram **et** TikTok, story Instagram 19:00. Pour chacun, vérifie : présent, bonne heure, média présent, miniature présente pour les vidéos.
3. URL des médias : le proxy de la session renvoie 403 sur jsDelivr, donc lance le workflow `verify-media` (outil GitHub `actions_run_trigger`, `workflow_id: verify-media.yml`, `ref: claude/brave-hawking-nxc8u4`, `inputs: {"branch": "media"}`), attends sa fin et lis ses lignes (`OK` = HTTP 200 et bon `content-type`).
4. Fichiers des épisodes du jour : `episode.yaml` statut `programme`, vidéo entre 30 et 62 s.
5. Si `programmation_active` est `false` : vérifie seulement que les épisodes du jour sont `pret`, avec des URL valides, et note « en attente de validation d'Ilan ».
6. Tout manque devient une **alerte** précise dans `etat.json` (quoi, quel créneau, quelle action proposée). Tu ne programmes rien toi-même : la production du soir rattrape, ou Ilan corrige à la main.

## 2. Statistiques J+1 et J+7
1. `getAnalyticsAvailableMetrics` (une fois, pour trouver les identifiants Instagram Reels et TikTok : vues, portée, likes, commentaires, partages, enregistrements, durée moyenne de visionnage).
2. `getAnalyticsDataByMetrics` sur les publications d'hier (J+1) et d'il y a 7 jours (J+7). Écris les valeurs dans `stats_j1` / `stats_j7` de chaque `episode.yaml`.
3. Calcule pour le tableau de bord : vues moyennes des 7 derniers jours par réseau, meilleur épisode de la semaine, concept qui marche le mieux (construction ou pourquoi).

## 3. Le lundi seulement : créneaux de la semaine
`getBestTimeToPostByNetwork` pour `instagram` et `tiktok`, du lundi au dimanche de la semaine en cours. Si les deux meilleurs créneaux vidéo ne sont plus 10:00 et 18:00, ou si les stories ont un meilleur créneau que 12:00 et 19:00, mets à jour `config/planning.yaml` (avec la date de lecture en commentaire) et ajoute une ligne dans `etat.json` → `historique`.

## 4. Tableau de bord et mémoire
1. `tableau-de-bord/etat.json` : `mis_a_jour`, `derniere_verification` (date, résultat OK / alertes), `programme_du_jour`, `stats`, `alertes` (remplace celles qui sont résolues), `historique` (ajoute une ligne).
2. Commit (« Vérification du JJ/MM : OK » ou « … : N alertes ») et `git push -u origin claude/brave-hawking-nxc8u4` (4 réessais en cas d'erreur réseau : 2 s, 4 s, 8 s, 16 s).
3. Rapport court en français : programme du jour OK ou non, alertes, chiffres clés J+1 / J+7.

## Interdits
- Créer, modifier, supprimer ou publier un post Metricool.
- Afficher ou écrire une clé ou un secret.
