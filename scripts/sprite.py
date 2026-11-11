"""
Pixel-art Sara at her laptop — modelled on her original GIF character
(round 3/4 face, side-swept bangs, soft bob with a fuller right side,
tall little eyes, tiny U smile, big soft blush), with light-brown hair.

The head is built procedurally on a pixel grid (ellipses + a hand-tuned
bangs edge), then merged into <rect> runs.
"""

PAL = {
    # hair — light brown (castaño claro) #B98A65 with soft shade/highlight
    'o': '#6E4A34', 'H': '#B98A65', 'h': '#93694A', 'L': '#D8B28E',
    # skin
    'S': '#FFECE1', 's': '#F7D6C6', 'k': '#E2AE98', 'B': '#F7B5C6',
    # face details
    'E': '#3B2D33', 'M': '#C8697E',
    # gingham shirt (like the reference)
    'C': '#CFE6FB', 'c': '#A9CDF2', 'W': '#FFFFFF',
}

HW, HH = 34, 30           # head grid size
FACE_CX, FACE_CY = 15.5, 15.2


def _in_ellipse(c, r, cx, cy, rx, ry):
    return ((c + .5 - cx) / rx) ** 2 + ((r + .5 - cy) / ry) ** 2 <= 1


def _build_head():
    g = [['.'] * HW for _ in range(HH)]
    # 1) hair mass (back)
    for r in range(HH):
        for c in range(HW):
            if _in_ellipse(c, r, 16.0, 12.4, 15.0, 11.4):
                g[r][c] = 'H'
    # fuller right side falling to the shoulder, with an outward flip
    for r in range(12, 26):
        for c in range(23, 32):
            if _in_ellipse(c, r, 27.0, 17.8, 4.6, 8.4):
                g[r][c] = 'H'
    # shorter left lock beside the cheek
    for r in range(12, 23):
        for c in range(1, 8):
            if _in_ellipse(c, r, 4.8, 15.6, 3.3, 6.4):
                g[r][c] = 'H'
    # 2) face (round, wide — like the reference)
    face = set()
    for r in range(HH):
        for c in range(HW):
            if _in_ellipse(c, r, FACE_CX, FACE_CY, 11.8, 9.6):
                face.add((r, c))
    # 3) bangs: hair covers face pixels above this jagged, right-sweeping edge
    edge = {4: 16, 5: 14, 6: 13, 7: 12, 8: 12, 9: 11, 10: 10, 11: 9, 12: 9, 13: 10, 14: 11,
            15: 11, 16: 11, 17: 10, 18: 9, 19: 9, 20: 9, 21: 10, 22: 11, 23: 12, 24: 13,
            25: 14, 26: 16, 27: 18}
    for (r, c) in face:
        if r >= edge.get(c, 99):
            g[r][c] = 'S'
    # left lock overlaps the outer cheek a little (as in the reference)
    for r in range(13, 21):
        for c in range(3, 6):
            if _in_ellipse(c, r, 4.4, 16.4, 1.9, 4.8):
                g[r][c] = 'H'
    # 4) hair shading: shadow under the bangs + strand lines sweeping right
    for c, e in edge.items():
        if 0 < e - 1 < HH and g[e - 1][c] == 'H':
            g[e - 1][c] = 'h'
    for r in range(3, 11):
        for c in range(4, 30):
            if g[r][c] == 'H' and (c - r * 0.6) % 7.5 < 0.9 and r > 5:
                g[r][c] = 'h'
    for r in range(13, 26):                  # inner shade of the side hair
        for c in (25, 26):
            if g[r][c] == 'H' and (r, c - 1) in face and g[r][c - 1] == 'S':
                g[r][c] = 'h'
    # strand separators rising from each bang tip (reference style)
    tips = [c for c in range(5, 27) if edge[c] >= edge.get(c - 1, 0) and edge[c] >= edge.get(c + 1, 0) and edge[c] > 10]
    for c0 in tips:
        r, c = edge[c0] - 2, c0
        for _ in range(5):
            if 0 <= r < HH and 0 <= c < HW and g[r][c] == 'H':
                g[r][c] = 'h'
            r -= 1
            c -= 1 if _ % 2 == 0 else 0
    # highlight arc
    for r, c in ((2, 10), (2, 11), (2, 12), (3, 8), (3, 9), (3, 13), (3, 14), (4, 7), (4, 15),
                 (2, 13), (3, 10)):
        if g[r][c] == 'H':
            g[r][c] = 'L'
    # skin shading under the bangs line + jaw
    for (r, c) in face:
        if g[r][c] == 'S' and g[r - 1][c] in 'Hh':
            g[r][c] = 's'
    # 5) outline (hair → dark brown, face edge → soft skin outline)
    out = [row[:] for row in g]
    for r in range(HH):
        for c in range(HW):
            if g[r][c] == '.':
                continue
            nb = [g[rr][cc] if 0 <= rr < HH and 0 <= cc < HW else '.'
                  for rr, cc in ((r - 1, c), (r + 1, c), (r, c - 1), (r, c + 1))]
            if '.' in nb:
                out[r][c] = 'o' if g[r][c] in 'HhL' else 'k'
    g = out
    # 6) blush, mouth
    for r, c in ((16, 7), (16, 8), (16, 9), (17, 6), (17, 7), (17, 8), (17, 9),
                 (16, 22), (16, 23), (16, 24), (17, 22), (17, 23), (17, 24), (17, 25)):
        if g[r][c] in 'Ss':
            g[r][c] = 'B'
    for r, c in ((17, 13), (18, 14), (18, 15), (18, 16), (18, 17), (17, 18)):
        g[r][c] = 'M'
    return g


HEAD_GRID = _build_head()

# eyes: tall & narrow with a tiny lash flick (reference style)
EYES_OPEN = [(12, 11, 'E'), (13, 10, 'E'), (13, 11, 'E'), (14, 10, 'E'), (14, 11, 'E'), (15, 10, 'E'), (15, 11, 'E'),
             (12, 20, 'E'), (13, 20, 'E'), (13, 21, 'E'), (14, 20, 'E'), (14, 21, 'E'), (15, 20, 'E'), (15, 21, 'E')]
EYES_CLOSED = [(14, 9, 'E'), (15, 10, 'E'), (15, 11, 'E'), (14, 12, 'E'),
               (14, 19, 'E'), (15, 20, 'E'), (15, 21, 'E'), (14, 22, 'E')]


def _shirt_rows():
    rows = {}
    for r in range(25, 32):
        half = min(5 + (r - 25) * 3, 15)
        s = ['.'] * HW
        for c in range(16 - half, 16 + half):
            if 0 <= c < HW:
                s[c] = 'C' if ((c // 2) + (r // 2)) % 2 else 'c'
        rows[r] = s
    # neck + white collar
    for c in (14, 15, 16, 17):
        rows[25][c] = 's'
    for r, c in ((25, 12), (25, 13), (25, 18), (25, 19), (26, 13), (26, 14), (26, 17), (26, 18)):
        rows[r][c] = 'W'
    return {r: ''.join(v) for r, v in rows.items()}


def rows_to_rects(grid_rows, dx=0, dy=0, pal=PAL):
    """grid_rows: {r: str} — merge horizontal runs of the same colour."""
    out = []
    for r in sorted(grid_rows):
        s = grid_rows[r]
        c = 0
        while c < len(s):
            ch = s[c]
            if ch == '.':
                c += 1
                continue
            e = c
            while e < len(s) and s[e] == ch:
                e += 1
            out.append(f'<rect x="{c+dx}" y="{r+dy}" width="{e-c}" height="1" fill="{pal[ch]}"/>')
            c = e
    return ''.join(out)


def cells_to_rects(cells, dx=0, dy=0, pal=PAL):
    return ''.join(f'<rect x="{c+dx}" y="{r+dy}" width="1" height="1" fill="{pal[ch]}"/>' for r, c, ch in cells)


def box(x, y, w, h, fill):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}"/>'


def heart(x, y, fill):
    """5x4 pixel heart (used sparingly)."""
    px = ['.X.X.', 'XXXXX', '.XXX.', '..X..']
    return ''.join(box(x + c, y + r, 1, 1, fill) for r, row in enumerate(px) for c, ch in enumerate(row) if ch == 'X')


def pix_spark(x, y, fill):
    """5x5 pixel sparkle."""
    px = ['..X..', '..X..', 'XX.XX', '..X..', '..X..']
    return ''.join(box(x + c, y + r, 1, 1, fill) for r, row in enumerate(px) for c, ch in enumerate(row) if ch == 'X')


def pix_plus(x, y, fill):
    px = ['.X.', 'XXX', '.X.']
    return ''.join(box(x + c, y + r, 1, 1, fill) for r, row in enumerate(px) for c, ch in enumerate(row) if ch == 'X')


def sprite(theme):
    """Returns (inner_svg, width, height) in pixel units."""
    t = theme
    W, H = 50, 42
    ox, oy = 8, 0           # head offset in the canvas
    parts = []
    # desk
    parts.append(box(0, 39, W, 1, t['desk_top']))
    parts.append(box(0, 40, W, 2, t['desk']))
    # plant (mint)
    leaves = [(30, 3, 'g'), (31, 2, 'g'), (31, 4, 'g'), (32, 1, 'g'), (32, 3, 'G'), (32, 5, 'g'),
              (33, 2, 'G'), (33, 3, 'G'), (33, 4, 'G'), (34, 3, 'G')]
    lp = {'g': '#B8E4D0', 'G': '#86CBAA'}
    parts.append(''.join(box(c, r, 1, 1, lp[ch]) for r, c, ch in leaves))
    parts.append(box(1, 35, 5, 1, '#F2C9A8') + box(1, 36, 5, 3, '#FFD6BA') + box(2, 38, 3, 1, '#F2C9A8'))
    # character
    parts.append(rows_to_rects(_shirt_rows(), ox, oy))
    head_rows = {r: ''.join(row) for r, row in enumerate(HEAD_GRID)}
    parts.append('<g class="bob">' + rows_to_rects(head_rows, ox, oy)
                 + '<g class="eyes-open">' + cells_to_rects(EYES_OPEN, ox, oy) + '</g>'
                 + '<g class="eyes-closed">' + cells_to_rects(EYES_CLOSED, ox, oy) + '</g>'
                 + '</g>')
    # laptop lid (back view) with a small "</>" pixel logo
    lx, ly, lw, lh = 13, 28, 24, 10
    parts.append(box(lx + 1, ly, lw - 2, lh, t['lap_edge']))
    parts.append(box(lx, ly + 1, lw, lh - 1, t['lap_edge']))
    parts.append(box(lx + 1, ly + 1, lw - 2, lh - 1, t['lap']))
    parts.append(box(lx + 2, ly + 1, lw - 4, 1, t['lap_shine']))
    logo = ['X.....X', '.X...X.', 'X..X..X']   # tiny < / > glyph
    lgx, lgy = lx + lw // 2 - 1, ly + 4
    parts.append('<g class="pulse">' + ''.join(box(lgx + c, lgy + r, 1, 1, '#B8A2D6')
                                               for r, row in enumerate(['.X.', 'XXX', '.X.'])
                                               for c, ch in enumerate(row) if ch == 'X') + '</g>')
    parts.append(box(lx - 2, 38, lw + 4, 1, t['lap_edge']))
    # hands typing
    parts.append('<g class="tapL">' + box(lx - 1, 36, 2, 2, '#FFECE1') + box(lx - 1, 37, 2, 1, '#F7D6C6') + '</g>')
    parts.append('<g class="tapR">' + box(lx + lw - 1, 36, 2, 2, '#FFECE1') + box(lx + lw - 1, 37, 2, 1, '#F7D6C6') + '</g>')
    # mug (butter yellow, no heart)
    mx = 42
    parts.append(box(mx, 33, 5, 1, '#EBD27A') + box(mx, 34, 5, 5, '#F9E6A0') + box(mx + 5, 35, 1, 1, '#EBD27A')
                 + box(mx + 6, 35, 1, 2, '#EBD27A') + box(mx + 5, 37, 1, 1, '#EBD27A') + box(mx + 1, 36, 3, 1, '#FFFFFF'))
    parts.append('<g class="steam s1">' + box(mx + 1, 30, 1, 2, t['steam']) + '</g>')
    parts.append('<g class="steam s2">' + box(mx + 3, 29, 1, 2, t['steam']) + '</g>')
    # floating accents: one small heart, a sparkle and a plus
    parts.append('<g class="float f1">' + pix_spark(43, 20, '#D8B4F8') + '</g>')
    parts.append('<g class="float f2">' + pix_plus(3, 23, '#F9E6A0') + '</g>')
    parts.append('<g class="float f3">' + pix_plus(46, 12, '#B8E4D0') + '</g>')
    return '<g transform="translate(0,0)">' + ''.join(parts) + '</g>', W, H


SPRITE_CSS = """
.bob{animation:bob 2.4s steps(1,end) infinite}
@keyframes bob{0%,100%{transform:translateY(0)}50%{transform:translateY(1px)}}
.eyes-closed{opacity:0;animation:blinkC 4.8s steps(1,end) infinite}
.eyes-open{animation:blinkO 4.8s steps(1,end) infinite}
@keyframes blinkO{0%,93%{opacity:1}94%,97%{opacity:0}98%,100%{opacity:1}}
@keyframes blinkC{0%,93%{opacity:0}94%,97%{opacity:1}98%,100%{opacity:0}}
.tapL{animation:tap .5s steps(1,end) infinite}
.tapR{animation:tap .5s steps(1,end) infinite;animation-delay:-.25s}
@keyframes tap{0%,100%{transform:translateY(0)}50%{transform:translateY(-1px)}}
.pulse{animation:pulse 2.4s steps(1,end) infinite}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:.55}}
.steam{animation:steam 2.6s steps(4,end) infinite;opacity:0}
.s2{animation-delay:-1.3s}
@keyframes steam{0%{opacity:0;transform:translateY(0)}25%{opacity:.9}100%{opacity:0;transform:translateY(-4px)}}
.float{animation:float 5s steps(10,end) infinite;opacity:0}
.f2{animation-delay:-1.7s}.f3{animation-delay:-3.4s}
@keyframes float{0%{opacity:0;transform:translateY(0)}20%{opacity:1}80%{opacity:.9}100%{opacity:0;transform:translateY(-8px)}}
"""
SPRITE_CSS_REDUCED = """.eyes-closed{opacity:0}.eyes-open{opacity:1}.steam{opacity:.8}.float{opacity:1}"""
