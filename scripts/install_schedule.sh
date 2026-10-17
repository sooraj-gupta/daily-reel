#!/bin/bash
# Installs (or updates) a launchd agent that runs scripts/daily_run.sh every day at the given time (default 07:00).
# It is a per-user LaunchAgent: no sudo. If the Mac is asleep at that time, launchd runs it when the Mac wakes.
# Usage: scripts/install_schedule.sh [HH:MM]
set -e
ROOT="$(cd "$(dirname "$0")/.." && pwd)"; T="${1:-07:00}"; H=$((10#${T%%:*})); M=$((10#${T##*:}))
LABEL="com.dailyreel.daily"; PLIST="$HOME/Library/LaunchAgents/$LABEL.plist"; LOGDIR="$HOME/Library/Logs/daily-reel"
mkdir -p "$HOME/Library/LaunchAgents" "$LOGDIR"; chmod +x "$ROOT/scripts/daily_run.sh"
cat > "$PLIST" <<PL
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
  <key>Label</key><string>$LABEL</string>
  <key>ProgramArguments</key><array><string>/bin/bash</string><string>$ROOT/scripts/daily_run.sh</string></array>
  <key>WorkingDirectory</key><string>$ROOT</string>
  <key>StartCalendarInterval</key><dict><key>Hour</key><integer>$H</integer><key>Minute</key><integer>$M</integer></dict>
  <key>EnvironmentVariables</key><dict><key>PATH</key><string>$PATH:/opt/homebrew/bin:/usr/local/bin</string><key>HOME</key><string>$HOME</string></dict>
  <key>StandardOutPath</key><string>$LOGDIR/launchd.out</string>
  <key>StandardErrorPath</key><string>$LOGDIR/launchd.err</string>
</dict></plist>
PL
launchctl bootout "gui/$(id -u)/$LABEL" 2>/dev/null || true
launchctl bootstrap "gui/$(id -u)" "$PLIST"
echo "Installed: runs daily at $(printf '%02d:%02d' $H $M). Logs: $LOGDIR"
echo "Check:     launchctl print gui/$(id -u)/$LABEL | grep -E 'state|hour|minute'"
W=$((H*60+M-5)); [ $W -lt 0 ] && W=0
echo
echo "To wake a sleeping Mac a few minutes earlier (needs your password; run it yourself):"
echo "  sudo pmset repeat wakeorpoweron MTWRFSU $(printf '%02d:%02d:00' $((W/60)) $((W%60)))"
