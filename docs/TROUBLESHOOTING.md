# Troubleshooting

Every problem below actually happened while building this.

## Mixkit returns HTTP 429 or "no footage found for sentence N"

Mixkit rate-limits scraping. Causes: several renders at once, or many keyword probes in a burst. The block lasted about an hour.

- Render **one story at a time**. Never launch parallel `produce.py` runs or subagents that run it.
- `produce.py` already throttles to one Mixkit page request every 3 seconds across processes and backs off on 429. It does not cache empty results.
- If blocked: stop all Mixkit requests, then run `pipeline/render_all.sh`. It checks every 4 minutes (up to 4 hours) and renders everything missing once Mixkit answers.
- Check status with one request: `curl -s -o /dev/null -w '%{http_code}\n' -A 'Mozilla/5.0' -L https://mixkit.co/free-stock-video/discover/robot/` (200 is fine). Check **one** keyword, not thirty.
- Footage downloads come from `assets.mixkit.co`, which was not blocked while the search pages were.

## A keyword has too little footage (bitcoin, press-conference, trampoline)

Mixkit lacks crypto and niche footage. Use concrete, generic visual nouns instead (`stock-market`, `trading`, `microphone`, `building`). The producer also falls back to `city`, `technology`, `business`, `night`, `abstract`.

## Disk fills up during or after rendering

HyperFrames' extracted-frame cache can reach several GB: `$TMPDIR/hyperframes-extract-cache-<uid>` (on macOS, `/var/folders/.../T/`). `npx hyperframes clean` does **not** remove it. After checking nothing is rendering (`ps aux | grep hyperframes`), delete that folder. `produce.py` does this after every successful reel. Also delete `pipeline/cache` and `pipeline/work` after a batch, and clear package caches (`npm cache clean --force`).

## `FileNotFoundError ... cache/.mixkit.lock`

Fixed: `produce.py` now creates `cache/`, `work/` and `out/reels/` itself. Update to the latest code.

## HyperFrames lint: `video_nested_in_timed_element`

A `<video>` with `data-start` must not sit inside another timed element. `build_reel.py` makes each video its own top-level layer. Do not wrap videos in timed divs. Remaining warnings about dense tracks and nested structure are style notes and safe to ignore.

## HyperFrames: font family warning

Fonts must be on its supported list or declared with `@font-face`. The builder uses Big Shoulders Display (loaded) with Impact/Arial Narrow fallbacks and system Helvetica for body text.

## Google TTS returns 403 or 400

- 403 "unregistered callers": the key was not sent or is wrong. Re-run `scripts/create_tts_key.sh <project>`.
- 403 "billing" or "API not enabled": link billing and enable `texttospeech.googleapis.com`.
- 400 on a voice name: use `en-US-Chirp3-HD-<Name>`.
- ffmpeg "Invalid data found" when joining audio: fixed by converting each sentence's MP3 to WAV before measuring and concatenating (already done in `make_voice.py`).

## Captions drift from the voice

Word times are estimated: each sentence is spoken separately, its real duration is measured from the decoded WAV, and words share it in proportion to letter count. If drift appears, check that durations come from the WAV (not the MP3 header) and that `voice_rate` has not changed between voice generation and render.

## Reel is over 18 MB

`produce.py` re-encodes at CRF 27 with a 2.8 Mbit/s cap; reels are normally 3 to 5 MB. The asset upload limit is 20 MiB.

## `gcloud services api-keys create` seemed to fail but created a key

The command's output is not clean JSON, so parsing it failed while the key was still created. `create_tts_key.sh` lists keys by display name afterwards instead of parsing the output. Never create a second key blindly: list first.

## The page shows "No reel yet"

`meta/latest` is missing or its `date` has no cards. Write the cards first and `meta/latest` last. See [PAGE.md](PAGE.md).

## The page shows old cards or duplicates

Old cards from earlier decks have a different `date` and are ignored; duplicates for the same story usually mean an old text card was not deleted. Delete old docs with `if_version` pins.

## No sound on iPhone

iOS needs a tap. The start overlay's "Play with sound" button starts the player inside a user gesture. If the video autoplays muted, the "Tap for sound" hint appears; tapping unmutes. Playback itself could not be tested by Claude.

## Share button does nothing

It depends on the `downloads` capability. If it is unavailable in a view, the page copies the headline and link instead. Confirm the artifact was published with `downloads: true`.

## Pexels key page says issuance is paused

True when this was built. Mixkit is the footage source; no key is needed.
