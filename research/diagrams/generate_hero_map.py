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
import colorsys
import pathlib
from html import escape

# --- neutral tokens -----------------------------------------------------------
# Background: a clean cool near-white. Not warm cream — that's the slop list's
# "default tasteful AI surface".
PAPER  = "#fcfcfd"
INK    = "#16161a"
SECOND = "#52525b"
MUTED  = "#86868f"
RULE   = "#e6e6ea"
REL    = "#5b5b62"   # relationship notes

# --- type system --------------------------------------------------------------
# Modern, distinctive, and deliberately not on the impeccable "overused" list
# (Inter, Geist, Space Grotesk, Instrument Serif). Bricolage Grotesque pairs
# a wide humanist display with subtle expressiveness; Hanken Grotesk is a
# clean, refined neutral for body. Two faces — no all-caps eyebrows, so no mono.
DISPLAY = "Bricolage Grotesque"   # title + family card headers
BODYF   = "Hanken Grotesk"        # body, deck, notes, footer

# Committed modular scale (~1.25). Body 16px (skill minimum); display jumps
# hard for the title so hierarchy reads at a glance.
SZ_CAPTION = 13   # notes, footer
SZ_BODY    = 16   # technique labels, deck
SZ_HEADING = 21   # family card headers
SZ_DISPLAY = 38   # title


# --- curated categorical palette (constant S/L => harmonious, not garish) -----
def hsl(h, s, l):
    r, g, b = colorsys.hls_to_rgb(h / 360.0, l, s)
    return f"#{int(r*255+0.5):02x}{int(g*255+0.5):02x}{int(b*255+0.5):02x}"


# 12 hues, gently rotated so neighbours in the column layout don't clash.
HUES = [205, 230, 168, 188, 262, 288, 32, 8, 330, 142, 96, 50]


def family_colors(i):
    h = HUES[i % len(HUES)]
    return {
        "header": hsl(h, 0.46, 0.38),   # header fill — white text sits on it
        "tint":   hsl(h, 0.50, 0.965),  # very light body wash
        "dot":    hsl(h, 0.55, 0.46),
        "key":    hsl(h, 0.52, 0.50),   # gradient-rule stop
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
        ["Contract (Pact)", "Doc / Code sync", "Model-based / Stateful",
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
    "Doc / Code sync":      "guards the docs / code boundary",
    "VCR cassette":         "guards the HTTP boundary",
    "Contract (Pact)":      "guards a consumer / producer boundary",
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

    HDR_H = 60
    PAD_TOP = 16
    LINE_H = 26      # body 16 * ~1.6 — vertical rhythm unit
    NOTE_H = 19
    PAD_BOT = 18

    def card_h(items):
        notes = sum(1 for it in items if it in NOTE_FOR)
        return HDR_H + PAD_TOP + len(items) * LINE_H + notes * NOTE_H + PAD_BOT

    body = []

    # ---- title (Bricolage Grotesque SemiBold, optically tightened) ----
    body.append(t(M, 64, "A map of testing techniques",
                  size=SZ_DISPLAY, weight="600", family=DISPLAY, fill=INK,
                  ls_em=-0.018))
    # deck — one line, measure kept moderate
    body.append(t(M, 94,
                  "Every testing technique, grouped by its oracle — how you "
                  "know the right answer. Colour is the family.",
                  size=SZ_BODY, fill=SECOND))
    # Step-Zero + boundary lens, folded into one quiet italic sentence.
    # No eyebrow, no banner, no editorial scaffolding. Italic is Hanken
    # (Bricolage has no italic master).
    body.append(t(M, 122,
                  "Before any test, encode the invariant in the type when "
                  "you can; otherwise tests live somewhere along  inbound  →  "
                  "typed interior  →  outbound.",
                  size=SZ_BODY, fill=INK, family=BODYF, italic=True))

    # ---- defs: gradient + soft elevation -----------------------------------
    stops = "".join(
        f'<stop offset="{i/(len(FAMILIES)-1)*100:.1f}%" '
        f'stop-color="{family_colors(i)["key"]}"/>'
        for i in range(len(FAMILIES))
    )
    defs = (f'<defs><linearGradient id="famkey" x1="0" y1="0" x2="1" y2="0">'
            f'{stops}</linearGradient>'
            f'<filter id="soft" x="-25%" y="-25%" width="150%" height="160%">'
            f'<feDropShadow dx="0" dy="2" stdDeviation="5" '
            f'flood-color="#0a0a14" flood-opacity="0.08"/></filter></defs>')

    # ---- gradient colour key (no caption — the gradient is self-explaining)
    grad_y = 148
    body.append(rrect(M, grad_y, W - 2 * M, 4, 2, "url(#famkey)"))

    grid_top = grad_y + 28

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
        # Card body with soft elevation only — no border (slop rule: commit
        # to a defined edge OR a soft elevation, never both).
        body.append('<g filter="url(#soft)">'
                    + rrect(x, y, COL_W, h, 10, col["tint"]) + '</g>')
        # Header (Bricolage Grotesque SemiBold + Hanken italic subhead)
        body.append(header_path(x, y, COL_W, HDR_H, 10, col["header"]))
        body.append(t(x + 18, y + 28, head, size=SZ_HEADING, weight="600",
                      family=DISPLAY, fill="#ffffff", ls_em=-0.005))
        body.append(t(x + 18, y + 47, sub, size=SZ_CAPTION, fill="#eef0f3",
                      italic=True, family=BODYF))
        # Techniques (Hanken Grotesk Regular)
        cy = y + HDR_H + PAD_TOP + 8
        for it in items:
            body.append(f'<circle cx="{x+18:.1f}" cy="{cy-5:.1f}" r="3.5" '
                        f'fill="{col["dot"]}"/>')
            body.append(t(x + 30, cy, it, size=SZ_BODY, fill=INK,
                          family=BODYF, weight="500"))
            cy += LINE_H
            if it in NOTE_FOR:
                body.append(t(x + 30, cy - LINE_H + NOTE_H, "→  " + NOTE_FOR[it],
                              size=SZ_CAPTION, fill=REL, italic=True,
                              family=BODYF))
                cy += NOTE_H

    grid_bottom = max(col_y)

    # ---- footer key ----
    fy = grid_bottom + 8
    body.append(line(M, fy, W - M, fy, RULE, 0.6))
    fy += 26
    body.append(t(M, fy,
                  "Each colour is one oracle family.   "
                  "→ italic notes name a technique’s closest relative outside "
                  "its family (“is a kind of”, or “audits” for the meta layer).",
                  size=SZ_CAPTION, fill=SECOND, italic=True))
    fy += 26

    H = int(fy + 8)
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
           f'viewBox="0 0 {W} {H}">',
           defs,
           rrect(0, 0, W, H, 0, PAPER)]
    out.extend(body)
    out.append("</svg>")
    return "\n".join(out), (W, H)


def main():
    # Requires Bricolage Grotesque + Hanken Grotesk on the system (fontconfig).
    # Install (variable TTFs from google/fonts):
    #   mkdir -p ~/.fonts/modern && cd ~/.fonts/modern
    #   B=https://raw.githubusercontent.com/google/fonts/main/ofl
    #   curl -Lo "BricolageGrotesque[opsz,wdth,wght].ttf" \
    #     "$B/bricolagegrotesque/BricolageGrotesque%5Bopsz%2Cwdth%2Cwght%5D.ttf"
    #   curl -Lo "HankenGrotesk[wght].ttf"        "$B/hankengrotesk/HankenGrotesk%5Bwght%5D.ttf"
    #   curl -Lo "HankenGrotesk-Italic[wght].ttf" "$B/hankengrotesk/HankenGrotesk-Italic%5Bwght%5D.ttf"
    #   fc-cache -f ~/.fonts
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
