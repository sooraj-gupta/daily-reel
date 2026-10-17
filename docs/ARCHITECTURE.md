# Architecture

## The parts

```
 news RSS + quotes ─┐
 Gmail / Calendar ──┼─►  Claude (you)  ──►  stories/<id>.json  ──►  pipeline/produce.py  ──►  out/reels/<id>.mp4
 Robinhood (read) ──┤     writes scripts,         one file per            voice + footage              + .jpg poster
 ratings from page ─┘     comments, cards          reel                    + captions + render          + .json metadata
                                 │
                                 └─► Artifact tool: upload mp4/jpg as assets ─► database: cards/*  ─►  page/index.html
                                                                                       ▲                    │
                                                                      ratings/*, signals/*, requests/*  ◄───┘ (phone)
```

## Components

| Component | Where it runs | What it does |
|---|---|---|
| Claude Code session | the user's computer | Picks stories, writes scripts and reactions, runs the pipeline, uploads files, writes database documents, reads ratings |
| `pipeline/produce.py` | the user's computer | One story file to one MP4. Calls Google TTS, scrapes Mixkit footage lists, renders with HyperFrames, compresses with ffmpeg |
| HyperFrames | the user's computer | Renders an HTML/GSAP composition to MP4 using a headless Chrome it downloads |
| Artifact page (`page/index.html`) | claude.ai (private) | The feed. Plays videos, shows text cards, records ratings and watch signals |
| Artifact database (`db` capability) | claude.ai | Shared JSON documents: cards, ratings, signals, requests, meta |
| Artifact assets (`assets` capability) | claude.ai | Hosts the MP4 and JPG files, served at `/_blob/<id>` |

## Why it is shaped this way

- **Video is rendered locally, not in the page.** A browser page cannot render these videos, and a cloud scheduler would not have the user's connectors or tools. So rendering needs the user's computer and a Claude session.
- **The page only plays and records.** It cannot generate reels. "More" on the phone writes a request document that a Claude session picks up (see [DAILY-RUN.md](DAILY-RUN.md#requests-from-the-phone)).
- **One persistent `<video>` element** moves between cards in the page, so a sound permission granted once (required by iOS Safari) keeps working for later reels.
- **Batches** pre-generate extra reels so the first refresh is instant.
- **Ratings go to the database**, not local storage, so Claude can read them the next morning.

## What was verified and what was not

Verified by running it: the full pipeline (voice, footage, render, compress, poster) on a fresh clone; the card documents reading back correctly after being written; the key-creation script re-run safely.

Not verifiable by Claude, so confirm with the user: video playback and sound on the user's phone, the share button's save sheet, and the reactions sheet. Claude cannot see the page or hear audio.

## Data flow for one reel

1. Story file written (`pipeline/stories/<id>.json`).
2. `make_voice.py` calls Google TTS once per sentence at `voice_rate`, converts to WAV, measures each sentence, and spreads word times across it by letter count (`timings.json`).
3. `produce.py` picks one Mixkit clip per sentence (keyword search, deterministic by story id), downloads 720p, picks a music track.
4. `build_reel.py` writes a HyperFrames project (1080x1920): blurred background clip, sharp 1080x780 clip, headline, chip, optional animated bars, captions (3 words or 16 characters per chunk), progress bar, voice and music audio.
5. `npx hyperframes render` renders it; ffmpeg compresses to roughly 3 to 5 MB; a poster JPG is cut at 2.5 s.
6. Claude uploads MP4 and JPG as assets, records the returned ids in `uploads.json`, runs `make_cards.py`, and writes card documents.
