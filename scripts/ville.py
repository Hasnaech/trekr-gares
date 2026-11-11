"""
Prepare une ville hors de Paris : lieux de vie et patrimoine d'OpenStreetMap
dans un rayon donne, avec la notoriete Wikidata (nombre d'editions de
Wikipedia). Ecrit sources/villes/<nom>.json, repris par scripts/tuiles.py.
Une ville preparee repond tout de suite ; ailleurs le site interroge
OpenStreetMap en direct, ce qui peut prendre 30 secondes.

Usage : python3 scripts/ville.py <nom> <lat> <lon> [rayon_m=2500]
"""
import json, os, re, subprocess, sys, time

ROOT = os.path.join(os.path.dirname(__file__), "..")
UA = "trekr-donnees/1.0 (donnees ouvertes)"
CATS = {"cafe": "Café", "bar": "Bar", "pub": "Bar", "ice_cream": "Glacier", "drinking_water": "Fontaine à boire", "bakery": "Boulangerie",
        "pastry": "Pâtisserie", "books": "Librairie", "chocolate": "Chocolaterie", "cheese": "Fromagerie", "viewpoint": "Point de vue",
        "artwork": "Art de rue", "gallery": "Galerie", "attraction": "Site culturel", "park": "Parc et jardin", "garden": "Parc et jardin",
        "place_of_worship": "Édifice religieux", "monument": "Monument", "memorial": "Monument", "city_gate": "Monument",
        "castle": "Château et fortification", "fort": "Château et fortification", "tower": "Château et fortification",
        "ruins": "Site archéologique", "archaeological_site": "Site archéologique"}
ART = {"mural": "Fresque murale", "sculpture": "Sculpture", "statue": "Statue", "graffiti": "Graffiti", "mosaic": "Mosaïque", "street_art": "Art de rue"}


def curl(args):
    for attempt in range(4):
        out = subprocess.run(["curl", "-s", "-m", "150", "-A", UA, "-w", "\n%{http_code}"] + args, capture_output=True).stdout.decode()
        body, code = out.rsplit("\n", 1)
        if code == "200":
            return json.loads(body)
        time.sleep(8 * (attempt + 1))
    raise SystemExit(f"echec apres 4 essais (dernier code {code})")


def main():
    nom, lat, lon = sys.argv[1], float(sys.argv[2]), float(sys.argv[3])
    r = int(sys.argv[4]) if len(sys.argv) > 4 else 2500
    a = f"(around:{r},{lat},{lon})"
    q = ('[out:json][timeout:120];(nwr["amenity"~"^(cafe|bar|pub|ice_cream|drinking_water)$"]' + a
         + ';nwr["shop"~"^(bakery|pastry|books|chocolate|cheese)$"]' + a + ';nwr["tourism"~"^(viewpoint|artwork|gallery|attraction)$"]' + a
         + ';nwr["leisure"~"^(park|garden)$"]["name"]' + a
         + ';nwr["historic"~"^(monument|memorial|castle|ruins|city_gate|archaeological_site|fort|tower)$"]["name"]' + a
         + ';nwr["amenity"="place_of_worship"]["name"]["wikidata"]' + a + ';);out tags center;')
    data = curl(["--data-urlencode", "data=" + q, "https://overpass-api.de/api/interpreter"])
    items = []
    for e in data["elements"]:
        t = e.get("tags", {})
        cat = CATS.get(t.get("amenity")) or CATS.get(t.get("shop")) or CATS.get(t.get("tourism")) or CATS.get(t.get("leisure")) or CATS.get(t.get("historic"))
        la = e.get("lat", e.get("center", {}).get("lat")); lo = e.get("lon", e.get("center", {}).get("lon"))
        if not cat or la is None or t.get("brand") or t.get("access") in ("private", "no"):
            continue
        name = t.get("name:fr") or t.get("name") or (cat if cat in ("Fontaine à boire", "Point de vue") else ART.get(t.get("artwork_type")) if cat == "Art de rue" else None)
        if not name:
            continue
        it = {"n": name, "c": cat, "la": round(la, 5), "lo": round(lo, 5), "o": 1, "src": f"https://www.openstreetmap.org/{e['type']}/{e['id']}"}
        if t.get("opening_hours"): it["oh"] = t["opening_hours"]
        if t.get("wheelchair") in ("yes", "no"): it["pmr"] = t["wheelchair"] == "yes"
        if t.get("outdoor_seating") == "yes": it["ter"] = 1
        if t.get("artist_name"): it["par"] = t["artist_name"]
        if re.fullmatch(r"Q\d+", t.get("wikidata", "")): it["wd"] = t["wikidata"]
        items.append(it)
    ids, links = sorted({i["wd"] for i in items if "wd" in i}), {}
    for k in range(0, len(ids), 50):
        res = curl(["https://www.wikidata.org/w/api.php?action=wbgetentities&props=sitelinks&format=json&ids=" + "|".join(ids[k:k + 50])])
        for qid, ent in res.get("entities", {}).items():
            links[qid] = sum(1 for w in ent.get("sitelinks", {}) if w.endswith("wiki") and not re.match(r"(commons|species|meta|wikidata)", w))
        time.sleep(1)
    for it in items:
        if it.get("wd") in links:
            it["no"] = links[it["wd"]]
        it.pop("wd", None)
    json.dump(items, open(os.path.join(ROOT, "sources", "villes", nom + ".json"), "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
    print(nom, ":", len(items), "lieux,", sum(1 for i in items if "oh" in i), "avec horaires,", sum(1 for i in items if "no" in i), "avec notoriete")


if __name__ == "__main__":
    main()
