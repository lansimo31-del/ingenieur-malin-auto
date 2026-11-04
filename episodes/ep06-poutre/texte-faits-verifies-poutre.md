# Faits vérifiés : la poutre en I (épisode 6, pilier « Les formes contre-intuitives »)

Recherche du 4 nov. 2026 (soir). Les pages ont été lues par résumé de moteur de recherche (les sites tiers ne sont pas tous joignables depuis le cloud) : sources secondaires. Les deux chiffres du script (225 et 29) sont **calculés** par nous à partir de la formule de la rigidité et des données d'un profilé du commerce, pas repris d'une vidéo.

| # | Fait retenu | Utilisé | Sources |
|---|---|---|---|
| 1 | Dans une poutre en I, les semelles reprennent l'essentiel du moment de flexion ; l'âme reprend surtout l'effort tranchant | oui | Wikipédia (I-beam) ; Université de Waikato (blog physique) |
| 2 | Près de l'axe neutre, la matière est peu sollicitée : il en faut peu, d'où l'âme mince | oui | Wikipédia (I-beam) ; Real Engineering (« Why are I-beams shaped like an I ? ») |
| 3 | La rigidité en flexion dépend du moment quadratique I, qui compte la distance de la matière à l'axe au carré ; plus I est grand, moins la poutre fléchit (même matière, même portée, même charge) | oui | Wikipédia (I-beam, second moment of area) ; Real Engineering |
| 4 | Rectangle : I = b·h³/12. Une règle de 30 mm de large sur 2 mm : sur la tranche / à plat = (30/2)² = **225** | oui, avec « environ » et ses dimensions | formule standard (résistance des matériaux) ; calcul refait en Python le 4/11 |
| 5 | IPE 200 : hauteur 200 mm, largeur 100 mm, âme 5,6 mm, semelle 8,5 mm, section 28,48 cm² (22,4 kg/m), Iy = 1 943 cm⁴ | oui | beamdimensions.com ; stad.fr ; fiches ArcelorMittal / British Steel (via moteur de recherche) |
| 6 | Barre carrée pleine de même section : côté √28,48 = 5,34 cm, I = A²/12 = 67,6 cm⁴. Rapport 1 943 / 67,6 = **28,7 ≈ vingt-neuf** | oui (« vingt-neuf fois plus rigide », même poids = même section) | calcul refait en Python le 4/11 à partir des faits 4 et 5 |

## Points divergents
- Le « 29 fois » relevé par Ilan sur TikTok (poutre en I, 26,3K likes, 3 nov.) n'a pas été retrouvé par la recherche web ; nous le retrouvons toutefois par le calcul ci-dessus (28,7). On ne cite aucune vidéo.
- Le rapport dépend du profilé comparé : avec un autre profilé ou une autre barre, le chiffre change. Le script précise donc « vingt centimètres de haut » et « barre carrée pleine de même poids ».
- Règle sur la tranche : en vrai, une règle trop fine se tord de côté ; le script ne parle que de rigidité à la flexion.

## Écarté
- Toute formule de résistance (rupture) : le script ne parle que de rigidité.

## Sources
- https://en.wikipedia.org/wiki/I-beam
- https://blog.waikato.ac.nz/physicsstop/?p=479
- https://rosetta.to/u/realengineering/why-are-i-beams-shaped-like-an-i
- https://www.beamdimensions.com/database/European/Steel/IPE_beams/IPE_200
- https://www.stad.fr/en/sections-products-ranges-ipe
- https://www.britishsteel.co.uk/wp-content/uploads/2026/02/british-steel-european-ipe-sections-datasheet.pdf
