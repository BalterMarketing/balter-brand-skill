#!/usr/bin/env python3
"""
Terminal blocks (Klemmleisten) of Balter devices, drawn the way they look on the device.

The terminal lists live in assets/devices/devices.json under "terminals", bound to the article
number and to their source (manual page, rating plate, photo of the strip). This module draws them:

    strip(terminals, x, y, pitch=22)  -> (svg fragment, {pin label: (x, y) where a wire lands})

so the wiring-plan generator can run each conductor to the exact terminal and label it.

    python3 scripts/terminals.py      # writes <article>-klemmen.svg next to every device that has terminals
"""
import json
import os
from html import escape

HERE = os.path.dirname(os.path.abspath(__file__))
DEV = os.path.normpath(os.path.join(HERE, "..", "assets", "devices"))

MONO = "'JetBrains Mono',ui-monospace,Menlo,monospace"
GREEN, GREEN_D, FACE = "#3f8f4a", "#2c6a35", "#d9eed5"


def _screw(x, y, r):
    return (f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" fill="#f4f4f4" stroke="#2c6a35" stroke-width="1.2"/>'
            f'<path d="M{x - r*.62:.1f} {y + r*.62:.1f}L{x + r*.62:.1f} {y - r*.62:.1f}" stroke="#2c6a35" stroke-width="1.3"/>')


def strip(t, x, y, pitch=22, label_size=10, gap=10, show_labels=True):
    """Draw a device's terminal blocks starting at (x, y) = top-left of the first block body.
    Returns (svg, pins) where pins maps 'BLOCK:LABEL#i' and plain 'LABEL' (first match) to the wire point
    at the bottom of the terminal."""
    out, pins = [], {}
    bh = pitch * 1.55
    cx = x
    for b in t.get("blocks", []):
        n = len(b["pins"])
        w = n * pitch
        out.append(f'<rect x="{cx:.1f}" y="{y:.1f}" width="{w:.1f}" height="{bh:.1f}" rx="2" fill="{FACE}" stroke="{GREEN_D}" stroke-width="1.2"/>')
        out.append(f'<rect x="{cx:.1f}" y="{y:.1f}" width="{w:.1f}" height="{pitch*.32:.1f}" fill="{GREEN}"/>')
        for i, (lab, _role) in enumerate(b["pins"]):
            px = cx + pitch * (i + .5)
            out.append(f'<circle cx="{px:.1f}" cy="{y + pitch*.62:.1f}" r="{pitch*.17:.1f}" fill="none" stroke="{GREEN_D}" stroke-width="1.1"/>')
            out.append(_screw(px, y + pitch * 1.12, pitch * .27))
            if i:
                out.append(f'<path d="M{cx + pitch*i:.1f} {y + pitch*.32:.1f}V{y + bh:.1f}" stroke="{GREEN_D}" stroke-width=".8" opacity=".6"/>')
            if show_labels:
                out.append(f'<text transform="translate({px + label_size*.36:.1f} {y - 5:.1f}) rotate(-90)" font-family="{MONO}" '
                           f'font-size="{label_size}" font-weight="600" fill="#0a0a0a">{escape(lab.replace("-", "−"))}</text>')
            pt = (px, y + bh)
            pins.setdefault(lab, pt)
            pins[f'{b["name"]}:{lab}#{i}'] = pt
        cx += w + gap
    for i, (lab, _role) in enumerate(t.get("connectors", [])):
        w = pitch * 1.6
        px = cx + w / 2
        out.append(f'<rect x="{cx:.1f}" y="{y:.1f}" width="{w:.1f}" height="{bh:.1f}" rx="3" fill="#fafafa" stroke="#525252" stroke-width="1.2"/>')
        for k in (-1, 1):
            out.append(f'<rect x="{px + k*pitch*.32 - pitch*.13:.1f}" y="{y + bh*.35:.1f}" width="{pitch*.26:.1f}" height="{bh*.4:.1f}" rx="1" fill="#d4d4d4" stroke="#737373" stroke-width=".8"/>')
        if show_labels:
            out.append(f'<text transform="translate({px + label_size*.36:.1f} {y - 5:.1f}) rotate(-90)" font-family="{MONO}" '
                       f'font-size="{label_size}" font-weight="600" fill="#0a0a0a">{escape(lab)}</text>')
        pins.setdefault(lab.replace(" ", ""), (px, y + bh))
        pins.setdefault(lab, (px, y + bh))
        cx += w + gap * .6
    return "".join(out), pins


def size(t, pitch=22, gap=10):
    w = sum(len(b["pins"]) * pitch + gap for b in t.get("blocks", [])) + sum(pitch * 1.6 + gap * .6 for _ in t.get("connectors", []))
    return w - gap, pitch * 1.55


def switches(items, x, y):
    """DIP switches and jumpers beside the strip, drawn as on the board; no setting is implied."""
    out, roles = [], []
    for it in items:
        if it["type"] == "dip":
            n = it["n"]
            w = n * 18 + 10
            out.append(f'<rect x="{x}" y="{y}" width="{w}" height="46" rx="3" fill="#111"/>')
            for i in range(n):
                sx = x + 7 + i * 18
                out.append(f'<rect x="{sx}" y="{y + 12}" width="12" height="24" rx="1.5" fill="#F7E7B0"/>'
                           f'<rect x="{sx + 2}" y="{y + 14}" width="8" height="8" fill="none" stroke="#111" stroke-width="1.4"/>'
                           f'<text x="{sx + 6}" y="{y + 9}" font-family="{MONO}" font-size="8" fill="#fff" text-anchor="middle">{i + 1}</text>')
            out.append(f'<text x="{x + w / 2}" y="{y + 44}" font-family="{MONO}" font-size="7" fill="#fff" text-anchor="middle">ON ↓</text>')
            out.append(f'<text x="{x}" y="{y + 60}" font-family="{MONO}" font-size="10.5" font-weight="700" fill="#0a0a0a">{escape(it["name"])}</text>')
            roles.append((it["name"], it["role"]))
            x += w + 30
        elif it["type"] == "jumper":
            pins = it["pins"]
            w = len(pins) * 28 + 6
            out.append(f'<rect x="{x}" y="{y + 10}" width="{w}" height="22" rx="3" fill="#111"/>')
            for i, pn in enumerate(pins):
                cx = x + 17 + i * 28
                out.append(f'<circle cx="{cx}" cy="{y + 21}" r="4.2" fill="#E6C15A" stroke="#7a5a00" stroke-width="1"/>'
                           f'<text x="{cx}" y="{y + 6}" font-family="{MONO}" font-size="9" fill="#0a0a0a" text-anchor="middle">{escape(pn)}</text>')
            for i, lb in enumerate(it.get("labels", [])):
                cx = x + 17 + i * 28
                out.append(f'<text x="{cx}" y="{y + 44}" font-family="{MONO}" font-size="8" fill="#404040" text-anchor="middle">{escape(lb)}</text>')
            out.append(f'<text x="{x}" y="{y + 60}" font-family="{MONO}" font-size="10.5" font-weight="700" fill="#0a0a0a">{escape(it["name"])}</text>')
            roles.append((it["name"], it["role"]))
            x += max(w, 60) + 30
    return "".join(out), roles


def card(d, pitch=26):
    """A stand-alone sheet for one device: its terminals, labelled, with the roles below."""
    t = d["terminals"]
    w, h = size(t, pitch)
    longest = max([len(p[0]) for b_ in t.get("blocks", []) for p in b_["pins"]] + [len(c[0]) for c in t.get("connectors", [])] + [4])
    lab_h = 24 + longest * 7.2
    rows = [p for b in t.get("blocks", []) for p in b["pins"]] + list(t.get("connectors", []))
    seen, roles = set(), []
    for lab, role in rows:
        if (lab, role) not in seen:
            seen.add((lab, role)); roles.append((lab, role))
    notes = t.get("notes", [])
    W = max(w + 40 + sum(150 for _ in t.get("switches", [])), 600)
    H = lab_h + h + 34 + len(roles) * 17 + (len(notes) * 16 + 10 if notes else 0) + 30
    body, _ = strip(t, 20, lab_h, pitch=pitch, label_size=11)
    sw_svg, sw_roles = switches(t.get("switches", []), w + 60, lab_h - 6)
    body += sw_svg
    roles += sw_roles
    H += len(sw_roles) * 17
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W:.0f} {H:.0f}" role="img" aria-label="Klemmen {escape(d["article"])}">',
           f'<rect width="100%" height="100%" fill="#fff"/>', body]
    y = lab_h + h + 34
    for lab, role in roles:
        out.append(f'<text x="20" y="{y:.0f}" font-family="{MONO}" font-size="11" font-weight="700" fill="#0a0a0a">{escape(lab)}</text>')
        out.append(f'<text x="140" y="{y:.0f}" font-family="Inter,Arial,sans-serif" font-size="11.5" fill="#404040">{escape(role)}</text>')
        y += 17
    y += 8
    for n_ in notes:
        out.append(f'<text x="20" y="{y:.0f}" font-family="Inter,Arial,sans-serif" font-size="11" fill="#0a0a0a">· {escape(n_)}</text>')
        y += 16
    out.append(f'<text x="20" y="{H-10:.0f}" font-family="Inter,Arial,sans-serif" font-size="10" fill="#8a8a8a">Quelle: {escape(t.get("source", ""))}</text>')
    out.append("</svg>")
    return "".join(out)


def main():
    path = os.path.join(DEV, "devices.json")
    man = json.load(open(path, encoding="utf-8"))
    n = 0
    for d in man["devices"]:
        if not d.get("terminals"):
            d.pop("terminal_card", None)
            continue
        fn = d["image"].rsplit(".", 1)[0] + "-klemmen.svg"
        open(os.path.join(DEV, fn), "w", encoding="utf-8").write(card(d))
        d["terminal_card"] = fn
        n += 1
    json.dump(man, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(n, "terminal cards")


if __name__ == "__main__":
    main()
