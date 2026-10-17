#!/bin/bash
# Downloads six royalty-free hip-hop beats from Mixkit into pipeline/music/ (not stored in this repo).
# Mixkit's license allows use in videos without attribution but not redistributing the tracks on their own,
# which is why they are fetched on your machine instead of committed. See docs/LICENSES.md.
# Usage: scripts/fetch_music.sh
DEST="$(cd "$(dirname "$0")/.." && pwd)/pipeline/music"; mkdir -p "$DEST"
for id in 235 257 262 267 293 303; do
  f="$DEST/$id.mp3"; [ -s "$f" ] && { echo "have $id"; continue; }
  curl -s -L -m 60 -A "Mozilla/5.0" -o "$f" "https://assets.mixkit.co/music/$id/$id.mp3"
  if [ "$(head -c 3 "$f")" = "ID3" ] || [ "$(head -c 2 "$f" | xxd -p)" = "fffb" ]; then echo "ok   $id ($(du -h "$f" | cut -f1))"; else echo "FAIL $id (not an mp3; Mixkit may be rate-limiting, retry later)"; rm -f "$f"; fi
  sleep 3
done
ls "$DEST"/*.mp3 2>/dev/null | wc -l | xargs echo "tracks available:"
