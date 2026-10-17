# pipeline/

Turns story files into reels and into database cards. Plain Python 3 (standard library only) plus Node for HyperFrames.

## Files

| File | Role |
|---|---|
| `produce.py` | **Main entry.** `python3 produce.py stories/<id>.json` makes `out/reels/<id>.mp4`, `<id>.jpg` and `<id>.json`. Voice, footage, music, build, render, compress, poster, cleanup |
| `make_voice.py` | Google TTS per sentence, converts to WAV, measures durations, writes `voice.wav` and `timings.json` into the given folder |
| `build_reel.py` | Reads a spec and the timings and writes a HyperFrames project (`index.html` plus an `assets` link) |
| `make_cards.py` | Turns finished reels into card JSON files in `cards_out/` (needs `uploads.json`) |
| `render_all.sh` | Renders every story lacking an MP4, one at a time; waits out a Mixkit block first |
| `package.json` | Pins `hyperframes` |
| `stories/` | Story JSON files: [stories/README.md](stories/README.md) |
| `template/` | Boilerplate copied into each render project: [template/README.md](template/README.md) |
| `music/` | Downloaded music (not committed): [music/README.md](music/README.md) |

Generated, git-ignored folders: `cache/` (footage clips and search results), `work/` (per-story scratch), `out/` (finished reels), `cards_out/` (card documents), `node_modules/`. `uploads.json` (asset ids) is also git-ignored.

## Usage

```bash
cd pipeline
npm install && npx hyperframes browser ensure     # once
python3 produce.py stories/example-markets.json    # about 50 seconds
ls out/reels                                       # example-markets.mp4, .jpg, .json
```

Configuration: optional `../config.json` (voice, voice_rate, music_volume). Secrets: `~/.daily-reels.env` must contain `GOOGLE_TTS_API_KEY`.

## What `produce.py` does, in order

1. Writes `work/<id>/assets/script.json`, runs `make_voice.py` (voice speed from `rate` in the story, else config, else 1.2).
2. For each sentence picks one footage clip: searches `https://mixkit.co/free-stock-video/discover/<keyword>/`, takes clip ids not yet used in this reel (deterministic by story id), downloads the 720p file, skips clips under 6 seconds. Search results are cached for 24 hours in `cache/search_<keyword>.txt` (empty results are never cached). All Mixkit page requests share one lock and are spaced at least 3 seconds apart; HTTP 429 backs off 25 s x attempt.
3. Picks one of the tracks in `music/` by hashing the story id; volume 0.16 by default.
4. Runs `build_reel.py` to write the HyperFrames project, then `npx hyperframes render . -q standard -f 30 -w 2`.
5. Re-encodes with ffmpeg (H.264, CRF 27, max 2.8 Mbit/s, faststart), cuts a poster at 2.5 s, writes `out/reels/<id>.json` with metadata.
6. Deletes the render project and HyperFrames' temp frame cache.

## Rules for anyone running this

- One render at a time. Parallel runs trigger Mixkit blocks.
- Never commit `out/`, `cache/`, `work/`, `*.mp4`, `*.mp3`.
- After a batch: `rm -rf cache work cards_out`.
- Failure fixes: [../docs/TROUBLESHOOTING.md](../docs/TROUBLESHOOTING.md).

## Changing the look

All layout lives in `build_reel.py` (CSS inside the generated HTML: positions in a 1080x1920 canvas, fonts, colors per topic come from `produce.py`'s `HUES` and `CHIPS`). After a change, render `stories/example-markets.json`, grab frames with `ffmpeg -ss 5 -i out/reels/example-markets.mp4 -frames:v 1 frame.png`, and look at them (headline fits, captions do not overlap the bars).
