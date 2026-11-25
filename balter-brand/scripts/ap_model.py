#!/usr/bin/env python3
"""
EVO Aufputz door stations (EVO-AP-*) as technical sketches.

Their front is not the EVO / EVO HD plate: a black glass block with the camera and the IR light at the
top, a white name field below it (one row per call button, the buttons in their own column on the
right) and the BALTER logo upright beside the field. Each part is found on the photo and drawn with one
symbol, in the same three tones and with the same chamfer check as station_model.py.

    python3 scripts/ap_model.py EVO-AP-4FAM
"""
import os
import sys

import cv2
import numpy as np
from scipy import ndimage

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sketch_fit as F  # noqa: E402
import station_model as S  # noqa: E402

INK, DARK, BODY = "#111111", "#111111", "#D9D9D9"


def bbox(mask):
    ys, xs = np.nonzero(mask)
    return (int(xs.min()), int(ys.min()), int(xs.max() - xs.min() + 1), int(ys.max() - ys.min() + 1))


def largest(mask):
    lab, n = ndimage.label(mask)
    if not n:
        return None
    s = ndimage.sum(mask, lab, range(1, n + 1))
    return lab == 1 + int(np.argmax(s))


def model(d):
    img, alpha, g, e, box = S.load(d)
    bx, by, bw, bh = box
    inner = cv2.erode(alpha.astype(np.uint8), np.ones((7, 7))) > 0
    gl = largest(cv2.morphologyEx(((g < 55) & inner).astype(np.uint8), cv2.MORPH_OPEN, np.ones((5, 5))) > 0)
    glass = bbox(gl)
    gx, gy, gw, gh = glass
    parts = [dict(t="glass", b=glass)]
    # camera: centre from the lens (Hough), radius where the lighter housing ends (radial profile)
    sub = cv2.GaussianBlur(g[gy:gy + gh, gx:gx + gw], (5, 5), 1.5)
    cs = cv2.HoughCircles(sub, cv2.HOUGH_GRADIENT, 1.2, gw, param1=80, param2=25,
                          minRadius=int(gw * .06), maxRadius=int(gw * .26))
    cam = None
    if cs is not None:
        cx, cy, r0 = cs[0][0]
        cx, cy = gx + cx, gy + cy
        glass_L = float(np.median(g[gy:gy + gh, gx:gx + gw]))
        yy, xx = np.mgrid[0:g.shape[0], 0:g.shape[1]]
        rr = np.hypot(xx - cx, yy - cy)
        r = r0
        seen = False
        for k in np.arange(r0 * .8, gw * .35, 1.0):
            ring = (rr >= k) & (rr < k + 1.5)
            if g[ring].mean() > glass_L + 12:
                r, seen = k, True
            elif seen:
                break
        cam = (cx, cy, r)
        parts.append(dict(t="camera", c=(cx, cy), r=float(r)))
    # IR light: the lighter bar below the camera
    if cam:
        y0 = int(cam[1] + cam[2] * 1.2)
        band = g[y0:gy + gh - 4, gx:gx + gw].astype(int)
        m = band > np.median(band) + 4
        m = cv2.morphologyEx(m.astype(np.uint8), cv2.MORPH_CLOSE, np.ones((5, 15))) > 0
        lab, n = ndimage.label(m)
        best = None
        for sl in ndimage.find_objects(lab) or []:
            h_, w_ = sl[0].stop - sl[0].start, sl[1].stop - sl[1].start
            if w_ > 4 * h_ and w_ > gw * .3 and (best is None or w_ > best[2]):
                best = (gx + sl[1].start, y0 + sl[0].start, w_, h_)
        if best:
            x, y, w, h = best
            h = max(h, gw * .045)
            parts.append(dict(t="ir", b=(x, y + best[3] / 2 - h / 2, w, h)))
    # white name field below the glass
    below = np.zeros_like(alpha)
    below[gy + gh + 4:, :] = True
    fm = largest(cv2.morphologyEx(((g > 205) & inner & below).astype(np.uint8), cv2.MORPH_CLOSE, np.ones((9, 9))) > 0)
    fx, fy, fw, fh = bbox(ndimage.binary_fill_holes(fm))
    field = (fx, fy, fw, fh)
    # call buttons in the right part of the field
    reg = cv2.GaussianBlur(g[fy:fy + fh, fx + int(fw * .55):fx + fw], (5, 5), 1.5)
    cs = cv2.HoughCircles(reg, cv2.HOUGH_GRADIENT, 1.2, fw * .12, param1=80, param2=22,
                          minRadius=int(fw * .06), maxRadius=int(fw * .16))
    buttons = []
    if cs is not None:
        rr = np.median(cs[0][:, 2])
        for cx, cy, r in cs[0]:
            if abs(r - rr) < rr * .2:
                buttons.append((fx + int(fw * .55) + float(cx), fy + float(cy), float(rr)))
    buttons.sort(key=lambda b: b[1])
    n = max(1, len(buttons))
    # button column: the strongest vertical edge between the names and the buttons
    left_btn = min((b[0] - b[2] for b in buttons), default=fx + fw * .75)
    sx = np.abs(cv2.Sobel(g[fy + 4:fy + fh - 4].astype(float), cv2.CV_64F, 1, 0, ksize=3)).mean(0)
    lo, hi = int(fx + fw * .5), int(left_btn - 2)
    colx = lo + int(np.argmax(sx[lo:hi])) if hi > lo + 2 else int(left_btn - fw * .04)
    # row separators in the name area
    sy = np.abs(cv2.Sobel(g[fy:fy + fh, fx + 6:colx - 6].astype(float), cv2.CV_64F, 0, 1, ksize=3)).mean(1)
    seps = []
    if n > 1:
        order = np.argsort(-sy)
        for y in order:
            if y < fh * .05 or y > fh * .95:
                continue
            if all(abs(y - s) > fh / (n * 1.6) for s in seps):
                seps.append(int(y))
            if len(seps) == n - 1:
                break
        seps = sorted(fy + s for s in seps)
    # logo: the printed letters right of the name field, darker than the grey body
    x0, x1 = fx + fw + 3, int(bx + bw - bw * .03)
    logo = None
    if x1 > x0 + 4:
        zone = g[fy:fy + fh, x0:x1].astype(int)
        lm = (zone < np.median(zone) - 30).astype(np.uint8)
        lm = cv2.dilate(lm, np.ones((9, 3)))
        lab, n = ndimage.label(lm)
        best = None
        for sl in ndimage.find_objects(lab) or []:
            h_, w_ = sl[0].stop - sl[0].start, sl[1].stop - sl[1].start
            if h_ > 2.2 * w_ and h_ > bh * .03 and (best is None or h_ > best[3]):
                best = (x0 + sl[1].start + 1, fy + sl[0].start + 4, w_ - 2, h_ - 8)
        logo = best
    return dict(article=d["article"], name=d["name"], W=g.shape[1], H=g.shape[0], box=box, parts=parts,
                field=field, colx=colx, seps=seps, buttons=buttons, logo=logo, e=e, alpha=alpha)


def render(m):
    W, H = m["W"], m["H"]
    bx, by, bw, bh = m["box"]
    sw = max(2.0, min(W, H) * .006)
    o = []
    R = lambda x, y, w, h, rx, fill, stroke=INK, s=sw: o.append(  # noqa: E731
        f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx:.1f}" fill="{fill}"'
        + (f' stroke="{stroke}" stroke-width="{s:.1f}"' if stroke else "") + "/>")
    C = lambda x, y, r, fill, stroke=INK, s=sw: o.append(  # noqa: E731
        f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" fill="{fill}"' + (f' stroke="{stroke}" stroke-width="{s:.1f}"' if stroke else "") + "/>")
    L = lambda x1, y1, x2, y2, s=sw * .7: o.append(  # noqa: E731
        f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{INK}" stroke-width="{s:.1f}"/>')
    defs = ('<defs><pattern id="mesh" width="5" height="5" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">'
            '<path d="M0 0V5M0 0H5" stroke="#8a8a8a" stroke-width="1.2"/></pattern></defs>')
    R(bx + sw / 2, by + sw / 2, bw - sw, bh - sw, bw * .012, BODY)
    for p in m["parts"]:
        if p["t"] == "glass":
            R(*p["b"], 2, DARK)
        elif p["t"] == "camera":
            (cx, cy), r = p["c"], p["r"]
            C(cx, cy, r, "#2B2B2B", "#6b6b6b", sw * .8)
            C(cx, cy, r * .55, "#1a1a1a", "#4a4a4a", sw * .6)
            C(cx, cy, r * .26, "#6b7280", None)
            C(cx - r * .09, cy - r * .09, r * .08, "#D4D4D4", None)
        elif p["t"] == "ir":
            x, y, w, h = p["b"]
            R(x, y, w, h, h / 2, "#1F1F1F", "#4a4a4a", sw * .6)
            o.append(f'<rect x="{x + h * .25:.1f}" y="{y + h * .25:.1f}" width="{w - h * .5:.1f}" height="{h * .5:.1f}" '
                     f'rx="{h * .25:.1f}" fill="url(#mesh)"/>')
    fx, fy, fw, fh = m["field"]
    R(fx, fy, fw, fh, fw * .01, "#FFFFFF")
    R(m["colx"], fy, fx + fw - m["colx"], fh, 0, "#F2F2F2", INK, sw * .7)
    for s in m["seps"]:
        L(fx, s, m["colx"], s)
    for x, y, r in m["buttons"]:
        C(x, y, r, BODY)
        C(x, y, r * .62, "none", "#8a8a8a", sw * .5)
        C(x, y, r * .14, INK, None)
    if m["logo"]:
        o.append(F.logo_svg(m["logo"], "#111111"))
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" '
            f'aria-label="{m["article"]} · {m["name"]} (Skizze)">' + defs + "".join(o) + "</svg>")


def check(m):
    e = m["e"]
    H, W = e.shape
    dist = cv2.distanceTransform((e == 0).astype(np.uint8), cv2.DIST_L2, 3)
    errs = []

    def rect(role, b):
        mk = np.zeros((H, W), np.uint8)
        x, y, w, h = [int(round(v)) for v in b]
        cv2.rectangle(mk, (x, y), (x + w - 1, y + h - 1), 1, 1)
        errs.append((role, float(np.median(dist[mk > 0]))))

    for p in m["parts"]:
        if "b" in p:
            rect(p["t"], p["b"])
        elif p["t"] == "camera":
            mk = np.zeros((H, W), np.uint8)
            cv2.circle(mk, (int(p["c"][0]), int(p["c"][1])), int(p["r"]), 1, 1)
            errs.append(("camera", float(np.median(dist[mk > 0]))))
    rect("field", m["field"])
    for x, y, r in m["buttons"]:
        mk = np.zeros((H, W), np.uint8)
        cv2.circle(mk, (int(round(x)), int(round(y))), int(round(r)), 1, 1)
        errs.append(("button", float(np.median(dist[mk > 0]))))
    mean = float(np.mean([v for _, v in errs])) if errs else 0.0
    worst = max(errs, key=lambda t: t[1]) if errs else ("-", 0.0)
    return dict(mean=round(mean, 2), worst=[worst[0], round(worst[1], 2)],
                parts=dict(button=len(m["buttons"]), rows=len(m["seps"]) + 1), logo=bool(m["logo"]))


def sketch(d, man=None):
    m = model(d)
    return render(m), check(m)
