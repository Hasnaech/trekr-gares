"""
Etape 1 : lit les fiches DATAtourisme d'origine (dossier carbon/) et ecrit
sources/lieux.json : une ligne compacte par lieu situe en France, avec
coordonnees. Rien n'est invente : les champs absents restent absents.

Usage : python3 scripts/extract_lieux.py [chemin/datatourisme_data]
"""
import glob, json, os, sys, collections

SRC = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
    os.path.dirname(__file__), "..", "..", "..", "carbon",
    "eco-travel-ai-service-main", "Apis", "DataTourisme", "datatourisme_data")

# Du plus precis au plus general : le premier type reconnu donne la categorie.
CATEGORIES = [
    ("Museum", "Musée"), ("InterpretationCentre", "Musée"),
    ("Castle", "Château et fortification"), ("DefenceSite", "Château et fortification"),
    ("ReligiousSite", "Édifice religieux"),
    ("ParkAndGarden", "Parc et jardin"),
    ("NaturalHeritage", "Site naturel"),
    ("RemembranceSite", "Lieu de mémoire"),
    ("ArcheologicalSite", "Site archéologique"),
    ("TechnicalHeritage", "Patrimoine technique"), ("IndustrialSite", "Patrimoine technique"),
    ("Library", "Bibliothèque"),
    ("TouristInformationCenter", "Office de tourisme"),
    ("Theater", "Salle de spectacle"), ("Cinema", "Cinéma"),
    ("SportsAndLeisurePlace", "Sport et loisirs"),
    ("TastingProvider", "Dégustation"),
    ("CraftsmanShop", "Artisanat"),
    ("Restaurant", "Restaurant"), ("FoodEstablishment", "Restaurant"),
    ("RemarkableBuilding", "Monument"), ("CityHeritage", "Monument"),
    ("CulturalSite", "Site culturel"),
]
SKIP = {"EntertainmentAndEvent", "Product", "Tour", "Accommodation"}  # dates perimees ou hors sujet


def fr(value):
    """Texte francais d'un champ multilingue, ou None."""
    if isinstance(value, dict):
        value = value.get("fr") or value.get("@value")
    if isinstance(value, list):
        value = value[0] if value else None
    return value.strip() if isinstance(value, str) and value.strip() else None


def main():
    files = [f for f in glob.glob(os.path.join(SRC, "objects", "**", "*.json"), recursive=True)]
    out, stats = [], collections.Counter()
    for path in files:
        try:
            o = json.load(open(path, encoding="utf-8"))
        except Exception:
            stats["illisible"] += 1
            continue
        types = set(o.get("@type", []))
        if types & SKIP:
            stats["hors sujet"] += 1
            continue
        cat = next((label for t, label in CATEGORIES if t in types), None)
        name = fr(o.get("rdfs:label"))
        loc = (o.get("isLocatedAt") or [{}])[0]
        geo = loc.get("schema:geo") or {}
        try:
            lat, lon = float(geo["schema:latitude"]), float(geo["schema:longitude"])
        except Exception:
            stats["sans coordonnees"] += 1
            continue
        if not cat or not name:
            stats["sans categorie ou nom"] += 1
            continue
        addr = (loc.get("schema:address") or [{}])[0]
        desc = None
        for d in o.get("hasDescription") or []:
            desc = fr(d.get("shortDescription")) or fr(d.get("dc:description"))
            if desc:
                break
        desc = desc or fr(o.get("rdfs:comment"))
        web = None
        for c in o.get("hasContact") or []:
            pages = c.get("foaf:homepage") or []
            if pages:
                web = pages[0]
                break
        item = {
            "n": name, "c": cat, "la": round(lat, 5), "lo": round(lon, 5),
            "v": addr.get("schema:addressLocality"), "cp": addr.get("schema:postalCode"),
            "maj": o.get("lastUpdate"), "src": o.get("@id"),
        }
        if "reducedMobilityAccess" in o:
            item["pmr"] = bool(o["reducedMobilityAccess"])
            stats["pmr oui" if item["pmr"] else "pmr non"] += 1
        else:
            stats["pmr non renseigne"] += 1
        if desc:
            item["d"] = desc[:280]
        if web and web.startswith("http"):
            item["w"] = web
        out.append(item)
        stats["gardes"] += 1
    dest = os.path.join(os.path.dirname(__file__), "..", "sources", "lieux.json")
    json.dump(out, open(dest, "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
    print(len(files), "fiches lues")
    for k, v in stats.most_common():
        print(f"  {k}: {v}")
    print(collections.Counter(i["c"] for i in out).most_common())
    print(collections.Counter((i.get("maj") or "?")[:4] for i in out).most_common(6))


if __name__ == "__main__":
    main()
