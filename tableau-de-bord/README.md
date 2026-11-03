# Tableau de bord

- `etat.json` : état du pipeline, écrit par la tâche du soir et par la tâche du matin.
- `index.html` : page qui lit `etat.json` (depuis GitHub, branche `claude/brave-hawking-nxc8u4`) et l'affiche :
  validation, prochain programme, dernière production, dernière vérification, alertes, statistiques, historique.
  À ouvrir dans un navigateur ; elle se met à jour seule à chaque commit.

## Schéma de `etat.json`

| Clé | Contenu |
|---|---|
| `mis_a_jour` | date et heure ISO de la dernière écriture |
| `pipeline_actif` | `true` quand les deux Routines sont activées |
| `programmation_active` | copie de `config/planning.yaml` |
| `dernier_pilier` | `devine_construction`, `fait_expres` ou `forme_contre_intuitive` (sert à la rotation) |
| `derniere_veille` | `{date, metricool, web, tiktok, decisions}` ; `tiktok` vaut « illisible (raison) » quand TikTok n'est pas accessible |
| `prochaine_production` / `prochaine_verification` | date et heure ISO |
| `derniere_production` | `{date, episodes: [{numero, sujet, concept, creneau, duree_s, taille_mo, voix, video, miniature, story}]}` |
| `derniere_verification` | `{date, resultat, details}` |
| `programme_metricool` | `[{date, heure, type, reseaux, episode, post_id}]` |
| `stats` | `{periode, instagram: {vues_moy}, tiktok: {vues_moy}, meilleur_episode, meilleur_concept}` |
| `alertes` | liste de phrases (vide si tout va bien) |
| `historique` | `[{date, tache, resume}]`, la plus récente en dernier |
