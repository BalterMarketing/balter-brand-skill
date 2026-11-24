#!/usr/bin/env python3
"""
Draw the vector illustration of every Balter device in assets/devices/devices.json.

Each device has two versions with the same file stem (the article number in lowercase):
    <article>.png   the real cut-out photo
    <article>.svg   the vector illustration

The illustration is MEASURED from the photo, not drawn by eye and never by AI: the photo is split
into flat tones (body, shade, glass, light plates, coloured LEDs), each tone is traced into exact
vector outlines with potrace, and the layers are stacked on the same canvas. Every element keeps the
photo's position and proportion one to one; only the surface becomes flat.

    python3 scripts/device_vectors.py              # all devices
    python3 scripts/device_vectors.py EVO-HD-7M    # one device

Needs: Python 3 with numpy, scipy and Pillow, and the potrace command (brew install potrace).
"""
import json
import os
import re
import subprocess
import sys
import tempfile

import numpy as np
from PIL import Image, ImageFilter
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
DEV = os.path.normpath(os.path.join(HERE, "..", "assets", "devices"))

DEFS = """<defs>
<linearGradient id="steel" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#e2e2e2"/><stop offset=".5" stop-color="#cdcdcd"/><stop offset="1" stop-color="#b9b9b9"/></linearGradient>
<linearGradient id="white" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#ffffff"/><stop offset="1" stop-color="#f0f0f0"/></linearGradient>
<linearGradient id="black" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#2e2e2e"/><stop offset="1" stop-color="#161616"/></linearGradient>
</defs>"""


def trace(mask, turd=6, alpha=1.0, opt=0.3):
    """potrace a boolean mask; returns (transform, path data) in image pixel coordinates."""
    if not mask.any():
        return None
    with tempfile.TemporaryDirectory() as td:
        pbm = os.path.join(td, "m.pbm")
        Image.fromarray(np.where(mask, 0, 255).astype(np.uint8)).convert("1").save(pbm)
        out = os.path.join(td, "m.svg")
        subprocess.run(["potrace", pbm, "-s", "-o", out, "-t", str(turd), "-a", str(alpha), "-O", str(opt),
                        "-r", "72", "--flat"], check=True)
        s = open(out).read()
    g = re.search(r"<g transform=\"([^\"]+)\"[^>]*>(.*?)</g>", s, re.S)
    if not g:
        return None
    paths = re.findall(r"<path d=\"([^\"]+)\"", g.group(2))
    if not paths:
        return None
    return g.group(1), " ".join(p.replace("\n", " ") for p in paths)


def layer(mask, fill, extra="", **kw):
    t = trace(mask, **kw)
    if not t:
        return ""
    tr, d = t
    return f'<path transform="{tr}" d="{d}" fill="{fill}" fill-rule="evenodd" {extra}/>'


def clean(mask, alpha, max_share=.06, min_area=30, solid=.25, big_solid=.62, min_h=5):
    """Keep only real elements of the device.

    Dropped: lighting gradients and brushed-steel streaks (too large and ragged, too thin, or
    touching the body edge). Kept: thin straight seams across the whole width, and large solid
    rectangles such as glass panels and lit windows."""
    if not mask.any():
        return mask
    H, W = mask.shape
    edge = alpha & ~ndimage.binary_erosion(alpha, iterations=4)
    lab, n = ndimage.label(mask)
    body = alpha.sum()
    keep = np.zeros(n + 1, bool)
    for i, sl in enumerate(ndimage.find_objects(lab), 1):
        comp = lab[sl] == i
        area = comp.sum()
        hh, ww = comp.shape
        fill = area / float(hh * ww)
        seam = hh <= 12 and ww > .8 * W and fill > .4
        if seam:
            keep[i] = True
            continue
        if area < min_area or min(hh, ww) < min_h:
            continue
        if area > body * max_share and fill < big_solid:
            continue
        if (edge[sl] & comp).any() and fill < big_solid:
            continue
        if fill < solid:
            continue
        keep[i] = True
    return keep[lab]


def shapes(mask, fill, extra="", turd=6):
    """Draw each element as a clean primitive at its measured place: near-rectangles as rounded
    rectangles on their exact bounds, near-circles as circles, everything else as a traced outline."""
    if not mask.any():
        return ""
    lab, n = ndimage.label(mask)
    rest = np.zeros_like(mask)
    out = []
    for i, sl in enumerate(ndimage.find_objects(lab), 1):
        comp = lab[sl] == i
        y0, x0 = sl[0].start, sl[1].start
        hh, ww = comp.shape
        f = comp.sum() / float(hh * ww)
        if f > .86 and min(hh, ww) >= 3:
            rx = min(6.0, min(hh, ww) * .08)
            out.append(f'<rect x="{x0}" y="{y0}" width="{ww}" height="{hh}" rx="{rx:.1f}" fill="{fill}" {extra}/>')
        elif .68 < f <= .86 and abs(hh - ww) <= .12 * max(hh, ww) and min(hh, ww) >= 6:
            out.append(f'<ellipse cx="{x0 + ww/2:.1f}" cy="{y0 + hh/2:.1f}" rx="{ww/2:.1f}" ry="{hh/2:.1f}" fill="{fill}" {extra}/>')
        else:
            rest[sl] |= comp
    return "".join(out) + layer(rest, fill, extra, turd=turd)


def material_of(d):
    """The body material, from the catalogue data in devices.json (not guessed from the photo)."""
    a, k, col = d["article"], d["kind"], d.get("colour", "")
    if col == "schwarz" or a.endswith("-CAM"):
        return "black"
    if col == "weiß":
        return "white"
    if k == "gehaeuse":
        return "steel" if "FRAME" in a else "black"
    return "steel"


def illustrate(d):
    im = Image.open(os.path.join(DEV, d["image"])).convert("RGBA")
    w, h = im.size
    a = np.array(im)
    alpha = a[..., 3] > 40
    rgb = Image.fromarray(a[..., :3]).filter(ImageFilter.MedianFilter(3))
    L = np.array(rgb.convert("L")).astype(np.int16)
    hsv = np.array(rgb.convert("HSV")).astype(np.int16)
    Hh, S, V = hsv[..., 0], hsv[..., 1], hsv[..., 2]
    ring = alpha & ~ndimage.binary_erosion(alpha, iterations=max(4, int(min(w, h) * .02)))
    ring &= ndimage.binary_erosion(alpha, iterations=2)
    med = float(np.median(L[ring])) if ring.any() else 200
    # local light: a blurred copy of the photo, so lighting gradients cancel out
    # the surface only (no glass, no plates), so dark and light parts leave no halo around them
    surf = alpha & (L > 120) & (L < 236)
    k = max(25, int(min(w, h) * .28))
    num = ndimage.uniform_filter(np.where(surf, L, 0).astype(float), k)
    den = ndimage.uniform_filter(surf.astype(float), k)
    glob = float(np.median(L[surf])) if surf.any() else 200.0
    bg = np.where(den > .05, num / np.maximum(den, 1e-6), glob)
    hp = L - bg

    material = material_of(d)
    base = {"white": "url(#white)", "black": "url(#black)", "steel": "url(#steel)"}[material]

    out_seams = []
    out = [layer(alpha, base, 'stroke="#9a9a9a" stroke-width="1.2" vector-effect="non-scaling-stroke"', turd=20)]
    if material == "steel":
        dark = clean(alpha & (L < 70), alpha, max_share=.95, solid=.12, min_area=12, min_h=3)
        mid = clean(alpha & (hp < -28) & (L >= 70), alpha, min_h=2, min_area=14, solid=.2)
        lm = alpha & ((hp > 12) | (L > 250)) & (S < 40) & (L > 205)
        lm = ndimage.binary_closing(lm, iterations=1) & alpha
        light = clean(lm, alpha, max_share=.9, solid=.72, min_area=60, min_h=6, big_solid=1.1)
        # name plates whose glass is no lighter than the steel: found by their darker outline
        ring = ndimage.binary_closing(alpha & (hp < -12), iterations=1)
        filled = ndimage.binary_fill_holes(ring) & ~ring
        plates = np.zeros_like(filled)
        lab, n = ndimage.label(filled)
        for i, sl in enumerate(ndimage.find_objects(lab), 1):
            comp = lab[sl] == i
            hh, ww = comp.shape
            if ww > 2.4 * hh and hh >= 8 and comp.sum() / float(hh * ww) > .8 and ww < .8 * w:
                plates[sl] |= comp
        light = light | ndimage.binary_dilation(plates, iterations=1)
        if d["kind"] == "pro-modul":
            light = clean(light, alpha, max_share=.9, solid=.82, min_area=60, min_h=6, big_solid=1.1)
            # seams between the plates: rows where a darker line runs across the whole module
            # (a module face is four equal bands; a seam can only sit on a band boundary)
            rows = ((hp < -10) & (L > 80) & (L < 205) & alpha).mean(axis=1)
            ys = np.where(rows > .3)[0]
            for grp in np.split(ys, np.where(np.diff(ys) > 2)[0] + 1):
                on_band = grp.size and min(abs(grp.mean() - h * q / 4) for q in (1, 2, 3)) < h * .04
                if grp.size and grp.size <= 8 and on_band:
                    y = float(grp.mean())
                    out_seams.append(f'<path d="M0 {y:.1f}H{w}" stroke="#7a7a7a" stroke-width="{max(1.5, grp.size):.1f}"/>'
                                     f'<path d="M0 {y + max(1.5, grp.size)/2 + .8:.1f}H{w}" stroke="#ffffff" stroke-width="1" opacity=".7"/>')
        out += [shapes(mid, "#8a8a8a"), shapes(dark, "#111111"),
                shapes(light, "#ffffff", 'stroke="#7a7a7a" stroke-width="1" vector-effect="non-scaling-stroke"', turd=10)]
        if dark.any():
            hull = ndimage.binary_fill_holes(ndimage.binary_closing(dark, iterations=3))
            ui = clean(hull & ~dark & (L > 200), alpha, max_share=.02, min_area=4, min_h=1, solid=.05)
            out.append(layer(ui, "#e5e5e5", turd=3))
    elif material == "white":
        mid = clean(alpha & (L < 215) & (L >= 75), alpha, max_share=.2, solid=.1, min_h=2, min_area=10)
        dark = alpha & (L < 75)
        out += [shapes(mid, "#bdbdbd"), shapes(dark, "#111111")]
        if dark.any():
            hull = ndimage.binary_fill_holes(ndimage.binary_closing(dark, iterations=3))
            out.append(layer(hull & ~dark & (L > 150), "#f2f2f2", turd=3))
    else:
        mid = clean(alpha & (L >= 95) & (L < 190) & (np.abs(hp) > 20), alpha, max_share=.12, solid=.2, min_h=3)
        light = clean(alpha & (L >= 190), alpha, max_share=.6, solid=.1, min_area=8, min_h=2)
        out += [shapes(mid, "#5c5c5c"), shapes(light, "#f5f5f5", turd=8)]

    out += out_seams
    # coloured details that carry meaning: blue status and fingerprint rings, green and red LEDs
    col = alpha & (S > 110) & (V > 90)
    out += [layer(col & (Hh > 130) & (Hh < 185), "#3b82f6", turd=2),
            layer(col & (Hh > 60) & (Hh < 120), "#22c55e", turd=2),
            layer(col & ((Hh < 12) | (Hh > 240)), "#dc2626", turd=2)]

    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" '
            f'aria-label="{d["article"]} · {d["name"]} (Illustration)">' + DEFS + "".join(out) + "</svg>")


def main():
    path = os.path.join(DEV, "devices.json")
    man = json.load(open(path, encoding="utf-8"))
    only = {x.upper() for x in sys.argv[1:]}
    n = 0
    for d in man["devices"]:
        if only and d["article"].upper() not in only:
            continue
        fn = d["image"].rsplit(".", 1)[0] + ".svg"
        open(os.path.join(DEV, fn), "w", encoding="utf-8").write(illustrate(d))
        d["vector"] = fn
        n += 1
    json.dump(man, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(n, "illustrations")


if __name__ == "__main__":
    main()
