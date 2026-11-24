#!/usr/bin/env python3
"""
Draw the vector illustration of every Balter device in assets/devices/devices.json.

Each device has two versions with the same file stem (the article number in lowercase):
    <article>.png   the real cut-out photo
    <article>.svg   the vector illustration, drawn here from the photo's proportions

The illustration is drawn by code from measured proportions of the real photo, never by AI.
Same canvas as the photo (viewBox = photo pixels), so both versions swap 1:1 in any layout.

    python3 scripts/device_vectors.py            # writes every .svg next to the photos
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
DEV = os.path.normpath(os.path.join(HERE, "..", "assets", "devices"))

DEFS = """<defs>
<linearGradient id="steel" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#e9e9e9"/><stop offset=".45" stop-color="#d2d2d2"/><stop offset=".7" stop-color="#e4e4e4"/><stop offset="1" stop-color="#bdbdbd"/></linearGradient>
<linearGradient id="dark" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#3a3a3a"/><stop offset=".5" stop-color="#262626"/><stop offset="1" stop-color="#1a1a1a"/></linearGradient>
<linearGradient id="glass" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#202020"/><stop offset=".55" stop-color="#0b0b0b"/><stop offset="1" stop-color="#000"/></linearGradient>
<linearGradient id="white" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#ffffff"/><stop offset="1" stop-color="#ededed"/></linearGradient>
<linearGradient id="screen" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#2a2a2a"/><stop offset=".6" stop-color="#121212"/><stop offset="1" stop-color="#050505"/></linearGradient>
<radialGradient id="lens" cx=".4" cy=".35" r=".7"><stop offset="0" stop-color="#5a6b80"/><stop offset=".35" stop-color="#1b2330"/><stop offset="1" stop-color="#000"/></radialGradient>
<linearGradient id="plate" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#ffffff"/><stop offset="1" stop-color="#e6e6e6"/></linearGradient>
</defs>"""

INK = "#0a0a0a"


class C:
    def __init__(self, w, h):
        self.w, self.h, self.o = w, h, []

    def r(self, x, y, w, h, fill, rx=0, stroke=None, sw=1, extra=""):
        st = f' stroke="{stroke}" stroke-width="{sw}"' if stroke else ""
        self.o.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx:.1f}" fill="{fill}"{st} {extra}/>')

    def c(self, x, y, r, fill, stroke=None, sw=1):
        st = f' stroke="{stroke}" stroke-width="{sw}"' if stroke else ""
        self.o.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" fill="{fill}"{st}/>')

    def p(self, d, fill="none", stroke=None, sw=1, extra=""):
        st = f' stroke="{stroke}" stroke-width="{sw}"' if stroke else ""
        self.o.append(f'<path d="{d}" fill="{fill}"{st} stroke-linecap="round" stroke-linejoin="round" {extra}/>')

    def t(self, x, y, s, size, fill=INK, weight=700, anchor="middle", font="Inter,Arial,sans-serif", extra=""):
        self.o.append(f'<text x="{x:.1f}" y="{y:.1f}" font-family="{font}" font-size="{size:.1f}" font-weight="{weight}" fill="{fill}" text-anchor="{anchor}" {extra}>{s}</text>')

    def svg(self, label):
        return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {self.w} {self.h}" role="img" aria-label="{label}">'
                + DEFS + "".join(self.o) + "</svg>")


# ---------------------------------------------------------------- parts
def brushed(c, x, y, w, h, n=26, col="#ffffff", op=.18):
    step = h / n
    for i in range(n):
        c.p(f"M{x} {y + i*step + step*.5:.1f}H{x+w}", stroke=col, sw=.6, extra=f'opacity="{op if i % 3 else op*.4}"')


def button(c, x, y, r, dark=False):
    c.c(x, y, r, "#2a2a2a" if dark else "#bdbdbd", stroke="#7a7a7a" if not dark else "#555", sw=r*.12)
    c.c(x, y, r*.72, "url(#steel)" if not dark else "#3a3a3a", stroke="#9a9a9a" if not dark else "#666", sw=r*.06)
    c.c(x, y, r*.12, "#5b8cff", None)


def nameplate(c, x, y, w, h, dark=False):
    c.r(x, y, w, h, "#111" if dark else "url(#plate)", rx=h*.12, stroke="#8a8a8a" if not dark else "#000", sw=max(1, h*.06))
    c.r(x + h*.12, y + h*.14, w - h*.24, h*.3, "#fff", rx=h*.08, extra='opacity=".55"')


def status_bar(c, x, y, w, h):
    c.r(x, y, w, h, "url(#glass)", rx=h*.15)
    icons = [.22, .45, .68]
    for i, fx in enumerate(icons):
        c.c(x + w*fx, y + h/2, h*.16, "none", stroke="#6b7280", sw=h*.06)
    c.c(x + w*.88, y + h/2, h*.1, "#3a3a3a")


def camera(c, cx, cy, s, small=False):
    # speaker slot, lens, microphone lines
    c.r(cx - s*.9, cy - s*1.25, s*1.8, s*.42, "url(#white)", rx=s*.21, stroke="#8a8a8a", sw=s*.05)
    c.c(cx, cy, s*.95, "#111", stroke="#5a5a5a", sw=s*.08)
    c.c(cx, cy, s*.62, "url(#lens)")
    c.c(cx - s*.2, cy - s*.22, s*.14, "#c9d6ea", None)


def mic(c, x, y, w, s):
    for k in (-1, 1):
        c.p(f"M{x} {y + k*s*.16:.1f}H{x+w}", stroke="#555", sw=s*.09)


def tab(c, x, y, w, h):
    c.r(x, y, w, h, "#f5f5f5", rx=h*.3, stroke="#9a9a9a", sw=1)


def logo_v(c, x, y, s, fill="#222"):
    c.t(x, y, "BALTER", s, fill, 800, "middle", extra=f'transform="rotate(-90 {x:.1f} {y:.1f})" font-style="italic" letter-spacing="1"')


# ---------------------------------------------------------------- families
def station(d, c):
    W, H = c.w, c.h
    dark = d.get("colour") == "schwarz"
    face = "url(#dark)" if dark else "url(#steel)"
    c.r(0, 0, W, H, face, rx=W*.012, stroke="#8f8f8f" if not dark else "#000", sw=2)
    brushed(c, 0, 0, W, H, n=60, op=.12 if not dark else .05)
    narrow = W / H < .45
    tab(c, W*.44, H*.022, W*.12, H*.018)
    tab(c, W*.44, H*.955, W*.12, H*.018)
    logo_v(c, W*.93, H*.86, W*.035, "#e5e5e5" if dark else "#333")
    n = d.get("buttons", 0)
    kind = d["kind"]
    if kind == "audio-tuerstation":
        cols, rows = (11, 5) if not narrow else (9, 5)
        gx0, gy0 = W*.26, H*.075
        dx = W*.48 / (cols - 1)
        for i in range(rows):
            for j in range(cols):
                c.c(gx0 + j*dx, gy0 + i*dx*.95, W*.011, "#2a2a2a")
        sb_y = H*(.27 if not narrow else .175)
    elif kind == "erweiterung":
        sb_y = None
    else:
        s = W*(.1 if not narrow else .12)
        cx, cy = W*(.33 if not narrow else .3), H*(.16 if not narrow else .1)
        camera(c, cx, cy, s)
        mic(c, cx + s*2, cy, W*.2, s)
        sb_y = H*(.235 if not narrow else .16)
    if sb_y is not None:
        status_bar(c, W*.24, sb_y, W*.52, H*(.05 if not narrow else .03))
    if "FN" in d["article"]:
        bx, by, bw, bh = W*.3, H*.31, W*.4, H*.25
        c.r(bx, by, bw, bh, "url(#glass)", rx=W*.02)
        c.p(f"M{bx+bw*.38} {by+bh*.2}h{bw*.24}M{bx+bw*.42} {by+bh*.26}h{bw*.16}", stroke="#d4d4d4", sw=W*.008)
        c.c(bx + bw/2, by + bh*.68, bw*.17, "none", stroke="#3b82f6", sw=W*.012)
    # call buttons
    if n:
        ph = H*(.045 if not narrow else .034)
        gap = H*(.075 if not narrow else .049)
        groups = [n] if n <= 4 else [4] * (n // 4) + ([n % 4] if n % 4 else [])
        if kind == "erweiterung":
            top = H*.07
            gg = (H*.86 - top - sum(g * gap for g in groups)) / max(1, len(groups) - 1) if len(groups) > 1 else 0
        else:
            top = H*.82 - n*gap if n <= 4 else H*(.38 if "FN" not in d["article"] else .62)
            gg = H*.035
        y = top
        for gi, g in enumerate(groups):
            for _ in range(g):
                nameplate(c, W*.24, y, W*.43, ph)
                button(c, W*.78, y + ph/2, ph*.62, dark)
                y += gap
            y += gg


def touch(d, c):
    W, H = c.w, c.h
    c.r(0, 0, W, H, "url(#steel)", rx=W*.012, stroke="#8f8f8f", sw=2)
    brushed(c, 0, 0, W, H, n=60, op=.12)
    c.r(W*.07, H*.035, W*.86, H*.93, "url(#glass)", rx=W*.03)
    c.c(W*.5, H*.09, W*.075, "#111", stroke="#444", sw=2)
    c.c(W*.5, H*.09, W*.045, "url(#lens)")
    sx, sy, sw, sh = W*.17, H*.2, W*.66, H*.58
    c.r(sx, sy, sw, sh, "url(#screen)", rx=W*.015, stroke="#333", sw=1.5)
    for i in range(5):
        y = sy + sh*.06 + i*sh*.13
        c.r(sx + sw*.05, y, sw*.9, sh*.105, "#2b2b2b", rx=sh*.02)
        c.c(sx + sw*.16, y + sh*.052, sh*.035, "#6b6b6b")
        c.r(sx + sw*.3, y + sh*.045, sw*.4, sh*.014, "#9a9a9a", rx=2)
    for k in (.3, .7):
        c.r(sx + sw*k - sw*.06, sy + sh*.8, sw*.12, sh*.08, "#d4d4d4", rx=4, extra='opacity=".8"')
    c.p(f"M{W*.45} {H*.885}h{W*.1}M{W*.47} {H*.9}h{W*.06}", stroke="#9a9a9a", sw=2)
    logo_v(c, W*.5, H*.985, W*.04, "#333")


def monitor7(d, c):
    W, H = c.w, c.h
    dark = d.get("colour") == "schwarz"
    pro = "PRO" in d["article"]
    c.r(2, 2, W-4, H-4, "#151515" if dark else "url(#white)", rx=W*.012, stroke="#000" if dark else "#cfcfcf", sw=3)
    if pro:
        sx, sy, sw, sh = W*.045, H*.06, W*.91, H*.86
    else:
        sx, sy, sw, sh = W*.15, H*.19, W*.7, H*.58
        c.t(W*.12, H*.12, "BALTER", H*.03, "#bbb" if dark else "#666", 800, "start", extra='font-style="italic"')
        for i, col in enumerate(("#9ca3af", "#60a5fa", "#22c55e")):
            c.c(W*(.78 + i*.04), H*.11, H*.011, col)
    c.r(sx, sy, sw, sh, "url(#screen)", rx=W*.006)
    t = "08:00" if pro else "10:06"
    c.t(sx + sw*.08, sy + sh*.33, t, sh*.2, "#f5f5f5", 500, "start")
    c.r(sx + sw*.08, sy + sh*.42, sw*.18, sh*.035, "#8a8a8a", rx=2)
    for i in range(3):
        for j in range(2):
            c.r(sx + sw*(.64 + j*.16), sy + sh*(.12 + i*.25), sw*.07, sh*.12, "#d9d9d9", rx=3, extra='opacity=".85"')
    for i in range(6):
        c.c(sx + sw*(.1 + i*.075), sy + sh*.88, sh*.035, "none", stroke="#bdbdbd", sw=1.6)


def mini(d, c):
    W, H = c.w, c.h
    dark = d.get("colour") == "schwarz"
    c.r(2, 2, W-4, H-4, "#151515" if dark else "url(#white)", rx=W*.012, stroke="#000" if dark else "#d4d4d4", sw=3)
    sx, sy, sw, sh = W*.13, H*.09, W*.74, H*.46
    c.r(sx, sy, sw, sh, "url(#screen)", rx=W*.006)
    c.t(sx + sw*.5, sy + sh*.48, "10:25", sh*.24, "#f5f5f5", 500)
    for k in range(3):
        c.c(sx + sw*(.08 + k*.12), sy + sh*.86, sh*.045, "none", stroke="#bdbdbd", sw=1.6)
    for k in range(3):
        c.c(W*(.22 + k*.13), H*.66, H*.022, "none", stroke="#9a9a9a" if not dark else "#777", sw=2.2)
    for k, y in enumerate((.62, .77)):
        c.c(W*.82, H*y, H*.045, "none", stroke="#cfcfcf" if not dark else "#555", sw=2.2)
    c.t(W*.17, H*.9, "BALTER", H*.035, "#9a9a9a" if not dark else "#aaa", 800, "start", extra='font-style="italic"')


def talk(d, c):
    W, H = c.w, c.h
    dark = d.get("colour") == "schwarz"
    body = "#1d1d1d" if dark else "url(#white)"
    edge = "#000" if dark else "#cfcfcf"
    c.r(W*.02, 2, W*.96, H*.84, body, rx=W*.06, stroke=edge, sw=3)
    c.r(W*.04, H*.01, W*.58, H*.82, "#262626" if dark else "#f7f7f7", rx=W*.08, stroke=edge, sw=2)
    c.p(f"M{W*.62} {H*.36}H{W*.96}", stroke=edge, sw=2)
    c.r(W*.74, H*.02, W*.03, H*.03, "#22c55e", rx=2)
    for i, col in enumerate(("#3b82f6", "#3a3a3a", "#3a3a3a")):
        c.c(W*.81, H*(.48 + i*.07), W*.07, col if i == 0 else ("#2b2b2b" if dark else "#4a4a4a"))
    c.t(W*.3, H*.66, "BALTER", W*.07, "#bbb" if dark else "#333", 800, extra='font-style="italic"')
    c.p(f"M{W*.3} {H*.83}C{W*.3} {H*.9} {W*.33} {H*.92} {W*.33} {H*.99}", stroke="#d4d4d4" if not dark else "#333", sw=W*.025)


def din_box(d, c, label, port=False, terms=None):
    W, H = c.w, c.h
    c.r(2, H*.08, W-4, H*.9, "url(#white)", rx=W*.015, stroke="#bdbdbd", sw=3)
    c.r(W*.06, 2, W*.38, H*.12, "url(#white)", rx=W*.01, stroke="#cfcfcf", sw=2)
    for y in (.2, .86):
        for i in range(40):
            c.r(W*(.04 + i*.023), H*y, W*.009, H*.04, "#3a3a3a", rx=1, extra='opacity=".7"')
    c.r(W*.06, H*.33, W*.52, H*.44, "#e6e6e6", rx=4, stroke="#9a9a9a", sw=1.5)
    c.t(W*.32, H*.5, label, H*.06, INK, 800)
    c.t(W*.32, H*.6, "BALTER", H*.045, "#333", 800, extra='font-style="italic"')
    if terms:
        for i, tt in enumerate(terms):
            x = W*(.42 + i*.04)
            c.r(x, H*.36, W*.032, H*.38, "#fff", rx=2, stroke="#9a9a9a")
            c.t(x + W*.016, H*.55, tt, H*.03, "#333", 600, extra=f'transform="rotate(-90 {x+W*.016:.1f} {H*.55:.1f})"')
    if port:
        c.r(W*.72, H*.38, W*.18, H*.28, "#1a1a1a", rx=4)
        c.r(W*.75, H*.43, W*.12, H*.16, "#4a4a4a", rx=2)
    c.c(W*.6, H*.14, W*.012, "#dc2626")


def c5001(d, c):
    din_box(d, c, "EVO-HD-C5001", terms=["BUS1 IM", "BUS2 IM", "BUS1 DS", "BUS2 DS"])


def dl(d, c):
    din_box(d, c, "EVO-HD-DL")


def wl(d, c):
    din_box(d, c, "EVO-HD-2WL", port=True)


def pro_module(d, c):
    W, H = c.w, c.h
    a = d["article"]
    glass = a.endswith("CAM")
    c.r(0, 0, W, H, "url(#glass)" if glass else "url(#steel)", rx=0, stroke="#111" if glass else "#8f8f8f", sw=3)
    if not glass:
        brushed(c, 0, 0, W, H, n=40, op=.14)
    band = H / 4

    def seam(i):
        c.p(f"M0 {band*i:.1f}H{W}", stroke="#8a8a8a", sw=2)
        c.p(f"M0 {band*i+2:.1f}H{W}", stroke="#fff", sw=1, extra='opacity=".6"')

    def plate(i, lit):
        if not lit:
            return
        y = band*i + band*.28
        c.r(W*.17, y, W*.66, band*.44, "#ffffff" if lit else "url(#steel)", rx=4, stroke="#7a7a7a", sw=2)
        if lit:
            c.r(W*.17, y, W*.66, band*.44, "none", rx=4, stroke="#e5e5e5", sw=6, extra='opacity=".7"')

    if glass:
        for x0, w0 in ((.15, .27), (.6, .27)):
            c.r(W*x0, H*.09, W*w0, H*.035, "#3a0d0d", rx=6)
        c.c(W*.5, H*.48, W*.13, "#111", stroke="#3a3a3a", sw=4)
        c.c(W*.5, H*.48, W*.09, "url(#lens)")
        for i in range(4):
            c.c(W*(.27 + i*.155), H*.8, W*.025, "none", stroke="#e5e5e5", sw=3)
    elif "AUD" in a:
        c.r(W*.18, band*.6, W*.3, band*.07, "#0d0d0d", rx=band*.035)
        n = 2 if "2K" in a else (1 if "1K" in a else 0)
        for i in range(4 - n, 4):
            if i:
                seam(i)
            plate(i, a.endswith("N"))
        if n:
            seam(4 - n)
    elif "KEY" in a:
        for i in range(4):
            if i:
                seam(i)
            plate(i, a.endswith("N"))
    elif "RFG" in a:
        c.r(W*.17, H*.17, W*.66, H*.73, "url(#glass)", rx=8)
        c.p(f"M{W*.43} {H*.3}h{W*.14}M{W*.46} {H*.34}h{W*.08}", stroke="#e5e5e5", sw=4)
        c.r(W*.34, H*.52, W*.32, H*.3, "#111", rx=10)
        c.c(W*.5, H*.67, W*.075, "none", stroke="#3b82f6", sw=5)
    elif "INF" in a:
        if a.endswith("KN"):
            c.r(W*.14, H*.14, W*.72, H*.72, "#ffffff", rx=6, stroke="#e5e5e5", sw=8)


def housing(d, c):
    W, H = c.w, c.h
    a = d["article"]
    if "FRAME" in a:
        c.r(0, 0, W, H, "url(#steel)", rx=W*.01, stroke="#8f8f8f", sw=2)
        brushed(c, 0, 0, W, H, n=60, op=.12)
        c.r(W*.12, H*.04, W*.76, H*.92, "#f5f5f5", rx=3, stroke="#9a9a9a", sw=2)
        return
    if a.endswith("ML"):
        c.p(f"M{W*.04} {H*.05}H{W*.96}V{H*.5}Q{W*.96} {H*.62} {W*.84} {H*.62}H{W*.16}Q{W*.04} {H*.62} {W*.04} {H*.5}Z", fill="#111")
        c.r(W*.13, H*.14, W*.74, H*.33, "#e5e5e5", rx=4)
        for x in (.12, .78):
            c.p(f"M{W*x} {H*.62}V{H*.9}Q{W*x} {H*.98} {W*(x+.05)} {H*.98}H{W*(x+.08)}V{H*.72}", stroke="#111", sw=W*.025)
        return
    c.r(2, 2, W-4, H-4, "#1a1a1a", rx=W*.05, stroke="#000", sw=3)
    c.r(W*.08, H*.03, W*.84, H*.94, "#0d0d0d", rx=W*.04, stroke="#2a2a2a", sw=2)
    if "F1M" in a:
        c.r(W*.22, H*.2, W*.56, H*.6, "#f2f2f2", rx=4, stroke="#2a2a2a", sw=W*.03)
        for x, y in ((.07, .05), (.93, .05), (.07, .95), (.93, .95)):
            c.c(W*x, H*y, W*.018, "#555")
        return
    if a.endswith("F3M") or a.endswith("S3M"):
        c.r(2, 2, W-4, H-4, "#111", rx=W*.03)
        for i in range(3):
            y0 = H*(.035 + i*.322)
            c.r(W*.14, y0 + H*.02, W*.72, H*.28, "#f2f2f2", rx=3, stroke="#2a2a2a", sw=W*.03)
        return
    holes = 3 if "3M" in a else 2
    for i in range(holes):
        c.c(W*.5, H*(.18 + i*(.64 / max(1, holes - 1))), W*.13, "#262626", stroke="#3a3a3a", sw=2)
    if "-L" in a or "LR" in a:
        c.r(0, H*.42, W*.08, H*.16, "#3a3a3a")
    if a.endswith("-R") or "LR" in a:
        c.r(W*.92, H*.42, W*.08, H*.16, "#3a3a3a")


def draw(d):
    w, h = d["px"]
    c = C(w, h)
    k, a = d["kind"], d["article"]
    if a.startswith("EVO-HD-TOUCH"):
        touch(d, c)
    elif k in ("video-tuerstation", "audio-tuerstation", "erweiterung"):
        station(d, c)
    elif k == "monitor" and "MINI" in a:
        mini(d, c)
    elif k == "monitor":
        monitor7(d, c)
    elif k == "audiostation":
        talk(d, c)
    elif a == "EVO-HD-C5001":
        c5001(d, c)
    elif a == "EVO-HD-DL":
        dl(d, c)
    elif a == "EVO-HD-2WL":
        wl(d, c)
    elif k == "pro-modul":
        pro_module(d, c)
    elif k == "gehaeuse":
        housing(d, c)
    else:
        return None
    return c.svg(f"{a} · {d['name']} (Illustration)")


def main():
    man = json.load(open(os.path.join(DEV, "devices.json"), encoding="utf-8"))
    n = 0
    for d in man["devices"]:
        s = draw(d)
        if not s:
            print("no drawing for", d["article"])
            continue
        fn = d["image"].rsplit(".", 1)[0] + ".svg"
        open(os.path.join(DEV, fn), "w", encoding="utf-8").write(s)
        d["vector"] = fn
        n += 1
    json.dump(man, open(os.path.join(DEV, "devices.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(n, "illustrations")


if __name__ == "__main__":
    main()
