# Concepts qui marchent sur TikTok

> Analyse faite par **Ilan le 3 nov. 2026** dans la recherche TikTok. Chiffres = **likes visibles dans les résultats
> de recherche**, en ordre de grandeur (ni vues, ni rétention). À recouper chaque mois.
> Complète [`comptes.md`](comptes.md) (comptes similaires).

## Veille du 03/11/2026 (première veille, faite à la main dans la session cloud)

**Nos chiffres** (Metricool, publications du 4 oct. au 3 nov., lus le 3 nov.) :

| Épisode | Pilier (a posteriori) | Instagram : vues | Partages | Enregistrements | Durée moy. regardée | TikTok : vues | Partages |
|---|---|---|---|---|---|---|---|
| Ép. 1, ballast | `fait_expres` (pierres cassées exprès) | 1 873 | 2 | 2 | 19,4 s | 53 | 0 |
| Ép. 2, stylo | construction sans mystère | 134 | 0 | 0 | 9,2 s | 53 | 0 |

- La rétention en % (`IGRE27`) et le taux de visionnage complet TikTok (`TKPO13`) sont **vides** pour l'instant.
- Deux publications seulement : c'est trop peu pour conclure. Le ballast, dont l'angle est « c'est fait exprès », est retenu deux fois plus longtemps que le stylo.

**Web** (recherche web) : utile pour les faits (le trou du pistolet de la pompe à essence s'explique par l'effet Venturi, d'après Caradisiac), mais **elle n'indexe presque pas TikTok**. Elle ne suffit pas à juger si un sujet est saturé sur TikTok.

**TikTok** : **illisible depuis le cloud le 03/11**. Le proxy de l'environnement refuse `www.tiktok.com`, `tiktok.com` et `m.tiktok.com` (403 `connect_rejected`). Aucun chiffre TikTok n'a été relevé automatiquement ; les chiffres ci-dessous sont ceux d'Ilan.

**Décisions** : trois piliers officiels, en rotation (voir plus bas). La serrure à goupilles en mystère passe en tête du pilier `devine_construction`.

## Relevé TikTok d'Ilan (3 nov.)

| Rang | Concept | Exemples relevés (likes) | Ce qu'on en retient |
|---|---|---|---|
| 1 | **« C'est fait exprès »** : un défaut apparent qui est en fait voulu | Archive66, pièces volontairement mal ajustées : **11,2K** · BeeX, « Engineers hate this trick » : **36K** · barrage au trou central : **22K** · compresseur de clim : **10,1K** | Ce qui marche le mieux. Accroche type : **« Ce n'est pas un défaut. »** |
| 2 | **Formes et structures contre-intuitives** | Poutre en I, même acier mais 29 fois plus rigide : **26,3K** · portes de cité qui s'ouvrent vers l'intérieur : **18,9K** · escalier en spirale : **6,2K** · trous sur les routes neuves : **3,4K** | Une forme bizarre et un chiffre fort |
| 3 | **Construction pièce par pièce AVEC mystère** : « devine ce que je construis, réponse à la fin » | sciences&découvertes : **150,8K**, en français, très au-dessus de tout le reste · serrure et clé en 3D (Jared Owen) : **65K** · compte français « Pixel », « on construit la serrure pièce par pièce » : **62 likes, publié il y a 20 h** | Le mystère fait rester jusqu'au bout. **La serrure, vite, et avec un autre angle que Pixel** |
| 4 | Humour de la sur-ingénierie (hors piliers) | Unnecessary Engineering : **241K** | Possible plus tard, **pas prioritaire** |
| 5 | Hublots d'avion (hors piliers) | Une dizaine de vidéos en français en une semaine ; la plus vue fait **52K** (en chanson), les autres **7K ou moins** | **Sujet saturé**, peu différenciant. L'ép. 3 reste notre épisode d'essai validé, mais on ne refait pas ce genre de sujet déjà très couvert |

## Ce que ça change pour nous (décision d'Ilan du 3 nov.)

**Trois piliers officiels, et seulement trois** (`config/planning.yaml` → `piliers`), en rotation stricte
`devine_construction` → `fait_expres` → `forme_contre_intuitive`. Jamais deux fois le même pilier d'affilée, jamais deux fois dans la même journée.

1. **« Devine ce que je construis »** : construction pièce par pièce, l'objet n'est nommé qu'à la fin. Notre meilleur repère : sciences&découvertes, 150,8K.
2. **« Ce n'est pas un défaut, c'est fait exprès »** : on montre le défaut, on laisse croire à une erreur, puis on révèle que c'est voulu.
3. **« Les formes contre-intuitives »** : la forme surprend, puis un chiffre ou une expérience simple la justifie.

- **La serrure à goupilles en mystère, en premier.** Elle se distingue de Pixel (construction annoncée, sans mystère) et de Jared Owen (3D, en anglais) par trois choses : le mystère, notre papier Seyès dessiné à la main, et la chute « c'est la serrure de ta porte d'entrée ».
- **Écartés** : tout sujet hors piliers, dont les « pourquoi c'est rond » ; les sujets saturés, comme les hublots ; les sujets déjà traités par un concurrent, sauf avec un angle vraiment différent.
- **Plus d'annonce du prochain objet** : la fin de chaque vidéo est un simple appel à s'abonner.
- **Veille automatique** avant chaque production (étape 1 de `pipeline/taches/soir.md`) : nos statistiques Metricool, la recherche web, puis TikTok s'il est accessible. Chaque veille ajoute une section datée en tête de ce fichier.
