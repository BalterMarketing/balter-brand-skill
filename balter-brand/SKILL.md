---
name: balter-brand
description: The complete BALTER brand book (Security division, balter.de, B2B video door intercoms) as one instruction set for AI agents. Use it for ANY work that carries the Balter brand — logo use, colour, typography, the black frame with the rounded window, motion, UI components, charts and dashboards, schemas (customer visualisation and the technical wiring plan, which has its own generator), product images, social posts and reels, video, Brevo newsletters, German copy and wording, design tokens. Trigger on "Balter", "BALTER", "Markenhandbuch", "brand book", "nach dem Brandbook", "im Balter-Stil", or any request to design, write, draw or check material for Balter.
metadata:
  version: "2.2"
  updated: "2026-11-25"
  owner: "Balter GmbH, Design und Marketing"
  source: "BALTER Markenhandbuch 2.0 (the HTML brand book this file ships with)"
  audience: "AI agents: Claude Code, Codex CLI, Cursor, any agent that reads Markdown"
---

# BALTER brand book — instructions for AI agents

You are reading the machine version of the **BALTER Markenhandbuch 2.0**. A person asked you to
make, change or check something for the Balter brand. Everything you need is in this one file:
read **0 · Always** first, then jump to the section for the task (router below). The HTML brand
book shows the same rules with examples; this file is the binding text for you.

**Language.** This file is English so every agent reads it the same way. Customer-facing output is
**German** unless the person asks for another language. Quoted German words are the exact terms
to use.

## Router — which section for which task

| The task is … | Read |
|---|---|
| Any task | 0 · Always |
| Placing or exporting a logo | 2 · Logo |
| Picking colours, contrast, print colour | 3 · Colour |
| Choosing fonts, sizes, other scripts (Cyrillic, Arabic, Turkish) | 4 · Type |
| Web page, admin, configurator, app screen layout | 5 · Frame, 7 · Components, 15 · Tokens |
| Animation, transitions, hover | 6 · Motion |
| Chart, dashboard, KPI, infographic | 8 · Charts |
| Diagram of the system for customers | 9a · Visualisation |
| Wiring plan / Verdrahtungsplan for installers | 9b · Technical plan (run the generator) |
| Any device picture (photo or vector) by article number | 9c · Device library |
| Product photo, scene, AI image | 10 · Product and image |
| Instagram, Facebook, LinkedIn, TikTok post, carousel, reel; content plan, rubric, posting rhythm, safe zones | 11 · Social |
| Video, trade-fair film, lower thirds; cutting a reel, subtitles, DaVinci Resolve workflow | 12 · Video (12a hold rules, 12b pipeline) |
| Newsletter, e-mail | 13 · E-mail |
| Any German text, caption, headline, product copy | 14 · Language |
| CSS variables, design system, new interface | 15 · Tokens |

Files in this skill: `assets/logo/` (all logos, SVG and PNG) · `assets/tokens.css` (design tokens)
· `assets/devices/` (every device as photo and vector, indexed by article number in `devices.json`) · `scripts/wiring_plan.py` (technical plan generator) · `assets/social/` (safe zones, overlays, caption glossary) · `scripts/captions.py` (brand subtitles) · `scripts/safe_zones.py` (overlays and checks) ·
`examples/` (a plan spec and its output).

---

## 0 · Always

1. **Two divisions, never mixed.** This book is for **Security**: balter.de, B2B, for installers,
   planners, wholesale (Fachpartner). **Home** (redshop.de, B2C, homeowners) has its own book.
   Never put Home content into Security material or the reverse.
2. **Black and white carry everything. Orange `#FB824B` is one signal per surface.** Text on
   orange is always black.
3. **Three fonts only:** Science Gothic 700 (titles), Inter (everything else), JetBrains Mono 500
   (technical data). All free on Google Fonts.
4. **The real device, real pixels, true size.** Never let AI draw a Balter product. AI may build
   the scene around a real photo or CAD render.
5. **Never invent facts.** Only use figures listed in 14 · Language → approved figures, or numbers
   the person gives you with a source. If unsure, leave it out and say so.
6. **Never name** the manufacturing partner, suppliers or revenue. Never write "Made in Germany"
   unless the person confirms it for that product.
7. **Claim:** `STAY AHEAD`: English, capitals, never translated or inflected; in the logo or as its
   own line, never inside running text.
8. When something is not covered here, take the closest rule and say which one you applied.
   Do not invent a new style.

---

## 1 · Brand

- Balter GmbH, Langenfeld. In security technology since 2006, own brand since 2008. Develops
  video door communication, access control and security technology.
- Ambition: make complex technology simple for installers, planners and users.
- Stance: "Wir denken Sicherheit nicht als Produkt, sondern als Verantwortung."
- Values: reliable innovation, cyber security, sustainability.
- Message for Security: development, engineering, made-to-measure (Sonderanfertigung), training
  (Schulung).
- Apps follow their own app brand book (platform first), with colour and type from here.

## 2 · Logo

- Parts: the mark (eagle head in a shield), the wordmark BALTER in bold italic, the claim STAY AHEAD.
- **Always one colour:** black on light, white on dark. Never orange, silver, gradient.
- Variants (in `assets/logo/`):
  | Use | File |
  |---|---|
  | Default, landscape with claim | `optisch/quer-claim-grundlinie-schwarz|weiss.svg/.png`, with clear space `optisch/quer-claim-schutzzone-*` |
  | Below 28 px height, UI, product print | `optisch/quer-grundlinie-*`, with clear space `optisch/quer-schutzzone-*` |
  | Narrow spaces (column, label) | `logo-hoch-black.svg`, `hoch-claim-*.png` |
  | App icon, favicon, avatar, seal | `logo-mark-black.svg` / `logo-mark-white.svg`, `bildmarke-*.png` |
- **Use the optically corrected landscape logos in `assets/logo/optisch/`** (since 2026-11-24). In the
  source artwork the text block sat on the middle of the eagle's bounding box and read low; it is raised
  by 3.1 of 111 units (with claim) and 2.7 of 94 (without), measured as the mean of the optical extent
  (thin crown and shield tip trimmed) and the centre of mass. Two files per logo and colour:
  `*-grundlinie-*` — cropped tight, for aligning to lines; `*-schutzzone-*` — clear space baked in,
  canvas centred on the logo's visual centre, for placing freely in a surface.
- **Baseline (Grundlinie)** = bottom of BALTER; cap line (Oberlinie) = top of BALTER. Claim and shield tip
  hang below like descenders. Inline in HTML: `.logo{height:var(--h);vertical-align:calc(var(--h) * -0.4356)}`
  with claim, `-0.2417` without; each file carries `data-baseline` (fraction from the top).
- Clear space = height of the "B" in BALTER, all round, including from image edges and frame corners.
- Minimum: with claim 28 px high (print 30 mm wide); otherwise use the version without claim. Mark alone from 16 px.
- Placement: top left on web and admin; top right in video and on trade-fair walls; bottom centre on end cards.
- Sizes in practice: web header 32–36 px high, admin 34 px, video 1920×1080 150 px wide with 48–60 px margin, trade-fair wall 240 mm wide with 120 mm margin.
- The eagle head may stand alone. The letters BALTER never stand alone without the eagle.
- Never: recolour, distort, shadow/glow/outline/relief, place on a busy image without its own plate, re-set the wordmark in another font.

## 3 · Colour

| Role | Value | Use |
|---|---|---|
| Ink | `#000000` | frame, text, primary button; print text K100 |
| White | `#FFFFFF` | sheet, cards |
| Accent | `#FB824B` | RGB 251 130 75 · CMYK 0 48 70 2; hover `#FF9564` |
| Accent ink | `#B5491A` | orange as text on white (5.3 : 1) |
| Line soft | `#F2F2F2` | cards, tracks, plates |
| Background | `#FAFAFA` | admin sheet, alternating sections |
| Line | `#E5E5E5` | borders, baselines |
| Muted | `#666666` | kickers, secondary text, axes |
| ink-2 / grey / grey-2 | `#404040` / `#A3A3A3` / `#BDBDBD` | second text / second chart series / pending |
| Frame line | `#262626` | lines on the black frame |
| Accent wash / peach | orange 5 % / 32 % | attention card fill / its border and focus ring |
| OK | `#4D7C0F` on `#F7FEE7` | done, valid, ▲ |
| Error | `#B42318` on `#FEF3F2` | error, cancelled, ▼ |

- Ratio per surface about white 60 · black 28 · grey 10 · orange a dot. On black media (reels,
  stand, video) black and white swap; orange stays a dot.
- Contrast: black on orange 8.4 : 1 (the only text on orange). White on orange 2.5 : 1 — **never**.
  Orange on black 8.4 : 1 (allowed as text).
- Orange **yes**: a dot before a kicker; one counter or badge ("Neu", "3 nicht versendet"); the one
  button that closes a surface; the one data segment that needs action.
- Orange **no**: backgrounds, areas, gradients (except the 5 % attention card); strokes, lines,
  underlines; inside the logo; twice on one surface.
- **Rejected colours:** `#FF5F14` (too saturated, like warning orange; do not use anywhere) and blue
  `#6699CC` (no second accent, no status blue).
- Print: CMYK 0 48 70 2; check foil against a sample. Large formats rather light; dark as bands. No
  thin white text on black in print.

## 4 · Type

- **Science Gothic 700 — titles.** Capitals for product names, labels, chapters, video titles
  (tracking 0); sentence case allowed for longer titles. From 20 px, once per surface, max. 3 lines;
  it is wide, so keep titles short.
- **Inter — everything else.** Headings 700 (−0.03 em), body 400 (line height 1.55), labels 500 caps
  +0.08 em, big numbers 800 tabular −0.03 em.
- **JetBrains Mono 500 — technical data:** article numbers, dimensions, specs, schema labels, code.
  11–14 px, never running text.
- Retired: Zen Dots, Canaro, Ginto Nord, Manrope. Do not use them in new work.
- E-mail: Inter, Helvetica, Arial; a Science Gothic title only as an image with alt text.
- Scale (web/UI): Display XL 56–78 · Display 30–54 · H1 Inter 700 30–40 · H2 22–28 · H3 600 16–18 ·
  body 15–18 · small 13–14 · label 11–12 · number Inter 800.
- Per medium (display / heading / body / smallest): web 30–72 / 22–40 / 15–18 / 11 · social 1080 px
  52–88 / 56–72 / 32–40 / 28 feed, 32 reel · video 1920 px 28 label, 72 title / 64–96 / 36–44 / 26 ·
  e-mail 600 px image 26–32 / 22–26 / 15–16 / 12 · slides 1920 80 / 56, 40 / 32, 24 / 20.
- Other scripts: all three fonts have Cyrillic. Arabic: titles Noto Kufi Arabic, text IBM Plex Sans
  Arabic (put them in the font stack after the house font); right-to-left layout (`dir="rtl"`) but
  never mirror logo, product photos or article numbers; no capitals and no tracking in Arabic.
  Turkish capital i is "İ" (`lang="tr"`). Translations go to a native speaker before publishing.

## 5 · Frame and form (web, admin, configurator)

The signature: a **black frame** and inside it a **white sheet with round corners**. The frame is
fixed to the screen; content scrolls underneath. Corners always sit at the screen edge and there is
never white space behind the frame.

- Frame = fixed overlay layer with radius, filled black outside (`box-shadow: 0 0 0 100vmax #000`).
  Never build it as an outer margin of the content.
- `html, body` and `theme-color` are black; `overscroll-behavior-y: none`.
- Header: black, fixed, no shadow, never transparent, never hidden on scroll. 68–76 px (phone 60);
  logo left, one orange button right.
- Footer: black, last part of the content, merges with the frame; 72 px padding, white logo.
- Sizes: desktop ≥1100 px frame 12 px, radius 40 · tablet 768–1099 px 8 / 28 · phone <768 px 6 / 22.
- Safe areas (notch, home bar) belong to the frame: `env(safe-area-inset-*)`.
- Scrollbars: page scrollbar on the frame, 12 px, thumb `#3A3A3A` with 3 px black border, hover
  `#8A8A8A`, black track. Inner scroll areas 6 px, black 25 % (on black: white 25 %).
- Page margin = frame width + 28 px (phone + 14). Anchors: `scroll-padding-top` = header + 24 px.
- **The frame grows with the interface.** Reading (site, landing): 12 px all round. Working (admin,
  dealer portal): frame becomes the left sidebar, 240 px, with navigation. Designing (configurator):
  frame carries the step bar on top and the questions on the left (400 px). The window keeps radius
  40 and only holds the content being worked on. Controls on the frame are dark: surfaces `#171717`
  / `#262626`, lines `#262626`–`#404040`, text white 100/68/46 %, active = white pill with black
  text. Under 900 px the sidebar becomes a bottom tab bar; the admin sheet goes borderless.
- Configurator stage: `#FAFAFA` with a 24 px grid in black 7.5 %, product centred at true size.
- **Dark theme:** frame stays `#000`; window `#0D0D0D` with a 1 px white-9 % edge; cards `#1B1B1B`;
  text `#F2F2F2` / `#9A9A9A`. Never make the window as black as the frame. Product photos, schemas,
  report charts, logo tiles and templates stay light "islands". Follow the system setting; a toggle
  overrides and is remembered.
- Radii ladder: 6 chip · 10 button, field · 16 card · 24 panel, image · 40 sheet, window; pills
  fully round. Nested = concentric: inner = outer − padding. No in-between values.
- Trade-fair wall: black stand, white wall fields with top corners r 130 mm; 500 mm black base with
  QR code and claim; logo top right 240 mm wide, 120 mm margin; groups with a caps label and a thin
  line; products at true size labelled only with the article number on the product axis; orange
  only as one "NEU" pill for the whole stand; 20 mm bleed, CMYK, PDF/X-4.

## 6 · Motion

| Token | Value | For |
|---|---|---|
| t-fast | 140 ms | press, popover, checkbox |
| t-base | 200 ms | colour, border, hover lift |
| t-slow | 280 ms | menu, closing a sheet |
| t-wipe | 600 ms | button fill, opening a sheet |
| t-enter | 700 ms | entrance on load (24 px rise, 80 ms stagger) |
| ease-out | `cubic-bezier(.23,1,.32,1)` | everything that appears |
| ease-site | `cubic-bezier(.3,1,.3,1)` | button fill, page elements |
| ease-sheet | `cubic-bezier(.7,0,.2,1)` | sheets and menus from below |

- Hover on cards: lift 2 px, black border, soft shadow; the image does not move. Buttons: a circle
  fills from below (600 ms); press `scale(.97)`.
- Charts draw once when first visible (1.1 s, 250 ms delay).
- Only transform and opacity. Exit faster than entry. Hover only with `(hover:hover) and (pointer:fine)`.
  `prefers-reduced-motion` turns everything off and nothing stays hidden.
- Never: zoom on images inside rounded frames (cuts the corner), fade-in for every section on
  scroll, parallax, scroll-jacking, tilt, springs, bounces, auto carousels, timed tabs, ease-in for
  appearing things.

## 7 · Components

- **Button:** 44 px (small 36), radius 10, 1 px black border, Inter 500 14 px. Primary black.
  Orange only for the one closing action. Label = verb + object.
- **Kicker:** Inter 500 12 px caps +0.08 em `#666`, optional orange dot. **Pill** 26 px, **delta**
  22 px, counters fully round.
- **Segmented control:** 36 px, outer radius 12, inner 9, active black. **Field:** 44 px, radius 10,
  visible label above. Focus ring 2 px orange 32 %.
- **Attention card** (the only orange surface): 5 % orange fill, 32 % border, counter in full orange
  with a black number. One per page.
- **Icons:** 1.5 px line, round caps, one colour, 24 px grid, 2 px inset; Lucide where the house set
  lacks one. No filled icons, no emoji, no gradients.
- **Pattern:** only as background of large surfaces (wall back, title slide, packaging), text on it
  ≥ 4.5 : 1, never behind products, tables or charts.

## 8 · Charts and data

Numbers are black, comparisons grey, problems orange.

- Pick: **line** for time (≥5 points, one black series, max. one grey comparison) · **bar** for
  categories (always from zero; horizontal when names are long; radius 4) · **ring** for parts of a
  whole (max. 4 segments, 100 %, value in the middle, 18 px stroke) · **progress** for rates and
  funnels (8 px on `#F2F2F2` track, value right) · **number tile** when one number is enough (value,
  delta, optional sparkline).
- Anatomy: grid 1 px `#F2F2F2`, 3–4 lines on round values · baseline 1 px `#E5E5E5`, no other axis
  lines, no ticks · axis text Inter 500 11 px `#666`, tabular, unit on the value ("900 €") · line
  2.2 px black, round joins (sparkline 1.6 px) · area black 6 % (single series only) · end dot 12 px
  black with 2 px white ring · label black, radius 8, Inter 600 12 px white, only the last or shown
  value.
- Title states the message, subtitle the basis ("B2B-Umsatz pro Woche" · "Netto, ohne Stornos ·
  letzte 8 Wochen"). Series order: black, `#A3A3A3`, `#BDBDBD`, track `#F2F2F2`. Legend above, 10 px
  square radius 3, or label directly at the line.
- German number format: "24.380 €", "12 %", "KW48", space before the unit.
- Never: pies with more than 4 slices, two y-axes, 3D/shadow/gradient/gloss, a colour per category
  (more than 4 categories → bars sorted by size, all black, one highlighted), red/green without ▲ ▼
  or a word, truncated bar axes.

## 9 · Schemas — two kinds, two readers

Both show **only real Balter devices** (cut-out photos), never placeholders, never boxes with
names. Never mix EVO HD and EVO HD PRO devices in one drawing.

### 9a · Visualisation (customers, social, slides, website)

- Tells one event at a building: a building section with floors, riser shaft and technical room.
  The path of the door call is the **only orange line**.
- Architecture as fine line drawing: slabs and walls `#EDEDED` with edge `#D4D4D4`, slight depth in
  `#E5E5E5`. No furniture, people or sky.
- Devices free on the wall, no plate, no frame. They may be larger than scale; then show no doors or
  people that would reveal the scale.
- Cable as one 3 px black line, junctions with a dot. No conductors, no terminals.
- Labels as chips: black with white Inter 600 12 px, fully round, thin leader line. Max. five chips;
  floor names outside right.

### 9b · Technical plan (installers, planners, training) — use the generator

Do **not** draw this by hand. Run `scripts/wiring_plan.py`; it draws the A3 sheet from a JSON spec
with every rule built in and refuses a sheet whose wires cross.

1. **Ask** for what is missing: floors (EG upward, max. 6 per sheet) and Wohneinheiten (WE) per
   floor; monitors per WE (1–4) and, if more than one, "reihe" or "stern"; station model and button
   count and which WE is on which Klingeltaste; door opener "intern" or "extern"; project name,
   drawing number, author, date, version.
2. **Stop** if the system needs more than one Netzteil (IM terminals bridged across up to five Netzteile,
   or coupled over EVO-HD-2WL and CAT 7) or is EVO HD PRO, ENTRI or ERA: say these plans are drawn by
   Balter Technik. The generator draws EVO HD,
   one Netzteil per sheet.
3. **Write the spec** by copying `examples/mehrfamilienhaus-8we.json` (station and monitors by article number from 9c, only devices with `plan: true`); floors bottom to top; `kt` =
   Klingeltaste (address "KT n von 128"); on 5–8 family stations button counting starts at the
   bottom. Only devices whose picture is in `assets/` — a new device needs a real cut-out photo first.
4. **Draw:** `python3 scripts/wiring_plan.py spec.json -o plan.svg --embed` (standalone SVG) or
   `-o plan.html --embed` (A3 page to print as PDF). It must print `crossings between groups = 0`.
5. **Look at the result** before handing it over: no label on a line, every WE with its address,
   cable list matches the drawing. A person checks the sheet against the real installation.

What the sheet contains: frame with zones 1–8 / A–F · floors as bands (highest on top) with tabs ·
per WE: number, real monitor, article number, "KT 05 · 1/4", **R** where the Endwiderstand is set ·
every line as two conductors in its group colour, parallel, never crossing, cable IDs W01… · Technik
zone with the station outside, door opener, Netzteil EVO-HD-C5001 in a dashed Elektrokasten, 230 V
from above (L brown / N blue), BUS terminals IM (monitors) and DS (station) below · details A
Netzteil terminals, B monitor connections and Reihenverdrahtung, C door opener intern/extern,
D legend · cable list, notes, commissioning checklist, title block.

Wire colours (fixed): station `#16A34A` · EG `#1D4ED8` · 1.OG `#EAB308` · 2.OG `#0EA5E9` · 3.OG
`#DC2626` · 4.OG `#7C3AED` · 5.OG `#0D9488` · EVO-HD-2WL `#000000` · CAT 7 `#F59E0B` dashed · 230 V
brown/blue · door opener `#737373`. Orange `#FB824B` is never a wire colour.

Technical facts used (and their sources — add nothing else):

| Fact | Value | Source |
|---|---|---|
| Netzteil input | 100–240 V~, 0,6 A, 50–60 Hz | rating plate EVO-HD-C5001 |
| Netzteil output | BUS 32 V DC, 3,5 A; BUS1/BUS2 (IM), BUS1/BUS2 (DS) | rating plate |
| IM → monitors BUS_IN · DS → station BUS+ / BUS− | | EVO HD manual v3.2 p. 17 |
| Stern: every monitor on IM · Reihe: BUS_OUT → BUS_IN | | manual p. 18–19 |
| Endwiderstand: stern at every monitor, reihe only at the last | | Balter technical knowledge base |
| Cable J-Y(St)Y 2×2×0,8 mm² or YR 0,8 mm² | | knowledge base, Balter plans |
| KT 1–128, up to 4 monitors per WE (1 master + 3 slave) | | manual, Adressierung |
| Door opener intern GND / LOCK+, 12 V DC, 300 mA | | manual p. 119 |
| Door opener extern NO / COM potential-free, 30 V DC 2 A or 250 V AC 2 A, own transformer | | manual p. 119 |
| Set up the station first, then the monitors · monitor WLAN 2,4 GHz only | | knowledge base · manual p. 32 |

Not on any sheet yet (no checked number): maximum cable length for EVO HD, monitors per Netzteil.

## 9c · Device library — every device twice, bound to its article number

`assets/devices/` holds every Balter device available as a real cut-out, in **two versions with the
same file stem** (the article number in lowercase, dots removed):

- `<article>.png` — the **photo**: real pixels, transparent background. For social, website, slides.
- `<article>.svg` — the **technical sketch** (Skizze). Never a trace and never drawn by eye. Every
  device is built from a small set of parts; each part is **found on the photo** and drawn with **one
  symbol**, so all sketches share one style and sit 1:1 on the photo:
  - stations, audio stations, extensions — `scripts/station_model.py`: sensor windows, IR light (mesh or
    its LEDs), camera dome, loudspeaker slots or hole grid, microphone, status display with its icons
    (bell, call, door), RFID / fingerprint block, name plates, call buttons (one size per station);
  - monitors, Talk, Touch — `scripts/flat_model.py`: screen (dark), status LEDs (dot, moon, mail),
    touch rings and the call / hang-up buttons, handset, base, key / bell / apps buttons, cable; the
    Touch station keeps a plain outline of its call list, because there the screen is how a visitor rings;
  - EVO Aufputz stations (EVO-AP-*) — `scripts/ap_model.py`: black glass block with the camera housing (found by its
    radial profile) and IR light, the white name field with one row per button and its button column, the logo upright
    beside the field;
  - flat touch units of the EVO line (EVO-QUICK-4.3M, EVO-QUICK-BLACK, EVO-MINI-4.3M, EVO-TALK) — `scripts/touch_flat.py`:
    the screen (where the plain face becomes textured), every printed touch symbol kept in its own simplified shape,
    the seam of a lower face part, the real logo;
  - EVO HD PRO modules and housings — `scripts/pro_model.py`: grooves, speaker slot, plates, RFID block,
    camera module (dome, IR bars, icon row); housings take their cut outline and openings from the photo,
    inner steps and round cable entries where they are found.
  **Printed icons** are never drawn from a generic icon set. Each icon is traced once, enlarged, from the
  clearest photo that carries it, and kept in `assets/icons/icon-library.json` (`scripts/icon_library.py`
  rebuilds it): the display icons bell · call · door (EVO-HD-2FAM-AUDIO), apps · person · key · call-wave
  (EVO-QUICK-4.3M), call-key · hang-up (EVO-HD-MINI-BLACK-4.3M), bell-talk (EVO-HD-TALK), moon · mail (EVO-HD-7M).
  On every other device the icon is found on its own photo, matched to the library by shape, and the library
  drawing is placed in the box measured there — the same icon looks the same on every device and sits where
  it sits on the product. The status display is one part on every station: its icons sit at 25 · 50 · 75 % of
  its width; the round light sensor at its right end is drawn only where the photo shows one. An icon that is
  not in the library keeps its own trace (`sketch_fit.trace_icon`).
  **Black twins** (EVO-HD-BLACK-8FAM, EVO-BLACK-8EXT/12EXT, 7M/MINI/PRO-7 black, BLACK-TALK) share the
  geometry of their steel or white twin; what differs (LEDs, display icons, IR pill, logo) is found on
  the black photo. Where white-on-white hides a part (MINI rings), it is taken from the clearer twin.
  **Every sketch is checked**: the distance from each drawn outline to the photo's edge, in pixels, goes
  to `assets/devices/sketch-check.json` (stations mean 0.5–1.3 px). Check it by eye too: photo, sketch
  and the sketch laid over the photo side by side. Three tones only: grey body (steel `#D9D9D9`, white
  `#F2F2F2`, black finish `#3A3A3A`), black for camera, screens, display, glass, RFID / fingerprint, white
  for name plates; one black outline; icons in light grey line. The real BALTER logo is placed where it
  sits on the device (upright on station plates, horizontal on monitors, Talk, Touch). **DIN-rail
  modules** (EVO-HD-C5001, EVO-HD-DL, EVO-HD-2WL, EVO-C4001) are taken from Balter Technik's own straight-on drawings
  in Figma (`assets/figma/`, `scripts/figma_modules.py`), because their photos are shot at an angle; their
  labels stay as on the module. `python3 scripts/device_sketch.py [ARTICLE …]` redraws them.

**Photos** come from the shop's front shots on white (`scripts/cutout.py` turns one into a transparent PNG; the
source is named in `photo_source`). The EVO (analog) line was added on 2026-11-25: stations Silver 1–8FAM and
6FAM-RFID, Black 1–4FAM, Aufputz 1–4FAM, monitors 7M (white, black), QUICK 4,3″ (white, black), MINI 4,3″, the
Audiostation EVO-TALK and the Netzteil EVO-C4001.

`assets/devices/devices.json` is the index: article, German name (house words), kind, line, colour,
button count, size in mm where the manual gives it, both file names, and `plan: true` for devices the
wiring-plan generator may use. **Always pick a device by its article number from this index.** A device
that is not in it does not exist for you: ask for a real photo, add it with its article number, then
run `python3 scripts/device_sketch.py <ARTICLE>` to draw its sketch, then look at it over the photo. Never draw, generate or borrow a
device that is not in the library, and never show a device under another article number.

The wiring-plan generator takes `--style photo` (default) or `--style vector`.

**Terminals (Klemmen).** Every known terminal strip is in `assets/devices/terminals-catalog.json`
(articles and article patterns, each with source and notes, taken from Balter Technik's wiring
schemas in Figma, the manuals, the rating plates and photos of the strips). Devices in the library
carry theirs in `devices.json → terminals` and a drawn card `<article>-klemmen.svg`. `scripts/terminals.py`
draws the strips (green screw terminals, labels rotated above, as on the device) and returns the point
of every terminal, so the wiring plan runs each conductor to the right terminal and names it.

| Device | Terminals, left to right |
|---|---|
| EVO HD Video-Türstation 1–8FAM | `GND · EXIT · GND · LOCK+` \| `NC/NO · COM · BUS− · BUS+`; jumper NC/NO; J1/J2 button modules |
| EVO (analog) Türstation 1–8FAM, BLACK, 6FAM-RFID | `NO/NC · COM · PL · S+ · S− · BUS2 · BUS1`; DIP 1–4 on the board (meaning not documented yet — ask Balter Technik); jumper 1-2-3: bridge 1–2 = NC, 2–3 = NO; RST · GND · SWIM · VCC is the programming header, not for installers |
| EVO-HD-C5001 / EVO-HD-PRO-C7001 | in `N · N · L · L`; out `BUS1 IM · BUS2 IM · BUS1 DS · BUS2 DS` (32 V, 3,5 A) |
| EVO-C4001 | in `N · GND · L · L`; out as above (32 V, 1,5 A) |
| EVO-HD-7M | plugs `NO/COM · GND/DOORBELL · BUS_OUT · BUS_IN` |
| EVO-HD-MINI-4.3M | `BUS_OUT · BUS_OUT · BUS_IN · BUS_IN`, plugs `NO/COM`, `GND/DOORBELL`; DIP 1–8, X1/X10/X100 |
| EVO-HD-TALK | `RING · GND · COM · NO · BUS− · BUS+` |
| EVO-HD-DL | `BUS OUT ×2 · BUS IN ×2` (between Netzteil DS and station), relay `NO · COM` |
| EVO-EV4 | `BUS_IN ×2`, outputs `A · B · C · D` |
| ERA relay / ERA station | `DC+ · DC− · IN1` \| `NC · COM · NO` / `E.R · GND · 2ND · P1 · IP1 · IP2 · P2` |

Rules from the same schemas: **several Netzteile** — the station hangs on DS of one Netzteil, DS stays
free on the others, the monitors are shared out and a bridge joins the IM terminals of all Netzteile (up
to five). **Endwiderstand = DIP 8** on the monitor: on at every monitor in star wiring, only at the last
in series. The schemas give the internal door opener as up to 350 mA, the manual's specification 300 mA:
use 300 mA until Balter Technik confirms.
Not recorded yet (do not guess): EVO HD audio and FN stations, Touch, 2WL, EVO HD PRO modules and monitors.

| Article | Name | Kind | Line | Files | Plan |
|---|---|---|---|---|---|
| `EVO-HD-1FAM` | Video-Türstation, 1 Klingeltaster | video-tuerstation | EVO HD | `evo-hd-1fam.png` · `evo-hd-1fam.svg` | yes |
| `EVO-HD-2FAM` | Video-Türstation, 2 Klingeltaster | video-tuerstation | EVO HD | `evo-hd-2fam.png` · `evo-hd-2fam.svg` | yes |
| `EVO-HD-3FAM` | Video-Türstation, 3 Klingeltaster | video-tuerstation | EVO HD | `evo-hd-3fam.png` · `evo-hd-3fam.svg` | yes |
| `EVO-HD-4FAM` | Video-Türstation, 4 Klingeltaster | video-tuerstation | EVO HD | `evo-hd-4fam.png` · `evo-hd-4fam.svg` | yes |
| `EVO-HD-6FAM` | Video-Türstation, 6 Klingeltaster | video-tuerstation | EVO HD | `evo-hd-6fam.png` · `evo-hd-6fam.svg` | yes |
| `EVO-HD-8FAM` | Video-Türstation, 8 Klingeltaster | video-tuerstation | EVO HD | `evo-hd-8fam.png` · `evo-hd-8fam.svg` | yes |
| `EVO-HD-BLACK-8FAM` | Video-Türstation, 8 Klingeltaster, schwarz | video-tuerstation | EVO HD | `evo-hd-black-8fam.png` · `evo-hd-black-8fam.svg` | yes |
| `EVO-HD-FN-2FAM` | Video-Türstation mit Fingerprint, 2 Klingeltaster | video-tuerstation | EVO HD | `evo-hd-fn-2fam.png` · `evo-hd-fn-2fam.svg` | yes |
| `EVO-HD-TOUCH-7` | Video-Türstation mit Touchdisplay | video-tuerstation | EVO HD | `evo-hd-touch-7.png` · `evo-hd-touch-7.svg` | — |
| `EVO-HD-1FAM-AUDIO` | Audio-Türstation, 1 Klingeltaster | audio-tuerstation | EVO HD | `evo-hd-1fam-audio.png` · `evo-hd-1fam-audio.svg` | — |
| `EVO-HD-2FAM-AUDIO` | Audio-Türstation, 2 Klingeltaster | audio-tuerstation | EVO HD | `evo-hd-2fam-audio.png` · `evo-hd-2fam-audio.svg` | — |
| `EVO-HD-3FAM-AUDIO` | Audio-Türstation, 3 Klingeltaster | audio-tuerstation | EVO HD | `evo-hd-3fam-audio.png` · `evo-hd-3fam-audio.svg` | — |
| `EVO-HD-4FAM-AUDIO` | Audio-Türstation, 4 Klingeltaster | audio-tuerstation | EVO HD | `evo-hd-4fam-audio.png` · `evo-hd-4fam-audio.svg` | — |
| `EVO-HD-6FAM-AUDIO` | Audio-Türstation, 6 Klingeltaster | audio-tuerstation | EVO HD | `evo-hd-6fam-audio.png` · `evo-hd-6fam-audio.svg` | — |
| `EVO-HD-8FAM-AUDIO` | Audio-Türstation, 8 Klingeltaster | audio-tuerstation | EVO HD | `evo-hd-8fam-audio.png` · `evo-hd-8fam-audio.svg` | — |
| `EVO-8EXT` | Erweiterung, 8 Klingeltaster | erweiterung | EVO HD | `evo-8ext.png` · `evo-8ext.svg` | — |
| `EVO-12EXT` | Erweiterung, 12 Klingeltaster | erweiterung | EVO HD | `evo-12ext.png` · `evo-12ext.svg` | — |
| `EVO-BLACK-8EXT` | Erweiterung, 8 Klingeltaster, schwarz | erweiterung | EVO HD | `evo-black-8ext.png` · `evo-black-8ext.svg` | — |
| `EVO-BLACK-12EXT` | Erweiterung, 12 Klingeltaster, schwarz | erweiterung | EVO HD | `evo-black-12ext.png` · `evo-black-12ext.svg` | — |
| `EVO-HD-7M` | Monitor 7″ | monitor | EVO HD | `evo-hd-7m.png` · `evo-hd-7m.svg` | yes |
| `EVO-HD-7M-BLACK` | Monitor 7″, schwarz | monitor | EVO HD | `evo-hd-7m-black.png` · `evo-hd-7m-black.svg` | yes |
| `EVO-HD-MINI-4.3M` | Monitor Mini 4,3″ | monitor | EVO HD | `evo-hd-mini-43m.png` · `evo-hd-mini-43m.svg` | — |
| `EVO-HD-MINI-BLACK-4.3M` | Monitor Mini 4,3″, schwarz | monitor | EVO HD | `evo-hd-mini-black-43m.png` · `evo-hd-mini-black-43m.svg` | — |
| `EVO-HD-TALK` | Audiostation | audiostation | EVO HD | `evo-hd-talk.png` · `evo-hd-talk.svg` | — |
| `EVO-HD-BLACK-TALK` | Audiostation, schwarz | audiostation | EVO HD | `evo-hd-black-talk.png` · `evo-hd-black-talk.svg` | — |
| `EVO-HD-C5001` | Netzteil | netzteil | EVO HD | `evo-hd-c5001.png` · `evo-hd-c5001.svg` | yes |
| `EVO-HD-DL` | Türöffner-Modul | modul | EVO HD | `evo-hd-dl.png` · `evo-hd-dl.svg` | — |
| `EVO-HD-2WL` | LAN-Konverter | modul | EVO HD | `evo-hd-2wl.png` · `evo-hd-2wl.svg` | — |
| `EVO-1FAM` | Video-Türstation, 1 Klingeltaster | video-tuerstation | EVO | `evo-1fam.png` · `evo-1fam.svg` | — |
| `EVO-2FAM` | Video-Türstation, 2 Klingeltaster | video-tuerstation | EVO | `evo-2fam.png` · `evo-2fam.svg` | — |
| `EVO-3FAM` | Video-Türstation, 3 Klingeltaster | video-tuerstation | EVO | `evo-3fam.png` · `evo-3fam.svg` | — |
| `EVO-4FAM` | Video-Türstation, 4 Klingeltaster | video-tuerstation | EVO | `evo-4fam.png` · `evo-4fam.svg` | — |
| `EVO-5FAM` | Video-Türstation, 5 Klingeltaster | video-tuerstation | EVO | `evo-5fam.png` · `evo-5fam.svg` | — |
| `EVO-7FAM` | Video-Türstation, 7 Klingeltaster | video-tuerstation | EVO | `evo-7fam.png` · `evo-7fam.svg` | — |
| `EVO-8FAM` | Video-Türstation, 8 Klingeltaster | video-tuerstation | EVO | `evo-8fam.png` · `evo-8fam.svg` | — |
| `EVO-6FAM-RFID` | Video-Türstation mit RFID, 6 Klingeltaster | video-tuerstation | EVO | `evo-6fam-rfid.png` · `evo-6fam-rfid.svg` | — |
| `EVO-BLACK-1FAM` | Video-Türstation, 1 Klingeltaster, schwarz | video-tuerstation | EVO | `evo-black-1fam.png` · `evo-black-1fam.svg` | — |
| `EVO-BLACK-2FAM` | Video-Türstation, 2 Klingeltaster, schwarz | video-tuerstation | EVO | `evo-black-2fam.png` · `evo-black-2fam.svg` | — |
| `EVO-BLACK-3FAM` | Video-Türstation, 3 Klingeltaster, schwarz | video-tuerstation | EVO | `evo-black-3fam.png` · `evo-black-3fam.svg` | — |
| `EVO-BLACK-4FAM` | Video-Türstation, 4 Klingeltaster, schwarz | video-tuerstation | EVO | `evo-black-4fam.png` · `evo-black-4fam.svg` | — |
| `EVO-AP-1FAM` | Video-Türstation Aufputz, 1 Klingeltaster | video-tuerstation | EVO | `evo-ap-1fam.png` · `evo-ap-1fam.svg` | — |
| `EVO-AP-2FAM` | Video-Türstation Aufputz, 2 Klingeltaster | video-tuerstation | EVO | `evo-ap-2fam.png` · `evo-ap-2fam.svg` | — |
| `EVO-AP-3FAM` | Video-Türstation Aufputz, 3 Klingeltaster | video-tuerstation | EVO | `evo-ap-3fam.png` · `evo-ap-3fam.svg` | — |
| `EVO-AP-4FAM` | Video-Türstation Aufputz, 4 Klingeltaster | video-tuerstation | EVO | `evo-ap-4fam.png` · `evo-ap-4fam.svg` | — |
| `EVO-7M` | Monitor 7″ | monitor | EVO | `evo-7m.png` · `evo-7m.svg` | — |
| `EVO-7M-BLACK` | Monitor 7″, schwarz | monitor | EVO | `evo-7m-black.png` · `evo-7m-black.svg` | — |
| `EVO-QUICK-4.3M` | Monitor 4,3″ | monitor | EVO | `evo-quick-43m.png` · `evo-quick-43m.svg` | — |
| `EVO-QUICK-BLACK` | Monitor 4,3″, schwarz | monitor | EVO | `evo-quick-black.png` · `evo-quick-black.svg` | — |
| `EVO-MINI-4.3M` | Monitor Mini 4,3″ | monitor | EVO | `evo-mini-43m.png` · `evo-mini-43m.svg` | — |
| `EVO-TALK` | Audiostation | audiostation | EVO | `evo-talk.png` · `evo-talk.svg` | — |
| `EVO-C4001` | Netzteil | netzteil | EVO | `evo-c4001.png` · `evo-c4001.svg` | — |
| `EVO-HD-PRO-7W` | Monitor 7″ | monitor | EVO HD PRO | `evo-hd-pro-7w.png` · `evo-hd-pro-7w.svg` | — |
| `EVO-HD-PRO-7B` | Monitor 7″, schwarz | monitor | EVO HD PRO | `evo-hd-pro-7b.png` · `evo-hd-pro-7b.svg` | — |
| `EVO-HD-PRO-CAM` | Kameramodul | pro-modul | EVO HD PRO | `evo-hd-pro-cam.png` · `evo-hd-pro-cam.svg` | — |
| `EVO-HD-PRO-AUD-0` | Sprachmodul ohne Klingeltaster | pro-modul | EVO HD PRO | `evo-hd-pro-aud-0.png` · `evo-hd-pro-aud-0.svg` | — |
| `EVO-HD-PRO-AUD-1K` | Sprachmodul, 1 Klingeltaster, graviert | pro-modul | EVO HD PRO | `evo-hd-pro-aud-1k.png` · `evo-hd-pro-aud-1k.svg` | — |
| `EVO-HD-PRO-AUD-1KN` | Sprachmodul, 1 Klingeltaster, hinterleuchtet | pro-modul | EVO HD PRO | `evo-hd-pro-aud-1kn.png` · `evo-hd-pro-aud-1kn.svg` | — |
| `EVO-HD-PRO-AUD-2K` | Sprachmodul, 2 Klingeltaster, graviert | pro-modul | EVO HD PRO | `evo-hd-pro-aud-2k.png` · `evo-hd-pro-aud-2k.svg` | — |
| `EVO-HD-PRO-AUD-2KN` | Sprachmodul, 2 Klingeltaster, hinterleuchtet | pro-modul | EVO HD PRO | `evo-hd-pro-aud-2kn.png` · `evo-hd-pro-aud-2kn.svg` | — |
| `EVO-HD-PRO-KEY-4K` | Ruftastenmodul, 4 Klingeltaster, graviert | pro-modul | EVO HD PRO | `evo-hd-pro-key-4k.png` · `evo-hd-pro-key-4k.svg` | — |
| `EVO-HD-PRO-KEY-4KN` | Ruftastenmodul, 4 Klingeltaster, hinterleuchtet | pro-modul | EVO HD PRO | `evo-hd-pro-key-4kn.png` · `evo-hd-pro-key-4kn.svg` | — |
| `EVO-HD-PRO-INF` | Infoschild, graviert | pro-modul | EVO HD PRO | `evo-hd-pro-inf.png` · `evo-hd-pro-inf.svg` | — |
| `EVO-HD-PRO-INF-KN` | Infoschild, hinterleuchtet | pro-modul | EVO HD PRO | `evo-hd-pro-inf-kn.png` · `evo-hd-pro-inf-kn.svg` | — |
| `EVO-HD-PRO-RFG` | Fingerprint- und RFID-Modul | pro-modul | EVO HD PRO | `evo-hd-pro-rfg.png` · `evo-hd-pro-rfg.svg` | — |
| `EVO-HD-PRO-COVER` | Blindplatte | pro-modul | EVO HD PRO | `evo-hd-pro-cover.png` · `evo-hd-pro-cover.svg` | — |
| `EVO-HD-PRO-F1M` | Einbaudose, 1 Modul | gehaeuse | EVO HD PRO | `evo-hd-pro-f1m.png` · `evo-hd-pro-f1m.svg` | — |
| `EVO-HD-PRO-F3M` | Einbaudose, 3 Module | gehaeuse | EVO HD PRO | `evo-hd-pro-f3m.png` · `evo-hd-pro-f3m.svg` | — |
| `EVO-HD-PRO-FJB-3M` | Unterputzdose, 3 Module | gehaeuse | EVO HD PRO | `evo-hd-pro-fjb-3m.png` · `evo-hd-pro-fjb-3m.svg` | — |
| `EVO-HD-PRO-FRAME-3M` | Rahmen, 3 Module | gehaeuse | EVO HD PRO | `evo-hd-pro-frame-3m.png` · `evo-hd-pro-frame-3m.svg` | — |
| `EVO-HD-PRO-JB2M-NO` | Aufputzdose, 2 Module, ohne Öffnung | gehaeuse | EVO HD PRO | `evo-hd-pro-jb2m-no.png` · `evo-hd-pro-jb2m-no.svg` | — |
| `EVO-HD-PRO-JB2M-L` | Aufputzdose, 2 Module, Öffnung links | gehaeuse | EVO HD PRO | `evo-hd-pro-jb2m-l.png` · `evo-hd-pro-jb2m-l.svg` | — |
| `EVO-HD-PRO-JB2M-R` | Aufputzdose, 2 Module, Öffnung rechts | gehaeuse | EVO HD PRO | `evo-hd-pro-jb2m-r.png` · `evo-hd-pro-jb2m-r.svg` | — |
| `EVO-HD-PRO-JB2M-LR` | Aufputzdose, 2 Module, beidseitig | gehaeuse | EVO HD PRO | `evo-hd-pro-jb2m-lr.png` · `evo-hd-pro-jb2m-lr.svg` | — |
| `EVO-HD-PRO-JB3M-NO` | Aufputzdose, 3 Module, ohne Öffnung | gehaeuse | EVO HD PRO | `evo-hd-pro-jb3m-no.png` · `evo-hd-pro-jb3m-no.svg` | — |
| `EVO-HD-PRO-S3M` | Einbaudose Aufputz, 3 Module | gehaeuse | EVO HD PRO | `evo-hd-pro-s3m.png` · `evo-hd-pro-s3m.svg` | — |
| `EVO-HD-PRO-ML` | Modulhebel | gehaeuse | EVO HD PRO | `evo-hd-pro-ml.png` · `evo-hd-pro-ml.svg` | — |

Not in the library yet (no clean cut-out): EVO-HD-5FAM, -7FAM, FN-1/3/4FAM, most black EVO HD stations,
EVO-HD-7M-WIFI, EVO-HD-PRO F2M/F6M, FJB-2M/-6M, FRAME-2M/-6M, JB3M-L/-R/-LR, S2M, EVO-HD-KLT8-24, ENTRI, ERA;
from the EVO line EVO-7M-WIFI / -WIFI-BLACK (no front shot of their own), EVO-DL, EVO-EV4, EVO-MD, EVO-GW, EVO-CAM
(shot at an angle only, no Figma drawing exported yet).

## 10 · Product and image

- Order in every list: **EVO HD PRO** (flagship, modular) → **EVO HD** (mid range, digital) →
  **EVO** (entry, analog) → **ENTRI** (ready sets, always last). Spelling with spaces, no hyphen.
- System first, then parts: Video-Türsprechanlage is the system; Video-Türstation, Monitor,
  Audiostation are parts.
- Cut-outs on white or `#F3F3F3`, no shadow, no frame; caption = article number on the product axis.
  EVO HD PRO modules on a plate get a 1 mm black outline; EVO HD parts never.
- True size from millimetres against door, brick, hand — never as a share of the frame.
- Brushed stainless steel is standard; every RAL colour is Sonderanfertigung. There is no black
  EVO HD PRO.
- AI builds only the scene. The product stays a real photo or CAD. Upscalers invent logos on
  modules: mask them back from the original.
- No stock images: no handshakes, padlock icons, blue data streams. Image types: product at the
  entrance (daylight, real façade), product in the room (wall, real light), the stand.

## 11 · Social media

Strategy and research behind these rules: `Security/social-strategy.md` in the Balter workspace (not in the public
copy). This section is what an agent needs to plan, cut, design and check a post.

### 11a · Strategy in one screen
- **Goal:** relevant followers (installers, electricians, security technicians in DACH) who follow, save, send and
  ask. Measure follows per post, sends per reach, 3-s hold, average watch time — not views.
- **Channel jobs:** Discovery = Instagram Reels (+ Trial Reels), same master to YouTube Shorts (TikTok optional) ·
  Search = YouTube long with chapters · Trust = LinkedIn (page + personal profiles + monthly newsletter) · Community =
  Facebook trade groups (answer as a person), Instagram Collab posts · Service = WhatsApp Business + WhatsApp Channel.
  Do not plan X, Telegram or Pinterest for Security.
- **Rubrics — every post belongs to exactly one:**

| # | Rubric (on screen) | Content | Format | Share |
|---|---|---|---|---|
| R1 | Montage in 60 s | one install step on site: hands, top view, the terminal, the result | Reel 20–60 s + YouTube long | 25 % |
| R2 | Balter antwortet | a Balter technician answers one real installer question; question card first | Reel 30–60 s, LinkedIn video | 15 % |
| R3 | Fehler am Bau | one mistake and its fix, "Falsch" above / "Richtig" below | Reel 15–40 s, carousel | 10 % |
| R4 | System erklärt | 2-Draht vs IP, Wohneinheiten, Netzteil rules, schema (9a/9b) | carousel 4:5, LinkedIn document | 15 % |
| R5 | Im Test | proof with a measured number in the result card | Reel 20–45 s, YouTube | 10 % |
| R6 | Projekt des Monats | a customer's finished install, installer named, Collab post | carousel + Reel | 10 % |
| R7 | Aus der Werkstatt | Sonderanfertigung, engraving, RAL, warehouse | Reel, carousel | 5 % |
| R8 | Neu bei Balter / Termine | launches framed as "Sie haben gefragt", fairs, Schulung | feed product/date templates, Stories | ≤ 20 % |

  At least 60 % R1–R4; never two R8 in a row.
- **Rubric plate (series recognition):** white pill, Inter 600 28 px caps, orange dot 14 px, at x 132 / y 290 in a
  reel (y 120 in a feed post), episode "3/8" after the name. Fixed forms: step card (R1, R7), question card (R2),
  Falsch/Richtig with black ✕ / white ✓ marks (R3, no red), schema (R4), result card bottom-left (R5), installer credit
  (R6), product on black (R8).
- **Rhythm (1–2 people):** Instagram 3/week (2 Reels + 1 carousel, Stories on posting days) · Facebook cross-post ·
  Shorts 2/week · YouTube long 2/month · LinkedIn 2 page posts + 1 personal each from sales and management + newsletter
  monthly · WhatsApp Channel 2–4/month. Week: Mon LinkedIn doc (R4) · Tue Reel (R1) · Wed carousel (R3/R4/R6) · Thu Reel
  (R2/R5) · Fri Stories/WhatsApp (R8). One filming day a month ≈ 8 reel masters + 1–2 tutorials.
- **Content-plan row:** KW/date · rubric · channels · format · hook (first caption line + first 2 s) · search word ·
  article numbers · footage + consent · CTA · status · result after 7 days (views, reach, watch time, sends, saves,
  comments, profile visits, follows, Stichtag). Asana "Content & Newsletter Planung", task `SM-YYYY-KWnn - <topic>`.

### 11b · Platforms (what each algorithm rewards)
- **Instagram:** watch time, sends per reach (strongest for non-followers), likes per reach. Reels for reach,
  carousels for interaction (up to 20 slides; schedulers often 10), Stories only reach followers, Trial Reels test
  hooks on non-followers. 20–60 s for discovery, how-to up to 2:45, never over 3 min for non-followers. Caption
  2,200, ~125 visible; ≤ 5 hashtags. Profile grid is 3:4. Own footage only (originality rules).
- **Facebook:** cross-post of Instagram; trade groups are where installers ask — answer as a person, never advertise.
- **YouTube long:** CTR × retention, search (47 % of Balter's views). One video per searched question; title = the
  query; chapters from 00:00, at least three.
- **Shorts:** every start counts as a view since 2025-03-31 — judge engaged views. Link each Short to its long video
  by hand in Studio (not possible via API).
- **TikTok:** search reads caption, on-screen text and speech. Second outlet for the same masters only.
- **LinkedIn:** topic matching by an LLM since March 2026 — stay on one professional topic. Document carousels (PDF 4:5)
  get the most engagement; personal profiles reach far more than the page. Links in the first comment.
- **WhatsApp:** Channel for updates (followers opt in, anonymous); Business for support; marketing messages only with
  logged double opt-in (UWG).

### 11c · Formats and safe zones
Data: `assets/social/safe-zones.json` (keep-free px per edge, researched 2026-11-25). Overlays for Resolve / Figma /
After Effects: `python3 scripts/safe_zones.py png <dir>` (also in `assets/social/overlays/`); check text boxes with
`python3 scripts/safe_zones.py check x <format-id> x y w h …`.

| Format | Pixels | Keep free (top / bottom / left / right) |
|---|---|---|
| 9:16 master (IG, FB, TikTok, Shorts, LinkedIn vertical) | 1080 × 1920 | 270 / 672 / 120 / 192 → text only in x 120–888, y 270–1248 |
| Instagram Story | 1080 × 1920 | 270 / 340 / 65 / 65 |
| Reel cover | 1080 × 1920 | title inside the centred 1012 × 1350 and above y 1300 |
| Feed / carousel 4:5 | 1080 × 1350 | profile grid crops 34 px left and right; layout margin 64 |
| LinkedIn document | 1080 × 1350 | 60 / 100 / 60 / 60 (viewer controls) |
| YouTube 16:9 | 1920 × 1080 | lower thirds above y 900 (captions, controls) |
| YouTube thumbnail | 1280 × 720 | 5 % border; duration badge bottom right ~240 × 100 |

Headline at y 300–700, product at y 600–1240 in the 9:16 master. Never a plate or caption over the product.

Proven on the real apps (iPhone 13 Pro Max, own posts, 2026-11-25; proofs in the brand book, chapter 11):
- On tall phones Instagram fills 1284 × 2529 px with the 9:16 file and **crops about 6 % of the frame left and right**
  — keep text off the outer 120 / 192 px anyway.
- Facebook's share button and Instagram's caption sit exactly where our old subtitles were (below y 1248): subtitles
  and lower thirds end at y 1248.
- TikTok briefly shows a "liked by" avatar at the left edge, reaching about 90 px into the frame.
- Story: header (progress, name, close) in the top 270 px, "send message" below the canvas.
- Profile grid crops reel covers to 3:4: plates at the edge ("TEIL 1/2") get cut — cover titles in the centred 1012 × 1350.
- Method for new proofs (any format change): drive the phone with WebDriverAgent (`scripts/iphone-capture/wda.py` in the
  workspace), find the video rectangle from frame differences (`vrect.py`), lay the zone over it (`proof.py`), blur
  other people.

### 11d · Templates, plates, captions

- Grid 1080: margin 64, 6 columns of 136, gutter 24, baseline 8. 4:5 and 9:16 each get their own
  layout; never stretch or pad a feed post to 9:16.
- Smallest text 28 px feed, 32 px reel.
- Radii at 1080 px: window in the frame 64 (frame 12 px black) · image card, panel 48 · product
  plate, cell 32 · subtitle box, chip 16 · pills round. Concentric inward with 16 px steps. Never
  cut a rounded corner; no text closer than 32 px to a corner; no zoom that moves the rounding.
- Feed templates: product (frame, window, plate) · infographic (one number per page) · date (fixed
  cells, photo on top) · schema (rules of 9a) · carousel title (panel at the bottom, counter on top)
  · end card (black, logo, contact). Do not invent a new form.
- Reels: title on top under the safe zone (from y 290); lower third bottom left above 672 px, from x 120; detail callout =
  white 28 px dot, 3 px line, white pill (max. two at once); end card stands 2 s.
- Overlays on video: solid white panel, radius 32–48, padding 26–40, text left (no semi-transparent
  white). Subtitles black 72 %, radius 16, Inter 700 48 px white, max. 2 lines, wrapped by width inside
  the usable area (about 26–30 characters), centred in that area above the bottom zone (`scripts/captions.py`). Hold ≥ 2 s plus 1.2 s per line; in 400 ms with 36 px rise, out
  250 ms opacity only. Logo at start or end, never a permanent watermark. Always subtitles.
- Never: a plate over the product, text in safe zones, orange strokes/underlines/frames, fake "Jetzt
  kaufen" buttons, other fonts, emoji in the graphic (sparingly allowed in the caption).
- Captions: German, "Sie", one version per channel — Instagram/Facebook 600–1,200 characters,
  LinkedIn 800–1,600, TikTok 100–150. First line is the hook (~125 characters before "mehr").
  Contact always written out: sales@balter.de, never "Link in der Bio". Hashtags at the end:
  Instagram at most 5 (platform limit since December 2025), LinkedIn 3–5; the search word goes in the first
  line, on screen and in speech.
- Workflow: pick template → real pixels → check (safe zones, one orange, Science Gothic once,
  smallest text, rounding intact) → approval by Balter Design und Marketing → publish. Report
  figures 7 days after posting, with the cut-off date.

## 12 · Video

- Product on black, picture inside the round window, label top left, logo top right.
- At 1920 × 1080: frame 12 px black, radius 40, picture always in the window, never full-bleed ·
  label Science Gothic 28 px at x 60, y 56, caps · logo white 150 px wide, 60 px margin (black on
  light panels) · title Science Gothic 72 or Inter 700 64–96, centred, max. two lines · kicker Inter
  400 24 px +0.5 em grey 62 % · big number Inter 800 200–260 px, unit Inter 300 beside it, approved
  figures only · article number JetBrains Mono 500 26 px white 70 %, centred under the product ·
  panel radius 32, padding 48, white or `#F2F2F2`, soft shadow only here. Scale to 1920: window 40,
  panel 32, card 24.
- Hard cuts or 12-frame dissolves; no wipes, zooms, glitches. Text in 400 ms with 36 px rise, out
  250 ms, ≥ 2 s, 3 words per second. Camera moves slow and linear, max. 5 % zoom per shot.
- Loudness −14 LUFS for social and YouTube; trade-fair monitors must work without sound.
- Colour: Sony S-Log3 with a curve, then colour space transform to Rec.709; no manufacturer LUT.
- Show the cut on the timeline before rendering. Export H.264: 16:9, 9:16 and 4:5 as separate cuts.
  File name `BALTER_Thema_v12_9x16.mp4`.
- Laptop mockups: MacBook, straight front view, lid does not move. Trade-fair and partner logos in
  original colours on their own plate. No orange divider strokes.

### 12a · What makes a short or a tutorial hold (frame-by-frame research, 2026-11-25)
- **0–3 s:** the result, the measured number or the mistake, plus the sentence an installer searches for
  ("Türsprechanlage auf 2 Adern nachrüsten"). No intro sting on a Reel.
- **3–7 s:** who speaks, in one line ("Ich bin Techniker bei Balter, so geht es").
- **Steps:** hands and top view, 4–7 s per shot; fast cuts (1–2 s) only in the hook and in action.
- **Name the mistake of each step** (wires swapped, screw too tight, power before the module): it keeps viewers.
- **Speed up waiting** (app pairing, boot) 4–8× with the real device in frame.
- **One graphic language:** rubric plate, step card, result card bottom-left (bold number, unit light, what was
  measured, date), dot-line-pill on the detail, summary table. Highlight what is being said; never decorate.
- **Real millimetres, real wall box, real terminals in macro** beat renders.
- **Sound:** close clean voice; keep real device sounds (terminal click, door-opener buzz); music about −18 dB
  under the voice or none; −14 LUFS.
- **Brand:** logo at start or end only; the product in frame is the brand. CTA at the end, one comment question in
  the middle. Sponsored creator content carries "Werbung/Anzeige".

### 12b · Production pipeline — automatic or co-pilot in DaVinci Resolve
Default stack (free first): DaVinci Resolve Studio 21.2 with its built-in MCP (only that one — a community Resolve MCP
beside it can conflict), WhisperX large-v3 for German word timings (ElevenLabs Scribe as fallback), ffmpeg, this
skill's scripts. Tools research: `Security/social/research/editing-tools.md` (workspace).

1. **Plan:** rubric, hook, search word, shot list (content-plan row, 11a).
2. **Ingest (Resolve):** bins raw / B-roll / sound / graphics; clip names `KWnn_Rubrik_Thema_take`; markers on product
   shots and silences; colour: Custom Curves node, then CST S-Gamut3.Cine/S-Log3 → Rec.709 (no Sony LUT).
3. **Transcript:** WhisperX word timings (JSON) or Resolve's transcript. Apply `assets/social/caption-glossary.json`.
4. **Selects:** the agent proposes in/out points from the transcript (hook first, one idea per Reel); **a human
   approves**.
5. **Rough cut:** Resolve removes silence; a filler-word pass by timings; the human trims rhythm (Resolve's API cannot
   cut or move clips on the timeline — in co-pilot mode the editor cuts, the agent prepares).
6. **Captions:** `python3 scripts/captions.py words.json out.srt` → SRT for the Resolve subtitle track (co-pilot), or
   `--burn in.mp4 out.mp4 --font Inter-Bold.ttf --format master-9x16` (automatic). **Proof-read numbers and product
   names before burning in.**
7. **Graphics:** rubric plate, step/question/result cards as the templates of chapter 11 (HTML rendered with a
   transparent background, or Fusion titles in Resolve where the editor must retype).
8. **Sound:** voice up, music ≈ −18 dB under it, normalise to −14 LUFS.
9. **Formats:** 9:16 master first; 4:5 and 16:9 as their own cuts; Smart Reframe, then a manual check.
10. **QC:** `scripts/safe_zones.py check` for every text box; overlay PNG on the top track for a visual check (switch
    off before render); hook visible in the first 3 s; captions ≤ 2 lines; loudness; file name
    `BALTER_Thema_v12_9x16.mp4`.
11. **Cover:** 1080 × 1920, title in the centred 1012 × 1350 above y 1300.
12. **Publish:** Metricool as a draft (Free plan: 20 posts a month in total, no LinkedIn); a human releases it.
    LinkedIn natively. Link the Short to its long video in YouTube Studio.
13. **Measure:** day 7, with Stichtag, into the Asana task.

Human decisions: selects, final cut, caption proof, approval to publish. Show the cut on the timeline before rendering.

## 13 · E-mail (Brevo newsletters)

- 600 px wide, sections alternating white and black. Every row exists twice: desktop (text left,
  image right) and mobile (image on top, text centred, title 20 instead of 28 px).
- Fonts Inter, Helvetica, Arial; Science Gothic titles only as images with alt text, else Inter 700.
- Buttons 48 px, radius 10, black; orange only for the one main action, black text on it.
- GIFs under 1 MB, 480 px wide, 3–5 s per frame, calm first frame.
- Subject starts with "Balter", preview text up to 90 characters, send on Tuesdays. Contact
  sales@balter.de with a prefilled mail per topic.
- In Brevo **never** overwrite the HTML through the API (it destroys the drag-and-drop editor for
  good); edit texts in developer mode after saving a template; add rows by duplicating. Never black
  on black in the header image.
- Every newsletter is approved by Balter Design und Marketing before sending. Figures after 7 days
  with the cut-off date.

## 14 · Language (German copy)

Speak like a technician who explains well: short sentences, clear facts, no superlatives.
Examples of the tone: "Technologie trifft Design." · "Klingeln. Sehen. Sprechen. Öffnen." ·
"Nicht von der Stange. Für Ihr Gebäude." · "Ein Hotel hat nicht eine Tür, sondern fünf."

- "Sie" (du only on career pages). **BALTER** in titles, **Balter** in text, "Balter GmbH" only in
  the footer. Titles short, often two-part, with a full stop.
- **The words:**
  | Use | Never |
  |---|---|
  | **Video-Türsprechanlage** (hyphen) = the system, leads every list | Türsprechanlage without Video- for camera systems, Gegensprechanlage, Intercom, Klingelanlage |
  | **Video-Türstation** (outside, camera) · **Audio-Türstation** (outside, no camera) | bare "Türstation" |
  | **Monitor** (inside, screen) · **Audiostation** (inside, audio handset) | Videostation, Haustelefon, Innensprechstelle |
  | Canonical trio: "Video-Türstationen, Monitore und Audiostationen" | starting a list with a component |
  | **Netzteil** | Hauptstromverteiler |
  | **Klingeltaster** | Klingelknopf |
  | **Zutrittskontrolle** | Zugangskontrolle |
  | **Sonderanfertigung** | Sonderlösung, Custom-Lösung |
  | **Türöffner-Modul** · **Sprachmodul** · **Unterputz / Aufputz** | Türöffner Modul, Sprechmodul |
  | **Einheiten** (default), Familien or Teilnehmer by context; **Wohneinheit (WE)** in plans | Parteien |
- **Approved figures only:** up to 64 Wohneinheiten on one Video-Türstation (EVO HD, EVO HD PRO),
  128 with EVO HD Touch, 1 Master + 3 Slave monitors per flat (max. 4). Anything else needs a
  source from the person.
- Never: "höchste Qualität", "setzt neue Maßstäbe", manufacturing partner, suppliers, revenue.

## 15 · Design tokens

`assets/tokens.css` holds every value of this book as CSS custom properties (`--b-*`): colours,
fonts, type sizes, 4 px spacing scale (4 … 128), radii, control heights, frame sizes per breakpoint,
shadows (only for floating things), easing and durations, chart values. New interfaces start from
these tokens, never from an old screenshot. Import it, then build:

```css
@import url("https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Science+Gothic:wght@700&family=JetBrains+Mono:wght@500;600&display=swap");
/* then paste assets/tokens.css */
```

## Before you hand anything over — checklist

- [ ] Security only, nothing from Home.
- [ ] Orange at most once on the surface, text on it black, no orange lines.
- [ ] Only Science Gothic, Inter, JetBrains Mono; Science Gothic once per surface.
- [ ] Logo one colour, clear space kept, correct variant for the size.
- [ ] Real device pictures, true size, nothing drawn or generated in place of a product.
- [ ] Every figure approved or sourced; no partner or supplier names.
- [ ] German words from section 14; "Video-Türsprechanlage" leads.
- [ ] Rounded corners intact; no hover zoom inside rounded frames.
- [ ] You looked at the result (rendered, at the real size) before saying it is done.

---

## Install this skill

The skill is one folder, `balter-brand/`, with `SKILL.md` at its root. Repository:
**https://github.com/BalterMarketing/balter-brand-skill**

**Any agent, one command** (skills CLI, installs for Claude Code, Codex, Cursor and others):

```bash
npx skills add BalterMarketing/balter-brand-skill
```

**Claude Code** (all projects, or put it in `.claude/skills/` of one project):

```bash
git clone https://github.com/BalterMarketing/balter-brand-skill /tmp/balter-brand-skill && cp -R /tmp/balter-brand-skill/balter-brand ~/.claude/skills/
```

**Codex CLI** (all projects, or put it in `.agents/skills/` of one project):

```bash
git clone https://github.com/BalterMarketing/balter-brand-skill /tmp/balter-brand-skill && cp -R /tmp/balter-brand-skill/balter-brand ~/.codex/skills/
```

**Without installing:** give the agent this file (`SKILL.md`) or its link and say "Arbeite nach
dem BALTER Markenhandbuch". The wiring-plan generator needs the whole folder and Python 3.

Then ask in plain words, for example: "Baue einen Instagram-Post 4:5 für EVO HD Touch nach dem
BALTER Markenhandbuch" or "Baue einen Verdrahtungsplan: EG bis 3.OG, je zwei Wohneinheiten,
EVO-HD-8FAM, Türöffner intern".
