"""
Etape 2 : croise les lieux (sources/lieux.json) avec les gares de voyageurs
SNCF (sources/gares-de-voyageurs.json) et ecrit les donnees du site :
  site/data/gares.json        index de toutes les gares (+ voyageurs 2024, source SNCF)
  site/data/g/<id>.json       lieux a moins de 1,5 km de la gare
La distance est a vol d'oiseau ; le temps de marche est une estimation
(distance majoree de 30 %, 4 km/h). Usage : python3 scripts/croiser.py
"""
import json, math, os, re, shutil, unicodedata, collections

ROOT = os.path.join(os.path.dirname(__file__), "..")
RAYON_M = 1500
DETOUR, VITESSE_M_MIN = 1.3, 4000 / 60


def dist_m(la1, lo1, la2, lo2):
    p = math.pi / 180
    h = math.sin((la2 - la1) * p / 2) ** 2 + math.cos(la1 * p) * math.cos(la2 * p) * math.sin((lo2 - lo1) * p / 2) ** 2
    return 2 * 6371000 * math.asin(math.sqrt(h))


def slug(text):
    t = unicodedata.normalize("NFD", text).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", t).strip("-")


def main():
    lieux = json.load(open(os.path.join(ROOT, "sources", "lieux.json"), encoding="utf-8"))
    gares = json.load(open(os.path.join(ROOT, "sources", "gares-de-voyageurs.json"), encoding="utf-8"))
    freq = json.load(open(os.path.join(ROOT, "sources", "frequentation-gares.json"), encoding="utf-8"))
    voyageurs = {f["code_uic_complet"]: f.get("total_voyageurs_2024") for f in freq}

    # Grille de 0,02 degre (~2 km) pour ne comparer que les voisins.
    cell = lambda la, lo: (int(la / 0.02), int(lo / 0.02))
    grid = collections.defaultdict(list)
    for l in lieux:
        grid[cell(l["la"], l["lo"])].append(l)

    out_dir = os.path.join(ROOT, "site", "data", "g")
    shutil.rmtree(out_dir, ignore_errors=True)
    os.makedirs(out_dir)

    index, seen, stats = [], set(), collections.Counter()
    for g in gares:
        pos = g.get("position_geographique")
        if not pos or not g.get("nom"):
            stats["gares sans position"] += 1
            continue
        la, lo = pos["lat"], pos["lon"]
        ci, cj = cell(la, lo)
        proches = []
        for i in (ci - 1, ci, ci + 1):
            for j in (cj - 1, cj, cj + 1):
                for l in grid.get((i, j), ()):
                    d = dist_m(la, lo, l["la"], l["lo"])
                    if d <= RAYON_M:
                        item = {k: v for k, v in l.items() if k not in ("la", "lo", "w") and v is not None}
                        item["m"] = int(round(d, -1))
                        item["min"] = max(1, round(d * DETOUR / VITESSE_M_MIN))
                        proches.append(item)
        proches.sort(key=lambda x: x["m"])
        gid = slug(g["nom"])
        if gid in seen:
            gid = f"{gid}-{g.get('codes_uic', '')[:8]}"
        seen.add(gid)
        pmr = sum(1 for p in proches if p.get("pmr") is True)
        row = {"id": gid, "n": g["nom"], "la": round(la, 4), "lo": round(lo, 4), "nb": len(proches), "pmr": pmr}
        voy = voyageurs.get((g.get("codes_uic") or "").split(";")[0])
        if voy:  # voyageurs comptes par la SNCF en 2024 ; absent ou zero = non publie
            row["voy"] = voy
            stats["gares avec frequentation 2024"] += 1
        index.append(row)
        json.dump({"gare": g["nom"], "lieux": proches}, open(os.path.join(out_dir, gid + ".json"), "w", encoding="utf-8"),
                  ensure_ascii=False, separators=(",", ":"))
        stats["gares"] += 1
        stats["gares avec au moins un lieu"] += bool(proches)
        stats["gares avec un lieu declare accessible"] += bool(pmr)
        stats["couples gare-lieu"] += len(proches)

    index.sort(key=lambda x: x["n"])
    meta = {
        "gares": index,
        "total_lieux": len(lieux),
        "rayon_m": RAYON_M,
        "stats": dict(stats),
    }
    json.dump(meta, open(os.path.join(ROOT, "site", "data", "gares.json"), "w", encoding="utf-8"),
              ensure_ascii=False, separators=(",", ":"))
    for k, v in stats.items():
        print(f"{k}: {v}")
    top = sorted(index, key=lambda x: -x["nb"])[:8]
    print([(t["n"], t["nb"], t["pmr"]) for t in top])


if __name__ == "__main__":
    main()
