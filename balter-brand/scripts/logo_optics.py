#!/usr/bin/env python3
"""
Optical correction of the landscape BALTER logos, and the files that carry it.

Why: in the source artwork the text block (BALTER + STAY AHEAD) is centred on the eagle's bounding
box. The eagle's box is a poor measure of where it *looks* to be: the thin crown and the pointed
shield tip carry almost no weight, and the bold BALTER pulls the text block's weight upwards while
the light claim hangs below. The text therefore reads slightly low.

Method (both axes use the same rule):
  visual centre of a block = mean of
      (a) the middle of its optical extent: rows whose silhouette is at least 25 % of the widest row
          (drops the thin crown and the shield tip; flat type edges stay), and
      (b) its centre of mass (ink area).
  The text block is moved so its visual centre sits on the mark's visual centre.

Clear space: x = cap height of the B in BALTER. The padded files add x on every side, then shift the
canvas so the logo's visual centre (same rule, whole logo) is the canvas centre.

Baseline: the BALTER baseline is the line other elements align to. The baseline files are cropped
tight; their <svg> carries data-baseline (fraction of the height from the top) and the brand book
gives the CSS for inline use.

    python3 tools/logo_optics.py      # writes logo/optisch/*.svg and *.png, prints the numbers
"""
import json
import os
import re
import subprocess
import tempfile

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, ".."))
OUT = os.path.join(ROOT, "logo", "optisch")
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
S = 10  # raster scale for measuring


def raster(svg_text, w, h, scale=S, transparent=False):
    with tempfile.TemporaryDirectory() as td:
        sp = os.path.join(td, "l.svg")
        open(sp, "w").write(svg_text)
        bg = "transparent" if transparent else "#fff"
        hp = os.path.join(td, "l.html")
        open(hp, "w").write(f'<body style="margin:0;background:{bg}"><img src="l.svg" style="width:{w*scale}px;height:{h*scale}px;display:block">')
        png = os.path.join(td, "l.png")
        args = [CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars", f"--window-size={int(round(w*scale))},{int(round(h*scale))}",
                f"--screenshot={png}", "file://" + hp]
        if transparent:
            args.insert(4, "--default-background-color=00000000")
        subprocess.run(args, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return Image.open(png).copy()


def ink_of(img):
    a = np.array(img.convert("L")).astype(float)
    return (255 - a) / 255.0


def block(ink, x0, x1):
    sub = ink[:, x0:x1]
    rows = (sub > .5)
    width = np.array([(np.nonzero(r)[0].max() - np.nonzero(r)[0].min()) if r.any() else 0 for r in rows], float)
    cols = (sub > .5).any(axis=0)
    ys = np.nonzero(width > 0)[0]
    xs = np.nonzero(cols)[0]
    opt = np.nonzero(width >= .25 * width.max())[0]
    mass = sub.sum()
    cy = (sub * np.arange(sub.shape[0])[:, None]).sum() / mass
    cx = (sub * np.arange(sub.shape[1])[None, :]).sum() / mass + x0
    return dict(top=ys.min() / S, bottom=ys.max() / S, left=(xs.min() + x0) / S, right=(xs.max() + x0) / S,
                opt_mid=(opt.min() + opt.max()) / 2 / S, cy=cy / S, cx=cx / S, mass=mass)


def visual_y(b):
    return (b["opt_mid"] + b["cy"]) / 2


def correct(src, text_ids, split_x, name, recolour=None):
    """src: svg path; text_ids: function(svg)->svg with text wrapped in <g id="text">; returns data."""
    s = open(src).read()
    vb = [float(v) for v in re.search(r'viewBox="([^"]+)"', s).group(1).split()]
    W, H = vb[2], vb[3]
    s = text_ids(s)
    ink = ink_of(raster(s.replace('id="text"', 'id="text" transform="translate(0 0)"'), W, H))
    mark = block(ink, 0, int(split_x * S))
    text = block(ink, int(split_x * S), int(W * S))
    dy = visual_y(mark) - visual_y(text)
    fixed = s.replace('<g id="text">', f'<g id="text" transform="translate(0 {dy:.3f})">')
    ink2 = ink_of(raster(fixed, W, H))
    allb = block(ink2, 0, int(W * S))
    text2 = block(ink2, int(split_x * S), int(W * S))
    return dict(svg=fixed, W=W, H=H, dy=dy, mark=mark, text=text, text_after=text2, all=allb)


def wrap_site(s):
    # logo-site-*: the wordmark + claim is the first <path> with translate(117.319 20.557)
    return re.sub(r'(<path[^>]*transform="translate\(117\.319 20\.557\)"[^>]*/>)', r'<g id="text">\1</g>', s, count=1)


def wrap_quer(s):
    # balter-logo-quer-*: the letters are the cls-1 paths, the mark is cls-2
    paths = re.findall(r'<path class="cls-1"[^>]*/>', s)
    for p in paths:
        s = s.replace(p, "", 1)
    return s.replace('<path class="cls-2"', '<g id="text">' + "".join(paths) + '</g><path class="cls-2"', 1)


def variants(d, cap, key, colours):
    """Write tight, padded (optically centred) and baseline files in black and white."""
    W, H = d["W"], d["H"]
    a = d["all"]
    x0, x1, y0, y1 = a["left"], a["right"], a["top"], a["bottom"]
    # visual centre of the whole logo, same rule on both axes
    vy = (( (y0 + y1) / 2) + a["cy"]) / 2
    vx = (((x0 + x1) / 2) + a["cx"]) / 2
    pad = cap
    left, right = pad + (vx - (x0 + x1) / 2), pad - (vx - (x0 + x1) / 2)
    top, bottom = pad + (vy - (y0 + y1) / 2), pad - (vy - (y0 + y1) / 2)
    # canvas: centre of canvas = visual centre
    box_x, box_y = x0 - (pad - (vx - (x0 + x1) / 2)) - 0, 0
    cx0 = vx - ((x1 - x0) / 2 + pad)
    cy0 = vy - ((y1 - y0) / 2 + pad)
    cw = (x1 - x0) + 2 * pad
    ch = (y1 - y0) + 2 * pad
    base_text = d["text_after"]
    baseline = d["baseline_y"]
    inner = re.search(r"<svg[^>]*>(.*)</svg>", d["svg"], re.S).group(1)
    out = {}
    for col, word in colours:
        body = inner
        body = re.sub(r'fill="#(?:000|000000|fff|ffffff)"', f'fill="{col}"', body)
        body = re.sub(r'fill: #[0-9a-fA-F]{3,6};', f'fill: {col};', body)
        tight = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{x0:.2f} {y0:.2f} {x1-x0:.2f} {y1-y0:.2f}" '
                 f'width="{x1-x0:.2f}" height="{y1-y0:.2f}" data-baseline="{(baseline-y0)/(y1-y0):.4f}">'
                 f'<desc>BALTER logo, optically corrected (text raised {abs(d["dy"]):.2f}). Baseline of BALTER at {100*(baseline-y0)/(y1-y0):.1f} % of the height from the top.</desc>{body}</svg>')
        padded = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{cx0:.2f} {cy0:.2f} {cw:.2f} {ch:.2f}" width="{cw:.2f}" height="{ch:.2f}">'
                  f'<desc>BALTER logo with clear space x = cap height of B ({pad:.2f}) on every side, canvas centred on the visual centre.</desc>{body}</svg>')
        for kind, svg, w, h in (("grundlinie", tight, x1 - x0, y1 - y0), ("schutzzone", padded, cw, ch)):
            fn = f"{key}-{kind}-{word}"
            open(os.path.join(OUT, fn + ".svg"), "w").write(svg)
            img = raster(svg, w, h, scale=8, transparent=True)
            img.save(os.path.join(OUT, fn + ".png"), optimize=True)
            out[fn] = dict(w=round(w, 2), h=round(h, 2))
    return dict(files=out, pad=pad, vx=vx, vy=vy, tight=[x0, y0, x1 - x0, y1 - y0], canvas=[cx0, cy0, cw, ch],
                baseline_frac=(baseline - y0) / (y1 - y0))


def main():
    os.makedirs(OUT, exist_ok=True)
    report = {}
    jobs = [("quer-claim", os.path.join(ROOT, "logo", "logo-site-black.svg"), wrap_site, 112, 20.557 + 45.1),
            ("quer", os.path.join(ROOT, "logo", "balter-logo-quer-black.svg"), wrap_quer, None, None)]
    for key, src, wrap, split, base in jobs:
        s = open(src).read()
        if split is None:
            # find the gap between mark and letters from the raster
            vb = [float(v) for v in re.search(r'viewBox="([^"]+)"', s).group(1).split()]
            ink = ink_of(raster(s, vb[2], vb[3]))
            cols = (ink > .5).any(axis=0)
            # first empty column after the mark (the gap between eagle and B)
            start = int(vb[2] * S * .1)
            empty = np.nonzero(~cols[start:])[0]
            split = (start + empty.min() + 2) / S if empty.size else vb[2] * .3
        d = correct(src, wrap, split, key)
        # BALTER baseline after the shift: bottom of the flat letters (the B), measured
        t = d["text_after"]
        if base is None:
            # the B's flat bottom: lowest row of the first letter column band
            ink = ink_of(raster(d["svg"], d["W"], d["H"]))
            bx0 = int(t["left"] * S)
            band = ink[:, bx0:bx0 + int(10 * S)] > .5
            base = np.nonzero(band.any(axis=1))[0].max() / S
        else:
            base = base + d["dy"]
        d["baseline_y"] = base
        cap = base - t["top"] if key == "quer" else (20.557 + 45.1) - (20.557 + 0.8)
        v = variants(d, cap, key, [("#000000", "schwarz"), ("#ffffff", "weiss")])
        report[key] = dict(text_shift=round(d["dy"], 3), mark=d["mark"], text_before=d["text"], text_after=t,
                           cap=round(cap, 2), **{k: v[k] for k in ("pad", "vx", "vy", "tight", "canvas", "baseline_frac")})
    for k, r in report.items():
        print(k, "text shift", r["text_shift"], "cap", r["cap"], "baseline", round(r["baseline_frac"], 4),
              "canvas", [round(x, 2) for x in r["canvas"]])
    json.dump(report, open(os.path.join(OUT, "optik.json"), "w"), indent=1, default=float)


if __name__ == "__main__":
    main()
