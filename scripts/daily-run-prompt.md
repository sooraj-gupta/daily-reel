You are running UNATTENDED as the scheduled daily build of Daily Reel. Nobody can answer questions or approve prompts. Never ask for approval. If a step needs a person, skip it and say so in your final report.

Mode: {{MODE}}
Today: {{DATE}} ({{LABEL}}). Time zone and settings are in config.json.

First read CLAUDE.md. Its hard rules apply in full (no trading, no secrets in output, no personal data beyond what docs/PRIVACY-AND-SAFETY.md allows, facts only, AI-labeled reactions, never hammer Mixkit). Then read docs/DAILY-RUN.md and follow it, with these unattended overrides.

## Overrides for unattended runs

- Work in the repository root. Render stories ONE AT A TIME; do not start parallel renders or subagents that render.
- Tools are restricted by an allow-list. If a tool call is denied, do not try to work around it; skip that part and report it.
- Never print balances, share counts, cost basis, email bodies or API keys. Print counts and status only.
- Do not create or change calendar events; the 9:00 alert already exists.
- Deadline: finish by 08:45 local time. If it is past 08:20, do not start any new render; publish what is finished (batch 1 first).
- If Mixkit is rate-limiting, do not probe it repeatedly. Run ./render_all.sh once from pipeline/, which waits and throttles itself.
- Never print message subjects, senders, balances or event titles in your visible output; counts and "ok" only. (Inbox and calendar card text goes only into the database documents.)
- Clean up with `scripts/cleanup.sh` (not `rm`).
- FINISH BY WRITING THE FILE `.run.done` in the repository root (use the Write tool) containing your final report. This is the very last thing you do, whether the run succeeded or failed. The scheduler waits for this file and then closes this session.

## If mode is "full"

1. Follow docs/DAILY-RUN.md steps 1 to 7: inputs, ratings-based story choice, story files, sequential renders, QA, upload, cards, text cards, `meta/state` reset to `{"revealed": 1}`, then `meta/latest` LAST.
2. Build `reels_per_batch` reels in batch 1 and the same number in batch 2 (batch 2 may be smaller if time runs short). Use today's ISO date for `date` and `--date`.
3. Only write `meta/latest` if at least 8 reels rendered and uploaded successfully. Otherwise leave yesterday's deck in place and say why.
4. Storage guard and pruning. Unattended runs cannot delete assets (the Artifact tool needs a human to confirm every delete), and the artifact allows 1 GiB. Before uploading, list the assets (Artifact tool, action `list`, scope `assets`) and read the usage line. If usage is above 800 MB, do NOT upload batch 2. If usage is above 930 MB, upload nothing, keep yesterday's deck, and say so in the report. After a successful deck, delete `cards` documents (database only) whose `date` is more than 3 days old. Never delete assets; the user prunes old assets in an interactive session.
5. Clean up: run `scripts/cleanup.sh`.
6. Write `.run.done` with a short report with counts (stories chosen, rendered, uploaded), anything skipped or denied, and the time finished. No secrets, no personal figures.

## If mode is "dry-run"

Do NOT touch the live deck (`meta/*`, existing `cards/*`). Run these checks and print PASS or FAIL for each, then stop:

1. config.json is readable (print only the keys present).
2. Read the `ratings` and `signals` collections (print counts only).
3. Call the Gmail search tool once (`is:unread in:inbox newer_than:2d`, page size 3); print the count only.
4. Call the Calendar list-events tool once for today; print the count only.
5. Call the Robinhood portfolio tool for the individual account once; print only "ok".
6. Fetch one RSS feed with curl (https://feeds.npr.org/1001/rss.xml); print the first item title.
7. Write pipeline/stories/dryrun-test.json (copy pipeline/stories/example-world.json, set id to "dryrun-test"), run `cd pipeline && python3 produce.py stories/dryrun-test.json`, and print the MP4 duration with ffprobe.
8. List the artifact's assets (Artifact tool, action `list`, scope `assets`) and print only the usage line (bytes used and the limit). Do not upload or delete anything in this check.
9. Write a document `requests/dryrun-probe` with `{"probe": true}` using the database tool, read it back, then delete it.
10. Clean up: run `scripts/cleanup.sh` (it removes the dry-run test files).
11. Write `.run.done` containing one line `DRY RUN: <n> of 9 checks passed` and a list of any failures.
