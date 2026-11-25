#!/usr/bin/env python3
"""
EVO HD door stations as technical sketches: find each part on the real photo, draw it as a clean symbol.

Every EVO HD station, audio station and extension is built from the same few parts. Each is found on
the photo (assets/devices/<article>.png) and drawn with one symbol, so all sketches share one style:

    window   sensor window at the top / bottom      light field + its dark sensor bar
    ir       IR light above the camera               dark pill, mesh or its LEDs
    camera   camera dome                             black circle, ring, lens
    speaker  loudspeaker slots / holes               black slots, black dots
    mic      microphone hole                         black slot
    display  status display                          black bar with its icons (bell, call, door)
    rfid     RFID / fingerprint glass block          black block, RFID sign, finger ring
    plate    name plate                              white field
    button   call button                             body-coloured button, ring, centre dot
    logo     BALTER logo                             the real logo, upright, where it sits on the plate

Black variants share the geometry of their steel twin (same housing): the parts are taken from the
twin and then re-found locally on the black photo (LEDs, display icons, IR pill).

The result is checked against the photo's edges (chamfer distance, px) — see sketch_fit.py.
"""
import os
import sys

import cv2
import numpy as np
from scipy import ndimage

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sketch_fit as F  # noqa: E402

INK = "#111111"
DARK = "#111111"
BODY = {"steel": "#D9D9D9", "white": "#F2F2F2", "black": "#3A3A3A"}
TWIN = {"EVO-HD-BLACK-8FAM": "EVO-HD-8FAM", "EVO-BLACK-8EXT": "EVO-8EXT", "EVO-BLACK-12EXT": "EVO-12EXT", "EVO-BLACK-1FAM": "EVO-1FAM", "EVO-BLACK-2FAM": "EVO-2FAM", "EVO-BLACK-3FAM": "EVO-3FAM", "EVO-BLACK-4FAM": "EVO-4FAM"}

GLYPH = {   # 24x24, stroked
    "bell": "M6.5 16.5h11l-1.4-2.2V10.8a4.1 4.1 0 0 0-8.2 0v3.5z M10.4 18.8a1.6 1.6 0 0 0 3.2 0",
    "call": "M8 5h2.4l1.2 3.4-1.7 1.1a9 9 0 0 0 4.6 4.6l1.1-1.7 3.4 1.2V16a1.8 1.8 0 0 1-1.9 1.8A12.6 12.6 0 0 1 6.2 6.9 1.8 1.8 0 0 1 8 5z M15 5.5a4 4 0 0 1 3.5 3.5 M15 2.8a6.8 6.8 0 0 1 6.2 6.2",
    "door": "M3.5 5.5l7.5 1.5v12l-7.5-1.5z M20.5 5.5l-7.5 1.5v12l7.5-1.5z",
    "rfid": "M3 8.5h9.5v7H3z M15.5 9a4.2 4.2 0 0 1 0 6 M18.2 6.6a7.6 7.6 0 0 1 0 10.8",
}


def load(d):
    img4 = cv2.imread(os.path.join(F.DEV, d["image"]), cv2.IMREAD_UNCHANGED)
    alpha = img4[..., 3] > 40
    img = img4[..., :3]
    e, g = F.edges_of(img, alpha)
    ys, xs = np.nonzero(alpha)
    box = (int(xs.min()), int(ys.min()), int(xs.max() - xs.min() + 1), int(ys.max() - ys.min() + 1))
    return img, alpha, g, e, box


# ------------------------------------------------------------------ detection
def find_buttons(g, alpha, box):
    bx, by, bw, bh = box
    x0 = int(bx + bw * .55)
    roi = cv2.GaussianBlur(g[:, x0:bx + bw], (5, 5), 1.2)
    cc = cv2.HoughCircles(roi, cv2.HOUGH_GRADIENT, dp=1, minDist=bw * .08, param1=70, param2=18,
                          minRadius=int(bw * .035), maxRadius=int(bw * .075))
    if cc is None:
        return []
    bs = [(float(x + x0), float(y), float(r)) for x, y, r in cc[0]]
    # call buttons stand in one column: keep the dominant x
    xm = np.median([b[0] for b in bs])
    rm = np.median([b[2] for b in bs])
    bs = [b for b in bs if abs(b[0] - xm) < rm * .6 and abs(b[2] - rm) < rm * .3 and by + bh * .08 < b[1] < by + bh * .93]
    rm = float(np.median([b[2] for b in bs])) if bs else rm
    return sorted([(x, y, rm) for x, y, _ in bs], key=lambda b: b[1])   # one size for all buttons


def find_plates(g, e, buttons, box):
    """Plates sit left of the buttons; edges taken from the summed gradient over all rows."""
    if not buttons:
        return []
    bx, by, bw, bh = box
    gs = cv2.GaussianBlur(g.astype(np.float32), (3, 3), 0)
    gx = np.abs(cv2.Sobel(gs, cv2.CV_32F, 1, 0, ksize=3))
    gy = np.abs(cv2.Sobel(gs, cv2.CV_32F, 0, 1, ksize=3))
    r = np.median([b[2] for b in buttons])
    xb = np.median([b[0] for b in buttons])
    prof = np.zeros(g.shape[1], np.float32)
    for _, cy, _ in buttons:
        prof += gx[int(cy - r * .4):int(cy + r * .4)].mean(0)
    lim_r = int(xb - r * 1.15)
    p = prof.copy()
    p[lim_r:] = 0
    p[:int(bx + bw * .06)] = 0
    right = int(np.argmax(p[int(xb - r * 3.5):lim_r]) + xb - r * 3.5)
    p2 = p.copy()
    p2[int(right - bw * .2):] = 0
    left = int(np.argmax(p2))
    plates = []
    cx0, cx1 = int(left + (right - left) * .3), int(left + (right - left) * .7)
    for _, cy, _ in buttons:
        col = gy[:, cx0:cx1].mean(1)
        up = int(cy - r * 1.6), int(cy - r * .15)
        dn = int(cy + r * .15), int(cy + r * 1.6)
        top = up[0] + int(np.argmax(col[up[0]:up[1]]))
        bot = dn[0] + int(np.argmax(col[dn[0]:dn[1]]))
        plates.append([left, top, right - left, bot - top])
    hm = float(np.median([p_[3] for p_ in plates]))
    for p_ in plates:        # one height for all: centre each plate on its own measured middle
        mid = p_[1] + p_[3] / 2
        p_[1], p_[3] = mid - hm / 2, hm
    return plates


def find_upper(img, g, e, alpha, box, limit_y, logo=None):
    """Everything above the first plate row (and the bottom window)."""
    bx, by, bw, bh = box
    inner = cv2.erode(alpha.astype(np.uint8), np.ones((15, 15))) > 0
    body_L = float(np.median(g[alpha]))
    parts = []
    dark = (g < body_L - 55) & inner
    lab, n = ndimage.label(dark)
    holes = []
    for i, sl in enumerate(ndimage.find_objects(lab), 1):
        comp = lab[sl] == i
        a = int(comp.sum())
        y, x = sl[0].start, sl[1].start
        h, w = comp.shape
        if a < 5:
            continue
        cy = y + h / 2
        if not (y > by + bh * .02 and (cy < limit_y or cy > by + bh * .9)):
            continue
        if .7 < w / h < 1.4 and bw * .12 < w < bw * .32 and a > .55 * w * h and not any(
                p_["t"] == "camera" for p_ in parts) and y < by + bh * .3:
            parts.append(dict(t="camera", c=(x + w / 2, y + h / 2), r=(w + h) / 4))
        elif w > bw * .35 and bh * .02 < h < bh * .09 and a > .7 * w * h:
            parts.append(dict(t="display", b=(x, y, w, h)))
        elif w > bw * .3 and .7 < w / h < 1.5 and a > .7 * w * h:
            parts.append(dict(t="rfid", b=(x, y, w, h)))
        elif w < bw * .06 and h < bw * .06 and .5 < w / h < 2 and a > .5 * w * h:
            holes.append((x + w / 2, y + h / 2, (w + h) / 4))
        elif w >= 3 * h and h < bh * .015 and w >= bw * .08:
            parts.append(dict(t="slot", b=(x, y, w, h)))
        elif (h >= 2 * w or w >= 2 * h) and max(w, h) < bh * .03 and max(w, h) >= 6:
            parts.append(dict(t="mic", b=(x, y, w, h)))
    if len(holes) >= 12:
        rr = float(np.median([hh[2] for hh in holes]))
        parts.append(dict(t="grille", dots=[(hx, hy) for hx, hy, hr in holes if abs(hr - rr) < rr * .5], r=rr))
    elif holes:
        for hx, hy, hr in holes:
            parts.append(dict(t="mic", b=(hx - hr * .6, hy - hr * 1.6, hr * 1.2, hr * 3.2)))
    # light parts from closed outlines: windows and the IR pill
    els = F.elements(e, g, alpha, g.shape[1], g.shape[0])
    cam = next((p_ for p_ in parts if p_["t"] == "camera"), None)
    for el in sorted(els, key=lambda el: -el["area"]):
        x, y, w, h = el["x"], el["y"], el["w"], el["h"]
        cx_, cy_ = x + w / 2, y + h / 2
        near_edge = cy_ < by + bh * .07 or cy_ > by + bh * .9
        if near_edge and bw * .06 < w < bw * .3 and 1.3 < w / h < 3.5 and abs(cx_ - (bx + bw / 2)) < bw * .12:
            if not any(p_["t"] == "window" and abs(p_["b"][1] - y) < h for p_ in parts):
                parts.append(dict(t="window", b=(x, y, w, h)))
        elif cam and w > 2.2 * h and w < bw * .4 and 0 < cam["c"][1] - cy_ < cam["r"] * 3 and abs(cx_ - cam["c"][0]) < cam["r"]:
            if not any(p_["t"] == "ir" for p_ in parts):
                parts.append(dict(t="ir", b=(x, y, w, h)))
    for band in ("top", "bottom"):
        if not any(p_["t"] == "window" and ((p_["b"][1] < by + bh * .5) == (band == "top")) for p_ in parts):
            wb = window_by_template(g, box, band)
            if wb:
                parts.append(dict(t="window", b=wb, matched=True))
    # small dark bits inside a larger part (window sensor, IR mesh, edges) are not parts of their own
    def box_of(p_):
        if "b" in p_:
            return p_["b"]
        if "c" in p_:
            return (p_["c"][0] - p_["r"], p_["c"][1] - p_["r"], 2 * p_["r"], 2 * p_["r"])
        return None
    big = [box_of(p_) for p_ in parts if p_["t"] in ("window", "ir", "camera", "display", "rfid")]
    if logo:
        big.append(logo)

    def inside(b):
        cx_, cy_ = b[0] + b[2] / 2, b[1] + b[3] / 2
        return any(o[0] - 6 <= cx_ <= o[0] + o[2] + 6 and o[1] - 6 <= cy_ <= o[1] + o[3] + 6 for o in big)
    parts = [p_ for p_ in parts if not (p_["t"] in ("slot", "mic") and (
        inside(p_["b"]) or (p_["t"] == "mic" and max(p_["b"][2], p_["b"][3]) < 6) or (p_["t"] == "slot" and (p_["b"][3] < 2 or p_["b"][2] < bw * .08))))]
    for p_ in parts:
        if p_["t"] == "ir":
            p_["leds"] = leds_in(g, p_["b"])
        if p_["t"] == "display":
            p_["icons"] = icons_in(g, p_["b"])
        if p_["t"] == "rfid":
            p_.update(rfid_in(g, e, p_["b"]))
        if p_["t"] == "window":
            p_["bar"] = window_bar(g, p_["b"], body_L)
    return parts


def leds_in(g, b):
    x, y, w, h = [int(round(v)) for v in b]
    roi = g[y:y + h, x:x + w]
    if roi.size == 0:
        return []
    m = roi > max(200, np.percentile(roi, 75))
    lab, n = ndimage.label(m)
    out = []
    for i, sl in enumerate(ndimage.find_objects(lab), 1):
        hh, ww = sl[0].stop - sl[0].start, sl[1].stop - sl[1].start
        if hh > h * .35 and .6 < ww / hh < 1.6:
            out.append((x + sl[1].start + ww / 2, y + sl[0].start + hh / 2, (ww + hh) / 4))
    return out if 3 <= len(out) <= 6 else []


def icons_in(g, b):
    """Printed icons and the round light sensor on the status display. A sensor is a filled round blob;
    an icon is line art (low fill). Icons are named bell, call, door from left to right."""
    x, y, w, h = [int(round(v)) for v in b]
    roi = g[y + 2:y + h - 2, x + 2:x + w - 2]
    th = cv2.morphologyEx(roi, cv2.MORPH_TOPHAT, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (int(h * .7) | 1,) * 2))
    raw = th > 28
    m = cv2.dilate(raw.astype(np.uint8), np.ones((5, 5))) > 0
    lab, n = ndimage.label(m)
    found = []
    for i, sl in enumerate(ndimage.find_objects(lab), 1):
        hh, ww = sl[0].stop - sl[0].start, sl[1].stop - sl[1].start
        if hh < h * .3:
            continue
        fill = float(raw[sl][lab[sl] == i].mean())
        found.append((x + 2 + sl[1].start + ww / 2, y + 2 + sl[0].start + hh / 2, max(ww, hh), ww / hh, fill))
    found.sort()
    names = ["bell", "call", "door"]
    res, k = [], 0
    for cx, cy, s_, ar, fill in found:
        if .7 < ar < 1.4 and fill > .5:
            res.append(("dot", cx, cy, s_))
        elif k < 3:
            res.append((names[k], cx, cy, s_))
            k += 1
    return res


def rfid_in(g, e, b):
    x, y, w, h = [int(round(v)) for v in b]
    roi = g[y:y + h, x:x + w]
    out = {}
    cc = cv2.HoughCircles(cv2.GaussianBlur(roi, (5, 5), 1.2), cv2.HOUGH_GRADIENT, dp=1, minDist=w, param1=60, param2=15,
                          minRadius=int(w * .08), maxRadius=int(w * .2))
    if cc is not None:
        cx, cy, r = cc[0][0]
        out["ring"] = (x + cx, y + cy, r)
    th = cv2.morphologyEx(roi, cv2.MORPH_TOPHAT, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (int(w * .3) | 1,) * 2)) > 30
    top = th[:int(h * .45)]
    ys, xs = np.nonzero(top)
    if len(xs) > 10:
        x5, x95 = np.percentile(xs, [10, 90])
        out["sign"] = (x + float(np.median(xs)), y + float(np.median(ys)), float(min(x95 - x5, w * .3)))
    return out


def window_bar(g, b, body_L):
    x, y, w, h = [int(round(v)) for v in b]
    roi = g[y + 2:y + h - 2, x + 2:x + w - 2].astype(float)
    if roi.size == 0:
        return None
    col = roi.mean(0)
    j = int(np.argmin(col))
    if col[j] > np.median(col) - 25:
        return None
    k0 = j
    while k0 > 0 and col[k0 - 1] < np.median(col) - 25:
        k0 -= 1
    k1 = j
    while k1 < len(col) - 1 and col[k1 + 1] < np.median(col) - 25:
        k1 += 1
    return (x + 2 + k0, y + h * .25, k1 - k0 + 1, h * .5)


_WIN = {}


def window_by_template(g, box, band):
    """Sensor window that the outlines missed: match the window of the reference station of the same width."""
    import json
    bx, by, bw, bh = box
    if not _WIN:
        man = json.load(open(os.path.join(F.DEV, "devices.json"), encoding="utf-8"))["devices"]
        for ref in ("EVO-HD-1FAM", "EVO-HD-6FAM", "EVO-12EXT"):
            d = next(x for x in man if x["article"] == ref)
            img, alpha, g2, e2, box2 = load(d)
            ps = find_upper(img, g2, e2, alpha, box2, box2[1] + box2[3] * .9)
            for p_ in ps:
                if p_["t"] == "window":
                    x, y, w, h = [int(round(v)) for v in p_["b"]]
                    _WIN.setdefault(box2[2], []).append(g2[y:y + h, x:x + w])
    tpls = _WIN.get(min(_WIN, key=lambda k: abs(k - bw))) if _WIN else None
    if not tpls:
        return None
    y0, y1 = (by, int(by + bh * .1)) if band == "top" else (int(by + bh * .88), by + bh)
    roi = g[y0:y1, bx:bx + bw]
    best = None
    for t in tpls:
        if t.shape[0] >= roi.shape[0] or t.shape[1] >= roi.shape[1]:
            continue
        r = cv2.matchTemplate(roi, t, cv2.TM_CCOEFF_NORMED)
        _, v, _, loc = cv2.minMaxLoc(r)
        if v > .5 and (best is None or v > best[0]):
            best = (v, (bx + loc[0], y0 + loc[1], t.shape[1], t.shape[0]))
    return best[1] if best else None


def logo_box(e, box):
    bx, by, bw, bh = box
    reg = np.zeros_like(e, bool)
    reg[int(by + bh * .7):, int(bx + bw * .82):] = True
    blobs = ndimage.label(cv2.dilate(((e > 0) & reg).astype(np.uint8), np.ones((7, 7))) > 0)[0]
    best = None
    for sl in ndimage.find_objects(blobs) or []:
        hh, ww = sl[0].stop - sl[0].start, sl[1].stop - sl[1].start
        if hh > 2.5 * ww and hh > bh * .04 and (best is None or hh > best[3]):
            best = (sl[1].start + 3, sl[0].start + 3, ww - 6, hh - 6)
    return best


def model(d, man):
    img, alpha, g, e, box = load(d)
    a = d["article"]
    if a in TWIN:
        tw = next(x for x in man if x["article"] == TWIN[a])
        m = model(tw, man)
        return transfer(m, d, img, alpha, g, e, box)
    buttons = find_buttons(g, alpha, box)
    plates = find_plates(g, e, buttons, box)
    limit = min([p[1] for p in plates]) - 4 if plates else box[1] + box[3] * .9
    logo = logo_box(e, box)
    parts = find_upper(img, g, e, alpha, box, limit, logo)
    near = lambda b, q: q[0] - 8 <= b[0] + b[2] / 2 <= q[0] + q[2] + 8 and q[1] - 10 <= b[1] + b[3] / 2 <= q[1] + q[3] + 10  # noqa: E731
    parts = [p_ for p_ in parts if not (p_["t"] in ("slot", "mic") and any(near(p_["b"], q) for q in plates))]
    if "RFID" in a and not any(p_["t"] == "rfid" for p_ in parts):
        lite = rfid_light(g, e, alpha, box, parts, plates)
        if lite:
            parts.append(lite)
    return dict(article=a, box=box, W=g.shape[1], H=g.shape[0], mat=F.material_of(d), buttons=buttons, plates=plates,
                parts=parts, logo=logo, e=e, img=img, alpha=alpha, name=d["name"])


def rfid_light(g, e, alpha, box, parts, plates):
    """EVO analog RFID stations: a light glass field with the card sign, between display and name plates."""
    bx, by, bw, bh = box
    top = max([p_["b"][1] + p_["b"][3] for p_ in parts if p_["t"] == "display"] or [by + bh * .2]) + 4
    bot = min([p[1] for p in plates] or [by + bh * .8]) - 4
    # the glass is smooth where the brushed steel around it is streaked: find it by its missing texture
    tex = cv2.blur(np.abs(cv2.Sobel(g.astype(float), cv2.CV_64F, 1, 0, ksize=3)), (11, 11))
    m = (tex < np.percentile(tex[alpha], 12)) & alpha
    reg = np.zeros_like(m)
    reg[int(top):int(bot), int(bx + bw * .08):int(bx + bw * .92)] = True
    m = cv2.morphologyEx((m & reg).astype(np.uint8), cv2.MORPH_OPEN, np.ones((5, 5)))
    m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((9, 9)))
    lab, n = ndimage.label(m)
    best = None
    for sl in ndimage.find_objects(lab) or []:
        h_, w_ = sl[0].stop - sl[0].start, sl[1].stop - sl[1].start
        if w_ > bw * .3 and (best is None or w_ * h_ > best[2] * best[3]):
            best = (sl[1].start, sl[0].start, w_, h_)
    if not best:
        return None
    x, y, w, h = best
    return dict(t="rfidlite", b=best, sign=(x + w / 2, y + h / 2, h * .45))


def transfer(m, d, img, alpha, g, e, box):
    (sx0, sy0, sw0, sh0), (tx, ty, tw_, th_) = m["box"], box
    kx, ky = tw_ / sw0, th_ / sh0
    P = lambda x, y: (tx + (x - sx0) * kx, ty + (y - sy0) * ky)  # noqa: E731
    B = lambda b: (*P(b[0], b[1]), b[2] * kx, b[3] * ky)  # noqa: E731
    parts = []
    for p in m["parts"]:
        q = dict(p)
        if "b" in p:
            q["b"] = B(p["b"])
        if "c" in p:
            q["c"] = P(*p["c"])
            q["r"] = p["r"] * kx
        if p["t"] == "grille":
            q["dots"] = [P(*xy) for xy in p["dots"]]
            q["r"] = p["r"] * kx
        if p["t"] == "window" and p.get("bar"):
            q["bar"] = B(p["bar"])
        parts.append(q)
    # re-find on the black photo what differs between twins
    els = F.elements(e, g, alpha, g.shape[1], g.shape[0])
    for q in parts:
        if q["t"] == "ir":
            x, y, w, h = q["b"]
            cand = [el for el in els if el["w"] > 2.2 * el["h"] and abs(el["x"] + el["w"] / 2 - (x + w / 2)) < w * .4
                    and abs(el["y"] + el["h"] / 2 - (y + h / 2)) < h * 1.2 and .6 * w < el["w"] < 1.6 * w]
            if cand:
                el = max(cand, key=lambda el: el["area"])
                q["b"] = (el["x"], el["y"], el["w"], el["h"])
            q["leds"] = leds_in(g, q["b"])
        if q["t"] == "display":
            q["icons"] = icons_in(g, q["b"])
    buttons = [(*P(x, y), r * kx) for x, y, r in m["buttons"]]
    plates = [list(B(p)) for p in m["plates"]]
    # plates are bright on the black plate: measure them again on this photo, keep only if consistent
    again = find_plates(g, e, buttons, box)
    if again and all(abs(a_[1] - b_[1]) < b_[3] * .4 and abs(a_[2] - b_[2]) < b_[2] * .1 for a_, b_ in zip(again, plates)):
        plates = again
    return dict(article=d["article"], box=box, W=g.shape[1], H=g.shape[0], mat=F.material_of(d),
                buttons=buttons, plates=plates,
                parts=parts, logo=logo_box(e, box), e=e, img=img, alpha=alpha, name=d["name"])


# ------------------------------------------------------------------ drawing
def render(m):
    W, H, mat = m["W"], m["H"], m["mat"]
    bx, by, bw, bh = m["box"]
    sw = max(2.0, min(W, H) * .006)
    black = mat == "black"
    body = BODY[mat]
    lite = "#2C2C2C" if black else "#F7F7F7"
    glyph = "#D4D4D4"
    o = []
    R = lambda x, y, w, h, rx, fill, stroke=INK, s=sw: o.append(  # noqa: E731
        f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx:.1f}" fill="{fill}"'
        + (f' stroke="{stroke}" stroke-width="{s:.1f}"' if stroke else "") + "/>")
    C = lambda x, y, r, fill, stroke=INK, s=sw: o.append(  # noqa: E731
        f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" fill="{fill}"' + (f' stroke="{stroke}" stroke-width="{s:.1f}"' if stroke else "") + "/>")
    defs = (f'<defs><pattern id="mesh" width="5" height="5" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">'
            f'<path d="M0 0V5M0 0H5" stroke="#8a8a8a" stroke-width="1.2"/></pattern></defs>')
    R(bx + sw / 2, by + sw / 2, bw - sw, bh - sw, bw * .015, body)
    for p in m["parts"]:
        t = p["t"]
        if t == "window":
            x, y, w, h = p["b"]
            R(x, y, w, h, h * .22, lite)
            if p.get("bar"):
                R(*p["bar"], 0.8, DARK, None)
        elif t == "ir":
            x, y, w, h = p["b"]
            R(x, y, w, h, h / 2, DARK)
            if p.get("leds"):
                for lx, ly, lr in p["leds"]:
                    C(lx, ly, lr, "#FFFFFF", "#6b6b6b", sw * .5)
            else:
                o.append(f'<rect x="{x + h * .22:.1f}" y="{y + h * .22:.1f}" width="{w - h * .44:.1f}" height="{h * .56:.1f}" '
                         f'rx="{h * .28:.1f}" fill="url(#mesh)"/>')
        elif t == "camera":
            (cx, cy), r = p["c"], p["r"]
            C(cx, cy, r, DARK)
            C(cx, cy, r * .56, "#2B2B2B", "#4a4a4a", sw * .6)
            C(cx, cy, r * .27, "#6b7280", None)
            C(cx - r * .09, cy - r * .09, r * .08, "#D4D4D4", None)
        elif t in ("slot", "mic"):
            x, y, w, h = p["b"]
            R(x, y, w, h, min(w, h) / 2, DARK, None)
        elif t == "grille":
            for gx_, gy_ in p["dots"]:
                C(gx_, gy_, p["r"], DARK, None)
        elif t == "display":
            x, y, w, h = p["b"]
            R(x, y, w, h, h * .1, DARK)
            if p.get("trace"):
                o.append(f'<path d="{p["trace"]}" fill="{glyph}" fill-rule="evenodd"/>')
            if p.get("trace"):
                for cx, cy, s in p.get("dots", []):
                    C(cx, cy, s * .45, "#3a3a3a", None)
            for name, cx, cy, s in ([] if p.get("trace") else p.get("icons", [])):
                if name == "dot":
                    C(cx, cy, s * .4, "#3a3a3a", None)
                    continue
                k = h * .5 / 24
                o.append(f'<path d="{GLYPH[name]}" transform="translate({cx - 12 * k:.1f} {cy - 12 * k:.1f}) scale({k:.3f})" '
                         f'fill="none" stroke="{glyph}" stroke-width="{1.6:.1f}" stroke-linecap="round" stroke-linejoin="round"/>')
        elif t == "rfidlite":
            x, y, w, h = p["b"]
            R(x, y, w, h, h * .06, "#F7F7F7")
            if p.get("trace"):
                o.append(f'<path d="{p["trace"]}" fill="#6b6b6b" fill-rule="evenodd"/>')
                continue
            cx, cy, sz = p["sign"]
            k = sz * 1.1 / 24
            o.append(f'<path d="{GLYPH["rfid"]}" transform="translate({cx - 12 * k:.1f} {cy - 12 * k:.1f}) scale({k:.3f})" '
                     f'fill="none" stroke="#6b6b6b" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/>')
        elif t == "rfid":
            x, y, w, h = p["b"]
            R(x, y, w, h, w * .04, DARK)
            if p.get("trace"):
                o.append(f'<path d="{p["trace"]}" fill="{glyph}" fill-rule="evenodd"/>')
            elif p.get("sign"):
                cx, cy, s = p["sign"]
                k = s * 1.1 / 24
                o.append(f'<path d="{GLYPH["rfid"]}" transform="translate({cx - 12 * k:.1f} {cy - 12 * k:.1f}) scale({k:.3f})" '
                         f'fill="none" stroke="{glyph}" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/>')
            if p.get("ring"):      # fingerprint sensor: its square window, then the lit ring
                cx, cy, r = p["ring"]
                R(cx - r * 1.9, cy - r * 2.05, r * 3.8, r * 3.8, r * .25, "#1F1F1F", "#3A3A3A", sw * .6)
                C(cx, cy, r, "none", "#9CA3AF", sw)
    for x, y, w, h in m["plates"]:
        R(x, y, w, h, h * .1, "#FFFFFF")
    for x, y, r in m["buttons"]:
        C(x, y, r, "#2A2A2A" if black else body)
        C(x, y, r * .62, "none", "#6b6b6b" if black else "#8a8a8a", sw * .5)
        C(x, y, r * .14, "#D4D4D4" if black else INK, None)
    if m["logo"]:
        o.append(F.logo_svg(m["logo"], "#E5E5E5" if black else "#111111"))
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" '
            f'aria-label="{m["article"]} · {m["name"]} (Skizze)">' + defs + "".join(o) + "</svg>")


def check(m):
    """Chamfer distance of every drawn outline to the photo's edges (median px per part)."""
    e = m["e"]
    if m["mat"] == "black":       # weak outlines on black: equalise first, then a lower threshold
        g = cv2.cvtColor(m["img"], cv2.COLOR_BGR2GRAY)
        g = cv2.createCLAHE(3.0, (8, 8)).apply(cv2.blur(g, (9, 1)))
        e = cv2.Canny(cv2.bilateralFilter(g, 9, 30, 9), 20, 60)
        e[~(cv2.erode(m["alpha"].astype(np.uint8), np.ones((9, 9))) > 0)] = 0
    H, W = e.shape
    dist = cv2.distanceTransform((e == 0).astype(np.uint8), cv2.DIST_L2, 3)
    errs = []

    def ring(role, mask):
        pts = dist[mask > 0]
        if pts.size:
            errs.append((role, float(np.median(pts))))

    for x, y, w, h in m["plates"]:
        mk = np.zeros((H, W), np.uint8)
        cv2.rectangle(mk, (int(round(x)), int(round(y))), (int(round(x + w - 1)), int(round(y + h - 1))), 1, 1)
        ring("plate", mk)
    for x, y, r in m["buttons"]:
        mk = np.zeros((H, W), np.uint8)
        cv2.circle(mk, (int(round(x)), int(round(y))), int(round(r)), 1, 1)
        ring("button", mk)
    for p in m["parts"]:
        mk = np.zeros((H, W), np.uint8)
        if p.get("matched"):      # found by template match on a faint window: its proof is the match score
            continue
        if "b" in p and p["t"] not in ("slot", "mic"):
            x, y, w, h = p["b"]
            cv2.rectangle(mk, (int(round(x)), int(round(y))), (int(round(x + w - 1)), int(round(y + h - 1))), 1, 1)
        elif p["t"] == "camera":
            cv2.circle(mk, (int(round(p["c"][0])), int(round(p["c"][1]))), int(round(p["r"])), 1, 1)
        else:
            continue
        ring(p["t"], mk)
    mean = float(np.mean([v for _, v in errs])) if errs else 0.0
    worst = max(errs, key=lambda t: t[1]) if errs else ("-", 0.0)
    count = {}
    for p in m["parts"]:
        count[p["t"]] = count.get(p["t"], 0) + 1
    count["plate"], count["button"] = len(m["plates"]), len(m["buttons"])
    return dict(mean=round(mean, 2), worst=[worst[0], round(worst[1], 2)], parts=count, logo=bool(m["logo"]))


ICON_MASTER = "EVO-HD-2FAM-AUDIO"   # cleanest photo of the status display; the same part sits on every station
_MASTER = {}


def _icon_paths(man):
    """The three display icons of the master photo, each as its own traced path (left to right)."""
    d = next(x for x in man if x["article"] == ICON_MASTER)
    mm = model(d, man)
    v = mm["img"].max(-1)
    disp = next(p for p in mm["parts"] if p["t"] == "display")
    h = disp["b"][3]
    out = []
    for name, cx, cy, sz in icons_in(v, disp["b"]):
        if name == "dot":
            continue
        half = min(sz * .75, h * .5 - 3)
        out.append(F.trace_icon(v, (cx - half, cy - half, 2 * half, 2 * half), light=True, tophat=True, level=.42))
    return out


def _master_icons(man):
    """The display icons (bell, call, door) traced once from the master photo, in display-relative units."""
    if "icons" in _MASTER:
        return _MASTER["icons"]
    d = next(x for x in man if x["article"] == ICON_MASTER)
    mm = model(d, man)
    v = mm["img"].max(-1)
    disp = next(p for p in mm["parts"] if p["t"] == "display")
    x, y, w, h = disp["b"]
    polys = []
    for name, cx, cy, sz in icons_in(v, disp["b"]):
        if name == "dot":
            continue
        half = min(sz * .75, h * .5 - 3)
        path = F.trace_icon(v, (cx - half, cy - half, 2 * half, 2 * half), light=True, tophat=True, level=.42)
        for seg in path.split("Z"):
            pts = [tuple(map(float, q.strip().lstrip("ML").split())) for q in seg.replace("M", "L").split("L") if q.strip()]
            if len(pts) >= 3:
                polys.append([((px - x) / w, (py - y) / h) for px, py in pts])
    _MASTER["icons"] = polys
    return polys


def sensor_in(v, b):
    """The round light sensor at the right end of the display, if this station has one."""
    x, y, w, h = [int(round(q)) for q in b]
    x0 = x + int(w * .84)
    roi = cv2.GaussianBlur(v[y + 2:y + h - 2, x0:x + w - 3], (3, 3), 0)
    if roi.size == 0:
        return None
    cs = cv2.HoughCircles(roi, cv2.HOUGH_GRADIENT, 1.2, h, param1=60, param2=10,
                          minRadius=max(2, int(h * .13)), maxRadius=int(h * .32))
    if cs is None:
        return None
    cx, cy, r = cs[0][0]
    yy, xx = np.mgrid[0:roi.shape[0], 0:roi.shape[1]]
    rr = np.hypot(xx - cx, yy - cy)
    inside, ring = roi[rr < r * .8], roi[(rr > r * 1.25) & (rr < r * 1.8)]
    if inside.size == 0 or ring.size == 0 or float(inside.mean()) - float(ring.mean()) < 6:
        return None
    return (x0 + cx, y + 2 + cy, r)


def add_traces(m, man):
    """Printed icons: the display icons come from the master trace, placed in this station's measured
    display frame; the light sensor, RFID and card signs are found on this device's own photo."""
    g = cv2.cvtColor(m["img"], cv2.COLOR_BGR2GRAY)
    v = m["img"].max(-1)          # coloured print (blue icons) is bright in its own channel
    for p in m["parts"]:
        if p["t"] == "display":
            x, y, w, h = p["b"]
            polys = _master_icons(man)
            p["trace"] = " ".join("M" + " L".join(f"{x + u * w:.2f} {y + t * h:.2f}" for u, t in pl) + "Z" for pl in polys)
            sen = sensor_in(v, p["b"])
            p["dots"] = [(sen[0], sen[1], sen[2] / .45)] if sen else []
        elif p["t"] == "rfid":
            x, y, w, h = p["b"]
            p["trace"] = F.trace_icon(v, (x + 3, y + 3, w - 6, h - 6), light=True)
        elif p["t"] == "rfidlite":
            x, y, w, h = p["b"]
            p["trace"] = F.trace_icon(g, (x + 4, y + 4, w - 8, h - 8), light=False)


def sketch(d, man):
    m = model(d, man)
    add_traces(m, man)
    return render(m), check(m)


if __name__ == "__main__":
    import json
    man = json.load(open(os.path.join(F.DEV, "devices.json"), encoding="utf-8"))["devices"]
    for a in sys.argv[1:]:
        d = next(x for x in man if x["article"].upper() == a.upper())
        svg, rep = sketch(d, man)
        open(os.path.join(F.DEV, d["image"].rsplit(".", 1)[0] + ".svg"), "w", encoding="utf-8").write(svg)
        print(f"{d['article']:22} {rep}")
