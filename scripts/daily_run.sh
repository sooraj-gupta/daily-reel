#!/bin/bash
# Daily build. Starts a real interactive Claude Code session in the background (GNU screen, built into macOS)
# because only interactive sessions have the Artifact upload and database tools. Claude follows
# docs/DAILY-RUN.md, writes .run.done when finished, and this script then closes the session.
# Normally launched by launchd (see install_schedule.sh); you can also run it by hand.
# Usage: scripts/daily_run.sh [--dry-run]     (dry run checks access without touching the live deck)
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
MODE="full"; [ "${1:-}" = "--dry-run" ] && MODE="dry-run"
LOGDIR="$HOME/Library/Logs/daily-reel"; mkdir -p "$LOGDIR"
LOG="$LOGDIR/$(date +%F)-$MODE.log"
exec >>"$LOG" 2>&1
export PATH="$PATH:/opt/homebrew/bin:/usr/local/bin:$HOME/.nvm/versions/node/$(ls "$HOME/.nvm/versions/node" 2>/dev/null | tail -1)/bin"
echo "== $MODE run started $(date)"
LOCK="$ROOT/.run.lock"
if ! mkdir "$LOCK" 2>/dev/null; then echo "another run is in progress ($LOCK exists); exiting"; exit 0; fi
SESSION="dailyreel-$MODE"
cleanup() { screen -S "$SESSION" -X quit 2>/dev/null; rmdir "$LOCK" 2>/dev/null; }
trap cleanup EXIT
fail() { echo "FAILED: $1"; osascript -e "display notification \"$1\" with title \"Daily Reel build failed\"" 2>/dev/null; exit 1; }
command -v claude >/dev/null || fail "claude CLI not found on PATH"
command -v screen >/dev/null || fail "screen not found"
cd "$ROOT" || exit 1
DONE="$ROOT/.run.done"; rm -f "$DONE"
sed -e "s/{{MODE}}/$MODE/g" -e "s/{{DATE}}/$(date +%F)/g" -e "s/{{LABEL}}/$(date '+%a %b %d')/g" -e "s/{{DATE_COMPACT}}/$(date +%Y%m%d)/g" scripts/daily-run-prompt.md > "$ROOT/.run-prompt.txt"
# keep the Mac awake while the job runs (on AC power)
caffeinate -i -s -w $$ &
SCREENLOG="$LOGDIR/$(date +%F)-$MODE-screen.log"
( cd "$LOGDIR" && rm -f screenlog.0 && screen -L -dmS "$SESSION" bash -c "cd '$ROOT' && claude \"\$(cat '$ROOT/.run-prompt.txt')\" --settings scripts/headless-settings.json --permission-mode dontAsk" )
sleep 3
screen -ls | grep -q "$SESSION" || fail "could not start the background Claude session"
echo "session started; waiting for $DONE (limit 2 hours)"
for i in $(seq 1 1440); do
  [ -f "$DONE" ] && break
  screen -ls | grep -q "$SESSION" || { echo "session ended without writing .run.done"; break; }
  sleep 5
done
[ -f "$LOGDIR/screenlog.0" ] && mv "$LOGDIR/screenlog.0" "$SCREENLOG"
if [ -f "$DONE" ]; then
  echo "---- final report ----"; cat "$DONE"; echo "----------------------"
  rm -f "$DONE" "$ROOT/.run-prompt.txt"
  osascript -e "display notification \"$MODE run finished\" with title \"Daily Reel\"" 2>/dev/null
  echo "== $MODE run finished $(date)"; exit 0
fi
rm -f "$ROOT/.run-prompt.txt"
fail "$MODE run did not finish (see $LOG and $SCREENLOG)"
