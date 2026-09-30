#!/usr/bin/env python3
"""Build the 1puni org profile artwork.

Everything under profile/assets/ is generated; edit this file, not the SVGs.
Palette, type and copy follow https://1puni.com — since September 30, 2026 the
moonlit address: a black sky with the illustrated moon, parchment, sea-grey
and rust, set in Bricolage Grotesque with Georgia italics.

Text widths are measured here and pinned with textLength, so a poster lays
out the same whether the viewer's machine has Bricolage, Arial or a stand-in.
Motion is finite and stops. The resting frame is the punchline, so a renderer
that skips animation (or honours prefers-reduced-motion) still tells the joke.

Requires Pillow plus the bundled fonts (tools/fonts/, both OFL): Bricolage
Grotesque for the grotesque faces, Gelasio as the metric-compatible stand-in
for Georgia when the macOS system fonts are absent. Pins come out the same
either way. The moon, moon dust and Nike's side elevation are the site's own
accepted artwork, kept under tools/art/.
"""

import base64
import io
from pathlib import Path

from PIL import Image, ImageChops, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parent.parent
BRAND = ROOT / "brand"
OUT = ROOT / "profile" / "assets"
FONTS = ROOT / "tools" / "fonts"
ARTWORK = ROOT / "tools" / "art"

INK, PAPER = "#171918", "#f8f8ed"
DUST, SEA, RUST = "#d8c7aa", "#a9bbb7", "#b96144"
CHALK, QUIET, DEEP = "#e6ddcf", "#655f56", "#a64730"
NIGHT, MOON = "#000000", "#bdb4a6"
LINE = "#17191830"
SANS = "'Bricolage Grotesque', Arial, sans-serif"
SERIF = "Georgia, 'Times New Roman', serif"
MONO = "ui-monospace, SFMono-Regular, Menlo, Consolas, 'Liberation Mono', monospace"

SYSTEM = Path("/System/Library/Fonts/Supplemental")
# face -> (candidate paths, variable-font instance: named string or wght axis)
FACES = {
    "display": ([FONTS / "bricolage-grotesque.ttf"], 800),
    "semibold": ([FONTS / "bricolage-grotesque.ttf"], 650),
    "regular": ([FONTS / "bricolage-grotesque.ttf"], 400),
    "georgia-italic": ([SYSTEM / "Georgia Italic.ttf", FONTS / "Gelasio-Italic[wght].ttf"], None),
    "georgia-bold": ([SYSTEM / "Georgia Bold.ttf", FONTS / "Gelasio[wght].ttf"], "Bold"),
}

_FONTS = {}


def load(face):
    if face not in _FONTS:
        paths, instance = FACES[face]
        for path in paths:
            if path.exists():
                font = ImageFont.truetype(str(path), 400)
                if isinstance(instance, int):
                    font.set_variation_by_axes([instance])
                elif instance:
                    font.set_variation_by_name(instance)
                _FONTS[face] = font
                break
        else:
            raise FileNotFoundError(f"no font for {face!r}: {paths}")
    return _FONTS[face]


def width(text, face, size, tracking=0.0):
    """Rendered advance of text in px, including CSS-style letter-spacing (em)."""
    font = load(face)
    natural = font.getlength(text) * size / 400
    return natural + tracking * size * (len(text) - 1)


def fit(lines, face_of, size, tracking, budget):
    """Largest size <= size at which every line fits the width budget."""
    while size > 10 and max(width(t, face_of(t, i), size, tracking) for i, t in enumerate(lines)) > budget:
        size -= 1
    return size


def esc(text):
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def text(x, y, body, *, size, family=SANS, weight="normal", style="normal", fill=INK,
         tracking=0.0, face=None, anchor="start", extra=""):
    """A <text>; when face is given its width is measured and pinned."""
    pinned = ""
    if face:
        pinned = f' textLength="{width(body, face, size, tracking):.1f}" lengthAdjust="spacingAndGlyphs"'
    spacing = f' letter-spacing="{tracking * size:.2f}"' if tracking else ""
    return (f'<text x="{x}" y="{y}" font-family="{family}" font-size="{size}" font-weight="{weight}"'
            f' font-style="{style}" fill="{fill}" text-anchor="{anchor}"{spacing}{pinned}{extra}>{esc(body)}</text>')


def label(x, y, body, *, size=13, fill=QUIET, weight="650", anchor="start", tracking=0.035):
    """A Bricolage small-cap label: the moonlit replacement for the old mono eyebrow."""
    face = "display" if weight in ("750", "800") else "semibold" if weight == "650" else "regular"
    return text(x, y, body, size=size, weight=weight, fill=fill, anchor=anchor, tracking=tracking, face=face)


def mono(x, y, body, *, size=13, fill=INK, weight="bold", anchor="start", tracking=0.06):
    """Monospace stays for the artefacts that are literally paperwork."""
    return text(x, y, body, size=size, family=MONO, weight=weight, fill=fill, anchor=anchor, tracking=tracking)


def light_uri(path, target_width):
    """The logo, inverted for the night sky the way the landing footer does it."""
    art = Image.open(path).convert("RGBA")
    inverted = ImageOps.invert(art.convert("RGB"))
    art = Image.merge("RGBA", (*inverted.split(), art.split()[3]))
    return data_uri(art, target_width)


def on_paper(path, paper=DUST):
    """The site's CSS multiply, baked: paper takes the field colour, ink stays ink."""
    art = Image.open(path).convert("RGB")
    return ImageChops.multiply(art, Image.new("RGB", art.size, paper))


def data_uri(image, target_width):
    scaled = image.resize((target_width, round(image.height * target_width / image.width)), Image.LANCZOS)
    buf = io.BytesIO()
    scaled.save(buf, "PNG", optimize=True)
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode(), scaled.size


def inner(path):
    """The drawable content of an SVG file, for nesting inside a poster."""
    source = Path(path).read_text()
    return source[source.index(">", source.index("<svg")) + 1:source.rindex("</svg>")]


def svg(w, h, title, body, style=""):
    css = f"<style>{style}</style>" if style else ""
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}"'
            f' role="img" aria-labelledby="t"><title id="t">{esc(title)}</title>{css}{body}</svg>\n')


def write(name, content):
    path = OUT / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)
    print(f"{path.relative_to(ROOT)}  {len(content.encode()) / 1024:.1f} kB")


def waves(y, period, amp, x0=-140, x1=1400):
    d = f"M{x0} {y}"
    x = x0
    while x < x1:
        d += f" q{period / 4} {-amp} {period / 2} 0 t{period / 2} 0"
        x += period
    return d


def hero():
    W, H, M = 1200, 760, 44
    logo, (lw, lh) = light_uri(BRAND / "logo-horizontal.png", 400)
    logo_h = 52
    logo_w = logo_h * lw / lh
    moon = inner(ARTWORK / "moon-illustrated.svg")
    dust = inner(ARTWORK / "dust-far.svg")
    nike = inner(ARTWORK / "nike.svg")

    big = "organisation."
    big_track = -0.045
    budget = 690  # the moon owns the right of the sky; the word stays clear of it and the masts
    big_size = fit([big], lambda t, i: "display", 176, big_track, budget)
    first_size = round(big_size * 0.62)
    base1, base2 = 262, 412

    final = "rotate(-7deg)"
    style = f"""
.sign{{transform-box:fill-box;transform-origin:50% 0;transform:{final};animation:reveal 4.6s cubic-bezier(.45,0,.25,1) 1.2s 1 both}}
@keyframes reveal{{0%{{transform:rotate(2deg)}}16%{{transform:rotate(-10deg)}}30%{{transform:rotate(-4deg)}}44%{{transform:rotate(-9deg)}}56%{{transform:rotate(-6deg)}}100%{{transform:{final}}}}}
.nike{{transform-origin:860px 700px;animation:bob 3.8s ease-in-out 3}}
@keyframes bob{{0%,100%{{transform:translate(0,0) rotate(0)}}25%{{transform:translate(0,-4px) rotate(-.6deg)}}75%{{transform:translate(0,3px) rotate(.5deg)}}}}
.swell{{animation:drift 4.2s linear 3}}.swell2{{animation:drift 3.2s linear 4 reverse}}
@keyframes drift{{to{{transform:translateX(-120px)}}}}
.dust{{animation:drift 5.4s linear 2}}
@media (prefers-reduced-motion:reduce){{.sign{{animation:none;transform:{final}}}.nike,.swell,.swell2,.dust{{animation:none}}}}
"""
    body = f"""
<rect width="{W}" height="{H}" fill="{NIGHT}"/>
<svg class="dust" width="{W}" height="763" viewBox="0 0 1440 1000" preserveAspectRatio="xMinYMin slice">{dust}</svg>
<svg x="820" y="-20" width="400" height="400" viewBox="0 0 560 560">{moon}</svg>
<image href="{logo}" x="{M}" y="20" width="{logo_w:.1f}" height="{logo_h}"/>
{label(M + logo_w + 22, 42, "ONE PERSON UNICORN", size=12, fill=MOON, weight="500", tracking=0.02)}
{label(M + logo_w + 22, 60, "ENGINEERING · MACHINE INTELLIGENCE", size=12, fill=MOON, weight="500", tracking=0.02)}
{label(790, 48, "MEET GURUGEE ↘", size=14, fill=CHALK, weight="650", anchor="end")}
{label(M, 150, "1PUNI / A COMPANY IN THE FIRST PERSON", size=12, fill=DUST, weight="550", tracking=0.035)}
{text(M - 2, base1, "I am an", size=first_size, family=SERIF, style="italic", weight="400", fill=PAPER,
      tracking=-0.02, face="georgia-italic")}
{text(M - 6, base2, big, size=big_size, weight="800", fill=PAPER, tracking=big_track, face="display")}
{text(M, 466, "Intelligence gets room to think.", size=29, family=SERIF, style="italic", fill=PAPER, face="georgia-italic")}
{text(M, 502, "The machinery has to justify itself.", size=29, family=SERIF, style="italic", fill=PAPER, face="georgia-italic")}
{label(M, 546, "GURUGEE EXPLORES VOICE, MEMORY AND THE AWKWARD QUESTION.", size=12, fill=MOON, weight="500")}
{label(M, 566, "STEWARD HARNESS CONTROLS WHAT COUNTS AS DONE.", size=12, fill=MOON, weight="500")}
<g class="nike"><g transform="translate(620 320) scale(.52)">{nike}</g></g>
{label(70, 676, "↑ THE AUTOPILOT", size=11, fill=DUST)}
{label(70, 694, "IS A DRILL.", size=11, fill=DUST)}
<path class="swell" d="{waves(742, 120, 12)}" fill="none" stroke="{CHALK}" stroke-width="2" opacity=".5"/>
<path class="swell2" d="{waves(754, 120, 8, -20, 1500)}" fill="none" stroke="{CHALK}" stroke-width="1.5" opacity=".3"/>
{label(W - M, 738, "ILLUSTRATION / NOT A VESSEL SURVEY", size=9, fill=MOON, weight="500", anchor="end", tracking=0.05)}
<g class="sign">
  <text x="858" y="444" font-family="{SANS}" font-size="30" font-weight="800" fill="{PAPER}">NIKE.</text>
  <text x="858" y="468" font-family="{SERIF}" font-style="italic" font-size="19" fill="{PAPER}">A 90-year-old sailing boat.</text>
  <rect x="850" y="502" width="250" height="140" fill="{NIGHT}"/>
  <rect x="845" y="495" width="250" height="140" fill="{DUST}" stroke="{INK}" stroke-width="2.5"/>
  {label(857, 520, "1PUNI GLOBAL HEADQUARTERS", size=10, fill=INK, weight="550", tracking=0.06)}
  {text(857, 552, "ROOM FOR", size=29, weight="800", fill=INK, tracking=-0.02, face="display")}
  {text(857, 586, "EXPANSION.", size=29, weight="800", fill=INK, tracking=-0.02, face="display")}
  <rect x="857" y="602" width="226" height="22" fill="{PAPER}" stroke="{INK}" stroke-width="1.5"/>
  {label(970, 617, "INSPECT THE FOUNDATIONS ↗", size=10, fill=INK, weight="650", anchor="middle")}
</g>
"""
    write("hero.svg", svg(W, H, "1puni. A company in the first person. I am an organisation. Under the illustrated "
                             "moon, Nike — a 90-year-old sailing boat with rust-red sails and a drill at the helm — "
                             "carries a parchment sign: 1puni global headquarters, room for expansion.", body, style))


# --- Project posters -------------------------------------------------------------------

CW, CH = 800, 460
ART = (500, 88, 264, 272)  # x, y, w, h


def card(slug, *, title, bg, fg, top, headline, lede, link, status, art, bar=DUST, bar_fg=INK):
    """A poster: quiet section rule, headline with a Georgia-italic last line, art, parchment link bar."""
    dark = bg in (INK, NIGHT, RUST)  # rust reads as the night sky's warm neighbour
    rule = "#d8c7aa40" if dark else LINE
    quiet = MOON if dark else QUIET
    lines = headline
    face_of = lambda t, i: "georgia-italic" if i == len(lines) - 1 else "display"
    size = fit(lines, face_of, 58, -0.04, 440)
    y0 = 128 + (3 - len(lines)) * size * 0.5
    heads = []
    for i, line in enumerate(lines):
        y = y0 + i * size * 1.02
        if i == len(lines) - 1:
            heads.append(text(36, round(y), line, size=size + 2, family=SERIF, style="italic", fill=fg,
                              tracking=-0.045, face="georgia-italic"))
        else:
            heads.append(text(36, round(y), line, size=size, weight="800", fill=fg, tracking=-0.04, face="display"))
    lede_size = fit([lede], lambda t, i: "regular", 20, 0, 440)
    body = f"""
<rect width="{CW}" height="{CH}" fill="{bg}"/>
{label(36, 46, top[0], size=13, fill=quiet, weight="750")}
{label(CW - 36, 46, top[1], size=13, fill=quiet, weight="500", anchor="end")}
<path d="M36 62H{CW - 36}" stroke="{rule}" stroke-width="1.5"/>
{''.join(heads)}
{text(36, 340, lede, size=lede_size, fill=fg, face="regular")}
<g transform="translate({ART[0]} {ART[1]})">{art}</g>
<rect y="{CH - 80}" width="{CW}" height="80" fill="{bar}"/>
{label(36, CH - 33, link + " ↗", size=18, fill=bar_fg, weight="750", tracking=0)}
{label(CW - 36, CH - 34, status, size=11, fill=bar_fg, weight="650", anchor="end", tracking=0.06)}
<rect x="2" y="2" width="{CW - 4}" height="{CH - 4}" fill="none" stroke="{INK}" stroke-width="2.5"/>
"""
    write(f"cards/{slug}.svg", svg(CW, CH, title, body))


def grid(w, h, step=24, color="#17191822"):
    lines = "".join(f"M{x} 0V{h}" for x in range(step, w, step)) + "".join(f"M0 {y}H{w}" for y in range(step, h, step))
    return f'<path d="{lines}" stroke="{color}" stroke-width="1"/>'


def cards():
    aw, ah = ART[2], ART[3]

    chart = f"""
<g transform="rotate(3 {aw / 2} {ah / 2})">
<rect x="10" y="10" width="{aw}" height="{ah - 18}" fill="{DUST}"/>
<rect width="{aw}" height="{ah - 18}" fill="{SEA}" stroke="{INK}" stroke-width="2"/>{grid(aw, ah - 18)}
<svg width="{aw}" height="{ah - 18}" viewBox="0 0 420 350" preserveAspectRatio="xMidYMid slice">
<path d="M240-10Q160 40 215 92T198 196T251 354H440V0" fill="{DUST}" stroke="{INK}" stroke-width="3"/>
<path d="M279-10Q204 51 251 99T238 203T295 370M306-10Q235 51 280 103T270 207T330 370" fill="none" stroke="{INK}"/>
<path d="M85 319Q25 201 103 181T136 80L103 44" fill="none" stroke="{INK}" stroke-width="3" stroke-dasharray="8 7"/>
<path d="M92 52L101 29L116 50Z" fill="{RUST}" stroke="{INK}" stroke-width="2"/>
<circle cx="110" cy="285" r="26" fill="none" stroke="{INK}"/><path d="M110 250V320M75 285H145" stroke="{INK}"/>
<text x="276" y="178" font-family="{MONO}" font-size="19" font-weight="bold" fill="{INK}">LAND.</text>
<text x="267" y="202" font-family="{MONO}" font-size="14" fill="{INK}">AVOID IT.</text></svg>
</g>"""
    card("openhelm", title="OpenHelm: navigation software for the boat you're actually on. Closed beta. 1puni.com/#openhelm",
         bg=PAPER, fg=INK, top=("01 / OPENHELM", "A CHART PLOTTER, BUILT FROM THE COCKPIT"),
         headline=["The sea doesn’t", "give a shit about", "your roadmap."],
         lede="Every rock, buoy, light and depth contour is a live object.",
         link="1PUNI.COM/#OPENHELM", status="CLOSED BETA · REQUEST ACCESS", art=chart)

    pothole = f"""
<circle cx="{aw / 2}" cy="120" r="112" fill="none" stroke="{INK}" stroke-width="3"/>
<circle cx="{aw / 2}" cy="120" r="78" fill="none" stroke="{INK}" stroke-width="1.5" stroke-dasharray="3 6"/>
<circle cx="{aw / 2}" cy="120" r="44" fill="{SEA}" stroke="{INK}" stroke-width="3"/>
<path d="M{aw / 2 - 26} 116q13-10 26 0t26 0" fill="none" stroke="{INK}" stroke-width="2.5"/>
{label(aw / 2, 262, "ICE WAS HERE. LEFT A RING.", size=11, fill=INK, anchor="middle")}"""
    card("cartography", title="Cartography: 3D table-top sea charts — Malma Kvarn and Fjäderholmarna. 1puni.com/#cartography",
         bg=DUST, fg=INK, top=("CARTOGRAPHY", "THE CARTOGRAPHER’S SHORE LEAVE"),
         headline=["The glacier left", "the bath running."],
         lede="3D table-top sea charts, built from open data.",
         link="1PUNI.COM/#CARTOGRAPHY", status="3D BROWSER EXHIBIT", art=pothole)

    beams = "".join(
        f'<path d="M150 118L{x2} {y2}L{x3} {y3}Z" fill="{DUST}" opacity="{o}"/>'
        for x2, y2, x3, y3, o in [(-20, 40, -20, 110, .5), (270, 20, 270, 95, .3), (270, 150, 270, 200, .16)])
    contours = "".join(f'<path d="M-10 {y}Q70 {y - 14} 132 {y + 2}T290 {y - 6}" fill="none" stroke="{SEA}" stroke-width="1.4" opacity=".55"/>'
                       for y in range(175, 272, 16))
    alcatraz = f"""
<rect width="{aw}" height="{ah}" fill="#0e1815" stroke="{SEA}" stroke-width="2"/>
<svg width="{aw}" height="{ah}">{contours}{beams}
<path d="M70 170Q96 146 128 150L142 138L160 140L176 152Q214 150 226 170Z" fill="{PAPER}" stroke="{INK}" stroke-width="2"/>
<path d="M146 140V112H154V140" fill="{PAPER}" stroke="{INK}" stroke-width="2"/><circle cx="150" cy="116" r="6" fill="{DUST}"/>
</svg>
{label(12, ah - 12, "macOS 14+ · APPLE SILICON + INTEL", size=10, fill=SEA, weight="550")}"""
    card("screensaver", title="OpenHelm Lighthouses: your Mac has gone sailing. Tynningö and Alcatraz chart screensavers. 1puni.com/#screensaver",
         bg=INK, fg=PAPER, top=("MAC SCREENSAVER", "OPENHELM LIGHTHOUSES · MIT"),
         headline=["Your Mac has", "gone sailing."],
         lede="Tynningö and Alcatraz lights on your idle Mac.",
         link="1PUNI.COM/#SCREENSAVER", status="PRE-RELEASE · NOT NOTARISED", art=alcatraz)

    receipt = f"""
<rect x="8" y="8" width="{aw - 16}" height="{ah - 16}" fill="{INK}"/>
<rect width="{aw - 16}" height="{ah - 16}" fill="{PAPER}" stroke="{INK}" stroke-width="2"/>
<text x="22" y="112" font-family="{MONO}" font-size="100" font-weight="900" letter-spacing="-10" fill="{INK}">↓≈</text>
<path d="M18 132H{aw - 34}" stroke="{INK}" stroke-dasharray="4 4"/>
{label(22, 160, "SOUNDING RECEIPT", size=13, fill=INK, weight="750", tracking=0)}
{mono(22, 186, "HASHED ··········· ✓", size=12, weight="normal", tracking=0)}
{mono(22, 206, "QUARANTINED ······ ✓", size=12, weight="normal", tracking=0)}
{mono(22, 226, "REVIEWED, THEN SHOWN", size=12, weight="normal", tracking=0)}"""
    card("bathy", title="Bathy: a Swedish commons for bathymetric source data. Depth data with a paper trail. bathy.1puni.com",
         bg=SEA, fg=INK, top=("BATHY / THE DEPTH COMMONS", "LEAVE MORE THAN A WAKE"),
         headline=["Below the boat.", "Above board."],
         lede="Depth data with a paper trail.",
         link="BATHY.1PUNI.COM", status="DEPTH COMMONS", art=receipt)

    rig = f"""
<svg width="{aw}" height="{ah}" viewBox="0 0 430 370"><g fill="none" stroke="{INK}">
<path d="M45 290Q220 350 395 281L350 333H110Z" stroke-width="4"/>
<path d="M161 291V41M277 291V76M70 285L161 41L365 285M105 285L277 76L390 285M92 136H223M212 160H338M116 85H201M240 112H313" stroke-width="2"/>
<path d="M40 350H396M40 342V358M396 342V358M27 41V331M19 41H35M19 331H35" stroke-dasharray="3 4"/></g>
<text x="95" y="220" fill="{INK}" font-size="65" font-family="{SERIF}" font-style="italic">India.</text></svg>"""
    card("crosstrees", title="Crosstrees and India: vessel knowledge, hull form and rigging in a modelling workbench. crosstrees.1puni.com",
         bg=PAPER, fg=INK, top=("CROSSTREES + INDIA", "OLD BOATS. NEW TOOLS."),
         headline=["A boat is", "a thousand", "arguments."],
         lede="Give them somewhere to line up.",
         link="CROSSTREES.1PUNI.COM", status="PRESENTATION OPEN · DESK BY INVITATION", art=rig)

    contract = f"""
<g transform="rotate(-3 {aw / 2} {ah / 2})">
<rect x="8" y="18" width="{aw - 16}" height="{ah - 36}" fill="{INK}"/>
<rect y="10" width="{aw - 16}" height="{ah - 36}" fill="{PAPER}" stroke="{INK}" stroke-width="2"/>
{label(18, 40, "EMPLOYMENT CONTRACT", size=12, fill=INK, weight="750", tracking=0)}
<text x="18" y="108" font-family="{MONO}" font-size="44" font-weight="bold" fill="{INK}">⟲ ━━┓</text>
{mono(18, 150, "Previous role:  holes.", size=13, weight="normal", tracking=0)}
{mono(18, 172, "Current role:   heading.", size=13, weight="normal", tracking=0)}
{mono(18, 194, "Marine cert.:   absolutely", size=13, weight="normal", tracking=0)}
{mono(18, 212, "                not.", size=13, weight="normal", tracking=0)}
</g>"""
    card("drill", title="Drill autopilot: our helmsman came from the power-tool aisle. 1puni.com/autopilot/",
         bg=RUST, fg=INK, top=("DRILL AUTOPILOT", "THE HARDWARE DEPARTMENT"),
         headline=["Our helmsman", "came from the", "power-tool aisle."],
         lede="A drill, recruited into steering duty.",
         link="1PUNI.COM/AUTOPILOT", status="EXPERIMENTAL · GPL-3.0+", art=contract)

    spread = ""
    panels = [(-16, -64, PAPER), (-3, -10, DUST), (10, 44, CHALK)]
    labels = ["ONE BEGINNING.", "STRANGER.", "TEN TURNS."]
    for i, (rot, ox, panel) in enumerate(panels):
        cx = aw / 2 + ox
        spread += (f'<g transform="rotate({rot} {cx:.0f} {ah + 70})">'
                   f'<rect x="{cx - 72:.0f}" y="40" width="146" height="200" fill="{panel}" stroke="{INK}" stroke-width="2"/>')
        if i == 0:
            spread += (f'<path d="M{cx:.0f} 200V110" stroke="{INK}" stroke-width="3"/><circle cx="{cx:.0f}" cy="100" r="8" fill="none" stroke="{INK}" stroke-width="3"/>')
        else:
            spread += f'<path d="M{cx:.0f} 210V170M{cx:.0f} 170L{cx - 34:.0f} 132M{cx:.0f} 170L{cx + 34:.0f} 132" fill="none" stroke="{INK}" stroke-width="3"/>'
        spread += "</g>"
    for (rot, ox, _), lab in zip(panels, labels):
        # Captions last and below the fanned pages: the spread overlaps;
        # the labels never do.
        cx = aw / 2 + ox
        spread += (f'<g transform="rotate({rot} {cx:.0f} {ah + 70})">'
                   + label(cx, 260, lab, size=10, fill=CHALK, anchor="middle") + "</g>")
    card("overprint", title="Overprint: comics none of us could make alone. Concept demo; the co-creation platform is looking for its first co-authors. overprint.1puni.com",
         bg=INK, fg=PAPER, top=("OVERPRINT", "AN IDEA IN THE MAKING"),
         headline=["One beginning.", "Ten wild turns."],
         lede="Comics none of us could make alone.",
         link="OVERPRINT.1PUNI.COM", status="CONCEPT DEMO · CO-AUTHORS WELCOME", art=spread)

    phone = f"""
<path d="M20 {ah}V92Q20 8 132 8Q244 8 244 92V{ah}Z" fill="{INK}"/>
<text x="132" y="112" font-family="'Apple Symbols','Segoe UI Symbol','DejaVu Sans',sans-serif" font-size="96" fill="{DUST}" text-anchor="middle">☎</text>
{label(132, 140, "GG SWITCHBOARD / YOUR CALL", size=9, fill=PAPER, weight="550", anchor="middle")}
<rect x="40" y="156" width="184" height="96" fill="{PAPER}"/>
{mono(52, 182, "So. You want", size=13, weight="normal", tracking=0)}
{mono(52, 202, "GuruGee in your", size=13, weight="normal", tracking=0)}
{mono(52, 222, "life? Interesting.", size=13, weight="normal", tracking=0)}
{mono(52, 242, "Come with me.", size=13, tracking=0)}"""
    card("gurugee", title="GuruGee: an anti-assistant for a brain with too many tabs open. You have ideas. GG has questions. 1puni.com/#switchboard",
         bg=DUST, fg=INK, top=("GURUGEE", "THE OTHER VOICE IN THE ROOM"),
         headline=["You have ideas.", "GG has", "questions."],
         lede="An anti-assistant for a brain with too many tabs open.",
         link="1PUNI.COM/#SWITCHBOARD", status="PRIVATE RESEARCH PREVIEW", art=phone)

    verdict = f"""
<rect x="16" y="16" width="{aw - 14}" height="{ah - 14}" fill="{DUST}"/>
<rect x="10" y="10" width="{aw - 14}" height="{ah - 14}" fill="{PAPER}" stroke="{INK}" stroke-width="2"/>
{label(16, 30, "YOUR UNSOLICITED VERDICT", size=11, fill=INK, weight="750")}
{text(14, 128, "HMM.", size=fit(["HMM."], lambda t, i: "georgia-bold", 94, -0.02, aw - 58), family=SERIF, weight="bold", tracking=-0.02, face="georgia-bold")}
{mono(16, 172, "Observed: you opened", size=12, weight="normal", tracking=0)}
{mono(16, 190, "a receipt.", size=12, weight="normal", tracking=0)}
{mono(16, 214, "Inferred: you are", size=12, weight="normal", tracking=0)}
{mono(16, 232, "curious.", size=12, weight="normal", tracking=0)}"""
    card("glance", title="GG Glance: a verdict desk for ideas and architectural messes. Paid inquiry. glance.1puni.com",
         bg=PAPER, fg=INK, top=("GG GLANCE", "THE SECOND OPINION DEPARTMENT"),
         headline=["Your project.", "Eyebrow raised."],
         lede="A verdict desk for ideas and architectural messes.",
         link="GLANCE.1PUNI.COM", status="PAID INQUIRY · US$5 IN BITCOIN", art=verdict)

    steps = ["INTENT", "WORK", "CHECK", "PROVE IT."]
    flow = ""
    for i, step in enumerate(steps):
        y = 8 + i * 68
        last = i == len(steps) - 1
        flow += (f'<rect x="{i * 14}" y="{y}" width="{aw - 42}" height="46" fill="{DUST if last else INK}" stroke="{DUST if last else PAPER}" stroke-width="1.5"/>'
                 + label(i * 14 + 16, y + 30, step, size=17, fill=INK if last else PAPER, weight="750"))
        if not last:
            flow += label(i * 14 + aw - 72, y + 64, "↓", size=17, fill=DUST, weight="750")
    card("steward", title="Steward Harness: \"I'll get back to it\" is not an operating system. Git-native AI work with checks and proof. github.com/1puni/steward",
         bg=INK, fg=PAPER, top=("STEWARD HARNESS", "SOMEBODY HAS TO FINISH THE JOB"),
         headline=["“I’ll get back to it”", "is not an", "operating system."],
         lede="For the executive function you forgot to hire.",
         link="GITHUB.COM/1PUNI/STEWARD", status="MIT · PRE-1.0", art=flow)

    chorus = f"""
<g transform="rotate(-3 {aw / 2} {ah / 2})">
<rect width="{aw}" height="{ah - 10}" fill="{INK}" stroke="{INK}" stroke-width="2"/>
{text(14, 86, "ALLA.", size=84, weight="800", fill=PAPER, tracking=-0.09, face="display")}
{text(34, 156, "ALLA.", size=84, weight="800", fill=DEEP, tracking=-0.09, face="display")}
{text(54, 226, "ALLA.", size=84, weight="800", fill=CHALK, tracking=-0.09, face="display")}
{label(16, 252, "TURN AN IDEA INTO SOMETHING YOU CAN FEEL.", size=8, fill=DUST, weight="550")}
</g>"""
    card("allmanningen", title="ALLMÄNNINGEN: an idea needs a body. Our contribution: visuals, voice, content. allmanningen.fyi",
         bg=DUST, fg=INK, top=("ALLMÄNNINGEN", "VISUALS · VOICE · CONTENT"),
         headline=["An idea needs", "a body."],
         lede="Pictures. A voice. A world to step into.",
         link="ALLMANNINGEN.FYI", status="AUDIOVISUAL CREDIT", art=chorus)


def stamps():
    for slug, name, stamp, line, tilt in [
        ("nsnodes", "nsnodes", "BORDERS: UNDER DISCUSSION", "A gathering point for network societies.", -2),
        ("llmpsych", "llmpsych", "HOW DID THAT CHAT FEEL?", "AI psychological safety.", 2),
    ]:
        w, h = 800, 220
        body = f"""
<rect width="{w}" height="{h}" fill="{PAPER}"/>
{label(36, 46, "COLLABORATION", size=13, fill=QUIET, weight="750")}
{label(w - 36, 46, "ASHORE ↗", size=13, fill=QUIET, anchor="end")}
<path d="M36 62H{w - 36}" stroke="{LINE}" stroke-width="1.5"/>
{text(36, 146, name, size=72, weight="800", tracking=-0.045, face="display")}
{text(36, 186, line, size=20, face="regular")}
<g transform="rotate({tilt} 600 130)"><rect x="470" y="96" width="290" height="66" fill="none" stroke="{RUST}" stroke-width="4"/>
<rect x="478" y="104" width="274" height="50" fill="none" stroke="{RUST}" stroke-width="1.5"/>
{label(615, 135, stamp, size=14, fill=RUST, weight="750", anchor="middle", tracking=0.05)}</g>
<rect x="2" y="2" width="{w - 4}" height="{h - 4}" fill="none" stroke="{INK}" stroke-width="2.5"/>
"""
        write(f"cards/{slug}.svg", svg(w, h, f"{name}: {line} Collaboration. {stamp}", body))


def strip(slug, lab, right, title):
    w, h = 1200, 64
    body = f"""
<rect width="{w}" height="{h}" fill="{NIGHT}"/>
{label(28, 39, lab, size=17, fill=DUST, weight="750")}
{label(w - 28, 39, right, size=13, fill=CHALK, anchor="end")}
"""
    write(f"{slug}.svg", svg(w, h, title, body))


def footer():
    w, h = 1200, 250
    logo, (lw, lh) = light_uri(BRAND / "logo-stacked.png", 230)
    logo_h = 150
    body = f"""
<rect width="{w}" height="{h}" fill="{NIGHT}"/>
<path d="M0 1H{w}" stroke="{DUST}" stroke-width="1" opacity=".5"/>
<image href="{logo}" x="40" y="46" width="{logo_h * lw / lh:.1f}" height="{logo_h}"/>
{text(320, 118, "The headcount is settled.", size=38, family=SERIF, style="italic", fill=PAPER, face="georgia-italic")}
{text(320, 164, "The scope is another matter.", size=38, family=SERIF, style="italic", fill=PAPER, face="georgia-italic")}
{label(322, 208, "BUILT BY COOKIE, WITH AI IN THE WORKSHOP · GURUGEE INBOX · PRIVACY · BOARD AT 1PUNI.COM ↗", size=11, fill=MOON, weight="550")}
"""
    write("footer.svg", svg(w, h, "1puni. The headcount is settled. The scope is another matter. Built by Cookie, "
                               "with AI in the workshop. Board at 1puni.com.", body))


def avatar():
    # Extend the crop's own paper before multiplying, so its edge disappears.
    # The night sky took the landing's footer and avatar with it: parchment now.
    art = Image.open(BRAND / "logo-emblem.png").convert("RGB")
    side = 440
    canvas = Image.new("RGB", (side, side), art.getpixel((2, art.height - 3)))
    canvas.paste(art, ((side - art.width) // 2, (side - art.height) // 2 + 6))
    canvas = ImageChops.multiply(canvas, Image.new("RGB", canvas.size, DUST))
    path = ROOT / "brand" / "avatar-yellow.png"
    canvas.save(path, optimize=True)
    print(f"{path.relative_to(ROOT)}  {side}x{side}")


if __name__ == "__main__":
    hero()
    cards()
    stamps()
    strip("strip-enterprise", "THE WHOLE UNREASONABLE ENTERPRISE ↓", "EVERY POSTER IS A DOOR",
          "The whole unreasonable enterprise. Every poster links to its project.")
    strip("strip-ashore", "OCCASIONALLY, WE GO ASHORE ↓", "OTHER GOOD TROUBLE", "Occasionally, we go ashore. Collaborations.")
    strip("strip-crew", "THE CREW ↓", "ORG CHART, SUCH AS IT IS", "The crew.")
    strip("strip-source", "SOURCE, AS IN ACTUAL SOURCE ↓", "READ IT · FORK IT · ARGUE WITH IT", "Public source repositories.")
    footer()
    avatar()
