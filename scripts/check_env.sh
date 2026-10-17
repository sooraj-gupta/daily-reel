#!/bin/bash
# Checks everything the reel pipeline needs and prints PASS / FAIL / WARN per item.
# Read-only: installs nothing, prints no secrets (only whether keys exist).
# Usage: scripts/check_env.sh
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
ENVF="$HOME/.daily-reels.env"
fail=0
ok()   { echo "PASS  $1"; }
bad()  { echo "FAIL  $1"; echo "      fix: $2"; fail=1; }
warn() { echo "WARN  $1"; echo "      note: $2"; }

# Node >= 22
if command -v node >/dev/null; then v=$(node -v | sed 's/v//; s/\..*//'); [ "$v" -ge 22 ] && ok "node $(node -v)" || bad "node $(node -v) is older than 22" "install Node 22+ (nvm install 22, or brew install node)"; else bad "node not found" "install Node 22+ (nvm install 22, or brew install node)"; fi
command -v npm >/dev/null && ok "npm present" || bad "npm not found" "comes with Node"
# ffmpeg / ffprobe
command -v ffmpeg >/dev/null && command -v ffprobe >/dev/null && ok "ffmpeg + ffprobe present" || bad "ffmpeg/ffprobe not found" "brew install ffmpeg  (Linux: apt install ffmpeg)"
# python3
if command -v python3 >/dev/null; then python3 -c 'import sys; sys.exit(0 if sys.version_info>=(3,9) else 1)' && ok "python3 $(python3 -V | cut -d' ' -f2)" || bad "python3 older than 3.9" "install Python 3.9+"; else bad "python3 not found" "install Python 3.9+"; fi
# Chrome for rendering (HyperFrames downloads its own)
if [ -d "$ROOT/pipeline/node_modules/hyperframes" ]; then
  ( cd "$ROOT/pipeline" && npx --no-install hyperframes browser path >/dev/null 2>&1 ) && ok "HyperFrames browser ready" || warn "HyperFrames browser not downloaded yet" "run: cd pipeline && npx hyperframes browser ensure"
else warn "HyperFrames not installed yet" "run: cd pipeline && npm install"; fi
# Google TTS key (name only, never the value)
if [ -f "$ENVF" ] && grep -q '^GOOGLE_TTS_API_KEY=.\+' "$ENVF"; then ok "GOOGLE_TTS_API_KEY present in $ENVF"; else bad "GOOGLE_TTS_API_KEY missing in $ENVF" "see docs/COSTS-AND-KEYS.md, or run scripts/create_tts_key.sh <gcp-project-id>"; fi
[ -f "$ENVF" ] && [ "$(stat -f '%Lp' "$ENVF" 2>/dev/null || stat -c '%a' "$ENVF")" != "600" ] && warn "$ENVF is readable by others" "run: chmod 600 $ENVF"
# music
n=$(ls "$ROOT/pipeline/music"/*.mp3 2>/dev/null | wc -l | tr -d ' '); [ "$n" -ge 1 ] && ok "$n music track(s) in pipeline/music" || warn "no music tracks yet" "run: scripts/fetch_music.sh  (produce.py needs at least one track in pipeline/music)"
# disk (>= 8 GB free)
free_kb=$(df -k "$ROOT" | tail -1 | awk '{print $4}'); [ "$free_kb" -gt 8000000 ] && ok "disk free: $((free_kb/1024/1024)) GB" || warn "only $((free_kb/1024/1024)) GB free" "rendering a reel temporarily needs a few GB (HyperFrames frame cache lives in your temp dir); free up ~8 GB"
[ -f "$ROOT/config.json" ] && ok "config.json present" || warn "config.json not created" "cp config/config.example.json config.json and edit it"
echo; [ $fail -eq 0 ] && echo "Environment looks good." || echo "Fix the FAIL items above, then re-run."
exit $fail
