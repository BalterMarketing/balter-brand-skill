#!/usr/bin/env python3
"""
One library of printed icons for every device sketch.

An icon is traced once, from the clearest photo that carries it, and kept in assets/icons/icon-library.json
as polygons normalised to the icon's own box. Every other device that carries the same icon gets this
drawing, placed in the box measured on its own photo: same shape everywhere, true size and place.
A mark is matched to the library by shape (overlap of the two drawings at a common size); a mark that
matches nothing keeps its own trace.

    python3 scripts/icon_library.py            # rebuild the library from its source photos
"""
import json
import os
import re
import sys

import cv2
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
LIB = os.path.normpath(os.path.join(HERE, "..", "assets", "icons", "icon-library.json"))
N = 48
_lib = None


def polys_of(path):
    out = []
    for seg in path.split("Z"):
        pts = re.findall(r"(-?\d+\.?\d*) (-?\d+\.?\d*)", seg)
        if len(pts) >= 3:
            out.append([(float(a), float(b)) for a, b in pts])
    return out


def bbox(polys):
    xs = [p[0] for pl in polys for p in pl]
    ys = [p[1] for pl in polys for p in pl]
    return min(xs), min(ys), max(xs) - min(xs), max(ys) - min(ys)


def normalise(path):
    pl = polys_of(path)
    if not pl:
        return None
    x, y, w, h = bbox(pl)
    w, h = max(w, 1e-6), max(h, 1e-6)
    return dict(polys=[[((px - x) / w, (py - y) / h) for px, py in p] for p in pl], ar=w / h)


def raster(norm):
    """The drawing at a common size, aspect kept, centred."""
    img = np.zeros((N, N), np.uint8)
    ar = norm["ar"]
    w, h = (N - 4, (N - 4) / ar) if ar >= 1 else ((N - 4) * ar, N - 4)
    ox, oy = (N - w) / 2, (N - h) / 2
    cnts = [np.array([[ox + u * w, oy + t * h] for u, t in p], np.int32) for p in norm["polys"]]
    cv2.drawContours(img, cnts, -1, 255, -1)       # even-odd approximated by drawing holes after
    if len(cnts) > 1:
        img = np.zeros((N, N), np.uint8)
        for c in cnts:
            m = np.zeros((N, N), np.uint8)
            cv2.fillPoly(m, [c], 255)
            img ^= m
    return cv2.GaussianBlur(img, (5, 5), 1.2) > 60


def load():
    global _lib
    if _lib is None:
        _lib = json.load(open(LIB, encoding="utf-8")) if os.path.exists(LIB) else {}
        for v in _lib.values():
            v["_r"] = raster(v)
    return _lib


def match(path, min_iou=.6):
    """The library icon this traced mark is, or None."""
    n = normalise(path)
    if not n:
        return None, 0.0
    r = raster(n)
    best, score = None, 0.0
    for name, v in load().items():
        if not (.67 < n["ar"] / v["ar"] < 1.5):
            continue
        inter, union = (r & v["_r"]).sum(), (r | v["_r"]).sum()
        s = inter / union if union else 0.0
        if s > score:
            best, score = name, s
    return (best, score) if score >= min_iou else (None, score)


def place(name, box):
    x, y, w, h = box
    v = load()[name]
    return " ".join("M" + " L".join(f"{x + u * w:.2f} {y + t * h:.2f}" for u, t in p) + "Z" for p in v["polys"])


def reuse(path, min_iou=.6):
    """Replace a traced mark by its library icon, fitted to the mark's measured box."""
    name, _ = match(path, min_iou)
    if not name:
        return path, None
    return place(name, bbox(polys_of(path))), name


# ------------------------------------------------------------------ building the library
def build():
    import flat_model as FM
    import station_model as S
    import touch_flat as T
    man = json.load(open(os.path.join(HERE, "..", "assets", "devices", "devices.json"), encoding="utf-8"))["devices"]
    dev = lambda a: next(x for x in man if x["article"] == a)  # noqa: E731
    lib = {}

    def put(name, src, path):
        n = normalise(path)
        if n:
            lib[name] = dict(src=src, **n)

    # status display of the stations: bell, call, door
    for (name, *_), seg in zip([("bell",), ("call",), ("door",)], S._icon_paths(man)):
        put(name, S.ICON_MASTER, seg)
    # flat EVO touch units: the QUICK carries the full set, in clean grey print
    T.REUSE = False
    m = T.model(dev("EVO-QUICK-4.3M"))
    T.REUSE = True
    names = {}
    for path in m["marks"]:
        x, y, w, h = bbox(polys_of(path))
        names[(x, y)] = path
    row = sorted([k for k in names if names[k]], key=lambda k: (round(k[1] / 40), k[0]))
    q = [names[k] for k in row]
    for name, path in zip(["apps", "person", "door-touch", "key", "call-wave"], q):
        put(name, "EVO-QUICK-4.3M", path)
    # EVO HD MINI (black): call and hang-up keys
    mm = FM.model(dev("EVO-HD-MINI-BLACK-4.3M"), man)
    FM.add_traces(mm, man, reuse=False)
    for name, mk in zip(["call-key", "hangup"], sorted([k for k in mm["marks"] if k["t"] == "button"], key=lambda k: k["c"][1])):
        if mk.get("trace"):
            put(name, "EVO-HD-MINI-BLACK-4.3M", mk["trace"])
    # EVO HD Talk: key, bell, apps
    tk = FM.model(dev("EVO-HD-TALK"), man)
    FM.add_traces(tk, man, reuse=False)
    for name, path in zip(["key-talk", "bell-talk", "apps-talk"], tk.get("btn_traces", [])):
        if path:
            put(name, "EVO-HD-TALK", path)
    # EVO HD 7M: night and message LEDs
    m7 = FM.model(dev("EVO-HD-7M"), man)
    FM.add_traces(m7, man, reuse=False)
    for mk in m7["marks"]:
        if mk.get("glyph") in ("moon", "mail") and mk.get("trace"):
            put(mk["glyph"], "EVO-HD-7M", mk["trace"])
    # one drawing per symbol: an icon that is the same as one already kept is dropped
    kept = {}
    for k, v in lib.items():
        r = raster(v)
        if any(((r & kr).sum() / max((r | kr).sum(), 1)) >= .8 for kr in (raster(x) for x in kept.values())):
            continue
        kept[k] = v
    lib = kept
    os.makedirs(os.path.dirname(LIB), exist_ok=True)
    json.dump(lib, open(LIB, "w", encoding="utf-8"), ensure_ascii=False, indent=0)
    print(len(lib), "icons:", ", ".join(f"{k} ({v['src']})" for k, v in lib.items()))


if __name__ == "__main__":
    build()
