#!/bin/bash
# Deletes generated working files after a build. Safe: only touches known generated paths inside this repo.
# Usage: scripts/cleanup.sh
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
rm -rf "$ROOT/pipeline/cache" "$ROOT/pipeline/work" "$ROOT/pipeline/cards_out"
rm -f "$ROOT/pipeline/stories/dryrun-test.json" "$ROOT/pipeline/out/reels/dryrun-test."*
rm -rf "${TMPDIR:-/tmp}/hyperframes-extract-cache-$(id -u)"
echo "cleaned generated files"
