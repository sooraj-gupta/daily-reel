# SETUP.md

Setup procedure for Claude Code. Do the steps in order. After each step, run its **Verify** command and only continue when it passes. Steps marked **USER ACTION** need the user; tell them exactly what to do and wait.

Before you start, read [`CLAUDE.md`](CLAUDE.md) (hard rules) and tell the user, in three sentences, what you are about to do and roughly how long it takes (20 to 30 minutes plus the user's account steps).

## 0. Ask the setup questions

Ask these together, once, then store the answers in `config.json` (step 6):

1. Time zone (default `America/Los_Angeles`) and notification time (default 9:00).
2. Interests: any of `ai`, `tech`, `bayarea`, `world`, `markets`, `spark` (curiosity). Default all.
3. Tickers to track (markets cards). Or "read my Robinhood holdings" (read-only, needs step 9).
4. Include Gmail summary card? Include Calendar card?

## 1. Check the machine

```bash
scripts/check_env.sh
```

It reports PASS/FAIL/WARN. Fix every FAIL. Ask before installing system software.

- Node 22+: `brew install node` or `nvm install 22`
- ffmpeg: `brew install ffmpeg` (Linux: `apt install ffmpeg`)
- Python 3.9+: standard library only, nothing to pip install

**Verify:** `scripts/check_env.sh` prints no `FAIL`.

## 2. Make sure there is disk space

Rendering writes a few GB of temporary frames. If `check_env.sh` warns about disk, tell the user how much is free and suggest safe cleanups (package manager caches such as `npm cache clean --force`). Do not delete the user's files without asking.

**Verify:** at least ~8 GB free.

## 3. Install the renderer

```bash
cd pipeline && npm install && npx hyperframes browser ensure
```

`browser ensure` downloads a headless Chrome (about 200 MB) that HyperFrames uses.

**Verify:** `npx hyperframes browser path` prints a path.

## 4. Voice key (Google Text-to-Speech)

**USER ACTION**, in this order:

1. Install and sign in to the Google Cloud CLI. Tell the user to run this in the Claude prompt so the sign-in happens in their browser:
   `! gcloud auth login`
2. Have a Google Cloud project. If they have none, create one: `gcloud projects create daily-reels-<random digits> --name="Daily Reels"` (ask first).
3. Link a billing account to that project at <https://console.cloud.google.com/billing>. Text-to-Speech will not work without it, even inside the free allowance. You must not enter card details; the user does this in the console.
4. Recommend a $5 budget alert: <https://console.cloud.google.com/billing/budgets>.

Then run (safe to re-run; it never prints the key):

```bash
scripts/create_tts_key.sh <project-id>
```

**Verify:** the script prints `OK: key saved ... (HTTP 200)`.

If the user prefers another voice provider, only `pipeline/make_voice.py` changes: it must write `voice.wav` and `timings.json` (see [docs/COSTS-AND-KEYS.md](docs/COSTS-AND-KEYS.md)).

## 5. Music

```bash
scripts/fetch_music.sh
```

Downloads six royalty-free beats from Mixkit into `pipeline/music/`.

**Verify:** the script ends with `tracks available: 6`.

## 6. Personal config

```bash
cp config/config.example.json config.json
```

Edit `config.json` with the answers from step 0. This file is git-ignored. See [config/README.md](config/README.md) for each field.

**Verify:** `python3 -c "import json;json.load(open('config.json'))"` succeeds.

## 7. Render a test reel

```bash
cd pipeline && python3 produce.py stories/example-markets.json
```

Takes about a minute. If it prints a Mixkit 429 or "no footage found", wait and retry; see [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md).

**Verify:** `ffprobe -v error -show_entries format=duration -of csv=p=0 pipeline/out/reels/example-markets.mp4` prints 14 to 26. Open the file for the user (`open pipeline/out/reels/example-markets.mp4` on macOS) and ask if the look and voice are right. Voice, speed and music volume are in `config.json`.

## 8. Publish the feed page

Use the Artifact tool to publish `page/index.html` as a **new private artifact** with:

- `capabilities`: `{"db": {}, "downloads": true, "assets": {}}`
- `icon`: `feed`
- `description`: "A vertical video feed of your daily news, markets, inbox and calendar, with AI reactions, likes that tune tomorrow, and a share button."

Save the returned URL into `config.json` under `artifact_url`. Keep the artifact private; only the user decides about sharing (it contains their feed).

**Verify:** the publish result says the artifact is private and lists capabilities `assets; db; downloads`.

## 9. Optional connectors (USER ACTION for each)

Only for what the user said yes to in step 0.

- **Gmail and Google Calendar**: the user types `/mcp` and authorizes "claude.ai Gmail" and "claude.ai Google Calendar".
- **Robinhood, read-only**: the user runs
  `! claude mcp add --scope user --transport http robinhood-trading https://agent.robinhood.com/mcp/trading`
  then `/mcp` and signs in on Robinhood's own page. Availability may depend on Robinhood's Agentic Trading access. You will use **only the read tools listed in CLAUDE.md rule 1**. Tell the user that plainly.

**Verify:** the connector's tools appear in your tool list (load them with ToolSearch).

## 10. Build the first deck

Follow [docs/DAILY-RUN.md](docs/DAILY-RUN.md) end to end. For a first deck: 12 reels in batch 1 and, if the user wants refresh to work immediately, 12 more in batch 2.

**Verify:** read back the `cards` collection and confirm the card count, the `batch` split and that `meta/latest` has today's date.

## 11. Morning notification (ask first)

Offer a recurring 9:00 calendar event with the feed link (see "Notification" in [docs/DAILY-RUN.md](docs/DAILY-RUN.md)). Creating it changes the user's calendar, so get a clear yes.

## 11b. Daily schedule (ask first)

Offer the 7:00 AM headless build described in [docs/SCHEDULING.md](docs/SCHEDULING.md). It runs Claude unattended with access to the connectors the user enabled, so explain the allow-list and the limits first and get a clear yes. Prerequisites (USER ACTION): the user runs `claude` once in the repo folder and accepts "Yes, I trust this folder", then `/exit`; and Robinhood must have been added with `--scope user` (step 9). Then run `scripts/daily_run.sh --dry-run`, show the user the result (expect 9 of 9), and only then `scripts/install_schedule.sh 07:00`. The optional `sudo pmset` wake command is for the user to run.

## 12. Clean up and report

```bash
rm -rf pipeline/cache pipeline/work pipeline/cards_out
```

Then tell the user, in plain language: the feed link; what you could verify and what you could not (you cannot see the page or hear audio); what is not automated (see "What can be automated" in docs/DAILY-RUN.md); and where the files are.
