# CLAUDE.md - Trekr : "J'ai 40 minutes"

## Le produit (decision du 10 novembre 2026, d'apres les mots d'Hasnae)

Elle veut : des lieux a visiter comme une locale, hors de la masse, en
optimisant son temps avec des propositions a la minute quand elle en a peu,
du visuel anime, l'ecologie sans greenwashing. Elle a dit qu'elle
n'utiliserait PAS un simple guide declenche au passage.

Donc : on dit combien de temps on a (20/40/60/90 min) ; Trekr compose une
boucle a pied depuis la position, minute par minute, qui ecarte les lieux
tres connus, et ramene a l'heure. Suivi en direct optionnel.

## Fichiers

- site/index.html : "J'ai X minutes". build() = boucle gloutonne (marche,
  temps sur place par categorie, retour garanti), trace SVG anime, suivi GPS.
- site/guide.html : guide declenche au passage (secondaire).
- site/gares.html : recherche par gare (secondaire).
- scripts/extract_lieux.py : fiches DATAtourisme (../../carbon/) -> sources/lieux.json
- scripts/notoriete.py : sources/wd/*.json (Wikidata) -> sources/notoriete.json
- scripts/tuiles.py : lieux + notoriete -> site/data/t/ (cases de 0,1 degre)
- scripts/croiser.py : lieux x gares -> site/data/g/
- En ligne : https://hasnaech.github.io/trekr-gares/ (push sur main = republication)
- Previsualisation : configuration "trekr-gares" (port 4173)

## Notoriete ("hors des foules")

Champ `no` = nombre d'editions de Wikipedia ayant une page sur le lieu
(Wikidata, element a moins de 150 m dont le nom ressemble). Plus de 20 =
tres connu, ecarte en mode calme. Paris uniquement pour l'instant.
Les fichiers sources/wd/ viennent de 5 requetes SPARQL (wikibase:box par
quart de Paris, champs item, itemLabel, lat, lon, sitelinks) ; ils ne sont
pas dans git. PIEGE : l'API de Wikipedia limite vite les appels (429), et
le Python de python.org n'a pas les certificats : passer par curl.
Le rapprochement par nom est volontairement large : mieux vaut ecarter a
tort un lieu obscur qu'envoyer quelqu'un dans la foule.

## Regles

Aucune donnee inventee ; Trekr lit la fiche officielle. Notoriete n'est pas
frequentation : toujours le dire. Ecologie : seulement "tout a pied" et
"repartir les visites", aucun chiffre de CO2 evite. Pas de cameras : compter
des gens sur des webcams publiques sans accord n'est pas legal en France
(dossier d'arbitrage, sections 19 a 21). Francais, pas de tiret long.

## Limites connues

Pas d'horaires d'ouverture ; fiches d'aout 2025 ; certaines fiches sont des
expositions temporaires ou commerciales ; ce sont des lieux d'offices de
tourisme, pas des adresses d'habitants ; teste sur poste, pas encore en
marchant avec un vrai GPS ; application web (ecran allume).
Pistes : adresses proposees par des habitants, horaires, notoriete hors
Paris, affluence reelle par partenariat, application installable.
