"""
Photos des lieux : pour chaque element Wikidata relie strictement a un lieu
(sources/notoriete.json), l'image principale (sources/wd_images.json, requete
SPARQL sur la propriete P18), puis auteur, licence et vignette demandes a
Wikimedia Commons. Ecrit sources/photos.json {qid: {u, a, l, p}}.
Appels groupes par 40 et espaces de 2 s : l'API limite vite les rafales.
Usage : python3 scripts/photos.py
"""
import html, json, os, re, subprocess, time

ROOT = os.path.join(os.path.dirname(__file__), "..")
API = "https://commons.wikimedia.org/w/api.php"
UA = "trekr-photos/1.0 (donnees ouvertes)"


def main():
    imgs = json.load(open(os.path.join(ROOT, "sources", "wd_images.json"), encoding="utf-8"))
    by_file = {}
    for qid, f in imgs.items():
        by_file.setdefault("File:" + f.replace("_", " "), []).append(qid)
    files, out = sorted(by_file), {}
    for i in range(0, len(files), 40):
        args = ["curl", "-s", "-m", "40", "-A", UA, "-w", "\n%{http_code}", API,
                "--data-urlencode", "action=query", "--data-urlencode", "format=json", "--data-urlencode", "prop=imageinfo",
                "--data-urlencode", "iiprop=url|extmetadata", "--data-urlencode", "iiurlwidth=640",
                "--data-urlencode", "iiextmetadatafilter=Artist|LicenseShortName",
                "--data-urlencode", "titles=" + "|".join(files[i:i + 40])]
        body, code = subprocess.run(args, capture_output=True).stdout.decode().rsplit("\n", 1)
        if code != "200":
            print("arret : code", code, "au lot", i)
            break
        res = json.loads(body)
        norm = {n["to"]: n["from"] for n in res["query"].get("normalized", [])}
        for page in res["query"]["pages"].values():
            info = (page.get("imageinfo") or [None])[0]
            if not info or "thumburl" not in info:
                continue
            meta = info.get("extmetadata", {})
            artist = re.sub(r"<[^>]+>", "", html.unescape(meta.get("Artist", {}).get("value", ""))).strip()
            artist = " ".join(artist.split())[:60] or "auteur non renseigné"
            lic = meta.get("LicenseShortName", {}).get("value", "licence sur Commons")
            title = norm.get(page["title"], page["title"])
            for qid in by_file.get(title, by_file.get(page["title"], [])):
                out[qid] = {"u": info["thumburl"], "a": artist, "l": lic, "p": info["descriptionurl"]}
        print(i + 40, "/", len(files), "->", len(out))
        time.sleep(2)
    json.dump(out, open(os.path.join(ROOT, "sources", "photos.json"), "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
    print(len(out), "photos avec auteur et licence")


if __name__ == "__main__":
    main()
