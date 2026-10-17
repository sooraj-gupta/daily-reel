# The feed page

`page/index.html` is a single self-contained HTML file published as a **private Claude Artifact**. No build step, no dependencies besides Google Fonts.

## Publishing

Publish with the Artifact tool, with these settings:

| Setting | Value |
|---|---|
| file | `page/index.html` |
| capabilities | `{"db": {}, "downloads": true, "assets": {}}` |
| icon | `feed` |
| privacy | leave private; only the user shares it |

- `db`: cards, ratings, watch signals, requests.
- `downloads`: lets the share button offer the MP4 for saving (on iOS in the Claude app this should open the share sheet; unverified).
- `assets`: needed for Claude to upload the MP4 and JPG files. The page itself references them by URL.

To update an existing artifact, publish the same file path again (keeps the URL). Small edits can use the Artifact tool's `edits` parameter.

## What the page does

- Vertical, snap-scrolling feed; one card per screen; phone-width column (max 480 px) on wide screens.
- **One persistent `<video id="player">`** hops into the active reel card. After the user taps "Play with sound" once, sound keeps working on later reels (iOS requirement).
- Controls: **Auto** (auto-next after a reel ends), **Sound/Muted**, **More** (reveal next batch or request more). Tap = pause/play, double-tap = like with a heart, pull down at the top = More, arrow keys / space on desktop.
- Right rail per reel: like, dislike, reactions (AI-written, labeled), share (saves the MP4).
- Bottom bar per reel: source and "Read story" link; thin progress line.
- Text cards: `intro`, `schedule` (calendar), `inbox`, `stocks` (rows with sparklines), plus a generated `end` card with a watched counter and a "Load more reels" button.
- Streak counter (per device, in local storage) and a watched count (`done`).
- Records **ratings** and **watch signals** to the database.

## Database collections

All documents are JSON. Paths follow the Artifact `db` rules (collection/doc).

### `meta/latest`
`{ "date": "2026-10-16", "count": 29, "generatedAt": "<ISO>" }`. The page shows the deck whose cards have this `date`. Write it **last** when publishing a new deck.

### `meta/state`
`{ "revealed": 1, "updatedAt": "<ISO>" }`. Highest batch the user has revealed. The page writes it; default is 1. Reset to `{"revealed": 1}` when you publish a new deck.

### `cards/<docId>`
Common fields: `kind`, `date` (ISO, matches `meta/latest`), `order` (number; sorts the feed ascending; fractions allowed), `batch` (integer, default 1; cards with `batch` greater than `revealed` are hidden), `topic`, `kicker`, `headline`/`headline_text`, `source`, `url`.

| kind | Used for | Extra fields |
|---|---|---|
| `reel` | A video | `headline_text`, `video` (`/_blob/<id>`), `poster` (`/_blob/<id>`), `duration`, `comments` (array of `{who, text}`, up to 4), optional `why` (small caption such as "You liked 3 AI reels") |
| `intro` | First card | `headline`, `body`, `kicker`, `ghost` |
| `schedule` | Calendar summary | `headline`, `body`, `kicker`, `topic: "calendar"` |
| `inbox` | Gmail summary | `rows`: `[{label, sub}]` (sender or subject only), `topic: "inbox"` |
| `stocks` | Tickers | `rows`: `[{label, value, delta, series}]`; `delta` starts with `+` or `−` (U+2212); `series` is an array of closes; `topic: "markets"` |

Doc ids: reels are `r-<story-id>`; others use any unique id. Topics: `ai`, `tech`, `bayarea`, `world`, `markets`, `spark`, `inbox`, `calendar`, `you`.

### `ratings/<cardDocId>`
`{ value: 1 | -1, date, cardId, topic, kind, source, headline, ts, dwell, finished }`. Written by the page when the user likes or dislikes. Deleting the doc clears the rating.

### `signals/<date>`
`{ date, dwell: { <cardDocId>: seconds }, done: { <cardDocId>: true }, updatedAt }`. `dwell` is seconds spent on each card; `done` marks reels watched past 90%.

### `requests/pending`
`{ at, want: 8, after: <revealedBatch>, status: "open" }`. Written when the user asks for more reels and no unrevealed batch exists. See [DAILY-RUN.md](DAILY-RUN.md#requests-from-the-phone).

## Editing the page

- Keep it dependency-free. External hosts allowed by the Artifact sandbox: Google Fonts only for styles; CDN scripts from a short allowlist (not used here).
- Colors are tokens on `:root`; the page is deliberately dark-only.
- Scripts must tolerate `claude.use('db')` returning `null`.
- After a change: `node --check` on the extracted script, publish, read back one `cards` query, and tell the user what you could not test (playback, sound, share sheet).
- Do not write to the database from render code or timers; writes happen on user actions and a 20-second signal flush.
