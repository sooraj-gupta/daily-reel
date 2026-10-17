# Costs and keys

Only one account is required: **Google Cloud** for the voice. Everything else is free or optional. Prices below come from secondary sources and could not be checked on official pricing pages when this was written. Verify before relying on them: <https://cloud.google.com/text-to-speech/pricing>.

## Required

| What | Why | Key | Cost |
|---|---|---|---|
| Google Cloud Text-to-Speech (Chirp 3 HD voices) | Voiceover | API key restricted to the Text-to-Speech API, saved as `GOOGLE_TTS_API_KEY` in `~/.daily-reels.env` | Reported free allowance of about 1 million characters a month; this project uses roughly 5,000 to 10,000 a day (about 150k to 300k a month). Billing must be linked even to use the free allowance. Set a $5 budget alert. |

Create the key with `scripts/create_tts_key.sh <project-id>` after the user has signed in with `gcloud auth login` and linked billing. The script never prints the key.

Voice choice: set `voice` in `config.json`. The default is `en-US-Chirp3-HD-Charon`; other Chirp 3 HD voices follow the pattern `en-US-Chirp3-HD-<Name>` (for example Aoede). Speed is `voice_rate` (1.2 by default; 1.0 is normal).

## No key needed

| What | Source | Notes |
|---|---|---|
| Stock footage | Mixkit (scraped keyword pages, direct mp4) | Free, no attribution. Rate-limits scraping; see [TROUBLESHOOTING.md](TROUBLESHOOTING.md) |
| Music | Mixkit hip-hop beats | `scripts/fetch_music.sh` |
| Rendering | HyperFrames (npm) + ffmpeg | Free. HyperFrames downloads its own Chrome |
| News | public RSS feeds | See [DAILY-RUN.md](DAILY-RUN.md) |
| Quotes | Yahoo Finance chart endpoint | Unofficial and unauthenticated; may change |

## Optional

| What | Needed for | How |
|---|---|---|
| Gmail and Google Calendar connectors | Inbox and schedule cards, 9:00 notification | `/mcp` in Claude Code, authorize the claude.ai connectors |
| Robinhood MCP (read-only) | Portfolio card | `claude mcp add --transport http robinhood https://agent.robinhood.com/mcp/trading`, then `/mcp`. Availability may depend on Robinhood's Agentic Trading access |
| ntfy | Richer push than the calendar alert | Install the free iOS/Android app; pick a long random topic |

## Things we checked and did not use

- **Pexels** (best stock source): new API keys were paused when this was built. If they reopen, the producer's footage search is the only place to change.
- **Pixabay**: free key, not implemented.
- **AI-generated video** (Veo, Kling, Runway and others): roughly $250 to $2,000 a month for 11 reels a day at 15 seconds each, per aggregator pages; also risks fake-looking news footage. Not used.
- **Other voices** (ElevenLabs about $22 a month, OpenAI TTS about $2 to $3 a month, Azure and Google free tiers, Kokoro free and local): all workable. To swap, rewrite `pipeline/make_voice.py` so it writes `voice.wav` (44.1 kHz mono) and `timings.json` (`{"duration": <s>, "words": [{"w": "word", "start": <s>, "end": <s>, "s": <sentence index>}]}`) into the folder passed as its first argument.

## Disk

Rendering is disk-hungry: HyperFrames caches extracted video frames in your temp folder (about 160 MB per reel; `produce.py` deletes it after each reel, but a crashed run can leave gigabytes). Footage clips cached in `pipeline/cache/` are about 30 MB per reel. Keep roughly 8 GB free.
