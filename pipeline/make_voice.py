import json, os, re, subprocess, sys, base64, urllib.request

env = dict(l.strip().split("=", 1) for l in open(os.path.expanduser("~/.daily-reels.env")) if "=" in l)
KEY = env["GOOGLE_TTS_API_KEY"]
VOICE = sys.argv[2] if len(sys.argv) > 2 else "en-US-Chirp3-HD-Charon"
out = sys.argv[1] if len(sys.argv) > 1 else "assets"
sentences = json.load(open(os.path.join(out, "script.json")))["sentences"]
GAP = 0.18

def synth(text, path):
    body = json.dumps({"input": {"text": text}, "voice": {"languageCode": "en-US", "name": VOICE},
                       "audioConfig": {"audioEncoding": "MP3", "sampleRateHertz": 44100, "speakingRate": float(os.environ.get("RATE", "1.2"))}}).encode()
    req = urllib.request.Request("https://texttospeech.googleapis.com/v1/text:synthesize?key=" + KEY, body, {"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as r:
        open(path, "wb").write(base64.b64decode(json.load(r)["audioContent"]))

def dur(path):
    return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path]).decode())

files, timings, t = [], [], 0.0
for i, s in enumerate(sentences):
    mp = os.path.join(out, f"s{i}.mp3"); synth(s, mp)
    p = os.path.join(out, f"s{i}.wav")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", mp, "-ar", "44100", "-ac", "1", p], check=True)
    d = dur(p); files.append(p)
    words = s.split()
    weights = [len(re.sub(r"\W", "", w)) + 1.5 + (2.5 if w[-1] in ",.;:!?" else 0) for w in words]
    tot = sum(weights); cur = t
    for w, wt in zip(words, weights):
        span = d * wt / tot
        timings.append({"w": w, "start": round(cur, 3), "end": round(cur + span, 3), "s": i}); cur += span
    t += d + GAP
total = t - GAP
lst = os.path.join(out, "concat.txt")
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi", "-i", f"anullsrc=r=44100:cl=mono", "-t", str(GAP), os.path.join(out, "gap.wav")], check=True)
with open(lst, "w") as f:
    for i, p in enumerate(files):
        f.write(f"file '{os.path.abspath(p)}'\n")
        if i < len(files) - 1: f.write(f"file '{os.path.abspath(os.path.join(out, 'gap.wav'))}'\n")
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst, "-ar", "44100", "-ac", "1", os.path.join(out, "voice.wav")], check=True)
json.dump({"duration": round(total, 3), "words": timings}, open(os.path.join(out, "timings.json"), "w"))
print("voice", VOICE, "duration", round(total, 2), "words", len(timings))
