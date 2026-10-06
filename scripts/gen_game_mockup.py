"""Generate the animated, game-style SVG mockup of the ACER 3D case floor."""
import math, random, os

random.seed(11)
OUT = os.path.join(os.path.dirname(__file__), "..", "docs", "mockups", "00-case-floor-game.svg")
C, S = math.cos(math.radians(30)), math.sin(math.radians(30))
W, H = 1920, 1080
K = 26
OX, OY = 900, 250

GREEN, AMBER, RED, CYAN = "#3ef0a0", "#ffc247", "#ff4d6a", "#4de1ff"


def iso(x, y, z=0, ox=OX, oy=OY, k=K):
    return ox + (x - y) * C * k, oy + (x + y) * S * k - z * k


def pts(ps):
    return " ".join(f"{a:.1f},{b:.1f}" for a, b in ps)


def poly(ps, fill, extra=""):
    return f'<polygon points="{pts(ps)}" fill="{fill}" {extra}/>'


def shade(hex_, f):
    h = hex_.lstrip("#"); r, g, b = (int(h[i:i+2], 16) for i in (0, 2, 4))
    return "#%02x%02x%02x" % tuple(max(0, min(255, int(c * f))) for c in (r, g, b))


def box(x, y, z, w, d, h, col, o=(OX, OY, K), edge=True, top=None, op=1):
    f = lambda a, b, c: iso(a, b, c, *o)
    t = [f(x, y, z+h), f(x+w, y, z+h), f(x+w, y+d, z+h), f(x, y+d, z+h)]
    l = [f(x, y+d, z), f(x+w, y+d, z), f(x+w, y+d, z+h), f(x, y+d, z+h)]
    r = [f(x+w, y, z), f(x+w, y+d, z), f(x+w, y+d, z+h), f(x+w, y, z+h)]
    e = 'stroke="#ffffff" stroke-opacity=".18" stroke-width=".8"' if edge else ""
    return (f'<g opacity="{op}">' + poly(l, shade(col, .55), e) + poly(r, shade(col, .78), e)
            + poly(t, top or shade(col, 1.12), e)
            # specular sheen on the right face
            + poly(r, "url(#sheen)") + "</g>")


def shadow(x, y, w, d, blur=True):
    ps = [iso(x + .5, y + .5), iso(x + w + 1.3, y + .5), iso(x + w + 1.3, y + d + 1.1), iso(x + .5, y + d + 1.1)]
    return poly(ps, "#000", 'opacity=".45" filter="url(#soft)"' if blur else 'opacity=".3"')


def text(x, y, s, size=12, fill="#e6edf7", anchor="start", weight=400, extra=""):
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" fill="{fill}" text-anchor="{anchor}" '
            f'font-weight="{weight}" {extra}>{s}</text>')


def panel(x, y, w, h, accent="#3a4d80", r=14):
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="url(#glass)" stroke="{accent}" '
            f'stroke-opacity=".7" stroke-width="1.4"/>'
            f'<rect x="{x+1}" y="{y+1}" width="{w-2}" height="2" rx="1" fill="#fff" opacity=".12"/>')


DEFS = f"""
<defs>
 <radialGradient id="sky" cx="50%" cy="35%" r="80%"><stop offset="0" stop-color="#22305e"/><stop offset=".55" stop-color="#101833"/><stop offset="1" stop-color="#05070f"/></radialGradient>
 <radialGradient id="vig" cx="50%" cy="50%" r="70%"><stop offset=".6" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity=".7"/></radialGradient>
 <linearGradient id="floorTop" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#1b2a52"/><stop offset="1" stop-color="#0e1832"/></linearGradient>
 <linearGradient id="sheen" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff" stop-opacity=".22"/><stop offset=".5" stop-color="#fff" stop-opacity="0"/></linearGradient>
 <linearGradient id="glass" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#152042" stop-opacity=".92"/><stop offset="1" stop-color="#0a1027" stop-opacity=".92"/></linearGradient>
 <linearGradient id="beam" x1="0" y1="1" x2="0" y2="0"><stop offset="0" stop-color="{CYAN}" stop-opacity=".75"/><stop offset="1" stop-color="{CYAN}" stop-opacity="0"/></linearGradient>
 <linearGradient id="beamRed" x1="0" y1="1" x2="0" y2="0"><stop offset="0" stop-color="{RED}" stop-opacity=".55"/><stop offset="1" stop-color="{RED}" stop-opacity="0"/></linearGradient>
 <linearGradient id="lh" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#fff6c2" stop-opacity=".55"/><stop offset="1" stop-color="#fff6c2" stop-opacity="0"/></linearGradient>
 <linearGradient id="road" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{CYAN}"/><stop offset="1" stop-color="#8a6bff"/></linearGradient>
 <filter id="soft" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="7"/></filter>
 <filter id="glow" x="-60%" y="-60%" width="220%" height="220%"><feGaussianBlur stdDeviation="3.5" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
 <filter id="bigglow" x="-100%" y="-100%" width="300%" height="300%"><feGaussianBlur stdDeviation="10"/></filter>
</defs>"""


STAGES = [
    # name, colour, cases, (amber, red), pad, kind
    ("Mandate Intake", "#4f86ff", 14, (1, 0), (1, 1), "gate"),
    ("Info Gathering", "#8b6bff", 31, (5, 6), (8, 1), "archive"),
    ("Analysis Lab", "#22c3e6", 38, (6, 3), (15, 1), "radar"),
    ("Mgmt Meeting", "#d86bff", 17, (3, 2), (19, 7), "pavilion"),
    ("Rating Committee", "#ff8a3d", 9, (1, 2), (15, 12), "dome"),
    ("Letter &amp; Acceptance", "#f2cf3a", 12, (2, 1), (8, 12), "antenna"),
    ("Published", "#2fe39a", 21, (0, 0), (1, 12), "lighthouse"),
]
PATH = [(3, 3), (10, 3), (17, 3), (21, 9), (17, 14), (10, 14), (3, 14)]


def building(kind, px, py, col):
    """Return (svg, top_z) for a stage building on a 4x4 pad at (px, py)."""
    o = []
    bx, by = px + .4, py + .4
    if kind == "gate":
        o.append(box(bx, by, .3, .6, 1.8, 2.6, col)); o.append(box(bx + 1.4, by, .3, .6, 1.8, 2.6, col))
        o.append(box(bx, by, 2.9, 2.0, 1.8, .6, shade(col, 1.2)))
        cx, cy = iso(bx + 1.0, by + .9, 3.8)
        o.append(f'<polygon points="{cx},{cy-26} {cx+16},{cy-20} {cx},{cy-14}" fill="{col}"><animate attributeName="points" dur="1.4s" repeatCount="indefinite" values="{cx},{cy-26} {cx+16},{cy-20} {cx},{cy-14};{cx},{cy-26} {cx+13},{cy-17} {cx},{cy-14};{cx},{cy-26} {cx+16},{cy-20} {cx},{cy-14}"/></polygon>')
        o.append(f'<line x1="{cx}" y1="{cy}" x2="{cx}" y2="{cy-27}" stroke="#cfd8ea" stroke-width="2"/>')
        return "".join(o), 4.2
    if kind == "archive":
        for k in range(3):
            o.append(box(bx + k * .7, by, .3, .55, 2.2, 2.2 + k * .6, col))
        for k in range(4):
            cx, cy = iso(bx + 1.0, by + 1.0, 3.6)
            dx = (k - 1.5) * 14
            o.append(f'<rect x="{cx+dx-5:.1f}" y="{cy:.1f}" width="10" height="13" rx="1.5" fill="#fff" opacity="0">'
                     f'<animate attributeName="y" from="{cy:.1f}" to="{cy-50:.1f}" dur="3s" begin="{k*.7}s" repeatCount="indefinite"/>'
                     f'<animate attributeName="opacity" values="0;.9;0" dur="3s" begin="{k*.7}s" repeatCount="indefinite"/></rect>')
        return "".join(o), 4.4
    if kind == "radar":
        o.append(box(bx, by, .3, 2.0, 2.0, 1.4, col)); o.append(box(bx + .5, by + .5, 1.7, 1.0, 1.0, 2.8, shade(col, 1.1)))
        cx, cy = iso(bx + 1.0, by + 1.0, 4.9)
        o.append(f'<line x1="{cx}" y1="{cy+6}" x2="{cx}" y2="{cy-6}" stroke="#cfd8ea" stroke-width="3"/>')
        o.append(f'<ellipse cx="{cx}" cy="{cy-10}" rx="22" ry="9" fill="#e9f6ff" stroke="{col}" stroke-width="2">'
                 f'<animate attributeName="rx" values="22;3;22" dur="2.4s" repeatCount="indefinite"/></ellipse>')
        o.append(f'<circle cx="{cx}" cy="{cy-10}" r="3" fill="{RED}" filter="url(#glow)"><animate attributeName="opacity" values="1;.2;1" dur="1s" repeatCount="indefinite"/></circle>')
        return "".join(o), 5.6
    if kind == "pavilion":
        o.append(box(bx, by, .3, 2.2, 2.2, .3, shade(col, .8)))
        o.append(box(bx + .1, by + .1, .6, 2.0, 2.0, 1.6, "#9fe8ff", op=.38))
        cx, cy = iso(bx + 1.1, by + 1.1, 1.3)
        o.append(f'<ellipse cx="{cx}" cy="{cy}" rx="22" ry="11" fill="{col}" opacity=".7" filter="url(#glow)"/>')
        for a in range(4):
            ax, ay = iso(bx + .5 + (a % 2) * 1.1, by + .5 + (a // 2) * 1.1, .6)
            o.append(f'<circle cx="{ax:.1f}" cy="{ay-8:.1f}" r="4" fill="#f2d3b3"/><rect x="{ax-4:.1f}" y="{ay-4:.1f}" width="8" height="9" rx="3" fill="#e6edf7"/>')
        o.append(box(bx - .1, by - .1, 2.2, 2.4, 2.4, .25, col))
        return "".join(o), 3.2
    if kind == "dome":
        o.append(box(bx, by, .3, 2.4, 2.4, 1.6, col))
        cx, cy = iso(bx + 1.2, by + 1.2, 1.9)
        o.append(f'<path d="M{cx-38},{cy} A38,34 0 0 1 {cx+38},{cy} Z" fill="{shade(col, 1.15)}" stroke="#fff" stroke-opacity=".3"/>')
        o.append(f'<path d="M{cx-24},{cy-6} A26,24 0 0 1 {cx+6},{cy-30}" fill="none" stroke="#fff" stroke-opacity=".45" stroke-width="3"/>')
        for k, r in enumerate((52, 66)):
            o.append(f'<ellipse cx="{cx}" cy="{cy-50}" rx="{r}" ry="{r*.32:.0f}" fill="none" stroke="{CYAN}" stroke-width="1.6" stroke-dasharray="10 8" opacity=".85">'
                     f'<animate attributeName="stroke-dashoffset" from="0" to="{-72 if k else 72}" dur="{3+k}s" repeatCount="indefinite"/></ellipse>')
        return "".join(o), 4.6
    if kind == "antenna":
        o.append(box(bx, by, .3, 2.2, 1.8, 1.8, col)); o.append(box(bx + .2, by + .2, 2.1, 1.8, 1.4, .3, shade(col, .7)))
        cx, cy = iso(bx + 1.6, by + .8, 2.4)
        o.append(f'<line x1="{cx}" y1="{cy}" x2="{cx}" y2="{cy-46}" stroke="#cfd8ea" stroke-width="2.5"/>')
        for k in range(3):
            o.append(f'<circle cx="{cx}" cy="{cy-46}" r="4" fill="none" stroke="{col}" stroke-width="2">'
                     f'<animate attributeName="r" from="4" to="40" dur="2.4s" begin="{k*.8}s" repeatCount="indefinite"/>'
                     f'<animate attributeName="opacity" from="1" to="0" dur="2.4s" begin="{k*.8}s" repeatCount="indefinite"/></circle>')
        return "".join(o), 4.8
    # lighthouse
    o.append(box(bx + .4, by + .4, .3, 1.2, 1.2, 4.0, "#e9eef8"))
    for k in range(2):
        o.append(box(bx + .38, by + .38, .9 + k * 1.4, 1.24, 1.24, .45, col, edge=False))
    o.append(box(bx + .3, by + .3, 4.3, 1.4, 1.4, .7, "#fff6c2", op=.9))
    cx, cy = iso(bx + 1.0, by + 1.0, 4.65)
    o.append(f'<g><polygon points="{cx},{cy} {cx+260},{cy-40} {cx+260},{cy+40}" fill="url(#lh)"/>'
             f'<animateTransform attributeName="transform" type="rotate" from="0 {cx} {cy}" to="360 {cx} {cy}" dur="7s" repeatCount="indefinite"/></g>')
    o.append(f'<circle cx="{cx}" cy="{cy}" r="9" fill="#fff6c2" filter="url(#glow)"/>')
    return "".join(o), 5.4


def tree(x, y, s=1.0):
    cx, cy = iso(x, y)
    g = random.choice(["#1fa36b", "#21b878", "#178a5a"])
    return (f'<ellipse cx="{cx:.1f}" cy="{cy:.1f}" rx="{10*s:.1f}" ry="{5*s:.1f}" fill="#000" opacity=".35"/>'
            f'<rect x="{cx-1.5:.1f}" y="{cy-10*s:.1f}" width="3" height="{10*s:.1f}" fill="#6b4a2b"/>'
            f'<polygon points="{cx:.1f},{cy-38*s:.1f} {cx+11*s:.1f},{cy-8*s:.1f} {cx-11*s:.1f},{cy-8*s:.1f}" fill="{g}"/>'
            f'<polygon points="{cx:.1f},{cy-38*s:.1f} {cx+11*s:.1f},{cy-8*s:.1f} {cx:.1f},{cy-8*s:.1f}" fill="#000" opacity=".18"/>')


def lamp(x, y):
    cx, cy = iso(x, y)
    return (f'<line x1="{cx:.1f}" y1="{cy:.1f}" x2="{cx:.1f}" y2="{cy-30:.1f}" stroke="#8090b0" stroke-width="2"/>'
            f'<circle cx="{cx:.1f}" cy="{cy-31:.1f}" r="10" fill="#ffe9a8" opacity=".35" filter="url(#bigglow)"/>'
            f'<circle cx="{cx:.1f}" cy="{cy-31:.1f}" r="3" fill="#fff3c4"/>')


def walker(path_pts, dur, delay=0):
    d = "M" + " L".join(f"{a:.1f},{b:.1f}" for a, b in path_pts) + " Z"
    return (f'<g><ellipse cx="0" cy="0" rx="5" ry="2.5" fill="#000" opacity=".35"/>'
            f'<rect x="-3.5" y="-14" width="7" height="11" rx="3" fill="#e6edf7"/><circle cx="0" cy="-18" r="4" fill="#f2d3b3"/>'
            f'<animateMotion path="{d}" dur="{dur}s" begin="{delay}s" repeatCount="indefinite"/></g>')


def health_bar(cx, cy, n, amb, red):
    w = 92
    g = n - amb - red
    s = f'<rect x="{cx-w/2-2:.1f}" y="{cy-2:.1f}" width="{w+4}" height="10" rx="5" fill="#05070f" stroke="#ffffff" stroke-opacity=".25"/>'
    x = cx - w / 2
    for v, c in ((g, GREEN), (amb, AMBER), (red, RED)):
        if not v: continue
        ww = w * v / n
        s += f'<rect x="{x:.1f}" y="{cy:.1f}" width="{ww:.1f}" height="6" rx="3" fill="{c}"/>'
        x += ww
    return s


def hexagon(cx, cy, r, fill, stroke):
    p = [(cx + r * math.cos(math.radians(60 * i - 30)), cy + r * math.sin(math.radians(60 * i - 30))) for i in range(6)]
    return poly(p, fill, f'stroke="{stroke}" stroke-width="2"')


def scene():
    o = [f'<rect width="{W}" height="{H}" fill="url(#sky)"/>']
    for _ in range(140):
        x, y, r = random.uniform(0, W), random.uniform(0, H * .6), random.uniform(.4, 1.6)
        o.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{r:.1f}" fill="#fff" opacity="{random.uniform(.15,.7):.2f}">'
                 + (f'<animate attributeName="opacity" values=".1;.8;.1" dur="{random.uniform(2,5):.1f}s" repeatCount="indefinite"/>' if r > 1.2 else "")
                 + "</circle>")
    # island slab
    x0, y0, x1, y1, th = -1, -1, 25, 19, 1.4
    o.append(poly([iso(x0, y1, -th), iso(x1, y1, -th), iso(x1, y0, -th), iso(x1, y0), iso(x1, y1), iso(x0, y1)], "#000", 'opacity=".5" filter="url(#bigglow)"'))
    o.append(poly([iso(x0, y1, 0), iso(x1, y1, 0), iso(x1, y1, -th), iso(x0, y1, -th)], "#0c1530"))
    o.append(poly([iso(x1, y0, 0), iso(x1, y1, 0), iso(x1, y1, -th), iso(x1, y0, -th)], "#13204a"))
    o.append(poly([iso(x0, y0), iso(x1, y0), iso(x1, y1), iso(x0, y1)], "url(#floorTop)"))
    for i in range(x0, x1 + 1):
        a, b = iso(i, y0), iso(i, y1)
        o.append(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}" stroke="#2a3d73" stroke-opacity=".35"/>')
    for j in range(y0, y1 + 1):
        a, b = iso(x0, j), iso(x1, j)
        o.append(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}" stroke="#2a3d73" stroke-opacity=".35"/>')
    edge = [iso(x0, y0), iso(x1, y0), iso(x1, y1), iso(x0, y1)]
    o.append(f'<polygon points="{pts(edge)}" fill="none" stroke="{CYAN}" stroke-width="2" opacity=".55" filter="url(#glow)"/>')
    # ground decals: office name
    a = iso(12, 8.6)
    o.append(text(a[0], a[1], "MUMBAI HQ", 46, "#ffffff", "middle", 900,
                  f'opacity=".05" letter-spacing="10" transform="rotate(0)"'))
    # roads / conveyor
    road = [iso(a, b, .02) for a, b in PATH]
    d = "M" + " L".join(f"{a:.1f},{b:.1f}" for a, b in road)
    o.append(f'<path d="{d}" fill="none" stroke="#070c1c" stroke-width="30" stroke-linejoin="round" stroke-linecap="round"/>')
    o.append(f'<path d="{d}" fill="none" stroke="#1a2a55" stroke-width="24" stroke-linejoin="round" stroke-linecap="round"/>')
    o.append(f'<path d="{d}" fill="none" stroke="url(#road)" stroke-width="3" stroke-dasharray="14 12" filter="url(#glow)" opacity=".9">'
             f'<animate attributeName="stroke-dashoffset" from="0" to="-52" dur="1.2s" repeatCount="indefinite"/></path>')
    # scenery
    for (tx, ty) in [(-0.3, 6), (0.2, 8), (-0.5, 9.5), (6.5, 7), (7.3, 8.6), (12, 6.5), (13, 9), (12.4, 10.6), (23.5, 2), (24, 4),
                     (23.8, 15), (22.5, 17.5), (6, 18.3), (12.5, 18.4), (-0.4, 17.6), (18.5, -.4), (4.8, -.5)]:
        o.append(tree(tx, ty, random.uniform(.8, 1.2)))
    for (lx, ly) in [(6, 4), (13, 4), (19, 5), (19.5, 12.5), (13, 15.5), (6, 15.5)]:
        o.append(lamp(lx, ly))
    # crates riding the conveyor
    k = K
    crate_cols = [GREEN, GREEN, AMBER, GREEN, RED, GREEN, AMBER, GREEN, GREEN, AMBER, GREEN, GREEN]
    for i, c in enumerate(crate_cols):
        cr = box(-.32, -.32, 0, .64, .64, .55, c, (0, 0, k))
        glow = f'<circle cx="0" cy="-8" r="12" fill="{c}" opacity=".35" filter="url(#bigglow)"/>' if c == RED else ""
        o.append(f'<g>{glow}{cr}<animateMotion path="{d}" dur="26s" begin="-{i*26/len(crate_cols):.2f}s" repeatCount="indefinite"/></g>')
    # stage pads, drawn back to front
    order = sorted(range(len(STAGES)), key=lambda i: STAGES[i][4][0] + STAGES[i][4][1])
    labels, select_xy = [], None
    for i in order:
        name, col, n, (amb, red), (px, py), kind = STAGES[i]
        o.append(shadow(px, py, 4, 4))
        o.append(box(px, py, 0, 4, 4, .3, shade(col, .35), top=shade(col, .45)))
        pad = [iso(px + .15, py + .15, .31), iso(px + 3.85, py + .15, .31), iso(px + 3.85, py + 3.85, .31), iso(px + .15, py + 3.85, .31)]
        o.append(f'<polygon points="{pts(pad)}" fill="none" stroke="{col}" stroke-width="1.5" opacity=".8" filter="url(#glow)"/>')
        b, topz = building(kind, px, py, col)
        o.append(b)
        # crates stacked on the pad
        cols = [RED] * red + [AMBER] * amb + [GREEN] * (n - amb - red)
        for idx, cc in enumerate(cols[:30]):
            s = idx % 15
            sx, sy, sz = px + 2.75 + (s % 2) * .55, py + .35 + (s // 2) * .48, .3 + (idx // 15) * .46
            if sy > py + 3.6: continue
            o.append(box(sx, sy, sz, .44, .44, .42, cc))
        # alert marker
        if red:
            ax, ay = iso(px + 1.4, py + 1.4, topz + 1.6)
            o.append(f'<g><circle cx="{ax:.1f}" cy="{ay:.1f}" r="16" fill="{RED}" opacity=".4" filter="url(#bigglow)"/>'
                     f'<path d="M{ax:.1f},{ay-15:.1f} L{ax+13:.1f},{ay+9:.1f} L{ax-13:.1f},{ay+9:.1f} Z" fill="{RED}" stroke="#fff" stroke-width="1.5"/>'
                     + text(ax, ay + 6, "!", 15, "#fff", "middle", 900)
                     + f'<animateTransform attributeName="transform" type="translate" values="0 0;0 -7;0 0" dur="1.3s" repeatCount="indefinite"/></g>')
        lx, ly = iso(px + 2, py + 2, topz + 2.7)
        labels.append((lx, ly, i, name, col, n, amb, red))
        if kind == "dome":
            select_xy = iso(px + 3.0, py + 1.0, .75)
    # floating labels on top of everything
    for lx, ly, i, name, col, n, amb, red in labels:
        w = 150 + len(name) * 3.2
        o.append(f'<line x1="{lx:.1f}" y1="{ly+16:.1f}" x2="{lx:.1f}" y2="{ly+34:.1f}" stroke="{col}" stroke-width="1.5" opacity=".7"/>')
        o.append(f'<rect x="{lx-w/2:.1f}" y="{ly-26:.1f}" width="{w:.1f}" height="44" rx="10" fill="#0a1027" fill-opacity=".9" stroke="{col}" stroke-width="1.6"/>')
        o.append(hexagon(lx - w / 2 + 4, ly - 4, 15, col, "#0a1027"))
        o.append(text(lx - w / 2 + 4, ly + 1, str(i + 1), 13, "#0a1027", "middle", 900))
        o.append(text(lx - w / 2 + 26, ly - 8, name.upper().replace("&AMP;", "&amp;"), 11.5, "#fff", weight=800, extra='letter-spacing=".6"'))
        o.append(text(lx + w / 2 - 10, ly - 8, str(n), 13, col, "end", 900))
        o.append(health_bar(lx + 10, ly + 2, n, amb, red))
    # selected case: light beam + rotating ring
    sx, sy = select_xy
    o.append(f'<rect x="{sx-12:.1f}" y="{sy-260:.1f}" width="24" height="260" fill="url(#beam)" opacity=".85"><animate attributeName="opacity" values=".55;.95;.55" dur="2s" repeatCount="indefinite"/></rect>')
    o.append(f'<ellipse cx="{sx:.1f}" cy="{sy:.1f}" rx="30" ry="15" fill="none" stroke="{CYAN}" stroke-width="3" stroke-dasharray="14 8" filter="url(#glow)">'
             f'<animate attributeName="stroke-dashoffset" from="0" to="44" dur="1s" repeatCount="indefinite"/></ellipse>')
    o.append(f'<ellipse cx="{sx:.1f}" cy="{sy:.1f}" rx="30" ry="15" fill="none" stroke="{CYAN}" stroke-width="2"><animate attributeName="rx" from="30" to="60" dur="1.6s" repeatCount="indefinite"/><animate attributeName="ry" from="15" to="30" dur="1.6s" repeatCount="indefinite"/><animate attributeName="opacity" from=".9" to="0" dur="1.6s" repeatCount="indefinite"/></ellipse>')
    o.append(f'<path d="M{sx+30:.1f},{sy-6:.1f} C{sx+140:.1f},{sy-30:.1f} 1500,{sy-120:.1f} 1560,{sy-150:.1f}" fill="none" stroke="{CYAN}" stroke-width="1.5" stroke-dasharray="4 5" opacity=".8"/>')
    # analysts walking between buildings
    o.append(walker([iso(4, 5.2), iso(9, 5.2), iso(9, 4.8), iso(4, 4.8)], 9))
    o.append(walker([iso(18.5, 5.5), iso(20.5, 10.5), iso(19.5, 11), iso(18, 6)], 11, 2))
    o.append(walker([iso(11, 16), iso(15, 16), iso(15, 16.4), iso(11, 16.4)], 8, 1))
    o.append(walker([iso(4.5, 10.5), iso(9, 10.5), iso(9, 11), iso(4.5, 11)], 10, 4))
    o.append(f'<rect width="{W}" height="{H}" fill="url(#vig)" pointer-events="none"/>')
    return "".join(o)


def bar(x, y, w, frac, col, label, val):
    return (text(x, y, label, 11, "#8fa2c8", weight=600) + text(x + w, y, val, 11, "#fff", "end", 700)
            + f'<rect x="{x}" y="{y+6}" width="{w}" height="7" rx="3.5" fill="#05070f" stroke="#2a3d73"/>'
            + f'<rect x="{x}" y="{y+6}" width="{w*min(frac,1):.1f}" height="7" rx="3.5" fill="{col}" filter="url(#glow)"/>')


def hud():
    o = []
    # top resource bar
    o.append(f'<rect x="0" y="0" width="{W}" height="70" fill="#060a18" opacity=".85"/><line x1="0" y1="70" x2="{W}" y2="70" stroke="{CYAN}" stroke-opacity=".35"/>')
    o.append(hexagon(44, 35, 22, "#ff8a3d", "#ffd2a8") + text(44, 41, "A", 18, "#0a1027", "middle", 900))
    o.append(text(78, 32, "ACER", 20, "#fff", weight=900, extra='letter-spacing="2"') + text(78, 52, "RATING OPS · CASE FLOOR", 11, "#8fa2c8", weight=700, extra='letter-spacing="1.5"'))
    res = [("◆", "MANDATES", "142", CYAN), ("⚠", "OVERDUE", "9", RED), ("◔", "AT RISK", "18", AMBER),
           ("⏱", "AVG TAT", "17.4d", "#fff"), ("⚖", "COMMITTEE", "6 this wk", "#ff8a3d"), ("★", "PUBLISHED", "21 MTD", GREEN)]
    x = 340
    for ic, lab, val, c in res:
        w = 168
        o.append(f'<rect x="{x}" y="14" width="{w}" height="42" rx="21" fill="#0d1531" stroke="{c}" stroke-opacity=".55"/>')
        o.append(f'<circle cx="{x+21}" cy="35" r="14" fill="{c}" opacity=".18"/>' + text(x + 21, 40, ic, 14, c, "middle", 700))
        o.append(text(x + 42, 31, lab, 9.5, "#8fa2c8", weight=800, extra='letter-spacing="1"') + text(x + 42, 48, val, 15, c, weight=800))
        x += w + 10
    o.append(text(W - 24, 32, "TUE 06 OCT · 10:42 IST", 12, "#fff", "end", 800, 'letter-spacing="1"'))
    o.append(f'<circle cx="{W-150}" cy="48" r="4" fill="{RED}"><animate attributeName="opacity" values="1;.2;1" dur="1s" repeatCount="indefinite"/></circle>' + text(W - 24, 52, "LIVE · Zoho synced 12s ago", 11, "#8fa2c8", "end", 600))
    # objectives (quest log)
    o.append(panel(20, 90, 330, 300, "#ffc247"))
    o.append(text(38, 118, "⚑ TODAY'S OBJECTIVES", 12, AMBER, weight=900, extra='letter-spacing="1"'))
    quests = [("Clear 6 overdue in Info Gathering", 2 / 6, AMBER, "2/6"), ("Close committee minutes (3)", 1 / 3, CYAN, "1/3"),
              ("Publish 4 rating PRs", 3 / 4, GREEN, "3/4"), ("Onboard 2 new mandates", 1, GREEN, "2/2 ✓")]
    for k, (q, f, c, v) in enumerate(quests):
        o.append(bar(38, 148 + k * 56, 294, f, c, q, v))
    o.append(f'<rect x="38" y="364" width="294" height="1" fill="#2a3d73"/>' + text(38, 382, "Team XP this week: 1,240 · Streak 5 days 🔥", 11, "#cfd8ea", weight=600))
    # office switcher
    o.append(panel(20, 404, 330, 152))
    o.append(text(38, 430, "OFFICES", 11, "#8fa2c8", weight=900, extra='letter-spacing="1.5"'))
    for k, (nme, c, on, alert) in enumerate([("Mumbai HQ", 88, True, 7), ("New Delhi", 41, False, 2), ("Kolkata", 13, False, 0)]):
        y = 442 + k * 36
        o.append(f'<rect x="34" y="{y}" width="302" height="30" rx="8" fill="{"#1b2a5c" if on else "#0d1531"}" stroke="{CYAN if on else "#22305e"}"/>')
        o.append(text(48, y + 20, nme, 13, "#fff", weight=700 if on else 500) + text(290, y + 20, str(c), 13, "#cfd8ea", "end", 700))
        if alert:
            o.append(f'<circle cx="316" cy="{y+15}" r="9" fill="{RED}"/>' + text(316, y + 19, str(alert), 10, "#fff", "middle", 900))
    # minimap
    o.append(panel(20, 790, 330, 270))
    o.append(text(38, 816, "MINIMAP", 11, "#8fa2c8", weight=900, extra='letter-spacing="1.5"'))
    mo = (185, 845, 5.6)
    mm = [iso(-1, -1, 0, *mo), iso(25, -1, 0, *mo), iso(25, 19, 0, *mo), iso(-1, 19, 0, *mo)]
    o.append(f'<polygon points="{pts(mm)}" fill="#0f1a3a" stroke="{CYAN}" stroke-opacity=".6"/>')
    rp = [iso(a, b, 0, *mo) for a, b in PATH]
    o.append(f'<polyline points="{pts(rp)}" fill="none" stroke="{CYAN}" stroke-width="1.5" opacity=".7"/>')
    for name, col, n, (amb, red), (px, py), _ in STAGES:
        cx, cy = iso(px + 2, py + 2, 0, *mo)
        o.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{4 + n/8:.1f}" fill="{col}" opacity=".9"/>')
        if red:
            o.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="6" fill="none" stroke="{RED}" stroke-width="2"><animate attributeName="r" from="6" to="16" dur="1.5s" repeatCount="indefinite"/><animate attributeName="opacity" from="1" to="0" dur="1.5s" repeatCount="indefinite"/></circle>')
    view = [iso(2, 0, 0, *mo), iso(22, 0, 0, *mo), iso(22, 17, 0, *mo), iso(2, 17, 0, *mo)]
    o.append(f'<polygon points="{pts(view)}" fill="none" stroke="#fff" stroke-width="1.2" stroke-dasharray="4 3" opacity=".6"/>')
    # selected unit card (right)
    x0, y0, w0 = 1560, 90, 340
    o.append(panel(x0, y0, w0, 610, CYAN))
    o.append(hexagon(x0 + 50, y0 + 58, 34, "#1b2a5c", CYAN) + text(x0 + 50, y0 + 66, "SI", 22, CYAN, "middle", 900))
    o.append(text(x0 + 96, y0 + 40, "ACR/2026/0847", 11, CYAN, weight=800, extra='letter-spacing="1"'))
    o.append(text(x0 + 96, y0 + 62, "Shreeji Infra Projects", 17, "#fff", weight=800))
    o.append(text(x0 + 96, y0 + 82, "Bank Loan · ₹450 Cr · Initial", 12, "#8fa2c8", weight=600))
    o.append(f'<rect x="{x0+20}" y="{y0+108}" width="96" height="24" rx="12" fill="{RED}" fill-opacity=".2" stroke="{RED}"/>' + text(x0 + 68, y0 + 124, "OVERDUE 3d", 10.5, RED, "middle", 900))
    o.append(f'<rect x="{x0+124}" y="{y0+108}" width="134" height="24" rx="12" fill="#ff8a3d" fill-opacity=".2" stroke="#ff8a3d"/>' + text(x0 + 191, y0 + 124, "⚖ RATING COMMITTEE", 10.5, "#ff8a3d", "middle", 900))
    o.append(text(x0 + 20, y0 + 168, "CASE VITALS", 11, "#8fa2c8", weight=900, extra='letter-spacing="1.5"'))
    for k, (lab, f, c, v) in enumerate([("TAT used", 1.0, RED, "112%"), ("Documents received", 9 / 12, AMBER, "9 / 12"),
                                         ("Committee readiness", .8, CYAN, "80%"), ("Fee collected", 1.0, GREEN, "Paid")]):
        o.append(bar(x0 + 20, y0 + 194 + k * 44, w0 - 40, f, c, lab, v))
    o.append(text(x0 + 20, y0 + 392, "PARTY", 11, "#8fa2c8", weight=900, extra='letter-spacing="1.5"'))
    for k, (ini, role, nm, c) in enumerate([("RM", "Lead analyst", "R. Mehta", "#4f86ff"), ("SI", "Reviewer", "S. Iyer", "#d86bff"), ("AK", "Chair", "A. Kapoor", "#ff8a3d")]):
        cx = x0 + 52 + k * 104
        o.append(f'<circle cx="{cx}" cy="{y0+430}" r="22" fill="{c}" fill-opacity=".25" stroke="{c}" stroke-width="2"/>' + text(cx, y0 + 435, ini, 13, "#fff", "middle", 900))
        o.append(text(cx, y0 + 468, nm, 11.5, "#fff", "middle", 700) + text(cx, y0 + 483, role, 10, "#8fa2c8", "middle"))
    o.append(text(x0 + 20, y0 + 516, "ACTIONS", 11, "#8fa2c8", weight=900, extra='letter-spacing="1.5"'))
    for k, (ic, lab, key) in enumerate([("↗", "Zoho", "Q"), ("⇄", "Reassign", "W"), ("✉", "Nudge", "E"), ("⚡", "Escalate", "R")]):
        bx = x0 + 20 + k * 77
        o.append(f'<rect x="{bx}" y="{y0+530}" width="68" height="62" rx="10" fill="#0d1531" stroke="{CYAN if k == 0 else "#2a3d73"}"/>')
        o.append(text(bx + 34, y0 + 560, ic, 20, CYAN if k == 0 else "#cfd8ea", "middle", 700) + text(bx + 34, y0 + 582, lab, 10, "#cfd8ea", "middle", 700))
        o.append(f'<rect x="{bx+50}" y="{y0+534}" width="14" height="14" rx="3" fill="#22305e"/>' + text(bx + 57, y0 + 545, key, 9, "#fff", "middle", 900))
    # event feed
    o.append(panel(1560, 716, 340, 344))
    o.append(text(1578, 742, "EVENT LOG", 11, "#8fa2c8", weight=900, extra='letter-spacing="1.5"'))
    feed = [("10:42", "ACR/0851 advanced to Mgmt Meeting", CYAN, "▲"), ("10:31", "ACR/0812 rating letter accepted", GREEN, "✓"),
            ("10:18", "ACR/0847 crossed TAT threshold", RED, "!"), ("09:55", "New mandate · Kavya Textiles NCD ₹120 Cr", "#4f86ff", "+"),
            ("09:40", "Committee slot booked · 08 Oct 11:00", "#ff8a3d", "⚖"), ("09:12", "ACR/0790 published · ACER A- / Stable", GREEN, "★")]
    for k, (t, msg, c, ic) in enumerate(feed):
        y = 770 + k * 46
        o.append(f'<circle cx="1592" cy="{y+4}" r="11" fill="{c}" fill-opacity=".2" stroke="{c}"/>' + text(1592, y + 9, ic, 11, c, "middle", 900))
        o.append(text(1612, y, t, 10.5, "#8fa2c8", weight=700) + text(1612, y + 16, msg, 11.5, "#e6edf7", weight=600))
    # controls hint
    o.append(text(960, 1062, "🖱 drag orbit · scroll zoom · click any building, crate or analyst · [1-7] jump to stage · [Space] pause sim",
                  12, "#8fa2c8", "middle", 600))
    return "".join(o)


svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" '
       f'font-family="Inter, Segoe UI, Helvetica, Arial, sans-serif">{DEFS}{scene()}{hud()}</svg>')
with open(OUT, "w") as fh:
    fh.write(svg)
print("wrote", os.path.basename(OUT), len(svg) // 1024, "KB")
