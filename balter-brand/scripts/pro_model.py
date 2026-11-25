#!/usr/bin/env python3
"""
EVO HD PRO modules and housings (frames, flush boxes, surface boxes, rain hood) as technical sketches.

The photos are taken straight from the front, so the method is the same as for the stations: find each
part on the photo, draw it as a clean symbol.

Modules (512 x 512 px photo, steel unless the camera module):
    seam     the grooves between the module's bands           one line across
    slot     loudspeaker slot                                 black slot
    plate    name plate / info field                          white field
    rfid     RFID block with its fingerprint window and ring  black block, sign, window, ring
    camera   camera dome, IR LEDs, the icon row               black module, dome, LED bars, icons

Housings: the outline and the openings come straight from the photo's alpha (they are the real cut
shape, simplified to a clean polygon); inner steps are drawn where a rectangular outline is found, and
round cable entries where a circle is found.
"""
import os
import sys

import cv2
import numpy as np
from scipy import ndimage

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sketch_fit as F  # noqa: E402
import station_model as S  # noqa: E402

INK = "#111111"
DARK = "#111111"
STEEL = "#D9D9D9"
BLACKB = "#3A3A3A"
LIGHT = "#D4D4D4"
GLYPH = dict(S.GLYPH, hand="M10 13V5.5a1.5 1.5 0 0 1 3 0V11 M13 10.5a1.5 1.5 0 0 1 3 0v1 M16 11.5a1.5 1.5 0 0 1 3 0V16a5 5 0 0 1-5 5h-1.5a5 5 0 0 1-4.2-2.3L5.5 15.5a1.4 1.4 0 0 1 2.3-1.6L10 16")


def load(d):
    im = cv2.imread(os.path.join(F.DEV, d["image"]), cv2.IMREAD_UNCHANGED)
    alpha = im[..., 3] > 40
    img = im[..., :3]
    return img, alpha, cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)


def bl(mask, amin=20):
    lab, n = ndimage.label(mask)
    out = []
    for i, sl in enumerate(ndimage.find_objects(lab), 1):
        a = int((lab[sl] == i).sum())
        if a >= amin:
            out.append((sl[1].start, sl[0].start, sl[1].stop - sl[1].start, sl[0].stop - sl[0].start, a))
    return out


def seams_of(g, W, H):
    gy = np.abs(cv2.Sobel(g.astype(np.float32), cv2.CV_32F, 0, 1))
    # only the margins: plates sit in the middle and their edges are not grooves
    pr = np.concatenate([gy[:, int(W * .03):int(W * .14)], gy[:, int(W * .86):int(W * .97)]], 1).mean(1)
    pk = [y for y in range(8, H - 8) if pr[y] > 200 and pr[y] == pr[y - 6:y + 7].max()]
    out = []
    for y in pk:                       # a groove gives two edges a few px apart: one line
        if out and y - out[-1][1] <= 16:
            out[-1] = (out[-1][0], y)
        else:
            out.append((y, y))
    return [(a + b) / 2 for a, b in out]


def module(d, img, alpha, g):
    H, W = g.shape
    a = d["article"]
    m = dict(kind="module", W=W, H=H, cam=a.endswith("-CAM"))
    if m["cam"]:
        top = cv2.GaussianBlur(g, (5, 5), 1.2)
        cc = cv2.HoughCircles(top, cv2.HOUGH_GRADIENT, 1, W, param1=60, param2=25, minRadius=int(W * .07), maxRadius=int(W * .16))
        m["dome"] = tuple(cc[0][0]) if cc is not None else None
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        bgr = img.astype(int)
        red = (bgr[..., 2] - np.maximum(bgr[..., 1], bgr[..., 0]) > 5)
        red[int(H * .35):] = False
        red = cv2.morphologyEx(red.astype(np.uint8), cv2.MORPH_CLOSE, np.ones((5, 9))) > 0
        m["leds"] = [b[:4] for b in bl(red, 40) if b[2] > 2 * b[3]]
        lo = g.copy()
        lo[:int(H * .72)] = 0
        lo[int(H * .95):] = 0
        th = cv2.dilate((lo > 130).astype(np.uint8), np.ones((7, 7))) > 0   # the lit icons
        icons = sorted([b for b in bl(th, 30) if 12 < b[2] < W * .1 and 12 < b[3] < W * .1], key=lambda b: b[0])
        m["icons"] = [(b[0] + b[2] / 2, b[1] + b[3] / 2, max(b[2], b[3])) for b in icons]
        hi = g.copy()
        hi[int(H * .3):] = 255
        m["dots"] = [(b[0] + b[2] / 2, b[1] + b[3] / 2, max(b[2], b[3]) / 2) for b in bl((hi < 25) & alpha, 15)
                     if b[2] < 16 and b[3] < 16 and .6 < b[2] / b[3] < 1.6]
        return m
    m["seams"] = seams_of(g, W, H)
    m["slots"] = [b[:4] for b in bl((g < 60) & alpha, 60) if b[2] > 5 * b[3] and b[3] >= 4 and b[2] < W * .5]
    br = [b for b in bl((g > 215) & alpha, 400) if W * .4 < b[2] < W * .9 and 20 < b[3] < H * .9]
    m["plates"] = [b[:4] for b in br]
    m["rfid"] = None
    dk = [b for b in bl((g < 60) & alpha, 2000) if W * .4 < b[2] < W * .95 and b[3] > H * .4]
    if dk:
        x, y, w, h, _ = dk[0]
        r = dict(b=(x, y, w, h))
        r.update(S.rfid_in(g, None, (x, y, w, h)))
        sub = g[y:y + h, x:x + w].astype(int)
        win = [b for b in bl(np.abs(sub - np.median(sub)) > 12, 400) if .7 < b[2] / b[3] < 1.4 and b[2] < w * .6 and b[1] > h * .4]
        if win:
            wx, wy, ww, wh, _ = max(win, key=lambda b: b[4])
            r["win"] = (x + wx, y + wy, ww, wh)
        m["rfid"] = r
        m["seams"] = [s for s in m["seams"] if not (y - 6 < s < y + h + 6)]
    return m


def housing(d, img, alpha, g):
    H, W = g.shape
    a8 = alpha.astype(np.uint8)
    cs, hi = cv2.findContours(a8, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_NONE)
    outer = max([c for c, h in zip(cs, hi[0]) if h[3] < 0], key=cv2.contourArea)
    holes = [c for c, h in zip(cs, hi[0]) if h[3] >= 0 and cv2.contourArea(c) > 30]
    simp = lambda c: cv2.approxPolyDP(c, 1.2, True).reshape(-1, 2)  # noqa: E731
    body_L = float(np.median(g[alpha]))
    steel = body_L > 120
    # inner steps: closed, roughly rectangular outlines inside the body
    e = cv2.Canny(cv2.GaussianBlur(g, (5, 5), 0), 18, 50)
    e[~(cv2.erode(a8, np.ones((7, 7))) > 0)] = 0
    e = cv2.morphologyEx(e, cv2.MORPH_CLOSE, np.ones((3, 3)))
    ics, ih = cv2.findContours(e, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    rects = []
    for c in ics:
        x, y, w, h = cv2.boundingRect(c)
        if w * h < W * H * .04 or w > W * .97 or h > H * .97:
            continue
        if cv2.contourArea(cv2.convexHull(c)) < .8 * w * h:
            continue
        if any(abs(x - r[0]) < 12 and abs(y - r[1]) < 12 and abs(w - r[2]) < 22 and abs(h - r[3]) < 22 for r in rects):
            continue
        if any(abs(x - hx) < 8 and abs(y - hy) < 8 and abs(w - hw) < 14 for hx, hy, hw, hh in [cv2.boundingRect(h_) for h_ in holes]):
            continue
        rects.append((x, y, w, h))
    # round parts: rings around the cable holes, and round cable entries away from the edges
    inside = cv2.distanceTransform(a8, cv2.DIST_L2, 5)
    cc = cv2.HoughCircles(cv2.GaussianBlur(g, (5, 5), 1.2), cv2.HOUGH_GRADIENT, 1, W * .08, param1=50, param2=24,
                          minRadius=int(min(W, H) * .02), maxRadius=int(min(W, H) * .12))
    centres = []
    for h_ in holes:
        mo = cv2.moments(h_)
        x, y, w, h = cv2.boundingRect(h_)
        if mo["m00"] and .8 < w / h < 1.25:
            centres.append((mo["m10"] / mo["m00"], mo["m01"] / mo["m00"], (w + h) / 4))
    circles = []
    if cc is not None:
        for x, y, r in cc[0]:
            ring = any(np.hypot(x - cx, y - cy) < 6 and r > cr * 1.25 for cx, cy, cr in centres)
            free = inside[int(y), int(x)] > r * 2.2 and not any(cv2.pointPolygonTest(h_, (float(x), float(y)), True) > -r * 1.2 for h_ in holes)
            if ring or free:
                circles.append((float(x), float(y), float(r)))
    return dict(kind="housing", W=W, H=H, outer=simp(outer), holes=[simp(h) for h in holes], rects=rects,
                circles=circles, steel=steel)


def poly(p):
    return "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in p) + "Z"


def render(m, d):
    W, H = m["W"], m["H"]
    sw = max(2.0, min(W, H) * .006)
    o = []

    def R(x, y, w, h, rx, fill, stroke=INK, s=sw):
        o.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx:.1f}" fill="{fill}"'
                 + (f' stroke="{stroke}" stroke-width="{s:.1f}"' if stroke else "") + "/>")

    def C(x, y, r, fill, stroke=INK, s=sw):
        o.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" fill="{fill}"' + (f' stroke="{stroke}" stroke-width="{s:.1f}"' if stroke else "") + "/>")

    def G(name, cx, cy, size, col, s):
        k = size / 24
        o.append(f'<path d="{GLYPH[name]}" transform="translate({cx - 12 * k:.1f} {cy - 12 * k:.1f}) scale({k:.3f})" fill="none" '
                 f'stroke="{col}" stroke-width="{s / k:.2f}" stroke-linecap="round" stroke-linejoin="round"/>')

    if m["kind"] == "module":
        R(sw / 2, sw / 2, W - sw, H - sw, W * .01, DARK if m["cam"] else STEEL)
        if m["cam"]:
            if m["dome"]:
                cx, cy, r = m["dome"]
                C(cx, cy, r, "#1E1E1E", "#4a4a4a", sw * .7)
                C(cx, cy, r * .56, "#2B2B2B", "#4a4a4a", sw * .5)
                C(cx, cy, r * .27, "#6b7280", None)
            for x, y, w, h in m["leds"]:
                R(x, y, w, h, h / 2, "#2B2B2B", "#5a5a5a", sw * .5)
            for cx, cy, r in m["dots"]:
                C(cx, cy, r, "#2B2B2B", "#5a5a5a", sw * .4)
            for (cx, cy, s), name in zip(m["icons"], ["call", "door", "hand", "bell"]):
                G(name, cx, cy, s * 1.1, LIGHT, sw * .6)
        else:
            for y in m["seams"]:
                o.append(f'<path d="M{sw:.1f} {y:.1f}H{W - sw:.1f}" stroke="{INK}" stroke-width="{sw:.1f}"/>')
            for x, y, w, h in m["slots"]:
                R(x, y, w, h, h / 2, DARK, None)
            for x, y, w, h in m["plates"]:
                R(x, y, w, h, min(w, h) * .04, "#FFFFFF")
            r = m["rfid"]
            if r:
                R(*r["b"], r["b"][2] * .02, DARK)
                if r.get("sign"):
                    cx, cy, s = r["sign"]
                    G("rfid", cx, cy, s * 1.1, LIGHT, sw * .7)
                if r.get("win"):
                    R(*r["win"], r["win"][2] * .1, "#1F1F1F", "#3A3A3A", sw * .6)
                if r.get("ring"):
                    C(*r["ring"], "none", "#9CA3AF", sw)
    else:
        body = STEEL if m["steel"] else BLACKB
        path = poly(m["outer"]) + "".join(poly(h) for h in m["holes"])
        o.append(f'<path d="{path}" fill="{body}" fill-rule="evenodd" stroke="{INK}" stroke-width="{sw:.1f}" stroke-linejoin="round"/>')
        for x, y, w, h in m["rects"]:
            R(x, y, w, h, min(w, h) * .03, "none", "#8C8C8C" if not m["steel"] else "#8a8a8a", sw * .7)
        for x, y, r in m["circles"]:
            C(x, y, r, "none", "#8C8C8C", sw * .7)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" '
            f'aria-label="{d["article"]} · {d["name"]} (Skizze)">' + "".join(o) + "</svg>")


def check(m, g):
    e = cv2.Canny(cv2.GaussianBlur(g, (3, 3), 0), 25, 70)
    dist = cv2.distanceTransform((e == 0).astype(np.uint8), cv2.DIST_L2, 3)
    H, W = g.shape
    errs = []

    def rect(role, b):
        mk = np.zeros((H, W), np.uint8)
        x, y, w, h = [int(round(v)) for v in b]
        cv2.rectangle(mk, (x, y), (x + w - 1, y + h - 1), 1, 1)
        errs.append((role, float(np.median(dist[mk > 0]))))

    if m["kind"] == "module":
        for p in m.get("plates", []):
            rect("plate", p)
        if m.get("rfid"):
            rect("rfid", m["rfid"]["b"])
        for y in m.get("seams", []):
            errs.append(("seam", float(np.median(dist[int(round(y)), int(W * .1):int(W * .9)]))))
    else:
        for r in m["rects"]:
            rect("step", r)
    mean = float(np.mean([v for _, v in errs])) if errs else 0.0
    worst = max(errs, key=lambda t: t[1]) if errs else ("-", 0.0)
    return dict(mean=round(mean, 2), worst=[worst[0], round(worst[1], 2)], n=len(errs), logo=False)


def sketch(d, man=None):
    img, alpha, g = load(d)
    m = module(d, img, alpha, g) if d["kind"] == "pro-modul" else housing(d, img, alpha, g)
    return render(m, d), check(m, g)


if __name__ == "__main__":
    import json
    man = json.load(open(os.path.join(F.DEV, "devices.json"), encoding="utf-8"))["devices"]
    for a in sys.argv[1:]:
        d = next(x for x in man if x["article"].upper() == a.upper())
        svg, rep = sketch(d)
        open(os.path.join(F.DEV, d["image"].rsplit(".", 1)[0] + ".svg"), "w", encoding="utf-8").write(svg)
        print(f"{d['article']:22} {rep}")
