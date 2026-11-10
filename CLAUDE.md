# CLAUDE.md - Trekr : le guide qui se declenche sur votre passage

Idee d'Hasnae (10 novembre 2026) : "une application avec des points qui se
declenchent a chaque moment ou on passe devant un lieu, un peu comme un
guide". Elle a rejete le guide Maroc ("fade, une IA peut le faire") et la
recherche par gare ("tout le monde ne part pas d'une gare"). Le guide est
la page d'accueil ; la recherche par gare reste en page secondaire.

- site/index.html : le guide. Geolocalisation continue, charge les tuiles
  autour de la position, declenche le lieu non encore croise le plus proche
  dans le rayon choisi (80/150/300 m), carte + vibration + voix (synthese
  vocale du navigateur, fr-FR). Demonstration : position simulee a Colmar.
- site/gares.html : recherche par gare (lieux a moins de 1,5 km).
- scripts/extract_lieux.py : fiches DATAtourisme (dossier ../../carbon/)
  -> sources/lieux.json (52 230 lieux)
- scripts/tuiles.py : lieux -> site/data/t/<i>_<j>.json (cases de 0,1 degre)
- scripts/croiser.py : lieux x gares x frequentation -> site/data/g/
- Un fichier HTML par page, JS natif, aucune dependance, aucun traceur.
- Previsualisation : configuration "trekr-gares" (port 4173).
- En ligne : https://hasnaech.github.io/trekr-gares/ (chaque push sur main
  republie via .github/workflows/pages.yml).

Regles : aucune donnee inventee, Trekr lit la fiche officielle et ne redige
rien ; afficher la date de la fiche et "declare" pour l'accessibilite ;
pas de tiret long ; francais ; la position ne quitte jamais le telephone.

Limites connues : application web, donc suivi seulement page ouverte et
ecran allume (une vraie application mobile est necessaire pour le suivi en
arriere-plan) ; fiches d'aout 2025 ; pas de carte ; teste en simulation
uniquement, pas encore en marchant avec un vrai GPS.
Pistes : application installable, carte, fiches a jour (cle DATAtourisme),
textes audio plus longs, lieux hors France.
