# scripts/

Helper scripts. All are safe to re-run. None prints a secret.

| Script | What it does | Needs |
|---|---|---|
| `check_env.sh` | Read-only check of Node, ffmpeg, Python, HyperFrames browser, the voice key (name only), music, disk, config. Prints PASS/FAIL/WARN and the fix | nothing |
| `create_tts_key.sh <project-id>` | Enables the Text-to-Speech API, finds or creates an API key named `daily-reels-tts` restricted to that API, saves it to `~/.daily-reels.env` (mode 600), tests it | `gcloud` installed and signed in (`gcloud auth login`, done by the user), billing linked to the project |
| `fetch_music.sh` | Downloads six royalty-free beats into `pipeline/music/` | internet |

Run from the repo root, e.g. `scripts/check_env.sh`.
