# scripts/

Helper scripts. All are safe to re-run. None prints a secret.

| Script | What it does | Needs |
|---|---|---|
| `check_env.sh` | Read-only check of Node, ffmpeg, Python, HyperFrames browser, the voice key (name only), music, disk, config. Prints PASS/FAIL/WARN and the fix | nothing |
| `create_tts_key.sh <project-id>` | Enables the Text-to-Speech API, finds or creates an API key named `daily-reels-tts` restricted to that API, saves it to `~/.daily-reels.env` (mode 600), tests it | `gcloud` installed and signed in (`gcloud auth login`, done by the user), billing linked to the project |
| `install_schedule.sh [HH:MM]` | Installs the launchd timer (default 07:00) that runs `daily_run.sh` | macOS; see [../docs/SCHEDULING.md](../docs/SCHEDULING.md) |
| `uninstall_schedule.sh` | Removes the timer | macOS |
| `daily_run.sh [--dry-run]` | The unattended job: starts a background interactive Claude session (via `screen`) with the allow-list and prompt below, waits for it to finish, logs to `~/Library/Logs/daily-reel/` | `claude` CLI logged in, repo folder trusted once |
| `daily-run-prompt.md` | Instructions given to the unattended session | read by `daily_run.sh` |
| `headless-settings.json` | Allow-list and deny-list for the unattended session | read by `daily_run.sh` |
| `cleanup.sh` | Deletes generated working files (cache, work, cards_out, dry-run leftovers, HyperFrames temp frames) | nothing |
| `fetch_music.sh` | Downloads six royalty-free beats into `pipeline/music/` | internet |

Run from the repo root, e.g. `scripts/check_env.sh`.
