#!/usr/bin/env python3
"""Build the 1puni org profile artwork from the approved logo crops.

Everything under profile/assets/ is generated; edit this file, not the SVGs.
Palette, type and copy follow https://1puni.com (landing docs/design.md).

Text widths are measured here and pinned with textLength, so a poster lays
out the same whether the viewer's machine has Arial, Helvetica or Liberation.
Motion is finite and stops. The resting frame is the punchline, so a renderer
that skips animation (or honours prefers-reduced-motion) still tells the joke.

Requires Pillow and the macOS system Arial/Georgia/Menlo fonts.
"""

import base64
import io
from pathlib import Path

from PIL import Image, ImageChops, ImageFont

ROOT = Path(__file__).resolve().parent.parent
BRAND = ROOT / "brand"
OUT = ROOT / "profile" / "assets"

INK, YELLOW, BLUE, PAPER, ORANGE = "#171918", "#eaff00", "#83bbc7", "#f8f8ed", "#ff653b"
SANS = "Arial, 'Helvetica Neue', Helvetica, 'Liberation Sans', sans-serif"
SERIF = "Georgia, 'Times New Roman', serif"
MONO = "ui-monospace, SFMono-Regular, Menlo, Consolas, 'Liberation Mono', monospace"

FONTS = Path("/System/Library/Fonts/Supplemental")
FACES = {
    "bold": FONTS / "Arial Bold.ttf",
    "italic": FONTS / "Arial Italic.ttf",
    "regular": FONTS / "Arial.ttf",
    "georgia-italic": FONTS / "Georgia Italic.ttf",
    "georgia-bold": FONTS / "Georgia Bold.ttf",
}


def width(text, face, size, tracking=0.0):
    """Rendered advance of text in px, including CSS-style letter-spacing (em)."""
    font = ImageFont.truetype(str(FACES[face]), 400)
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


def mono(x, y, body, *, size=13, fill=INK, weight="bold", anchor="start", tracking=0.06):
    return text(x, y, body, size=size, family=MONO, weight=weight, fill=fill, anchor=anchor, tracking=tracking)


def on_paper(path, paper=YELLOW):
    """The site's CSS multiply, baked: paper takes the field colour, ink stays ink."""
    art = Image.open(path).convert("RGB")
    return ImageChops.multiply(art, Image.new("RGB", art.size, paper))


def data_uri(image, target_width):
    scaled = image.resize((target_width, round(image.height * target_width / image.width)), Image.LANCZOS)
    buf = io.BytesIO()
    scaled.save(buf, "PNG", optimize=True)
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode(), scaled.size


def svg(w, h, title, body, style=""):
    css = f"<style>{style}</style>" if style else ""
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}"'
            f' role="img" aria-labelledby="t"><title id="t">{esc(title)}</title>{css}{body}</svg>\n')


def write(name, content):
    path = OUT / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)
    print(f"{path.relative_to(ROOT)}  {len(content.encode()) / 1024:.1f} kB")


# --- Nike, redrawn from the homepage's original inline illustration (bow to the right).
NIKE = f"""
<defs><pattern id="bow-net" width="13" height="13" patternUnits="userSpaceOnUse"><path d="M0 0L13 13M13 0L0 13" fill="none" stroke="#eee2c3" stroke-width="1.3"/></pattern></defs>
<g fill="none" stroke="{INK}" stroke-width="2"><path d="M172 376L303 157L540 377M320 377L555 30L944 345M555 30L792 373M303 157L209 379"/></g>
<g stroke="{INK}" stroke-width="4" stroke-linejoin="round">
<path d="M552 78L462 130L548 255Z" fill="#913b2b"/><path d="M548 266L438 143L353 346Q436 358 548 346Z" fill="#a64730"/>
<path d="M568 106Q688 223 906 332Q790 284 660 322Z" fill="#783127"/><path d="M578 233L589 349L736 346Z" fill="#9e432f"/>
<path d="M295 185L221 235L291 297Z" fill="#913b2b"/><path d="M291 304L215 239L161 354L292 357Z" fill="#a64730"/></g>
<g fill="none" stroke="#6b2924" stroke-width="2"><path d="M424 184L382 345M459 221L407 350M490 252L449 350M372 302L548 312M208 274L182 353M245 295L223 356M680 257L829 284"/></g>
<path d="M303 158V381M555 30V378" fill="none" stroke="{INK}" stroke-width="7"/><path d="M555 31L596 43L555 47Z" fill="#913b2b"/>
<path d="M349 351H551M158 359L294 362" stroke="#aa8050" stroke-width="6"/>
<path d="M176 379L181 362H256L264 380M353 378L365 359H450L465 379M647 374L659 359H714L730 373" fill="#eee2c3" stroke="{INK}" stroke-width="3"/>
<path d="M374 367H391M405 367H424" stroke="{INK}" stroke-width="7"/>
<path d="M739 370L951 340" stroke="{INK}" stroke-width="10"/><path d="M739 368L951 338" stroke="#c59760" stroke-width="6"/>
<path d="M797 363L950 342Q887 414 800 404Z" fill="url(#bow-net)" stroke="{INK}" stroke-width="2"/>
<path d="M149 374Q438 403 802 362L795 432Q445 465 169 433Q147 416 149 374Z" fill="#542b36" stroke="{INK}" stroke-width="5"/>
<path d="M153 387Q436 419 800 377" fill="none" stroke="#eee2c3" stroke-width="7"/>
<path d="M166 427Q439 455 795 425L795 432Q444 468 169 433Z" fill="{INK}"/>
<g fill="none" stroke="{INK}" stroke-width="2"><path d="M156 374V350M217 380V356M276 383V359M626 381V357M694 376V352M760 368V344M156 351Q434 388 760 344"/></g>
<path d="M191 376V333M163 336H216V322H163ZM176 336V357H191V336" fill="{YELLOW}" stroke="{INK}" stroke-width="4"/>
<text x="657" y="414" fill="#eee2c3" font-family="{MONO}" font-size="21" transform="rotate(-4 657 414)">NIKE</text>
"""

# The hand-drawn "ish" annotation from the homepage headline (viewBox 0 0 100 70).
ISH = ('<g fill="none" stroke="currentColor" stroke-width="4" stroke-linecap="round" stroke-linejoin="round">'
       '<path d="M12 32l-4 24m8-39l1-2M45 31c-21-9-30 12-10 13s-2 23-15 12M61 9L49 56m6-17c22-24 26-10 17 15M10 65q30-7 68-3"/></g>')


def waves(y, period, amp, x0=-140, x1=1400):
    d = f"M{x0} {y}"
    x = x0
    while x < x1:
        d += f" q{period / 4} {-amp} {period / 2} 0 t{period / 2} 0"
        x += period
    return d


def hero():
    W, H, M = 1200, 760, 44
    logo, (lw, lh) = data_uri(on_paper(BRAND / "logo-horizontal.png"), 420)
    logo_h = 66
    logo_w = logo_h * lw / lh

    big = "BIG IDEAS."
    big_size, big_track = 172, -0.085
    small_size, small_track = round(big_size * 0.92), -0.075
    base1, base2 = 262, 262 + round(big_size * 0.84)
    small_w = width("SMALL", "italic", small_size, small_track)
    ish_w = small_size * 0.65
    ish_x = M + small_w + 6
    boat_x = ish_x + ish_w + 14

    band = 452
    sign_x, sign_y, sign_w, sign_h = 842, 488, 312, 168
    final = "translate(0px,132px) rotate(-8deg)"
    style = f"""
.sign{{transform-box:fill-box;transform-origin:50% 0;transform:{final};animation:reveal 4.6s cubic-bezier(.45,0,.25,1) 1.2s 1 both}}
@keyframes reveal{{0%{{transform:rotate(4deg)}}16%{{transform:rotate(-4deg)}}30%{{transform:rotate(5deg)}}44%{{transform:rotate(-2deg)}}56%{{transform:rotate(3deg)}}100%{{transform:{final}}}}}
.nike{{transform-origin:640px 700px;animation:bob 3.4s ease-in-out 3}}
@keyframes bob{{0%,100%{{transform:translate(0,0) rotate(0)}}25%{{transform:translate(0,-4px) rotate(-.8deg)}}75%{{transform:translate(0,3px) rotate(.7deg)}}}}
.swell{{animation:drift 3.4s linear 3}}.swell2{{animation:drift 2.6s linear 4 reverse}}
@keyframes drift{{to{{transform:translateX(-120px)}}}}
@media (prefers-reduced-motion:reduce){{.sign{{animation:none;transform:{final}}}.nike,.swell,.swell2{{animation:none}}}}
"""
    body = f"""
<rect width="{W}" height="{H}" fill="{YELLOW}"/>
<image href="{logo}" x="{M}" y="16" width="{logo_w:.1f}" height="{logo_h}"/>
{mono(M + logo_w + 24, 44, "ONE PERSON UNICORN", size=13, weight="normal")}
{mono(M + logo_w + 24, 62, "EST. SOMEWHERE OFFSHORE", size=13, weight="normal")}
{mono(W - M, 53, "COOKIE’S DEEPLY UNREASONABLE COMPANY", size=13, anchor="end")}
<path d="M0 97H{W}" stroke="{INK}" stroke-width="2"/>
{text(M - 6, base1, big, size=big_size, weight="900", tracking=big_track, face="bold")}
{text(M - 4, base2, "SMALL", size=small_size, weight="500", style="italic", tracking=small_track, face="italic")}
<g color="{INK}" transform="translate({ish_x:.1f} {base2 - small_size * 0.3 - small_size * 0.5:.1f}) rotate(-12 {ish_w / 2:.1f} 40) scale({ish_w / 100:.3f})">{ISH}</g>
{text(boat_x, base2, "BOAT.", size=small_size, weight="500", style="italic", tracking=small_track, face="italic")}
<rect y="{band}" width="{W}" height="{H - band}" fill="{BLUE}"/>
<path d="M0 {band}H{W}" stroke="{INK}" stroke-width="2"/>
<g transform="translate({sign_x} {sign_y})">
  {text(8, 44, "IT’S A BOAT.", size=34, weight="900", tracking=-0.02, face="bold")}
  {text(8, 76, "Of course it’s a fucking boat.", size=22, family=SERIF, style="italic", face="georgia-italic")}
</g>
<g class="nike"><g transform="translate(200 470) scale(.62)">{NIKE}</g></g>
<path class="swell" d="{waves(740, 120, 12)}" fill="none" stroke="{INK}" stroke-width="3"/>
<path class="swell2" d="{waves(752, 120, 8, -20, 1500)}" fill="none" stroke="{INK}" stroke-width="2" opacity=".45"/>
{mono(M, 655, "THE AUTOPILOT", size=12)}
{mono(M, 672, "IS A DRILL. →", size=12)}
{mono(M, 700, "ILLUSTRATION / NOT A VESSEL SURVEY", size=9, weight="normal")}
<g class="sign">
  <rect x="{sign_x + 9}" y="{sign_y + 9}" width="{sign_w}" height="{sign_h}" fill="{INK}"/>
  <rect x="{sign_x}" y="{sign_y}" width="{sign_w}" height="{sign_h}" fill="{PAPER}" stroke="{INK}" stroke-width="3"/>
  {mono(sign_x + 18, sign_y + 28, "1PUNI GLOBAL HEADQUARTERS", size=11, weight="normal", tracking=0.12)}
  {text(sign_x + 16, sign_y + 78, "VERY SERIOUS", size=40, weight="900", tracking=-0.05, face="bold")}
  {text(sign_x + 16, sign_y + 118, "BUSINESS.", size=40, weight="900", tracking=-0.05, face="bold")}
  <rect x="{sign_x + 16}" y="{sign_y + 132}" width="{sign_w - 32}" height="22" fill="{YELLOW}" stroke="{INK}"/>
  {mono(sign_x + sign_w / 2, sign_y + 147, "INSPECT THE FOUNDATIONS ↗", size=10, anchor="middle")}
</g>
"""
    write("hero.svg", svg(W, H, "1puni. Big ideas. Small-ish boat. Nike, a hundred-year-old two-masted boat with "
                             "rust-red sails and a drill at the helm, under a corporate sign reading 1puni global "
                             "headquarters, very serious business. It swings loose: it's a boat. Of course it's a "
                             "fucking boat.", body, style))


# --- Project posters -------------------------------------------------------------------

CW, CH = 800, 460
ART = (500, 88, 264, 272)  # x, y, w, h


def card(slug, *, title, bg, fg, top, headline, lede, link, status, art, accent=YELLOW, bar=INK, bar_fg=None):
    """A poster: section rule, headline with a Georgia-italic last line, art, link bar."""
    bar_fg = bar_fg or accent
    lines = headline
    face_of = lambda t, i: "georgia-italic" if i == len(lines) - 1 else "bold"
    size = fit(lines, face_of, 58, -0.05, 440)
    y0 = 128 + (3 - len(lines)) * size * 0.5
    heads = []
    for i, line in enumerate(lines):
        y = y0 + i * size * 1.02
        if i == len(lines) - 1:
            heads.append(text(36, round(y), line, size=size + 2, family=SERIF, style="italic", fill=fg,
                              tracking=-0.04, face="georgia-italic"))
        else:
            heads.append(text(36, round(y), line, size=size, weight="900", fill=fg, tracking=-0.05, face="bold"))
    lede_size = fit([lede], lambda t, i: "regular", 21, 0, 440)
    body = f"""
<rect width="{CW}" height="{CH}" fill="{bg}"/>
{mono(36, 46, top[0], size=14, fill=fg)}
{mono(CW - 36, 46, top[1], size=14, fill=fg, anchor="end", weight="normal")}
<path d="M36 62H{CW - 36}" stroke="{fg}" stroke-width="1.5"/>
{''.join(heads)}
{text(36, 340, lede, size=lede_size, fill=fg, face="regular")}
<g transform="translate({ART[0]} {ART[1]})">{art}</g>
<rect y="{CH - 80}" width="{CW}" height="80" fill="{bar}"/>
{mono(36, CH - 33, link + " ↗", size=19, fill=bar_fg)}
{mono(CW - 36, CH - 34, status, size=12, fill=PAPER if bar == INK else INK, anchor="end", weight="normal", tracking=0.1)}
<rect x="2" y="2" width="{CW - 4}" height="{CH - 4}" fill="none" stroke="{INK}" stroke-width="4"/>
"""
    write(f"cards/{slug}.svg", svg(CW, CH, title, body))


def grid(w, h, step=24, color="#17191822"):
    lines = "".join(f"M{x} 0V{h}" for x in range(step, w, step)) + "".join(f"M0 {y}H{w}" for y in range(step, h, step))
    return f'<path d="{lines}" stroke="{color}" stroke-width="1"/>'


def cards():
    aw, ah = ART[2], ART[3]

    chart = f"""
<g transform="rotate(3 {aw / 2} {ah / 2})">
<rect x="10" y="10" width="{aw}" height="{ah - 18}" fill="{YELLOW}"/>
<rect width="{aw}" height="{ah - 18}" fill="{BLUE}" stroke="{INK}" stroke-width="2"/>{grid(aw, ah - 18)}
<svg width="{aw}" height="{ah - 18}" viewBox="0 0 420 350" preserveAspectRatio="xMidYMid slice">
<path d="M240-10Q160 40 215 92T198 196T251 354H440V0" fill="{YELLOW}" stroke="{INK}" stroke-width="3"/>
<path d="M279-10Q204 51 251 99T238 203T295 370M306-10Q235 51 280 103T270 207T330 370" fill="none" stroke="{INK}"/>
<path d="M85 319Q25 201 103 181T136 80L103 44" fill="none" stroke="{INK}" stroke-width="3" stroke-dasharray="8 7"/>
<path d="M92 52L101 29L116 50Z" fill="{ORANGE}" stroke="{INK}" stroke-width="2"/>
<circle cx="110" cy="285" r="26" fill="none" stroke="{INK}"/><path d="M110 250V320M75 285H145" stroke="{INK}"/>
<text x="276" y="178" font-family="{MONO}" font-size="19" font-weight="bold" fill="{INK}">LAND.</text>
<text x="267" y="202" font-family="{MONO}" font-size="14" fill="{INK}">AVOID IT.</text></svg>
</g>"""
    card("openhelm", title="OpenHelm: navigation software for the boat you're actually on. 1puni.com/#openhelm",
         bg=PAPER, fg=INK, top=("01 / OPENHELM", "BUILT FROM THE COCKPIT"),
         headline=["The sea doesn’t", "give a shit about", "your roadmap."],
         lede="Navigation software for the boat you’re actually on.",
         link="1PUNI.COM/#OPENHELM", status="IN DEVELOPMENT", art=chart)

    pothole = f"""
<circle cx="{aw / 2}" cy="120" r="112" fill="none" stroke="{INK}" stroke-width="3"/>
<circle cx="{aw / 2}" cy="120" r="78" fill="none" stroke="{INK}" stroke-width="1.5" stroke-dasharray="3 6"/>
<circle cx="{aw / 2}" cy="120" r="44" fill="{BLUE}" stroke="{INK}" stroke-width="3"/>
<path d="M{aw / 2 - 26} 116q13-10 26 0t26 0" fill="none" stroke="{INK}" stroke-width="2.5"/>
{mono(aw / 2, 262, "ICE WAS HERE. LEFT A RING.", size=12, anchor="middle")}"""
    card("cartography", title="Cartography: explore Malmaön's Korshamn reserve and its glacial potholes. 1puni.com/cartography/",
         bg=YELLOW, fg=INK, top=("CARTOGRAPHY", "THE CARTOGRAPHER’S SHORE LEAVE"),
         headline=["The glacier left", "the bath running."],
         lede="Real map geometry, woodland paths and glacial potholes.",
         link="1PUNI.COM/CARTOGRAPHY", status="BROWSER EXHIBIT", art=pothole, bar_fg=YELLOW)

    beams = "".join(
        f'<path d="M150 118L{x2} {y2}L{x3} {y3}Z" fill="{YELLOW}" opacity="{o}"/>'
        for x2, y2, x3, y3, o in [(-20, 40, -20, 110, .55), (270, 20, 270, 95, .35), (270, 150, 270, 200, .18)])
    contours = "".join(f'<path d="M-10 {y}Q70 {y - 14} 132 {y + 2}T290 {y - 6}" fill="none" stroke="{BLUE}" stroke-width="1.4" opacity=".55"/>'
                       for y in range(175, 272, 16))
    alcatraz = f"""
<rect width="{aw}" height="{ah}" fill="#0f2330" stroke="{BLUE}" stroke-width="2"/>
<svg width="{aw}" height="{ah}">{contours}{beams}
<path d="M70 170Q96 146 128 150L142 138L160 140L176 152Q214 150 226 170Z" fill="{PAPER}" stroke="{INK}" stroke-width="2"/>
<path d="M146 140V112H154V140" fill="{PAPER}" stroke="{INK}" stroke-width="2"/><circle cx="150" cy="116" r="6" fill="{YELLOW}"/>
</svg>
{mono(12, ah - 12, "macOS 14+ · APPLE SILICON", size=11, fill=BLUE, weight="normal")}"""
    card("screensaver", title="Your Mac has gone sailing: a native macOS chart screensaver of Alcatraz and San Francisco Bay. 1puni.com/#screensaver",
         bg=INK, fg=PAPER, top=("MAC SCREENSAVER", "NATIVE macOS · MIT"),
         headline=["Your Mac has", "gone sailing."],
         lede="Shore leave around Alcatraz, drawn from NOAA charts.",
         link="1PUNI.COM/#SCREENSAVER", status="PREVIEW · NOT NOTARIZED", art=alcatraz, bar=YELLOW, bar_fg=INK)

    receipt = f"""
<rect x="8" y="8" width="{aw - 16}" height="{ah - 16}" fill="{INK}"/>
<rect width="{aw - 16}" height="{ah - 16}" fill="{PAPER}" stroke="{INK}" stroke-width="2"/>
<text x="22" y="112" font-family="{MONO}" font-size="100" font-weight="900" letter-spacing="-10" fill="{INK}">↓≈</text>
<path d="M18 132H{aw - 34}" stroke="{INK}" stroke-dasharray="4 4"/>
{mono(22, 160, "SOUNDING RECEIPT", size=13)}
{mono(22, 186, "HASHED ··········· ✓", size=12, weight="normal", tracking=0)}
{mono(22, 206, "QUARANTINED ······ ✓", size=12, weight="normal", tracking=0)}
{mono(22, 226, "REVIEWED, THEN SHOWN", size=12, weight="normal", tracking=0)}"""
    card("bathy", title="Bathy: a Swedish commons for bathymetric source data. Depth data with a paper trail. bathy.1puni.com",
         bg=BLUE, fg=INK, top=("BATHY / THE DEPTH COMMONS", "LEAVE MORE THAN A WAKE"),
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
         link="CROSSTREES.1PUNI.COM", status="PUBLIC PRESENTATION", art=rig)

    contract = f"""
<g transform="rotate(-3 {aw / 2} {ah / 2})">
<rect x="8" y="18" width="{aw - 16}" height="{ah - 36}" fill="{INK}"/>
<rect y="10" width="{aw - 16}" height="{ah - 36}" fill="{PAPER}" stroke="{INK}" stroke-width="2"/>
{mono(18, 40, "EMPLOYMENT CONTRACT", size=12)}
<text x="18" y="108" font-family="{MONO}" font-size="44" font-weight="bold" fill="{INK}">⟲ ━━┓</text>
{mono(18, 150, "Previous role:  holes.", size=13, weight="normal", tracking=0)}
{mono(18, 172, "Current role:   heading.", size=13, weight="normal", tracking=0)}
{mono(18, 194, "Marine cert.:   absolutely", size=13, weight="normal", tracking=0)}
{mono(18, 212, "                not.", size=13, weight="normal", tracking=0)}
</g>"""
    card("drill", title="Drill autopilot: our helmsman came from the power-tool aisle. 1puni.com/autopilot/",
         bg=ORANGE, fg=INK, top=("DRILL AUTOPILOT", "THE HARDWARE DEPARTMENT"),
         headline=["Our helmsman", "came from the", "power-tool aisle."],
         lede="A drill, recruited into steering duty.",
         link="1PUNI.COM/AUTOPILOT", status="EXPERIMENTAL · GPL-3.0+", art=contract)

    phone = f"""
<path d="M20 {ah}V92Q20 8 132 8Q244 8 244 92V{ah}Z" fill="{INK}"/>
<text x="132" y="112" font-family="'Apple Symbols','Segoe UI Symbol','DejaVu Sans',sans-serif" font-size="96" fill="{YELLOW}" text-anchor="middle">☎</text>
{mono(132, 140, "GG SWITCHBOARD / YOUR CALL", size=9, fill=PAPER, weight="normal", anchor="middle")}
<rect x="40" y="156" width="184" height="96" fill="{PAPER}"/>
{mono(52, 182, "So. You want", size=13, weight="normal", tracking=0)}
{mono(52, 202, "GuruGee in your", size=13, weight="normal", tracking=0)}
{mono(52, 222, "life? Interesting.", size=13, weight="normal", tracking=0)}
{mono(52, 242, "Come with me.", size=13, tracking=0)}"""
    card("gurugee", title="GuruGee: an anti-assistant for a brain with too many tabs open. You have ideas. GG has questions. 1puni.com/#switchboard",
         bg=YELLOW, fg=INK, top=("GURUGEE", "THE OTHER VOICE IN THE ROOM"),
         headline=["You have ideas.", "GG has", "questions."],
         lede="An anti-assistant for a brain with too many tabs open.",
         link="1PUNI.COM/#SWITCHBOARD", status="RESEARCH PREVIEW", art=phone, bar_fg=YELLOW)

    verdict = f"""
<rect x="10" y="10" width="{aw - 14}" height="{ah - 14}" fill="{INK}"/>
<rect width="{aw - 14}" height="{ah - 14}" fill="{YELLOW}" stroke="{INK}" stroke-width="2"/>
{mono(16, 30, "YOUR UNSOLICITED VERDICT", size=11)}
{text(14, 128, "HMM.", size=fit(["HMM."], lambda t, i: "georgia-bold", 94, -0.02, aw - 44), family=SERIF, weight="bold", tracking=-0.02, face="georgia-bold")}
{mono(16, 172, "Observed: you opened", size=12, weight="normal", tracking=0)}
{mono(16, 190, "a receipt.", size=12, weight="normal", tracking=0)}
{mono(16, 214, "Inferred: you are", size=12, weight="normal", tracking=0)}
{mono(16, 232, "curious.", size=12, weight="normal", tracking=0)}"""
    card("glance", title="GG Glance: a proposed verdict desk for ideas and architectural messes. Test build. 1puni.com/glance/",
         bg=PAPER, fg=INK, top=("GG GLANCE", "THE SECOND OPINION DEPARTMENT"),
         headline=["Your project.", "Eyebrow raised."],
         lede="A verdict desk for ideas and architectural messes.",
         link="1PUNI.COM/GLANCE", status="TEST BUILD · NOT TAKING PAYMENT", art=verdict)

    steps = ["INTENT", "WORK", "CHECK", "PROVE IT."]
    flow = ""
    for i, step in enumerate(steps):
        y = 8 + i * 68
        last = i == len(steps) - 1
        flow += (f'<rect x="{i * 14}" y="{y}" width="{aw - 42}" height="46" fill="{YELLOW if last else INK}" stroke="{YELLOW if last else PAPER}" stroke-width="1.5"/>'
                 + mono(i * 14 + 16, y + 30, step, size=18, fill=INK if last else PAPER))
        if not last:
            flow += mono(i * 14 + aw - 72, y + 64, "↓", size=18, fill=YELLOW)
    card("steward", title="Steward Harness: \"I'll get back to it\" is not an operating system. Git-native AI work with checks and proof. github.com/1puni/steward",
         bg=INK, fg=PAPER, top=("STEWARD HARNESS", "SOMEBODY HAS TO FINISH THE JOB"),
         headline=["“I’ll get back to it”", "is not an", "operating system."],
         lede="For the executive function you forgot to hire.",
         link="GITHUB.COM/1PUNI/STEWARD", status="MIT · PRE-1.0", art=flow, bar=YELLOW, bar_fg=INK)

    chorus = f"""
<g transform="rotate(-3 {aw / 2} {ah / 2})">
<rect width="{aw}" height="{ah - 10}" fill="{INK}" stroke="{INK}" stroke-width="2"/>
{text(14, 86, "ALLA.", size=84, weight="900", fill=YELLOW, tracking=-0.09, face="bold")}
{text(34, 156, "ALLA.", size=84, weight="900", fill=BLUE, tracking=-0.09, face="bold")}
{text(54, 226, "ALLA.", size=84, weight="900", fill=PAPER, tracking=-0.09, face="bold")}
{mono(16, 252, "TURN AN IDEA INTO SOMETHING YOU CAN FEEL.", size=8, fill=YELLOW, weight="normal")}
</g>"""
    card("allmanningen", title="ALLMÄNNINGEN: an idea needs a body. Our contribution: visuals, voice, content. allmanningen.fyi",
         bg=YELLOW, fg=INK, top=("ALLMÄNNINGEN", "VISUALS · VOICE · CONTENT"),
         headline=["An idea needs", "a body."],
         lede="Pictures. A voice. A world to step into.",
         link="ALLMANNINGEN.FYI", status="AUDIOVISUAL CREDIT", art=chorus, bar_fg=YELLOW)


def stamps():
    for slug, name, stamp, line, tilt in [
        ("nsnodes", "nsnodes", "BORDERS: UNDER DISCUSSION", "A gathering point for network societies.", -2),
        ("llmpsych", "llmpsych", "HOW DID THAT CHAT FEEL?", "AI psychological safety.", 2),
    ]:
        w, h = 800, 220
        body = f"""
<rect width="{w}" height="{h}" fill="{PAPER}"/>
{mono(36, 46, "COLLABORATION", size=14)}
{mono(w - 36, 46, "ASHORE ↗", size=14, anchor="end", weight="normal")}
<path d="M36 62H{w - 36}" stroke="{INK}" stroke-width="1.5"/>
{text(36, 146, name, size=72, weight="900", tracking=-0.05, face="bold")}
{text(36, 186, line, size=20, face="regular")}
<g transform="rotate({tilt} 600 130)"><rect x="470" y="96" width="290" height="66" fill="none" stroke="{ORANGE}" stroke-width="4"/>
<rect x="478" y="104" width="274" height="50" fill="none" stroke="{ORANGE}" stroke-width="1.5"/>
{mono(615, 135, stamp, size=15, fill=ORANGE, anchor="middle")}</g>
<rect x="2" y="2" width="{w - 4}" height="{h - 4}" fill="none" stroke="{INK}" stroke-width="4"/>
"""
        write(f"cards/{slug}.svg", svg(w, h, f"{name}: {line} Collaboration. {stamp}", body))


def strip(slug, label, right, title):
    w, h = 1200, 64
    body = f"""
<rect width="{w}" height="{h}" fill="{INK}"/>
{mono(28, 39, label, size=18, fill=YELLOW)}
{mono(w - 28, 39, right, size=14, fill=PAPER, anchor="end", weight="normal")}
"""
    write(f"{slug}.svg", svg(w, h, title, body))


def footer():
    w, h = 1200, 250
    logo, (lw, lh) = data_uri(on_paper(BRAND / "logo-stacked.png"), 230)
    logo_h = 190
    body = f"""
<rect width="{w}" height="{h}" fill="{YELLOW}"/>
<path d="M0 1H{w}" stroke="{INK}" stroke-width="2"/>
<image href="{logo}" x="40" y="30" width="{logo_h * lw / lh:.1f}" height="{logo_h}"/>
{text(230, 112, "One person. A boat.", size=44, weight="900", tracking=-0.05, face="bold")}
{text(230, 160, "A deeply unreasonable to-do list.", size=40, family=SERIF, style="italic", tracking=-0.03, face="georgia-italic")}
{mono(232, 204, "BUILT BY COOKIE, WITH AI IN THE WORKSHOP · NO TRACKERS · BOARD AT 1PUNI.COM ↗", size=12, weight="normal")}
"""
    write("footer.svg", svg(w, h, "1puni. One person. A boat. A deeply unreasonable to-do list. Built by Cookie, "
                               "with AI in the workshop. Board at 1puni.com.", body))


def avatar():
    # Extend the crop's own paper before multiplying, so its edge disappears.
    art = Image.open(BRAND / "logo-emblem.png").convert("RGB")
    side = 440
    canvas = Image.new("RGB", (side, side), art.getpixel((2, art.height - 3)))
    canvas.paste(art, ((side - art.width) // 2, (side - art.height) // 2 + 6))
    canvas = ImageChops.multiply(canvas, Image.new("RGB", canvas.size, YELLOW))
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
