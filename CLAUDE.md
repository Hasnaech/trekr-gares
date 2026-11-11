# CLAUDE.md - Trekr : "J'ai 40 minutes"

## Le produit (decision du 10 novembre 2026, d'apres les mots d'Hasnae)

Elle veut : des lieux a visiter comme une locale, hors de la masse, en
optimisant son temps avec des propositions a la minute quand elle en a peu,
du visuel anime, l'ecologie sans greenwashing. Elle a dit qu'elle
n'utiliserait PAS un simple guide declenche au passage.

Donc : on dit combien de temps on a (20/40/60/90 min) ; Trekr compose une
boucle a pied depuis la position, minute par minute, qui ecarte les lieux
tres connus, et ramene a l'heure. Suivi en direct optionnel.

## Audit utilisateur du 11 novembre 2026 et refonte du 12

Constat (parcours reel sur telephone, canal Saint-Martin a 23h37) : l'outil
proposait un jardin et un atelier de peinture a minuit, aucun cafe, aucune
raison d'y aller, bouton principal a deux ecrans de defilement.
Refonte : on choisit une ENVIE (cafe au calme, verdure, beau a voir, pause
gourmande, livres et galeries, boire un verre, surprise), une duree, une
heure de depart (maintenant ou plus tard). Trekr ne propose que ce qui est
ouvert au moment du passage.

- sources/osm_paris.json : 13 324 lieux de vie OpenStreetMap (Overpass,
  bbox Paris : cafes, bars, boulangeries, patisseries, librairies,
  chocolateries, fromageries, glaciers, galeries, art de rue, points de vue,
  fontaines). Integres par scripts/tuiles.py (champ o:1, oh = horaires,
  ter = terrasse, par = artiste). Les elements avec tag "brand" (chaines)
  sont ecartes. Si overpass-api.de repond 502, reessayer ou utiliser
  overpass.private.coffee.
- index.html : horaires() lit la syntaxe opening_hours courante (jours,
  plages, apres minuit, off ; les regles PH/SH sont ignorees ; formes
  complexes -> inconnu). etat() : ouvert sur / ouvert probable (HABITUEL
  par categorie, signale "a verifier") / ferme. build() : cout = marche +
  repetition + poids de l'envie + notoriete + incertitude ; une pause
  (cafe, bar, boulangerie...) par parcours, deux a 90 min ; deux oeuvres
  d'art de rue au plus. raisons() : une raison par lieu, faits seulement.
- Lien partageable : le parcours est dans l'adresse (#la, lo, t, e, m, h, n)
  et se recompose a l'identique. Bouton "Envoyer ce parcours".
- "C'est parti" est juste sous la carte.
- NE PAS affirmer qu'un cafe est bon ni "independant" : on sait seulement
  qu'il n'a pas de tag de chaine.

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

## Ville en 3D et photos (10 novembre 2026, "aller au-dela des points")

- index.html, init3D() : MapLibre GL 4.7.1 (unpkg) + style OpenFreeMap
  "liberty" (gratuit, sans cle) : batiments OpenStreetMap en volume, trace
  qui avance, survol camera d'etape en etape (fly()), colonnes de lumiere,
  marqueurs = photo du lieu. Repli automatique sur le trace SVG (drawMap)
  si la 3D ne se charge pas. prefers-reduced-motion : pas de survol.
- scripts/photos.py : image principale Wikidata (P18) + auteur et licence
  via l'API Commons -> sources/photos.json (347 photos a Paris). Photo
  seulement si le nom concorde strictement. Le credit est TOUJOURS affiche.
- notoriete.py ecarte aussi les fiches mal localisees (meme nom exact connu
  de Wikidata a plus de 500 m, ex. "Palais Garnier" place a Bastille).
- Le trace est en lignes droites : pas encore d'itineraire pieton reel.

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
