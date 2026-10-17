"""Produce one reel from a story file.   python3 produce.py stories/<id>.json
Writes out/reels/<id>.mp4, <id>.jpg and out/reels/<id>.json (metadata + comments)."""
import json, os, re, subprocess, sys, hashlib, time, urllib.request, urllib.error, shutil

ROOT = os.path.dirname(os.path.abspath(__file__))
for _d in ("cache", "work", os.path.join("out", "reels")): os.makedirs(os.path.join(ROOT, _d), exist_ok=True)
HUES = {"ai": "#b79cff", "tech": "#5ee0ff", "bayarea": "#ff9a4d", "world": "#f2e86b", "markets": "#6dff9c", "spark": "#ffd0a8"}
CHIPS = {"ai": "AI", "tech": "TECH", "bayarea": "BAY AREA", "world": "WORLD", "markets": "MARKETS", "spark": "CURIOUS"}
UA = {"User-Agent": "Mozilla/5.0"}
MUSIC = ["235", "257", "262", "267", "293", "303"]
FALLBACK_KW = ["city", "technology", "business", "night", "abstract"]
story = json.load(open(sys.argv[1])); sid = story["id"]
CFG_PATH = os.path.join(ROOT, "..", "config.json")
CFG = json.load(open(CFG_PATH)) if os.path.exists(CFG_PATH) else {}   # optional; copy config/config.example.json to config.json
W = os.path.join(ROOT, "work", sid); A = os.path.join(W, "assets")
os.makedirs(A, exist_ok=True)
H = lambda s: int(hashlib.md5(s.encode()).hexdigest(), 16)

import fcntl
def throttle():
    lf = open(os.path.join(ROOT, "cache", ".mixkit.lock"), "a+")
    fcntl.flock(lf, fcntl.LOCK_EX)
    try:
        st = os.path.join(ROOT, "cache", ".mixkit.last")
        last = float(open(st).read()) if os.path.exists(st) else 0
        wait = 3.0 - (time.time() - last)
        if wait > 0: time.sleep(wait)
        open(st, "w").write(str(time.time()))
    finally:
        fcntl.flock(lf, fcntl.LOCK_UN); lf.close()

def get_page(url):
    for attempt in range(5):
        throttle()
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=40) as r: return r.read().decode("utf8", "ignore")
        except urllib.error.HTTPError as e:
            if e.code == 429: time.sleep(25 * (attempt + 1)); continue
            return ""
        except Exception: time.sleep(3)
    return ""

def get(url, binary=False):
    for _ in range(3):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=40) as r:
                d = r.read(); return d if binary else d.decode("utf8", "ignore")
        except Exception: time.sleep(1.5)
    return b"" if binary else ""

def candidates(kw):
    f = os.path.join(ROOT, "cache", f"search_{kw}.txt")
    if os.path.exists(f) and os.path.getsize(f) > 0 and time.time() - os.path.getmtime(f) < 86400: return open(f).read().split()
    page = get_page(f"https://mixkit.co/free-stock-video/discover/{kw}/")
    ids = []
    for i in re.findall(r"https://assets\.mixkit\.co/videos/(\d+)/\d+-\d+\.mp4", page):
        if i not in ids: ids.append(i)
    if ids: open(f, "w").write(" ".join(ids))
    return ids

def fetch_clip(i):
    p = os.path.join(ROOT, "cache", f"clip{i}.mp4")
    if not os.path.exists(p) or os.path.getsize(p) < 50000:
        for q in ("720", "1080", "360"):
            d = get(f"https://assets.mixkit.co/videos/{i}/{i}-{q}.mp4", binary=True)
            if d and len(d) > 50000 and d[4:8] == b"ftyp": open(p, "wb").write(d); break
        else: return None
    try:
        dur = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", p]).decode())
    except Exception: return None
    return p if dur >= 6 else None

sentences = story["sentences"]
json.dump({"sentences": sentences}, open(os.path.join(A, "script.json"), "w"))
env = dict(os.environ, RATE=str(story.get("rate", CFG.get("voice_rate", 1.2))))
subprocess.run([sys.executable, os.path.join(ROOT, "make_voice.py"), A, story.get("voice", CFG.get("voice", "en-US-Chirp3-HD-Charon"))], check=True, env=env, stdout=subprocess.DEVNULL)

kws = story.get("keywords") or [story["topic"]]
used, clips = set(), []
for si in range(len(sentences)):
    order = [kws[(si + k) % len(kws)] for k in range(len(kws))] + FALLBACK_KW
    chosen = None
    for kw in order:
        ids = [i for i in candidates(kw) if i not in used]
        ids.sort(key=lambda i: H(sid + str(si) + i))
        for i in ids[:6]:
            p = fetch_clip(i)
            if p: chosen = (i, p); break
        if chosen: break
    if not chosen: raise SystemExit("no footage found for sentence %d" % si)
    used.add(chosen[0]); name = f"clip{chosen[0]}.mp4"
    link = os.path.join(A, name)
    if not os.path.exists(link): os.symlink(chosen[1], link)
    clips.append(name)
mus = MUSIC[H(sid) % len(MUSIC)]
ml = os.path.join(A, "music.mp3")
if not os.path.exists(ml): os.symlink(os.path.join(ROOT, "music", mus + ".mp3"), ml)

topic = story["topic"]
spec = {"assets": A, "chip": story.get("chip", CHIPS.get(topic, topic.upper())), "hue": HUES.get(topic, "#ffffff"), "date": story.get("date") or time.strftime("%a %b %d"),
        "headline": story["headline"], "clips": clips, "media_start": 1.2, "bars": story.get("bars", []), "music": "music.mp3", "music_volume": story.get("music_volume", CFG.get("music_volume", 0.16))}
json.dump(spec, open(os.path.join(W, "spec.json"), "w"))
R = os.path.join(W, "reel")
subprocess.run([sys.executable, os.path.join(ROOT, "build_reel.py"), os.path.join(W, "spec.json"), R], check=True, stdout=subprocess.DEVNULL)
mp4 = os.path.join(ROOT, "out", "reels", sid + ".mp4")
subprocess.run(["npx", "hyperframes", "render", ".", "-o", mp4, "-q", "standard", "-f", "30", "-w", "2"], cwd=R, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
tmp = mp4 + ".tmp.mp4"
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", mp4, "-c:v", "libx264", "-crf", "27", "-preset", "medium", "-maxrate", "2800k", "-bufsize", "5600k", "-pix_fmt", "yuv420p", "-c:a", "copy", "-movflags", "+faststart", tmp], check=True)
os.replace(tmp, mp4)
jpg = os.path.join(ROOT, "out", "reels", sid + ".jpg")
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", "2.5", "-i", mp4, "-frames:v", "1", "-vf", "scale=540:-1", "-q:v", "4", jpg], check=True)
dur = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", mp4]).decode())
meta = {k: story.get(k) for k in ("id", "topic", "kicker", "source", "url", "comments", "headline_text", "why")}
meta.update({"headline_text": story.get("headline_text") or " ".join(h.lstrip("*") for h in story["headline"]), "mp4": mp4, "poster": jpg, "duration": round(dur, 1), "mb": round(os.path.getsize(mp4) / 1e6, 1)})
json.dump(meta, open(os.path.join(ROOT, "out", "reels", sid + ".json"), "w"), indent=1)
shutil.rmtree(R, ignore_errors=True)
import tempfile
shutil.rmtree(os.path.join(tempfile.gettempdir(), "hyperframes-extract-cache-%d" % os.getuid()), ignore_errors=True)
print(json.dumps({"id": sid, "mp4": mp4, "duration": meta["duration"], "mb": meta["mb"]}))
