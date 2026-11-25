#!/usr/bin/env python3
"""
Flat touch indoor units of the EVO (analog) line — EVO-QUICK-4.3M, EVO-QUICK-BLACK, EVO-MINI-4.3M and
EVO-TALK — as technical sketches.

Their front is one flat glass face: a screen (QUICK, MINI) and printed touch symbols. The screen is the
textured region on the plain face; every printed symbol is found as its own mark on the photo and kept
in its own shape (simplified contour), like the label text of the DIN modules; the BALTER logo is the
real logo, horizontal, where it sits. Three tones, one outline, checked against the photo's edges.

    python3 scripts/touch_flat.py EVO-QUICK-4.3M
"""
import os
import sys

import cv2
import numpy as np
from scipy import ndimage

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import flat_model as FM  # noqa: E402
import icon_library as IL  # noqa: E402
import sketch_fit as F  # noqa: E402

REUSE = True
INK = "#111111"
BODY = {"white": "#F2F2F2", "black": "#3A3A3A"}


def model(d):
    img, alpha, g, box = FM.load(d)
    bx, by, bw, bh = box
    black = F.material_of(d) == "black"
    inner = cv2.erode(alpha.astype(np.uint8), np.ones((15, 15))) > 0
    mx, my = int(bw * .035), int(bh * .03)
    face = np.zeros_like(inner)
    face[by + my:by + bh - my, bx + mx:bx + bw - mx] = True
    inner &= face
    body_L = float(np.median(g[inner]))
    # screen: where the face stops being plain (texture or colour)
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    std = np.sqrt(np.maximum(cv2.blur((g.astype(float) - cv2.blur(g.astype(float), (9, 9))) ** 2, (9, 9)), 0))
    busy = ((hsv[..., 1] > 40) | (std > 9)) & inner
    busy = cv2.morphologyEx(busy.astype(np.uint8), cv2.MORPH_CLOSE, np.ones((25, 25))) > 0
    screen = None
    lab, n = ndimage.label(busy)
    if n:
        s = ndimage.sum(busy, lab, range(1, n + 1))
        k = int(np.argmax(s))
        if s[k] > bw * bh * .08:
            sl = ndimage.find_objects(lab)[k]
            screen = (sl[1].start, sl[0].start, sl[1].stop - sl[1].start, sl[0].stop - sl[0].start)
    if screen:   # refine each side to the strongest edge nearby
        x, y, w, h = screen
        gx = np.abs(cv2.Sobel(g.astype(float), cv2.CV_64F, 1, 0, ksize=3))
        gy = np.abs(cv2.Sobel(g.astype(float), cv2.CV_64F, 0, 1, ksize=3))
        def best(prof, c):
            lo = max(0, c - 16)
            return lo + int(np.argmax(prof[lo:c + 17]))
        ys_, xs_ = slice(y + h // 4, y + 3 * h // 4), slice(x + w // 4, x + 3 * w // 4)
        x0 = best(gx[ys_].mean(0), x); x1 = best(gx[ys_].mean(0), x + w)
        y0 = best(gy[:, xs_].mean(1), y); y1 = best(gy[:, xs_].mean(1), y + h)
        screen = (x0, y0, x1 - x0, y1 - y0)
    # step: the seam of a lower face part, a strong full-width horizontal edge in the bottom fifth
    step = None
    gyy = np.abs(cv2.Sobel(g.astype(float), cv2.CV_64F, 0, 1, ksize=3))[:, bx + int(bw * .1):bx + int(bw * .9)].mean(1)
    y_lo, y_hi = by + int(bh * .78), by + bh - int(bh * .02)
    if y_hi > y_lo:
        k = y_lo + int(np.argmax(gyy[y_lo:y_hi]))
        if gyy[k] > 6 * np.median(gyy[by:by + bh]) and gyy[k] > 8:
            step = k
    # logo: lower part of the face
    logo = FM.logo_in(g, alpha, (bx + bw * .02, by + bh * .7, bx + bw * .85, by + bh * .97), body_L)
    # printed marks: contrasting blobs outside screen and logo
    boost = screen is not None and not black     # faint print on a white monitor face
    ge = cv2.createCLAHE(2.5, (8, 8)).apply(g) if boost else g
    bg = cv2.medianBlur(ge, 41).astype(int)
    m = (np.abs(ge.astype(int) - bg) > (22 if black else 16 if boost else 13)) & inner
    if boost:
        m = cv2.morphologyEx(m.astype(np.uint8), cv2.MORPH_CLOSE, np.ones((5, 5))) > 0
    if step:
        m[step - 4:step + 5] = False
    if screen:
        x, y, w, h = screen
        m[max(0, y - 6):y + h + 6, max(0, x - 6):x + w + 6] = False
    if logo:
        x, y, w, h = logo
        m[y - 8:y + h + 8, max(0, int(x - h * 2.2)):x + w + 14] = False
    m = cv2.morphologyEx(m.astype(np.uint8), cv2.MORPH_OPEN, np.ones((2, 2)))
    # each printed symbol: found here, then traced enlarged from the photo (smooth, true shape and place)
    kk = max(9, int(bw * .028)) | 1           # pieces of one faint symbol belong together
    grp = cv2.dilate(m.astype(np.uint8), np.ones((kk, kk)))
    lab, n = ndimage.label(grp)
    marks = []
    for i, sl in enumerate(ndimage.find_objects(lab) or [], 1):
        ink = (m[sl] > 0) & (lab[sl] == i)
        a = int(ink.sum())
        y, x = sl[0].start, sl[1].start
        h, w = sl[0].stop - y, sl[1].stop - x
        if a < (25 if boost else 12) or w * h > bw * bh * .03 or w > bw * .5:
            continue
        pad = 8
        lightmark = black or float((ge[sl].astype(int) - bg[sl])[ink].mean()) > 0   # white print on a white face
        t = F.trace_icon(ge, (x - pad, y - pad, w + 2 * pad, h + 2 * pad), light=lightmark, tophat=True, level=.4)
        if t:
            marks.append(t)
    # traced pieces whose boxes touch are one symbol (a handset and its sound waves)
    merged = True
    while merged:
        merged = False
        for i in range(len(marks)):
            for j in range(i + 1, len(marks)):
                a_, b_ = IL.bbox(IL.polys_of(marks[i])), IL.bbox(IL.polys_of(marks[j]))
                if a_[0] - kk < b_[0] + b_[2] and b_[0] - kk < a_[0] + a_[2] and a_[1] - kk < b_[1] + b_[3] and b_[1] - kk < a_[1] + a_[3]:
                    marks[i] = marks[i] + " " + marks.pop(j)
                    merged = True
                    break
            if merged:
                break
    if REUSE:         # the same icon as on another device: the library drawing, placed in the box found here
        marks = [IL.reuse(t, .5)[0] for t in marks]
    # rings round the touch keys (faint grey outlines)
    rings = []
    face = ge.copy()
    if screen:
        x, y, w, h = screen
        face[max(0, y - 10):y + h + 10, max(0, x - 10):x + w + 10] = int(np.median(ge[inner]))
    cs = cv2.HoughCircles(cv2.GaussianBlur(face, (5, 5), 1.5), cv2.HOUGH_GRADIENT, 1.2, bw * .12, param1=60, param2=28,
                          minRadius=int(bw * .04), maxRadius=int(bw * .075))
    if cs is not None:
        for cx, cy, r in cs[0]:
            if not (bx + bw * .05 < cx < bx + bw * .95 and by + bh * .05 < cy < by + bh * .95):
                continue
            ang = np.linspace(0, 2 * np.pi, 90, endpoint=False)
            on = ge[np.clip((cy + r * np.sin(ang)).astype(int), 0, ge.shape[0] - 1), np.clip((cx + r * np.cos(ang)).astype(int), 0, ge.shape[1] - 1)].astype(int)
            off = ge[np.clip((cy + r * 1.25 * np.sin(ang)).astype(int), 0, ge.shape[0] - 1), np.clip((cx + r * 1.25 * np.cos(ang)).astype(int), 0, ge.shape[1] - 1)].astype(int)
            if np.mean(np.abs(on - off) > 6) > .6:
                rings.append((float(cx), float(cy), float(r)))
    # a key in the same column as a found ring has the same ring
    import icon_library as _IL
    for cx, cy, r in list(rings):
        for t in marks:
            x, y, w, h = _IL.bbox(_IL.polys_of(t))
            mx, my = x + w / 2, y + h / 2
            if abs(mx - cx) < r * .4 and abs(my - cy) > r * 1.5 and max(w, h) < r * 1.6 \
                    and not any(np.hypot(mx - a, my - b) < c for a, b, c in rings):
                rings.append((cx, my, r))
    return dict(article=d["article"], name=d["name"], W=g.shape[1], H=g.shape[0], box=box, black=black,
                rx=FM.corner_r(alpha, box), screen=screen, step=step, rings=rings, logo=logo, marks=marks, g=g, alpha=alpha)


def _d(c):
    c = cv2.approxPolyDP(c, 0.7, True).reshape(-1, 2)
    return "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in c) + "Z"


def render(m):
    W, H = m["W"], m["H"]
    bx, by, bw, bh = m["box"]
    sw = max(2.0, min(W, H) * .006)
    body = BODY["black" if m["black"] else "white"]
    mark = "#D4D4D4" if m["black"] else "#6b6b6b"
    o = [f'<rect x="{bx + sw / 2:.1f}" y="{by + sw / 2:.1f}" width="{bw - sw:.1f}" height="{bh - sw:.1f}" rx="{max(m["rx"], bw * .01):.1f}" '
         f'fill="{body}" stroke="{INK}" stroke-width="{sw:.1f}"/>']
    if m["screen"]:
        x, y, w, h = m["screen"]
        o.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="2" fill="#111111" stroke="{INK}" stroke-width="{sw:.1f}"/>')
    if m.get("step"):
        o.append(f'<line x1="{bx + sw:.1f}" y1="{m["step"]:.1f}" x2="{bx + bw - sw:.1f}" y2="{m["step"]:.1f}" stroke="{INK}" stroke-width="{sw * .7:.1f}"/>')
    for cx, cy, r in m.get("rings", []):
        o.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="none" stroke="{mark}" stroke-width="{sw * .6:.1f}"/>')
    for path in m["marks"]:
        o.append(f'<path d="{path}" fill="{mark}" fill-rule="evenodd"/>')
    if m["logo"]:
        o.append(FM.logo_h(m["logo"], "#E5E5E5" if m["black"] else "#111111"))
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" '
            f'aria-label="{m["article"]} · {m["name"]} (Skizze)">' + "".join(o) + "</svg>")


def check(m):
    g = cv2.GaussianBlur(m["g"], (3, 3), 0)
    e = cv2.Canny(g, 30, 90)
    a = m["alpha"].astype(np.uint8)
    e |= (cv2.morphologyEx(a, cv2.MORPH_GRADIENT, np.ones((3, 3))) > 0).astype(np.uint8) * 255
    H, W = e.shape
    e[0, :] = e[-1, :] = e[:, 0] = e[:, -1] = 255     # a full-bleed cut-out ends at the image edge
    dist = cv2.distanceTransform((e == 0).astype(np.uint8), cv2.DIST_L2, 3)
    errs = []
    for role, b in (("body", m["box"]), ("screen", m["screen"])):
        if not b:
            continue
        mk = np.zeros((H, W), np.uint8)
        x, y, w, h = [int(round(v)) for v in b]
        cv2.rectangle(mk, (x, y), (x + w - 1, y + h - 1), 1, 1)
        errs.append((role, float(np.median(dist[mk > 0]))))
    mean = float(np.mean([v for _, v in errs]))
    worst = max(errs, key=lambda t: t[1])
    return dict(mean=round(mean, 2), worst=[worst[0], round(worst[1], 2)], parts=dict(marks=len(m["marks"])), logo=bool(m["logo"]))


def sketch(d, man=None):
    m = model(d)
    return render(m), check(m)
