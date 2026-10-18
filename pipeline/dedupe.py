"""Duplicate guard for stories. Keeps a ledger of every story already used (pipeline/seen.json, git-ignored).

Run it BEFORE writing a story, so nothing is written, voiced or rendered twice:

  python3 pipeline/dedupe.py check  --url <article-url> --title "<headline>" [--days 7]
  python3 pipeline/dedupe.py record --id <story-id> --url <article-url> --title "<headline>" [--date 2026-10-17]
  python3 pipeline/dedupe.py seed [--dir <folder>]   # add stories from pipeline/stories (and any extra folders) to the ledger
  python3 pipeline/dedupe.py list [--days 7]

check prints one JSON line:  {"verdict": "new" | "similar" | "duplicate", "match": {...}, "score": 0.0-1.0, "reason": "..."}
  duplicate = same article URL, or a title that is nearly the same -> SKIP the story.
  similar   = overlapping title (often the same event from another outlet) -> skip unless the new article
              adds materially new facts (a new development, new numbers). Say why in the report if you keep it.
  new       = go ahead, then `record` it immediately.
produce.py also records each story when its reel renders, so the ledger stays right even if `record` is forgotten.
Standard library only.
"""
import argparse, datetime, glob, json, os, re, sys
from urllib.parse import urlsplit

ROOT = os.path.dirname(os.path.abspath(__file__))
LEDGER = os.path.join(ROOT, "seen.json")
STOP = set("the a an and or of to in on at for with by from as is are was were be been it its this that these those after over into out up down new says say said just now more than not no".split())
KEEP_DAYS = 30

def norm_url(u):
    if not u: return ""
    p = urlsplit(u.strip())
    return (p.netloc.lower().replace("www.", "") + p.path.rstrip("/")).lower()

def tokens(title):
    words = re.findall(r"[a-z0-9$%.]+", (title or "").lower().replace("−", "-"))
    return {w.strip(".") for w in words if len(w) > 2 and w not in STOP}

def entities(title):
    """Capitalized words and acronyms (company, product and person names)."""
    found = re.findall(r"\b[A-Z][A-Za-z0-9&'-]{2,}\b|\b[A-Z]{2,}\b", title or "")
    return {w.lower().strip("'-") for w in found} - STOP

def jaccard(a, b):
    return len(a & b) / len(a | b) if a and b else 0.0

def load():
    try: return json.load(open(LEDGER))
    except Exception: return []

def save(rows):
    cutoff = (datetime.date.today() - datetime.timedelta(days=KEEP_DAYS)).isoformat()
    rows = [r for r in rows if r.get("date", "9999") >= cutoff]
    json.dump(rows, open(LEDGER, "w"), indent=1)

def record(id_, url, title, date=None, text=None):
    rows = [r for r in load() if r.get("id") != id_]
    rows.append({"id": id_, "url": url or "", "title": title or "", "text": text or title or "", "date": date or datetime.date.today().isoformat()})
    save(rows)

def check(url, title, days=7):
    cutoff = (datetime.date.today() - datetime.timedelta(days=days)).isoformat()
    nu, nt, ne = norm_url(url), tokens(title), entities(title)
    best, best_score, best_shared = None, 0.0, 0
    for r in load():
        if r.get("date", "") < cutoff: continue
        if nu and norm_url(r.get("url")) == nu and len(nu.split("/", 1)[-1]) > 3:    # not just a homepage
            return {"verdict": "duplicate", "match": r, "score": 1.0, "reason": "same article URL"}
        s = jaccard(nt, tokens(r.get("title"))); shared = len(ne & entities(r.get("text") or r.get("title")))
        if (s, shared) > (best_score, best_shared) or best is None: best, best_score, best_shared = r, s, shared
        if shared > best_shared or (shared == best_shared and s > best_score): best, best_score, best_shared = r, s, shared
    out = {"match": best, "score": round(best_score, 2), "shared_names": best_shared}
    if best_score >= 0.6 or (best_shared >= 3 and best_score >= 0.3):
        return dict(out, verdict="duplicate", reason="nearly identical title or same names and wording")
    if best_score >= 0.35 or best_shared >= 2:
        return dict(out, verdict="similar", reason="shares %d names / overlapping title: possibly the same event" % best_shared)
    return dict(out, verdict="new", match=None, reason="no overlap in the last %d days" % days)

def seed(dirs=None):
    """Add every story file in the given folders to the ledger (additive; same id replaces)."""
    rows = {r["id"]: r for r in load()}
    for d in (dirs or [os.path.join(ROOT, "stories")]):
        for p in sorted(glob.glob(os.path.join(d, "*.json"))):
            try: s = json.load(open(p))
            except Exception: continue
            if s.get("id", "").startswith(("example", "dryrun")): continue
            title = " ".join(h.lstrip("*") for h in s.get("headline", [])) + " " + (s.get("sentences") or [""])[0]
            date = datetime.date.fromtimestamp(os.path.getmtime(p)).isoformat()
            rows[s["id"]] = {"id": s["id"], "url": s.get("url", ""), "title": title.strip(), "text": (title + " " + " ".join(s.get("sentences", []))).strip(), "date": date}
    save(list(rows.values())); return len(rows)

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("cmd", choices=["check", "record", "seed", "list"])
    ap.add_argument("--url", default=""); ap.add_argument("--title", default=""); ap.add_argument("--id", default="")
    ap.add_argument("--date"); ap.add_argument("--days", type=int, default=7); ap.add_argument("--dir", action="append", help="seed: extra folder of story JSON files (repeatable)")
    a = ap.parse_args()
    if a.cmd == "check": print(json.dumps(check(a.url, a.title, a.days)))
    elif a.cmd == "record":
        if not a.id: sys.exit("--id required")
        record(a.id, a.url, a.title, a.date); print("recorded", a.id)
    elif a.cmd == "seed": print("ledger now has", seed(a.dir), "stories")
    else:
        cutoff = (datetime.date.today() - datetime.timedelta(days=a.days)).isoformat()
        for r in load():
            if r.get("date", "") >= cutoff: print(r["date"], r["id"], "|", r["title"][:70])
