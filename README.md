# Trekr : le guide qui se déclenche sur votre passage

Marchez, roulez, flânez : dès que vous approchez d'un lieu, Trekr vous le
signale et vous lit sa fiche officielle, à voix haute si vous le voulez.
52 230 lieux réels en France. Essayer : https://hasnaech.github.io/trekr-gares/

La position reste dans le téléphone. Application web : le suivi fonctionne
tant que la page est ouverte et l'écran allumé.

## Aussi : à pied depuis la gare (`site/gares.html`)

Pour chaque gare de voyageurs de France, les lieux réels à visiter à pied en
sortant du train, avec l'accessibilité en fauteuil quand le lieu la déclare.

## Pourquoi

Partir sans voiture suppose de savoir ce qu'on trouve à l'arrivée. Cette
information existe, mais éparpillée dans des dizaines de milliers de fiches
publiques que personne ne croise avec les gares. Ce site le fait :

- 2 792 gares, 52 230 lieux, 14 764 couples gare-lieu à moins de 1,5 km ;
- 1 950 gares ont au moins un lieu à pied ; 305 ont un lieu déclaré
  accessible en fauteuil ;
- les « gares oubliées » : très peu de voyageurs en 2024, beaucoup à voir.
  Y descendre répartit les visites loin des sites saturés.

## Honnêteté

- Distances à vol d'oiseau ; temps de marche estimé (distance + 30 %, 4 km/h).
- Accessibilité déclarée par le lieu, non vérifiée ; le chemin depuis la gare
  et l'accessibilité de la gare ne sont pas évalués.
- 86 % des fiches ne renseignent pas l'accessibilité : le site l'affiche.
- La couverture dépend de ce que les offices de tourisme publient.

## Régénérer les données

```bash
python3 scripts/extract_lieux.py   # fiches DATAtourisme -> sources/lieux.json
python3 scripts/tuiles.py          # lieux -> tuiles géographiques du guide
python3 scripts/croiser.py         # lieux x gares -> site/data/g/
```

Le site (`site/`) est un seul fichier HTML sans dépendance ni traceur.

## Sources et licences

- DATAtourisme (ADN Tourisme), Licence Ouverte 2.0, extraction d'août 2025
  (copie d'origine du projet Trekr, dossier `carbon/`).
- SNCF Open Data : « Gares de voyageurs » et « Fréquentation en gares »
  (2024), licence ODbL, téléchargés le 10 novembre 2026.
- Données croisées (`site/data/`) : ODbL. Code : MIT.
