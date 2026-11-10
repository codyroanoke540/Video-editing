#!/usr/bin/env python3
"""Build a vertical 9:16 HyperFrames composition with brand-styled captions
from a Whisper word-timestamp JSON.

Usage: python3 build_captions.py <whisper.json> <out_index.html> [--duration 7] [--offset 0.4]
         [--audio assets/voice.wav] [--cta "Follow for more"]

Brand: Orange #FF5A1F, Navy #0B1F3A, Montserrat (see ../SKILL.md).
"""
import argparse, html, json, re, subprocess

ap = argparse.ArgumentParser()
ap.add_argument("transcript")
ap.add_argument("out")
ap.add_argument("--duration", type=float, default=7.3)
ap.add_argument("--offset", type=float, default=0.3, help="audio start time in the video")
ap.add_argument("--audio", default="assets/voice.wav")
ap.add_argument("--cta", default="Follow for more")
ap.add_argument("--max-words", type=int, default=3)
a = ap.parse_args()

data = json.load(open(a.transcript))
words = []
for seg in data.get("segments", []):
    for w in seg.get("words", []):
        t = w["word"].strip()
        if t and re.search(r"\w", t):
            words.append({"text": t, "start": w["start"] + a.offset, "end": w["end"] + a.offset})

# Group: break at sentence end, a pause >= 150 ms, or the word limit.
groups, cur = [], []
for i, w in enumerate(words):
    cur.append(w)
    nxt = words[i + 1] if i + 1 < len(words) else None
    if (len(cur) >= a.max_words or re.search(r"[.!?,]$", w["text"])
            or nxt is None or nxt["start"] - w["end"] >= 0.15):
        groups.append(cur)
        cur = []

cap_html, cap_js = [], []
for gi, g in enumerate(groups):
    start = max(0.1, g[0]["start"] - 0.05)
    nxt_start = groups[gi + 1][0]["start"] - 0.05 if gi + 1 < len(groups) else None
    end = g[-1]["end"] + 0.15
    if nxt_start is not None:
        end = min(end, nxt_start)
    spans = []
    for wi, w in enumerate(g):
        wid = f"g{gi}w{wi}"
        spans.append(f'<span class="w" id="{wid}">{html.escape(w["text"])}</span>')
        cap_js.append(f'tl.to("#{wid}", {{ color: "#FF5A1F", scale: 1.05, duration: 0.08, ease: "power2.out" }}, {w["start"]:.3f});')
        cap_js.append(f'tl.to("#{wid}", {{ color: "#FFFFFF", scale: 1, duration: 0.08, ease: "power2.in" }}, {max(w["end"], w["start"] + 0.1):.3f});')
    cap_html.append(f'<div class="cap" id="g{gi}"><div class="pill">{" ".join(spans)}</div></div>')
    cap_js.append(f'tl.fromTo("#g{gi}", {{ opacity: 0, y: 24 }}, {{ opacity: 1, y: 0, duration: 0.14, ease: "power3.out" }}, {start:.3f});')
    cap_js.append(f'tl.to("#g{gi}", {{ opacity: 0, duration: 0.1, ease: "power2.in" }}, {end - 0.1:.3f});')
    cap_js.append(f'tl.set("#g{gi}", {{ opacity: 0, visibility: "hidden" }}, {end:.3f});')

speech_end = words[-1]["end"] if words else a.duration - 1.5
cta_start = min(speech_end + 0.15, a.duration - 2.0)
D = a.duration
try:
    audio_len = float(subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",a.audio]).decode())
except Exception:
    audio_len = D - a.offset
audio_len = min(audio_len, D - a.offset)

page = f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1080, height=1920" />
    <script src="assets/gsap.min.js"></script>
    <style>
      :root {{ --orange: #FF5A1F; --navy: #0B1F3A; --ink: #FFFFFF; --font: "Montserrat"; }}
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body {{ width: 1080px; height: 1920px; overflow: hidden; background: var(--navy); }}
      #root {{ position: relative; width: 100%; height: 100%; font-family: var(--font); overflow: hidden; }}
      #bg {{ position: absolute; inset: 0; background: radial-gradient(120% 80% at 50% 30%, #17345E 0%, var(--navy) 65%); }}
      .blob {{ position: absolute; border-radius: 50%; background: var(--orange); opacity: 0.18; }}
      #b1 {{ width: 620px; height: 620px; left: -180px; top: 240px; }}
      #b2 {{ width: 420px; height: 420px; right: -120px; top: 820px; opacity: 0.12; }}
      #badge {{ position: absolute; left: 0; right: 0; top: 220px; text-align: center; }}
      #badge span {{ display: inline-block; padding: 18px 38px; border-radius: 999px; border: 4px solid var(--orange);
                    color: var(--ink); font-weight: 800; font-size: 44px; letter-spacing: 0.08em; }}
      #frame {{ position: absolute; left: 140px; right: 140px; top: 420px; height: 640px; border-radius: 48px;
               background: linear-gradient(160deg, rgba(255,90,31,0.35), rgba(255,255,255,0.04)); border: 3px solid rgba(255,255,255,0.12); }}
      #frame p {{ position: absolute; left: 0; right: 0; top: 270px; text-align: center; color: rgba(255,255,255,0.55);
                 font-weight: 600; font-size: 40px; }}
      .cap {{ position: absolute; left: 0; right: 0; bottom: 640px; text-align: center; overflow: visible; opacity: 0; }}
      .pill {{ display: inline-block; max-width: 900px; padding: 22px 36px; border-radius: 28px; background: rgba(11,31,58,0.88);
              color: var(--ink); font-weight: 800; font-size: 72px; line-height: 1.15; white-space: nowrap; text-transform: uppercase; }}
      .w {{ display: inline-block; margin: 0 0.06em; transform-origin: 50% 60%; }}
      #cta {{ position: absolute; left: 0; right: 0; bottom: 620px; text-align: center; opacity: 0; }}
      #cta span {{ display: inline-block; padding: 28px 56px; border-radius: 999px; background: var(--orange); color: var(--ink);
                  font-weight: 800; font-size: 72px; }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-variables='[{{"id":"brand","type":"string","label":"Brand name","default":"YOUR BRAND"}},{{"id":"cta","type":"string","label":"Call to action","default":"{html.escape(a.cta)}"}}]' data-composition-id="main" data-start="0" data-duration="{D}" data-width="1080" data-height="1920">
      <div id="bgwrap" class="clip" data-start="0" data-duration="{D}" data-track-index="0">
        <div id="bg"></div><div class="blob" id="b1"></div><div class="blob" id="b2"></div>
      </div>
      <div id="badgewrap" class="clip" data-start="0" data-duration="{D}" data-track-index="1">
        <div id="badge"><span data-var-text="brand">YOUR BRAND</span></div>
        <div id="frame"><p>your footage here</p></div>
      </div>
      <div id="captions" class="clip" data-start="0" data-duration="{D}" data-track-index="2" data-track-kind="captions">
        {chr(10).join("        " + c for c in cap_html).strip()}
      </div>
      <div id="ctawrap" class="clip" data-start="{cta_start:.3f}" data-duration="{D - cta_start:.3f}" data-track-index="3">
        <div id="cta"><span data-var-text="cta">{html.escape(a.cta)}</span></div>
      </div>
      <audio id="voice" class="clip" src="{a.audio}" data-start="{a.offset}" data-duration="{audio_len:.3f}" data-track-index="4"></audio>
    </div>
    <script>
      const tl = gsap.timeline({{ paused: true }});
      tl.fromTo("#b1", {{ x: 0, y: 0 }}, {{ x: 120, y: 90, duration: {D}, ease: "sine.inOut" }}, 0);
      tl.fromTo("#b2", {{ x: 0, y: 0 }}, {{ x: -90, y: -140, duration: {D}, ease: "sine.inOut" }}, 0);
      tl.fromTo("#badge", {{ y: -12 }}, {{ y: 0, duration: 0.4, ease: "power3.out" }}, 0);
      tl.fromTo("#frame", {{ scale: 0.97 }}, {{ scale: 1, duration: 0.6, ease: "power3.out" }}, 0);
      {chr(10).join("      " + j for j in cap_js).strip()}
      tl.fromTo("#cta", {{ opacity: 0, scale: 0.8 }}, {{ opacity: 1, scale: 1, duration: 0.3, ease: "back.out(2)" }}, {cta_start:.3f});
      window.__timelines["main"] = tl;
    </script>
  </body>
</html>
"""
open(a.out, "w").write(page)
print(f"{len(words)} words, {len(groups)} caption groups, CTA at {cta_start:.2f}s -> {a.out}")
