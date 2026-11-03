# Plan d'automatisation cloud — @ingenieur.malin (Instagram) et @ingenieur.malin_off (TikTok)

## Décisions de Ilan
- Tout tourne dans le cloud, sans l'ordinateur allumé.
- Publication via Metricool (marque « ingenieur.malin », id 7844668, fuseau Europe/Paris, Instagram + TikTok connectés). Horaires : ceux que recommande Metricool (getBestTimeToPostByNetwork).
- 2 vidéos par jour, programmées 24 h à l'avance dans Metricool (annulables à la main si besoin).
- 2 stories par jour et par réseau : petites questions liées au contenu du compte.
- Même direction artistique que l'épisode 1 (ballast) et l'épisode 2 (stylo) : papier Seyès, encre noire, accent vert.
- Concepts en alternance : « construction d'un objet pièce par pièce » (type stylo) et « pourquoi c'est conçu comme ça » (type ballast, hublots d'avion).
- Vidéos qui gardent en haleine : accroche dans les 3 premières secondes, question ouverte, révélation finale, boucle vers le début.
- Analyse du marché : comptes qui marchent dans le même concept, reproduits avec notre DA.
- Stockage du code et des médias : GitHub (en attente de la connexion à Claude).

## Rythme quotidien
- Soir (production) : choix des 2 concepts du lendemain, faits vérifiés, script, voix, rendu vidéo, miniature, légendes, 2 × 2 stories ; dépôt sur GitHub ; programmation dans Metricool.
- Matin (vérification) : contrôle que les vidéos de la nuit existent, ont la bonne durée et le son, sont programmées sur les deux réseaux ; contrôle des posts de la veille ; mise à jour du tableau de bord.

## Limites connues (à dire à Ilan)
- Les stickers « question » interactifs d'Instagram ne peuvent pas être ajoutés par l'API : la question est écrite dans l'image de la story.
- Les stories TikTok ne sont pas programmables via Metricool : stories Instagram seulement, sauf nouveauté.
- La voix Enzo vient de l'interface Google AI Studio : en cloud il faut une clé API Gemini (à créer et enregistrer par Ilan lui-même) ou une autre voix.
- Metricool a besoin d'adresses publiques pour les vidéos et images : GitHub (dépôt public) les fournira.
- 2 vidéos par jour = beaucoup de rendu et d'usage : à surveiller la première semaine.

## État
- Metricool connecté et lu : OK.
- GitHub : jeton du cloud invalide, connexion à faire par Ilan.
- Voix cloud : à décider.
