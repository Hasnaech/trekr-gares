"""
Etape 3 : decoupe sources/lieux.json en tuiles de 0,1 degre (environ 11 km)
dans site/data/t/<i>_<j>.json, pour que le telephone ne charge que les lieux
autour de lui. i = floor(lat / 0.1), j = floor(lon / 0.1).
Usage : python3 scripts/tuiles.py
"""
import glob, json, math, os, shutil, collections

ROOT = os.path.join(os.path.dirname(__file__), "..")


OSM_CATS = {"cafe": "Café", "bar": "Bar", "pub": "Bar", "ice_cream": "Glacier", "drinking_water": "Fontaine à boire",
            "bakery": "Boulangerie", "pastry": "Pâtisserie", "books": "Librairie", "chocolate": "Chocolaterie",
            "cheese": "Fromagerie", "viewpoint": "Point de vue", "artwork": "Art de rue", "gallery": "Galerie"}


def main():
    lieux = json.load(open(os.path.join(ROOT, "sources", "lieux.json"), encoding="utf-8"))
    # Notoriete (scripts/notoriete.py) : nombre d'editions de Wikipedia, Paris seulement pour l'instant.
    chemin = os.path.join(ROOT, "sources", "notoriete.json")
    notoriete = json.load(open(chemin, encoding="utf-8")) if os.path.exists(chemin) else {}
    chemin = os.path.join(ROOT, "sources", "photos.json")
    photos = json.load(open(chemin, encoding="utf-8")) if os.path.exists(chemin) else {}
    tuiles = collections.defaultdict(list)
    for l in lieux:
        if l["src"] in notoriete and len(notoriete[l["src"]]) > 3 and notoriete[l["src"]][3]:
            continue  # localisation contredite par Wikidata : on ne guide personne vers une erreur
        item = {k: v for k, v in l.items() if k != "w" and v is not None}
        if l["src"] in notoriete:
            item["no"] = notoriete[l["src"]][0]
            photo = photos.get(notoriete[l["src"]][2] or "")
            if photo:  # vignette Wikimedia Commons, auteur, licence, page de la photo
                item["img"] = {**photo, "u": photo["u"].split("?")[0]}
        tuiles[(math.floor(l["la"] * 10), math.floor(l["lo"] * 10))].append(item)
    # Lieux de vie (OpenStreetMap, sources/osm_paris.json) : cafes, boulangeries, librairies,
    # art de rue, fontaines... avec horaires quand ils sont renseignes. Les chaines sont ecartees.
    chemin = os.path.join(ROOT, "sources", "osm_paris.json")
    if os.path.exists(chemin):
        n_osm = 0
        for e in json.load(open(chemin, encoding="utf-8"))["elements"]:
            t = e.get("tags", {})
            cat = OSM_CATS.get(t.get("amenity")) or OSM_CATS.get(t.get("shop")) or OSM_CATS.get(t.get("tourism"))
            la, lo = (e.get("lat"), e.get("lon")) if "lat" in e else (e.get("center", {}).get("lat"), e.get("center", {}).get("lon"))
            if not cat or la is None or t.get("brand") or t.get("access") in ("private", "no"):
                continue
            name = t.get("name")
            if not name:
                if cat == "Fontaine à boire":
                    name = "Fontaine à boire"
                elif cat == "Art de rue" and t.get("artwork_type"):
                    name = {"mural": "Fresque murale", "sculpture": "Sculpture", "statue": "Statue", "graffiti": "Graffiti", "mosaic": "Mosaïque", "street_art": "Art de rue"}.get(t["artwork_type"])
                elif cat == "Point de vue":
                    name = "Point de vue"
                if not name:
                    continue
            item = {"n": name, "c": cat, "la": round(la, 5), "lo": round(lo, 5), "o": 1,
                    "src": f"https://www.openstreetmap.org/{e['type']}/{e['id']}"}
            if t.get("opening_hours"):
                item["oh"] = t["opening_hours"]
            if t.get("wheelchair") in ("yes", "no"):
                item["pmr"] = t["wheelchair"] == "yes"
            if t.get("outdoor_seating") == "yes":
                item["ter"] = 1
            if t.get("artist_name"):
                item["par"] = t["artist_name"]
            tuiles[(math.floor(la * 10), math.floor(lo * 10))].append(item)
            n_osm += 1
        print(n_osm, "lieux de vie OpenStreetMap ajoutes")
    # Villes preparees hors de Paris (scripts/ville.py) : deja au format du site.
    for f in sorted(glob.glob(os.path.join(ROOT, "sources", "villes", "*.json"))):
        ville = json.load(open(f, encoding="utf-8"))
        for item in ville:
            tuiles[(math.floor(item["la"] * 10), math.floor(item["lo"] * 10))].append(item)
        print(os.path.basename(f), ":", len(ville), "lieux")
    out = os.path.join(ROOT, "site", "data", "t")
    shutil.rmtree(out, ignore_errors=True)
    os.makedirs(out)
    for (i, j), items in tuiles.items():
        json.dump(items, open(os.path.join(out, f"{i}_{j}.json"), "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
    # Liste des tuiles existantes : evite au telephone de demander des fichiers absents.
    json.dump(sorted(f"{i}_{j}" for i, j in tuiles), open(os.path.join(ROOT, "site", "data", "tuiles.json"), "w"), separators=(",", ":"))
    tailles = sorted(len(v) for v in tuiles.values())
    print(len(tuiles), "tuiles ; lieux par tuile : mediane", tailles[len(tailles) // 2], "max", tailles[-1])


if __name__ == "__main__":
    main()
