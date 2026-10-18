# Daily run: building a day's deck

This is the procedure Claude follows each morning (or whenever the user says "make today's reels"). Total time: about 30 minutes for 24 reels, mostly rendering (about a minute each, one at a time).

> Replace example values (dates, URLs) with real ones. `<ARTIFACT_URL>` is `artifact_url` from `config.json`.

## What can be automated

| Part | Automated? |
|---|---|
| Reading connectors, writing stories, rendering, uploading | Needs the **user's computer awake and logged in**. Best option: a launchd timer that starts a background interactive Claude session at 07:00 (see [SCHEDULING.md](SCHEDULING.md)); print-mode `claude -p` cannot publish because it has no Artifact tools. Alternatives: a session-scoped cron (`CronCreate`), which only works while a session is open and expires after 7 days; or running it by hand. A cloud routine cannot render video or use locally added connectors. |
| 9:00 AM nudge | Yes, as a recurring Google Calendar event (runs on Google's servers, even if the computer is asleep). It cannot know whether new reels exist. |
| "More" pressed on the phone | Only queues a request (`requests/pending`). A Claude session must pick it up. |

Be upfront about this with the user. Do not promise unattended daily rendering.

## Step 1: Gather inputs

1. **Config**: read `config.json` (interests, tickers, reels per batch, flags).
2. **Ratings**: read collections `ratings` and `signals` (see [Using ratings](#using-ratings-to-personalize)).
3. **News**: fetch RSS with `curl -sL -A 'Mozilla/5.0' <url>`. Feeds that worked when this was built:

   | Beat | Feeds |
   |---|---|
   | AI / tech | `https://techcrunch.com/feed/`, `https://www.theverge.com/rss/index.xml` (sometimes empty), `https://feeds.arstechnica.com/arstechnica/index`, `https://www.wired.com/feed/rss` |
   | World / US | `https://feeds.bbci.co.uk/news/rss.xml`, `https://feeds.npr.org/1001/rss.xml`, `https://feeds.theguardian.com/theguardian/world/rss`, `https://www.aljazeera.com/xml/rss/all.xml` |
   | Bay Area / CA | `https://sfist.com/feed/` (use `curl -L`) |
   | Space / science | `https://www.nasa.gov/feed/` |
   | Markets | `https://www.cnbc.com/id/100003114/device/rss/rss.html`, `https://feeds.content.dowjones.io/public/rss/mw_topstories` |

   Not working: KQED (404), SF Chronicle (blocked), Yahoo Finance RSS (empty). Check feeds still work before relying on them.
4. **Quotes**: `https://query1.finance.yahoo.com/v8/finance/chart/<SYMBOL>?range=5d&interval=1d` (no key). Weekly move = last price vs first close in the range; say "since Monday's close" or similar, and verify the arithmetic.
5. **Calendar** (if enabled): list today's and tomorrow's events with the Calendar connector. Do not show the "Daily Reel" notification event.
6. **Gmail** (if enabled): search `is:unread in:inbox newer_than:2d category:primary`. Keep **sender and subject only**; skip security alerts and promotions.
7. **Portfolio** (if `use_portfolio_from_robinhood`): read-only Robinhood tools only (CLAUDE.md rule 1). The tools need an explicit account number and must never choose one themselves, so read `robinhood_accounts` from `config.json` (never print them). For each account call `get_equity_positions`; take the union of the symbols; skip symbols that have no Yahoo quote (for example warrants); fetch 5-day closes from Yahoo; and build the cards with one command: `python3 pipeline/portfolio_cards.py --date <today ISO> --order 35 SYM1 SYM2 ...` (tickers only; it fetches Yahoo closes, sorts worst weekly move first, balances up to 8 rows per card, and writes `pipeline/cards_out/stocks-portfolio-N.json`). Write each file to the database as `cards/<YYYYMMDD>-mine1`, `-mine2`, ... Never include quantities, cost basis or account identifiers. If `robinhood_accounts` is empty, call `get_accounts`, report which accounts exist (type and last four digits only), and fall back to the `tickers` list for this run.

## Step 2: Choose stories

Aim for `reels_per_batch` reels in batch 1 and the same again in batch 2. Mix the beats, interleave them by order, and lead with the strongest story. Skip stories centered on violence against individuals or graphic crime. Use [Using ratings](#using-ratings-to-personalize) to weight beats and sources.

### Avoid duplicates

Never write, voice or render a story twice. `pipeline/dedupe.py` keeps a ledger of every story used (`pipeline/seen.json`, git-ignored; `produce.py` also records each rendered story). For **every** candidate, before writing anything:

```bash
python3 pipeline/dedupe.py seed            # once per run: loads all story files into the ledger
python3 pipeline/dedupe.py check --url "<article url>" --title "<headline>"
python3 pipeline/dedupe.py record --id <story-id> --url "<url>" --title "<headline>"     # right after choosing it
```

`duplicate` (same article URL, or near-identical title/names) means skip. `similar` (shares two or more proper names or overlapping wording, often the same event from another outlet) means skip unless the article adds materially new facts, and say why in the report. `new` means proceed. It is a heuristic, so use judgment on `similar`. Also use the article's own URL as `url`, never a homepage or feed URL.

## Step 3: Write story files

One file per reel in `pipeline/stories/<id>.json`, following [STORY-SCHEMA.md](STORY-SCHEMA.md): hook, 5 to 6 short sentences, 3 to 5 concrete footage keywords, optional `bars`, and 4 AI-written reactions. Facts only from the source text.

You may delegate story writing to subagents (one beat each). Tell them: write story files only, do **not** run `produce.py` in parallel, do not curl Mixkit.

## Step 4: Render

Sequentially, one story at a time:

```bash
python3 pipeline/produce.py pipeline/stories/<id>.json        # about 50 s each, run from the repo root
```

Or all stories lacking an MP4: `cd pipeline && ./render_all.sh` (it waits out a Mixkit block first).

QA each reel: `ffprobe -v error -show_entries format=duration -of csv=p=0 out/reels/<id>.mp4` (expect 14 to 26), then look at `out/reels/<id>.jpg`. If the headline overflows or the footage is wrong, fix `headline` or `keywords` and re-run that story.

## Step 5: Upload

With the Artifact tool, `asset: true`, `url: <ARTIFACT_URL>`, and `file_paths` (up to 25 files per call, so 12 reels' MP4 plus JPG per call), upload `out/reels/<id>.mp4` and `<id>.jpg`. Each result prints `-> "/_blob/<id>"`. Record them in `pipeline/uploads.json`:

```json
{ "mkt-example": { "video": "/_blob/<video-id>", "poster": "/_blob/<poster-id>" } }
```

## Step 6: Build and write cards

```bash
python3 pipeline/make_cards.py --date 2026-10-16 --batch 1 --start 10 id1 id2 id3     # reels in batch 1, orders 10, 20, 30
python3 pipeline/make_cards.py --date 2026-10-16 --batch 2 --start 200 id4 id5        # batch 2
```

This writes `pipeline/cards_out/<id>.json`. Then write to the database with the `ArtifactData` tool, a `batch` action, one `set` per card, `collection: "cards"`, `doc_id: "r-<id>"`, `file_path: "<cards_out file>"` (up to 50 writes per batch; pin existing docs with `if_version`).

Also write the text cards (hand-built JSON, shapes in [PAGE.md](PAGE.md#cardsdocid)), interleaved between reels by `order`:

- `intro` at order 0, e.g. "12 reels to start. Pull down or tap More for another 12. Tap to pause, double-tap to like."
- `schedule` after the first reels, `inbox`, then `stocks` card(s).

**Replacing yesterday's deck**: old cards have an older `date` and are ignored by the page. Reset `meta/state` to `{"revealed": 1}`. Delete database cards older than 3 days. Assets can only be deleted with a human confirmation, so prune old assets in an interactive session ("prune old reels"); the artifact allows 1 GiB and about 100 MB per day is used.

Finally write `meta/latest` last: `{ "date": "<today ISO>", "count": <n>, "generatedAt": "<ISO>" }`.

**Verify**: query `cards` where `date == today`, ordered by `order`; confirm the count and that batch 2 cards have `batch: 2`.

## Using ratings to personalize

Read `ratings/*` and `signals/*` for recent days. This is a simple heuristic, not machine learning:

- Per `topic` and per `source`: like = +2, dislike = -3, finished (`finished: true` or `done`) = +1, skipped (dwell under 2 s, not finished) = -1. Average per reel, shrink toward zero for few samples.
- Allocate batch 1 slots across topics roughly in proportion to `1 + score`, but never drop a topic below 1 reel (so the user can discover), and keep one wildcard story.
- Order reels by expected interest, mixing topics so the same topic does not appear twice in a row.
- Add a short `why` to reels that benefited, such as "You liked 3 AI reels". Do not invent reasons.
- Mention in the intro card what changed ("More AI today, less world news").

## Requests from the phone

When the user presses More with no unrevealed batch, the page writes `requests/pending` (`status: "open"`). During a session, check it: read `requests/pending`; if `open`, build `want` more reels as a new batch (`after + 1`), write them with `batch` equal to `after + 1` and set the doc to `{"status": "done", ...}`. A session can poll with `/loop`, but only while it is open and the computer is awake.

## Notification (9:00 AM)

Ask first (it edits the user's calendar). Then, with the Calendar connector's `create_event`: summary `Daily Reel`; start tomorrow at the configured time in the user's time zone; 15 minutes; `recurrenceData: ["RRULE:FREQ=DAILY"]`; `availability: AVAILABILITY_FREE`; `useDefaultReminders: false`; `overrideReminders: [{"method": "popup", "minutes": 0}]`; `notificationLevel: NONE`; no attendees; description containing the feed link.

Optional richer push: install the free ntfy app, pick a long random topic, and after a build run `curl -d "12 new reels" ntfy.sh/<topic>`. Topics are effectively public; put no personal content in the message.

## Step 7: Clean up

```bash
rm -rf pipeline/cache pipeline/work pipeline/cards_out
```

`produce.py` already removes HyperFrames' temp frame cache after each reel. Keep `pipeline/out/` only if the user wants local copies (it is git-ignored). Report to the user: link, counts, what could not be verified.
