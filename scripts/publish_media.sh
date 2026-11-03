#!/usr/bin/env bash
# Met en ligne les médias à servir à Metricool et supprime tout le reste.
# Usage : scripts/publish_media.sh fichier1.mp4 fichier2.png ...
#   -> liste COMPLÈTE des fichiers qui doivent rester en ligne (ceux déjà publiés et vérifiés sont simplement omis).
# Principe : la branche `media` est remplacée à chaque fois par UN commit orphelin (push forcé).
#   Les anciens fichiers disparaissent de la branche, et le dépôt ne grossit pas.
# Les URL publiques sont servies par jsDelivr, verrouillées sur le SHA du commit :
#   https://cdn.jsdelivr.net/gh/<repo>@<sha>/<fichier>   (Content-Type vérifié : video/mp4, image/png)
# Ensuite : lancer le workflow verify-media (branche media) et lire son résumé avant de programmer.
set -euo pipefail
[ $# -ge 1 ] || { echo "usage : $0 fichier..."; exit 1; }
REMOTE=$(git remote get-url origin); REPO=$(echo "$REMOTE" | sed -E 's#.*github.com[/:]##; s#\.git$##')
T=$(mktemp -d); trap 'rm -rf "$T"' EXIT
for f in "$@"; do
  case "$f" in *.mp4|*.png|*.jpg) ;; *) echo "type non accepté : $f"; exit 1;; esac
  sz=$(stat -c %s "$f"); [ "$sz" -lt 10000000 ] || { echo "$f dépasse 10 Mo ($sz octets)"; exit 1; }
  cp "$f" "$T/$(basename "$f")"
done
cd "$T"
git init -q -b media . && git remote add origin "$REMOTE"
git add -A && git -c user.name="Ingénieur Malin (auto)" -c user.email="noreply@users.noreply.github.com" commit -qm "media: $(date -u +%FT%TZ)"
git push -f -q origin media:refs/heads/media
SHA=$(git rev-parse HEAD)
echo "SHA=$SHA"
for f in "$@"; do echo "https://cdn.jsdelivr.net/gh/$REPO@$SHA/$(basename "$f")"; done
