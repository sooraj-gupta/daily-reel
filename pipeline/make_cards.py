"""Turn finished reels into feed card documents (one JSON file per reel, in cards_out/).

Usage:
  python3 make_cards.py --date 2026-10-16 --batch 1 --start 10 id1 id2:35 id3 ...

  --date   ISO date of the deck (the page shows the deck whose date is in meta/latest). Default: today.
  --batch  1 = shown first; 2, 3, ... are revealed by the page's pull-down / More button. Default: 1.
  --start  order of the first reel; later reels get +10 each. An id written id:35 uses order 35 explicitly.

Reads, per id:   out/reels/<id>.json (written by produce.py), stories/<id>.json (comments, source, url),
                 uploads.json (id -> {"video": "/_blob/...", "poster": "/_blob/..."}, filled from the asset upload results).
Writes:          cards_out/<id>.json   -> then write each file to the database as cards/r-<id> (see docs/DAILY-RUN.md).
"""
import argparse, datetime, json, os

R = os.path.dirname(os.path.abspath(__file__))
ap = argparse.ArgumentParser()
ap.add_argument("--date", default=datetime.date.today().isoformat())
ap.add_argument("--batch", type=int, default=1)
ap.add_argument("--start", type=float, default=10)
ap.add_argument("ids", nargs="+")
a = ap.parse_args()

uploads = json.load(open(os.path.join(R, "uploads.json")))
os.makedirs(os.path.join(R, "cards_out"), exist_ok=True)
for k, spec in enumerate(a.ids):
    sid, _, o = spec.partition(":")
    order = float(o) if o else a.start + 10 * k
    meta = json.load(open(os.path.join(R, "out", "reels", sid + ".json")))
    sp = os.path.join(R, "stories", sid + ".json")
    story = json.load(open(sp)) if os.path.exists(sp) else {}
    up = uploads[sid]
    card = {"kind": "reel", "date": a.date, "batch": a.batch, "order": order, "topic": meta["topic"],
            "kicker": story.get("kicker") or meta.get("kicker"), "source": story.get("source") or meta.get("source"),
            "url": story.get("url") or meta.get("url"), "headline_text": meta["headline_text"],
            "video": up["video"], "poster": up["poster"], "duration": meta["duration"],
            "comments": (story.get("comments") or meta.get("comments") or [])[:4]}
    if story.get("why") or meta.get("why"): card["why"] = story.get("why") or meta.get("why")
    card = {key: v for key, v in card.items() if v is not None}
    json.dump(card, open(os.path.join(R, "cards_out", sid + ".json"), "w"))
    print(f"{sid}: batch {a.batch}, order {order:g}, {len(card['comments'])} comments")
