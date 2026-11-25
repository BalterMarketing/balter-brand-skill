#!/usr/bin/env python3
"""
Safe-zone overlays for every social format, from assets/social/safe-zones.json.

    python3 scripts/safe_zones.py png  <out-dir>   # transparent PNG overlays (Resolve, Figma, Premiere)
    python3 scripts/safe_zones.py svg  <out-dir>   # small SVG diagrams for the brand book
    python3 scripts/safe_zones.py check <image> <format-id> [x y w h ...]
                                                   # are these boxes (text, logo) inside the usable area?

In Resolve: put the PNG on the top video track, composite mode Normal, disable it before the render.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SPEC = os.path.join(HERE, "..", "assets", "social", "safe-zones.json")


def formats():
    return {f["id"]: f for f in json.load(open(SPEC, encoding="utf-8"))["formats"]}


def usable(f):
    return f["left"], f["top"], f["w"] - f["left"] - f["right"], f["h"] - f["top"] - f["bottom"]


def png(out):
    from PIL import Image, ImageDraw
    os.makedirs(out, exist_ok=True)
    for f in formats().values():
        im = Image.new("RGBA", (f["w"], f["h"]), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        x, y, w, h = usable(f)
        hatch = (255, 64, 64, 70)
        for box in ((0, 0, f["w"], y), (0, y + h, f["w"], f["h"]), (0, y, x, y + h), (x + w, y, f["w"], y + h)):
            if box[2] > box[0] and box[3] > box[1]:
                d.rectangle(box, fill=hatch)
        d.rectangle((x, y, x + w - 1, y + h - 1), outline=(255, 255, 255, 230), width=3)
        if f.get("inner"):
            i = f["inner"]
            d.rectangle((i, i, f["w"] - i - 1, f["h"] - i - 1), outline=(255, 255, 255, 120), width=2)
        for e in f.get("extra", []):
            d.line((0, e["y0"], f["w"], e["y0"]), fill=(255, 255, 255, 160), width=2)
            d.line((0, e["y1"], f["w"], e["y1"]), fill=(255, 255, 255, 160), width=2)
        for b in f.get("boxes", []):
            d.rectangle((b["x"], b["y"], b["x"] + b["w"], b["y"] + b["h"]), fill=hatch)
        im.save(os.path.join(out, f"safe-{f['id']}.png"))
    print(len(formats()), "overlays in", out)


def svg_of(f, scale=0.25):
    W, H = f["w"] * scale, f["h"] * scale
    x, y, w, h = [v * scale for v in usable(f)]
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W:.0f} {H:.0f}" role="img" aria-label="Sicherheitszone {f["name"]}">',
         f'<defs><pattern id="hz-{f["id"]}" width="6" height="6" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">'
         '<rect width="6" height="6" fill="#f2f2f2"/><path d="M0 0V6" stroke="#bdbdbd" stroke-width="2"/></pattern></defs>',
         f'<rect x="0.5" y="0.5" width="{W - 1:.1f}" height="{H - 1:.1f}" rx="8" fill="url(#hz-{f["id"]})" stroke="#000"/>',
         f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" fill="#fff" stroke="#000" stroke-width="1"/>']
    for e in f.get("extra", []):
        for yy in (e["y0"], e["y1"]):
            o.append(f'<line x1="0" y1="{yy * scale:.1f}" x2="{W:.1f}" y2="{yy * scale:.1f}" stroke="#000" stroke-dasharray="3 3" stroke-width=".8"/>')
    for b in f.get("boxes", []):
        o.append(f'<rect x="{b["x"] * scale:.1f}" y="{b["y"] * scale:.1f}" width="{b["w"] * scale:.1f}" height="{b["h"] * scale:.1f}" fill="url(#hz-{f["id"]})" stroke="#000" stroke-width=".8"/>')
    o.append("</svg>")
    return "".join(o)


def check(fid, boxes):
    f = formats()[fid]
    x, y, w, h = usable(f)
    bad = []
    for i in range(0, len(boxes), 4):
        bx, by, bw, bh = boxes[i:i + 4]
        if bx < x or by < y or bx + bw > x + w or by + bh > y + h:
            bad.append((bx, by, bw, bh))
    print("OK" if not bad else f"outside the safe area: {bad}  (usable x {x}–{x + w}, y {y}–{y + h})")
    return not bad


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "png":
        png(sys.argv[2])
    elif cmd == "svg":
        os.makedirs(sys.argv[2], exist_ok=True)
        for f in formats().values():
            open(os.path.join(sys.argv[2], f"safe-{f['id']}.svg"), "w").write(svg_of(f))
    elif cmd == "check":
        sys.exit(0 if check(sys.argv[3], [float(v) for v in sys.argv[4:]]) else 1)
