# Scheduling the daily build

A macOS launchd timer starts the build every morning (07:00 by default) so the deck is ready for the 9:00 notification.

```
launchd (07:00)
   └─ scripts/daily_run.sh
        └─ starts a real interactive Claude Code session in the background (GNU screen)
             ├─ settings: scripts/headless-settings.json   (permission mode dontAsk + allow/deny lists)
             ├─ instructions: scripts/daily-run-prompt.md   (which points at CLAUDE.md and docs/DAILY-RUN.md)
             └─ finishes by writing .run.done  ─►  daily_run.sh reads it, logs it, closes the session, notifies
```

## Why an interactive session in the background (not `claude -p`)

The Artifact upload and database tools exist only in **interactive** sessions. A `claude -p` (print mode) run cannot publish to the feed; we verified this by listing its tools. So the job starts a normal session inside `screen` (built into macOS) and the session ends itself by writing `.run.done`.

## Files

| File | Role |
|---|---|
| `scripts/install_schedule.sh [HH:MM]` | Writes `~/Library/LaunchAgents/com.dailyreel.daily.plist` and loads it. Per-user, no sudo. Default 07:00 |
| `scripts/uninstall_schedule.sh` | Unloads and removes the agent |
| `scripts/daily_run.sh [--dry-run]` | The job: lock, keep awake (`caffeinate`), start the background session, wait up to 2 hours for `.run.done`, log, notify |
| `scripts/daily-run-prompt.md` | The unattended instructions (`{{MODE}}`, `{{DATE}}`, `{{LABEL}}` are filled in) |
| `scripts/headless-settings.json` | Allow-list and deny-list for the session |
| `scripts/cleanup.sh` | Deletes generated working files (the only `rm` the session may run) |

Logs: `~/Library/Logs/daily-reel/<date>-full.log` (and `-dry-run.log`, `...-screen.log` with the session's terminal output), plus `launchd.out` and `launchd.err`.

## One-time prerequisites (the user does these)

1. **Trust the folder.** Run `claude` once in the repo folder and choose "Yes, I trust this folder", then `/exit`. Without this, the background session waits forever at the trust question.
2. **User-scope Robinhood** (only if the portfolio card is wanted): `claude mcp add --scope user --transport http robinhood-trading https://agent.robinhood.com/mcp/trading`, then `/mcp` to sign in. The default "local" scope ties the server to the folder it was added from, so the repo folder would not see it.
3. Gmail and Calendar connectors authorized (`/mcp`), if wanted.

## Install

```bash
scripts/install_schedule.sh 07:00
launchctl print gui/$(id -u)/com.dailyreel.daily | grep -E 'state|hour|minute'
```

Optional (the user runs this; it needs a password and Claude must not): wake the Mac five minutes earlier.

```bash
sudo pmset repeat wakeorpoweron MTWRFSU 06:55:00      # cancel with: sudo pmset repeat cancel
```

## Test before trusting it

```bash
scripts/daily_run.sh --dry-run        # about 2 minutes; does not touch the live deck
cat ~/Library/Logs/daily-reel/$(date +%F)-dry-run.log
```

The dry run checks nine things: config, ratings read, Gmail search, Calendar list, Robinhood portfolio read, an RSS fetch, one full reel render, an asset-storage check (read-only listing), and a database write/read/delete. Expected result: `DRY RUN: 9 of 9 checks passed`.

## What the session may and may not do

Defined in `scripts/headless-settings.json`, mode `dontAsk` (anything not allowed is refused, never prompted).

- **Allowed**: read/write/edit files in the repo, `curl`, `python3`, a few read-only shell commands, `ffprobe`, `scripts/cleanup.sh`, the Artifact and ArtifactData tools, Gmail **search**, Calendar **list events**, Robinhood **accounts, positions, portfolio, quotes**.
- **Denied explicitly**: every Robinhood order, preview, review, cancel and exercise tool; Gmail send, reply, forward, trash and draft tools; Calendar create, update, delete and respond tools.
- `python3` and `curl` are broad. The session is also bound by CLAUDE.md and the prompt, and treats fetched text as data, but this is **not a sandbox**. Use it only on a machine and account you control.

## Limits to know

- **Mac on and logged in.** launchd runs a missed job when the Mac wakes, but not while it is logged out or off. Closing the lid on battery can prevent the wake.
- **Storage.** The artifact allows 1 GiB of assets (about 100 MB per day of 24 reels). **Unattended runs cannot delete assets**: the Artifact delete needs a human confirmation every time. So the job checks usage before uploading (it skips batch 2 above 800 MB and stops uploading above 930 MB, and says so in its report), and deletes old **database cards** (older than 3 days) but not assets. About once a week, open Claude Code and say "prune old reels": Claude lists the assets, deletes those uploaded more than 3 days ago (with your confirmation), and checks usage.
- **No human reviews the deck** before it appears. Scripts and reactions are AI-written from feed text. Skim the feed and the logs now and then.
- **Usage.** A full run uses a meaningful amount of Claude usage (writing about 24 stories) and Google TTS characters.
- **Failure behavior.** `meta/latest` is written last and only after at least 8 reels uploaded, so a failed run leaves the previous deck live. A failure shows a macOS notification and a log.
- **First real run** is the real test. After installing, check the log the next morning.

## Turning it off

```bash
scripts/uninstall_schedule.sh
sudo pmset repeat cancel        # only if you set the wake schedule
```
