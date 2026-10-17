"""Build a HyperFrames reel project from a spec: python3 build_reel.py spec.json outdir"""
import json, os, re, sys, html, shutil

spec = json.load(open(sys.argv[1])); out = sys.argv[2]
assets = os.path.abspath(spec["assets"])
T = json.load(open(os.path.join(assets, "timings.json")))
words, total = T["words"], T["duration"]
END = round(total + 0.7, 2)
HUE = spec.get("hue", "#6dff9c"); CHIP = spec.get("chip", "MARKETS"); DATE = spec.get("date", "")
esc = lambda s: html.escape(s, quote=True)
clean = lambda w: re.sub(r"[^\w%&]", "", w).lower()

os.makedirs(out, exist_ok=True)
for f in ("hyperframes.json", "meta.json", "package.json"):
    src = os.path.join(os.path.dirname(os.path.abspath(__file__)), "template", f)
    if os.path.exists(src): shutil.copy(src, os.path.join(out, f))
link = os.path.join(out, "assets")
if not os.path.exists(link): os.symlink(assets, link)

# sentence starts -> clip cuts
sent_start = {}
for w in words: sent_start.setdefault(w["s"], w["start"])
starts = [sent_start[k] for k in sorted(sent_start)]
clips = spec["clips"]; n = len(starts)
cuts = []
for i in range(n):
    s = starts[i]; e = starts[i + 1] if i + 1 < n else END
    cuts.append((0.0 if i == 0 else s, e))

# caption chunks (<=3 words, inside a sentence)
chunks, cur = [], []
for idx, w in enumerate(words):
    if cur and (w["s"] != words[cur[0]]["s"] or len(cur) >= 3 or len(" ".join(words[x]["w"].strip(",.") for x in cur + [idx])) > 16): chunks.append(cur); cur = []
    cur.append(idx)
if cur: chunks.append(cur)
merged = []
for c in chunks:
    if len(c) == 1 and merged and words[merged[-1][0]]["s"] == words[c[0]]["s"] and len(" ".join(words[x]["w"].strip(",.") for x in merged[-1] + c)) <= 16: merged[-1].append(c[0])
    else: merged.append(c)
chunks = merged

# stat bars, shown when their keyword is spoken
bars = []
for b in spec.get("bars", []):
    hit = next((w for w in words if b["kw"].lower() in clean(w["w"])), None)
    if hit: bars.append((hit["start"], b))
bars.sort(key=lambda x: x[0])

h = []
A = h.append
A(f'''<!doctype html>
<html lang="en" data-resolution="portrait">
<head>
<meta charset="UTF-8" /><meta name="viewport" content="width=1080, height=1920" />
<script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
html,body{{margin:0;width:1080px;height:1920px;overflow:hidden;background:#0a0b0f}}
:root{{--hue:{HUE}}}
#root{{position:relative;width:1080px;height:1920px;overflow:hidden;font-family:Helvetica,Arial,sans-serif;color:#fff;background:#0a0b0f}}
.bgv{{position:absolute;left:-120px;top:-120px;width:1320px;height:2160px;object-fit:cover;filter:blur(36px) brightness(.42) saturate(1.3)}}
.vid{{position:absolute;left:0;top:500px;width:1080px;height:780px;object-fit:cover}}
.vwrap{{position:absolute;left:0;top:500px;width:1080px;height:780px;overflow:hidden}}
.shade-t{{position:absolute;left:0;top:0;width:1080px;height:760px;background:linear-gradient(to bottom,rgba(8,9,12,.92),rgba(8,9,12,0))}}
.shade-b{{position:absolute;left:0;top:1180px;width:1080px;height:740px;background:linear-gradient(to top,rgba(8,9,12,.95),rgba(8,9,12,0))}}
.chip{{position:absolute;left:60px;top:104px;display:flex;align-items:center;gap:14px;padding:14px 26px;border-radius:999px;background:var(--hue);color:#06120a;font:900 40px/1 "Big Shoulders Display",Impact,"Arial Narrow",sans-serif;letter-spacing:.08em;text-transform:uppercase}}
.chip i{{width:16px;height:16px;border-radius:50%;background:#06120a}}
.date{{position:absolute;right:60px;top:118px;font:700 28px/1 Helvetica,Arial,sans-serif;letter-spacing:.14em;text-transform:uppercase;color:rgba(255,255,255,.7)}}
.hl{{position:absolute;left:60px;top:196px;width:960px;font:900 148px/.9 "Big Shoulders Display",Impact,"Arial Narrow",sans-serif;text-transform:uppercase;letter-spacing:.005em;text-shadow:0 6px 40px rgba(0,0,0,.6)}}
.hl div{{overflow:hidden}} .hl span{{display:block}} .hl .hue{{color:var(--hue)}}
.bar{{position:absolute;left:60px;width:960px;height:46px;display:flex;align-items:center;gap:22px}}
.bar .lb{{width:150px;font:900 46px/1 "Big Shoulders Display",Impact,"Arial Narrow",sans-serif;letter-spacing:.04em}}
.bar .tr{{position:relative;width:600px;height:26px;border-radius:13px;background:rgba(255,255,255,.14);overflow:hidden}}
.bar .fl{{position:absolute;left:0;top:0;height:26px;width:0;border-radius:13px;background:#ff5d5d}}
.bar .vl{{width:150px;text-align:right;font:900 46px/1 "Big Shoulders Display",Impact,"Arial Narrow",sans-serif;color:#ff7b7b}}
.chunk{{position:absolute;left:60px;top:1580px;width:960px;height:220px;display:flex;flex-wrap:wrap;justify-content:center;align-content:center;gap:0 26px;text-align:center}}
.w{{position:relative;display:inline-block;font:900 136px/1.0 "Big Shoulders Display",Impact,"Arial Narrow",sans-serif;text-transform:uppercase;letter-spacing:.01em;text-shadow:0 6px 30px rgba(0,0,0,.7)}}
.w .b{{color:#fff}} .w .h{{position:absolute;left:0;top:0;color:var(--hue);opacity:0}}
.prog{{position:absolute;left:0;top:1880px;height:10px;width:0;background:var(--hue)}}
</style></head><body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{END}" data-width="1080" data-height="1920">
''')
for i, ((s, e), clip) in enumerate(zip(cuts, clips)):
    d = round(e - s + (0.14 if i + 1 < n else 0), 3)
    off = spec.get("media_start", 1.0)
    A(f'<video id="bg{i}" class="clip bgv" src="assets/{clip}" muted playsinline data-start="{s:.3f}" data-duration="{d}" data-media-start="{off+0.04:.2f}" data-track-index="0"></video>')
A('<div class="shade-t"></div><div class="shade-b"></div>')
for i, ((s, e), clip) in enumerate(zip(cuts, clips)):
    d = round(e - s + (0.14 if i + 1 < n else 0), 3)
    off = spec.get("media_start", 1.0)
    A(f'<video id="v{i}" class="clip vid" src="assets/{clip}" muted playsinline data-start="{s:.3f}" data-duration="{d}" data-media-start="{off}" data-track-index="2"></video>')
A(f'<div class="chip clip" id="chip" data-start="0" data-duration="{END}" data-track-index="3"><i></i>{esc(CHIP)}</div>')
A(f'<div class="date clip" id="date" data-start="0" data-duration="{END}" data-track-index="3">{esc(DATE)}</div>')
A(f'<div class="hl clip" id="hl" data-start="0" data-duration="{END}" data-track-index="3">')
for j, line in enumerate(spec["headline"]):
    cls = ' class="hue"' if line.startswith("*") else ""
    A(f'<div><span id="hl{j}"{cls}>{esc(line.lstrip("*"))}</span></div>')
A('</div>')
for k, (t, b) in enumerate(bars):
    top = 1296 + k * 54
    wpx = round(600 * abs(b["pct"]) / spec.get("bar_max", 22))
    A(f'<div class="bar clip" id="bar{k}" style="top:{top}px" data-start="{max(0,t-0.05):.3f}" data-duration="{round(END - t + 0.05, 3)}" data-track-index="4"><div class="lb">{esc(b["label"])}</div><div class="tr"><div class="fl" id="fl{k}"></div></div><div class="vl" id="vl{k}">{esc(b["text"])}</div></div>')
for c_i, c in enumerate(chunks):
    s = max(0, words[c[0]]["start"] - 0.03)
    e = words[chunks[c_i + 1][0]]["start"] - 0.03 if c_i + 1 < len(chunks) else words[c[-1]]["end"] + 0.5
    A(f'<div class="chunk clip" id="ch{c_i}" data-start="{s:.3f}" data-duration="{round(e - s, 3)}" data-track-index="5">')
    for wi in c:
        t = esc(words[wi]["w"].strip(",."))
        A(f'<span class="w" id="w{wi}"><span class="b">{t}</span><span class="h" id="h{wi}">{t}</span></span>')
    A('</div>')
A(f'<div class="prog clip" id="prog" data-start="0" data-duration="{END}" data-track-index="6"></div>')
A(f'<audio id="voice" src="assets/voice.wav" data-start="0" data-duration="{total}" data-track-index="7"></audio>')
if spec.get("music"):
    A(f'<audio id="music" src="assets/{spec["music"]}" data-start="0" data-duration="{END}" data-volume="{spec.get("music_volume", 0.09)}" data-fade-out="1.2" data-track-index="8"></audio>')
A('</div><script>\nwindow.__timelines = window.__timelines || {};\nconst tl = gsap.timeline({ paused: true });')
for i, (s, e) in enumerate(cuts):
    d = e - s + 0.14
    A(f'tl.fromTo("#v{i}",{{opacity:0,scale:1.0}},{{opacity:1,scale:1.06,duration:{d:.3f},ease:"none"}},{s:.3f});')
    A(f'tl.fromTo("#bg{i}",{{scale:1.0}},{{scale:1.12,duration:{d:.3f},ease:"none"}},{s:.3f});')
A('tl.fromTo("#chip",{x:-300,opacity:0},{x:0,opacity:1,duration:.4,ease:"power3.out"},0.05);')
A('tl.fromTo("#date",{opacity:0},{opacity:1,duration:.4},0.25);')
for j in range(len(spec["headline"])):
    A(f'tl.fromTo("#hl{j}",{{y:170}},{{y:0,duration:.5,ease:"power4.out"}},{0.1 + j*0.12:.2f});')
for k, (t, b) in enumerate(bars):
    wpx = round(600 * abs(b["pct"]) / spec.get("bar_max", 22))
    A(f'tl.fromTo("#bar{k}",{{x:-120,opacity:0}},{{x:0,opacity:1,duration:.3,ease:"power3.out"}},{max(0,t-0.05):.3f});')
    A(f'tl.to("#fl{k}",{{width:{wpx},duration:.55,ease:"power3.out"}},{t:.3f});')
for c_i, c in enumerate(chunks):
    s = max(0, words[c[0]]["start"] - 0.03)
    A(f'tl.fromTo("#ch{c_i}",{{y:26,opacity:0}},{{y:0,opacity:1,duration:.1,ease:"power2.out"}},{s:.3f});')
    for wi in c:
        w = words[wi]
        A(f'tl.set("#h{wi}",{{opacity:1}},{w["start"]:.3f});tl.set("#h{wi}",{{opacity:0}},{w["end"]:.3f});')
        A(f'tl.fromTo("#w{wi}",{{scale:1}},{{scale:1.12,duration:.07}},{w["start"]:.3f});tl.to("#w{wi}",{{scale:1,duration:.12}},{w["start"]+0.07:.3f});')
A(f'tl.fromTo("#prog",{{width:0}},{{width:1080,duration:{END},ease:"none"}},0);')
A('window.__timelines["main"] = tl;\ntl.seek(0);\n</script></body></html>')
open(os.path.join(out, "index.html"), "w").write("\n".join(h))
print("built", out, "| cuts", n, "| chunks", len(chunks), "| bars", len(bars), "| dur", END)
