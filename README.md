# Daily Reel

A personal morning briefing that looks like a feed of short vertical videos instead of a wall of text.

Every reel is a ~17 to 20 second video: a human-sounding voiceover, stock footage that matches the story, a big headline, word-by-word captions, animated stock bars for market stories, and a quiet music bed. Your calendar, inbox summary and portfolio show up as cards in the same feed. You like or dislike each reel, and that feedback is saved so tomorrow's deck can lean toward what you actually watch.

It is built to be set up by [Claude Code](https://claude.com/claude-code). You do not follow the setup steps yourself: you point Claude at this repo and it does the work, asking you only for the few things nobody else can do (signing in, linking billing, approving connectors).

## Quick start

Open Claude Code in an empty folder on your Mac and say:

> Set up https://github.com/sooraj-gupta/daily-reel for me.

Claude reads [`CLAUDE.md`](CLAUDE.md), follows [`SETUP.md`](SETUP.md), and checks in with you at each step that needs you.

## What you get

- **A vertical video feed** (a private page on claude.ai) with autoplay, auto-next, tap to pause, double-tap to like, a share button that saves the MP4, and a watched counter.
- **AI-written reactions** under each reel, clearly labeled as AI commentary (not real viewers, not real engagement numbers).
- **Reels made on your machine**: voice (Google Cloud Text-to-Speech), footage (Mixkit, free), rendering (HyperFrames + ffmpeg). About 50 seconds and 3 to 5 MB per reel.
- **Personalization**: likes, dislikes and watch time are stored and read by Claude each morning.
- **Optional private cards**: today's calendar, a Gmail summary (subjects and senders only), and a read-only portfolio snapshot.
- **A 9:00 AM calendar alert** with a link to the feed, and an optional 7:00 AM headless build so the deck is ready ([docs/SCHEDULING.md](docs/SCHEDULING.md)).

## Requirements

| Need | Why | Cost |
|---|---|---|
| Claude Code, on a claude.ai plan that supports Artifacts | Runs the setup and the daily build; hosts the feed page | your Claude plan |
| macOS or Linux, Node 22+, Python 3.9+, ffmpeg | Renders the reels | free |
| About 8 GB free disk | Rendering uses a few GB of temporary frames | free |
| A Google Cloud project with billing linked | Voice (Text-to-Speech) | free allowance, then pay-per-use; see [docs/COSTS-AND-KEYS.md](docs/COSTS-AND-KEYS.md) |
| Optional: Gmail, Google Calendar connectors; Robinhood read-only | Private cards | free |

No key is needed for footage or music (Mixkit). Details and signup links: [docs/COSTS-AND-KEYS.md](docs/COSTS-AND-KEYS.md).

## Safety and privacy in one paragraph

The feed page is private to your claude.ai account. Nothing personal is committed to this repo (see [`.gitignore`](.gitignore)). The Robinhood connection is **read-only by design**: Claude is instructed never to call any order, cancel or exercise tool. Reels contain no share counts or dollar balances. Reactions are labeled as AI. Read [docs/PRIVACY-AND-SAFETY.md](docs/PRIVACY-AND-SAFETY.md) before you connect anything.

## Honest limits

- Footage is **generic stock b-roll** that illustrates a topic, not footage of the actual event. Crypto and niche topics have thin footage.
- Making new reels needs your computer and a Claude session. Pressing "More" on the phone only queues a request; it cannot render video. See [docs/DAILY-RUN.md](docs/DAILY-RUN.md) for what can and cannot be automated.
- Mixkit rate-limits aggressive scraping (HTTP 429). The producer throttles itself; do not run many renders in parallel. See [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md).
- The music is royalty-free, not trending TikTok audio (that is copyrighted and not downloadable here).
- Pricing and free-tier numbers in the docs came from secondary sources and are flagged where unverified.

## Repo map

| Path | What it is |
|---|---|
| [`CLAUDE.md`](CLAUDE.md) | Instructions for Claude Code: rules, setup entry point, file map |
| [`SETUP.md`](SETUP.md) | Step-by-step setup that Claude follows |
| [`docs/`](docs/README.md) | Architecture, daily runbook, page data model, schemas, safety, costs, troubleshooting, licenses |
| [`page/`](page/README.md) | The feed web page (single HTML file) |
| [`pipeline/`](pipeline/README.md) | Voice, footage, rendering, and card-building scripts |
| [`pipeline/stories/`](pipeline/stories/README.md) | One JSON file per reel (examples included) |
| [`scripts/`](scripts/README.md) | Environment check, voice-key creator, music downloader |
| [`config/`](config/README.md) | Example personal configuration |

## License

MIT, see [`LICENSE`](LICENSE). Third-party footage, music and services have their own terms: [docs/LICENSES.md](docs/LICENSES.md).
