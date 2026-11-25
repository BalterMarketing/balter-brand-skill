#!/usr/bin/env python3
"""
Technical sketches (Skizzen) of Balter devices for wiring plans and manuals.

Not a trace. Each device is drawn from a handful of plain shapes in three tones:
    grey   body (steel #D9D9D9, white plastic #F2F2F2, black finish #3A3A3A)
    black  camera, status bar, glass, RFID / fingerprint block, screens
    white  name plates and lit windows
with one black outline (2 px at the photo's scale), always seen straight from the front.

Where each shape sits is measured from the real photo (assets/devices/<article>.png), so position and
proportion match the photo one to one; the shape itself is a clean rectangle, circle or line.
DIN-rail modules (Netzteil, Türöffner-Modul, LAN-Konverter) are photographed at an angle, so they are
drawn as their front panel, the way Balter Technik draws them in its wiring schemas.

    python3 scripts/device_sketch.py               # all devices -> assets/devices/<article>.svg
    python3 scripts/device_sketch.py EVO-HD-4FAM   # one
"""
import json
import os
import sys

import numpy as np
from PIL import Image, ImageFilter
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
DEV = os.path.normpath(os.path.join(HERE, "..", "assets", "devices"))

INK = "#111111"
BODY = {"steel": "#D9D9D9", "white": "#F2F2F2", "black": "#3A3A3A"}
DARK = "#111111"
PLATE = "#FFFFFF"


class Sk:
    def __init__(self, w, h, sw):
        self.w, self.h, self.sw, self.o = w, h, sw, []

    def rect(self, x, y, w, h, fill, rx=None, stroke=INK, sw=None, extra=""):
        rx = min(w, h) * .12 if rx is None else rx
        st = f' stroke="{stroke}" stroke-width="{(sw or self.sw):.1f}"' if stroke else ""
        self.o.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx:.1f}" fill="{fill}"{st} {extra}/>')

    def circ(self, x, y, r, fill, stroke=INK, sw=None):
        st = f' stroke="{stroke}" stroke-width="{(sw or self.sw):.1f}"' if stroke else ""
        self.o.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" fill="{fill}"{st}/>')

    def line(self, x1, y1, x2, y2, col=INK, sw=None):
        self.o.append(f'<path d="M{x1:.1f} {y1:.1f}L{x2:.1f} {y2:.1f}" stroke="{col}" stroke-width="{(sw or self.sw):.1f}" stroke-linecap="round"/>')

    def text(self, x, y, s, size, anchor="middle", fill=INK, weight=600):
        self.o.append(f'<text x="{x:.1f}" y="{y:.1f}" font-family="Inter,Arial,sans-serif" font-size="{size:.1f}" font-weight="{weight}" fill="{fill}" text-anchor="{anchor}">{s}</text>')

    def svg(self, label):
        return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {self.w} {self.h}" width="{self.w}" height="{self.h}" role="img" '
                f'aria-label="{label}">' + "".join(self.o) + "</svg>")


def material_of(d):
    a, k, col = d["article"], d["kind"], d.get("colour", "")
    if col == "schwarz" or a.endswith("-CAM"):
        return "black"
    if col == "weiß":
        return "white"
    if k == "gehaeuse":
        return "steel" if "FRAME" in a else "black"
    return "steel"


def comps(mask, min_area=20):
    lab, n = ndimage.label(mask)
    out = []
    for i, sl in enumerate(ndimage.find_objects(lab), 1):
        c = lab[sl] == i
        a = int(c.sum())
        if a < min_area:
            continue
        y0, x0 = sl[0].start, sl[1].start
        h, w = c.shape
        out.append(dict(x=x0, y=y0, w=w, h=h, area=a, fill=a / float(w * h)))
    return out


def measure(d):
    im = Image.open(os.path.join(DEV, d["image"])).convert("RGBA")
    W, H = im.size
    a = np.array(im)
    alpha = a[..., 3] > 40
    rgb = Image.fromarray(a[..., :3]).filter(ImageFilter.MedianFilter(3))
    L = np.array(rgb.convert("L")).astype(np.int16)
    S = np.array(rgb.convert("HSV"))[..., 1]
    inner = ndimage.binary_erosion(alpha, iterations=4)
    surf = alpha & (L > 120) & (L < 236)
    k = max(25, int(min(W, H) * .28))
    num = ndimage.uniform_filter(np.where(surf, L, 0).astype(float), k)
    den = ndimage.uniform_filter(surf.astype(float), k)
    glob = float(np.median(L[surf])) if surf.any() else 200.0
    hp = L - np.where(den > .05, num / np.maximum(den, 1e-6), glob)
    ys, xs = np.nonzero(alpha)
    box = (xs.min(), ys.min(), xs.max() - xs.min() + 1, ys.max() - ys.min() + 1)
    return dict(W=W, H=H, alpha=alpha, inner=inner, L=L, S=S, hp=hp, box=box)


# ---------------------------------------------------------------- stations, extensions, audio stations
def station(d, m, s):
    W, H = m["W"], m["H"]
    bx, by, bw, bh = m["box"]
    mat = material_of(d)
    s.rect(bx + s.sw / 2, by + s.sw / 2, bw - s.sw, bh - s.sw, BODY[mat], rx=bw * .02)
    L, hp, inner = m["L"], m["hp"], m["inner"]
    if mat == "black":
        bodyL = float(np.median(L[inner]))
        dark = comps(inner & (L < bodyL - 18), 30)
    else:
        dark = comps(inner & (L < 70), 30)
    used = np.zeros_like(inner)
    for c in dark:
        if c["area"] > W * H * .5:
            continue
        x, y, w, h = c["x"], c["y"], c["w"], c["h"]
        sq = abs(w - h) <= .2 * max(w, h)
        if sq and c["fill"] > .55 and W * .06 < w < W * .3:                # camera lens
            s.circ(x + w / 2, y + h / 2, max(w, h) / 2, DARK)
            s.circ(x + w / 2, y + h / 2, max(w, h) * .22, "#6b7280", stroke=None)
        elif w > 2.2 * h and h >= 3 and w > W * .18:                         # status bar or slot
            s.rect(x, y, w, h, DARK, rx=min(h * .3, 6))
        elif w > W * .2 and h > H * .08:                                     # glass / RFID / fingerprint block
            s.rect(x, y, w, h, DARK, rx=min(w, h) * .06)
        elif w > 2.5 * h and w > W * .06:                                    # microphone lines
            s.line(x, y + h / 2, x + w, y + h / 2, INK, max(2, h * .8))
        elif sq and w <= W * .05 and c["fill"] > .5:                          # grille dot
            s.circ(x + w / 2, y + h / 2, max(w, h) / 2, DARK, stroke=None)
        else:
            continue
        used[y:y + h, x:x + w] = True
    if d["article"].startswith("EVO-HD-TOUCH") or "TOUCH" in d["article"]:
        ys_, xs_ = np.nonzero(inner & (L > 60) & (L < 200) & (m["S"] < 60))
        glass = [c for c in dark if c["w"] > W * .5]
        if glass:
            g = max(glass, key=lambda c: c["area"])
            sub = (xs_ > g["x"] + 4) & (xs_ < g["x"] + g["w"] - 4) & (ys_ > g["y"] + g["h"] * .15) & (ys_ < g["y"] + g["h"] * .85)
            if sub.sum() > 200:
                x0_, x1_ = np.percentile(xs_[sub], [2, 98]); y0_, y1_ = np.percentile(ys_[sub], [2, 98])
                s.rect(x0_, y0_, x1_ - x0_, y1_ - y0_, "#2a2a2a", rx=4, stroke="#6b6b6b")
            s.circ(g["x"] + g["w"] / 2, g["y"] + g["h"] * .06, g["w"] * .06, "#2a2a2a", stroke="#6b6b6b")
    # name plates: bright or outlined rectangles, wide
    lm = inner & ((hp > 12) | (L > 248)) & (m["S"] < 40) & (L > 200)
    ring = ndimage.binary_closing(inner & (hp < -12), iterations=1)
    lm |= ndimage.binary_fill_holes(ring) & ~ring
    cands = [c for c in comps(ndimage.binary_closing(lm, iterations=1), 200)]
    if d.get("buttons") and sum(1 for c in cands if c["w"] > 2.4 * c["h"]) < d["buttons"]:
        cands = comps(ndimage.binary_fill_holes(ring) & ~ring, 200) or cands
    plates = [c for c in cands if c["w"] > 2.4 * c["h"] and c["h"] > H * .015 and c["fill"] > .6 and bw * .2 < c["w"] < bw * .8]
    if d.get("buttons") and plates and len(plates) < d["buttons"]:
        # find the missing plates in the same column: pairs of darker edges one plate-height apart
        ref = max(plates, key=lambda c: c["area"])
        x0_, x1_, ph = int(ref["x"] + ref["w"] * .1), int(ref["x"] + ref["w"] * .9), ref["h"]
        sig = hp[:, x0_:x1_].mean(axis=1)
        edges = np.nonzero(sig < -8)[0]
        runs = np.split(edges, np.where(np.diff(edges) > 2)[0] + 1) if edges.size else []
        mids = [r.mean() for r in runs if r.size]
        have = [(c["y"], c["y"] + c["h"]) for c in plates]
        for i in range(len(mids) - 1):
            top, bot = mids[i], mids[i + 1]
            if .75 * ph <= bot - top <= 1.3 * ph and not any(a_ - 3 <= top <= b_ + 3 for a_, b_ in have):
                plates.append(dict(x=ref["x"], y=int(top), w=ref["w"], h=int(bot - top), area=0, fill=1))
                have.append((top, bot))
    cands = plates
    for c in cands:
        if c["w"] > 2.4 * c["h"] and c["h"] > H * .015 and c["fill"] > .6 and c["w"] < bw * .8 and c["w"] > bw * .2:
            s.rect(c["x"], c["y"], c["w"], c["h"], PLATE, rx=c["h"] * .12)
            # the call button sits right of the plate, centred on it
            cy = c["y"] + c["h"] / 2
            xs = c["x"] + c["w"]
            band = (m["alpha"][int(c["y"]):int(c["y"] + c["h"]), int(xs):int(min(W, xs + c["h"] * 3))])
            r = c["h"] * .42
            cx = xs + c["h"] * .25 + r if band.size else xs + r * 2
            # find the button's centre from the darker ring right of the plate
            seg = hp[int(c["y"]):int(c["y"] + c["h"]), int(xs):int(min(W, xs + c["h"] * 2.2))]
            if seg.size:
                cols = np.nonzero((seg < -10).sum(axis=0) > c["h"] * .15)[0]
                if cols.size:
                    cx = xs + (cols.min() + cols.max()) / 2
                    r = min(c["h"] * .55, max(c["h"] * .3, (cols.max() - cols.min()) / 2))
            if cx + r < bx + bw * .92:
                s.circ(cx, cy, r, BODY[mat] if mat != "black" else "#2a2a2a")
                s.circ(cx, cy, r * .18, INK, stroke=None)
    # mounting tabs top and bottom: small pills on the centre line
    for c in comps(inner & ((L > 245) | (L < 90)), 30):
        cx = c["x"] + c["w"] / 2
        if abs(cx - (bx + bw / 2)) < bw * .08 and c["w"] < bw * .2 and c["w"] > 1.5 * c["h"] and (c["y"] < by + bh * .06 or c["y"] > by + bh * .92):
            s.rect(c["x"], c["y"], c["w"], c["h"], "#f5f5f5", rx=c["h"] * .3)


# ---------------------------------------------------------------- monitors and audio station
def monitor(d, m, s):
    bx, by, bw, bh = m["box"]
    mat = material_of(d)
    s.rect(bx + s.sw / 2, by + s.sw / 2, bw - s.sw, bh - s.sw, BODY[mat], rx=min(bw, bh) * .03)
    L, inner = m["L"], m["inner"]
    thr = 60 if mat == "white" else 18
    big = [c for c in comps(inner & (L < thr), 200) if c["w"] > bw * .3 and c["h"] > bh * .2]
    if mat == "black":
        # the screen is the darkest large block; on a black body use the glass edge from the brightness step
        big = [c for c in comps(inner & (L < 12), 200) if c["w"] > bw * .3 and c["h"] > bh * .2] or big
    if mat == "black":
        ys_, xs_ = np.nonzero(inner & (L > 110))
        if ys_.size > 200:
            x0_, x1_ = np.percentile(xs_, [1, 99]); y0_, y1_ = np.percentile(ys_, [1, 99])
            pad = (x1_ - x0_) * .03
            big = [dict(x=x0_ - pad, y=y0_ - pad, w=x1_ - x0_ + 2 * pad, h=y1_ - y0_ + 2 * pad, area=1)]
    if big:
        c = max(big, key=lambda c: c["area"])
        s.rect(c["x"], c["y"], c["w"], c["h"], DARK, rx=min(c["w"], c["h"]) * .02)
        scr = (c["x"], c["y"], c["w"], c["h"])
    else:
        scr = None
    # round keys and LEDs outside the screen
    ring = (np.abs(m["hp"]) > 25) & inner
    for c in comps(ndimage.binary_fill_holes(ring), 30):
        x, y, w, h = c["x"], c["y"], c["w"], c["h"]
        if scr and scr[0] - 2 <= x <= scr[0] + scr[2] and scr[1] - 2 <= y <= scr[1] + scr[3]:
            continue
        if abs(w - h) <= .25 * max(w, h) and c["fill"] > .5 and 4 <= w <= bw * .05:
            s.circ(x + w / 2, y + h / 2, w / 2, "none" if w > 10 else INK, sw=s.sw * (.8 if w > 10 else .5))


def talk(d, m, s):
    bx, by, bw, bh = m["box"]
    mat = material_of(d)
    body = BODY[mat]
    # the body without the cable: rows wider than 40 % of the widest row
    rows = m["alpha"].sum(axis=1)
    full = np.nonzero(rows > rows.max() * .4)[0]
    y1 = full.max()
    s.rect(bx + s.sw / 2, by + s.sw / 2, bw - s.sw, y1 - by - s.sw, body, rx=bw * .06)
    # the handset: the left column, edge found where the brightness steps
    cols = np.abs(np.diff(m["L"][by + 10:y1 - 10, bx:bx + bw].astype(float).mean(axis=0)))
    split = bx + int(np.argmax(cols[int(bw * .4):int(bw * .8)]) + bw * .4)
    s.rect(bx + bw * .03, by + 4, split - bx - bw * .03, y1 - by - 8, body, rx=bw * .08)
    # keys on the right
    for c in comps(ndimage.binary_fill_holes((np.abs(m["hp"]) > 25) & m["inner"]), 40):
        if c["x"] > split and abs(c["w"] - c["h"]) <= .3 * max(c["w"], c["h"]) and c["w"] > bw * .08:
            blue = m["S"][c["y"] + c["h"] // 2, c["x"] + c["w"] // 2] > 110
            s.circ(c["x"] + c["w"] / 2, c["y"] + c["h"] / 2, c["w"] / 2, "#3b82f6" if blue else "none")
    # cable
    cx = bx + bw * .3
    s.line(cx, y1, cx, m["H"] - 2, "#9a9a9a", s.sw * 1.4)


# ---------------------------------------------------------------- EVO HD PRO modules, straight on
def pro_module(d, m, s):
    W, H = m["W"], m["H"]
    a = d["article"]
    band = H / 4
    glass = a.endswith("CAM")
    s.rect(s.sw / 2, s.sw / 2, W - s.sw, H - s.sw, DARK if glass else BODY["steel"], rx=W * .01)
    if glass:
        s.circ(W * .5, H * .48, W * .12, DARK, stroke="#9a9a9a")
        s.circ(W * .5, H * .48, W * .05, "#6b7280", stroke=None)
        for i in range(4):
            s.circ(W * (.27 + i * .155), H * .8, W * .025, "none", stroke="#d4d4d4", sw=s.sw * .8)
        return
    if "AUD" in a:
        s.rect(W * .18, band * .58, W * .3, band * .08, DARK, rx=band * .04, stroke=None)
        n = 2 if "2K" in a else (1 if "1K" in a else 0)
        for i in range(4 - n, 4):
            s.line(0, band * i, W, band * i)
            if a.endswith("N"):
                s.rect(W * .17, band * i + band * .28, W * .66, band * .44, PLATE, rx=4)
        return
    if "KEY" in a:
        for i in range(4):
            if i:
                s.line(0, band * i, W, band * i)
            if a.endswith("N"):
                s.rect(W * .17, band * i + band * .28, W * .66, band * .44, PLATE, rx=4)
        return
    if "RFG" in a:
        s.rect(W * .17, H * .17, W * .66, H * .73, DARK, rx=8)
        s.rect(W * .34, H * .52, W * .32, H * .3, "#262626", rx=10, stroke="#5a5a5a")
        s.circ(W * .5, H * .67, W * .075, "none", stroke="#3b82f6")
        return
    if a.endswith("INF-KN"):
        s.rect(W * .14, H * .14, W * .72, H * .72, PLATE, rx=6)


# ---------------------------------------------------------------- housings and parts (measured outline, few holes)
def housing(d, m, s):
    bx, by, bw, bh = m["box"]
    a = d["article"]
    if "FRAME" in a:
        s.rect(bx + s.sw / 2, by + s.sw / 2, bw - s.sw, bh - s.sw, BODY["steel"], rx=bw * .02)
        inner = comps(m["inner"] & (m["L"] > 238), 500)
        if inner:
            c = max(inner, key=lambda c: c["area"])
            s.rect(c["x"], c["y"], c["w"], c["h"], PLATE, rx=3)
        return
    if a.endswith("-ML"):
        s.rect(bx + bw * .02, by + bh * .04, bw * .96, bh * .56, BODY["black"], rx=bh * .08)
        s.rect(bx + bw * .13, by + bh * .14, bw * .74, bh * .33, PLATE, rx=4)
        for x in (.12, .78):
            s.rect(bx + bw * x, by + bh * .58, bw * .1, bh * .38, BODY["black"], rx=bw * .03)
        return
    s.rect(bx + s.sw / 2, by + s.sw / 2, bw - s.sw, bh - s.sw, BODY["black"], rx=min(bw, bh) * .05)
    filled = ndimage.binary_fill_holes(m["alpha"])
    holes = comps((filled & ~m["alpha"]) | (m["inner"] & (m["L"] > 200)), 150)
    for c in holes:
        if c["w"] > bw * .9:
            continue
        sq = abs(c["w"] - c["h"]) <= .25 * max(c["w"], c["h"])
        lab_, _ = ndimage.label((filled & ~m["alpha"]) | (m["inner"] & (m["L"] > 200)))
        y0_, x0_ = c["y"], c["x"]
        cw_, ch_ = max(2, c["w"] // 8), max(2, c["h"] // 8)
        corner = lab_[y0_:y0_ + ch_, x0_:x0_ + cw_].astype(bool).mean()
        if sq and corner < .05:
            s.circ(c["x"] + c["w"] / 2, c["y"] + c["h"] / 2, max(c["w"], c["h"]) / 2, PLATE)
        else:
            s.rect(c["x"], c["y"], c["w"], c["h"], PLATE, rx=min(c["w"], c["h"]) * .15)


# ---------------------------------------------------------------- DIN-rail modules: front panel, as in the Technik schemas
def din_front(d, s, W, H, label, kind):
    s.rect(s.sw, H * .12, W - 2 * s.sw, H * .86, BODY["white"], rx=W * .012)
    s.rect(W * .07, s.sw, W * .34, H * .14, BODY["white"], rx=W * .008)
    # vent rows
    for yy in (.2, .86):
        n = 34
        for i in range(n):
            x = W * .05 + i * (W * .9 / n)
            s.rect(x, H * yy, W * .9 / n * .5, H * .035, DARK, rx=1, stroke=None)
    s.rect(W * .5, H * .32, W * .44, H * .44, "#ffffff", rx=W * .01)
    s.text(W * .72, H * .57, label, H * .075)
    s.line(W * .08, H * .3, W * .08, H * .8, "#9a9a9a", s.sw * .8)
    if kind == "2wl":
        s.rect(W * .14, H * .4, W * .2, H * .28, DARK, rx=4)
        s.rect(W * .18, H * .46, W * .12, H * .14, "#6b7280", rx=2, stroke=None)
    s.circ(W * .56, H * .2 - H * .02, W * .012, "#dc2626", stroke=None)


CHECK = {}
MAN = []


def draw(d):
    k, a = d["kind"], d["article"]
    if a in ("EVO-HD-C5001", "EVO-HD-DL", "EVO-HD-2WL"):
        return None, None   # taken from Balter Technik's Figma drawings: scripts/figma_modules.py
        W, H = 520, 357
        s = Sk(W, H, 2.2)
        din_front(d, s, W, H, a, "2wl" if a.endswith("2WL") else "")
        return s.svg(f"{a} · {d['name']} (Skizze)"), [W, H]
    m = measure(d)
    sw = max(2.0, min(m["W"], m["H"]) * .006)
    s = Sk(m["W"], m["H"], sw)
    if a in ("EVO-QUICK-4.3M", "EVO-QUICK-BLACK", "EVO-MINI-4.3M", "EVO-TALK"):
        import touch_flat
        svg, rep = touch_flat.sketch(d)
        CHECK[a] = rep
        return svg, [m["W"], m["H"]]
    if a.startswith("EVO-AP-"):
        import ap_model
        svg, rep = ap_model.sketch(d)
        CHECK[a] = rep
        return svg, [m["W"], m["H"]]
    if k in ("video-tuerstation", "audio-tuerstation", "erweiterung") and not a.startswith("EVO-HD-TOUCH"):
        import station_model
        svg, rep = station_model.sketch(d, MAN)
        CHECK[a] = rep
        return svg, [m["W"], m["H"]]
    if k in ("monitor", "audiostation") or a.startswith("EVO-HD-TOUCH"):
        import flat_model
        svg, rep = flat_model.sketch(d, MAN)
        CHECK[a] = rep
        return svg, [m["W"], m["H"]]
    if k in ("pro-modul", "gehaeuse"):
        import pro_model
        svg, rep = pro_model.sketch(d)
        CHECK[a] = rep
        return svg, [m["W"], m["H"]]
    if k == "pro-modul":
        pro_module(d, m, s)
    elif k == "gehaeuse":
        housing(d, m, s)
    return s.svg(f"{a} · {d['name']} (Skizze)"), [m["W"], m["H"]]


def main():
    path = os.path.join(DEV, "devices.json")
    man = json.load(open(path, encoding="utf-8"))
    MAN[:] = man["devices"]
    cpath = os.path.join(DEV, "sketch-check.json")
    if os.path.exists(cpath):
        CHECK.update(json.load(open(cpath)))
    only = {x.upper() for x in sys.argv[1:]}
    n = 0
    for d in man["devices"]:
        if only and d["article"].upper() not in only:
            continue
        svg, size = draw(d)
        if svg is None:
            continue
        fn = d["image"].rsplit(".", 1)[0] + ".svg"
        open(os.path.join(DEV, fn), "w", encoding="utf-8").write(svg)
        d["vector"] = fn
        d["vector_px"] = size
        n += 1
    json.dump(man, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    json.dump(CHECK, open(cpath, "w"), indent=1)
    for a_, r_ in CHECK.items():
        print(f"{a_:24} mean {r_['mean']:.2f}px  worst {r_['worst'][0]} {r_['worst'][1]:.2f}px  logo {r_['logo']}")
    print(n, "sketches")


if __name__ == "__main__":
    main()
