#!/usr/bin/env python3
"""
Monitors, the Talk audio station and the Touch door station as technical sketches.

Same method as station_model.py: every part is found on the real photo and drawn as one clean symbol
in the three tones (grey body, black glass and buttons, white light fields), with the real BALTER logo
where it sits on the device. The screen is drawn dark; the Touch station keeps a plain outline of its
call list, because on that station the screen is how a visitor rings.

Black twins share the geometry of their white twin: the parts that are hard to see on black (the screen
edge, the handset seam) are taken from the twin; logo, buttons and LEDs are found on the black photo.

    python3 scripts/flat_model.py EVO-HD-7M EVO-HD-TALK ...   # writes assets/devices/<article>.svg
"""
import os
import re
import sys

import cv2
import numpy as np
from scipy import ndimage

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sketch_fit as F  # noqa: E402

INK = "#111111"
DARK = "#111111"
BODY = {"white": "#F2F2F2", "black": "#3A3A3A", "steel": "#D9D9D9"}
TWIN = {"EVO-HD-7M-BLACK": "EVO-HD-7M", "EVO-HD-MINI-BLACK-4.3M": "EVO-HD-MINI-4.3M",
        "EVO-HD-PRO-7B": "EVO-HD-PRO-7W", "EVO-HD-BLACK-TALK": "EVO-HD-TALK",
        "EVO-7M-BLACK": "EVO-7M", "EVO-QUICK-BLACK": "EVO-QUICK-4.3M"}
# buttons and LEDs read better on one twin than on the other (white-on-white rings, LEDs in a black glare):
# take them from the clearer photo, the logo always from the device's own photo
MARKS_SRC = {"EVO-HD-7M-BLACK": "EVO-HD-7M", "EVO-HD-MINI-4.3M": "EVO-HD-MINI-BLACK-4.3M", "EVO-HD-PRO-7B": "EVO-HD-PRO-7W"}

GLYPH = {   # 24x24, stroked
    "bell": "M6.5 16.5h11l-1.4-2.2V10.8a4.1 4.1 0 0 0-8.2 0v3.5z M10.4 18.8a1.6 1.6 0 0 0 3.2 0",
    "call": "M8 5h2.4l1.2 3.4-1.7 1.1a9 9 0 0 0 4.6 4.6l1.1-1.7 3.4 1.2V16a1.8 1.8 0 0 1-1.9 1.8A12.6 12.6 0 0 1 6.2 6.9 1.8 1.8 0 0 1 8 5z M15 5.5a4 4 0 0 1 3.5 3.5 M15 2.8a6.8 6.8 0 0 1 6.2 6.2",
    "hangup": "M3.5 13.5c4.8-4 12.2-4 17 0l-1.6 2.6-3.2-1v-2.3a11 11 0 0 0-7.4 0v2.3l-3.2 1z",
    "key": "M3.5 12h9 M7 12v2.6 M10 12v2 M17 12m-3.6 0a3.6 3.6 0 1 0 7.2 0a3.6 3.6 0 1 0-7.2 0",
    "apps": "M4.5 4.5h6v6h-6z M4.5 13.5h6v6h-6z M13.5 13.5h6v6h-6z M16.5 3.6l3.4 3.4-3.4 3.4-3.4-3.4z",
    "moon": "M15.5 4.5a7.5 7.5 0 1 0 4 12.8A6.2 6.2 0 0 1 15.5 4.5z",
    "mail": "M4 6.5h16v11H4z M4 6.5l8 6 8-6",
    "rfid": "M12 12m-1.6 0a1.6 1.6 0 1 0 3.2 0a1.6 1.6 0 1 0-3.2 0 M8 8.5a5 5 0 0 0 0 7 M16 8.5a5 5 0 0 1 0 7 M5.2 6a8.6 8.6 0 0 0 0 12 M18.8 6a8.6 8.6 0 0 1 0 12",
    "keypad": "M6 6h.01M12 6h.01M18 6h.01M6 12h.01M12 12h.01M18 12h.01M6 18h.01M12 18h.01M18 18h.01",
    "contacts": "M5 3.5h12.5v17H5z M11.2 9.5m-2.3 0a2.3 2.3 0 1 0 4.6 0a2.3 2.3 0 1 0-4.6 0 M7.6 16.2a3.8 3.8 0 0 1 7.2 0 M19.5 7v3",
    "up": "M7 14.5l5-5 5 5", "down": "M7 9.5l5 5 5-5",
    "search": "M10.5 10.5m-5 0a5 5 0 1 0 10 0a5 5 0 1 0-10 0 M14.2 14.2l4.6 4.6",
}


def load(d):
    im = cv2.imread(os.path.join(F.DEV, d["image"]), cv2.IMREAD_UNCHANGED)
    alpha = im[..., 3] > 40
    img = im[..., :3]
    g = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    ys, xs = np.nonzero(alpha)
    box = (int(xs.min()), int(ys.min()), int(xs.max() - xs.min() + 1), int(ys.max() - ys.min() + 1))
    return img, alpha, g, box


def blobs(mask, min_area=6):
    lab, n = ndimage.label(mask)
    out = []
    for i, sl in enumerate(ndimage.find_objects(lab), 1):
        c = lab[sl] == i
        a = int(c.sum())
        if a >= min_area:
            out.append(dict(x=sl[1].start, y=sl[0].start, w=c.shape[1], h=c.shape[0], a=a))
    return out


def corner_r(alpha, box):
    bx, by, bw, bh = box
    k = 0
    while k < min(bw, bh) // 4 and not alpha[by + k, bx + k]:
        k += 1
    return k * 3.41


def logo_in(g, alpha, region, body_L):
    """The logo: a short row of letters plus the eagle, wider than tall, contrasting with the body."""
    x0, y0, x1, y1 = [int(v) for v in region]
    m = np.zeros_like(alpha)
    m[y0:y1, x0:x1] = (np.abs(g[y0:y1, x0:x1].astype(int) - body_L) > 45) & alpha[y0:y1, x0:x1]
    m = cv2.dilate(m.astype(np.uint8), np.ones((3, 13))) > 0
    best = None
    for b in blobs(m, 30):
        if 3 < b["w"] / max(b["h"], 1) < 9 and (best is None or b["w"] > best[2]):
            best = (b["x"] + 6, b["y"] + 1, b["w"] - 12, b["h"] - 2)
    return best


def logo_h(box, colour):
    """The real logo, horizontal, fitted into box."""
    src = open(F.LOGO, encoding="utf-8").read()
    vb = [float(v) for v in re.search(r'viewBox="([^"]+)"', src).group(1).split()]
    inner = re.search(r"<g[^>]*id=\"Layer_1-2\"[^>]*>(.*)</g>\s*</svg>", src, re.S)
    body = inner.group(1) if inner else re.search(r"<svg[^>]*>(.*)</svg>", src, re.S).group(1)
    body = re.sub(r'class="cls-2"', f'fill="{colour}" fill-rule="evenodd"', body)
    body = re.sub(r'class="cls-1"', f'fill="{colour}"', body)
    x, y, w, h = box
    sc = min(w / vb[2], h / vb[3])
    return f'<g transform="translate({x + (w - vb[2] * sc) / 2:.2f} {y + (h - vb[3] * sc) / 2:.2f}) scale({sc:.4f})">{body}</g>'


# ------------------------------------------------------------------ models
def monitor(d, img, alpha, g, box):
    bx, by, bw, bh = box
    dark = blobs((g < 70) & alpha, 500)
    scr = max(dark, key=lambda b: b["a"])
    screen = (scr["x"], scr["y"], scr["w"], scr["h"])
    return dict(screen=screen, **monitor_marks(img, alpha, g, box, screen))


def monitor_marks(img, alpha, g, box, screen):
    bx, by, bw, bh = box
    sx, sy, sw_, sh = screen
    inner = cv2.erode(alpha.astype(np.uint8), np.ones((11, 11))) > 0
    off = inner.copy()
    off[max(0, sy - 6):sy + sh + 6, max(0, sx - 6):sx + sw_ + 6] = False
    body_L = float(np.median(g[off]))
    logo = None
    for reg in ((bx, by, bx + bw * .45, sy), (bx, sy + sh, bx + bw * .5, by + bh)):
        logo = logo or logo_in(g, alpha & off, reg, body_L)
    mask = (np.abs(g.astype(int) - body_L) > 28) & off
    if logo:
        x, y, w, h = logo
        mask[y - 4:y + h + 4, x - 8:x + w + 8] = False
    marks = []
    for b in blobs(mask, 5):
        w, h = b["w"], b["h"]
        dia = (w + h) / 2
        if not (.55 < w / h < 1.8) or dia > bw * .12:
            continue
        fill = b["a"] / (w * h)
        cx, cy = b["x"] + w / 2, b["y"] + h / 2
        if dia >= bw * .062:
            marks.append(dict(t="button", c=(cx, cy), r=dia / 2))
        elif dia >= bw * .035 and fill < .6:
            marks.append(dict(t="ring", c=(cx, cy), r=dia / 2))
        elif dia < bw * .035:
            marks.append(dict(t="dot", c=(cx, cy), r=dia / 2))
    # merge pieces of one button (glyph + rim)
    out = []
    for m_ in sorted(marks, key=lambda m_: -m_["r"]):
        if any(np.hypot(m_["c"][0] - o["c"][0], m_["c"][1] - o["c"][1]) < o["r"] for o in out):
            continue
        out.append(m_)
    # status LEDs above the screen, right: faint on white, so colour counts too
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    led = ((np.abs(g.astype(int) - body_L) > 18) | ((hsv[..., 1] > 40) & (hsv[..., 2] > 60))) & off
    led[sy - 4:] = False
    led[:, :int(sx + sw_ * .55)] = False
    row = [b for b in blobs(cv2.dilate(led.astype(np.uint8), np.ones((3, 3))) > 0, 4)
           if .5 < b["w"] / b["h"] < 2 and b["w"] < bw * .04]
    if len(row) >= 2:
        out = [m_ for m_ in out if not (m_["c"][1] < sy and m_["c"][0] > sx + sw_ * .55)]
        row.sort(key=lambda b: b["x"])
        names = ["dot", "moon", "mail"] if len(row) == 3 else ["dot"] * len(row)
        for b, name in zip(row, names):
            mk = dict(t="dot", c=(b["x"] + b["w"] / 2, b["y"] + b["h"] / 2), r=max(b["w"], b["h"]) / 2)
            if name != "dot":
                mk["glyph"] = name
            else:
                mk["r"] = min(mk["r"], 3)
            out.append(mk)
    btn = sorted([m_ for m_ in out if m_["t"] == "button"], key=lambda m_: m_["c"][1])
    for m_, name in zip(btn, ["call", "hangup"]):
        m_["glyph"] = name
    return dict(logo=logo, marks=out, body_L=body_L)


def talk(d, img, alpha, g, box):
    bx, by, bw, bh = box
    gs = g.astype(np.float32)
    gx = np.abs(cv2.Sobel(gs, cv2.CV_32F, 1, 0, ksize=3))
    gy = np.abs(cv2.Sobel(gs, cv2.CV_32F, 0, 1, ksize=3))
    rows = slice(int(bh * .45), int(bh * .7))
    lo, hi = int(bx + bw * .5), int(bx + bw * .72)
    split = lo + int(np.argmax(gx[rows, lo:hi].mean(0)))
    full = [y for y in range(bh) if alpha[y, bx + 5:split - 5].mean() > .9]
    hs = (bx, min(full), split - bx - 2, max(full) - min(full) + 1)
    bfull = [y for y in range(bh) if alpha[y, split + 8:bx + bw - 4].mean() > .9]
    base = (split + 1, min(bfull), bx + bw - split - 1, max(bfull) - min(bfull) + 1)
    pr = gy[:, base[0] + 8:base[0] + base[2] - 8].mean(1)
    y0 = int(base[1] + base[3] * .25)
    step = y0 + int(np.argmax(pr[y0:int(base[1] + base[3] * .55)]))
    return dict(handset=hs, base=base, step=step, **talk_marks(img, alpha, g, box, hs, base))


def talk_marks(img, alpha, g, box, hs, base):
    bx, by, bw, bh = box
    x0 = base[0]
    cc = cv2.HoughCircles(cv2.GaussianBlur(g[:, x0:], (5, 5), 1.2), cv2.HOUGH_GRADIENT, 1, base[2] * .4,
                          param1=60, param2=20, minRadius=int(base[2] * .14), maxRadius=int(base[2] * .3))
    buttons = sorted([(x0 + x, y, r) for x, y, r in cc[0]], key=lambda b: b[1]) if cc is not None else []
    if buttons:
        rm = float(np.median([b[2] for b in buttons]))
        buttons = [(x, y, rm) for x, y, _ in buttons]
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    sat = (hsv[..., 1] > 70) & (hsv[..., 2] > 80) & alpha
    sat[int(base[1] + base[3] * .15):] = False
    led = max(blobs(sat, 6), key=lambda b: b["a"], default=None)
    body_L = float(np.median(g[hs[1] + 20:hs[1] + hs[3] // 2, hs[0] + 10:hs[0] + hs[2] - 10]))
    logo = logo_in(g, alpha, (hs[0], hs[1] + hs[3] * .8, hs[0] + hs[2], hs[1] + hs[3]), body_L)
    # cable below the handset: coil (wide) then the wire
    below = alpha[hs[1] + hs[3]:, hs[0]:hs[0] + hs[2]]
    widths = below.sum(1)
    ys = np.nonzero((widths > 0) & (widths < hs[2] * .4))[0]   # skip the handset's rounded lower edge
    cable = None
    if len(ys):
        cols = np.nonzero(below[ys[0] + 2])[0]
        coil_end = ys[0] + int(np.argmax(widths[ys[0]:] < widths[ys[0]] * .6)) if (widths[ys[0]:] < widths[ys[0]] * .6).any() else ys[-1]
        wire = np.nonzero(below[min(len(below) - 1, coil_end + 5)])[0]
        cable = dict(x=hs[0] + float(wire.mean() if len(wire) else cols.mean()), cw=float(len(cols)),
                     y0=hs[1] + hs[3] + ys[0], y1=hs[1] + hs[3] + coil_end, y2=hs[1] + hs[3] + ys[-1],
                     ww=float(max(2, len(wire))))
    return dict(buttons=buttons, led=(led["x"], led["y"], led["w"], led["h"]) if led else None, logo=logo, cable=cable)


def touch(d, img, alpha, g, box):
    bx, by, bw, bh = box
    dark = blobs((g < 70) & alpha, 500)
    gl = max(dark, key=lambda b: b["a"])
    glass = (gl["x"], gl["y"], gl["w"], gl["h"])
    gx_, gy_, gw, gh = glass
    gsub = g[gy_:gy_ + gh, gx_:gx_ + gw]
    glass_L = float(np.median(gsub))
    # camera dome in the top of the glass
    top = cv2.GaussianBlur(g[gy_:gy_ + int(gh * .2), gx_:gx_ + gw], (5, 5), 1.2)
    cc = cv2.HoughCircles(top, cv2.HOUGH_GRADIENT, 1, gw, param1=60, param2=20, minRadius=int(gw * .08), maxRadius=int(gw * .18))
    cam = (gx_ + cc[0][0][0], gy_ + cc[0][0][1], cc[0][0][2]) if cc is not None else None
    # screen: the lighter field inside the glass
    lt = (g > glass_L + 25) & alpha
    lt[:gy_ + int(gh * .2)] = False
    lt[gy_ + gh:] = False
    lt[:, :gx_] = False
    lt[:, gx_ + gw:] = False
    lt = cv2.morphologyEx(lt.astype(np.uint8), cv2.MORPH_CLOSE, np.ones((15, 15))) > 0
    sc = max(blobs(lt, 2000), key=lambda b: b["a"])
    screen = (sc["x"], sc["y"], sc["w"], sc["h"])
    sx, sy, sw_, sh = screen
    rows, navs = [], []
    for b in blobs((g < 70) & alpha, 300):
        if not (sx <= b["x"] and b["x"] + b["w"] <= sx + sw_ and sy <= b["y"] < sy + sh):
            continue
        if b["w"] > sw_ * .6 and b["h"] < sh * .2:
            rows.append((b["x"], b["y"], b["w"], b["h"]))
    rows.sort(key=lambda r: r[1])
    # nav row: the three small keys under the list
    if rows:
        rh = rows[0][3]
        last = rows[-1][1] + rows[-1][3]
        ed = cv2.Canny(cv2.GaussianBlur(g, (3, 3), 0), 30, 80)
        band = ed[last + 4:last + int(rh * 1.6), sx:sx + sw_]
        pr = band.sum(0) > 2 * 255
        xs = np.nonzero(pr)[0]
        ny = last + 4
        hrow = np.nonzero(ed[last + 4:last + int(rh * 1.6), sx:sx + sw_].sum(1) > sw_ * .2 * 255)[0]
        if len(hrow) >= 2:
            ny0, ny1 = last + 4 + hrow[0], last + 4 + hrow[-1]
            k = 3
            gap = sw_ * .02
            w3 = (sw_ - gap * (k + 1)) / k
            navs = [(sx + gap + i * (w3 + gap), ny0, w3, ny1 - ny0) for i in range(k)]
    # small bits on the glass and the frame
    ltl = (g > glass_L + 60) & alpha
    gm = np.zeros_like(alpha)
    gm[gy_ + 4:gy_ + gh - 4, gx_ + 4:gx_ + gw - 4] = True
    sens = [b for b in blobs(ltl & gm, 4) if b["y"] < gy_ + gh * .2 and b["w"] < gw * .05 and
            (not cam or np.hypot(b["x"] - cam[0], b["y"] - cam[1]) > cam[2] * 1.3)]
    rf = [b for b in blobs(cv2.dilate((ltl & gm).astype(np.uint8), np.ones((5, 9))) > 0, 20)
          if b["y"] > sy + sh + 10 and b["w"] > b["h"] * 1.5]
    rfid = max(rf, key=lambda b: b["w"], default=None)
    frame_L = float(np.median(g[alpha & ~(cv2.dilate(((g < 70) & alpha).astype(np.uint8), np.ones((9, 9))) > 0)]))
    logo = logo_in(g, alpha, (bx, gy_ + gh + 4, bx + bw, by + bh), frame_L)
    fd = [b for b in blobs((np.abs(g.astype(int) - frame_L) > 60) & alpha & ~gm, 3)
          if b["y"] < gy_ and b["w"] < 10 and b["h"] < 10]
    return dict(glass=glass, cam=cam, screen=screen, rows=rows, navs=navs, sens=sens,
                rfid=(rfid["x"], rfid["y"], rfid["w"], rfid["h"]) if rfid else None, logo=logo,
                fdots=[(b["x"] + b["w"] / 2, b["y"] + b["h"] / 2, max(b["w"], b["h"]) / 2) for b in fd])


def model(d, man, own_marks=False):
    m = _model(d, man)
    src = MARKS_SRC.get(d["article"])
    if src and not own_marks and m["type"] == "monitor":
        t = model(next(x for x in man if x["article"] == src), man, own_marks=True)
        (sx0, sy0, sw0, sh0), (tx, ty, tw_, th_) = t["box"], m["box"]
        kx, ky = tw_ / sw0, th_ / sh0
        m["marks"] = [dict(mk, twin=True, c=(tx + (mk["c"][0] - sx0) * kx, ty + (mk["c"][1] - sy0) * ky), r=mk["r"] * kx) for mk in t["marks"]]
    return m


def _model(d, man):
    img, alpha, g, box = load(d)
    a, k = d["article"], d["kind"]
    mat = F.material_of(d)
    base = dict(article=a, name=d["name"], box=box, W=g.shape[1], H=g.shape[0], mat=mat, kind=k,
                rx=corner_r(alpha, box), img=img, alpha=alpha, g=g)
    if a in TWIN:
        tw = next(x for x in man if x["article"] == TWIN[a])
        t = model(tw, man, own_marks=True)
        (sx0, sy0, sw0, sh0), (tx, ty, tw_, th_) = t["box"], box
        kx, ky = tw_ / sw0, th_ / sh0
        B = lambda b: (tx + (b[0] - sx0) * kx, ty + (b[1] - sy0) * ky, b[2] * kx, b[3] * ky)  # noqa: E731
        if k == "monitor":
            screen = B(t["screen"])
            return dict(base, type="monitor", screen=screen, **monitor_marks(img, alpha, g, box, [int(v) for v in screen]))
        hs, bs = B(t["handset"]), B(t["base"])
        return dict(base, type="talk", handset=hs, base=bs, step=ty + (t["step"] - sy0) * ky,
                    **talk_marks(img, alpha, g, box, [int(v) for v in hs], [int(v) for v in bs]))
    if k == "monitor":
        return dict(base, type="monitor", **monitor(d, img, alpha, g, box))
    if k == "audiostation":
        return dict(base, type="talk", **talk(d, img, alpha, g, box))
    return dict(base, type="touch", **touch(d, img, alpha, g, box))


# ------------------------------------------------------------------ drawing
def render(m):
    W, H, mat = m["W"], m["H"], m["mat"]
    bx, by, bw, bh = m["box"]
    sw = max(2.0, min(W, H) * .006)
    black = mat == "black"
    body = BODY[mat]
    light = "#D4D4D4"
    o = []

    def R(x, y, w, h, rx, fill, stroke=INK, s=sw):
        o.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx:.1f}" fill="{fill}"'
                 + (f' stroke="{stroke}" stroke-width="{s:.1f}"' if stroke else "") + "/>")

    def C(x, y, r, fill, stroke=INK, s=sw):
        o.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" fill="{fill}"' + (f' stroke="{stroke}" stroke-width="{s:.1f}"' if stroke else "") + "/>")

    def G(name, cx, cy, size, col, s=1.6, fill="none"):
        k = size / 24
        o.append(f'<path d="{GLYPH[name]}" transform="translate({cx - 12 * k:.1f} {cy - 12 * k:.1f}) scale({k:.3f})" fill="{fill}" '
                 f'stroke="{col}" stroke-width="{s / k:.2f}" stroke-linecap="round" stroke-linejoin="round"/>')

    t = m["type"]
    if t == "monitor":
        R(bx + sw / 2, by + sw / 2, bw - sw, bh - sw, max(m["rx"], bw * .012), body)
        x, y, w, h = m["screen"]
        R(x, y, w, h, min(w, h) * .015, DARK)
        for mk in m["marks"]:
            (cx, cy), r = mk["c"], mk["r"]
            if mk["t"] == "button":
                C(cx, cy, r, body, "#6b6b6b" if black else INK, sw * .8)
                if mk.get("trace"):
                    o.append(f'<path d="{mk["trace"]}" fill="{light if black else INK}" fill-rule="evenodd"/>')
                elif mk.get("glyph"):
                    G(mk["glyph"], cx, cy, r * 1.15, light if black else INK, sw * .7)
            elif mk["t"] == "ring":
                C(cx, cy, r * .86, "none", light if black else INK, sw * .9)
            elif mk.get("trace"):
                o.append(f'<path d="{mk["trace"]}" fill="#9a9a9a" fill-rule="evenodd"/>')
            elif mk.get("glyph"):
                G(mk["glyph"], cx, cy, r * 2.2, "#9a9a9a", sw * .6)
            else:
                C(cx, cy, max(r, sw), light if black else INK, None)
        if m["logo"]:
            o.append(logo_h(m["logo"], "#E5E5E5" if black else INK))
    elif t == "talk":
        x, y, w, h = m["base"]
        R(x, y, w, h, w * .04, body)
        o.append(f'<path d="M{x + sw:.1f} {m["step"]:.1f}H{x + w - sw:.1f}" stroke="{INK}" stroke-width="{sw * .7:.1f}"/>')
        if m["led"]:
            lx, ly, lw, lh = m["led"]
            R(lx, ly, lw, lh, lw / 2, "#FFFFFF", INK, sw * .5)
        tr = m.get("btn_traces") or []
        for i, ((cx, cy, r), name) in enumerate(zip(m["buttons"], ["key", "bell", "apps"])):
            C(cx, cy, r, "#2A2A2A" if name != "key" else DARK, INK, sw * .8)
            if i < len(tr) and tr[i]:
                o.append(f'<path d="{tr[i]}" fill="{light}" fill-rule="evenodd"/>')
            else:
                G(name, cx, cy, r * 1.05, light, sw * .7)
        c = m["cable"]
        if c:
            ww = min(max(c["ww"] * .5, 2), 4)
            o.append(f'<path d="M{c["x"]:.1f} {c["y1"]:.1f}V{c["y2"]:.1f}" stroke="{INK}" stroke-width="{ww:.1f}" stroke-linecap="round"/>')
            R(c["x"] - c["cw"] / 2, c["y0"], c["cw"], c["y1"] - c["y0"], c["cw"] * .3, body)
            n = max(3, int((c["y1"] - c["y0"]) / (c["cw"] * .5)))
            for i in range(1, n):
                yy = c["y0"] + (c["y1"] - c["y0"]) * i / n
                o.append(f'<path d="M{c["x"] - c["cw"] / 2 + sw:.1f} {yy:.1f}H{c["x"] + c["cw"] / 2 - sw:.1f}" stroke="{INK}" stroke-width="{sw * .5:.1f}"/>')
        x, y, w, h = m["handset"]
        R(x + sw / 2, y + sw / 2, w - sw / 2, h - sw, w * .04, body)
        if m["logo"]:
            o.append(logo_h(m["logo"], "#E5E5E5" if black else INK))
    else:
        R(bx + sw / 2, by + sw / 2, bw - sw, bh - sw, bw * .015, body)
        x, y, w, h = m["glass"]
        R(x, y, w, h, w * .01, DARK)
        if m["cam"]:
            cx, cy, r = m["cam"]
            C(cx, cy, r, "#1E1E1E", "#4a4a4a", sw * .7)
            C(cx, cy, r * .56, "#2B2B2B", "#4a4a4a", sw * .5)
            C(cx, cy, r * .27, "#6b7280", None)
        for b in m["sens"]:
            C(b["x"] + b["w"] / 2, b["y"] + b["h"] / 2, max(b["w"], b["h"]) / 2, "#4a4a4a", None)
        x, y, w, h = m["screen"]
        R(x, y, w, h, w * .02, "#2A2A2A", "#5a5a5a", sw * .6)
        for rx_, ry, rw, rh in m["rows"]:
            R(rx_, ry, rw, rh, rh * .12, "#1A1A1A", "#6b6b6b", sw * .5)
            C(rx_ + rh * .55, ry + rh / 2, rh * .3, "#6b6b6b", None)
            o.append(f'<path d="M{rx_ + rw * .37:.1f} {ry + rh / 2:.1f}H{rx_ + rw * .7:.1f}" stroke="{light}" stroke-width="{rh * .1:.1f}" stroke-linecap="round"/>')
            G("bell", rx_ + rw - rh * .45, ry + rh / 2, rh * .45, light, sw * .5, light)
        for (nx, ny, nw, nh), name in zip(m["navs"], ["up", "search", "down"]):
            R(nx, ny, nw, nh, nh * .2, "#1A1A1A", "#6b6b6b", sw * .5)
            G(name, nx + nw / 2, ny + nh / 2, nh * .6, light, sw * .5)
        if m["navs"]:
            ny = m["navs"][0][1] + m["navs"][0][3]
            for fx, name in ((.3, "keypad"), (.7, "contacts")):
                G(name, x + w * fx, ny + (y + h - ny) * .42, (y + h - ny) * .38, light, sw * (1.4 if name == "keypad" else .6))
        if m["rfid"]:
            rx_, ry, rw, rh = m["rfid"]
            G("rfid", rx_ + rw / 2, ry + rh / 2, rw * .75, light, sw * .6)
        for cx, cy, r in m["fdots"]:
            C(cx, cy, max(r, 1.5), INK, None)
        if m["logo"]:
            o.append(logo_h(m["logo"], INK))
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" '
            f'aria-label="{m["article"]} · {m["name"]} (Skizze)">' + "".join(o) + "</svg>")


def check(m):
    """Chamfer distance of the main outlines to the photo's edges (equalised for black)."""
    g = m["g"]
    if m["mat"] == "black":
        g = cv2.createCLAHE(3.0, (8, 8)).apply(g)
    e = cv2.Canny(cv2.bilateralFilter(cv2.blur(g, (5, 1)), 9, 30, 9), 25, 70)
    dist = cv2.distanceTransform((e == 0).astype(np.uint8), cv2.DIST_L2, 3)
    H, W = g.shape
    errs = []

    def rect(role, b):
        mk = np.zeros((H, W), np.uint8)
        x, y, w, h = [int(round(v)) for v in b]
        cv2.rectangle(mk, (x, y), (x + w - 1, y + h - 1), 1, 1)
        errs.append((role, float(np.median(dist[mk > 0]))))

    def circ(role, cx, cy, r):
        mk = np.zeros((H, W), np.uint8)
        cv2.circle(mk, (int(round(cx)), int(round(cy))), int(round(r)), 1, 1)
        errs.append((role, float(np.median(dist[mk > 0]))))

    if m["type"] == "monitor":
        rect("screen", m["screen"])
        for mk in m["marks"]:   # marks taken from the twin are proven on the twin's photo
            if mk["t"] in ("button", "ring") and not mk.get("twin"):
                circ(mk["t"], *mk["c"], mk["r"])
    elif m["type"] == "talk":
        for b in m["buttons"]:
            circ("button", *b)
    else:
        rect("glass", m["glass"])
        rect("screen", m["screen"])
        for r in m["rows"]:
            rect("row", r)
        if m["cam"]:
            circ("camera", *m["cam"])
    mean = float(np.mean([v for _, v in errs])) if errs else 0.0
    worst = max(errs, key=lambda t: t[1]) if errs else ("-", 0.0)
    return dict(mean=round(mean, 2), worst=[worst[0], round(worst[1], 2)], n=len(errs), logo=bool(m.get("logo")))


ICON_FROM = {"EVO-HD-MINI-4.3M": "EVO-HD-MINI-BLACK-4.3M"}   # white-on-white print: shape taken from the black twin


def _move_path(path, src_c, src_r, dst_c, dst_r):
    import re as _re
    k = dst_r / src_r

    def pt(mo):
        x, y = float(mo.group(1)), float(mo.group(2))
        return f"{dst_c[0] + (x - src_c[0]) * k:.2f} {dst_c[1] + (y - src_c[1]) * k:.2f}"
    return _re.sub(r"(-?\d+\.?\d*) (-?\d+\.?\d*)", pt, path)


def add_traces(m, man=None, reuse=True):
    """Printed icons on buttons, status LEDs and the Talk keys: found on this device's own photo; an icon that
    is already in the icon library is drawn from there (same drawing on every device), placed in the box
    measured here."""
    _trace(m, man)
    if not reuse:
        return
    import icon_library as IL
    for mk in m.get("marks", []):
        if mk.get("trace"):
            mk["trace"] = IL.reuse(mk["trace"])[0]
    m["btn_traces"] = [IL.reuse(t)[0] if t else t for t in m.get("btn_traces", [])]


def _trace(m, man=None):
    img = m["img"]
    g = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    v = img.max(-1)
    black = m["mat"] == "black"
    if m["type"] == "monitor":
        for mk in m["marks"]:
            if not mk.get("glyph"):
                continue
            (cx, cy), r = mk["c"], mk["r"]
            if mk["t"] == "button":
                k = r * .72
                mk["trace"] = F.trace_icon(v if black else g, (cx - k, cy - k, 2 * k, 2 * k), light=black, tophat=True, level=.45)
            else:            # status icon (moon, mail): coloured LED print, a little larger frame
                k = r * 1.6
                mk["trace"] = F.trace_icon(g, (cx - k, cy - k, 2 * k, 2 * k), light=black, tophat=True, level=.4)
        src = ICON_FROM.get(m["article"])
        if src and man:
            t = model(next(x for x in man if x["article"] == src), man)
            _trace(t)
            sb = sorted([q for q in t["marks"] if q["t"] == "button"], key=lambda q: q["c"][1])
            db = sorted([q for q in m["marks"] if q["t"] == "button"], key=lambda q: q["c"][1])
            for a_, b_ in zip(sb, db):
                if a_.get("trace"):
                    b_["trace"] = _move_path(a_["trace"], a_["c"], a_["r"], b_["c"], b_["r"])
    elif m["type"] == "talk":
        m["btn_traces"] = []
        for cx, cy, r in m["buttons"]:
            k = r * .72
            m["btn_traces"].append(F.trace_icon(v, (cx - k, cy - k, 2 * k, 2 * k), light=True, tophat=True, level=.45))


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
        print(f"{d['article']:24} {rep}")
