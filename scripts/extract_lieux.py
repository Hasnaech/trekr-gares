"""
Etape 1 : lit les fiches DATAtourisme d'origine (dossier carbon/) et ecrit
sources/lieux.json : une ligne compacte par lieu situe en France, avec
coordonnees. Rien n'est invente : les champs absents restent absents.

Usage : python3 scripts/extract_lieux.py [chemin/datatourisme_data]
"""
import glob, json, os, re, sys, collections, unicodedata

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


def dedoublonner(items, stats):
    """Une meme adresse est parfois publiee par deux organismes : on garde
    la fiche la plus recente quand le nom est identique a moins de 200 m."""
    def cle(n):
        t = unicodedata.normalize("NFD", n).encode("ascii", "ignore").decode().lower()
        t = re.sub(r"[^a-z0-9]+", " ", t)
        return " ".join(w for w in t.split() if w not in ("le", "la", "les", "l", "de", "du", "des", "d"))
    groupes = collections.defaultdict(list)
    for it in items:
        groupes[cle(it["n"])].append(it)
    garde = []
    for g in groupes.values():
        g.sort(key=lambda x: (x.get("maj") or "", len(x.get("dl", "")) + len(x.get("d", ""))), reverse=True)
        retenus = []
        for it in g:  # meme nom : doublon si a moins de ~200 m d'une fiche deja retenue
            if any(abs(it["la"] - r["la"]) < 0.002 and abs(it["lo"] - r["lo"]) < 0.003 for r in retenus):
                stats["doublons retires"] += 1
            else:
                retenus.append(it)
        garde.extend(retenus)
    return garde


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
        desc = long = None
        for d in o.get("hasDescription") or []:
            desc = desc or fr(d.get("shortDescription"))
            long = long or fr(d.get("dc:description"))
        desc = desc or fr(o.get("rdfs:comment")) or long
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
            desc = " ".join(desc.split())
            if len(desc) > 500:  # coupe en fin de phrase, jamais en plein mot
                cut = desc[:500]
                desc = cut[: cut.rfind(". ") + 1] or cut[: cut.rfind(" ")] + "…"
            item["d"] = desc
        # Texte long de la fiche, pour la lecture a voix haute (coupe en fin de phrase).
        if long and len(long) > len(desc or "") + 80:
            long = " ".join(long.split())
            if len(long) > 1200:
                cut = long[:1200]
                long = cut[: cut.rfind(". ") + 1] or cut
            item["dl"] = long
            stats["avec texte long"] += 1
        if web and web.startswith("http"):
            item["w"] = web
        out.append(item)
        stats["gardes"] += 1
    out = dedoublonner(out, stats)
    dest = os.path.join(os.path.dirname(__file__), "..", "sources", "lieux.json")
    json.dump(out, open(dest, "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
    print(len(files), "fiches lues")
    for k, v in stats.most_common():
        print(f"  {k}: {v}")
    print(collections.Counter(i["c"] for i in out).most_common())
    print(collections.Counter((i.get("maj") or "?")[:4] for i in out).most_common(6))


if __name__ == "__main__":
    main()
