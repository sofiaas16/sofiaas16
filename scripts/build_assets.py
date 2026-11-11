#!/usr/bin/env python3
"""
Pastel Tech — asset generator for Sara Zambrano's GitHub profile.

Every SVG in /assets is produced by this script, in a light and a dark
variant, from the single palette below. To change a colour, a phrase or a
project, edit this file and run:

    python3 scripts/build_assets.py

No dependencies beyond the Python standard library.
"""
from __future__ import annotations

import base64
import os
from html import escape
from pathlib import Path

from sprite import SPRITE_CSS, SPRITE_CSS_REDUCED, sprite, heart, box

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets"

# ─────────────────────────────────────────────────────────────── palette ──
# Pastel families. base = the pastel itself, T = accessible text/icon tone,
# tile = soft surface, chip = even softer surface.
FAMILIES = {
    #          base       light T    light tile light chip  dark T     dark tile  dark chip
    "pink":   ("#F8BBD0", "#B83E76", "#FFEAF1", "#FFF2F7", "#F8BBD0", "#2E2236", "#2A2134"),
    "blue":   ("#BDE0FE", "#2C64A8", "#E8F3FF", "#EEF6FF", "#A9D3FF", "#1E2C44", "#1D2A41"),
    "lav":    ("#CDB4DB", "#74519B", "#F3EAF8", "#F6F0FA", "#D7C2E6", "#29243F", "#27223B"),
    "lilac":  ("#D8B4F8", "#8447C2", "#F5ECFE", "#F9F3FF", "#DDBEFA", "#2B2343", "#29213F"),
    "mint":   ("#B8E4D0", "#2E7A5C", "#E6F6EE", "#EEF9F4", "#B8E4D0", "#1C3233", "#1B2F31"),
    "butter": ("#F9E6A0", "#85640A", "#FDF4D6", "#FEF8E6", "#F9E6A0", "#302D25", "#2D2A24"),
    "peach":  ("#FFD6BA", "#A8502A", "#FFEFE4", "#FFF5EE", "#FFD6BA", "#33282B", "#302629"),
}


def fam(theme, name):
    b, lt, ltile, lchip, dt, dtile, dchip = FAMILIES[name]
    if theme == "light":
        return dict(base=b, T=lt, tile=ltile, chip=lchip)
    return dict(base=b, T=dt, tile=dtile, chip=dchip)


THEMES = {
    "light": dict(
        page="#FFFFFF", bg="#FFFBFD", card="#FFFFFF", border="#ECE3EE",
        text="#293247", muted="#59617A", faint="#8A90A6",
        pink="#F8BBD0", blue="#BDE0FE", lav="#CDB4DB", blush="#FFE5EC", sky="#A2D2FF",
        pinkT="#B83E76", blueT="#2C64A8", lavT="#74519B",            # accessible accent text
        grad=("#8447C2", "#7457B8", "#2E7A5C"),                       # name gradient (lilac → mint)
        heroA="#FFF3E8", heroB="#FFFDF8", heroC="#EAF7F0", dot="#E7DDEC",
        tileP="#FFEAF1", tileB="#E9F4FF", tileL="#F3EAF8",
        chip="#FFF1F6", chipB="#EDF6FF", chipL="#F5EEFA",
        term="#FFFDFE", termbar="#F8F2F8",
        desk_top="#E9DCEF", desk="#F5EEF8", lap="#F4F6FB", lap_edge="#B7C0D4", lap_shine="#FFFFFF", steam="#CDB4DB",
        board="#EEF6FF", board2="#E3EFFC",
    ),
    "dark": dict(
        page="#0D1117", bg="#161B2B", card="#1A2033", border="#2D3551",
        text="#F4F1F8", muted="#BAC0D6", faint="#8992AE",
        pink="#F8BBD0", blue="#BDE0FE", lav="#CDB4DB", blush="#2B2236", sky="#A2D2FF",
        pinkT="#F8BBD0", blueT="#A9D3FF", lavT="#D7C2E6",
        grad=("#F8BBD0", "#CDB4DB", "#A2D2FF"),
        heroA="#221C30", heroB="#171C2C", heroC="#16223A", dot="#2A3150",
        tileP="#2E2236", tileB="#1E2C44", tileL="#29243F",
        chip="#2A2236", chipB="#1E2B42", chipL="#272340",
        term="#131828", termbar="#1D2338",
        desk_top="#4A3A55", desk="#2B2236", lap="#DDE3F0", lap_edge="#8E99B3", lap_shine="#F4F6FB", steam="#8E7BA6",
        board="#1C2640", board2="#202B47",
    ),
}

SANS = "'Segoe UI', -apple-system, BlinkMacSystemFont, 'Helvetica Neue', Helvetica, Arial, sans-serif"
MONO = "ui-monospace, SFMono-Regular, 'SF Mono', Menlo, Consolas, 'Liberation Mono', 'DejaVu Sans Mono', monospace"

REDUCED = "@media (prefers-reduced-motion: reduce){*{animation:none!important;transition:none!important}%s}"

BASE_CSS = f"""
.sans{{font-family:{SANS}}}
.mono{{font-family:{MONO}}}
.b{{font-weight:700}} .sb{{font-weight:600}}
"""


def svg(w, h, body, css="", reduced_extra="", title="", t=None):
    style = BASE_CSS + css + (REDUCED % reduced_extra)
    ttl = f"<title>{escape(title)}</title>" if title else ""
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" '
            f'role="img" aria-label="{escape(title)}">{ttl}<style>{style}</style>{body}</svg>')


def write(name, content):
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / name).write_text(content, encoding="utf-8")


def T(x, y, s, cls="", fill="#000", size=16, anchor="start", extra=""):
    return (f'<text x="{x}" y="{y}" class="{cls}" fill="{fill}" font-size="{size}" '
            f'text-anchor="{anchor}" {extra}>{escape(s)}</text>')


# ───────────────────────────────────────────────────────────── icons ──
import json
ICONS = json.loads((Path(__file__).parent / "icons.json").read_text())


def icon(name, x, y, size, fill):
    """Place a react-icons/simple-icons SVG path at x,y with given size."""
    import re
    raw = ICONS[name]
    vb = [float(v) for v in re.search(r'viewBox="([^"]+)"', raw).group(1).split()]
    inner = re.search(r'<svg[^>]*>(.*)</svg>', raw, re.S).group(1)
    s = size / max(vb[2], vb[3])
    ox = x + (size - vb[2] * s) / 2
    oy = y + (size - vb[3] * s) / 2
    return f'<g transform="translate({ox:.2f},{oy:.2f}) scale({s:.4f})" fill="{fill}">{inner}</g>'


def sparkle(cx, cy, r, fill, cls=""):
    """Four-point star."""
    k = r * 0.28
    d = (f"M{cx},{cy-r} Q{cx+k},{cy-k} {cx+r},{cy} Q{cx+k},{cy+k} {cx},{cy+r} "
         f"Q{cx-k},{cy+k} {cx-r},{cy} Q{cx-k},{cy-k} {cx},{cy-r}Z")
    return f'<path class="{cls}" d="{d}" fill="{fill}"/>'


def pixel_icon(rows, x, y, scale, colors):
    out = []
    for r, row in enumerate(rows):
        for c, ch in enumerate(row):
            if ch != ".":
                out.append(f'<rect x="{x+c*scale}" y="{y+r*scale}" width="{scale}" height="{scale}" fill="{colors[ch]}"/>')
    return f'<g shape-rendering="crispEdges">{"".join(out)}</g>'


PIX = {
    "prompt":  ["AAAAAAA", "A.....A", "AB....A", "A.B...A", "AB.CC.A", "A.....A", "AAAAAAA"],
    "diamond": ["..A..", ".AAA.", "AAAAA", ".AAA.", "..A.."],
    "heart":   [".AA.AA.", "AABAAAA", "AAAAAAA", ".AAAAA.", "..AAA..", "...A..."],
    "spark":   ["...A...", "...A...", "..ABA..", "AABBBAA", "..ABA..", "...A...", "...A..."],
    "folder":  ["AAA....", "ABBAAAA", "ABBBBBA", "ABBBBBA", "ABBBBBA", "AAAAAAA"],
    "chart":   [".....A.", ".....A.", "..B..A.", "..B..A.", "A.B..A.", "A.B..A.", "AAAAAAA"],
    "pad":     [".AAAAA.", "AABAAAA", "ABBBACA", "AABAAAA", "AAAAAAA", "AA...AA"],
    "mail":    ["AAAAAAA", "ABAAABA", "AABABAA", "AAABAAA", "AAAAAAA"],
    "user":    ["..AAA..", ".AAAAA.", ".AAAAA.", "..AAA..", ".BBBBB.", "BBBBBBB", "BBBBBBB"],
}


# ──────────────────────────────────────────────────────────── 1. HERO ──
HERO_PHRASES = [
    "Software Developer",
    "Creative web experiences",
    "Frontend · Backend · Databases",
    "Turning ideas into code",
]


def typing_block(phrases, x0, y, cw, size, fill, caret_fill, prefix="tp"):
    """Per-character typing/erasing loop. Returns (svg, css, reduced_css)."""
    tt, te, hold, gap = 0.075, 0.035, 1.7, 0.35
    starts, t = [], 0.0
    for p in phrases:
        starts.append(t)
        t += len(p) * tt + hold + len(p) * te + gap
    total = t
    pct = lambda v: f"{100 * v / total:.3f}%"
    body, css, events = [], [], []
    for i, p in enumerate(phrases):
        for j, ch in enumerate(p):
            if ch == " ":
                continue
            a = starts[i] + (j + 1) * tt
            d = starts[i] + len(p) * tt + hold + (len(p) - 1 - j) * te
            name = f"{prefix}{i}_{j}"
            css.append(f"@keyframes {name}{{0%,{pct(a-0.0001)}{{opacity:0}}{pct(a)},{pct(d-0.0001)}{{opacity:1}}{pct(d)},100%{{opacity:0}}}}"
                       f".{name}{{opacity:{1 if i == 0 else 0};animation:{name} {total:.2f}s step-end infinite}}")
            body.append(f'<text x="{x0 + j*cw:.1f}" y="{y}" class="mono {name}" fill="{fill}" font-size="{size}">{escape(ch)}</text>')
        # caret events
        for j in range(len(p)):
            events.append((starts[i] + (j + 1) * tt, j + 1))
        for j in range(len(p)):
            events.append((starts[i] + len(p) * tt + hold + j * te, len(p) - 1 - j))
    events.sort()
    frames = ["0%{transform:translateX(0px)}"]
    for tm, n in events:
        frames.append(f"{pct(tm)}{{transform:translateX({n*cw:.1f}px)}}")
    css.append(f"@keyframes {prefix}caret{{{''.join(frames)}}}"
               f".{prefix}caret{{transform:translateX({len(phrases[0])*cw:.1f}px);animation:{prefix}caret {total:.2f}s step-end infinite}}"
               f".{prefix}blink{{animation:{prefix}blink 1s step-end infinite}}@keyframes {prefix}blink{{0%,100%{{opacity:1}}50%{{opacity:0}}}}")
    body.append(f'<g class="{prefix}caret"><rect class="{prefix}blink" x="{x0+2}" y="{y-size*0.82:.1f}" width="{size*0.5:.1f}" height="{size*1.0:.1f}" rx="2" fill="{caret_fill}"/></g>')
    reduced = f".{prefix}caret{{transform:translateX({len(phrases[0])*cw:.1f}px)}}"
    return "".join(body), "".join(css), reduced


def hero(theme):
    t = THEMES[theme]
    W, H = 1000, 360
    g1, g2, g3 = t["grad"]
    defs = f"""<defs>
<linearGradient id="hbg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{t['heroA']}"/><stop offset=".55" stop-color="{t['heroB']}"/><stop offset="1" stop-color="{t['heroC']}"/></linearGradient>
<linearGradient id="name" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{g1}"/><stop offset=".55" stop-color="{g2}"/><stop offset="1" stop-color="{g3}"/></linearGradient>
<radialGradient id="glow" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="{'#D8B4F8' if theme == 'light' else t['pink']}" stop-opacity="{.55 if theme=='light' else .22}"/><stop offset="1" stop-color="{'#D8B4F8' if theme == 'light' else t['pink']}" stop-opacity="0"/></radialGradient>
<radialGradient id="glow2" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="{'#F9E6A0' if theme == 'light' else t['sky']}" stop-opacity="{.45 if theme=='light' else .18}"/><stop offset="1" stop-color="{'#F9E6A0' if theme == 'light' else t['sky']}" stop-opacity="0"/></radialGradient>
<radialGradient id="glow3" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="#B8E4D0" stop-opacity="{.45 if theme=='light' else .12}"/><stop offset="1" stop-color="#B8E4D0" stop-opacity="0"/></radialGradient>
<radialGradient id="glow4" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="#FFD6BA" stop-opacity="{.5 if theme=='light' else .1}"/><stop offset="1" stop-color="#FFD6BA" stop-opacity="0"/></radialGradient>
<pattern id="dots" width="22" height="22" patternUnits="userSpaceOnUse"><circle cx="2" cy="2" r="1.3" fill="{t['dot']}"/></pattern>
<clipPath id="card"><rect x="1" y="1" width="{W-2}" height="{H-2}" rx="26"/></clipPath>
</defs>"""
    bg = (f'<rect x="1" y="1" width="{W-2}" height="{H-2}" rx="26" fill="url(#hbg)" stroke="{t["border"]}" stroke-width="1.5"/>'
          f'<g clip-path="url(#card)"><rect width="{W}" height="{H}" fill="url(#dots)" opacity=".8"/>'
          f'<circle class="drift" cx="800" cy="170" r="170" fill="url(#glow)"/>'
          f'<circle class="drift d2" cx="640" cy="330" r="160" fill="url(#glow2)"/>'
          f'<circle class="drift" cx="960" cy="330" r="150" fill="url(#glow3)"/>'
          f'<circle class="drift d2" cx="60" cy="20" r="170" fill="url(#glow4)"/></g>')
    # window chrome
    chrome = (f'<circle cx="38" cy="36" r="6.5" fill="{'#D8B4F8' if theme == 'light' else '#F8BBD0'}"/><circle cx="60" cy="36" r="6.5" fill="#F9E6A0"/>'
              f'<circle cx="82" cy="36" r="6.5" fill="#B8E4D0"/>'
              + T(104, 41, "~/sara-zambrano/README.md", "mono", t["faint"], 14)
              + T(W - 36, 41, "pastel tech edition", "mono", t["faint"], 14, "end"))
    # text block
    x = 56
    hello = (f'<g class="rise r0">' + T(x, 112, "<hello world />", "mono sb", fam(theme, "lilac")["T"] if theme == "light" else t["pinkT"], 18)
             + T(x + 168, 112, "I'm", "mono", t["muted"], 18) + "</g>")
    name = (f'<g class="rise r1">' + T(x - 3, 174, "Sara", "sans b", t["text"], 64, extra='letter-spacing="-0.5"') + "</g>"
            f'<g class="rise r2">' + T(x - 3, 242, "Zambrano", "sans b", "url(#name)", 64, extra='letter-spacing="-0.5"') + "</g>")
    prompt = T(x, 284, "❯", "mono b", t["lavT"], 22)
    typed, tcss, tred = typing_block(HERO_PHRASES, x + 28, 284, 13.2, 22, t["text"], fam(theme, "lilac")["T"] if theme == "light" else t["pinkT"])
    # chips
    chips, cx = [], x
    for label, fm in (("Frontend", "butter" if theme == "light" else "blue"), ("Backend", "mint"), ("Databases", "lilac" if theme == "light" else "lav"), ("UI / UX", "peach")):
        F = fam(theme, fm)
        fill, tc = F["chip"], F["T"]
        w = len(label) * 8.6 + 28
        chips.append(f'<rect x="{cx}" y="308" width="{w:.0f}" height="28" rx="14" fill="{fill}" stroke="{t["border"]}"/>'
                     + T(cx + w / 2, 327, label, "sans sb", tc, 13.5, "middle"))
        cx += w + 10
    chips = '<g class="rise r3">' + "".join(chips) + "</g>"
    # sprite
    inner, sw, sh = sprite(t)
    sc = 5.7
    spx, spy = 664, 64
    blob = (f'<ellipse cx="{spx + sw*sc/2}" cy="{spy + sh*sc - 18}" rx="165" ry="18" fill="{t["lav"]}" opacity="{.35 if theme=="light" else .25}"/>')
    spr = (blob + f'<g transform="translate({spx},{spy}) scale({sc})" shape-rendering="crispEdges">{inner}</g>')
    # sparkles
    sp = "".join([
        sparkle(642, 104, 10, "#F9E6A0" if theme == "dark" else "#EBCB5E", "tw t1"),
        sparkle(958, 268, 9, "#D8B4F8", "tw t3"),
        f'<rect class="tw t2" x="536" y="74" width="6" height="6" fill="#B8E4D0"/>',
        f'<rect class="tw t4" x="604" y="232" width="5" height="5" fill="#FFD6BA"/>',
    ])
    code_tag = (f'<g class="floaty"><rect x="886" y="62" width="64" height="30" rx="10" fill="{t["card"]}" stroke="{t["border"]}"/>'
                + T(918, 82, "</>", "mono b", fam(theme, "mint")["T"], 15, "middle") + "</g>"
                + f'<g class="floaty f2"><rect x="606" y="150" width="52" height="30" rx="10" fill="{t["card"]}" stroke="{t["border"]}"/>'
                + T(632, 170, "{ }", "mono b", fam(theme, "peach")["T"], 15, "middle") + "</g>")
    css = SPRITE_CSS + tcss + """
.rise{animation:rise .9s cubic-bezier(.2,.7,.2,1) both}
.r1{animation-delay:.15s}.r2{animation-delay:.3s}.r3{animation-delay:.55s}
@keyframes rise{from{opacity:0;transform:translateY(14px)}to{opacity:1;transform:none}}
.tw{transform-box:fill-box;transform-origin:center;animation:tw 3.2s ease-in-out infinite}
.t2{animation-delay:-.8s}.t3{animation-delay:-1.6s}.t4{animation-delay:-2.4s}
@keyframes tw{0%,100%{opacity:.35;transform:scale(.7) rotate(0)}50%{opacity:1;transform:scale(1) rotate(20deg)}}
.floaty{animation:floaty 4s ease-in-out infinite}.f2{animation-delay:-2s}
@keyframes floaty{0%,100%{transform:translateY(0)}50%{transform:translateY(-6px)}}
.drift{animation:drift 9s ease-in-out infinite alternate}.d2{animation-delay:-4s}
@keyframes drift{from{transform:translate(0,0)}to{transform:translate(-24px,10px)}}
"""
    body = defs + bg + chrome + hello + name + prompt + typed + chips + sp + code_tag + spr
    return svg(W, H, body, css, tred + SPRITE_CSS_REDUCED,
               "Sara Zambrano — Software Developer. Pixel-art illustration of Sara coding at her laptop.")


# ─────────────────────────────────────────────── 2. SECTION HEADERS ──
SECTIONS = [
    ("about", "01", "About me", "// whoami", "prompt"),
    ("stack", "02", "Tech stack", "// tools I build with", "spark"),
    ("projects", "03", "Featured projects", "// things I've built", "folder"),
    ("activity", "04", "GitHub activity", "// commits & languages", "chart"),
    ("game", "05", "Take a little break!", "// sara's arcade", "pad"),
    ("connect", "06", "Let's connect", "// say hi ✿", "mail"),
]


def section(theme, key, num, title, sub, pix):
    t = THEMES[theme]
    W, H = 1000, 76
    fm = {"about": "pink", "stack": "blue", "projects": "lav", "activity": "mint", "game": "butter", "connect": "lilac"}[key]
    F = fam(theme, fm)
    tile = F["tile"]
    colors = {"A": F["T"], "B": F["T"] if pix == "prompt" else F["base"], "C": F["T"]}
    rows = PIX[pix]
    sc = 4
    pw, ph = len(rows[0]) * sc, len(rows) * sc
    ico = (f'<rect x="12" y="12" width="52" height="52" rx="16" fill="{tile}" stroke="{t["border"]}"/>'
           + pixel_icon(rows, 12 + (52 - pw) / 2, 12 + (52 - ph) / 2, sc, colors))
    tw = len(title) * 15.2
    text = (T(82, 33, num, "mono b", F["T"], 14) + T(82 + 26, 33, sub, "mono", t["faint"], 14)
            + T(80, 62, title, "sans b", t["text"], 27))
    lx = 96 + max(tw, len(sub) * 8.6 + 26)
    end = {
        "about": "".join(f'<rect x="{W-58+i*12}" y="49" width="6" height="6" rx="1" fill="{F["T"] if i == 2 else F["base"]}"/>' for i in range(3)),
        "stack": f'<rect x="{W-40}" y="45" width="12" height="12" transform="rotate(45 {W-34} 51)" fill="{F["base"]}"/>',
        "projects": T(W - 30, 57, "</>", "mono b", F["T"], 14, "end"),
        "activity": "".join(f'<rect x="{W-56+i*9}" y="{57-h}" width="6" height="{h}" rx="1" fill="{F["T"] if i == 3 else F["base"]}"/>' for i, h in enumerate((6, 11, 8, 15))),
        "game": pixel_icon(PIX["spark"], W - 52, 38, 4, {"A": F["T"], "B": F["base"]}),
        "connect": f'<circle cx="{W-36}" cy="51" r="7" fill="none" stroke="{F["T"]}" stroke-width="2.5"/>',
    }[key]
    line = (f'<line x1="{lx:.0f}" y1="52" x2="{W-72}" y2="52" stroke="{t["border"]}" stroke-width="2" stroke-dasharray="2 8" stroke-linecap="round"/>'
            + f'<g class="tw">{end}</g>')
    bgr = f'<rect x="1" y="1" width="{W-2}" height="{H-2}" rx="22" fill="{t["bg"]}" stroke="{t["border"]}"/>'
    css = """.tw{animation:tw 3.4s ease-in-out infinite}
@keyframes tw{0%,100%{opacity:.55}50%{opacity:1}}"""
    return svg(W, H, bgr + ico + text + line, css, "", f"{num} — {title}")


# ──────────────────────────────────────────────────── 3. ABOUT TERMINAL ──
def about(theme):
    t = dict(THEMES[theme])
    for fm in FAMILIES:
        t[fm + "T"] = fam(theme, fm)["T"]
    W = 1000
    lh = 27
    lines = []  # list of (kind, segments) ; segments = [(text, colorkey, cls)]
    P = lambda cmd: ("cmd", [("sara", "pinkT", "b"), ("@github", "lavT", ""), (":", "faint", ""), ("~", "blueT", "b"),
                             ("$ ", "faint", ""), (cmd, "text", "sb")])
    O = lambda *segs: ("out", list(segs))
    lines += [P("whoami"),
              O(("  Sara Zambrano", "text", "b"), (" — Software Developer", "muted", "")),
              P("cat about.txt"),
              O(("  ✦ ", "pinkT", ""), ("builds responsive web apps end-to-end: ", "text", ""), ("frontend · backend · databases", "blueT", "sb")),
              O(("  ✦ ", "mintT", ""), ("cares about ", "text", ""), ("UX", "peachT", "sb"), (", maintainable code and the tiny details", "text", "")),
              O(("  ✦ ", "butterT", ""), ("fast learner · adaptable · problem solver · team player", "text", "")),
              P("ls ./languages"),
              O(("  spanish", "text", "sb"), ("@native", "peachT", ""), ("   english", "text", "sb"), ("@B2", "blueT", ""),
                ("   french", "text", "sb"), ("@B1", "lilacT", "")),
              P("ls ./soft-skills"),
              O(("  leadership  collaboration  communication  creativity", "muted", "")),
              O(("  proactivity  discipline  adaptability", "muted", "")),
              ("cmd_last", [("sara", "pinkT", "b"), ("@github", "lavT", ""), (":", "faint", ""), ("~", "blueT", "b"), ("$ ", "faint", "")])]
    top = 64
    H = top + len(lines) * lh + 34
    cw = 10.2  # 17px mono advance
    body = [f'<rect x="1" y="1" width="{W-2}" height="{H-2}" rx="22" fill="{t["term"]}" stroke="{t["border"]}" stroke-width="1.5"/>',
            f'<path d="M1 23 a22 22 0 0 1 22 -22 H{W-23} a22 22 0 0 1 22 22 V44 H1Z" fill="{t["termbar"]}"/>',
            f'<line x1="1" y1="44" x2="{W-1}" y2="44" stroke="{t["border"]}"/>',
            f'<circle cx="28" cy="23" r="6.5" fill="#F8BBD0"/><circle cx="50" cy="23" r="6.5" fill="#F9E6A0"/><circle cx="72" cy="23" r="6.5" fill="#B8E4D0"/>',
            T(W / 2, 28, "sara@github: ~ — zsh", "mono", t["faint"], 13.5, "middle")]
    css = []
    for i, (kind, segs) in enumerate(lines):
        y = top + i * lh + 18
        x = 30
        parts = []
        for txt, ck, cls in segs:
            parts.append(f'<tspan fill="{t[ck]}" class="{cls}">{escape(txt)}</tspan>')
            x += len(txt) * cw
        delay = 0.2 + i * 0.2
        body.append(f'<text x="30" y="{y}" class="mono ln" font-size="17" style="animation-delay:{delay:.2f}s" xml:space="preserve">{"".join(parts)}</text>')
        if kind == "cmd_last":
            body.append(f'<rect class="caret" x="{x+2:.1f}" y="{y-15}" width="10" height="19" rx="2" fill="{t["pinkT"]}" style="animation-delay:{delay:.2f}s,{delay:.2f}s"/>')
    css.append("""
.ln{opacity:1;animation:ln .5s ease-out both}
@keyframes ln{from{opacity:0;transform:translateX(-6px)}to{opacity:1;transform:none}}
.caret{animation:ln .5s ease-out both,blink 1s step-end infinite}
@keyframes blink{0%,100%{opacity:1}50%{opacity:0}}
.beat{transform-box:fill-box;transform-origin:center;animation:beat 1.6s ease-in-out infinite}
@keyframes beat{0%,100%{transform:scale(1)}15%{transform:scale(1.15)}30%{transform:scale(1)}}
""")
    return svg(W, H, "".join(body), "".join(css), "",
               "Terminal: whoami — Sara Zambrano, Software Developer. Builds responsive web apps "
               "end-to-end (frontend, backend, databases); cares about UX and maintainable code. Languages: Spanish "
               "(native), English (B2), French (B1). Soft skills: leadership, collaboration, communication, creativity, "
               "proactivity, discipline, adaptability.")


# ─────────────────────────────────────────────────────── 4. TECH STACK ──
STACK = [
    ("Languages", "peach", [("Python", "SiPython"), ("JavaScript", "SiJavascript"), ("PHP", "SiPhp")]),
    ("Frontend", "blue", [("HTML5", "SiHtml5"), ("CSS3", "SiCss"), ("Tailwind", "SiTailwindcss"), ("React", "SiReact")]),
    ("Databases", "lav", [("MySQL", "SiMysql"), ("PostgreSQL", "SiPostgresql")]),
    ("Version control", "mint", [("Git", "SiGit"), ("GitHub", "SiGithub")]),
    ("Design & methods", "butter", [("Figma", "SiFigma"), ("Scrum", "FaArrowsRotate")]),
]


def stack(theme):
    t = THEMES[theme]
    W = 1000
    tile, gap, pad, head = 104, 14, 22, 54
    rows = [STACK[:2], STACK[2:]]
    ch = head + tile + pad + 4
    body, k = [], 0
    y = 18
    for row in rows:
        widths = [len(items) * tile + (len(items) - 1) * gap + 2 * pad for _, _, items in row]
        total = sum(widths) + 20 * (len(row) - 1)
        x = (W - total) / 2
        for (cat, a, items), cwid in zip(row, widths):
            F = fam(theme, a)
            body.append(f'<g class="up" style="animation-delay:{k*0.12:.2f}s">')
            body.append(f'<rect x="{x}" y="{y}" width="{cwid}" height="{ch}" rx="22" fill="{t["card"]}" stroke="{t["border"]}" stroke-width="1.5"/>')
            body.append(f'<rect x="{x+pad}" y="{y+23}" width="10" height="10" rx="2" fill="{F["base"]}"/>')
            body.append(T(x + pad + 18, y + 33, cat, "sans b", t["text"], 16))
            body.append(T(x + cwid - pad, y + 33, f"{len(items):02d}", "mono", t["faint"], 13, "end"))
            for i, (label, ic) in enumerate(items):
                tx, ty = x + pad + i * (tile + gap), y + head
                body.append(f'<rect x="{tx}" y="{ty}" width="{tile}" height="{tile}" rx="18" fill="{F["tile"]}"/>')
                body.append(icon(ic, tx + tile / 2 - 20, ty + 18, 40, F["T"]))
                body.append(T(tx + tile / 2, ty + tile - 16, label, "sans sb", t["text"], 13.5, "middle"))
            body.append("</g>")
            x += cwid + 20
            k += 1
        y += ch + 18
    H = y
    css = """.up{animation:up .7s cubic-bezier(.2,.7,.2,1) both}
@keyframes up{from{opacity:0;transform:translateY(12px)}to{opacity:1;transform:none}}"""
    return svg(W, H, "".join(body), css, "",
               "Tech stack — Languages: Python, JavaScript, PHP. Frontend: HTML5, CSS3, Tailwind CSS, React. "
               "Databases: MySQL, PostgreSQL. Version control: Git, GitHub. Design & methods: Figma, Scrum.")


# ───────────────────────────────────────────────────── 5. PROJECT CARDS ──
def chip(x, y, label, fill, tc, border, size=13):
    w = len(label) * size * 0.58 + 24
    return (f'<rect x="{x:.1f}" y="{y}" width="{w:.1f}" height="26" rx="13" fill="{fill}" stroke="{border}"/>'
            + T(x + w / 2, y + 17.5, label, "sans sb", tc, size, "middle")), w


def project_card(theme, p):
    t = THEMES[theme]
    W, H = 1000, 360
    body = [f'<rect x="1" y="1" width="{W-2}" height="{H-2}" rx="26" fill="{t["card"]}" stroke="{t["border"]}" stroke-width="1.5"/>']
    x = 40
    fams = [fam(theme, f) for f in p["fams"]]
    tag, tw = chip(x, 34, p["tag"], fams[0]["chip"], fams[0]["T"], t["border"], 12.5)
    body.append(tag)
    body.append(pixel_icon(p["pix"], x, 80, 4, {k: fams[v]["T"] if isinstance(v, int) else v for k, v in p["pixcol"].items()}))
    body.append(T(x + 48, 108, p["name"], "sans b", t["text"], 34, extra='letter-spacing="-0.4"'))
    for i, ln in enumerate(p["desc"]):
        body.append(T(x, 146 + i * 23, ln, "sans", t["muted"], 16.5))
    fy = 146 + len(p["desc"]) * 23 + 18
    for i, f in enumerate(p["features"]):
        col, row = i % 2, i // 2
        fx, fyy = x + col * 262, fy + row * 27
        body.append(pixel_icon([".A.", "AAA", ".A."], fx, fyy - 10, 3, {"A": fams[i % len(fams)]["T"]}))
        body.append(T(fx + 16, fyy, f, "sans", t["text"], 14.5))
    cx = x
    ty = H - 54
    for i, tech in enumerate(p["tech"]):
        fill, tc = fams[i % len(fams)]["chip"], fams[i % len(fams)]["T"]
        c, w = chip(cx, ty, tech, fill, tc, t["border"], 12.5)
        body.append(c)
        cx += w + 8
    # preview window
    px, py, pw, ph = 590, 34, 370, 292
    body.append(f'<rect x="{px}" y="{py}" width="{pw}" height="{ph}" rx="18" fill="{t["bg"]}" stroke="{t["border"]}" stroke-width="1.5"/>')
    body.append(f'<circle cx="{px+20}" cy="{py+18}" r="5" fill="#F8BBD0"/><circle cx="{px+36}" cy="{py+18}" r="5" fill="#F9E6A0"/><circle cx="{px+52}" cy="{py+18}" r="5" fill="#B8E4D0"/>')
    body.append(f'<rect x="{px+70}" y="{py+9}" width="{pw-90}" height="18" rx="9" fill="{t["card"]}" stroke="{t["border"]}"/>')
    body.append(T(px + 82, py + 22, p["url"], "mono", t["faint"], 11.5))
    inner_x, inner_y, inner_w, inner_h = px + 10, py + 36, pw - 20, ph - 46
    body.append(f'<clipPath id="pv{p["id"]}"><rect x="{inner_x}" y="{inner_y}" width="{inner_w}" height="{inner_h}" rx="12"/></clipPath>')
    body.append(f'<g clip-path="url(#pv{p["id"]})">{p["preview"](t, inner_x, inner_y, inner_w, inner_h)}</g>')
    css = (p.get("css", "") + """
.sh{animation:sh 6s ease-in-out infinite}@keyframes sh{0%,100%{transform:translateY(0)}50%{transform:translateY(-4px)}}""")
    return svg(W, H, "".join(body), css, "", f'{p["name"]} — {" ".join(p["desc"])}')


def coffee_preview(t, x, y, w, h):
    """Real screenshot of CoffeeLand (from Sara's portfolio), embedded so the card is self-contained."""
    shot = ROOT / "scripts" / "coffeeland-preview.jpg"
    if not shot.exists():
        return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{t["blush"]}"/>'
    b64 = base64.b64encode(shot.read_bytes()).decode()
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="#FFF6EC"/>'
            f'<image href="data:image/jpeg;base64,{b64}" x="{x}" y="{y}" width="{w}" height="{h}" preserveAspectRatio="xMidYMid slice"/>')


CAR = [
    "........AAAA.................",
    "........ABBA.................",
    "..AAAA..AAAAAAAAAAAA.........",
    "..ACCAAAAAAAAAAAAAAAAAAAA....",
    "..ACCAAAAAWWWAAAAAAAAAAAAAA..",
    "...AAAAAAAAAAAAAAAAAAAAAAAAAA",
    "....KKK.............KKK......",
    "...KKKKK...........KKKKK.....",
    "....KKK.............KKK......",
]


def f1_preview(t, x, y, w, h):
    sky = t["board"]
    out = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{sky}"/>']
    # grandstand
    for i in range(9):
        out.append(f'<rect x="{x + i*40}" y="{y+40}" width="36" height="44" rx="4" fill="{[fam('light' if t['page']=='#FFFFFF' else 'dark', f)['tile'] for f in ('mint', 'blue', 'lilac')][i%3]}" stroke="{t["border"]}"/>')
        for j in range(3):
            out.append(f'<rect x="{x + i*40 + 6 + j*10}" y="{y+52}" width="6" height="6" rx="3" fill="{["#B8E4D0", "#BDE0FE", "#D8B4F8", "#F9E6A0"][(i+j)%4]}"/>')
    # checkered flag
    fx, fy = x + w - 70, y + 10
    out.append(f'<rect x="{fx-3}" y="{fy}" width="3" height="70" fill="{t["faint"]}"/>')
    for r in range(4):
        for c in range(6):
            out.append(f'<rect class="wave" x="{fx + c*7}" y="{fy + r*7}" width="7" height="7" fill="{t["text"] if (r+c)%2 else t["card"]}"/>')
    # track
    ty = y + 110
    out.append(f'<rect x="{x}" y="{ty}" width="{w}" height="{h-110}" fill="{t["muted"] if False else ("#5E6680" if t["page"]=="#FFFFFF" else "#2A3150")}"/>')
    out.append(f'<rect x="{x}" y="{ty}" width="{w}" height="8" fill="#B8E4D0"/>')
    for i in range(0, int(w) + 40, 40):
        out.append(f'<rect x="{x+i}" y="{ty}" width="20" height="8" fill="#FFFFFF"/>')
    out.append(f'<g class="lanes">' + "".join(f'<rect x="{x+i}" y="{ty+70}" width="28" height="5" rx="2" fill="#FFF9FC" opacity=".8"/>' for i in range(-60, int(w) + 60, 60)) + '</g>')
    out.append(f'<rect x="{x}" y="{y+h-8}" width="{w}" height="8" fill="{t["sky"]}"/>')
    # cars
    car1 = pixel_icon(CAR, 0, 0, 4, {"A": "#F8BBD0", "B": "#A2D2FF", "C": "#CDB4DB", "W": "#293247", "K": "#1E2333"})
    car2 = pixel_icon(CAR, 0, 0, 3, {"A": "#A2D2FF", "B": "#F8BBD0", "C": "#FFE5EC", "W": "#293247", "K": "#1E2333"})
    x0, x1 = x - 130, x + w + 20
    out.append(f"<style>@keyframes drive1{{from{{transform:translate({x0}px,{ty+26}px)}}to{{transform:translate({x1}px,{ty+26}px)}}}}"
               f"@keyframes drive2{{from{{transform:translate({x0}px,{ty+96}px)}}to{{transform:translate({x1}px,{ty+96}px)}}}}"
               f".c1{{transform:translate({x+40}px,{ty+26}px);animation:drive1 3.6s linear infinite}}"
               f".c2{{transform:translate({x+200}px,{ty+96}px);animation:drive2 5.2s linear infinite;animation-delay:-2.4s}}</style>")
    out.append(f'<g class="c1">{car1}</g>')
    out.append(f'<g class="c2">{car2}</g>')
    return "".join(out)


F1_CSS = """
.lanes{animation:lanes .8s linear infinite}
@keyframes lanes{from{transform:translateX(0)}to{transform:translateX(-60px)}}
"""

PROJECTS = [
    dict(id="coffee", name="CoffeeLand", tag="Full-stack · Web platform", url="coffeeland · catálogo de café colombiano",
         pix=["..A.A..", "...A...", "BBBBBB.", "BCCCCBB", "BCCCCB.B", "BBBBBBB", ".BBBBB."],
         pixcol={"A": 2, "B": 0, "C": "#FFF6EC"}, fams=["peach", "butter", "pink"],
         desc=["Interactive platform showcasing Colombia's coffee", "varieties, from technical cards to a coffee map."],
         features=["Dynamic cards & filters", "Interactive map (Leaflet)", "PDF report generation",
                   "REST API with Slim 4", "Admin data management", "Responsive Tailwind UI"],
         tech=["PHP", "Slim 4", "MySQL", "JavaScript", "Tailwind CSS", "HTML5 · CSS3"],
         preview=coffee_preview, css=""),
    dict(id="f1", name="F1 Simulation", tag="Team project · Web app", url="f1-simulador · race control",
         pix=["AB.....", "ABBA...", "ABBABBA", "A..ABBA", "A......", "A......", "A......"],
         pixcol={"A": 2, "B": 0}, fams=["mint", "blue", "lilac"],
         desc=["Web app to manage Formula 1 circuits, drivers and", "vehicles — and simulate races between them."],
         features=["CRUD: circuits, drivers, cars", "Race logic: track & strategy",
                   "Local storage persistence", "Dynamic visualizations",
                   "Reusable Web Components", "Animations & interactions"],
         tech=["JavaScript", "HTML5", "CSS3", "Web Components", "localStorage"],
         preview=f1_preview, css=F1_CSS),
]


# ──────────────────────────────────────────────────── 6. GAME PREVIEW ──
def game_preview(theme):
    t = THEMES[theme]
    W, H = 1000, 320
    cell, cols, rows = 22, 17, 11
    bx, by = 40, 38
    body = [f'<rect x="1" y="1" width="{W-2}" height="{H-2}" rx="26" fill="{t["card"]}" stroke="{t["border"]}" stroke-width="1.5"/>']
    body.append(f'<rect x="{bx-8}" y="{by-8}" width="{cols*cell+16}" height="{rows*cell+16}" rx="18" fill="{t["board"]}" stroke="{t["border"]}"/>')
    for r in range(rows):
        for c in range(cols):
            if (r + c) % 2:
                body.append(f'<rect x="{bx+c*cell}" y="{by+r*cell}" width="{cell}" height="{cell}" fill="{t["board2"]}"/>')
    # loop path (rectangle perimeter)
    x0, y0, x1, y1 = 2, 2, 14, 8
    path = [(c, y0) for c in range(x0, x1)] + [(x1, r) for r in range(y0, y1)] + \
           [(c, y1) for c in range(x1, x0, -1)] + [(x0, r) for r in range(y1, y0, -1)]
    n = len(path)
    step = 0.16
    total = n * step
    kf = "".join(f"{100*i/n:.3f}%{{transform:translate({bx+c*cell}px,{by+r*cell}px)}}" for i, (c, r) in enumerate(path))
    css = [f"@keyframes snk{{{kf}100%{{transform:translate({bx+path[0][0]*cell}px,{by+path[0][1]*cell}px)}}}}"
           f".seg{{animation:snk {total:.2f}s step-end infinite}}"]
    L = 7
    seg_cols = ["#E58FB4" if theme == "light" else "#F8BBD0", "#F4AFC9", "#F8BBD0", "#EDBBE6", "#D8B4F8", "#CDB4DB", "#BDE0FE"]
    for k in range(L - 1, -1, -1):
        delay = -(total - k * step) % total
        c, r = path[(-k) % n]
        inner = f'<rect x="2" y="2" width="{cell-4}" height="{cell-4}" rx="6" fill="{seg_cols[k]}"/>'
        if k == 0:
            inner += f'<rect x="6" y="7" width="3" height="3" fill="#293247"/><rect x="13" y="7" width="3" height="3" fill="#293247"/>'
        body.append(f'<g class="seg" style="animation-delay:{-((n - k) * step) % total:.2f}s;transform:translate({bx+c*cell}px,{by+r*cell}px)">{inner}</g>')
    # foods on path
    for fi, idx in enumerate((7, 20, 31)):
        c, r = path[idx]
        eat = idx * step
        back = ((idx + n // 2) % n) * step
        a, b = 100 * eat / total, 100 * back / total
        name = f"food{fi}"
        if b > a:
            frames = f"0%,{a-0.01:.2f}%{{opacity:1}}{a:.2f}%,{b-0.01:.2f}%{{opacity:0}}{b:.2f}%,100%{{opacity:1}}"
        else:
            frames = f"0%,{b-0.01:.2f}%{{opacity:0}}{b:.2f}%,{a-0.01:.2f}%{{opacity:1}}{a:.2f}%,100%{{opacity:0}}"
        css.append(f"@keyframes {name}{{{frames}}}.{name}{{animation:{name} {total:.2f}s step-end infinite}}")
        col = [fam(theme, "pink")["T"], fam(theme, "butter")["T"] if theme == "light" else "#F9E6A0", fam(theme, "mint")["T"]][fi]
        if fi == 2:
            body.append(f'<g class="{name}">{pixel_icon(PIX["diamond"], bx+c*cell+6, by+r*cell+6, 2, {"A": col})}</g>')
        elif fi == 1:
            body.append(f'<g class="{name}">{sparkle(bx+c*cell+cell/2, by+r*cell+cell/2, 8, col)}</g>')
        else:
            body.append(f'<g class="{name}">{pixel_icon(PIX["heart"], bx+c*cell+4, by+r*cell+5, 2, {"A": col, "B": "#FFFFFF"})}</g>')
        # +1 pop
        pa = a
        css.append(f"@keyframes pop{fi}{{0%,{pa-0.01:.2f}%{{opacity:0;transform:translateY(0)}}{pa:.2f}%{{opacity:1;transform:translateY(0)}}"
                   f"{min(pa+12,99.9):.2f}%{{opacity:0;transform:translateY(-14px)}}100%{{opacity:0}}}}.pop{fi}{{opacity:0;animation:pop{fi} {total:.2f}s linear infinite}}")
        body.append(f'<g class="pop{fi}">' + T(bx + c * cell + cell / 2, by + r * cell - 2, "+1", "mono b", col, 13, "middle") + "</g>")
    # right side copy
    rx = 470
    body.append(T(rx, 92, "MINI GAME  ·  PLAY IN YOUR BROWSER", "mono b", fam(theme, "butter")["T"], 15, extra='letter-spacing="3"'))
    body.append(T(rx, 140, "Pastel Snake", "sans b", t["text"], 40, extra='letter-spacing="-0.4"'))
    body.append(T(rx, 172, "Even developers need a little fun.", "sans", t["muted"], 18))
    # keycaps
    kx, ky = rx, 196
    def keycap(x, y, rot):
        tri = {"u": "M0,-5 L6,4 L-6,4Z", "d": "M0,5 L6,-4 L-6,-4Z", "l": "M-5,0 L4,-6 L4,6Z", "r": "M5,0 L-4,-6 L-4,6Z"}[rot]
        return (f'<rect x="{x}" y="{y}" width="34" height="30" rx="8" fill="{t["bg"]}" stroke="{t["border"]}" stroke-width="1.5"/>'
                f'<rect x="{x}" y="{y+26}" width="34" height="4" rx="2" fill="{t["border"]}"/>'
                f'<path transform="translate({x+17},{y+14})" d="{tri}" fill="{fam(theme, "lilac")["T"]}"/>')
    body.append(keycap(kx + 38, ky, "u") + keycap(kx, ky + 34, "l") + keycap(kx + 38, ky + 34, "d") + keycap(kx + 76, ky + 34, "r"))
    body.append(T(kx + 128, ky + 42, "arrows / WASD", "mono", t["faint"], 14))
    body.append(T(kx + 128, ky + 62, "or swipe on mobile", "mono", t["faint"], 14))
    # CTA
    bx2, by2 = rx + 300, 238
    body.append(f'<g class="cta"><rect x="{bx2}" y="{by2}" width="196" height="50" rx="25" fill="{t["pink"]}"/>'
                f'<rect x="{bx2}" y="{by2}" width="196" height="50" rx="25" fill="none" stroke="{t["pinkT"]}" stroke-opacity=".35" stroke-width="1.5"/>'
                f'<path transform="translate({bx2+30},{by2+25})" d="M-6,-8 L8,0 L-6,8Z" fill="#293247"/>'
                + T(bx2 + 112, by2 + 31, "Play now", "sans b", "#293247", 17, "middle") + "</g>")
    css.append(""".cta{transform-box:fill-box;transform-origin:center;animation:cta 2.4s ease-in-out infinite}
@keyframes cta{0%,100%{transform:scale(1)}50%{transform:scale(1.04)}}""")
    return svg(W, H, "".join(body), "".join(css), ".pop0,.pop1,.pop2{opacity:0}",
               "Pastel Snake — a tiny pastel snake game. Click to play in your browser.")


# ────────────────────────────────────────────────────── 7. CONTACT PILLS ──
CONTACT = [
    ("linkedin", "LinkedIn", "Sara Zambrano", "FaLinkedinIn", "blue"),
    ("portfolio", "Portfolio", "my website", "FaGlobe", "mint"),
    ("github", "GitHub", "@sofiaas16", "FaGithub", "lilac"),
]


def contact_pill(theme, key, label, sub, ic, acc):
    t = THEMES[theme]
    W, H = 232, 64
    F = fam(theme, acc)
    tile = F["tile"]
    body = (f'<rect x="1" y="1" width="{W-2}" height="{H-2}" rx="32" fill="{t["card"]}" stroke="{t["border"]}" stroke-width="1.5"/>'
            f'<circle cx="32" cy="32" r="21" fill="{tile}"/>' + icon(ic, 22, 22, 20, F["T"])
            + T(64, 28, label, "sans b", t["text"], 15.5) + T(64, 47, sub, "mono", t["faint"], 11.5)
            + f'<path d="M{W-34},26 l6,6 l-6,6" fill="none" stroke="{F["T"]}" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/>')
    return svg(W, H, body, "", "", f"{label}: {sub}")


# ──────────────────────────────────────────────────────────── 8. FOOTER ──
def footer(theme):
    t = THEMES[theme]
    W, H = 1000, 176
    body = [f'<defs><linearGradient id="fb" x1="0" x2="1"><stop offset="0" stop-color="{t["heroA"]}"/><stop offset=".5" stop-color="{t["heroB"]}"/><stop offset="1" stop-color="{t["heroC"]}"/></linearGradient></defs>',
            f'<rect x="1" y="1" width="{W-2}" height="{H-2}" rx="26" fill="url(#fb)" stroke="{t["border"]}" stroke-width="1.5"/>']
    body.append(f'<line x1="{W/2-28}" y1="62" x2="{W/2+28}" y2="62" stroke="{fam(theme, "lilac")["T"] if theme == "light" else t["lav"]}" stroke-width="3" stroke-linecap="round" opacity=".7"/>')
    body.append(T(W / 2, 104, "Thanks for stopping by", "sans b", t["text"], 30, "middle", 'letter-spacing="-0.3"'))
    body.append(T(W / 2, 136, "Turning ideas into code — one soft pixel at a time.", "sans", t["muted"], 18, "middle"))
    css = """.hop{animation:hop 2.2s ease-in-out infinite}@keyframes hop{0%,60%,100%{transform:translateY(0)}30%{transform:translateY(-7px)}}
.tw{transform-box:fill-box;transform-origin:center;animation:tw 3.2s ease-in-out infinite}.t2{animation-delay:-1s}.t3{animation-delay:-2s}
@keyframes tw{0%,100%{opacity:.4;transform:scale(.7)}50%{opacity:1;transform:scale(1) rotate(25deg)}}"""
    return svg(W, H, "".join(body), css, "", "Thanks for stopping by — turning ideas into code, one soft pixel at a time.")


# ─────────────────────────────────────────────────────────────── main ──
def main():
    for th in THEMES:
        write(f"hero-{th}.svg", hero(th))
        for key, num, title, sub, pix in SECTIONS:
            write(f"section-{key}-{th}.svg", section(th, key, num, title, sub, pix))
        write(f"about-{th}.svg", about(th))
        write(f"stack-{th}.svg", stack(th))
        for p in PROJECTS:
            write(f"project-{p['id']}-{th}.svg", project_card(th, p))
        for c in CONTACT:
            write(f"contact-{c[0]}-{th}.svg", contact_pill(th, *c))
        write(f"footer-{th}.svg", footer(th))
    total = sum(f.stat().st_size for f in OUT.glob("*.svg"))
    print(f"✓ {len(list(OUT.glob('*.svg')))} SVGs written to {OUT} ({total/1024:.0f} KB)")


if __name__ == "__main__":
    main()
