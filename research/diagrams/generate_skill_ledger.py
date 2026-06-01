#!/usr/bin/env python3
"""Testing techniques as a commitment ledger — the impeccable-workflow redesign.

Workflow applied (pbakaus/impeccable): register = brand; critique found the
card grid is the "identical card grids" absolute ban and the editorial-serif
escape is the "editorial-typographic" reflex-reject lane. distill + brand
direct the fix: no cards, a committed POV, colour that ENCODES meaning.

POV / named reference: a Field-Notes / risograph spec sheet — two committed
inks (a teal obligation-ramp + one coral spot) on cool paper. Not SaaS-cream,
not Klim-editorial, not a card grid.

Composition: a ledger, not a grid. Colour encodes the commitment gradient
(obligation falls, cost rises across tiers). Each technique carries a
bug-catching-power meter from the skill's own cost-benefit table — the real
data layer, so the piece is information design, not a styled list.

Fonts: Bricolage Grotesque (display) + Hanken Grotesk (text). Neither is on
the impeccable reflex-reject font list. See generate_hero_map.py for install.
"""
import colorsys
import pathlib
from html import escape

# --- palette: cool paper, teal obligation-ramp, one coral spot ---------------
PAPER  = "#fcfcfd"
INK    = "#15171a"
BODY   = "#4a4d55"   # trigger text — ~8:1 on paper
MUTED  = "#8a8d96"
HAIR   = "#e9e9ee"

ACCENT = "#ef5a40"   # the single spot colour (bug-power meters, focal marks)


def hsl(h, s, l):
    r, g, b = colorsys.hls_to_rgb(h / 360.0, l, s)
    return f"#{int(r*255+0.5):02x}{int(g*255+0.5):02x}{int(b*255+0.5):02x}"


# Sequential teal ramp — darker = more obligatory. Colour IS the data here.
TIER_INK = {
    1: hsl(193, 0.55, 0.24),
    2: hsl(190, 0.48, 0.35),
    3: hsl(187, 0.40, 0.47),
}

DISPLAY = "Bricolage Grotesque"
TEXT    = "Hanken Grotesk"

# --- type scale (1.25) --------------------------------------------------------
SZ_MICRO   = 12
SZ_TRIGGER = 14
SZ_NAME    = 18
SZ_GLOSS   = 15
SZ_TIER    = 21
SZ_NUM     = 58
SZ_DECK    = 17
SZ_TITLE   = 40

# --- content: (name, trigger, bug_power 1-5, relation note|None) -------------
# bug_power from references/test-types.md cost-benefit summary
# (VH=5, H=4, M=3, L=2). Fuzz/Performance not in that table: Fuzz=4 (its whole
# job is finding crashes on untrusted input), Performance=2 (niche power).
LEDGER = [
    (1, "Always", "Required on every project, no trigger needed.", [
        ("Unit",       "Any function with non-trivial logic: branches, loops, arithmetic.", 3, None),
        ("Smoke",      "Every deployable unit. The app boots and answers.", 2, "low power, catches the embarrassing failures"),
        ("Regression", "After every bug fix; the failing test comes first.", 4, None),
    ]),
    (2, "When triggered", "Add when a specific condition below appears.", [
        ("Property-based",       "Parsers, serializers, transforms, rankings: anything generative.", 5, None),
        ("Differential",         "Reimplementing a known algorithm against a trusted reference.", 5, None),
        ("Pirate / Conformance", "One specification, several language implementations.", 4, "a symmetric Differential test"),
        ("Contract",             "Unit tests lean on mocks for an external service.", 4, "guards a consumer / producer seam"),
        ("End-to-end",           "HTTP endpoints, CLI workflows, a platform-specific runtime.", 4, None),
        ("VCR cassette",         "Code calls third-party APIs: LLM, payments, auth.", 3, "guards the HTTP seam"),
        ("Characterization",     "Refactoring legacy code with no test suite to lean on.", 3, "a Golden test on unknown behaviour"),
        ("Golden file",          "Input-to-output transforms; complex generated output.", 3, None),
        ("Doc / Code sync",      "CLI commands, plugin hooks, or config described in docs.", 2, "guards the docs / code seam"),
    ]),
    (3, "With caution", "Slow, costly, or flaky. Reach only when the payoff clears the cost.", [
        ("Mutation",            "Critical modules; or coverage is high yet bugs still escape.", 5, "audits the suites above"),
        ("Fuzz",                "Security-sensitive code parsing untrusted input.", 4, "structured = Property-based"),
        ("Visual / Screenshot", "UI work where exact pixel layout is the contract.", 3, None),
        ("Performance",         "When a 2× slowdown would itself be a user-visible bug.", 2, None),
    ]),
]


# --- svg helpers --------------------------------------------------------------
def t(x, y, s, size=SZ_TRIGGER, fill=INK, weight="400", anchor="start",
      family=TEXT, ls_em=None, italic=False):
    extra = f' letter-spacing="{ls_em*size:.2f}"' if ls_em else ""
    style = ' font-style="italic"' if italic else ""
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" '
            f'font-family="{family}" font-weight="{weight}" fill="{fill}" '
            f'text-anchor="{anchor}" font-kerning="normal"{extra}{style}'
            f'>{escape(s)}</text>')


def line(x1, y1, x2, y2, stroke, w=1):
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{stroke}" stroke-width="{w}"/>')


def meter(x, y, power, on=ACCENT, off="#eceaea"):
    """Five-segment bug-power meter, right-anchored at x."""
    seg, gap, n = 13, 4, 5
    total = n * seg + (n - 1) * gap
    sx = x - total
    out = []
    for i in range(n):
        c = on if i < power else off
        out.append(f'<rect x="{sx+i*(seg+gap):.1f}" y="{y:.1f}" width="{seg}" '
                   f'height="5" rx="2.5" fill="{c}"/>')
    return "".join(out), sx


def wrap(text, max_chars):
    words, lines, cur = text.split(), [], ""
    for w in words:
        if not cur:
            cur = w
        elif len(cur) + 1 + len(w) <= max_chars:
            cur += " " + w
        else:
            lines.append(cur); cur = w
    if cur:
        lines.append(cur)
    return lines


# --- build --------------------------------------------------------------------
def build():
    W = 1400
    M = 52
    RAIL = 250                  # left rail width per tier
    COL_GAP = 44
    entries_x = M + RAIL
    entries_w = W - M - entries_x
    col_w = (entries_w - COL_GAP) / 2
    meas = int((col_w - 70) / 7.0)   # chars/line for triggers (leave room for meter)

    p = []

    # ---- masthead ----------------------------------------------------------
    p.append(t(M, 70, "Testing techniques",
               size=SZ_TITLE, weight="700", family=DISPLAY, fill=INK,
               ls_em=-0.02))
    p.append(t(M, 70, "  ·  a working order",
               size=SZ_TITLE, weight="300", family=DISPLAY, fill=MUTED,
               ls_em=-0.02))
    # the move: offset the subtitle after the title width — approximate
    # (drawn as a second tspan-like text shifted right)
    # Replace the naive overlap above with a measured placement:
    p[-1] = t(M + 415, 70, "a working order", size=SZ_TITLE, weight="300",
              family=DISPLAY, fill=MUTED, ls_em=-0.02)

    p.append(t(M, 102,
               "Sixteen techniques, ordered by how much they ask of you. "
               "Read top to bottom: obligation falls, cost rises.",
               size=SZ_DECK, fill=BODY, family=TEXT))
    p.append(t(M, 128,
               "Before any of them, encode the invariant in the type when you "
               "can. Otherwise a test along inbound → interior → outbound "
               "earns its keep.",
               size=SZ_DECK - 2, fill=MUTED, family=TEXT, italic=True))

    # ---- the rhythm: red, green, refactor — the loop every tier is written in
    # A discipline, not a 17th technique. It wraps the whole ledger, so it sits
    # above the tiers rather than inside one.
    p.append(line(M, 156, W - M, 156, HAIR, 1))
    ly = 188
    p.append(t(M, ly, "The rhythm", size=SZ_GLOSS, weight="600",
               family=DISPLAY, fill=INK, ls_em=-0.01))
    p.append(t(M, ly + 18, "every fix, every feature",
               size=SZ_MICRO, fill=MUTED, family=TEXT))

    phases = [
        ("Red", "a test that fails first"),
        ("Green", "the smallest code that passes"),
        ("Refactor", "clean up, stays green"),
    ]
    pxs = [M + 212, M + 520, M + 828]
    for (word, gloss), px in zip(phases, pxs):
        p.append(f'<circle cx="{px-15:.1f}" cy="{ly-5:.1f}" r="3.5" '
                 f'fill="{ACCENT}"/>')
        p.append(t(px, ly, word, size=SZ_NAME, weight="600", family=DISPLAY,
                   fill=INK, ls_em=-0.006))
        p.append(t(px, ly + 18, gloss, size=SZ_MICRO, fill=BODY, family=TEXT))
    # coral step arrows between phases
    for i in (0, 1):
        ax = (pxs[i] + pxs[i + 1]) / 2 + 26
        p.append(t(ax, ly, "→", size=SZ_NAME + 2, fill=ACCENT, family=TEXT,
                   anchor="middle"))
    # curved return arrow: Refactor loops back to Red ("repeat")
    rx0 = pxs[2] + 138
    rx1 = pxs[0] - 22
    dip = ly + 32
    p.append(f'<path d="M {rx0:.1f},{ly+7:.1f} C {rx0:.1f},{dip:.1f} '
             f'{rx1:.1f},{dip:.1f} {rx1+5:.1f},{ly+11:.1f}" fill="none" '
             f'stroke="{ACCENT}" stroke-width="1.4"/>')
    p.append(f'<path d="M {rx1+5:.1f},{ly+11:.1f} l -5,7 l 9,-1 z" '
             f'fill="{ACCENT}"/>')
    p.append(t((rx0 + rx1) / 2, dip + 4, "repeat until green, then clean",
               size=SZ_MICRO, fill=ACCENT, family=TEXT, anchor="middle",
               italic=True))

    p.append(line(M, ly + 58, W - M, ly + 58, HAIR, 1))
    y = ly + 86

    for tier_no, tier_name, gloss, items in LEDGER:
        tcol = TIER_INK[tier_no]

        block_top = y

        # ---- left rail: big numeral + tier name + gloss ------------------
        p.append(t(M, y + 50, str(tier_no), size=SZ_NUM, weight="700",
                   family=DISPLAY, fill=tcol, ls_em=-0.03))
        p.append(t(M + 64, y + 24, tier_name, size=SZ_TIER, weight="600",
                   family=DISPLAY, fill=INK, ls_em=-0.01))
        for i, ln in enumerate(wrap(gloss, 26)):
            p.append(t(M + 64, y + 46 + i * 18, ln, size=SZ_MICRO + 1,
                       fill=MUTED, family=TEXT))
        # count, quietly, under the numeral
        p.append(t(M, y + 74, f"{len(items)} of 16", size=SZ_MICRO,
                   fill=MUTED, family=TEXT))

        # ---- entries: two columns, no cards ------------------------------
        half = (len(items) + 1) // 2
        columns = [items[:half], items[half:]]
        col_bottoms = []

        for ci, colitems in enumerate(columns):
            cx = entries_x + ci * (col_w + COL_GAP)
            cy = y
            for (name, trig, power, note) in colitems:
                # name + meter on the same baseline
                p.append(f'<circle cx="{cx+3:.1f}" cy="{cy+9:.1f}" r="3.5" '
                         f'fill="{tcol}"/>')
                p.append(t(cx + 16, cy + 14, name, size=SZ_NAME, weight="600",
                           family=DISPLAY, fill=INK, ls_em=-0.006))
                segs, _ = meter(cx + col_w, cy + 7, power)
                p.append(segs)

                ty = cy + 36
                for ln in wrap(trig, meas):
                    p.append(t(cx + 16, ty, ln, size=SZ_TRIGGER, fill=BODY,
                               family=TEXT))
                    ty += 19
                if note:
                    p.append(t(cx + 16, ty + 1, note, size=SZ_MICRO,
                               fill=tcol, family=TEXT, italic=True))
                    ty += 18

                cy = ty + 16
                p.append(line(cx + 16, cy - 8, cx + col_w, cy - 8, HAIR, 1))
            col_bottoms.append(cy)

        y = max(col_bottoms) + 26

    # ---- footer legend (one quiet line, no eyebrow) ------------------------
    y += 2
    p.append(line(M, y, W - M, y, "#dededd", 1))
    y += 26
    legend = []
    segs, sx = meter(M + 88, y - 9, 4)
    legend.append(segs)
    legend.append(t(M, y - 5, "Power", size=SZ_MICRO, fill=MUTED, family=TEXT))
    legend.append(t(M + 100, y - 5,
                    "bug-catching power, from the skill’s cost-benefit table.   "
                    "Teal depth tracks the tier.   Italic notes name a "
                    "technique’s nearest relative or the boundary it guards.   "
                    "Full triggers and costs: references/test-types.md",
                    size=SZ_MICRO, fill=MUTED, family=TEXT))
    p.extend(legend)
    y += 22

    H = int(y + 16)
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
           f'viewBox="0 0 {W} {H}">',
           f'<rect width="{W}" height="{H}" fill="{PAPER}"/>']
    out.extend(p)
    out.append("</svg>")
    return "\n".join(out), (W, H)


def main():
    import cairosvg
    here = pathlib.Path(__file__).parent
    svg, (w, h) = build()
    (here / "skill-ledger.svg").write_text(svg, encoding="utf-8")
    cairosvg.svg2png(bytestring=svg.encode(),
                     write_to=str(here / "skill-ledger.png"),
                     output_width=w * 2, output_height=h * 2,
                     background_color=PAPER)
    print(f"wrote skill-ledger.svg / .png  ({w}x{h})")


if __name__ == "__main__":
    main()
