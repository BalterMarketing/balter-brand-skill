#!/usr/bin/env python3
"""
Brand subtitles from word timings: one cue per phrase, at most 2 lines of 32 characters, cleaned with the
caption glossary, written as SRT (for the Resolve subtitle track) and, if asked, burned in with the brand
caption box (black 72 %, radius 16 at 1080 px, Inter 700 48 px white, centred above the bottom safe zone).

Input: a JSON list of words [{"word": "...", "start": 0.0, "end": 0.4}, ...] as WhisperX, ElevenLabs Scribe
or a Resolve transcript export give it (a {"words": [...]} or {"segments": [{"words": [...]}]} wrapper is fine).

    python3 scripts/captions.py words.json out.srt
    python3 scripts/captions.py words.json out.srt --burn in.mp4 out.mp4 --font /path/Inter-Bold.ttf --format master-9x16

Always proof-read the SRT before burning in: numbers and product names are where recognition fails.
"""
import json
import os
import re
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
GLOSS = os.path.join(HERE, "..", "assets", "social", "caption-glossary.json")
MAXC, MAXL, MIN_CUE, GAP = 32, 2, 0.8, 0.6


def load_words(p):
    d = json.load(open(p, encoding="utf-8"))
    if isinstance(d, dict):
        d = d.get("words") or [w for s in d.get("segments", []) for w in s.get("words", [])]
    return [dict(word=str(w.get("word") or w.get("text")).strip(), start=float(w["start"]), end=float(w["end"]))
            for w in d if (w.get("word") or w.get("text")) and "start" in w and "end" in w]


def clean(text):
    rules = json.load(open(GLOSS, encoding="utf-8"))["replace"]
    for k, v in rules.items():
        text = re.sub(k, v, text, flags=re.I)
    return re.sub(r"\s+", " ", text).strip()


FIT = None   # set to a function(text) -> bool when a font and a width are known (pixel-exact wrapping)


def lines_of(words):
    out, cur = [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if (FIT(t) if FIT else len(t) <= MAXC):
            cur = t
        else:
            out.append(cur)
            cur = w
    if cur:
        out.append(cur)
    return out


def cues(words):
    res, buf = [], []
    for i, w in enumerate(words):
        buf.append(w)
        text = clean(" ".join(x["word"] for x in buf))
        nxt = words[i + 1] if i + 1 < len(words) else None
        pause = nxt is None or nxt["start"] - w["end"] > GAP
        sentence = re.search(r"[.!?…:]$", w["word"])
        full = nxt is not None and len(lines_of((text + " " + clean(nxt["word"])).split())) > MAXL
        if pause or sentence or full:
            res.append(dict(start=buf[0]["start"], end=max(w["end"], buf[0]["start"] + MIN_CUE), lines=lines_of(text.split())))
            buf = []
    for a, b in zip(res, res[1:]):          # no overlaps
        a["end"] = min(a["end"], b["start"] - 0.02)
    return res


def ts(t):
    h, r = divmod(t, 3600)
    m, s = divmod(r, 60)
    return f"{int(h):02}:{int(m):02}:{s:06.3f}".replace(".", ",")


def write_srt(cs, p):
    with open(p, "w", encoding="utf-8") as f:
        for i, c in enumerate(cs, 1):
            f.write(f"{i}\n{ts(c['start'])} --> {ts(c['end'])}\n" + "\n".join(c["lines"]) + "\n\n")


def burn(cs, src, dst, font, fmt):
    from PIL import Image, ImageDraw, ImageFont
    sys.path.insert(0, HERE)
    import safe_zones as SZ
    f = SZ.formats()[fmt]
    k = f["w"] / 1080
    size, pad_x, pad_y, rad, lh = int(48 * k), int(28 * k), int(16 * k), int(16 * k), int(60 * k)
    fnt = ImageFont.truetype(font, size)
    td = tempfile.mkdtemp()
    inputs, chain, last = [], [], "[0:v]"
    for i, c in enumerate(cs):
        tw = max(fnt.getlength(l) for l in c["lines"])
        W, H = int(tw + 2 * pad_x), int(lh * len(c["lines"]) + 2 * pad_y)
        im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        d.rounded_rectangle((0, 0, W - 1, H - 1), rad, fill=(0, 0, 0, 184))
        for j, l in enumerate(c["lines"]):
            d.text((W / 2, pad_y + lh * j + lh / 2), l, font=fnt, fill="white", anchor="mm")
        p = os.path.join(td, f"c{i:04}.png")
        im.save(p)
        inputs += ["-i", p]
        x = f"{f['left']}+({f['w'] - f['left'] - f['right']}-w)/2"
        y = f"H-{f['bottom'] + int(24 * k)}-h"
        out = f"[v{i}]"
        chain.append(f"{last}[{i + 1}:v]overlay={x}:{y}:enable='between(t,{c['start']:.3f},{c['end']:.3f})'{out}")
        last = out
    graph = ";".join(chain)
    cmd = ["ffmpeg", "-y", "-i", src, *inputs, "-filter_complex", graph, "-map", last, "-map", "0:a?",
           "-c:v", "libx264", "-crf", "18", "-preset", "medium", "-c:a", "copy", dst]
    subprocess.run(cmd, check=True)


def set_fit(font, fmt):
    """Wrap by real width: a line may be as wide as the usable area minus the box padding."""
    global FIT
    from PIL import ImageFont
    sys.path.insert(0, HERE)
    import safe_zones as SZ
    f = SZ.formats()[fmt]
    k = f["w"] / 1080
    fnt = ImageFont.truetype(font, int(48 * k))
    room = f["w"] - f["left"] - f["right"] - 2 * int(28 * k)
    FIT = lambda t: len(t) <= MAXC and fnt.getlength(t) <= room  # noqa: E731


if __name__ == "__main__":
    a = sys.argv[1:]
    font = a[a.index("--font") + 1] if "--font" in a else os.path.expanduser("~/Library/Fonts/Inter-Bold.ttf")
    fmt = a[a.index("--format") + 1] if "--format" in a else "master-9x16"
    if os.path.exists(font):
        set_fit(font, fmt)
    cs = cues(load_words(a[0]))
    write_srt(cs, a[1])
    print(len(cs), "cues ->", a[1])
    if "--burn" in a:
        i = a.index("--burn")
        burn(cs, a[i + 1], a[i + 2], font, fmt)
