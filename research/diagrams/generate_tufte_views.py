#!/usr/bin/env python3
"""Three Tufte-compliant views of the testing-technique cost/benefit data.

Data source: testing-best-practices/references/test-types.md, "Cost-Benefit
Summary" table (14 techniques x 5 ordinal attributes).

Design rules applied (from the tufte skill — principles.md / kill-list.md):
  - one accent color (#b3261e), reserved for the focal quantity
  - no frames, no heavy gridlines, range-frame thinking
  - direct labels, no legends
  - sorted by the value the reader cares about (bug power), never alphabetical
  - each ordinal column on its own labeled low->high scale (honest)
  - erase redundant data-ink: position encodes level; the word is dropped
"""
from html import escape
import pathlib

# --- Tufte tokens -------------------------------------------------------------
INK = "#1a1a1a"
PAPER = "#fafaf7"
RULE = "#d8d4cc"
MUTED = "#8a857c"
ACCENT = "#b3261e"
G1 = "#e7e3da"   # faintest track
G3 = "#6b665d"   # secondary

SERIF = "Georgia, 'Times New Roman', serif"
MONO = "'DejaVu Sans Mono', monospace"

# --- data: level ints. cost attrs scaleMax 4; bug power scaleMax 5 ------------
# (name, tier, setup, maint, speed, bug, flake, bug_note)
ROWS = [
    ("Differential",     1, 2, 2, 4, 5, 1, False),
    ("Property-based",   2, 3, 2, 3, 5, 2, False),
    ("Mutation",         3, 4, 2, 1, 5, 1, False),
    ("Regression",       1, 2, 2, 4, 4, 1, False),
    ("Contract",         2, 3, 3, 3, 4, 2, False),
    ("Pirate / conf.",   2, 3, 2, 3, 4, 1, False),
    ("End-to-end",       2, 4, 3, 2, 4, 3, False),
    ("Characterization", 2, 2, 3, 4, 3, 1, False),
    ("Golden file",      2, 2, 2, 4, 3, 1, False),
    ("Unit",             1, 2, 2, 4, 3, 1, False),
    ("VCR cassette",     2, 2, 2, 4, 3, 1, False),
    ("Screenshot",       3, 4, 4, 2, 3, 4, False),
    ("Smoke",            1, 1, 1, 4, 2, 2, True),
    ("Doc-sync",         2, 2, 2, 4, 2, 1, True),
]

# attribute: (key, header, better, scale_max, low_word, high_word, accent?)
ATTRS = [
    ("setup", "Setup",     "low",  4, "very low", "high",      False),
    ("maint", "Maint.",    "low",  4, "very low", "high",      False),
    ("speed", "Speed",     "high", 4, "very slow", "fast",     False),
    ("bug",   "Bug power", "high", 5, "low",       "very high", True),
    ("flake", "Flake risk","low",  4, "very low", "high",      False),
]
IDX = {"setup": 2, "maint": 3, "speed": 4, "bug": 5, "flake": 6}


def frac(level, scale_max):
    return (level - 1) / (scale_max - 1)


def t(x, y, s, size=12, fill=INK, weight="400", anchor="start",
      family=SERIF, ls=None):
    extra = f' letter-spacing="{ls}"' if ls else ""
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" '
            f'font-family="{family}" font-weight="{weight}" fill="{fill}" '
            f'text-anchor="{anchor}"{extra}>{escape(s)}</text>')


def line(x1, y1, x2, y2, stroke, w=1, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{stroke}" stroke-width="{w}"{d}/>')


def dot(cx, cy, r, fill):
    return f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r}" fill="{fill}"/>'


def svg_open(w, h):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
            f'viewBox="0 0 {w} {h}">\n'
            f'<rect width="{w}" height="{h}" fill="{PAPER}"/>')


# =============================================================================
# View 1 — encoded table (the multivariate table)
# =============================================================================
def view_table():
    W, H = 1180, 760
    name_x = 44
    tier_x = 250
    col0 = 300
    col_w = 168
    strip_w = 104
    top = 168
    row_h = 38

    p = [svg_open(W, H)]
    p.append(t(44, 56, "Fourteen testing techniques, ranked by bug-catching power",
               size=25, weight="700"))
    p.append(t(44, 84,
               "Each cell is a level on that attribute's own low→high scale; "
               "the dot is the value, the track is the range. Sorted by payoff, "
               "then by setup cost.",
               size=13, fill=G3))
    p.append(t(44, 104,
               "Source: test-types.md cost-benefit summary  ·  red = the payoff column",
               size=11.5, fill=MUTED))

    # column headers + scale labels
    p.append(t(name_x, top - 30, "Technique", size=11, fill=MUTED,
               weight="700", ls="0.06em"))
    p.append(t(tier_x, top - 30, "Tier", size=11, fill=MUTED, weight="700",
               anchor="middle", ls="0.06em"))
    for i, (key, head, better, smax, lo, hi, acc) in enumerate(ATTRS):
        cx = col0 + i * col_w
        col = ACCENT if acc else MUTED
        p.append(t(cx, top - 44, head, size=11, fill=col, weight="700",
                   ls="0.06em"))
        p.append(t(cx, top - 30,
                   f"{lo}", size=9.5, fill=MUTED))
        p.append(t(cx + strip_w, top - 30, hi, size=9.5, fill=MUTED,
                   anchor="end"))
        better_word = "lower better" if better == "low" else "higher better"
        p.append(t(cx, top - 16, better_word, size=9, fill=MUTED,
                   family=MONO))

    p.append(line(44, top - 6, W - 44, top - 6, INK, 1))

    for r, row in enumerate(ROWS):
        y = top + r * row_h + 22
        name = row[0]
        tier = row[1]
        p.append(t(name_x, y, name, size=13.5, fill=INK))
        p.append(t(tier_x, y, f"T{tier}", size=11, fill=MUTED, family=MONO,
                   anchor="middle"))
        for i, (key, head, better, smax, lo, hi, acc) in enumerate(ATTRS):
            cx = col0 + i * col_w
            level = row[IDX[key]]
            f = frac(level, smax)
            # faint track + level ticks
            p.append(line(cx, y - 4, cx + strip_w, y - 4, G1, 3))
            for lv in range(1, smax + 1):
                tx = cx + frac(lv, smax) * strip_w
                p.append(line(tx, y - 8, tx, y, G1, 1))
            fill = ACCENT if acc else INK
            dr = 5.0 if acc else 4.0
            p.append(dot(cx + f * strip_w, y - 4, dr, fill))
        # faint row rule
        p.append(line(44, y + 11, W - 44, y + 11, G1, 0.75))

    p.append(line(44, top + len(ROWS) * row_h + 13, W - 44,
                  top + len(ROWS) * row_h + 13, RULE, 1))
    p.append(t(44, top + len(ROWS) * row_h + 34,
               "Smoke and Doc-sync carry low bug power but catch critical, "
               "embarrassing failures — keep them anyway.",
               size=11, fill=MUTED))
    p.append("</svg>")
    return "\n".join(p), (W, H)


# =============================================================================
# View 2 — small multiples (one sorted dot plot per attribute, shared rows)
# =============================================================================
def view_small_multiples():
    W, H = 1320, 720
    name_x = 40
    names_w = 196
    panel0 = 250
    panel_w = 210
    strip_w = 150
    top = 150
    row_h = 38

    p = [svg_open(W, H)]
    p.append(t(40, 54, "The same fourteen techniques across five attributes",
               size=24, weight="700"))
    p.append(t(40, 80,
               "Rows share one order (by bug power). Read down a panel for that "
               "attribute; read across a row for one technique's profile.",
               size=13, fill=G3))

    # row names + shared faint guide lines
    p.append(t(name_x, top - 22, "Technique", size=11, fill=MUTED,
               weight="700", ls="0.06em"))
    for r, row in enumerate(ROWS):
        y = top + r * row_h + 20
        p.append(t(name_x, y, row[0], size=13, fill=INK))

    for i, (key, head, better, smax, lo, hi, acc) in enumerate(ATTRS):
        px = panel0 + i * panel_w
        col = ACCENT if acc else MUTED
        p.append(t(px, top - 38, head, size=12.5, fill=col, weight="700"))
        bw = "lower better" if better == "low" else "higher better"
        p.append(t(px, top - 23, bw, size=9, fill=MUTED, family=MONO))
        p.append(t(px, top - 8, lo, size=9, fill=MUTED))
        p.append(t(px + strip_w, top - 8, hi, size=9, fill=MUTED, anchor="end"))
        # baseline range frame for the panel
        p.append(line(px, top + 2, px + strip_w, top + 2, RULE, 0.75))
        for r, row in enumerate(ROWS):
            y = top + r * row_h + 20
            level = row[IDX[key]]
            f = frac(level, smax)
            p.append(line(px, y - 4, px + strip_w, y - 4, G1, 2))
            fill = ACCENT if acc else INK
            dr = 5.0 if acc else 4.0
            p.append(dot(px + f * strip_w, y - 4, dr, fill))
    p.append("</svg>")
    return "\n".join(p), (W, H)


# =============================================================================
# View 3 — payoff scatter (bug power vs setup cost, efficient frontier)
# =============================================================================
def view_scatter():
    W, H = 1080, 820
    # plot area
    x0, x1 = 230, 720          # setup cost 1..4
    y0, y1 = 640, 150          # bug power 2..5 (y inverted)
    sx_min, sx_max = 1, 4
    by_min, by_max = 2, 5

    def px(setup):
        return x0 + (setup - sx_min) / (sx_max - sx_min) * (x1 - x0)

    def py(bug):
        return y0 + (bug - by_min) / (by_max - by_min) * (y1 - y0)

    p = [svg_open(W, H)]
    p.append(t(44, 54, "Which tests pay off: bug power against setup cost",
               size=24, weight="700"))
    p.append(t(44, 80,
               "Up = catches more bugs. Left = cheaper to stand up. The "
               "top-left corner is where the cheap, high-yield tests live.",
               size=13, fill=G3))

    # range-frame axes (only spanning the data)
    p.append(line(x0, y0, x0, y1, G3, 0.75))
    p.append(line(x0, y0, x1, y0, G3, 0.75))
    # axis ticks (labeled values only)
    setup_words = {1: "very low", 2: "low", 3: "medium", 4: "high"}
    for s in range(sx_min, sx_max + 1):
        p.append(line(px(s), y0, px(s), y0 + 5, G3, 0.75))
        p.append(t(px(s), y0 + 20, setup_words[s], size=11, fill=G3,
                   anchor="middle"))
    bug_words = {2: "low", 3: "medium", 4: "high", 5: "very high"}
    for b in range(by_min, by_max + 1):
        p.append(t(x0 - 14, py(b) + 4, bug_words[b], size=11, fill=G3,
                   anchor="end"))
    p.append(t(px((sx_min + sx_max) / 2), y0 + 44,
               "setup cost  →", size=12, fill=MUTED, anchor="middle",
               weight="700"))
    p.append(f'<text x="{x0-86:.1f}" y="{(y0+y1)/2:.1f}" font-size="12" '
             f'font-family="{SERIF}" font-weight="700" fill="{MUTED}" '
             f'text-anchor="middle" transform="rotate(-90 {x0-86:.1f} '
             f'{(y0+y1)/2:.1f})">bug-catching power  →</text>')

    # group techniques by (setup, bug) cell to handle ties
    cells = {}
    for row in ROWS:
        key = (row[2], row[5])  # setup, bug
        cells.setdefault(key, []).append(row[0])

    frontier = {"Differential", "Regression", "Property-based"}
    # label offset directions per cell to avoid collisions
    offsets = {
        (2, 5): (12, -6),    # Differential
        (3, 5): (12, -6),    # Property
        (4, 5): (12, -6),    # Mutation
        (2, 4): (12, -8),     # Regression
        (3, 4): (14, -6),    # Contract, Pirate (to the right, clears Regression)
        (4, 4): (12, 4),     # E2E
        (2, 3): (14, 4),     # Unit/VCR/Char/Golden cluster
        (4, 3): (12, 4),     # Screenshot
        (1, 2): (12, -10),   # Smoke (above baseline)
        (2, 2): (12, -10),   # Doc-sync (above baseline)
    }

    for (setup, bug), names in cells.items():
        cx, cy = px(setup), py(bug)
        focal = any(n in frontier for n in names)
        fill = ACCENT if focal else INK
        p.append(dot(cx, cy, 5.5 if focal else 4.5, fill))
        dx, dy = offsets.get((setup, bug), (12, 4))
        anchor = "start" if dx > 0 else "end"
        lx = cx + dx
        for j, nm in enumerate(names):
            is_f = nm in frontier
            p.append(t(lx, cy + dy + j * 15, nm, size=12,
                       fill=ACCENT if is_f else INK,
                       weight="700" if is_f else "400", anchor=anchor))

    # annotate the sweet spot
    p.append(t(px(1.55), py(4.78), "cheap + powerful", size=12.5,
               fill=ACCENT, weight="700", anchor="start"))
    p.append(line(px(1.5), py(4.7), px(2) - 8, py(5) + 4, ACCENT, 0.75,
                  dash="2,3"))
    p.append("</svg>")
    return "\n".join(p), (W, H)


# =============================================================================
def main():
    import cairosvg
    here = pathlib.Path(__file__).parent
    views = {
        "tufte-1-encoded-table": view_table,
        "tufte-2-small-multiples": view_small_multiples,
        "tufte-3-payoff-scatter": view_scatter,
    }
    for name, fn in views.items():
        svg, (w, h) = fn()
        (here / f"{name}.svg").write_text(svg, encoding="utf-8")
        cairosvg.svg2png(bytestring=svg.encode(), write_to=str(here / f"{name}.png"),
                         output_width=w * 2, output_height=h * 2,
                         background_color="#fafaf7")
        print(f"wrote {name}.svg / .png ({w}x{h})")


if __name__ == "__main__":
    main()
