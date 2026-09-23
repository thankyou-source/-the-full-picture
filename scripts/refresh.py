from pathlib import Path
from datetime import datetime, timezone
import json, re, urllib.request
from html import unescape

DATA_FILE = Path("data/events.json")
UA = "TheFullPicture/0.2 (+public-source monitor)"

SOURCES = [
    {
        "id": "home-office-daily",
        "name": "UK Home Office / Border Force",
        "kind": "official_stats",
        "url": "https://www.gov.uk/government/publications/migrants-detected-crossing-the-english-channel-in-small-boats/migrants-detected-crossing-the-english-channel-in-small-boats-last-7-days"
    },
    {
        "id": "home-office-weekly",
        "name": "UK Home Office / Border Force",
        "kind": "official_stats",
        "url": "https://www.gov.uk/government/publications/migrants-detected-crossing-the-english-channel-in-small-boats/weekly-summary-of-small-boat-arrivals-and-preventions"
    },
    {
        "id": "premar-latest",
        "name": "Préfecture maritime de la Manche et de la mer du Nord",
        "kind": "official_incident",
        "url": "https://www.premar-manche.gouv.fr/communiques-presse/bilan-des-operation-d-assistance-et-de-sauvetage-en-mer-des-journees-du-21-au-23-septembre-2026-129-personnes-secourues"
    }
]

def fetch(url):
    req=urllib.request.Request(url, headers={"User-Agent":UA})
    with urllib.request.urlopen(req, timeout=20) as r:
        return r.read().decode("utf-8","replace")

def clean_html(s):
    s=re.sub(r"<script.*?</script>|<style.*?</style>"," ",s,flags=re.S|re.I)
    s=re.sub(r"<[^>]+>"," ",s)
    return re.sub(r"\s+"," ",unescape(s)).strip()

def main():
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    try:
        data=json.loads(DATA_FILE.read_text(encoding="utf-8"))
    except Exception:
        data={"updated":None,"events":[]}
    snapshots=[]
    for src in SOURCES:
        item={k:src[k] for k in ("id","name","kind","url")}
        try:
            text=clean_html(fetch(src["url"]))
            item["ok"]=True
            item["checked_at"]=datetime.now(timezone.utc).isoformat()
            # Store only a short fingerprint/preview, not republished article text.
            item["preview"]=text[:500]
            item["fingerprint"]=str(hash(text))
        except Exception as e:
            item["ok"]=False
            item["error"]=type(e).__name__
        snapshots.append(item)
    data["collector_checked_at"]=datetime.now(timezone.utc).isoformat()
    data["source_snapshots"]=snapshots
    DATA_FILE.write_text(json.dumps(data,indent=2,ensure_ascii=False),encoding="utf-8")
    print("Sources checked:", len(snapshots))
    print("Successful:", sum(1 for x in snapshots if x.get("ok")))

if __name__=="__main__":
    main()
