"""
Mesure la notoriete des lieux parisiens a partir de Wikidata (donnees
publiques, licence CC0). Pour chaque lieu : l'element Wikidata situe a moins
de 150 m dont le nom ressemble, et le nombre d'editions de Wikipedia qui lui
consacrent une page. Aucune page = lieu confidentiel (0).
C'est une mesure de NOTORIETE, pas un comptage de visiteurs.

Entree : sources/wd/*.json (resultats de requetes SPARQL par quart de Paris,
voir CLAUDE.md). Sortie : sources/notoriete.json {src: [langues, nom Wikidata]}.
"""
import glob, json, math, os, re, unicodedata, collections

ROOT = os.path.join(os.path.dirname(__file__), "..")
BOX = (48.80, 48.91, 2.24, 2.42)
VIDES = {"le", "la", "les", "l", "de", "du", "des", "d", "et", "a", "au", "aux", "paris", "en", "sur"}


def mots(text):
    t = unicodedata.normalize("NFD", text).encode("ascii", "ignore").decode().lower()
    return {w for w in re.sub(r"[^a-z0-9]+", " ", t).split() if w not in VIDES}


def dist(a, b, c, d):
    p = math.pi / 180
    h = math.sin((c - a) * p / 2) ** 2 + math.cos(a * p) * math.cos(c * p) * math.sin((d - b) * p / 2) ** 2
    return 2 * 6371000 * math.asin(math.sqrt(h))


def main():
    grid, n, illisibles = collections.defaultdict(list), 0, 0
    for f in glob.glob(os.path.join(ROOT, "sources", "wd", "*.json")):
        try:
            rows = json.load(open(f, encoding="utf-8"))["results"]["bindings"]
        except Exception:
            illisibles += 1
            continue
        for r in rows:
            la, lo = float(r["lat"]["value"]), float(r["lon"]["value"])
            grid[(int(la * 500), int(lo * 500))].append((la, lo, r["itemLabel"]["value"], int(r["links"]["value"])))
            n += 1
    print(n, "elements Wikidata ;", illisibles, "fichier(s) illisible(s)")
    lieux = [l for l in json.load(open(os.path.join(ROOT, "sources", "lieux.json"), encoding="utf-8"))
             if BOX[0] < l["la"] < BOX[1] and BOX[2] < l["lo"] < BOX[3]]
    out = {}
    for l in lieux:
        a, best = mots(l["n"]), (0, 0, None)
        ci, cj = int(l["la"] * 500), int(l["lo"] * 500)
        for i in (ci - 1, ci, ci + 1):
            for j in (cj - 2, cj - 1, cj, cj + 1, cj + 2):
                for la, lo, label, links in grid.get((i, j), ()):
                    b = mots(label)
                    if not a or not b or dist(l["la"], l["lo"], la, lo) > 150:
                        continue
                    score = len(a & b) / min(len(a), len(b))
                    if score >= 0.6 and (score, links) > best[:2]:
                        best = (score, links, label)
        out[l["src"]] = [best[1], best[2]]
    json.dump(out, open(os.path.join(ROOT, "sources", "notoriete.json"), "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
    noms = {l["src"]: l["n"] for l in lieux}
    avec = sorted(((v[0], noms[k], v[1]) for k, v in out.items() if v[1]), reverse=True)
    print(len(lieux), "lieux ;", len(avec), "relies a Wikidata ;", len(lieux) - len(avec), "sans page")
    for row in avec[:10] + avec[len(avec) // 2: len(avec) // 2 + 6]:
        print("  ", row)
    print(collections.Counter("0" if v[0] == 0 else "1-5" if v[0] <= 5 else "6-20" if v[0] <= 20 else "21-60" if v[0] <= 60 else "60+" for v in out.values()))


if __name__ == "__main__":
    main()
