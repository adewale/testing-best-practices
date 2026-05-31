#!/usr/bin/env python3
"""A map of testing techniques — color-forward and attractive, by design.

This is the synthesis view. It treats the session's lessons as design rules:

  * COLOR IS A DIMENSION. Each oracle family owns a hue; the palette is a
    curated HSL ramp (constant saturation/lightness) so it reads as designed,
    not as a default rainbow. Color carries the grouping AND makes the artifact
    scannable AND attractive — all three at once.
  * BEAUTY IS A GOAL. Soft shadows, tinted panels, rounded cards, and a
    gradient accent rule (which doubles as the color key) are kept precisely
    because Tufte would cut them. The artifact is meant to be liked.
  * KEEP THE USEFUL TUFTE BITS. Relationships are drawn on the map as inline
    notes (no arc spaghetti), type is hierarchical, labels are direct, and no
    quantity is encoded twice.
  * PRESERVE THE ORIGINAL PURPOSE. Every technique, grouped by family, with the
    cross-family relationships shown.
"""
from html import escape
import colorsys
import pathlib

# --- neutral tokens -----------------------------------------------------------
PAPER  = "#fbfaf7"
INK    = "#1f1d1a"
SECOND = "#5f5a52"
MUTED  = "#8a857c"
RULE   = "#e2ded4"
REL    = "#6b665d"   # relationship notes — hue-neutral so family color leads

# --- type system (impeccable/typeset): an intentional superfamily, not -------
# generic defaults. IBM Plex — Serif for display (structure + authority),
# Sans for body, Mono for all-caps eyebrows. Three genuine contrasts in one
# coherent type-design language.
DISPLAY = "IBM Plex Serif"   # title + family card headers
BODYF   = "IBM Plex Sans"    # technique labels, deck, notes
MONO    = "IBM Plex Mono"    # eyebrows / all-caps labels

# Modular scale, ratio 1.25 (major third) off a 15px base. Committed — four
# steps with real contrast, no muddy 14/15/16 neighbours.
SZ_CAPTION = 12   # eyebrows, subheads, notes      (base / 1.25)
SZ_BODY    = 15   # technique labels, deck         (base)
SZ_HEADING = 19   # family card headers           (base * 1.25)
SZ_DISPLAY = 32   # title                         (display jump)


# --- curated categorical palette (constant S/L => harmonious, not garish) -----
def hsl(h, s, l):
    r, g, b = colorsys.hls_to_rgb(h / 360.0, l, s)
    return f"#{int(r*255+0.5):02x}{int(g*255+0.5):02x}{int(b*255+0.5):02x}"


# 12 hues, gently rotated so neighbours in the column layout don't clash.
HUES = [205, 230, 168, 188, 262, 288, 32, 8, 330, 142, 96, 50]


def family_colors(i):
    h = HUES[i % len(HUES)]
    return {
        "header": hsl(h, 0.42, 0.40),   # solid header, white text sits on it
        "tint":   hsl(h, 0.55, 0.955),  # very light body wash
        "border": hsl(h, 0.40, 0.84),
        "dot":    hsl(h, 0.55, 0.46),
        "key":    hsl(h, 0.50, 0.50),   # gradient-rule stop
    }


# --- content ------------------------------------------------------------------
FAMILIES = [
    ("Foundation",      "tier 1 · always required",
        ["Unit", "Smoke", "Regression"]),
    ("Specified oracle", "assert exact values",
        ["Table-driven", "Integration", "End-to-end"]),
    ("Property / invariant", "assert relations",
        ["Property-based", "Metamorphic", "Combinatorial / Pairwise",
         "Bounded-exhaustive", "Fuzz"]),
    ("Reference oracle", "compare to another impl",
        ["Differential", "Pirate / Conformance", "Compatibility"]),
    ("Recorded oracle", "capture & replay",
        ["Golden / Snapshot", "Characterization", "VCR cassette",
         "Visual / Screenshot"]),
    ("Contract / model / spec", "derive from a spec",
        ["Contract (Pact)", "Doc ↔ Code sync", "Model-based / Stateful",
         "Spec-based / Formal", "Concolic / Symbolic"]),
    ("Resilience · non-functional", "stress the system, not logic",
        ["Load", "Stress", "Soak / Endurance", "Performance / Benchmark",
         "Chaos"]),
    ("Security oracle", "find what shouldn't happen",
        ["Penetration / Scan", "Adversarial / Red-team"]),
    ("AI-system oracle", "non-deterministic outputs",
        ["LLM eval-driven", "Prompt regression", "Vibes / Semantic",
         "Guardrail", "AI-code verification"]),
    ("Release-stage & human", "process, not code",
        ["Sanity (vs Smoke)", "Canary / Rollout", "Exploratory",
         "ATDD / BDD / Acceptance"]),
    ("Domain-specific", "specialised conformance",
        ["Data-quality / validation", "Accessibility / WCAG"]),
    ("Meta · audits the suite", "tests the tests",
        ["Mutation", "Coverage", "Assertion quality"]),
]

# Cross-family relationships shown inline under the technique.
NOTE_FOR = {
    "Pirate / Conformance": "symmetric variant of Differential",
    "Metamorphic":          "relational variant of Property-based",
    "Fuzz":                 "structured = Property-based; sibling of Red-team",
    "Characterization":     "Golden applied to legacy code",
    "Mutation":             "audits any suite above",
    "Coverage":             "audits any suite above",
    "Assertion quality":    "audits any suite above",
    "Doc ↔ Code sync":      "guards the docs↔code boundary",
    "VCR cassette":         "guards the HTTP boundary",
    "Contract (Pact)":      "guards a consumer↔producer boundary",
}


# --- svg helpers --------------------------------------------------------------
def t(x, y, s, size=SZ_BODY, fill=INK, weight="400", anchor="start",
      family=BODYF, ls_em=None, italic=False):
    # letter-spacing expressed in em, converted to user units
    extra = f' letter-spacing="{ls_em*size:.2f}"' if ls_em else ""
    style = ' font-style="italic"' if italic else ""
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" '
            f'font-family="{family}" font-weight="{weight}" fill="{fill}" '
            f'text-anchor="{anchor}" font-kerning="normal"{extra}{style}'
            f'>{escape(s)}</text>')


def rrect(x, y, w, h, r, fill, stroke="none", sw=1, opacity=None):
    op = f' opacity="{opacity}"' if opacity is not None else ""
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" '
            f'rx="{r}" ry="{r}" fill="{fill}" stroke="{stroke}" '
            f'stroke-width="{sw}"{op}/>')


def header_path(x, y, w, h, r, fill):
    """Rounded only on the top two corners."""
    return (f'<path d="M{x:.1f},{y+r:.1f} a{r},{r} 0 0 1 {r},{-r} '
            f'h{w-2*r:.1f} a{r},{r} 0 0 1 {r},{r} v{h-r:.1f} h{-w:.1f} z" '
            f'fill="{fill}"/>')


def line(x1, y1, x2, y2, stroke, w=1):
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{stroke}" stroke-width="{w}" stroke-linecap="round"/>')


# --- build --------------------------------------------------------------------
def build():
    W = 1540
    M = 32
    COLS = 4
    GUT = 24
    COL_W = (W - 2 * M - (COLS - 1) * GUT) / COLS

    HDR_H = 52
    PAD_TOP = 14
    LINE_H = 24      # body 15 * ~1.6 — vertical rhythm unit
    NOTE_H = 17
    PAD_BOT = 16

    def card_h(items):
        notes = sum(1 for it in items if it in NOTE_FOR)
        return HDR_H + PAD_TOP + len(items) * LINE_H + notes * NOTE_H + PAD_BOT

    body = []

    # ---- title (display: Plex Serif Bold, tightened tracking) ----
    body.append(t(M, 60, "A map of testing techniques",
                  size=SZ_DISPLAY, weight="700", family=DISPLAY, fill=INK,
                  ls_em=-0.01))
    # deck (body size, secondary colour — measure kept ~70ch)
    body.append(t(M, 88,
                  "Every technique, grouped by its oracle — how you know the "
                  "right answer. Colour is the family.",
                  size=SZ_BODY, fill=SECOND))

    # ---- gradient accent rule = the colour key ----
    grad_y = 100
    stops = "".join(
        f'<stop offset="{i/(len(FAMILIES)-1)*100:.1f}%" '
        f'stop-color="{family_colors(i)["key"]}"/>'
        for i in range(len(FAMILIES))
    )
    defs = (f'<defs><linearGradient id="famkey" x1="0" y1="0" x2="1" y2="0">'
            f'{stops}</linearGradient>'
            f'<filter id="soft" x="-25%" y="-25%" width="150%" height="160%">'
            f'<feDropShadow dx="0" dy="1.5" stdDeviation="3.5" '
            f'flood-color="#3a342b" flood-opacity="0.16"/></filter></defs>')
    body.append(rrect(M, grad_y, W - 2 * M, 5, 2.5, "url(#famkey)"))
    body.append(t(W - M, grad_y - 2, "TWELVE FAMILIES", size=SZ_CAPTION - 1.5,
                  fill=MUTED, anchor="end", family=MONO, weight="500",
                  ls_em=0.08))

    # ---- trust-boundary lens (soft tinted strip) ----
    sb_y = grad_y + 26
    seg_w = (W - 2 * M) / 3
    segs = [
        ("INBOUND", "parse, don’t validate", "#eef4f8"),
        ("TYPED INTERIOR", "behaviour on the public API", "#f0eef8"),
        ("OUTBOUND", "contract · VCR · E2E", "#f6eef2"),
    ]
    for i, (cap, sub, tint) in enumerate(segs):
        x = M + i * seg_w + (4 if i else 0)
        body.append(rrect(x, sb_y, seg_w - 8, 36, 6, tint))
        body.append(t(x + 14, sb_y + 16, cap, size=SZ_CAPTION - 1, fill=SECOND,
                      weight="500", family=MONO, ls_em=0.08))
        body.append(t(x + 14, sb_y + 30, sub, size=SZ_CAPTION, fill=MUTED,
                      italic=True))

    # ---- Step Zero band ----
    sz_y = sb_y + 48
    body.append(rrect(M, sz_y, W - 2 * M, 42, 7, INK))
    body.append(t(M + 16, sz_y + 18, "STEP ZERO", size=SZ_CAPTION - 1,
                  weight="500", fill="#f2c9c4", family=MONO, ls_em=0.1))
    body.append(t(M + 132, sz_y + 18,
                  "before any test — correctness-by-construction",
                  size=SZ_CAPTION + 1, weight="600", fill="#ffffff"))
    body.append(t(M + 16, sz_y + 34,
                  "If a tighter type makes the bad state unrepresentable, "
                  "encode the type and delete the test.",
                  size=SZ_CAPTION, fill="#d8d3ca", italic=True))

    grid_top = sz_y + 42 + 26

    # ---- packed coloured cards ----
    col_y = [grid_top] * COLS
    cards = []
    for i, (head, sub, items) in enumerate(FAMILIES):
        c = col_y.index(min(col_y))
        x = M + c * (COL_W + GUT)
        y = col_y[c]
        h = card_h(items)
        cards.append((i, head, sub, items, x, y, h))
        col_y[c] = y + h + 22

    for i, head, sub, items, x, y, h in cards:
        col = family_colors(i)
        # soft shadow + body
        body.append(rrect(x, y, COL_W, h, 9, PAPER, stroke="none"))
        body.append(f'<g filter="url(#soft)">'
                    + rrect(x, y, COL_W, h, 9, col["tint"],
                            stroke=col["border"], sw=1) + '</g>')
        # header (display serif semibold + caption-size italic subhead)
        body.append(header_path(x, y, COL_W, HDR_H, 9, col["header"]))
        body.append(t(x + 15, y + 24, head, size=SZ_HEADING, weight="600",
                      family=DISPLAY, fill="#ffffff"))
        body.append(t(x + 15, y + 41, sub, size=SZ_CAPTION, fill="#f3f1ee",
                      italic=True))
        # techniques (body: Plex Sans regular)
        cy = y + HDR_H + PAD_TOP + 7
        for it in items:
            body.append(f'<circle cx="{x+15:.1f}" cy="{cy-5:.1f}" r="3.2" '
                        f'fill="{col["dot"]}"/>')
            body.append(t(x + 27, cy, it, size=SZ_BODY, fill=INK,
                          family=BODYF))
            cy += LINE_H
            if it in NOTE_FOR:
                body.append(t(x + 27, cy - LINE_H + NOTE_H, "↳ " + NOTE_FOR[it],
                              size=SZ_CAPTION, fill=REL, italic=True,
                              family=BODYF))
                cy += NOTE_H

    grid_bottom = max(col_y)

    # ---- footer key ----
    fy = grid_bottom + 4
    body.append(line(M, fy, W - M, fy, RULE, 0.75))
    fy += 22
    body.append(t(M, fy,
                  "Each colour is one oracle family.   "
                  "↳ italic notes name a technique’s closest relative outside "
                  "its family (“is a kind of”, or “audits” for the meta layer).",
                  size=SZ_CAPTION, fill=SECOND, italic=True))
    fy += 24

    H = int(fy + 8)
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
           f'viewBox="0 0 {W} {H}">',
           defs,
           rrect(0, 0, W, H, 0, PAPER)]
    out.extend(body)
    out.append("</svg>")
    return "\n".join(out), (W, H)


def main():
    # Requires the IBM Plex superfamily on the system (fontconfig). Install with:
    #   mkdir -p ~/.fonts/ibmplex && cd ~/.fonts/ibmplex
    #   B=https://raw.githubusercontent.com/google/fonts/main/ofl
    #   curl -LO $B/ibmplexserif/IBMPlexSerif-{Bold,SemiBold,Medium}.ttf
    #   curl -LO $B/ibmplexmono/IBMPlexMono-{Medium,SemiBold}.ttf
    #   # Plex Sans is variable-only on google/fonts; fetch static from IBM/plex:
    #   P=https://cdn.jsdelivr.net/gh/IBM/plex@v6.4.0/IBM-Plex-Sans/fonts/complete/ttf
    #   curl -LO $P/IBMPlexSans-{Regular,Medium,SemiBold,Italic}.ttf && fc-cache -f
    import cairosvg
    here = pathlib.Path(__file__).parent
    svg, (w, h) = build()
    (here / "map-3-hero.svg").write_text(svg, encoding="utf-8")
    cairosvg.svg2png(bytestring=svg.encode(),
                     write_to=str(here / "map-3-hero.png"),
                     output_width=w * 2, output_height=h * 2,
                     background_color=PAPER)
    print(f"wrote map-3-hero.svg / .png  ({w}x{h})")


if __name__ == "__main__":
    main()
