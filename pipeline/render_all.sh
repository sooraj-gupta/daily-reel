#!/bin/bash
# Render every story in stories/ that has no mp4 yet, one at a time.
# If Mixkit is rate-limiting (HTTP 429), it first waits (checks every 4 min, up to 4 hours).
# Usage: ./render_all.sh
cd "$(dirname "$0")"
for n in $(seq 1 60); do
  code=$(curl -s -o /dev/null -m 15 -L -A "Mozilla/5.0" -w "%{http_code}" "https://mixkit.co/free-stock-video/discover/robot/")
  echo "$(date +%H:%M) mixkit status $code"
  [ "$code" = "200" ] && break
  sleep 240
done
[ "$code" = "200" ] || { echo "Mixkit still blocked after waiting"; exit 2; }
for f in stories/*.json; do
  id=$(basename "$f" .json)
  [ -f "out/reels/$id.mp4" ] && continue
  echo "rendering $id"
  python3 produce.py "$f" 2>&1 | tail -2
done
echo "ALL DONE: $(ls out/reels/*.mp4 | wc -l) reels"
