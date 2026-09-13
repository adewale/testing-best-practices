#!/usr/bin/env python3
"""A faithful map of the testing-best-practices skill.

Shows exactly the techniques the skill teaches in
references/test-types.md, organized by the skill's own tier structure
(always / when triggered / with caution). Step Zero and the trust-boundary
lens fold into the italic sentence at the top.

This differs from map-3-hero (the universe map) by including ONLY the
techniques the skill itself teaches — not the broader research catalogue
in research/NOVEL_TESTING_TYPES.md.

Requires Bricolage Grotesque + Hanken Grotesk on the system; see
generate_hero_map.py for install commands.
"""
import colorsys
import pathlib
from html import escape

# --- design tokens (consistent with map-3-hero) ------------------------------
PAPER  = "#fcfcfd"
INK    = "#16161a"
SECOND = "#52525b"
MUTED  = "#86868f"
RULE   = "#e6e6ea"
REL    = "#5b5b62"

DISPLAY = "Bricolage Grotesque"
BODYF   = "Hanken Grotesk"

SZ_CAPTION = 13
SZ_BODY    = 16
SZ_SUBHEAD = 18
SZ_HEADING = 22
SZ_SECTION = 24
SZ_DISPLAY = 38


def hsl(h, s, l):
    r, g, b = colorsys.hls_to_rgb(h / 360.0, l, s)
    return f"#{int(r*255+0.5):02x}{int(g*255+0.5):02x}{int(b*255+0.5):02x}"


# --- three-tier palette -------------------------------------------------------
# A coherent earthy modern palette: cool foundation, warm trigger, muted wine
# caution. Not traffic-lights — saturation and lightness held even, so the
# three colours read as a single designed set.
TIER_HUES = {"t1": 200, "t2": 28, "t3": 340}


def tier_colors(h):
    return {
        "ink":   hsl(h, 0.55, 0.32),   # tier-toned heading colour
        "dot":   hsl(h, 0.55, 0.46),   # accent dot on cards
        "wash":  hsl(h, 0.55, 0.97),   # very faint band tint
    }


# --- skill content from references/test-types.md ----------------------------
TIERS_META = [
    ("t1", "Tier 1 · Foundation",   "Always required.",
        "Three tests every project needs from day one.", 3),
    ("t2", "Tier 2 · Triggered",    "Required when triggered.",
        "Add when the project’s situation calls for them.", 3),
    ("t3", "Tier 3 · With caution", "Real value, real costs.",
        "Use when the trade-off genuinely earns the test back.", 4),
]

# Each tier: list of (technique, one-line trigger from test-types.md).
TECHNIQUES = {
    "t1": [
        ("Unit",       "Every function with non-trivial logic — ifs, loops, arithmetic."),
        ("Smoke",      "Every deployable unit — the app starts and responds."),
        ("Regression", "After every bug fix — write the failing test before the fix."),
    ],
    "t2": [
        ("Property-based",       "Parsers, serializers, transforms, rankings — anything generative."),
        ("Fuzz target",           "Hostile-input boundary with amplifying risk and a coverage-guided engine."),
        ("End-to-end",           "HTTP endpoints, CLI workflows, or a platform-specific runtime."),
        ("Doc / Code sync",      "CLI commands, plugin hooks, or config described in docs."),
        ("Contract",             "Anywhere unit tests rely on mocks for external services."),
        ("VCR cassette",         "Code calls third-party APIs (LLM, payment, auth)."),
        ("Characterization",     "Refactoring legacy code without an existing test suite."),
        ("Differential",         "Reimplementing a known algorithm against a trusted reference."),
        ("Golden file",          "Input-to-output file transforms; complex generated output."),
        ("Pirate / Conformance", "Multi-language SDKs of one specification."),
    ],
    "t3": [
        ("Visual / Screenshot",  "UI-heavy projects where pixel layout matters."),
        ("Mutation",             "Critical modules; or when coverage is high but bugs still escape."),
        ("Performance",          "When a 2× slowdown would be a user-visible bug."),
        ("Long fuzz campaigns",  "When sustained coverage growth earns scheduled compute and triage."),
    ],
}

# Cross-technique relationships among only the skill-taught techniques.
NOTE_FOR = {
    "Pirate / Conformance": "symmetric variant of Differential",
    "Characterization":     "Golden applied to legacy code",
    "Doc / Code sync":      "guards the docs / code boundary",
    "VCR cassette":         "guards the HTTP boundary",
    "Contract":             "guards a consumer / producer boundary",
    "Mutation":             "audits the suites above",
    "Fuzz target":          "coverage-guided discovery complements Property-based tests",
    "Long fuzz campaigns":  "the same target at a larger discovery budget",
}


# --- svg helpers --------------------------------------------------------------
def t(x, y, s, size=SZ_BODY, fill=INK, weight="400", anchor="start",
      family=BODYF, ls_em=None, italic=False):
    extra = f' letter-spacing="{ls_em*size:.2f}"' if ls_em else ""
    style = ' font-style="italic"' if italic else ""
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" '
            f'font-family="{family}" font-weight="{weight}" fill="{fill}" '
            f'text-anchor="{anchor}" font-kerning="normal"{extra}{style}'
            f'>{escape(s)}</text>')


def rrect(x, y, w, h, r, fill, stroke="none", sw=1):
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" '
            f'rx="{r}" ry="{r}" fill="{fill}" stroke="{stroke}" '
            f'stroke-width="{sw}"/>')


def line(x1, y1, x2, y2, stroke, w=1):
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{stroke}" stroke-width="{w}" stroke-linecap="round"/>')


def wrap(text, max_chars):
    """Greedy word-wrap to ≤max_chars lines."""
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
    W = 1540
    M = 32
    GUT = 18
    BAND_GAP = 30

    body = []

    # ----- title block ------------------------------------------------------
    body.append(t(M, 62, "Testing — best practices",
                  size=SZ_DISPLAY, weight="700", family=DISPLAY, fill=INK,
                  ls_em=-0.018))
    body.append(t(M, 92,
                  "Seventeen practices in three tiers — always, when "
                  "triggered, with caution.",
                  size=SZ_BODY, fill=SECOND))
    body.append(t(M, 120,
                  "Before any test, encode the invariant in the type when "
                  "you can; otherwise tests live somewhere along  inbound  "
                  "->  typed interior  ->  outbound.",
                  size=SZ_BODY, fill=INK, family=BODYF, italic=True))

    # ----- defs (soft shadow only — no border) ------------------------------
    defs = ('<defs>'
            '<filter id="soft" x="-25%" y="-25%" width="150%" height="160%">'
            '<feDropShadow dx="0" dy="2" stdDeviation="5" '
            'flood-color="#0a0a14" flood-opacity="0.07"/></filter>'
            '</defs>')

    y = 160

    for tier_key, tier_title, tier_kicker, tier_desc, cols in TIERS_META:
        col = tier_colors(TIER_HUES[tier_key])

        # ---- tier heading ------------------------------------------------
        # NOT an uppercase tracked eyebrow — a proper section heading.
        body.append(t(M, y + 22, tier_title,
                      size=SZ_SECTION, weight="700", family=DISPLAY,
                      fill=col["ink"], ls_em=-0.012))
        # Roman subhead beside it
        # Compute rough x offset based on title length (em ~ 13px at 24px)
        title_w = len(tier_title) * 13
        body.append(t(M + title_w + 14, y + 22, tier_kicker,
                      size=SZ_SUBHEAD, weight="500", family=DISPLAY,
                      fill=INK))
        body.append(t(M, y + 42, tier_desc,
                      size=SZ_BODY - 1, fill=MUTED, italic=True))

        y += 58

        # ---- card grid ---------------------------------------------------
        techs = TECHNIQUES[tier_key]
        card_w = (W - 2 * M - (cols - 1) * GUT) / cols
        n = len(techs)
        rows = (n + cols - 1) // cols

        # body line measure (chars/line) — Hanken ~7.5px per char at 15px
        meas = int((card_w - 36) / 7.5)

        def card_height(name, trigger, has_note, measure=meas):
            tlines = wrap(trigger, measure)
            HDR_PAD_TOP = 22
            BODY_TOP    = 22
            LINE_H      = 22
            NOTE_GAP    = 8
            NOTE_H      = 19
            PAD_BOT     = 18
            return (HDR_PAD_TOP + LINE_H + BODY_TOP
                    + len(tlines) * LINE_H
                    + (NOTE_GAP + NOTE_H if has_note else 0)
                    + PAD_BOT)

        for r in range(rows):
            row = techs[r * cols:(r + 1) * cols]
            row_h = max(card_height(nm, tr, nm in NOTE_FOR) for nm, tr in row)

            for c, (name, trigger) in enumerate(row):
                x = M + c * (card_w + GUT)

                # Card — white surface, soft elevation, no border.
                body.append('<g filter="url(#soft)">'
                            + rrect(x, y, card_w, row_h, 10, "#ffffff")
                            + '</g>')
                # Tier accent: a small coloured dot at top-left, with the
                # technique name beside it. Quiet — no banner, no stripe.
                cx = x + 22
                cy = y + 32
                body.append(f'<circle cx="{cx:.1f}" cy="{cy-7:.1f}" r="5" '
                            f'fill="{col["dot"]}"/>')
                body.append(t(cx + 14, cy, name,
                              size=SZ_HEADING, weight="700", family=DISPLAY,
                              fill=INK, ls_em=-0.008))

                # Trigger
                tlines = wrap(trigger, meas)
                ty = cy + 32
                for ln in tlines:
                    body.append(t(x + 22, ty, ln,
                                  size=SZ_BODY - 1, fill=SECOND,
                                  family=BODYF))
                    ty += 22

                # Inline relationship note
                if name in NOTE_FOR:
                    body.append(t(x + 22, ty + 6, "->  " + NOTE_FOR[name],
                                  size=SZ_CAPTION, fill=REL, italic=True,
                                  family=BODYF))

            y += row_h + 14

        y += BAND_GAP - 14

    # ---- footer ---------------------------------------------------------
    y += 4
    body.append(line(M, y, W - M, y, RULE, 0.6))
    y += 26
    body.append(t(M, y,
                  "Colour is the tier.  Italic notes name a technique’s "
                  "closest relative or the boundary it guards. "
                  "See references/test-types.md for triggers, costs, "
                  "and full rules.",
                  size=SZ_CAPTION, fill=SECOND, italic=True))
    y += 26

    H = int(y + 16)
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
           f'viewBox="0 0 {W} {H}">',
           defs,
           rrect(0, 0, W, H, 0, PAPER)]
    out.extend(body)
    out.append("</svg>")
    return "\n".join(out), (W, H)


def main():
    import cairosvg
    here = pathlib.Path(__file__).parent
    svg, (w, h) = build()
    (here / "skill-map.svg").write_text(svg, encoding="utf-8")
    cairosvg.svg2png(bytestring=svg.encode(),
                     write_to=str(here / "skill-map.png"),
                     output_width=w * 2, output_height=h * 2,
                     background_color=PAPER)
    print(f"wrote skill-map.svg / .png  ({w}x{h})")


if __name__ == "__main__":
    main()
