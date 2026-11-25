#!/usr/bin/env python3
"""
DIN-rail modules as technical sketches, taken from Balter Technik's own drawings in Figma
("Tech-Schemas"), because the product photos of these modules are shot at an angle.

The Figma drawings (assets/figma/t_*.png, straight-on line drawings) are vectorised layer by layer
and brought into the house sketch style: black lines exactly as drawn in Figma, grey body, white label
field, green screw terminals, red LED. The label text that Figma shows is kept as vector outlines.

    python3 scripts/figma_modules.py
"""
import json
import os
import re
import subprocess
import tempfile

import numpy as np
from PIL import Image
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.normpath(os.path.join(HERE, "..", "assets", "figma"))
DEV = os.path.normpath(os.path.join(HERE, "..", "assets", "devices"))
MAP = {"EVO-HD-DL": "t_dl.png", "EVO-HD-C5001": "t_c5001.png", "EVO-C4001": "t_c4001.png"}   # EVO-HD-2WL: drawn by hand from t_2wl.png (Figma source is 1x only)
UP = 3


def trace(mask, fill, turd=2):
    with tempfile.TemporaryDirectory() as td:
        p = os.path.join(td, "m.pbm")
        Image.fromarray(np.where(mask, 0, 255).astype(np.uint8)).convert("1").save(p)
        o = os.path.join(td, "m.svg")
        subprocess.run(["potrace", p, "-s", "-o", o, "-t", str(turd), "-a", "1", "-O", ".2", "-r", "72", "--flat"], check=True)
        s = open(o).read()
    g = re.search(r'<g transform="([^"]+)"[^>]*>(.*?)</g>', s, re.S)
    if not g:
        return ""
    d = " ".join(x.replace("\n", " ") for x in re.findall(r'<path d="([^"]+)"', g.group(2)))
    return f'<path transform="{g.group(1)}" d="{d}" fill="{fill}" fill-rule="evenodd"/>' if d else ""


def convert(png):
    im = Image.open(png).convert("RGB")
    im = im.resize((im.width * UP, im.height * UP), Image.LANCZOS)
    a = np.array(im).astype(int)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    L = .299 * r + .587 * g + .114 * b
    mx, mn = a.max(-1), a.min(-1)
    sat = (mx - mn)
    line = (L < 120) & (sat < 60)
    green = (g > r + 30) & (g > b + 10)
    red = (r > g + 60) & (r > b + 40)
    blue = (b > r + 60) & (b > g + 20)
    body = ndimage.binary_fill_holes(ndimage.binary_closing(line | green, iterations=2))
    # white fields: large enclosed light areas that are rectangles (label plates)
    inner = body & ~line & ~green & (L > 230)
    lab, n = ndimage.label(inner)
    white = np.zeros_like(inner)
    H, W = inner.shape
    for i, sl in enumerate(ndimage.find_objects(lab), 1):
        comp = lab[sl] == i
        hh, ww = comp.shape
        if comp.sum() > .03 * H * W and comp.sum() / (hh * ww) > .85 and hh < .8 * H:
            white[sl] |= comp
    layers = [trace(body, "#F2F2F2", 10), trace(white, "#FFFFFF", 10), trace(green, "#3F8F4A", 2),
              trace(red, "#DC2626", 2), trace(blue, "#2563EB", 2), trace(line, "#111111", 2)]
    return W, H, "".join(layers)


def main():
    path = os.path.join(DEV, "devices.json")
    man = json.load(open(path, encoding="utf-8"))
    for d in man["devices"]:
        src = MAP.get(d["article"])
        if not src:
            continue
        W, H, body = convert(os.path.join(SRC, src))
        svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" '
               f'aria-label="{d["article"]} · {d["name"]} (Skizze nach Balter-Technik-Zeichnung)">{body}</svg>')
        fn = d["image"].rsplit(".", 1)[0] + ".svg"
        open(os.path.join(DEV, fn), "w", encoding="utf-8").write(svg)
        d["vector"] = fn
        d["vector_px"] = [W, H]
        d["vector_source"] = "Figma Tech-Schemas (Balter Technik)"
        print(d["article"], W, H)
    json.dump(man, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
