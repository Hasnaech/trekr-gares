# CLAUDE.md - Trekr : à pied depuis la gare (10 novembre 2026)

Decision de Claude sur carte blanche d'Hasnae, apres relecture de carbon/ et
carbon 2/ : croiser les 55 427 fiches DATAtourisme d'origine avec toutes les
gares SNCF. Reunit ses pistes : priorite au train (v1), DATAtourisme (v1),
pepite d'escale (v3), dispersion des flux (arbitrage 6), "ne pas pouvoir
partir" (probleme C), ecologie au coeur.

- scripts/extract_lieux.py : fiches -> sources/lieux.json (52 230 lieux)
- scripts/croiser.py : lieux x gares x frequentation -> site/data/
- site/index.html : un seul fichier, JS natif, aucune dependance
- Previsualisation : configuration "trekr-gares" (port 4173)

Regles : aucune donnee inventee ; toujours afficher la date de la fiche et
"declare" pour l'accessibilite ; pas de tiret long ; francais.
Pistes suivantes : accessibilite des gares (fichier NeTEx SNCF), horaires
d'ouverture, fiches DATAtourisme a jour (cle API), itineraire pieton reel.
