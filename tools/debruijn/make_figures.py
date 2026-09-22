"""Generate the SVG figures for the post (no external dependencies).

Arrow heads are drawn as explicit triangles rather than with SVG markers, so
that the figures look the same in every renderer.
"""
import json, math, os

OUT = "assets/img/2026-09-22-binary-circles-de-bruijn"
os.makedirs(OUT, exist_ok=True)

BG, INK, MUTED, ACC, ACC2, FILL = "#fbfbfd", "#2c3e50", "#5a6572", "#c0392b", "#2471a3", "#dce8f5"
FONT = "font-family='Georgia, serif'"
MONO = "font-family='Menlo, Consolas, monospace'"


def header(w, h):
    return (f"<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 {w} {h}' "
            f"width='{w}' height='{h}'>\n"
            f"  <rect x='0' y='0' width='{w}' height='{h}' fill='{BG}'/>\n")


def arrow_head(x, y, dx, dy, col, size=10.0):
    d = math.hypot(dx, dy) or 1.0
    ux, uy = dx / d, dy / d
    px, py = -uy, ux
    pts = " ".join(f"{a:.1f},{b:.1f}" for a, b in (
        (x, y),
        (x - size * ux + 0.42 * size * px, y - size * uy + 0.42 * size * py),
        (x - size * ux - 0.42 * size * px, y - size * uy - 0.42 * size * py)))
    return f"  <polygon points='{pts}' fill='{col}'/>\n"


# ---------------------------------------------------------------- figure 1
def circle_panel(word, cx, cy, r, n):
    """One circular arrangement, with the all-zero window marked."""
    L = len(word)
    s = [f"  <circle cx='{cx}' cy='{cy}' r='{r}' fill='none' stroke='{MUTED}' "
         f"stroke-width='1' stroke-dasharray='3,4'/>\n"]
    ra = r + 30
    a0, a1 = math.radians(-92), math.radians(-90 + 360.0 * (n - 1) / L + 4)
    x0, y0 = cx + ra * math.cos(a0), cy + ra * math.sin(a0)
    x1, y1 = cx + ra * math.cos(a1), cy + ra * math.sin(a1)
    s.append(f"  <path d='M{x0:.1f},{y0:.1f} A{ra},{ra} 0 0 1 {x1:.1f},{y1:.1f}' "
             f"fill='none' stroke='{ACC}' stroke-width='2.2'/>\n")
    s.append(arrow_head(x1, y1, -math.sin(a1), math.cos(a1), ACC))
    for i, b in enumerate(word):
        ang = math.radians(-90 + 360.0 * i / L)
        x, y = cx + r * math.cos(ang), cy + r * math.sin(ang)
        hot = i < n
        s.append(f"  <circle cx='{x:.1f}' cy='{y:.1f}' r='14' fill='"
                 f"{FILL if hot else '#ffffff'}' stroke='{ACC if hot else INK}' "
                 f"stroke-width='{2.0 if hot else 1.3}'/>\n")
        s.append(f"  <text x='{x:.1f}' y='{y+5:.1f}' text-anchor='middle' {MONO} "
                 f"font-size='15' fill='{INK}'>{b}</text>\n")
        xl, yl = cx + (r - 36) * math.cos(ang), cy + (r - 36) * math.sin(ang)
        s.append(f"  <text x='{xl:.1f}' y='{yl+4:.1f}' text-anchor='middle' {FONT} "
                 f"font-size='11' fill='{MUTED}'>{i}</text>\n")
    return "".join(s)


def fig_circles(words):
    w, h = 700, 415
    s = [header(w, h)]
    for (word, val), cx in zip(words, (180, 520)):
        s.append(circle_panel(word, cx, 190, 110, 3))
        s.append(f"  <text x='{cx}' y='370' text-anchor='middle' {MONO} font-size='15' "
                 f"fill='{INK}'>{''.join(map(str, word))}</text>\n")
        s.append(f"  <text x='{cx}' y='390' text-anchor='middle' {FONT} font-size='13' "
                 f"fill='{ACC2}'>= {val}</text>\n")
    s.append(f"  <text x='350' y='28' text-anchor='middle' {FONT} font-size='13' fill='{MUTED}'>"
             f"read clockwise, starting at the window of three zeros</text>\n")
    s.append("</svg>\n")
    open(f"{OUT}/circles-n3.svg", "w").write("".join(s))


# ---------------------------------------------------------------- figure 2
def fig_graph(cycle_word):
    """B(2,3): the eight 3-bit windows and their sixteen shift-and-append edges."""
    n, w, h = 3, 660, 560
    N = 1 << n
    cx, cy, R, vr = 330, 296, 195, 27

    # walk the cycle once, both to collect its edges and to fix the layout
    cyc, order, v = set(), [], 0
    for b in list(cycle_word[n:]) + list(cycle_word[:n]):
        order.append(v)
        u = ((v << 1) | b) & (N - 1)
        cyc.add((v, u))
        v = u
    pos = {}
    for k, vv in enumerate(order):
        ang = math.radians(-90 + 360.0 * k / N)
        pos[vv] = (cx + R * math.cos(ang), cy + R * math.sin(ang))

    s = [header(w, h)]
    for v in range(N):
        for bit in (0, 1):
            u = ((v << 1) | bit) & (N - 1)
            hot = (v, u) in cyc
            col, sw = (ACC, 2.4) if hot else (MUTED, 1.2)
            x0, y0 = pos[v]
            x1, y1 = pos[u]
            if u == v:                                  # self-loop, pointing outwards
                a = math.atan2(y0 - cy, x0 - cx)
                p0 = (x0 + vr * math.cos(a - 0.55), y0 + vr * math.sin(a - 0.55))
                p1 = (x0 + vr * math.cos(a + 0.55), y0 + vr * math.sin(a + 0.55))
                c0 = (x0 + 2.25 * vr * math.cos(a - 0.45), y0 + 2.25 * vr * math.sin(a - 0.45))
                c1 = (x0 + 2.25 * vr * math.cos(a + 0.45), y0 + 2.25 * vr * math.sin(a + 0.45))
                s.append(f"  <path d='M{p0[0]:.1f},{p0[1]:.1f} C{c0[0]:.1f},{c0[1]:.1f} "
                         f"{c1[0]:.1f},{c1[1]:.1f} {p1[0]:.1f},{p1[1]:.1f}' fill='none' "
                         f"stroke='{col}' stroke-width='{sw}'/>\n")
                s.append(arrow_head(p1[0], p1[1], p1[0] - c1[0], p1[1] - c1[1], col))
                continue
            dx, dy = x1 - x0, y1 - y0
            d = math.hypot(dx, dy)
            ux, uy = dx / d, dy / d
            bow = 0.15 * d
            mx, my = (x0 + x1) / 2 - uy * bow, (y0 + y1) / 2 + ux * bow

            # Sample the quadratic Bezier and clip it against the two node
            # circles; this is more reliable than shortening the chord.
            def q(t):
                a = (1 - t) ** 2
                bq = 2 * (1 - t) * t
                c = t * t
                return (a * x0 + bq * mx + c * x1, a * y0 + bq * my + c * y1)

            ts = [k / 200.0 for k in range(201)]
            inside = [t for t in ts if math.hypot(*(p - c for p, c in zip(q(t), (x0, y0)))) > vr + 2
                      and math.hypot(*(p - c for p, c in zip(q(t), (x1, y1)))) > vr + 10]
            if not inside:
                continue
            pts = [q(t) for t in inside[::6] + [inside[-1]]]
            path = "M" + " L".join(f"{a:.1f},{b:.1f}" for a, b in pts)
            s.append(f"  <path d='{path}' fill='none' stroke='{col}' stroke-width='{sw}'/>\n")
            (ex, ey), (bx, by) = pts[-1], pts[-2]
            s.append(arrow_head(ex, ey, ex - bx, ey - by, col))
    for v in range(N):
        x, y = pos[v]
        s.append(f"  <circle cx='{x:.1f}' cy='{y:.1f}' r='{vr}' fill='#ffffff' "
                 f"stroke='{INK}' stroke-width='1.5'/>\n")
        s.append(f"  <text x='{x:.1f}' y='{y+5:.1f}' text-anchor='middle' {MONO} "
                 f"font-size='14' fill='{INK}'>{v:03b}</text>\n")
    s.append(f"  <text x='330' y='30' text-anchor='middle' {FONT} font-size='13' fill='{MUTED}'>"
             f"each vertex has two outgoing and two incoming edges</text>\n")
    s.append(f"  <text x='330' y='542' text-anchor='middle' {FONT} font-size='13' fill='{ACC}'>"
             f"red: the Hamiltonian cycle of the word 00010111</text>\n")
    s.append("</svg>\n")
    open(f"{OUT}/debruijn-graph-n3.svg", "w").write("".join(s))


# ---------------------------------------------------------------- figure 3
def fig_counts(counts, M, n):
    L = len(counts)
    w, h = 760, 380
    l, r, t, b = 62, 20, 40, 64
    pw, ph = w - l - r, h - t - b
    bw = pw / L
    ymax = M * 1.08
    s = [header(w, h)]
    for frac, lab in ((0, "0"), (0.25, f"{M//4}"), (0.5, f"{M//2}"), (0.75, f"{3*M//4}"), (1, f"{M}")):
        y = t + ph - frac * M / ymax * ph
        s.append(f"  <line x1='{l}' y1='{y:.1f}' x2='{l+pw}' y2='{y:.1f}' stroke='#d8dde3' "
                 f"stroke-width='1'/>\n")
        s.append(f"  <text x='{l-9}' y='{y+4:.1f}' text-anchor='end' {FONT} font-size='11' "
                 f"fill='{MUTED}'>{lab}</text>\n")
    for i, c in enumerate(counts):
        x = l + i * bw
        bh = c / ymax * ph
        s.append(f"  <rect x='{x+1.6:.1f}' y='{t+ph-bh:.1f}' width='{bw-3.2:.1f}' "
                 f"height='{bh:.1f}' fill='{FILL}' stroke='{ACC2}' stroke-width='1'/>\n")
        s.append(f"  <text x='{x+bw/2:.1f}' y='{t+ph+15:.1f}' text-anchor='middle' {FONT} "
                 f"font-size='9' fill='{MUTED}'>{i}</text>\n")
    axis = (n + L - 1) / 2.0
    xa = l + (axis + 0.5) * bw
    s.append(f"  <line x1='{xa:.1f}' y1='{t-8}' x2='{xa:.1f}' y2='{t+ph+4}' stroke='{ACC}' "
             f"stroke-width='1.4' stroke-dasharray='6,5'/>\n")
    s.append(f"  <text x='{xa:.1f}' y='{t-14}' text-anchor='middle' {FONT} font-size='11' "
             f"fill='{ACC}'>axis of symmetry at i = {axis:g}</text>\n")
    s.append(f"  <line x1='{l}' y1='{t+ph}' x2='{l+pw}' y2='{t+ph}' stroke='{INK}' stroke-width='1.2'/>\n")
    s.append(f"  <line x1='{l}' y1='{t}' x2='{l}' y2='{t+ph}' stroke='{INK}' stroke-width='1.2'/>\n")
    s.append(f"  <text x='{l+pw/2}' y='{h-24}' text-anchor='middle' {FONT} font-size='12' "
             f"fill='{INK}'>position i in the circular word</text>\n")
    s.append(f"  <text x='16' y='{t+ph/2}' text-anchor='middle' {FONT} font-size='12' fill='{INK}' "
             f"transform='rotate(-90 16 {t+ph/2})'>words with a 1 at position i</text>\n")
    s.append("</svg>\n")
    open(f"{OUT}/position-counts-n5.svg", "w").write("".join(s))


data = json.load(open("tools/debruijn/data/explore.json"))
fig_circles([([0, 0, 0, 1, 0, 1, 1, 1], 23), ([0, 0, 0, 1, 1, 1, 0, 1], 29)])
fig_graph([0, 0, 0, 1, 0, 1, 1, 1])
fig_counts(data["5"]["position_counts"], 2048, 5)
print("written:", sorted(os.listdir(OUT)))
