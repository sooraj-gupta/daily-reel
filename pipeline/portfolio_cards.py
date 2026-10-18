"""Build portfolio stocks cards from a list of tickers. Tickers only: no quantities, cost basis or balances ever enter this script.

  python3 pipeline/portfolio_cards.py --date 2026-10-17 --order 95 PANW NVDA AMD ...

Fetches 5-day closes from Yahoo Finance (no key), sorts worst weekly move first, and writes
pipeline/cards_out/stocks-portfolio-1.json, -2.json, ... (at most 8 rows per card, balanced). Symbols with no quote are skipped and listed.
Then write each file to the database as cards/<date-without-dashes>-mine1, -mine2 (see docs/DAILY-RUN.md).
"""
import argparse, datetime, json, os, subprocess, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
ap = argparse.ArgumentParser()
ap.add_argument("--date", default=datetime.date.today().isoformat()); ap.add_argument("--order", type=float, default=95)
ap.add_argument("--per-card", type=int, default=8); ap.add_argument("--batch", type=int, default=1); ap.add_argument("--kicker", default="Your portfolio")
ap.add_argument("symbols", nargs="+"); a = ap.parse_args()

def quote(sym):
    out = subprocess.run(["curl", "-s", "-m", "15", "-A", "Mozilla/5.0", f"https://query1.finance.yahoo.com/v8/finance/chart/{sym}?range=5d&interval=1d"], capture_output=True, text=True).stdout
    try:
        r = json.loads(out)["chart"]["result"][0]
        c = [x for x in r["indicators"]["quote"][0]["close"] if x] + [r["meta"]["regularMarketPrice"]]
        return {"sym": sym, "price": c[-1], "pct": (c[-1] / c[0] - 1) * 100, "series": [round(x, 2) for x in c]}
    except Exception: return None

rows, skipped = [], []
for s in dict.fromkeys(x.upper() for x in a.symbols):
    q = quote(s); (rows if q else skipped).append(q or s)
rows.sort(key=lambda q: q["pct"])
fmt = lambda q: {"label": q["sym"], "value": f"${q['price']:,.2f}", "delta": ("+" if q["pct"] >= 0 else "−") + f"{abs(q['pct']):.1f}%", "series": q["series"]}
os.makedirs(os.path.join(ROOT, "cards_out"), exist_ok=True)
n_cards = max(1, -(-len(rows) // a.per_card)); size = -(-len(rows) // n_cards)      # balanced cards, at most --per-card rows
chunks = [rows[i:i + size] for i in range(0, len(rows), size)]
down = sum(1 for q in rows if q["pct"] < 0)
for n, ch in enumerate(chunks, 1):
    card = {"kind": "stocks", "topic": "markets", "kicker": a.kicker, "source": "Robinhood · Yahoo Finance", "date": a.date, "batch": a.batch, "order": a.order + (n - 1),
            "rows": [fmt(q) for q in ch]}
    if n == 1:
        w = rows[0]; card["headline"] = f"{down} of your {len(rows)} holdings fell this week"
        card["body"] = f"Hardest hit: {w['sym']} {w['pct']:+.0f}%" + (f", {rows[1]['sym']} {rows[1]['pct']:+.0f}%" if len(rows) > 1 else "") + ". Moves are over the last few sessions."
        card["body"] = card["body"].replace("-", "−")
    else:
        card["headline"] = "The rest of your holdings"; card["body"] = "Sorted worst to best over the same stretch."
    json.dump(card, open(os.path.join(ROOT, "cards_out", f"stocks-portfolio-{n}.json"), "w"))
print(json.dumps({"cards": len(chunks), "rows": len(rows), "skipped": skipped}))
