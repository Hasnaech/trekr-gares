"""
Etape 3 : decoupe sources/lieux.json en tuiles de 0,1 degre (environ 11 km)
dans site/data/t/<i>_<j>.json, pour que le telephone ne charge que les lieux
autour de lui. i = floor(lat / 0.1), j = floor(lon / 0.1).
Usage : python3 scripts/tuiles.py
"""
import json, math, os, shutil, collections

ROOT = os.path.join(os.path.dirname(__file__), "..")


def main():
    lieux = json.load(open(os.path.join(ROOT, "sources", "lieux.json"), encoding="utf-8"))
    tuiles = collections.defaultdict(list)
    for l in lieux:
        item = {k: v for k, v in l.items() if k != "w" and v is not None}
        tuiles[(math.floor(l["la"] * 10), math.floor(l["lo"] * 10))].append(item)
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
