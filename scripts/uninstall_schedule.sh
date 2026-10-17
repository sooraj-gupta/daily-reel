#!/bin/bash
# Removes the daily launchd agent. Does not touch logs or the repo.
LABEL="com.dailyreel.daily"; PLIST="$HOME/Library/LaunchAgents/$LABEL.plist"
launchctl bootout "gui/$(id -u)/$LABEL" 2>/dev/null; rm -f "$PLIST"; echo "Removed $LABEL."
echo "If you set a wake schedule: sudo pmset repeat cancel   (run it yourself)"
