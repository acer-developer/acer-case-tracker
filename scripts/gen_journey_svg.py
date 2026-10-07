"""ACER case journey: flat isometric office illustration (original artwork)."""
import math, os

OUT = os.path.join(os.path.dirname(__file__), "..", "docs", "mockups", "acer-journey.svg")
W, H = 1920, 1120
K = 30
OX, OY = 985, 270
C, S = math.cos(math.radians(30)), math.sin(math.radians(30))
U = K / 27  # person scale

TEAL, TEAL_D = "#3AA4A9", "#2D6A67"
BG = "#dcedf4"
WALL_F, WALL_S, WALL_T = "#a9d5e5", "#8cc4d8", "#ffffff"
FLOOR, SLAB = "#fbfdfe", "#7cb8cf"
DESK_T, DESK_L, DESK_R = "#eef0f2", "#c3c8ce", "#d6dade"
CHAIR = "#5b6068"
SKIN = "#f2c8a5"
INK = "#2f3a44"


def iso(x, y, z=0):
    return OX + (x - y) * C * K, OY + (x + y) * S * K - z * K


def P(ps):
    return " ".join(f"{a:.1f},{b:.1f}" for a, b in ps)


def poly(ps, fill, extra=""):
    return f'<polygon points="{P(ps)}" fill="{fill}" {extra}/>'


def box(x, y, z, w, d, h, top, left, right, extra=""):
    f = iso
    t = [f(x, y, z+h), f(x+w, y, z+h), f(x+w, y+d, z+h), f(x, y+d, z+h)]
    l = [f(x, y+d, z), f(x+w, y+d, z), f(x+w, y+d, z+h), f(x, y+d, z+h)]
    r = [f(x+w, y, z), f(x+w, y+d, z), f(x+w, y+d, z+h), f(x+w, y, z+h)]
    return poly(l, left, extra) + poly(r, right, extra) + poly(t, top, extra)


def text(x, y, s, size=13, fill=INK, anchor="start", weight=500, extra=""):
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" fill="{fill}" text-anchor="{anchor}" '
            f'font-weight="{weight}" {extra}>{s}</text>')


# ---------------------------------------------------------------- scene objects
items = []  # (depth, svg)


def add(depth, svg):
    items.append((depth, svg))


def wall_x(x0, x1, y, h, t=0.25, door=None, windows=()):
    """Wall running along x at plane y (back wall of rooms in front of it)."""
    xs = x0
    while xs < x1 - 1e-6:
        xe = min(xs + 1, x1)
        if door and any(a < xs + .5 < b for a, b in (door if isinstance(door[0], tuple) else [door])):
            xs = xe; continue
        add(xe + y + t - .01, box(xs, y, 0, xe - xs, t, h, WALL_T, WALL_F, WALL_S))
        xs = xe
    for (wx, ww) in windows:
        a, b = wx, wx + ww
        ps = [iso(a, y + t, .9), iso(b, y + t, .9), iso(b, y + t, h - .45), iso(a, y + t, h - .45)]
        svg = poly(ps, "#ffffff", 'stroke="#d9e8ef" stroke-width="1.5"')
        mid = (a + b) / 2
        p1, p2 = iso(mid, y + t, .9), iso(mid, y + t, h - .45)
        svg += f'<line x1="{p1[0]:.1f}" y1="{p1[1]:.1f}" x2="{p2[0]:.1f}" y2="{p2[1]:.1f}" stroke="#d9e8ef" stroke-width="2"/>'
        cur = [iso(a, y + t, .9), iso(a + .3, y + t, .9), iso(a + .3, y + t, h - .45), iso(a, y + t, h - .45)]
        svg += poly(cur, "#e7c9cc")
        add(b + y + t, svg)


def wall_y(y0, y1, x, h, t=0.25, door=None, windows=()):
    """Wall running along y at plane x."""
    ys = y0
    while ys < y1 - 1e-6:
        ye = min(ys + 1, y1)
        if door and any(a < ys + .5 < b for a, b in (door if isinstance(door[0], tuple) else [door])):
            ys = ye; continue
        add(x + t + ye - .01, box(x, ys, 0, t, ye - ys, h, WALL_T, WALL_F, WALL_S))
        ys = ye
    for (wy, ww) in windows:
        a, b = wy, wy + ww
        ps = [iso(x + t, a, .9), iso(x + t, b, .9), iso(x + t, b, h - .45), iso(x + t, a, h - .45)]
        svg = poly(ps, "#ffffff", 'stroke="#d9e8ef" stroke-width="1.5"')
        cur = [iso(x + t, b - .3, .9), iso(x + t, b, .9), iso(x + t, b, h - .45), iso(x + t, b - .3, h - .45)]
        svg += poly(cur, "#e7c9cc")
        add(x + t + b, svg)


def slab(x, y, w, d, th=.35):
    s = poly([iso(x, y + d, 0), iso(x + w, y + d, 0), iso(x + w, y + d, -th), iso(x, y + d, -th)], SLAB)
    s += poly([iso(x + w, y, 0), iso(x + w, y + d, 0), iso(x + w, y + d, -th), iso(x + w, y, -th)], "#6aaac3")
    s += poly([iso(x, y), iso(x + w, y), iso(x + w, y + d), iso(x, y + d)], FLOOR)
    return s


def desk(x, y, w=1.6, d=.8, monitor=True, laptop=False):
    s = box(x, y, 0, w, d, .72, DESK_T, DESK_L, DESK_R)
    if monitor:
        s += box(x + w / 2 - .35, y + .1, .72, .7, .06, .48, "#4a5059", "#3a3f47", "#4a5059")
        ps = [iso(x + w / 2 - .32, y + .16, .76), iso(x + w / 2 + .32, y + .16, .76), iso(x + w / 2 + .32, y + .16, 1.16), iso(x + w / 2 - .32, y + .16, 1.16)]
        s += poly(ps, "#cfe7f2")
        s += box(x + w / 2 - .3, y + .4, .72, .6, .2, .02, "#ffffff", "#c9ced4", "#dfe3e7")
    if laptop:
        s += box(x + .2, y + .2, .72, .45, .3, .02, "#c9ced4", "#9aa1a9", "#b3b9c0")
    add(x + w / 2 + y + d / 2, s)


def papers(x, y, z=.72, col="#ffffff", n=2):
    s = ""
    for i in range(n):
        s += box(x + i * .05, y + i * .04, z + i * .015, .35, .25, .01, col, "#d5dbe0", "#e3e7ea")
    return s


def table(x, y, w, d, extra=""):
    s = box(x, y, 0, w, d, .74, DESK_T, DESK_L, DESK_R) + extra
    add(x + w / 2 + y + d / 2, s)


def plant(x, y, s=1.0):
    cx, cy = iso(x, y)
    g = (f'<ellipse cx="{cx:.1f}" cy="{cy:.1f}" rx="{9*s:.1f}" ry="{4*s:.1f}" fill="#000" opacity=".08"/>'
         f'<path d="M{cx-8*s:.1f},{cy-14*s:.1f} L{cx+8*s:.1f},{cy-14*s:.1f} L{cx+6*s:.1f},{cy:.1f} L{cx-6*s:.1f},{cy:.1f} Z" fill="#3f9bb5"/>'
         f'<ellipse cx="{cx:.1f}" cy="{cy-14*s:.1f}" rx="{8*s:.1f}" ry="{2.5*s:.1f}" fill="#2f7f96"/>')
    for ang, ln, col in [(-60, 22, "#3fae5b"), (-100, 26, "#2e9a4c"), (-130, 22, "#46b863"), (-20, 20, "#2e9a4c"), (-80, 30, "#55c06f"), (-150, 18, "#2e9a4c"), (-40, 26, "#46b863")]:
        a = math.radians(ang)
        ex, ey = cx + math.cos(a) * ln * s, cy - 14 * s + math.sin(a) * ln * s
        mx, my = cx + math.cos(a) * ln * .5 * s - 4 * s, cy - 14 * s + math.sin(a) * ln * .5 * s
        g += f'<path d="M{cx:.1f},{cy-14*s:.1f} Q{mx:.1f},{my-6*s:.1f} {ex:.1f},{ey:.1f} Q{mx+6*s:.1f},{my+2*s:.1f} {cx:.1f},{cy-14*s:.1f} Z" fill="{col}"/>'
    add(x + y, g)


def shelf(x, y, w=1.6):
    s = box(x, y, 0, w, .45, 2.1, "#f3f5f7", "#e3e7eb", "#d2d8de")
    cols = ["#7fa7d9", "#e58fa5", "#9fd3c7", "#b9a3e3", "#f2c46d", "#7fc7e8"]
    for row in range(4):
        for i in range(int(w / .18)):
            bx = x + .08 + i * .18
            if bx > x + w - .15: break
            z = .2 + row * .48
            ps = [iso(bx, y + .45, z), iso(bx + .12, y + .45, z), iso(bx + .12, y + .45, z + .36), iso(bx, y + .45, z + .36)]
            s += poly(ps, cols[(i + row) % len(cols)])
    add(x + w / 2 + y + .3, s)


def cabinet(x, y):
    s = box(x, y, 0, .7, .6, 1.2, "#eef0f2", "#c9ced4", "#dde1e5")
    for k in range(3):
        a, b = iso(x + .15, y + .6, .25 + k * .35), iso(x + .55, y + .6, .25 + k * .35)
        s += f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}" stroke="#9aa1a9" stroke-width="2"/>'
    add(x + .35 + y + .3, s)


def screen(x, y, w, z0, h, content):
    """Wall-mounted screen on a wall along x at plane y."""
    ps = [iso(x, y, z0), iso(x + w, y, z0), iso(x + w, y, z0 + h), iso(x, y, z0 + h)]
    s = poly(ps, "#3a3f47") + poly([iso(x + .08, y, z0 + .08), iso(x + w - .08, y, z0 + .08), iso(x + w - .08, y, z0 + h - .08), iso(x + .08, y, z0 + h - .08)], "#eaf6f8")
    return s + content


def water_cooler(x, y):
    s = box(x, y, 0, .5, .5, .9, "#e9edf0", "#c3c9cf", "#d7dce0")
    cx, cy = iso(x + .25, y + .25, .9)
    s += f'<path d="M{cx-9},{cy-2} L{cx-9},{cy-22} Q{cx},{cy-30} {cx+9},{cy-22} L{cx+9},{cy-2} Z" fill="#8fd0ea" opacity=".85"/>'
    add(x + y + .5, s)


# ------------------------------------------------------------------ people
SUITS = ["#3a3f47", "#4b5059", "#2f3640", "#5a6068", "#434a55"]
HAIRS = ["#2b2420", "#4a3324", "#1f1f1f", "#6b4a2b", "#3a2a20"]


def person(x, y, suit="#3a3f47", hair="#2b2420", face="front", tie=None, carry=None, skirt=False,
           arm_up=False, hand_out=False, depth_bias=0):
    sx, sy = iso(x, y)
    u = U
    trousers = "#2a2e34" if not skirt else SKIN
    g = f'<ellipse cx="{sx:.1f}" cy="{sy:.1f}" rx="{9*u:.1f}" ry="{3.6*u:.1f}" fill="#000" opacity=".1"/>'
    if skirt:
        g += f'<rect x="{sx-4.5*u:.1f}" y="{sy-14*u:.1f}" width="{3*u:.1f}" height="{13*u:.1f}" fill="{SKIN}"/>'
        g += f'<rect x="{sx+1.5*u:.1f}" y="{sy-14*u:.1f}" width="{3*u:.1f}" height="{13*u:.1f}" fill="{SKIN}"/>'
        g += f'<path d="M{sx-7*u:.1f},{sy-25*u:.1f} L{sx+7*u:.1f},{sy-25*u:.1f} L{sx+8.5*u:.1f},{sy-12*u:.1f} L{sx-8.5*u:.1f},{sy-12*u:.1f} Z" fill="{suit}"/>'
    else:
        g += f'<rect x="{sx-5.5*u:.1f}" y="{sy-23*u:.1f}" width="{4.6*u:.1f}" height="{22*u:.1f}" rx="1.5" fill="{trousers}"/>'
        g += f'<rect x="{sx+.9*u:.1f}" y="{sy-23*u:.1f}" width="{4.6*u:.1f}" height="{22*u:.1f}" rx="1.5" fill="{trousers}"/>'
    g += f'<ellipse cx="{sx-3.4*u:.1f}" cy="{sy-1*u:.1f}" rx="{3.4*u:.1f}" ry="{1.6*u:.1f}" fill="#1c1f23"/>'
    g += f'<ellipse cx="{sx+3.4*u:.1f}" cy="{sy-1*u:.1f}" rx="{3.4*u:.1f}" ry="{1.6*u:.1f}" fill="#1c1f23"/>'
    # torso
    g += f'<rect x="{sx-8*u:.1f}" y="{sy-41*u:.1f}" width="{16*u:.1f}" height="{19*u:.1f}" rx="{4*u:.1f}" fill="{suit}"/>'
    if face == "front":
        g += f'<path d="M{sx-3.2*u:.1f},{sy-41*u:.1f} L{sx+3.2*u:.1f},{sy-41*u:.1f} L{sx:.1f},{sy-33*u:.1f} Z" fill="#ffffff"/>'
        if tie:
            g += f'<path d="M{sx-1*u:.1f},{sy-39*u:.1f} L{sx+1*u:.1f},{sy-39*u:.1f} L{sx+1.4*u:.1f},{sy-31*u:.1f} L{sx:.1f},{sy-29.5*u:.1f} L{sx-1.4*u:.1f},{sy-31*u:.1f} Z" fill="{tie}"/>'
    # arms
    arm = "#00000022"
    if arm_up:
        g += f'<rect x="{sx+6.5*u:.1f}" y="{sy-56*u:.1f}" width="{4*u:.1f}" height="{17*u:.1f}" rx="{2*u:.1f}" fill="{suit}"/>'
        g += f'<circle cx="{sx+8.5*u:.1f}" cy="{sy-57*u:.1f}" r="{2.2*u:.1f}" fill="{SKIN}"/>'
    elif hand_out:
        g += f'<path d="M{sx+6*u:.1f},{sy-39*u:.1f} L{sx+15*u:.1f},{sy-29*u:.1f} L{sx+13*u:.1f},{sy-26*u:.1f} L{sx+5*u:.1f},{sy-33*u:.1f} Z" fill="{suit}"/>'
        g += f'<circle cx="{sx+15.5*u:.1f}" cy="{sy-27.5*u:.1f}" r="{2.3*u:.1f}" fill="{SKIN}"/>'
    else:
        g += f'<rect x="{sx+6*u:.1f}" y="{sy-40*u:.1f}" width="{4*u:.1f}" height="{16*u:.1f}" rx="{2*u:.1f}" fill="{suit}"/>'
        g += f'<rect x="{sx+6*u:.1f}" y="{sy-40*u:.1f}" width="{4*u:.1f}" height="{16*u:.1f}" rx="{2*u:.1f}" fill="{arm}"/>'
        g += f'<circle cx="{sx+8*u:.1f}" cy="{sy-23.5*u:.1f}" r="{2.1*u:.1f}" fill="{SKIN}"/>'
    g += f'<rect x="{sx-10*u:.1f}" y="{sy-40*u:.1f}" width="{4*u:.1f}" height="{16*u:.1f}" rx="{2*u:.1f}" fill="{suit}"/>'
    g += f'<circle cx="{sx-8*u:.1f}" cy="{sy-23.5*u:.1f}" r="{2.1*u:.1f}" fill="{SKIN}"/>'
    if carry:
        g += (f'<rect x="{sx+5*u:.1f}" y="{sy-33*u:.1f}" width="{10*u:.1f}" height="{12*u:.1f}" rx="1.2" fill="{carry}" transform="rotate(-8 {sx+10*u:.1f} {sy-27*u:.1f})"/>'
              f'<rect x="{sx+7*u:.1f}" y="{sy-30*u:.1f}" width="{6*u:.1f}" height="{1.6*u:.1f}" fill="#ffffff" opacity=".85" transform="rotate(-8 {sx+10*u:.1f} {sy-27*u:.1f})"/>')
    # head
    g += f'<rect x="{sx-2*u:.1f}" y="{sy-44*u:.1f}" width="{4*u:.1f}" height="{4*u:.1f}" fill="{SKIN}"/>'
    g += f'<circle cx="{sx:.1f}" cy="{sy-48.5*u:.1f}" r="{6*u:.1f}" fill="{SKIN}"/>'
    if face == "front":
        g += f'<path d="M{sx-6.3*u:.1f},{sy-48*u:.1f} A{6.3*u:.1f},{6.3*u:.1f} 0 0 1 {sx+6.3*u:.1f},{sy-48*u:.1f} Q{sx+2*u:.1f},{sy-51*u:.1f} {sx-6.3*u:.1f},{sy-48*u:.1f} Z" fill="{hair}"/>'
        if skirt:
            g += f'<path d="M{sx-6.3*u:.1f},{sy-49*u:.1f} Q{sx-8*u:.1f},{sy-40*u:.1f} {sx-5*u:.1f},{sy-38*u:.1f} L{sx-4*u:.1f},{sy-47*u:.1f} Z" fill="{hair}"/>'
            g += f'<path d="M{sx+6.3*u:.1f},{sy-49*u:.1f} Q{sx+8*u:.1f},{sy-40*u:.1f} {sx+5*u:.1f},{sy-38*u:.1f} L{sx+4*u:.1f},{sy-47*u:.1f} Z" fill="{hair}"/>'
    else:
        g += f'<circle cx="{sx:.1f}" cy="{sy-49*u:.1f}" r="{6.2*u:.1f}" fill="{hair}"/>'
        if skirt:
            g += f'<rect x="{sx-6*u:.1f}" y="{sy-49*u:.1f}" width="{12*u:.1f}" height="{10*u:.1f}" rx="{4*u:.1f}" fill="{hair}"/>'
    add(x + y + depth_bias, g)


def seated(x, y, suit="#3a3f47", hair="#2b2420", face="back", skirt=False, arm_up=False):
    """Seated person; 'back' faces away (desk behind on screen), 'front' faces viewer (table in front)."""
    sx, sy = iso(x, y)
    u = U
    g = f'<ellipse cx="{sx:.1f}" cy="{sy:.1f}" rx="{10*u:.1f}" ry="{4*u:.1f}" fill="#000" opacity=".1"/>'
    # chair base
    for dx in (-7, 0, 7):
        g += f'<line x1="{sx:.1f}" y1="{sy-6*u:.1f}" x2="{sx+dx*u:.1f}" y2="{sy-1*u:.1f}" stroke="#3b4047" stroke-width="{1.8*u:.1f}"/>'
        g += f'<circle cx="{sx+dx*u:.1f}" cy="{sy-1*u:.1f}" r="{1.4*u:.1f}" fill="#2a2e33"/>'
    g += f'<rect x="{sx-1*u:.1f}" y="{sy-14*u:.1f}" width="{2*u:.1f}" height="{8*u:.1f}" fill="#3b4047"/>'
    g += f'<ellipse cx="{sx:.1f}" cy="{sy-15*u:.1f}" rx="{9*u:.1f}" ry="{4*u:.1f}" fill="{CHAIR}"/>'
    if face == "front":
        g += f'<rect x="{sx-9*u:.1f}" y="{sy-46*u:.1f}" width="{18*u:.1f}" height="{30*u:.1f}" rx="{4*u:.1f}" fill="{CHAIR}"/>'
        g += f'<rect x="{sx-7*u:.1f}" y="{sy-37*u:.1f}" width="{14*u:.1f}" height="{20*u:.1f}" rx="{4*u:.1f}" fill="{suit}"/>'
        g += f'<path d="M{sx-2.8*u:.1f},{sy-37*u:.1f} L{sx+2.8*u:.1f},{sy-37*u:.1f} L{sx:.1f},{sy-30*u:.1f} Z" fill="#fff"/>'
        g += f'<rect x="{sx-6*u:.1f}" y="{sy-18*u:.1f}" width="{12*u:.1f}" height="{6*u:.1f}" rx="2" fill="{"#2a2e34" if not skirt else suit}"/>'
        if arm_up:
            g += f'<rect x="{sx+5.5*u:.1f}" y="{sy-52*u:.1f}" width="{3.6*u:.1f}" height="{17*u:.1f}" rx="{1.8*u:.1f}" fill="{suit}"/>'
            g += f'<circle cx="{sx+7.3*u:.1f}" cy="{sy-53*u:.1f}" r="{2.1*u:.1f}" fill="{SKIN}"/>'
            g += f'<rect x="{sx+3.5*u:.1f}" y="{sy-63*u:.1f}" width="{8*u:.1f}" height="{6*u:.1f}" rx="1" fill="#fff" stroke="{TEAL}" stroke-width="1.2"/>'
            g += f'<path d="M{sx+5.3*u:.1f},{sy-60*u:.1f} l{1.6*u:.1f},{1.6*u:.1f} l{3*u:.1f},{-3*u:.1f}" stroke="{TEAL}" stroke-width="1.4" fill="none"/>'
        g += f'<rect x="{sx-2*u:.1f}" y="{sy-41*u:.1f}" width="{4*u:.1f}" height="{4*u:.1f}" fill="{SKIN}"/>'
        g += f'<circle cx="{sx:.1f}" cy="{sy-45*u:.1f}" r="{5.8*u:.1f}" fill="{SKIN}"/>'
        g += f'<path d="M{sx-6.1*u:.1f},{sy-44.5*u:.1f} A{6.1*u:.1f},{6.1*u:.1f} 0 0 1 {sx+6.1*u:.1f},{sy-44.5*u:.1f} Q{sx+2*u:.1f},{sy-47.5*u:.1f} {sx-6.1*u:.1f},{sy-44.5*u:.1f} Z" fill="{hair}"/>'
        if skirt:
            g += f'<path d="M{sx-6*u:.1f},{sy-45*u:.1f} Q{sx-7.5*u:.1f},{sy-37*u:.1f} {sx-4.5*u:.1f},{sy-35*u:.1f} L{sx-4*u:.1f},{sy-44*u:.1f} Z" fill="{hair}"/>'
            g += f'<path d="M{sx+6*u:.1f},{sy-45*u:.1f} Q{sx+7.5*u:.1f},{sy-37*u:.1f} {sx+4.5*u:.1f},{sy-35*u:.1f} L{sx+4*u:.1f},{sy-44*u:.1f} Z" fill="{hair}"/>'
    else:
        g += f'<rect x="{sx-7*u:.1f}" y="{sy-38*u:.1f}" width="{14*u:.1f}" height="{22*u:.1f}" rx="{4*u:.1f}" fill="{suit}"/>'
        g += f'<rect x="{sx-2*u:.1f}" y="{sy-42*u:.1f}" width="{4*u:.1f}" height="{4*u:.1f}" fill="{SKIN}"/>'
        g += f'<circle cx="{sx:.1f}" cy="{sy-46*u:.1f}" r="{5.9*u:.1f}" fill="{hair}"/>'
        if skirt:
            g += f'<rect x="{sx-5.8*u:.1f}" y="{sy-46*u:.1f}" width="{11.6*u:.1f}" height="{10*u:.1f}" rx="{4*u:.1f}" fill="{hair}"/>'
        g += f'<rect x="{sx-9*u:.1f}" y="{sy-31*u:.1f}" width="{18*u:.1f}" height="{15*u:.1f}" rx="{4*u:.1f}" fill="{CHAIR}"/>'
    add(x + y, g)


def workstation(x, y, i=0, skirt=False):
    """Desk against the back; worker seated in front of it, seen from behind."""
    desk(x, y)
    add(x + .8 + y + .4 + .01, papers(x + 1.15, y + .45, n=2))
    seated(x + .8, y + 1.25, SUITS[i % 5], HAIRS[i % 5], "back", skirt)


def robot(x, y):
    sx, sy = iso(x, y)
    u = U * 1.05
    g = f'<ellipse cx="{sx:.1f}" cy="{sy:.1f}" rx="{11*u:.1f}" ry="{4*u:.1f}" fill="#000" opacity=".12"/>'
    g += f'<rect x="{sx-9*u:.1f}" y="{sy-9*u:.1f}" width="{18*u:.1f}" height="{7*u:.1f}" rx="{3*u:.1f}" fill="#8e98a3"/>'
    g += f'<circle cx="{sx-6*u:.1f}" cy="{sy-2.5*u:.1f}" r="{2.6*u:.1f}" fill="#2f353c"/><circle cx="{sx+6*u:.1f}" cy="{sy-2.5*u:.1f}" r="{2.6*u:.1f}" fill="#2f353c"/>'
    g += f'<rect x="{sx-1.5*u:.1f}" y="{sy-13*u:.1f}" width="{3*u:.1f}" height="{5*u:.1f}" fill="#8e98a3"/>'
    g += f'<rect x="{sx-9*u:.1f}" y="{sy-35*u:.1f}" width="{18*u:.1f}" height="{23*u:.1f}" rx="{6*u:.1f}" fill="#f5f8fa" stroke="#c9d3dc" stroke-width="1.2"/>'
    g += f'<rect x="{sx-4*u:.1f}" y="{sy-21*u:.1f}" width="{8*u:.1f}" height="{3*u:.1f}" rx="1.5" fill="{TEAL}"/>'
    g += f'<rect x="{sx-1*u:.1f}" y="{sy-38*u:.1f}" width="{2*u:.1f}" height="{4*u:.1f}" fill="#c9d3dc"/>'
    g += f'<rect x="{sx-8*u:.1f}" y="{sy-50*u:.1f}" width="{16*u:.1f}" height="{13*u:.1f}" rx="{5*u:.1f}" fill="#f5f8fa" stroke="#c9d3dc" stroke-width="1.2"/>'
    g += f'<rect x="{sx-6*u:.1f}" y="{sy-47*u:.1f}" width="{12*u:.1f}" height="{6.5*u:.1f}" rx="{3*u:.1f}" fill="#2f3a45"/>'
    g += f'<circle cx="{sx-2.5*u:.1f}" cy="{sy-43.7*u:.1f}" r="{1.4*u:.1f}" fill="#7fe3e8"/><circle cx="{sx+2.5*u:.1f}" cy="{sy-43.7*u:.1f}" r="{1.4*u:.1f}" fill="#7fe3e8"/>'
    g += f'<line x1="{sx:.1f}" y1="{sy-50*u:.1f}" x2="{sx:.1f}" y2="{sy-55*u:.1f}" stroke="#9aa5b0" stroke-width="1.5"/><circle cx="{sx:.1f}" cy="{sy-56*u:.1f}" r="{1.8*u:.1f}" fill="{TEAL}"/>'
    # arms holding the case file
    g += f'<rect x="{sx-12*u:.1f}" y="{sy-32*u:.1f}" width="{3.5*u:.1f}" height="{12*u:.1f}" rx="{1.7*u:.1f}" fill="#c9d3dc"/>'
    g += f'<rect x="{sx+8.5*u:.1f}" y="{sy-32*u:.1f}" width="{3.5*u:.1f}" height="{12*u:.1f}" rx="{1.7*u:.1f}" fill="#c9d3dc"/>'
    g += f'<rect x="{sx-9*u:.1f}" y="{sy-30*u:.1f}" width="{18*u:.1f}" height="{12*u:.1f}" rx="1.5" fill="{TEAL}"/>'
    g += f'<rect x="{sx-6*u:.1f}" y="{sy-27*u:.1f}" width="{12*u:.1f}" height="{2*u:.1f}" fill="#fff" opacity=".9"/>'
    g += f'<rect x="{sx-6*u:.1f}" y="{sy-23.5*u:.1f}" width="{8*u:.1f}" height="{1.5*u:.1f}" fill="#fff" opacity=".7"/>'
    add(x + y, g)


def car(x, y):
    s = ""
    # wheels on far side first
    for wx in (x + .55, x + 2.15):
        cx, cy = iso(wx, y + .05, .28)
        s += f'<ellipse cx="{cx:.1f}" cy="{cy:.1f}" rx="8" ry="9" fill="#2a2e33"/>'
    s += box(x, y, .25, 2.7, 1.25, .55, "#ffffff", "#e6ecf0", "#d3dce2")
    st = [iso(x, y + 1.25, .42), iso(x + 2.7, y + 1.25, .42), iso(x + 2.7, y + 1.25, .52), iso(x, y + 1.25, .52)]
    s += poly(st, TEAL)
    s += box(x + .65, y + .1, .8, 1.35, 1.05, .45, "#ffffff", "#bfe3f0", "#a9d6e8")
    for wx in (x + .55, x + 2.15):
        cx, cy = iso(wx, y + 1.25, .28)
        s += f'<ellipse cx="{cx:.1f}" cy="{cy:.1f}" rx="8" ry="9" fill="#2a2e33"/><ellipse cx="{cx:.1f}" cy="{cy:.1f}" rx="3.5" ry="4" fill="#9aa1a9"/>'
    hx, hy = iso(x + 2.7, y + .3, .55)
    s += f'<circle cx="{hx:.1f}" cy="{hy:.1f}" r="3" fill="#ffe7a3"/>'
    hx, hy = iso(x + 2.7, y + .95, .55)
    s += f'<circle cx="{hx:.1f}" cy="{hy:.1f}" r="3" fill="#ffe7a3"/>'
    add(x + 1.35 + y + .6, s)


def tree(x, y, s=1.0):
    cx, cy = iso(x, y)
    g = (f'<ellipse cx="{cx:.1f}" cy="{cy:.1f}" rx="{12*s:.1f}" ry="{5*s:.1f}" fill="#000" opacity=".08"/>'
         f'<rect x="{cx-2*s:.1f}" y="{cy-20*s:.1f}" width="{4*s:.1f}" height="{20*s:.1f}" fill="#9c7a5b"/>'
         f'<circle cx="{cx:.1f}" cy="{cy-34*s:.1f}" r="{17*s:.1f}" fill="#7fcf8f"/>'
         f'<path d="M{cx:.1f},{cy-51*s:.1f} A{17*s:.1f},{17*s:.1f} 0 0 1 {cx:.1f},{cy-17*s:.1f} Z" fill="#63bb76"/>')
    add(x + y, g)


# ------------------------------------------------------------------ build world
def car_y(x, y):
    """Car driving along +y (towards the viewer's lower-left)."""
    s = ""
    for wy in (y + .55, y + 2.15):
        cx, cy = iso(x + .05, wy, .28)
        s += f'<ellipse cx="{cx:.1f}" cy="{cy:.1f}" rx="8" ry="9" fill="#2a2e33"/>'
    s += box(x, y, .25, 1.25, 2.7, .55, "#ffffff", "#d3dce2", "#e6ecf0")
    st = [iso(x + 1.25, y, .42), iso(x + 1.25, y + 2.7, .42), iso(x + 1.25, y + 2.7, .52), iso(x + 1.25, y, .52)]
    s += poly(st, TEAL)
    s += box(x + .1, y + .55, .8, 1.05, 1.35, .45, "#ffffff", "#a9d6e8", "#bfe3f0")
    for wy in (y + .55, y + 2.15):
        cx, cy = iso(x + 1.25, wy, .28)
        s += f'<ellipse cx="{cx:.1f}" cy="{cy:.1f}" rx="8" ry="9" fill="#2a2e33"/><ellipse cx="{cx:.1f}" cy="{cy:.1f}" rx="3.5" ry="4" fill="#9aa1a9"/>'
    for hx in (x + .3, x + .95):
        a = iso(hx, y + 2.7, .55)
        s += f'<circle cx="{a[0]:.1f}" cy="{a[1]:.1f}" r="3" fill="#ffe7a3"/>'
    add(x + .6 + y + 1.35, s)


ground = []
# road (runs along y, between the client's office and ACER)
RX0, RX1, RY0, RY1 = -5.2, -2.6, -1.5, 21.5
ground.append(poly([iso(RX0 - .6, RY0), iso(RX0, RY0), iso(RX0, RY1), iso(RX0 - .6, RY1)], "#eef5f8"))
ground.append(poly([iso(RX0, RY0), iso(RX1, RY0), iso(RX1, RY1), iso(RX0, RY1)], "#c9d4dc"))
ground.append(poly([iso(RX1, RY0), iso(RX1 + .6, RY0), iso(RX1 + .6, RY1), iso(RX1, RY1)], "#eef5f8"))
for j in range(-1, 21, 2):
    ground.append(poly([iso(-3.96, j), iso(-3.84, j), iso(-3.84, j + 1), iso(-3.96, j + 1)], "#ffffff"))
for i in range(6):
    xx = RX0 + .1 + i * .42
    ground.append(poly([iso(xx, 12.6), iso(xx + .22, 12.6), iso(xx + .22, 14.0), iso(xx, 14.0)], "#ffffff"))
ground.append(poly([iso(-7.5, 12.6), iso(RX0 - .6, 12.6), iso(RX0 - .6, 14.0), iso(-7.5, 14.0)], "#eef5f8"))
ground.append(poly([iso(RX1 + .6, 12.6), iso(0, 12.6), iso(0, 14.0), iso(RX1 + .6, 14.0)], "#eef5f8"))

# slabs
ground.append(slab(0, 0, 28, 18))
ground.append(slab(-14.5, 7, 7, 8.5))

# client office · ABC Infrastructure Ltd.
wall_x(-14.5, -7.5, 7, 2.6, windows=[(-13.6, 1.6), (-10.2, 1.6)])
wall_y(7, 15.5, -14.5, 2.6, windows=[(8.4, 1.6)])
desk(-13.5, 7.8)
seated(-12.7, 9.05, SUITS[3], HAIRS[3], "back", skirt=True)
cabinet(-14.1, 12.6)
plant(-8.3, 7.9, .9)

# ACER outer walls
WALL_H = 3.0
wall_x(0, 28, 0, WALL_H, windows=[(1.4, 1.7), (5.2, 1.7), (11.0, 1.8), (16.0, 1.8), (22.6, 1.8)])
wall_y(0, 18, 0, WALL_H, door=(12.6, 14.2), windows=[(1.4, 1.6), (5.2, 1.6), (9.6, 1.6), (15.4, 1.6)])
# partitions
PH = 2.4
wall_x(.25, 28, 9, PH, t=.2, door=[(6.2, 7.9), (19.0, 20.8)])     # back row | front row
wall_y(.25, 9, 9, PH, t=.2, door=(5.6, 7.4))                       # Compliance | Rating Team
wall_y(9.2, 18, 9, PH, t=.2)                                        # Proposal | Published
wall_y(9.2, 18, 18, PH, t=.2, door=(13.8, 15.6))                    # Published | Committee

# Room A (front-left) · Proposal desk
desk(1.0, 9.6, w=2.0, d=.85)
seated(2.0, 10.95, SUITS[1], HAIRS[1], "back", skirt=True)
desk(3.8, 9.6)
seated(4.6, 10.85, SUITS[0], HAIRS[0], "back")
add(4.6 + 10.0 + .02, papers(4.95, 10.05, n=3))
plant(.8, 17.2)
water_cooler(7.2, 16.6)

# Room B (back-left) · Compliance
desk(1.0, .9)
seated(1.8, 2.15, SUITS[2], HAIRS[2], "back")
desk(3.6, .9)
seated(4.4, 2.15, SUITS[4], HAIRS[4], "back", skirt=True)
cabinet(.45, 3.6)
cabinet(.45, 4.4)
plant(8.0, .9, .9)

# Room C (back-right, largest) · Rating Team boardroom
shelf(9.7, .35, w=2.4)
for i, px in enumerate((15.0, 16.5, 18.0, 19.5)):
    seated(px, 2.5, SUITS[i], HAIRS[i], "front", skirt=(i == 2))
extra = ""
for i in range(4):
    extra += box(14.6 + i * 1.5, 3.2, .74, .45, .32, .02, "#c9ced4", "#9aa1a9", "#b3b9c0")
    extra += papers(14.9 + i * 1.5, 3.85, n=2)
table(14.2, 3.0, 6.2, 1.5, extra=extra)
for i, px in enumerate((15.6, 18.8)):
    seated(px, 5.05, SUITS[i + 2], HAIRS[i + 2], "back")
person(13.0, 3.9, SUITS[1], HAIRS[1], "front", tie=TEAL_D)
workstation(22.6, .9, 1)
workstation(24.8, .9, 3, skirt=True)
plant(27.3, 5.6)

# Room D (front-right) · Rating Committee
for i, px in enumerate((22.6, 24.0, 25.4)):
    seated(px, 11.3, SUITS[i], HAIRS[i + 1], "front", arm_up=True, skirt=(i == 1))
table(21.9, 11.8, 4.4, 1.5, extra=papers(23.2, 12.3, n=3) + papers(24.6, 12.2, n=2))
for i, px in enumerate((22.9, 25.3)):
    seated(px, 13.95, SUITS[i + 3], HAIRS[i], "back")
seated(27.0, 12.55, SUITS[2], HAIRS[3], "back")
plant(27.3, 17.2)

# Room E (front-middle) · Published
plant(9.9, 17.2)
plant(17.2, 9.9, .9)

# ---------------------------------------------------------------- journey cast
BD_SUIT, BD_HAIR = "#2f3640", "#2b2420"
CLIENT_SUIT, CLIENT_HAIR = "#5a6068", "#6b4a2b"
# 1 meeting at the client's office
person(-11.3, 11.6, CLIENT_SUIT, CLIENT_HAIR, "front", tie="#b08a5a", hand_out=True)
person(-9.7, 10.9, BD_SUIT, BD_HAIR, "front", tie=TEAL, carry=TEAL)
# 2 drive to ACER
car_y(-4.6, 6.0)
# 3 proposal
person(4.0, 12.9, BD_SUIT, BD_HAIR, "front", tie=TEAL, carry=TEAL)
# 4 compliance
person(3.6, 4.4, BD_SUIT, BD_HAIR, "front", tie=TEAL, carry=TEAL)
# 5 robot hand-off through the door
robot(9.6, 6.5)
# 8 published: client receives the rating
person(12.3, 14.0, CLIENT_SUIT, CLIENT_HAIR, "front", tie="#b08a5a", hand_out=True)
person(13.9, 13.3, "#434a55", HAIRS[2], "front", tie=TEAL)

# ---------------------------------------------------------------- signage on walls
def on_wall_x(x, y, z, inner):
    a = iso(x, y, z)
    return f'<g transform="translate({a[0]:.1f},{a[1]:.1f}) matrix(0.866 0.5 0 1 0 0)">{inner}</g>'


def on_wall_y(x, y, z, inner):
    a = iso(x, y, z)
    return f'<g transform="translate({a[0]:.1f},{a[1]:.1f}) matrix(0.866 -0.5 0 1 0 0)">{inner}</g>'


def screen_y(x, y, w, z0, h):
    """Screen on a wall along y (plane x)."""
    ps = [iso(x, y, z0), iso(x, y + w, z0), iso(x, y + w, z0 + h), iso(x, y, z0 + h)]
    return poly(ps, "#3a3f47") + poly([iso(x, y + .08, z0 + .08), iso(x, y + w - .08, z0 + .08), iso(x, y + w - .08, z0 + h - .08), iso(x, y + .08, z0 + h - .08)], "#eaf6f8")


signage = []
# rating wall on the Published room's back partition (plane y = 9.2)
add(16.0 + 9.2 + .2, screen(10.7, 9.2, 5.0, .85, 1.45, ""))
signage.append(on_wall_x(13.1, 9.2, 1.95,
               text(0, -14, "RATING PUBLISHED", 7.5, "#5f7480", "middle", 800, 'letter-spacing="1.2"')
               + text(0, 1, "ABC Infrastructure Ltd.", 9.5, INK, "middle", 800)
               + text(0, 19, "ACER AA+", 15, TEAL_D, "middle", 900) + text(0, 31, "Stable", 9, TEAL, "middle", 700)))
# boardroom screen on back wall
add(18.6 + .3, screen(16.0, .27, 2.6, 1.0, 1.25, ""))
bars = "".join(f'<rect x="{-26 + i*11}" y="{-h}" width="7" height="{h}" fill="{TEAL if i < 4 else TEAL_D}" opacity="{.5 + i*.1:.1f}"/>' for i, h in enumerate((10, 16, 13, 22, 26)))
signage.append(on_wall_x(17.3, .27, 1.62, bars + '<line x1="-30" y1="0" x2="30" y2="0" stroke="#9fb6c0"/>'))
# committee screen on partition (plane x = 18.2)
add(18.2 + 12.6, screen_y(18.2, 11.0, 2.6, .9, 1.25))
signage.append(on_wall_y(18.2, 12.3, 1.52, text(0, -6, "VOTE", 10, "#5f7480", "middle", 800, 'letter-spacing="1.5"')
                         + text(0, 12, "AA+ ✓ 5/5", 13, TEAL_D, "middle", 900)))
# ACER logo on compliance/back wall and on proposal room wall
signage.append(on_wall_x(6.8, .27, 2.2, text(0, 0, "ACER", 24, TEAL, "middle", 900, 'letter-spacing="3"')
                         + text(0, 14, "CREDIT RATING", 8, TEAL_D, "middle", 800, 'letter-spacing="2"')))
signage.append(on_wall_y(.27, 10.6, 2.2, text(0, 0, "PROPOSALS", 11, TEAL_D, "middle", 900, 'letter-spacing="2"')))
signage.append(on_wall_y(.27, 6.6, 2.2, text(0, 0, "COMPLIANCE", 11, TEAL_D, "middle", 900, 'letter-spacing="2"')))
signage.append(on_wall_x(-11.0, 7.27, 2.2, text(0, 0, "ABC INFRASTRUCTURE LTD.", 10.5, "#4a5a66", "middle", 900, 'letter-spacing="1"')))

# ---------------------------------------------------------------- journey path + callouts
path_pts = [(-10.2, 11.6), (-7.5, 13.3), (-3.9, 13.3), (0, 13.3), (4.0, 13.3), (7.05, 13.3), (7.05, 6.5),
            (19.9, 6.5), (19.9, 15.5), (18.0, 15.5), (15.2, 15.5)]
pp = [iso(a, b, .02) for a, b in path_pts]
path_svg = (f'<polyline points="{P(pp)}" fill="none" stroke="{TEAL}" stroke-width="3" stroke-dasharray="2 9" '
            f'stroke-linecap="round" stroke-linejoin="round" opacity=".9"/>')
for (a, b) in [(7.05, 9.0), (19.9, 9.0), (18.0, 15.5), (9.1, 6.5)]:
    q = iso(a, b, .02)
    path_svg += f'<circle cx="{q[0]:.1f}" cy="{q[1]:.1f}" r="3.5" fill="{TEAL}"/>'
end = iso(15.2, 15.5, .02)
path_svg += f'<circle cx="{end[0]:.1f}" cy="{end[1]:.1f}" r="6" fill="{TEAL_D}"/>'


def callout(n, ax, ay, title, sub, status=None, dx=0, dy=-70, w=None, at=None):
    w = w or max(170, 7.4 * max(len(title), len(sub)) + 58)
    bx, by = at if at else (ax + dx, ay + dy)
    s = f'<line x1="{ax:.1f}" y1="{ay:.1f}" x2="{bx:.1f}" y2="{by:.1f}" stroke="{TEAL}" stroke-width="1.2" opacity=".6"/>'
    s += f'<circle cx="{ax:.1f}" cy="{ay:.1f}" r="3" fill="{TEAL}"/>'
    h = 46 if not status else 68
    s += f'<rect x="{bx-w/2:.1f}" y="{by-22:.1f}" width="{w:.1f}" height="{h}" rx="12" fill="#ffffff" stroke="#cfe3ea"/>'
    s += f'<circle cx="{bx-w/2+22:.1f}" cy="{by+1:.1f}" r="12" fill="{TEAL}"/>' + text(bx - w / 2 + 22, by + 5.5, str(n), 13, "#fff", "middle", 800)
    s += text(bx - w / 2 + 42, by - 2, title, 13.5, INK, weight=800) + text(bx - w / 2 + 42, by + 14, sub, 11.5, "#6b7c88", weight=500)
    if status:
        s += f'<rect x="{bx-w/2+42:.1f}" y="{by+24:.1f}" width="{len(status)*6.6+22:.1f}" height="18" rx="9" fill="#e6f4f4"/>'
        s += text(bx - w / 2 + 52, by + 37, status + " ✓", 10.5, TEAL_D, weight=800)
    return s


callouts = []
a = iso(-11.3, 11.6, 2.4); callouts.append(callout(1, *a, "Client meeting", "ACER BD visits ABC Infrastructure", at=(165, 470)))
a = iso(-4.0, 7.4, 1.6); callouts.append(callout(2, *a, "Travel to ACER", "BD drives back with the brief", at=(330, 600)))
a = iso(4.0, 12.9, 2.3); callouts.append(callout(3, *a, "Proposal", "Proposal picked up and sent", "Proposal approved", at=(520, 760)))
a = iso(3.6, 4.4, 2.3); callouts.append(callout(4, *a, "Compliance", "CCO reviews the proposal", "Compliance approved", dx=-170, dy=-185))
a = iso(9.6, 6.5, 2.2); callouts.append(callout(5, *a, "Hand-off", "Robot carries the case file", dx=40, dy=-215))
a = iso(17.0, 2.5, 3.4); callouts.append(callout(6, *a, "Rating Team", "Analysts work the case in the boardroom", "Rating note ready", dx=80, dy=-100))
a = iso(24.0, 11.3, 2.6); callouts.append(callout(7, *a, "Rating Committee", "Committee meets and votes", "Voting done", dx=190, dy=-60))
a = iso(13.1, 13.6, 2.4); callouts.append(callout(8, *a, "Published", "Rating delivered to the client", "AA+ | Stable", dx=60, dy=120))

# speech bubbles
bx, by = iso(-11.3, 11.6, 2.25)
bubble = (f'<g transform="translate({bx-112:.1f},{by-34:.1f})"><rect x="0" y="0" width="160" height="30" rx="15" fill="#ffffff" stroke="#cfe3ea"/>'
          + text(80, 20, "Very glad to meet you!", 11.5, INK, "middle", 700) + "</g>")
bx, by = iso(12.3, 14.0, 2.25)
bubble += (f'<g transform="translate({bx-118:.1f},{by-30:.1f})"><rect x="0" y="0" width="128" height="28" rx="14" fill="#ffffff" stroke="#cfe3ea"/>'
           + text(64, 18.5, "Thank you, ACER!", 11.5, INK, "middle", 700) + "</g>")

# ---------------------------------------------------------------- frame / HUD
hud = []
hud.append(f'<rect x="0" y="0" width="{W}" height="78" fill="#ffffff" opacity=".85"/><line x1="0" y1="78" x2="{W}" y2="78" stroke="#cfe3ea"/>')
hud.append(f'<rect x="36" y="22" width="36" height="36" rx="9" fill="{TEAL}"/>' + text(54, 46, "A", 20, "#fff", "middle", 900))
hud.append(text(86, 38, "ACER", 20, INK, weight=900, extra='letter-spacing="2"') + text(86, 58, "Credit Rating · Case Journey", 12.5, "#6b7c88", weight=600))
hud.append(f'<rect x="700" y="20" width="520" height="40" rx="20" fill="#f3f8fa" stroke="#cfe3ea"/>'
           + f'<circle cx="724" cy="40" r="7" fill="none" stroke="#8aa0ac" stroke-width="2"/><line x1="729" y1="45" x2="734" y2="50" stroke="#8aa0ac" stroke-width="2"/>'
           + text(746, 45, "ABC Infrastructure Ltd.", 14, INK, weight=700) + text(1206, 45, "Rating Process", 12, TEAL_D, "end", 700))
hud.append(f'<rect x="1660" y="20" width="224" height="40" rx="20" fill="{TEAL}"/>'
           + f'<path d="M1690,31 L1690,49 L1705,40 Z" fill="#fff"/>' + text(1716, 46, "Replay Journey", 14, "#fff", weight=800))

# bottom timeline
steps = ["Client Meeting", "Travel to ACER", "Proposal", "Compliance", "Hand-off", "Rating Team", "Rating Committee", "Published"]
ty = 1062
hud.append(f'<rect x="0" y="1010" width="{W}" height="110" fill="#ffffff" opacity=".9"/><line x1="0" y1="1010" x2="{W}" y2="1010" stroke="#cfe3ea"/>')
x0, x1 = 170, 1750
hud.append(f'<line x1="{x0}" y1="{ty}" x2="{x1}" y2="{ty}" stroke="{TEAL}" stroke-width="3" opacity=".35"/>')
for i, s in enumerate(steps):
    x = x0 + i * (x1 - x0) / (len(steps) - 1)
    last = i == len(steps) - 1
    hud.append(f'<circle cx="{x:.1f}" cy="{ty}" r="{13 if last else 11}" fill="{TEAL_D if last else TEAL}"/>'
               + text(x, ty + 4.5, "✓" if not last else "★", 12, "#fff", "middle", 900)
               + text(x, ty + 34, s, 12.5, INK, "middle", 700))
hud.append(text(40, ty + 5, "JOURNEY", 11, "#6b7c88", weight=800, extra='letter-spacing="1.5"'))

# ---------------------------------------------------------------- assemble
items.sort(key=lambda t: t[0])
svg = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" '
       f'font-family="Inter, Segoe UI, Helvetica, Arial, sans-serif">',
       f'<rect width="{W}" height="{H}" fill="{BG}"/>']
svg += ground
svg.append(path_svg)
tree(-16, 9, 1.0); tree(-16, 13.5, 1.1); tree(-8, 17, .9); tree(-6.4, 3, 1.0); tree(-6.4, -1, .9); tree(-1.4, 19.5, 1.0); tree(30, 4, 1.1); tree(30, 10, 1.0); tree(30, 16, .9); tree(6, 20, .9); tree(16, 20, 1.0)
items.sort(key=lambda t: t[0])
svg += [s for _, s in items]
svg += signage
svg += callouts
svg.append(bubble)
svg += hud
svg.append("</svg>")
with open(OUT, "w") as fh:
    fh.write("\n".join(svg))
print("wrote", OUT)
