"""Generate SVG concept mockups for the ACER 3D case tracker."""
import math, random, os

random.seed(7)
OUT = os.path.join(os.path.dirname(__file__), "..", "docs", "mockups")
C, S = math.cos(math.radians(30)), math.sin(math.radians(30))

def iso(x, y, z, ox, oy, k):
    return ox + (x - y) * C * k, oy + (x + y) * S * k - z * k

def poly(pts, fill, stroke="none", sw=0, op=1, extra=""):
    p = " ".join(f"{a:.1f},{b:.1f}" for a, b in pts)
    return f'<polygon points="{p}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" opacity="{op}" {extra}/>'

def shade(hex_, f):
    h = hex_.lstrip("#"); r, g, b = (int(h[i:i+2], 16) for i in (0, 2, 4))
    return "#%02x%02x%02x" % tuple(max(0, min(255, int(c * f))) for c in (r, g, b))

def box(x, y, z, w, d, h, col, P, stroke="none", sw=0, extra=""):
    f = lambda a, b, c: iso(a, b, c, *P)
    top = [f(x, y, z+h), f(x+w, y, z+h), f(x+w, y+d, z+h), f(x, y+d, z+h)]
    left = [f(x, y+d, z), f(x+w, y+d, z), f(x+w, y+d, z+h), f(x, y+d, z+h)]
    right = [f(x+w, y, z), f(x+w, y+d, z), f(x+w, y+d, z+h), f(x+w, y, z+h)]
    return (poly(left, shade(col, .72), stroke, sw, extra=extra) + poly(right, shade(col, .88), stroke, sw, extra=extra)
            + poly(top, col, stroke, sw, extra=extra))

def text(x, y, s, size=12, fill="#e6edf7", anchor="start", weight=400, extra=""):
    return f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" fill="{fill}" text-anchor="{anchor}" font-weight="{weight}" {extra}>{s}</text>'

FONT = "font-family=\"Inter, Segoe UI, Helvetica, Arial, sans-serif\""
GREEN, AMBER, RED = "#3ecf8e", "#f5b83d", "#ef5b5b"

STAGES = [
    ("Mandate Intake", "#5b8def", 14, (1, 0, 0)),
    ("Info Gathering", "#7a6cf0", 31, (5, 6, 3)),
    ("Analysis", "#2fb4c9", 38, (6, 3, 2)),
    ("Mgmt Meeting", "#c86df0", 17, (3, 2, 1)),
    ("Rating Committee", "#f08a4b", 9, (1, 2, 1)),
    ("Letter &amp; Acceptance", "#e0c341", 12, (2, 1, 0)),
    ("Published / Surveillance", "#3ecf8e", 21, (0, 0, 0)),
]

def overview():
    W, H = 1600, 960
    P = (690, 235, 26)  # origin x, y, scale
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" {FONT}>',
           '<defs><radialGradient id="bg" cx="50%" cy="40%" r="75%"><stop offset="0" stop-color="#1a2440"/>'
           '<stop offset="1" stop-color="#0a0f1d"/></radialGradient>'
           '<filter id="glow" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="4" result="b"/>'
           '<feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter></defs>',
           f'<rect width="{W}" height="{H}" fill="url(#bg)"/>']
    f = lambda a, b, c=0: iso(a, b, c, *P)
    # floor
    out.append(poly([f(-1, -1), f(25, -1), f(25, 19), f(-1, 19)], "#131c33", "#24304f", 1.5))
    for i in range(0, 26, 2):
        out.append(f'<line x1="{f(i,-1)[0]:.1f}" y1="{f(i,-1)[1]:.1f}" x2="{f(i,19)[0]:.1f}" y2="{f(i,19)[1]:.1f}" stroke="#1d2846" stroke-width="1"/>')
    for j in range(0, 20, 2):
        out.append(f'<line x1="{f(-1,j)[0]:.1f}" y1="{f(-1,j)[1]:.1f}" x2="{f(25,j)[0]:.1f}" y2="{f(25,j)[1]:.1f}" stroke="#1d2846" stroke-width="1"/>')
    # conveyor path (serpentine): stage pads positions
    pads = [(1, 1), (8, 1), (15, 1), (19, 7), (15, 12), (8, 12), (1, 12)]
    path = [(3, 3), (10, 3), (17, 3), (21, 9), (17, 14), (10, 14), (3, 14)]
    for (a, b), (c, d) in zip(path, path[1:]):
        x1, y1 = f(a, b, .05); x2, y2 = f(c, d, .05)
        out.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="#2a3a63" stroke-width="16" stroke-linecap="round"/>')
        out.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="#5b8def" stroke-width="2" stroke-dasharray="6 10" opacity=".8"/>')
    # moving cases on conveyor
    for (a, b), (c, d) in zip(path, path[1:]):
        for t in (.35, .65):
            x, y = a + (c - a) * t, b + (d - b) * t
            out.append(box(x - .3, y - .3, 0, .6, .6, .5, random.choice([GREEN, GREEN, AMBER]), P))
    selected = None
    # draw pads back-to-front by x+y
    order = sorted(range(len(pads)), key=lambda i: pads[i][0] + pads[i][1])
    for i in order:
        name, col, n, (amb, red, crit) = STAGES[i]
        px, py = pads[i]
        out.append(box(px, py, 0, 4, 4, .25, shade(col, .45), P, "#0b1020", .6))
        # building
        bh = 1.2 + n / 18
        out.append(box(px + .3, py + .3, .25, 1.6, 1.6, bh, col, P, "#0b1020", .6))
        # windows
        for k in range(int(bh * 2)):
            wx, wy = f(px + 1.9, py + .6, .5 + k * .45)
            out.append(f'<rect x="{wx-2:.1f}" y="{wy-3:.1f}" width="10" height="3" fill="#fff" opacity=".35" transform="skewY(30 {wx} {wy})"/>')
        # crate stacks (case counts)
        greens = n - amb - red
        cols = [RED] * red + [AMBER] * amb + [GREEN] * greens
        slots = [(px + 2.2 + (s % 3) * .55, py + .4 + (s // 3 % 6) * .55) for s in range(18)]
        for idx, cc in enumerate(cols[:36]):
            sx, sy = slots[idx % 18]; sz = .25 + (idx // 18) * .45
            if sy > py + 3.6: continue
            out.append(box(sx, sy, sz, .45, .45, .42, cc, P, "#0b1020", .4))
        # analyst figures
        for a in range(min(4, 1 + n // 10)):
            ax, ay = f(px + .6 + a * .55, py + 3.3, .25)
            out.append(f'<ellipse cx="{ax:.1f}" cy="{ay:.1f}" rx="6" ry="3" fill="#000" opacity=".3"/>'
                       f'<rect x="{ax-4:.1f}" y="{ay-18:.1f}" width="8" height="14" rx="3" fill="#cfd8ea"/>'
                       f'<circle cx="{ax:.1f}" cy="{ay-22:.1f}" r="4.5" fill="#f2d3b3"/>')
        # red alert beacon
        if red:
            bx, by = f(px + 1.1, py + 1.1, .25 + bh + .6)
            out.append(f'<circle cx="{bx:.1f}" cy="{by:.1f}" r="7" fill="{RED}" filter="url(#glow)"/>')
            out.append(f'<circle cx="{bx:.1f}" cy="{by:.1f}" r="14" fill="none" stroke="{RED}" stroke-width="2" opacity=".5"/>')
        # label
        lx, ly = f(px + 2, py + 2, .25 + bh + 1.6)
        lw = 150 + len(name) * 3.5
        out.append(f'<rect x="{lx-lw/2:.1f}" y="{ly-30:.1f}" width="{lw:.1f}" height="38" rx="8" fill="#0d1428" stroke="{col}" stroke-width="1.5" opacity=".95"/>')
        out.append(text(lx, ly - 14, f"{i+1}. {name}", 12.5, "#fff", "middle", 600))
        out.append(text(lx, ly + 2, f"{n} cases · <tspan fill='{AMBER}'>{amb}</tspan> · <tspan fill='{RED}'>{red} overdue</tspan>", 10.5, "#9fb0d0", "middle"))
        if i == 4:
            selected = f(px + 2.6, py + 1.2, 1.2)
    # selection highlight + leader line to detail panel
    sx, sy = selected
    out.append(f'<circle cx="{sx:.1f}" cy="{sy:.1f}" r="22" fill="none" stroke="#ffffff" stroke-width="2.5" filter="url(#glow)"/>')
    out.append(f'<path d="M{sx+22:.1f},{sy:.1f} C{sx+120:.1f},{sy:.1f} 1150,330 1210,330" fill="none" stroke="#ffffff" stroke-width="1.5" stroke-dasharray="4 4" opacity=".7"/>')

    # HUD: top bar
    out.append('<rect x="0" y="0" width="1600" height="64" fill="#0b1122" opacity=".92"/><line x1="0" y1="64" x2="1600" y2="64" stroke="#24304f"/>')
    out.append(text(24, 40, "ACER", 22, "#fff", weight=800) + text(92, 40, "Rating Ops · 3D Case Floor", 16, "#9fb0d0"))
    kpis = [("Active mandates", "142", "#fff"), ("Overdue (SEBI TAT)", "9", RED), ("At risk", "18", AMBER),
            ("Avg TAT", "17.4 d", "#fff"), ("Committee this wk", "6", "#fff"), ("Published MTD", "21", GREEN)]
    for k, (lab, val, c) in enumerate(kpis):
        x = 470 + k * 175
        out.append(text(x, 26, lab.upper(), 10, "#7f8fb0", weight=600) + text(x, 50, val, 20, c, weight=700))
    # left panel: filters / sites
    out.append('<rect x="20" y="84" width="250" height="400" rx="12" fill="#0d1428" stroke="#24304f" opacity=".95"/>')
    out.append(text(38, 112, "OFFICES", 11, "#7f8fb0", weight=700))
    for k, (o, c, on) in enumerate([("Mumbai HQ", 88, True), ("New Delhi", 41, False), ("Kolkata", 13, False)]):
        y = 132 + k * 36
        out.append(f'<rect x="34" y="{y}" width="222" height="28" rx="6" fill="{"#1e2b4d" if on else "#121a31"}" stroke="{"#5b8def" if on else "#1d2846"}"/>')
        out.append(text(46, y + 19, o, 12.5, "#e6edf7") + text(244, y + 19, str(c), 12.5, "#9fb0d0", "end"))
    out.append(text(38, 258, "FILTERS", 11, "#7f8fb0", weight=700))
    for k, (fl, val) in enumerate([("Instrument", "All"), ("Sector", "All"), ("Analyst", "All"), ("Rating type", "Initial + Review")]):
        y = 272 + k * 34
        out.append(f'<rect x="34" y="{y}" width="222" height="26" rx="6" fill="#121a31" stroke="#1d2846"/>')
        out.append(text(46, y + 17, fl, 11.5, "#9fb0d0") + text(244, y + 17, val + " ▾", 11.5, "#e6edf7", "end"))
    out.append(text(38, 430, "SLA LEGEND", 11, "#7f8fb0", weight=700))
    for k, (lab, c) in enumerate([("On track", GREEN), ("At risk", AMBER), ("Overdue", RED)]):
        out.append(f'<rect x="{38 + k*78}" y="444" width="12" height="12" rx="2" fill="{c}"/>' + text(56 + k * 78, 455, lab, 11, "#cfd8ea"))
    # right detail panel
    x0 = 1210
    out.append(f'<rect x="{x0}" y="84" width="370" height="560" rx="14" fill="#0d1428" stroke="#f08a4b" stroke-width="1.5" opacity=".97"/>')
    out.append(text(x0 + 20, 114, "CASE · ACR/2026/0847", 11, "#f08a4b", weight=700))
    out.append(text(x0 + 20, 142, "Shreeji Infra Projects Ltd", 18, "#fff", weight=700))
    out.append(text(x0 + 20, 164, "Bank Loan Facilities · ₹ 450 Cr · Initial rating", 12, "#9fb0d0"))
    out.append(f'<rect x="{x0+20}" y="180" width="110" height="24" rx="12" fill="{RED}" opacity=".18" stroke="{RED}"/>' + text(x0 + 75, 196, "OVERDUE 3d", 11, RED, "middle", 700))
    out.append(f'<rect x="{x0+140}" y="180" width="150" height="24" rx="12" fill="#f08a4b" opacity=".18" stroke="#f08a4b"/>' + text(x0 + 215, 196, "Rating Committee", 11, "#f08a4b", "middle", 700))
    rows = [("Lead analyst", "R. Mehta"), ("Reviewer", "S. Iyer"), ("Mandate signed", "02 Sep 2026"),
            ("Committee slot", "08 Oct 2026, 11:00"), ("Proposed rating", "ACER BBB+ / Stable"), ("Fee status", "Invoiced · Paid")]
    for k, (a, b) in enumerate(rows):
        y = 236 + k * 30
        out.append(f'<line x1="{x0+20}" y1="{y+10}" x2="{x0+350}" y2="{y+10}" stroke="#1d2846"/>')
        out.append(text(x0 + 20, y + 2, a, 12, "#7f8fb0") + text(x0 + 350, y + 2, b, 12, "#e6edf7", "end", 600))
    out.append(text(x0 + 20, 438, "STAGE TIMELINE", 11, "#7f8fb0", weight=700))
    tl = [("In", 2, GREEN), ("Info", 9, AMBER), ("Analysis", 8, GREEN), ("Mgmt", 3, GREEN), ("RC", 6, RED)]
    tx = x0 + 20
    total = sum(d for _, d, _ in tl)
    for lab, d, c in tl:
        w = 330 * d / total
        out.append(f'<rect x="{tx:.1f}" y="450" width="{w-3:.1f}" height="14" rx="3" fill="{c}"/>')
        out.append(text(tx, 482, lab, 10, "#9fb0d0") + text(tx, 496, f"{d}d", 10, "#e6edf7", weight=600))
        tx += w
    for k, b in enumerate(["Open in Zoho CRM", "Reassign", "Nudge analyst"]):
        bx = x0 + 20 + k * 114
        out.append(f'<rect x="{bx}" y="590" width="106" height="34" rx="8" fill="{"#5b8def" if k == 0 else "#1a2442"}" stroke="#2c3b66"/>')
        out.append(text(bx + 53, 611, b, 11, "#fff", "middle", 600))
    out.append(text(x0 + 20, 530, "Next action", 11, "#7f8fb0"))
    out.append(text(x0 + 20, 552, "Committee minutes pending sign-off by chair", 12.5, "#e6edf7"))
    out.append(text(x0 + 20, 572, "Client acceptance letter due in 2 days", 12.5, "#e6edf7"))
    # bottom ticker
    out.append('<rect x="0" y="912" width="1600" height="48" fill="#0b1122" opacity=".92"/><line x1="0" y1="912" x2="1600" y2="912" stroke="#24304f"/>')
    out.append(text(24, 942, "LIVE", 11, RED, weight=800) +
               text(70, 942, "10:42  ACR/0851 moved Analysis → Mgmt Meeting   ·   10:31  ACR/0812 rating letter accepted   ·   10:18  ACR/0847 crossed TAT threshold   ·   09:55  New mandate: Kavya Textiles (NCD ₹120 Cr)", 12.5, "#cfd8ea"))
    out.append(text(1580, 900, "drag to orbit · scroll to zoom · click any building or crate", 11, "#5d6d90", "end"))
    out.append("</svg>")
    return "\n".join(out)

def team_view():
    W, H = 1600, 900
    P = (800, 150, 30)
    f = lambda a, b, c=0: iso(a, b, c, *P)
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" {FONT}>',
           '<defs><radialGradient id="bg2" cx="50%" cy="40%" r="75%"><stop offset="0" stop-color="#1d2a3f"/><stop offset="1" stop-color="#0b111c"/></radialGradient></defs>',
           f'<rect width="{W}" height="{H}" fill="url(#bg2)"/>']
    out.append(poly([f(-1, -1), f(21, -1), f(21, 15), f(-1, 15)], "#162236", "#28385a", 1.5))
    analysts = [("R. Mehta", 9, 2), ("S. Iyer", 6, 0), ("A. Khan", 12, 4), ("P. Nair", 5, 0), ("V. Rao", 7, 1),
                ("D. Shah", 14, 3), ("N. Gupta", 4, 0), ("K. Das", 8, 1)]
    pos = [(1 + (k % 4) * 5, 1 + (k // 4) * 7) for k in range(8)]
    order = sorted(range(8), key=lambda k: pos[k][0] + pos[k][1])
    for k in order:
        name, n, red = analysts[k]; x, y = pos[k]
        load = n / 14
        floorc = "#1f6b4f" if load < .6 else ("#7a5a1c" if load < .9 else "#7a2c2c")
        out.append(box(x, y, 0, 4, 4, .15, floorc, P, "#0b111c", .6))
        out.append(box(x + .4, y + .4, .15, 2.2, 1.1, .7, "#8d9bb5", P, "#0b111c", .5))  # desk
        out.append(box(x + 1.0, y + .5, .85, .9, .1, .6, "#1b2333", P))  # monitor
        for s in range(n):
            cx, cy = x + 2.9 + (s % 2) * .5, y + .5 + (s // 2 % 3) * .55
            cz = .15 + (s // 6) * .4
            c = RED if s < red else (AMBER if s < red + 2 else GREEN)
            out.append(box(cx, cy, cz, .42, .42, .36, c, P, "#0b111c", .4))
        ax, ay = f(x + 1.4, y + 2.4, .15)
        out.append(f'<ellipse cx="{ax:.1f}" cy="{ay:.1f}" rx="9" ry="4" fill="#000" opacity=".3"/><rect x="{ax-6:.1f}" y="{ay-24:.1f}" width="12" height="20" rx="4" fill="#cfd8ea"/><circle cx="{ax:.1f}" cy="{ay-30:.1f}" r="6" fill="#f2d3b3"/>')
        lx, ly = f(x + 2, y + 2, 3.4)
        out.append(f'<rect x="{lx-62:.1f}" y="{ly-24:.1f}" width="124" height="36" rx="8" fill="#0d1428" stroke="#2c3b66"/>')
        out.append(text(lx, ly - 8, name, 12.5, "#fff", "middle", 700))
        out.append(text(lx, ly + 7, f"{n} cases · <tspan fill='{RED}'>{red} overdue</tspan>", 10.5, "#9fb0d0", "middle"))
    out.append('<rect x="0" y="0" width="1600" height="60" fill="#0b1122" opacity=".92"/>')
    out.append(text(24, 38, "ACER", 22, "#fff", weight=800) + text(92, 38, "Team Workload View · Mumbai HQ", 16, "#9fb0d0"))
    out.append(text(1576, 38, "Floor tint = analyst load  ·  crate colour = case SLA", 12, "#7f8fb0", "end"))
    out.append('<rect x="24" y="780" width="420" height="96" rx="12" fill="#0d1428" stroke="#24304f"/>')
    out.append(text(44, 808, "SUGGESTED REBALANCE", 11, AMBER, weight=700))
    out.append(text(44, 832, "Move 3 cases from D. Shah → N. Gupta", 13, "#e6edf7"))
    out.append(text(44, 854, "Move 2 cases from A. Khan → P. Nair", 13, "#e6edf7"))
    out.append("</svg>")
    return "\n".join(out)

def architecture():
    W, H = 1400, 620
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" {FONT}>',
           '<defs><marker id="ar" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#7f8fb0"/></marker></defs>',
           f'<rect width="{W}" height="{H}" fill="#0b1122"/>',
           text(40, 50, "Architecture — 3D is just a view layer on the existing case data", 20, "#fff", weight=700)]
    def card(x, y, w, h, title, lines, col):
        s = f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="12" fill="#111a30" stroke="{col}" stroke-width="1.6"/>'
        s += f'<rect x="{x}" y="{y}" width="{w}" height="34" rx="12" fill="{col}" opacity=".2"/>'
        s += text(x + 16, y + 23, title, 14, "#fff", weight=700)
        for i, l in enumerate(lines):
            s += text(x + 16, y + 60 + i * 22, l, 12.5, "#cfd8ea")
        return s
    out.append(card(40, 100, 280, 200, "Source of truth", ["Zoho CRM / Creator", "  · Mandates (Deals)", "  · Stage, analyst, dates", "  · Fees (Zoho Books)", "Blueprint transitions"], "#5b8def"))
    out.append(card(40, 340, 280, 180, "Events", ["Zoho webhooks on", "stage / owner change", "+ 5-min sync fallback", "(COQL delta query)"], "#7a6cf0"))
    out.append(card(400, 180, 300, 260, "Case API (Node / FastAPI)", ["Normalised Case model", "SLA engine (SEBI TAT rules)", "Aggregates per stage/office", "WebSocket push to clients", "Role-based access (SSO)", "Audit log, read-only first"], "#2fb4c9"))
    out.append(card(780, 100, 280, 200, "Client state", ["React + Zustand store", "TanStack Query cache", "Same data feeds:", "  · 2D table view", "  · 3D floor view"], "#c86df0"))
    out.append(card(780, 340, 280, 200, "3D layer", ["React Three Fiber + drei", "Instanced crates (1k+ cases)", "Click → detail panel", "Camera presets per office", "Low-power 2D fallback"], "#f08a4b"))
    out.append(card(1120, 220, 240, 200, "Users", ["Analysts", "Rating committee", "Ops / compliance head", "Big-screen wall mode", "in the office"], "#3ecf8e"))
    for (x1, y1, x2, y2) in [(320, 200, 400, 260), (320, 430, 400, 370), (700, 280, 780, 200), (700, 360, 780, 440),
                             (1060, 200, 1120, 290), (1060, 440, 1120, 360)]:
        out.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#7f8fb0" stroke-width="2" marker-end="url(#ar)"/>')
    out.append(text(40, 585, "Write-backs (reassign, nudge) go through the API to Zoho — the 3D scene never owns data.", 13, "#9fb0d0"))
    out.append("</svg>")
    return "\n".join(out)

for name, fn in [("01-case-floor-overview.svg", overview), ("02-team-workload.svg", team_view), ("03-architecture.svg", architecture)]:
    with open(os.path.join(OUT, name), "w") as fh:
        fh.write(fn())
    print("wrote", name)
