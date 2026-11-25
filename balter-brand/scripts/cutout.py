#!/usr/bin/env python3
"""
Cut a product photo shot on a plain white background into a transparent PNG for the device library.

The background is every near-white pixel connected to the image border (flood fill), so white parts
inside the device stay. The largest object is kept, holes are filled, the edge gets a 1 px feather and
the result is trimmed to the device.

    python3 scripts/cutout.py <photo> <out.png> [--tol 14]
"""
import sys

import numpy as np
from PIL import Image
from scipy import ndimage


def cutout(src, out, tol=14):
    im = Image.open(src).convert("RGB")
    a = np.asarray(im).astype(int)
    near_white = (255 - a).max(-1) <= tol
    lab, _ = ndimage.label(near_white)
    border = set(np.unique(np.r_[lab[0], lab[-1], lab[:, 0], lab[:, -1]])) - {0}
    bg = np.isin(lab, list(border))
    obj = ndimage.binary_opening(~bg, iterations=1)
    lab, n = ndimage.label(obj)
    if n == 0:
        raise SystemExit("nothing found")
    sizes = ndimage.sum(obj, lab, range(1, n + 1))
    keep = lab == (1 + int(np.argmax(sizes)))
    keep = ndimage.binary_fill_holes(keep)
    alpha = ndimage.gaussian_filter(keep.astype(float), 0.6)
    alpha = np.clip((alpha - 0.15) / 0.7, 0, 1)
    rgba = np.dstack([a, (alpha * 255).round()]).astype(np.uint8)
    ys, xs = np.where(keep)
    rgba = rgba[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    Image.fromarray(rgba).save(out, optimize=True)
    return rgba.shape[1], rgba.shape[0]


if __name__ == "__main__":
    tol = 14
    if "--tol" in sys.argv:
        i = sys.argv.index("--tol"); tol = int(sys.argv[i + 1]); del sys.argv[i:i + 2]
    print(cutout(sys.argv[1], sys.argv[2], tol))
