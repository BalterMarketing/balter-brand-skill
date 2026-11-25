#!/usr/bin/env python3
"""
Fit a technical sketch onto the real photo, then prove it fits.

1. Edges: the photo is smoothed along the brushing (horizontal), then Canny finds the real outlines.
2. Elements: every closed outline becomes one element; its shape is classified (circle, pill,
   rectangle) and drawn as that clean shape on the outline's exact bounds.
3. Tone from the photo inside the element: black (camera, status bar, glass), white (name plates),
   body grey (buttons, tabs, slots); buttons get their centre dot.
4. Check: every drawn outline is compared with the photo's edges (chamfer distance). The script prints
   the mean and the worst element in pixels and writes an overlay (sketch in red over the photo).

    python3 scripts/sketch_fit.py EVO-HD-4FAM [--overlay out.png]
"""
import json
import os
import sys

import cv2
import numpy as np
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
DEV = os.path.normpath(os.path.join(HERE, "..", "assets", "devices"))
INK, DARK, PLATE = "#111111", "#111111", "#FFFFFF"
BODY = {"steel": "#D9D9D9", "white": "#F2F2F2", "black": "#3A3A3A"}


def edges_of(img, alpha):
    g = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gs = cv2.bilateralFilter(cv2.blur(g, (9, 1)), 9, 30, 9)
    e = cv2.Canny(gs, 35, 90)
    inner = cv2.erode(alpha.astype(np.uint8), np.ones((9, 9))) > 0
    e[~inner] = 0
    return e, g


def elements(e, g, alpha, W, H):
    closed = cv2.morphologyEx(e, cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8), iterations=2) > 0
    filled = ndimage.binary_fill_holes(closed)
    lab, n = ndimage.label(filled)
    out = []
    for i, sl in enumerate(ndimage.find_objects(lab), 1):
        comp = lab[sl] == i
        area = comp.sum()
        h, w = comp.shape
        if area < 60 or w > W * .9 or h > H * .9:
            continue
        y0, x0 = sl[0].start, sl[1].start
        cs, _ = cv2.findContours(comp.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        c = max(cs, key=cv2.contourArea)
        per = cv2.arcLength(c, True)
        circ = 4 * np.pi * cv2.contourArea(c) / (per * per + 1e-6)
        fill = area / float(w * h)
        inside = g[sl][comp]
        out.append(dict(x=x0, y=y0, w=w, h=h, area=int(area), fill=fill, circ=circ, L=float(np.median(inside)),
                        thin=False))
    return out


def lines_of(e, els, W):
    """Horizontal strokes that are not closed outlines (microphone grille)."""
    ls = cv2.HoughLinesP(e, 1, np.pi / 180, 30, minLineLength=W * .08, maxLineGap=4)
    res = []
    if ls is None:
        return res
    for x1, y1, x2, y2 in ls.reshape(-1, 4):
        if abs(y2 - y1) > 2:
            continue
        inside = any(el["x"] - 2 <= min(x1, x2) and max(x1, x2) <= el["x"] + el["w"] + 2 and el["y"] - 2 <= y1 <= el["y"] + el["h"] + 2 for el in els)
        if not inside:
            res.append((min(x1, x2), (y1 + y2) / 2, max(x1, x2)))
    # merge near-duplicates (both edges of one stroke)
    res.sort(key=lambda r: (round(r[1] / 4), r[0]))
    merged = []
    for r in res:
        if merged and abs(merged[-1][1] - r[1]) <= 3 and r[0] <= merged[-1][2] + 6:
            m = merged[-1]
            merged[-1] = (min(m[0], r[0]), (m[1] + r[1]) / 2, max(m[2], r[2]))
        else:
            merged.append(r)
    return merged


LOGO = os.path.normpath(os.path.join(HERE, "..", "assets", "logo", "balter-logo-quer-black.svg"))


def logo_svg(box, colour):
    """The real BALTER logo (eagle + wordmark), upright like on the plate, fitted into box."""
    import re as _re
    src = open(LOGO, encoding="utf-8").read()
    vb = [float(v) for v in _re.search(r'viewBox="([^"]+)"', src).group(1).split()]
    inner = _re.search(r"<g[^>]*id=\"Layer_1-2\"[^>]*>(.*)</g>\s*</svg>", src, _re.S)
    body = inner.group(1) if inner else _re.search(r"<svg[^>]*>(.*)</svg>", src, _re.S).group(1)
    body = _re.sub(r'class="cls-2"', f'fill="{colour}" fill-rule="evenodd"', body)
    body = _re.sub(r'class="cls-1"', f'fill="{colour}"', body)
    x, y, w, h = box
    # rotated -90: the logo's width runs along the box height (reads bottom to top)
    sc = min(h / vb[2], w / vb[3])
    return (f'<g transform="translate({x + (w - vb[3] * sc) / 2:.2f} {y + h - (h - vb[2] * sc) / 2:.2f}) rotate(-90) scale({sc:.4f})">{body}</g>')


def material_of(d):
    a, k, col = d["article"], d["kind"], d.get("colour", "")
    if col == "schwarz":
        return "black"
    if col == "weiß":
        return "white"
    return "steel"


def fit(d, overlay=None, ctx=False):
    img4 = cv2.imread(os.path.join(DEV, d["image"]), cv2.IMREAD_UNCHANGED)
    alpha = img4[..., 3] > 40
    img = img4[..., :3]
    H, W = alpha.shape
    e, g = edges_of(img, alpha)
    els = elements(e, g, alpha, W, H)
    mat = material_of(d)
    sw = max(2.0, min(W, H) * .006)
    ys, xs = np.nonzero(alpha)
    bx, by, bw, bh = xs.min(), ys.min(), xs.max() - xs.min() + 1, ys.max() - ys.min() + 1
    body_L = float(np.median(g[alpha]))
    shapes = []   # (kind, params, fill)
    shapes.append(("rect", (bx + sw / 2, by + sw / 2, bw - sw, bh - sw, bw * .015), BODY[mat], "body"))
    # camera: dark core in the upper part, ring found by radial search for the outer edge
    cam = None
    top = np.zeros_like(alpha); top[:int(by + bh * .35)] = True
    core = ndimage.label(alpha & top & (g < 60))[0]
    if core.max() and d["kind"] == "video-tuerstation":
        sizes = ndimage.sum(np.ones_like(core), core, range(1, core.max() + 1))
        for j, sl_ in enumerate(ndimage.find_objects(core)):
            hh_, ww_ = sl_[0].stop - sl_[0].start, sl_[1].stop - sl_[1].start
            if not (.7 <= ww_ / max(hh_, 1) <= 1.4) or ww_ > bw * .22:
                sizes[j] = 0          # only round dark blobs can be the lens
        k = int(np.argmax(sizes)) + 1
        if sizes[k - 1] > 80:
            cy, cx = ndimage.center_of_mass(core == k)
            r0 = np.sqrt(sizes[k - 1] / np.pi)
            radii = []
            for ang in np.linspace(0, 2 * np.pi, 72, endpoint=False):
                rr = []
                for r in np.arange(r0, r0 * 3.2, .5):
                    xx, yy = int(round(cx + r * np.cos(ang))), int(round(cy + r * np.sin(ang)))
                    if 0 <= xx < W and 0 <= yy < H and e[yy, xx]:
                        rr.append(r)
                if rr:
                    radii.append(max(rr))
            if radii:
                R = float(np.median(radii))
                if R < bw * .2:
                    cam = (cx, cy, R)
                    shapes.append(("circle", (cx, cy, R), DARK, "lens"))
                    shapes.append(("circle", (cx, cy, r0 * .6), "#6b7280", "lens-inner"))
    # BALTER logo on the plate: the upright text block at the lower right
    logo = None
    reg = np.zeros_like(alpha); reg[int(by + bh * .7):, int(bx + bw * .82):] = True
    blobs = ndimage.label(cv2.dilate(((e > 0) & reg).astype(np.uint8), np.ones((7, 7))) > 0)[0]
    best = None
    for sl_ in ndimage.find_objects(blobs) or []:
        hh_, ww_ = sl_[0].stop - sl_[0].start, sl_[1].stop - sl_[1].start
        if hh_ > 2.5 * ww_ and hh_ > bh * .04 and (best is None or hh_ > best[3]):
            best = (sl_[1].start + 3, sl_[0].start + 3, ww_ - 6, hh_ - 6)
    logo = best
    # keep the outer outline only: drop elements that sit inside a larger one of similar size
    keep = []
    for el in sorted(els, key=lambda el: -el["w"] * el["h"]):
        inside = any(o["x"] - 4 <= el["x"] and o["y"] - 4 <= el["y"] and el["x"] + el["w"] <= o["x"] + o["w"] + 4
                     and el["y"] + el["h"] <= o["y"] + o["h"] + 4 and el["w"] * el["h"] > .45 * o["w"] * o["h"] for o in keep)
        if not inside:
            keep.append(el)
    els = keep
    plates_h = [el["h"] for el in els if el["w"] > 2.4 * el["h"] and el["L"] > body_L - 5 and el["w"] > bw * .2]
    ph = float(np.median(plates_h)) if plates_h else 0
    for el in sorted(els, key=lambda el: -el["area"]):
        if cam and (el["x"] - cam[0]) ** 2 + (el["y"] - cam[1]) ** 2 < (cam[2] * 1.2) ** 2 and el["w"] < cam[2] * 2.2:
            continue
        if cam and abs(el["x"] + el["w"] / 2 - cam[0]) < cam[2] and abs(el["y"] + el["h"] / 2 - cam[1]) < cam[2]:
            continue
        if logo and el["x"] >= logo[0] - 3 and el["y"] >= logo[1] - 3 and el["x"] + el["w"] <= logo[0] + logo[2] + 3:
            continue
        x, y, w, h = el["x"], el["y"], el["w"], el["h"]
        sq = abs(w - h) <= .15 * max(w, h)
        dark = el["L"] < min(80, body_L - 40)
        bright = el["L"] > max(215, body_L + 12)
        if dark and sq and w > bw * .2:                                    # glass block: RFID / fingerprint
            shapes.append(("rect", (x, y, w, h, min(w, h) * .05), DARK, "dark"))
            ring = [c for c in els if c is not el and c["x"] > x and c["y"] > y and c["x"] + c["w"] < x + w
                    and c["y"] + c["h"] < y + h and abs(c["w"] - c["h"]) <= .2 * c["w"] and c["w"] > w * .2]
            if ring:
                c = max(ring, key=lambda c: c["w"])
                shapes.append(("circle", (c["x"] + c["w"] / 2, c["y"] + c["h"] / 2, c["w"] / 2), "#262626", "ring"))
            continue
        if dark and sq and w > bw * .2:
            continue
        if sq and ph and .6 * ph <= w <= 1.7 * ph and not dark:              # call button next to a plate
            r = (w + h) / 4
            shapes.append(("circle", (x + w / 2, y + h / 2, r), BODY[mat] if mat != "black" else "#2a2a2a", "button"))
            shapes.append(("dot", (x + w / 2, y + h / 2, r * .16), INK, "button-dot"))
            continue
        if sq and el["circ"] > .78:
            r = (w + h) / 4
            if dark:
                shapes.append(("circle", (x + w / 2, y + h / 2, r), DARK, "lens"))
                shapes.append(("circle", (x + w / 2, y + h / 2, r * .3), "#6b7280", "lens-inner"))
            else:
                shapes.append(("circle", (x + w / 2, y + h / 2, r), BODY[mat] if mat != "black" else "#2a2a2a", "button"))
                shapes.append(("dot", (x + w / 2, y + h / 2, r * .16), INK, "button-dot"))
        else:
            pill = w > 2.2 * h and h < W * .12 and w < W * .45
            rx = h / 2 if pill and w < W * .3 else min(w, h) * .1
            fill = DARK if dark else (PLATE if bright else ("#F5F5F5" if pill else BODY[mat]))
            role = "dark" if dark else ("plate" if bright else ("slot" if pill else "part"))
            shapes.append(("rect", (x, y, w, h, rx), fill, role))
    # every plate has its call button to the right: find any that the outlines missed
    plates = [sh for sh in shapes if sh[3] == "plate"]
    buttons = [sh for sh in shapes if sh[3] == "button"]
    gb = cv2.GaussianBlur(g, (5, 5), 1.2)
    for _, (x, y, w, h, rx), _, _ in plates:
        cy = y + h / 2
        if any(abs(b[1][1] - cy) < h * .6 and x + w <= b[1][0] <= x + w + h * 2.4 for b in buttons):
            continue
        x0, x1 = int(x + w), int(min(W - 1, x + w + h * 2.4))
        y0, y1 = int(max(0, cy - h)), int(min(H - 1, cy + h))
        roi = gb[y0:y1, x0:x1]
        if roi.size < 50:
            continue
        cc = cv2.HoughCircles(roi, cv2.HOUGH_GRADIENT, dp=1, minDist=h, param1=80, param2=12,
                              minRadius=int(h * .3), maxRadius=int(h * .8))
        if cc is not None:
            ccx, ccy, rr = cc[0][0]
            shapes.append(("circle", (x0 + ccx, y0 + ccy, rr), BODY[mat] if mat != "black" else "#2a2a2a", "button"))
            shapes.append(("dot", (x0 + ccx, y0 + ccy, rr * .16), INK, "button-dot"))
    # thin strokes inside a plate are its glass edge, not a part
    shapes = [sh for sh in shapes if not (sh[0] == "rect" and sh[3] in ("part", "slot") and sh[1][3] < 7 and any(
        p[1][0] - 3 <= sh[1][0] and sh[1][0] + sh[1][2] <= p[1][0] + p[1][2] + 3 and p[1][1] - 3 <= sh[1][1] <= p[1][1] + p[1][3] + 3 for p in plates))]
    for x1, yy, x2 in lines_of(e, els, W):
        shapes.append(("line", (x1, yy, x2), INK, "line"))
    # ---- check against the photo's edges
    dist = cv2.distanceTransform((e == 0).astype(np.uint8), cv2.DIST_L2, 3)
    errs = []
    for kind, p, fill, role in shapes[1:]:
        m = np.zeros((H, W), np.uint8)
        if kind == "rect":
            x, y, w, h, rx = p
            cv2.rectangle(m, (int(round(x)), int(round(y))), (int(round(x + w - 1)), int(round(y + h - 1))), 1, 1)
        elif kind in ("circle",):
            cv2.circle(m, (int(round(p[0])), int(round(p[1]))), int(round(p[2])), 1, 1)
        else:
            continue
        pts = dist[m > 0]
        if pts.size and role != "lens-inner":
            errs.append((role, float(np.median(pts))))
    mean_err = float(np.mean([e_ for _, e_ in errs])) if errs else 0.0
    worst = max(errs, key=lambda t: t[1]) if errs else ("-", 0.0)
    # ---- svg
    o = []
    for kind, p, fill, role in shapes:
        if kind == "rect":
            x, y, w, h, rx = p
            o.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx:.1f}" fill="{fill}" stroke="{INK}" stroke-width="{sw:.1f}"/>')
        elif kind == "circle":
            st = "" if role == "lens-inner" else f' stroke="{INK}" stroke-width="{sw:.1f}"'
            o.append(f'<circle cx="{p[0]:.1f}" cy="{p[1]:.1f}" r="{p[2]:.1f}" fill="{fill}"{st}/>')
        elif kind == "dot":
            o.append(f'<circle cx="{p[0]:.1f}" cy="{p[1]:.1f}" r="{p[2]:.1f}" fill="{fill}"/>')
        elif kind == "line":
            o.append(f'<path d="M{p[0]:.1f} {p[1]:.1f}H{p[2]:.1f}" stroke="{INK}" stroke-width="{sw:.1f}" stroke-linecap="round"/>')
    if logo:
        o.append(logo_svg(logo, "#111111" if mat != "black" else "#E5E5E5"))
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" '
           f'aria-label="{d["article"]} · {d["name"]} (Skizze)">' + "".join(o) + "</svg>")
    if overlay:
        ov = cv2.cvtColor(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY), cv2.COLOR_GRAY2BGR)
        ov = cv2.addWeighted(ov, .55, np.full_like(ov, 255), .45, 0)
        for kind, p, fill, role in shapes:
            col = (0, 0, 230)
            if kind == "rect":
                x, y, w, h, rx = p
                cv2.rectangle(ov, (int(round(x)), int(round(y))), (int(round(x + w - 1)), int(round(y + h - 1))), col, 1)
            elif kind == "circle":
                cv2.circle(ov, (int(round(p[0])), int(round(p[1]))), int(round(p[2])), col, 1)
            elif kind == "line":
                cv2.line(ov, (int(p[0]), int(p[1])), (int(p[2]), int(p[1])), col, 1)
        cv2.imwrite(overlay, ov)
    rep = dict(mean=round(mean_err, 2), worst=[worst[0], round(worst[1], 2)], n=len(shapes) - 1, logo=bool(logo))
    if ctx:
        return svg, rep, dict(shapes=shapes, logo=logo, img=img, g=g, e=e, alpha=alpha, box=(bx, by, bw, bh), mat=mat, sw=sw, W=W, H=H)
    return svg, rep


if __name__ == "__main__":
    man = json.load(open(os.path.join(DEV, "devices.json"), encoding="utf-8"))
    art = sys.argv[1].upper()
    ov = sys.argv[3] if len(sys.argv) > 3 and sys.argv[2] == "--overlay" else None
    d = next(x for x in man["devices"] if x["article"].upper() == art)
    svg, rep = fit(d, ov)
    print(art, rep)
