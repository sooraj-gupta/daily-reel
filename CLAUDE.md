# CLAUDE.md

You are Claude Code, working in the **Daily Reel** repository. This file is your entry point. Read it fully before doing anything.

## What this project is

A personal daily briefing delivered as a feed of short vertical videos ("reels"). A pipeline in `pipeline/` turns story files into MP4 reels (voiceover + stock footage + captions + music). A single-file web page in `page/` plays them as a swipeable feed, hosted as a private Claude **Artifact** with a small database that stores cards, ratings and watch signals. You (Claude) write the stories each morning, render them, upload them, and read the user's ratings to personalize the next deck.

Architecture in one picture: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

## If the user asked you to set this up

Follow [`SETUP.md`](SETUP.md) from the top, one step at a time. Do not skip the verification after each step. Do not batch the questions: ask only what you need for the next step. The steps that **only the user can do** are marked `USER ACTION`; tell them exactly what to type and wait.

## If the user asked you to make today's reels (the daily run)

Follow [`docs/DAILY-RUN.md`](docs/DAILY-RUN.md).

## If the user asked you to change something

Use the file map below to find the owner of the behavior, read that folder's `README.md`, change it, and update the matching doc in the same change. Docs and code must not drift.

## Hard rules (never break these)

1. **No trading, ever.** The Robinhood connection is read-only. You may call only: `get_accounts`, `get_equity_positions`, `get_portfolio`, `get_equity_quotes`, `get_equity_historicals`, `get_watchlists`, `get_watchlist_items`. You must never call any tool whose name starts with `place_`, `cancel_`, `exercise_`, `create_`, `update_`, `delete_`, `add_`, `remove_`, `follow_`, `unfollow_` or `decline_`, or `review_`/`preview_` order tools. If the user asks you to trade, say you are set up read-only and stop.
2. **Never print, log, commit or paste a secret.** API keys live only in `~/.daily-reels.env` (mode 600). When reading it, show variable *names* only. Never ask the user to paste a key into chat; have them save it to the file themselves, or use `scripts/create_tts_key.sh`, which writes it without displaying it.
3. **Never put personal data in the repo or on the page beyond what the docs allow.** No share counts, cost basis, balances, email bodies, or email addresses on cards. Inbox cards show sender and subject only. Portfolio cards show tickers, price and percent change only. See [docs/PRIVACY-AND-SAFETY.md](docs/PRIVACY-AND-SAFETY.md).
4. **Reactions are AI commentary and must say so.** Each reel's `comments` are written by you under fixed archetype personas ("The optimist", "The skeptic", "The nerd", "The one who read the article", "The doomscroller", "The practical one"). Never present them as real people, never invent statistics or like counts, never attribute a quote to a real person.
5. **Facts only from sources.** Story text uses only facts present in the feed excerpt or data you fetched. Attribute claims ("says", "reports"). No financial advice, no predictions unless attributed. Double-check every percentage you compute.
6. **Ask before outward-facing or hard-to-reverse actions**: publishing the page for others, sharing links, creating calendar events, deleting data, installing system software, spending money, linking billing. Approval for one does not carry over to the next.
7. **Do not hammer Mixkit.** `pipeline/produce.py` throttles itself. Render stories **one at a time**. Never run several renders or many curl probes in parallel; that triggers HTTP 429 blocks lasting about an hour. See [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md).
8. **Clean up after rendering**: `pipeline/cache/`, `pipeline/work/`, and the temp folder `hyperframes-extract-cache-*` can reach several GB. `produce.py` removes the temp frame cache after each reel; delete `pipeline/cache/` and `pipeline/work/` when a batch is done.
9. **Do not use a computer-use or browser tool to enter credentials** for the user. Sign-ins are `USER ACTION`.

## File map

| Path | Owns | Read this first |
|---|---|---|
| `SETUP.md` | First-time setup procedure | itself |
| `docs/ARCHITECTURE.md` | How the parts fit; data flow | itself |
| `docs/DAILY-RUN.md` | The morning build, step by step; ratings-based selection; requests; notifications | itself |
| `docs/PAGE.md` | The feed page: features, capabilities, database collections and card schema | itself |
| `docs/STORY-SCHEMA.md` | Story JSON fields and writing rules | itself |
| `docs/PRIVACY-AND-SAFETY.md` | What may and may not be shown or stored | itself |
| `docs/COSTS-AND-KEYS.md` | Accounts, keys, costs | itself |
| `docs/TROUBLESHOOTING.md` | Every failure we hit and the fix | itself |
| `docs/LICENSES.md` | Footage, music, voice and tool terms | itself |
| `page/index.html` | The feed (Artifact page) | `page/README.md` |
| `pipeline/produce.py` | One story JSON in, one MP4 + poster + metadata out | `pipeline/README.md` |
| `pipeline/make_voice.py` | Google TTS per sentence, word timings | `pipeline/README.md` |
| `pipeline/build_reel.py` | Builds the HyperFrames composition | `pipeline/README.md` |
| `pipeline/make_cards.py` | Finished reels to database card documents | `pipeline/README.md` |
| `pipeline/render_all.sh` | Render every story without an MP4, sequentially | `pipeline/README.md` |
| `pipeline/stories/` | Story files (two examples) | `pipeline/stories/README.md` |
| `pipeline/template/` | Boilerplate copied into each render project | `pipeline/template/README.md` |
| `pipeline/music/` | Music tracks (downloaded, not committed) | `pipeline/music/README.md` |
| `scripts/` | `check_env.sh`, `create_tts_key.sh`, `fetch_music.sh` | `scripts/README.md` |
| `config/` | `config.example.json`; the user's real `config.json` lives at the repo root and is git-ignored | `config/README.md` |

## Conventions

- Dates in file names and database fields are ISO (`2026-10-16`). The on-video date label is free text (`Fri Oct 16`).
- Story id = file name without `.json`, lowercase-hyphen, prefixed by beat: `ai-`, `tech-`, `bay-`, `world-`, `mkt-`, `spark-`.
- Feed card documents are named `r-<story-id>` for reels; fixed names for the rest (see docs/PAGE.md).
- Python is plain stdlib (no pip installs). Node is only for HyperFrames. Keep it that way.
- Never commit `config.json`, `uploads.json`, `out/`, `cache/`, `work/`, `*.mp4`, `*.mp3`. They are in `.gitignore`; check `git status` before every commit.
- Commit messages: short imperative summary, then a blank line and what/why.

## Verifying your own work

- Environment: `scripts/check_env.sh` (read-only; prints PASS/FAIL/WARN).
- A single reel end to end: `cd pipeline && python3 produce.py stories/example-markets.json` (about a minute; writes `pipeline/out/reels/example-markets.mp4`). Check the duration with `ffprobe` and look at the poster JPG.
- The page: after publishing, read back the `cards` collection once and confirm the count and `order` values. You cannot see the rendered page or hear audio; tell the user what you could not verify.
