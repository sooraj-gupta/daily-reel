#!/bin/bash
# Creates (or reuses) a Google Cloud API key restricted to the Text-to-Speech API and saves it to ~/.daily-reels.env.
# Safe to re-run: it looks for an existing key named "daily-reels-tts" before creating one, never prints the key,
# and keeps any other lines already in the env file.
#
# Prerequisites you do yourself (Claude must not do these for you):
#   1. Install the gcloud CLI and sign in:      gcloud auth login
#   2. Have a Google Cloud project with a billing account linked (Text-to-Speech requires billing, even for the free allowance).
#      Create one at https://console.cloud.google.com and link billing at https://console.cloud.google.com/billing
# Usage: scripts/create_tts_key.sh <gcp-project-id>
set -u
P="${1:-}"; [ -n "$P" ] || { echo "usage: $0 <gcp-project-id>"; exit 1; }
ENVF="$HOME/.daily-reels.env"; NAME_TAG="daily-reels-tts"
command -v gcloud >/dev/null || { echo "gcloud not installed: brew install --cask google-cloud-sdk"; exit 1; }
gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q . || { echo "not signed in: run  gcloud auth login"; exit 1; }
gcloud billing projects describe "$P" --format="value(billingEnabled)" 2>/dev/null | grep -q True || { echo "billing is not enabled on $P. Link a billing account in the console, then re-run."; exit 1; }
echo "enabling Text-to-Speech API on $P ..."; gcloud services enable texttospeech.googleapis.com --project="$P" >/dev/null || exit 1
KEYNAME=$(gcloud services api-keys list --project="$P" --filter="displayName=$NAME_TAG" --format="value(name)" | head -1)
if [ -z "$KEYNAME" ]; then
  echo "creating API key restricted to texttospeech.googleapis.com ..."
  gcloud services api-keys create --project="$P" --display-name="$NAME_TAG" --api-target=service=texttospeech.googleapis.com >/dev/null 2>&1
  KEYNAME=$(gcloud services api-keys list --project="$P" --filter="displayName=$NAME_TAG" --format="value(name)" | head -1)
fi
[ -n "$KEYNAME" ] || { echo "could not find or create the key"; exit 1; }
KEY=$(gcloud services api-keys get-key-string "$KEYNAME" --format="value(keyString)" 2>/dev/null)
[ -n "$KEY" ] || { echo "could not read the key string"; exit 1; }
umask 077; touch "$ENVF"; grep -v '^GOOGLE_TTS_API_KEY=' "$ENVF" > "$ENVF.tmp" 2>/dev/null; printf 'GOOGLE_TTS_API_KEY=%s\n' "$KEY" >> "$ENVF.tmp"; mv "$ENVF.tmp" "$ENVF"; chmod 600 "$ENVF"
code=$(curl -s -o /dev/null -w "%{http_code}" "https://texttospeech.googleapis.com/v1/text:synthesize?key=$KEY" -H 'Content-Type: application/json' -d '{"input":{"text":"Test."},"voice":{"languageCode":"en-US","name":"en-US-Chirp3-HD-Charon"},"audioConfig":{"audioEncoding":"MP3"}}')
[ "$code" = "200" ] && echo "OK: key saved to $ENVF and the voice API answered (HTTP 200)." || echo "Key saved, but the test call returned HTTP $code. Check billing and that the API is enabled."
echo "Tip: set a \$5 budget alert at https://console.cloud.google.com/billing/budgets"
