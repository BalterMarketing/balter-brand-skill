#!/usr/bin/env python3
"""
Balter wiring plan (Verdrahtungsplan) generator — EVO HD, one Netzteil per sheet.

Reads a project spec (JSON) and draws the technical plan as one A3-landscape sheet
in the Balter house style: floor tabs and bands, real device pictures, one colour
per bus group, wires as two parallel conductors that never cross, terminal detail of
the EVO-HD-C5001, monitor connections, door opener, cable list, notes, legend and a
title block.

    python3 wiring_plan.py spec.json -o plan.svg            # images linked from ../assets
    python3 wiring_plan.py spec.json -o plan.svg --embed    # standalone, images inlined
    python3 wiring_plan.py spec.json -o plan.html --embed   # A3 page, print to PDF

Every technical statement printed on the sheet comes from FACTS below, which were
read from the EVO HD manual v3.2 and the C5001 rating plate. Do not add numbers
that are not in FACTS. See ../SKILL.md.
"""

import argparse
import base64
import json
import os
import sys
from html import escape

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.normpath(os.path.join(HERE, "..", "assets"))
DEVICES = json.load(open(os.path.join(ASSETS, "devices", "devices.json"), encoding="utf-8"))["devices"]
BY_ART = {d["article"].upper(): d for d in DEVICES}
STYLE = {"v": "photo"}          # "photo" or "vector", set from --style


def device(article, need_plan=True):
    """The library entry for an article; refuses devices the plan may not use."""
    d = BY_ART.get(article.upper())
    if not d:
        sys.exit(f"{article}: not in assets/devices/devices.json — add the real device first")
    if need_plan and not d.get("plan"):
        sys.exit(f"{article}: not cleared for wiring plans (plan: false in devices.json)")
    return d


def dev_img(article, need_plan=True):
    d = device(article, need_plan)
    f = d.get("vector") if STYLE["v"] == "vector" and d.get("vector") else d["image"]
    return "devices/" + f, d["px"][0] / d["px"][1]

# ---------------------------------------------------------------- facts (sourced)
FACTS = {
    "bus_cable": "J-Y(St)Y 2×2×0,8 mm² oder YR 0,8 mm²",
    "bus_cable_short": "J-Y(St)Y 2×2×0,8",
    "nt_in": "100–240 V~ · 0,6 A · 50–60 Hz",
    "nt_out": "BUS 32 V DC · 3,5 A",
    "lock_int": "12 V DC · max. 300 mA",
    "lock_ext": "30 V DC 2 A / 250 V AC 2 A",
    "max_units": 128,
    "max_monitors_per_unit": 4,
}

# ---------------------------------------------------------------- house colours
FLOOR_NAMES = ["EG", "1.OG", "2.OG", "3.OG", "4.OG", "5.OG"]
WIRE = {"EG": "#1D4ED8", "1.OG": "#EAB308", "2.OG": "#0EA5E9", "3.OG": "#DC2626",
        "4.OG": "#7C3AED", "5.OG": "#0D9488"}
BAND = {"EG": ("#F6E9E1", "#D7A68A"), "1.OG": ("#ECF3E5", "#A8C98C"),
        "2.OG": ("#E9E4E2", "#8F807C"), "3.OG": ("#EAF2F8", "#A9C8DD"),
        "4.OG": ("#F7F2E2", "#CDB66E"), "5.OG": ("#F2EEF8", "#B4A2D0")}
STATION = "#16A34A"
LOCKC = "#737373"
L_BROWN, N_BLUE = "#8B5A2B", "#2563EB"
INK, MUTED, HAIR, FAINT = "#0A0A0A", "#525252", "#D4D4D4", "#F5F5F5"
ACCENT = "#FB824B"

W, H = 1680, 1188              # A3 landscape at 4 px per mm
MONO = "'JetBrains Mono',ui-monospace,Menlo,monospace"
SANS = "Inter,'Helvetica Neue',Arial,sans-serif"


class Sheet:
    def __init__(self, embed, asset_href):
        self.o = []
        self.embed = embed
        self.asset_href = asset_href
        self.segments = []          # for the crossing check

    def add(self, s):
        self.o.append(s)

    def img(self, name, x, y, w, h, extra=""):
        if self.embed:
            with open(os.path.join(ASSETS, name), "rb") as fh:
                data = base64.b64encode(fh.read()).decode()
            mime = "image/svg+xml" if name.endswith(".svg") else "image/png"
            href = f"data:{mime};base64,{data}"
        else:
            href = f"{self.asset_href}/{name}"
        self.add(f'<image href="{href}" x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" {extra}/>')

    def text(self, x, y, s, size=11, weight=500, fill=INK, anchor="start", font=SANS, extra=""):
        self.add(f'<text x="{x:.1f}" y="{y:.1f}" font-family="{font}" font-size="{size}" '
                 f'font-weight="{weight}" fill="{fill}" text-anchor="{anchor}" {extra}>{escape(str(s))}</text>')

    # two conductors along an orthogonal path, never crossing each other
    def pair(self, pts, color, gap=2.4, width=1.5, group=None, dash=None):
        if group is not None:
            for a, b in zip(pts, pts[1:]):
                self.segments.append((a, b, group))
        for side in (-1, 1):
            p = offset(pts, side * gap)
            d = "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in p)
            da = f' stroke-dasharray="{dash}"' if dash else ""
            self.add(f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{width}" '
                     f'stroke-linejoin="round" stroke-linecap="round"{da}/>')


def offset(pts, d):
    """Offset an orthogonal polyline by d along its left normal."""
    def n(a, b):
        dx, dy = b[0] - a[0], b[1] - a[1]
        L = (dx * dx + dy * dy) ** 0.5 or 1
        return (dy / L, -dx / L)
    out = []
    for i, p in enumerate(pts):
        if i == 0:
            nx, ny = n(p, pts[1])
        elif i == len(pts) - 1:
            nx, ny = n(pts[i - 1], p)
        else:
            a, b = n(pts[i - 1], p), n(p, pts[i + 1])
            nx, ny = a[0] + b[0], a[1] + b[1]
            if abs(a[0]) > 0 and abs(b[0]) > 0 or abs(a[1]) > 0 and abs(b[1]) > 0:
                nx, ny = a          # straight on
        out.append((p[0] + nx * d, p[1] + ny * d))
    return out


def crossings(segments):
    """Count proper crossings between segments of different groups."""
    def inter(a, b, c, d):
        (x1, y1), (x2, y2), (x3, y3), (x4, y4) = a, b, c, d
        den = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
        if abs(den) < 1e-9:
            return False
        t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / den
        u = -((x1 - x2) * (y1 - y3) - (y1 - y2) * (x1 - x3)) / den
        return 0.001 < t < 0.999 and 0.001 < u < 0.999
    n = 0
    for i, (a, b, g) in enumerate(segments):
        for c, d, h in segments[i + 1:]:
            if g != h and inter(a, b, c, d):
                n += 1
    return n


# ---------------------------------------------------------------- drawing parts
def frame(s, spec):
    s.add(f'<rect x="0" y="0" width="{W}" height="{H}" fill="#fff"/>')
    s.add(f'<rect x="16" y="16" width="{W-32}" height="{H-32}" fill="none" stroke="{INK}" stroke-width="1"/>')
    s.add(f'<rect x="36" y="36" width="{W-72}" height="{H-72}" fill="none" stroke="{INK}" stroke-width="2"/>')
    cols, rows = 8, 6
    for i in range(cols):
        x = 36 + (W - 72) * (i + .5) / cols
        for y in (29, H - 23):
            s.text(x, y, i + 1, 10, 600, MUTED, "middle", MONO)
        if i:
            xx = 36 + (W - 72) * i / cols
            s.add(f'<path d="M{xx:.1f} 16V36M{xx:.1f} {H-36}V{H-16}" stroke="{INK}" stroke-width="1"/>')
    for j in range(rows):
        y = 36 + (H - 72) * (j + .5) / rows
        for x in (26, W - 26):
            s.text(x, y + 4, "ABCDEF"[j], 10, 600, MUTED, "middle", MONO)
        if j:
            yy = 36 + (H - 72) * j / rows
            s.add(f'<path d="M16 {yy:.1f}H36M{W-36} {yy:.1f}H{W-16}" stroke="{INK}" stroke-width="1"/>')


def r_tag(s, x, y):
    """Endwiderstand gesetzt."""
    s.add(f'<g><rect x="{x-9}" y="{y-8}" width="18" height="16" rx="3" fill="{INK}"/>'
          f'<text x="{x}" y="{y+4}" font-family="{MONO}" font-size="10" font-weight="700" fill="#fff" text-anchor="middle">R</text></g>')


def chip(s, x, y, label, fill=INK, ink="#fff", anchor="start", size=10):
    w = 7 + len(label) * size * 0.62
    x0 = x if anchor == "start" else x - w / 2
    s.add(f'<rect x="{x0:.1f}" y="{y-9}" width="{w:.1f}" height="17" rx="8.5" fill="{fill}"/>')
    s.text(x0 + w / 2, y + 3.5, label, size, 600, ink, "middle", MONO)
    return w


def lock_symbol(s, x, y):
    """Door opener (Türöffner) as the usual coil symbol."""
    s.add(f'<g fill="none" stroke="{INK}" stroke-width="1.6">'
          f'<rect x="{x}" y="{y}" width="34" height="22" rx="2"/>'
          f'<path d="M{x+6} {y+16}l6-10 6 10 6-10 6 10"/></g>')


def build(spec, embed=False, asset_href="assets"):
    s = Sheet(embed, asset_href)
    floors = spec["floors"]                       # bottom → top
    nf = len(floors)
    if not 1 <= nf <= 6:
        sys.exit("1 to 6 floors per sheet")
    names = [f.get("name", FLOOR_NAMES[i]) for i, f in enumerate(floors)]
    for f in floors:
        for u in f["units"]:
            if len(u["monitors"]) > FACTS["max_monitors_per_unit"]:
                sys.exit(f"{u['we']}: max. 4 Monitore je Wohneinheit")

    frame(s, spec)

    # ------------------------------------------------ geometry
    X0, X1 = 56, 1180               # main drawing area
    TAB_W, BAND_X = 34, 100
    Y_TOP = 60
    TECH_H = 226
    Y_TECH = 1188 - 36 - 196 - TECH_H - 10   # tech zone top
    gap = 12
    band_h = min(168, (Y_TECH - 18 - Y_TOP - gap * (nf - 1)) / nf)
    RISER_X0, LANE = 344, 14         # top floor riser is the leftmost
    MON_W, MON_H = 92, 64

    # ------------------------------------------------ floors
    taps = {}                        # floor index → list of tap x on bus, bus y
    reihe_links = []                 # (we, from, to, colour)
    for k in range(nf):              # k = 0 → top floor
        fi = nf - 1 - k
        name = names[fi]
        y = Y_TOP + k * (band_h + gap)
        fill, edge = BAND.get(name, ("#F5F5F5", "#A3A3A3"))
        s.add(f'<rect x="{X0}" y="{y:.1f}" width="{TAB_W}" height="{band_h:.1f}" rx="3" fill="{fill}" stroke="{edge}" stroke-width="1.4"/>')
        s.add(f'<text transform="translate({X0+TAB_W/2+6:.1f} {y+band_h/2:.1f}) rotate(-90)" font-family="{SANS}" font-size="17" font-weight="800" fill="{INK}" text-anchor="middle">{escape(name)}</text>')
        s.add(f'<rect x="{BAND_X}" y="{y:.1f}" width="{X1-BAND_X}" height="{band_h:.1f}" rx="3" fill="{fill}" stroke="{edge}" stroke-width="1.4"/>')

        units = floors[fi]["units"]
        bus_y = y + band_h - 20
        xs_start, xs_end = 330 + nf * LANE, X1 - 30
        widths = [len(u["monitors"]) * 250 for u in units]
        free = (xs_end - xs_start - sum(widths)) / (len(units) + 1)
        cx = xs_start + free
        tlist = []
        color = WIRE.get(name, INK)
        for u, wu in zip(units, widths):
            ux = cx
            s.text(ux, y + 24, u["we"], 15, 800, INK)
            reihe = len(u["monitors"]) > 1 and u.get("wiring", "reihe") == "reihe"
            prev = None
            for m_i, m in enumerate(u["monitors"]):
                mx = ux + m_i * 250
                my = y + 36
                s.img(dev_img(m.get("model", "EVO-HD-7M"))[0], mx, my, MON_W, MON_H)
                s.text(mx + MON_W + 10, my + 14, m.get("model", "EVO-HD-7M"), 10.5, 600, INK, font=MONO)
                role = ("Master" if m_i == 0 else "Slave") if len(u["monitors"]) > 1 else ""
                s.text(mx + MON_W + 10, my + 30, f"KT {u['kt']:02d} · {m_i+1}/4", 10, 500, MUTED, font=MONO)
                if role:
                    s.text(mx, my + MON_H + 14, role, 9.5, 700, INK, font=MONO)
                end = (not reihe) or m_i == len(u["monitors"]) - 1
                if end:
                    r_tag(s, mx + MON_W + 19, my + 46)
                bx = mx + MON_W / 2
                if m_i == 0 or not reihe:
                    tlist.append(bx)
                    s.pair([(bx, my + MON_H + 2), (bx, bus_y)], color, group=f"f{fi}")
                if reihe and prev is not None:
                    reihe_links.append((u['we'], m_i, m_i + 1, color))
                    # BUS_OUT of the previous monitor → BUS_IN of this one
                    y_r = my + MON_H - 10
                    s.pair([(prev + MON_W + 2, y_r), (mx - 2, y_r)], color, gap=1.8, width=1.2, group=f"r{fi}{m_i}")
                    s.text((prev + MON_W + mx) / 2, y_r - 8, "BUS_OUT → BUS_IN", 8.5, 600, MUTED, "middle", MONO)
                    wid = f"W{nf + 1 + len(reihe_links):02d}"
                    mid = (prev + MON_W + mx) / 2
                    s.add(f'<rect x="{mid-15}" y="{y_r+8}" width="30" height="15" rx="3" fill="#fff" stroke="{color}" stroke-width="1.2"/>')
                    s.text(mid, y_r + 19, wid, 9, 700, INK, "middle", MONO)
                prev = mx
            cx += wu + free
        taps[k] = (tlist, bus_y, color, name)

    # ------------------------------------------------ technical zone
    yT = Y_TECH
    s.add(f'<rect x="{X0}" y="{yT}" width="{TAB_W}" height="{TECH_H}" rx="3" fill="#F2F2F2" stroke="#A3A3A3" stroke-width="1.4"/>')
    s.add(f'<text transform="translate({X0+TAB_W/2+6:.1f} {yT+TECH_H/2:.1f}) rotate(-90)" font-family="{SANS}" font-size="15" font-weight="800" fill="{INK}" text-anchor="middle">TECHNIK</text>')
    tech_x = 470
    s.add(f'<rect x="{tech_x}" y="{yT}" width="{X1-tech_x}" height="{TECH_H}" rx="3" fill="#F5F5F5" stroke="#A3A3A3" stroke-width="1.4"/>')
    s.text(tech_x + 14, yT + 22, spec.get("technikraum", "Technikraum · Unterverteilung"), 11, 700, MUTED)
    s.text(BAND_X + 4, yT + 22, "Eingang · außen", 11, 700, MUTED)

    # Netzteil
    NT_W, NT_H = 118, 81
    nt_x, nt_y = 700, yT + 52
    s.add(f'<rect x="{nt_x-40}" y="{yT+32}" width="{NT_W+250}" height="{TECH_H-42}" rx="6" fill="none" stroke="#737373" stroke-width="1.2" stroke-dasharray="6 5"/>')
    s.text(nt_x + NT_W + 12, yT + 50, "Elektrokasten · DIN-Hutschiene", 10, 600, MUTED)
    # 230 V in at the top
    for i, c in enumerate((L_BROWN, N_BLUE)):
        x = nt_x + 18 + i * 8
        s.add(f'<path d="M{x} {nt_y+4}V{yT+32}" stroke="{c}" stroke-width="2"/>')
    s.img(dev_img("EVO-HD-C5001")[0], nt_x, nt_y, NT_W, NT_H)
    s.text(nt_x + NT_W + 12, nt_y + 26, "EVO-HD-C5001", 11, 700, INK, font=MONO)
    s.text(nt_x + NT_W + 12, nt_y + 42, "Netzteil 1", 10.5, 500, MUTED)
    s.text(nt_x + NT_W + 12, nt_y + 58, "230 V AC (L/N) von oben", 10.5, 500, MUTED)

    # terminal strip under the Netzteil: IM | DS
    ts_y = nt_y + NT_H + 4
    im_w = max(60, nf * LANE + 24)
    im_x = nt_x + 6
    ds_x = im_x + im_w + 10
    ds_w = 36
    for x0, w0, lab in ((im_x, im_w, "IM"), (ds_x, ds_w, "DS")):
        s.add(f'<rect x="{x0}" y="{ts_y}" width="{w0}" height="16" rx="2" fill="#E5E5E5" stroke="{INK}" stroke-width="1"/>')
        s.text(x0 + w0 / 2, ts_y + 12, lab, 9.5, 700, INK, "middle", MONO)
    strip_bottom = ts_y + 16

    # station
    st = spec["station"]
    st_h = 156
    st_src, st_asp = dev_img(st["model"])
    st_w = st_h * st_asp
    st_x, st_y = BAND_X + 14, yT + 34
    s.img(st_src, st_x, st_y, st_w, st_h)
    lx = st_x + st_w + 12
    s.text(lx, st_y + 14, st["model"], 11, 700, INK, font=MONO)
    s.text(lx, st_y + 30, "Video-Türstation", 10.5, 500, MUTED)
    s.text(lx, st_y + 46, f"KT 1–{st['buttons']} · Zählung von unten", 10, 500, MUTED)

    # collectors: nested from the left — top floor outermost
    col_y0 = strip_bottom + 14
    for k in range(nf):
        tlist, bus_y, color, name = taps[k]
        xr = RISER_X0 + k * LANE
        yc = col_y0 + (nf - 1 - k) * 10
        xt = im_x + 12 + (nf - 1 - k) * LANE
        pts = [(max(tlist), bus_y), (xr, bus_y), (xr, yc), (xt, yc), (xt, strip_bottom)]
        s.pair(pts, color, group=f"f{nf-1-k}")
        for t in tlist:
            s.add(f'<circle cx="{t:.1f}" cy="{bus_y:.1f}" r="5" fill="{color}" stroke="#fff" stroke-width="1.5"/>')
        # cable id on the riser
        cid = f"W{k+2:02d}"
        s.add(f'<rect x="{xr-15}" y="{bus_y+18}" width="30" height="15" rx="3" fill="#fff" stroke="{color}" stroke-width="1.2"/>')
        s.text(xr, bus_y + 29, cid, 9, 700, INK, "middle", MONO)

    # station bus: outermost of all, lowest, into DS
    ys = col_y0 + nf * 10 + 4
    sx = st_x + st_w / 2
    s.pair([(sx, st_y + st_h), (sx, ys), (ds_x + ds_w / 2, ys), (ds_x + ds_w / 2, strip_bottom)], STATION, group="st")
    s.add(f'<rect x="{sx+30}" y="{ys-8}" width="30" height="15" rx="3" fill="#fff" stroke="{STATION}" stroke-width="1.2"/>')
    s.text(sx + 45, ys + 3, "W01", 9, 700, INK, "middle", MONO)

    # door opener off the station
    lk = spec.get("lock", {"mode": "intern"})
    lkx, lky = lx + 2, st_y + 96
    lock_symbol(s, lkx, lky)
    s.pair([(st_x + st_w, lky + 11), (lkx - 1, lky + 11)], LOCKC, gap=1.8, width=1.2, group="lk")
    s.text(lkx + 44, lky + 9, "Türöffner", 10.5, 700, INK)
    s.text(lkx + 44, lky + 23, ("GND / LOCK+" if lk["mode"] == "intern" else "NO / COM"), 9.5, 500, MUTED, font=MONO)

    # ------------------------------------------------ right column: details
    RX, RW = 1196, 1644 - 1196 - 16
    def panel(y, h, letter, title):
        s.add(f'<rect x="{RX}" y="{y}" width="{RW}" height="{h}" rx="6" fill="#fff" stroke="{HAIR}" stroke-width="1.2"/>')
        s.add(f'<circle cx="{RX+20}" cy="{y+20}" r="11" fill="{INK}"/>')
        s.text(RX + 20, y + 24, letter, 11, 800, "#fff", "middle")
        s.text(RX + 40, y + 24, title, 12.5, 800, INK)

    # A · Netzteil terminals (from the rating plate)
    py = 56
    panel(py, 236, "A", "Klemmen EVO-HD-C5001")
    bx, by = RX + 40, py + 74
    s.add(f'<rect x="{bx}" y="{by}" width="{RW-80}" height="96" rx="8" fill="{FAINT}" stroke="{INK}" stroke-width="1.2"/>')
    # input
    labs_in = ["N", "N", "L", "L"]
    for i, l in enumerate(labs_in):
        x = bx + 14 + i * 26
        s.add(f'<rect x="{x}" y="{by-12}" width="20" height="18" rx="2" fill="#fff" stroke="{INK}"/>')
        s.text(x + 10, by + 1, l, 9.5, 700, INK, "middle", MONO)
        c = N_BLUE if l == "N" else L_BROWN
        s.add(f'<path d="M{x+10} {by-12}V{py+44}" stroke="{c}" stroke-width="2"/>')
    s.text(bx + 124, by - 16, "EINGANG", 9.5, 700, INK, font=MONO)
    s.text(bx + 124, by - 3, FACTS["nt_in"], 9.5, 500, MUTED, font=MONO)
    s.text(bx + 16, by + 38, "Netzteil · DIN-Hutschiene", 11, 700, INK)
    s.text(bx + 16, by + 55, "AUSGANG " + FACTS["nt_out"], 9.5, 500, MUTED, font=MONO)
    outs = [("BUS1", "IM"), ("BUS2", "IM"), ("BUS1", "DS"), ("BUS2", "DS")]
    for i, (a, b) in enumerate(outs):
        x = bx + 14 + i * 64 + (14 if i > 1 else 0)
        s.add(f'<rect x="{x}" y="{by+78}" width="52" height="30" rx="2" fill="#fff" stroke="{INK}"/>')
        s.text(x + 26, by + 91, a, 9, 700, INK, "middle", MONO)
        s.text(x + 26, by + 103, b, 9, 500, MUTED, "middle", MONO)
    s.pair([(bx + 72, by + 110), (bx + 72, by + 132)], WIRE["EG"], gap=26, width=1.6)
    s.pair([(bx + 220, by + 110), (bx + 220, by + 132)], STATION, gap=32, width=1.6)
    s.text(bx + 72, by + 148, "→ Monitore BUS_IN", 10, 600, INK, "middle")
    s.text(bx + 220, by + 148, "→ Türstation BUS+ / BUS−", 10, 600, INK, "middle")

    # B · Monitor connections and Reihenverdrahtung
    py = 306
    panel(py, 232, "B", "Monitor EVO-HD-7M · Anschlüsse")
    rows = [("BUS", "Spannung + Signal vom Netzteil (BUS_IN)"),
            ("BUS_OUT", "Erweiterungsmonitor, Reihenverdrahtung"),
            ("GND / DOORBELL", "Etagentaste (optional)"),
            ("NO / COM", "Externer Gong, eigene Versorgung")]
    for i, (a, b) in enumerate(rows):
        y = py + 52 + i * 21
        s.text(RX + 22, y, a, 9.5, 700, INK, font=MONO)
        s.text(RX + 150, y, b, 10, 500, MUTED)
    # mini Reihe
    my = py + 150
    for i, lab in enumerate(("Master · 1/4", "Slave · 2/4")):
        x = RX + 34 + i * 190
        s.img(dev_img("EVO-HD-7M")[0], x, my, 66, 46)
        s.text(x + 33, my + 62, lab, 9.5, 600, INK, "middle", MONO)
    s.pair([(RX + 34 + 66 + 4, my + 23), (RX + 34 + 190 - 4, my + 23)], WIRE["3.OG"], gap=1.8, width=1.2)
    s.text(RX + 162, my + 16, "BUS_OUT → BUS_IN", 9, 600, MUTED, "middle", MONO)
    r_tag(s, RX + 34 + 190 + 80, my + 12)
    s.text(RX + 34 + 190 + 92, my + 16, "nur am", 9, 500, MUTED)
    s.text(RX + 34 + 190 + 92, my + 28, "letzten", 9, 500, MUTED)

    # C · door opener
    py = 552
    panel(py, 160, "C", "Türöffner an der Türstation")
    s.text(RX + 22, py + 54, "Intern", 11, 800, INK)
    s.text(RX + 22, py + 70, "GND + LOCK+", 9.5, 600, INK, font=MONO)
    s.text(RX + 22, py + 86, FACTS["lock_int"], 9.5, 500, MUTED, font=MONO)
    s.text(RX + 22, py + 102, "Versorgung aus der Station", 10, 500, MUTED)
    s.text(RX + 222, py + 54, "Extern", 11, 800, INK)
    s.text(RX + 222, py + 70, "NO + COM, potentialfrei", 9.5, 600, INK, font=MONO)
    s.text(RX + 222, py + 86, FACTS["lock_ext"], 9.5, 500, MUTED, font=MONO)
    s.text(RX + 222, py + 102, "eigener Trafo; Haftmagnet immer", 10, 500, MUTED)
    s.text(RX + 222, py + 116, "extern versorgen", 10, 500, MUTED)
    s.add(f'<path d="M{RX+206} {py+44}V{py+140}" stroke="{HAIR}"/>')
    lock_symbol(s, RX + 22, py + 120)
    s.text(RX + 66, py + 136, "Symbol Türöffner", 9.5, 500, MUTED)

    # D · legend
    py = 726
    panel(py, 196, "D", "Legende")
    used = [taps[k] for k in range(nf)]
    items = [(STATION, "BUS Video-Türstation")] + [(c, f"BUS Monitore {n}") for _, _, c, n in used]
    items += [(LOCKC, "Türöffner"), (L_BROWN, "230 V AC (L braun / N blau)")]
    for i, (c, lab) in enumerate(items):
        col, row = divmod(i, 5)
        x = RX + 22 + col * 210
        y = py + 50 + row * 20
        s.pair([(x, y - 4), (x + 26, y - 4)], c, gap=1.8, width=1.4)
        s.text(x + 34, y, lab, 10, 500, INK)
    yy = py + 158
    s.add(f'<circle cx="{RX+30}" cy="{yy-4}" r="5" fill="{INK}" stroke="#fff" stroke-width="1.5"/>')
    s.text(RX + 42, yy, "Abzweig", 10, 500, INK)
    r_tag(s, RX + 118, yy - 4)
    s.text(RX + 132, yy, "Endwiderstand gesetzt", 10, 500, INK)
    s.add(f'<rect x="{RX+272}" y="{yy-12}" width="22" height="16" rx="2" fill="none" stroke="#737373" stroke-dasharray="4 3"/>')
    s.text(RX + 300, yy, "Elektrokasten", 10, 500, INK)
    s.text(RX + 22, yy + 22, "KT = Klingeltaste · 1/4 = Monitor 1 von 4 in der WE", 9.5, 500, MUTED, font=MONO)

    # ------------------------------------------------ bottom: cable list, notes, title block
    BY = 1188 - 36 - 196
    s.add(f'<path d="M36 {BY}H{W-36}" stroke="{INK}" stroke-width="1.6"/>')
    # cable list
    cx0 = 52
    s.text(cx0, BY + 24, "KABELLISTE", 11, 800, INK)
    cols = [("Nr.", 0), ("Von", 46), ("Nach", 250), ("Leitung", 470)]
    for lab, dx in cols:
        s.text(cx0 + dx, BY + 46, lab, 9.5, 700, MUTED)
    rows = [("W01", f"{st['model']} · BUS+ / BUS−", "Netzteil 1 · DS", FACTS["bus_cable_short"], STATION)]
    for k in range(nf):
        tlist, bus_y, color, name = taps[k]
        n_dev = len(tlist)
        rows.append((f"W{k+2:02d}", f"Monitore {name} · BUS_IN ({n_dev})", "Netzteil 1 · IM", FACTS["bus_cable_short"], color))
    nxt = nf + 2
    for we, a_, b_, col in reihe_links:
        rows.append((f"W{nxt:02d}", f"{we} Monitor {a_}/4 · BUS_OUT", f"{we} Monitor {b_}/4 · BUS_IN", FACTS['bus_cable_short'], col))
        nxt += 1
    rows.append((f"W{nxt:02d}", f"{st['model']} · GND / LOCK+", "Türöffner", "lt. Datenblatt Öffner", LOCKC))
    for i, (a, b, c, d, col) in enumerate(rows):
        y = BY + 62 + i * 14.5
        if y > H - 66:
            break
        s.add(f'<rect x="{cx0}" y="{y-10}" width="4" height="12" rx="1" fill="{col}"/>')
        s.text(cx0 + 10, y, a, 9.5, 700, INK, font=MONO)
        s.text(cx0 + 46, y, b, 9.5, 500, INK, font=MONO)
        s.text(cx0 + 250, y, c, 9.5, 500, INK, font=MONO)
        s.text(cx0 + 470, y, d, 9.5, 500, INK, font=MONO)
    s.add(f'<path d="M{cx0+640} {BY+12}V{H-68}" stroke="{HAIR}"/>')
    s.add(f'<path d="M{cx0} {H-64}H{1172}" stroke="{HAIR}"/>')
    ck = ["Türstation registriert", "Monitore adressiert", "Endwiderstände geprüft", "Türöffner getestet", "WLAN 2,4 GHz am Monitor"]
    yk = H - 47
    s.text(cx0, yk, "INBETRIEBNAHME", 9.5, 800, INK)
    xk = cx0 + 112
    for t in ck:
        s.add(f'<rect x="{xk}" y="{yk-10}" width="11" height="11" rx="2" fill="none" stroke="{INK}" stroke-width="1.2"/>')
        s.text(xk + 16, yk, t, 9.5, 500, INK)
        xk += 34 + len(t) * 5.4


    # notes
    nx = cx0 + 660
    s.text(nx, BY + 24, "HINWEISE", 11, 800, INK)
    notes = [
        f"Leitung {FACTS['bus_cable']}. Strom und Signal auf zwei Adern.",
        "Leitungslänge vorher berechnen: am letzten Monitor muss die Spannung reichen.",
        "Ein zweites Netzteil ersetzt keine Leitungsberechnung.",
        f"Adressen am Monitor im Menü: KT 1–{FACTS['max_units']}, je WE bis {FACTS['max_monitors_per_unit']} Monitore.",
        "Erst die Türstation registrieren, dann die Monitore.",
        "Endwiderstand: Stern an jedem Monitor, Reihe nur am letzten.",
        "EVO (analog) und EVO HD (digital) nie mischen. 230 V nur Elektrofachkraft.",
    ]
    for i, t in enumerate(notes):
        y = BY + 46 + i * 17
        s.text(nx, y, f"{i+1}", 9.5, 800, INK, font=MONO)
        s.text(nx + 16, y, t, 10, 500, INK)

    # title block
    tx, tw = 1196, W - 36 - 1196
    s.add(f'<path d="M{tx-12} {BY}V{H-36}" stroke="{INK}" stroke-width="1.6"/>')
    s.img("balter-logo.svg", tx + 6, BY + 14, 92, 28)
    s.text(tx + 6, BY + 60, "Balter GmbH", 10, 700, INK)
    s.text(tx + 6, BY + 74, "Elisabeth-Selbert-Str. 19", 9.5, 500, MUTED)
    s.text(tx + 6, BY + 88, "40764 Langenfeld", 9.5, 500, MUTED)
    meta = spec.get("meta", {})
    cells = [("PROJEKT", meta.get("project", "")), ("ANLAGE", meta.get("system", "EVO HD")),
             ("ZEICHNUNG", meta.get("drawing", "")), ("GEZEICHNET", meta.get("drawn", "")),
             ("GEPRÜFT", meta.get("checked", "—")), ("DATUM", meta.get("date", "")),
             ("VERSION", meta.get("version", "1.0")), ("BLATT", meta.get("sheet", "1 / 1"))]
    gx = tx + 170
    for i, (k_, v) in enumerate(cells):
        col, row = divmod(i, 4)
        x = gx + col * 140
        y = BY + 22 + row * 40
        s.text(x, y, k_, 8.5, 700, MUTED, font=MONO)
        s.text(x, y + 16, v, 11 if col == 0 else 10.5, 700 if i == 0 else 600, INK, font=SANS if i < 2 else MONO)
    s.add(f'<path d="M{gx-12} {BY+8}V{H-70}" stroke="{HAIR}"/>')
    s.add(f'<path d="M{tx} {H-66}H{W-52}" stroke="{HAIR}"/>')
    n_mon = sum(len(u["monitors"]) for f in floors for u in f["units"])
    n_we = sum(len(f["units"]) for f in floors)
    s.text(tx + 6, H - 48, f"{n_we} WE · {n_mon} Monitore · 1 Türstation · 1 Netzteil · A3 quer", 9.5, 600, INK, font=MONO)

    n = crossings(s.segments)
    return s, n


def render(spec, embed=False, asset_href="assets"):
    s, n = build(spec, embed, asset_href)
    head = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" role="img" '
            f'aria-label="Verdrahtungsplan {escape(spec.get("meta", {}).get("project", ""))}">')
    style = ('<style>@import url("https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800'
             '&amp;family=JetBrains+Mono:wght@500;600;700&amp;display=swap");</style>') if embed else ""
    return head + style + "".join(s.o) + "</svg>", n


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("spec")
    ap.add_argument("-o", "--out", required=True)
    ap.add_argument("--embed", action="store_true", help="inline the device pictures")
    ap.add_argument("--style", choices=["photo", "vector"], default="photo", help="device pictures: real photo or vector illustration")
    ap.add_argument("--assets", default=None, help="href prefix for device pictures (default: relative path to assets)")
    a = ap.parse_args()
    spec = json.load(open(a.spec, encoding="utf-8"))
    STYLE["v"] = a.style
    href = a.assets or os.path.relpath(ASSETS, os.path.dirname(os.path.abspath(a.out)))
    svg, n = render(spec, a.embed, href)
    if a.out.endswith(".html"):
        svg = ('<!doctype html><meta charset="utf-8"><title>Verdrahtungsplan</title>'
               '<style>@page{size:A3 landscape;margin:0}html,body{margin:0}svg{width:420mm;height:297mm;display:block}</style>'
               + svg)
    with open(a.out, "w", encoding="utf-8") as fh:
        fh.write(svg)
    print(f"{a.out}: crossings between groups = {n}")
    if n:
        sys.exit("wires cross — change the floor or Netzteil order")


if __name__ == "__main__":
    main()
