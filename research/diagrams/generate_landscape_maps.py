#!/usr/bin/env python3
"""Two README-ready maps of the testing-technique landscape.

Both views preserve the original purpose: show every technique that exists,
grouped by how the families relate. Tufte's discipline is applied to the
ink, not the content — restrained palette (one accent), no colored bars,
typographic hierarchy, and the relationships are DRAWN as light arcs with
labels rather than buried in a text legend.

  View A — refined cluster map (closest to the original; clusters by oracle)
  View B — horizontal taxonomy tree (root -> family -> technique, with
            relationship cross-links)
"""
import pathlib
from html import escape

# --- restrained palette -------------------------------------------------------
PAPER   = "#fbfaf7"
INK     = "#1a1a1a"
RULE    = "#d8d4cc"
GRID    = "#ece9e0"
MUTED   = "#8a857c"
SECOND  = "#6b665d"
ACCENT  = "#b3261e"  # variants / "is a kind of"
LINK    = "#3a6ea5"  # audits / spans (secondary relationship)

SERIF = "Georgia, 'Times New Roman', serif"
SANS  = "-apple-system, 'Segoe UI', Helvetica, Arial, sans-serif"

# --- content ------------------------------------------------------------------
# Each family: (key, header, subhead, [techniques])
FAMILIES = [
    ("foundation", "Foundation",      "tier 1 · always required",
        ["Unit", "Smoke", "Regression"]),
    ("specified",  "Specified oracle", "assert exact values",
        ["Table-driven", "Integration", "End-to-end"]),
    ("property",   "Property / invariant oracle", "assert relations",
        ["Property-based",
         "Metamorphic",
         "Combinatorial / Pairwise",
         "Bounded-exhaustive",
         "Fuzz"]),
    ("reference",  "Reference oracle", "compare to another impl",
        ["Differential", "Pirate / Conformance", "Compatibility"]),
    ("recorded",   "Recorded oracle", "capture & replay",
        ["Golden / Snapshot / Approval",
         "Characterization",
         "VCR cassette",
         "Visual / Screenshot"]),
    ("contract",   "Contract / model / spec oracle", "derive from a spec",
        ["Contract (Pact)",
         "Doc ↔ Code sync",
         "Model-based / Stateful",
         "Spec-based / Formal",
         "Concolic / Symbolic"]),
    ("resilience", "Resilience · non-functional", "stress the system, not logic",
        ["Load", "Stress", "Soak / Endurance",
         "Performance / Benchmark", "Chaos"]),
    ("security",   "Security oracle", "find what shouldn't happen",
        ["Penetration / Security scan", "Adversarial / Red-team"]),
    ("ai",         "AI-system oracle", "non-deterministic outputs",
        ["LLM eval-driven", "Prompt regression",
         "Vibes / Semantic", "Guardrail", "AI-code verification"]),
    ("human",      "Release-stage & human-driven", "process, not code",
        ["Sanity (vs Smoke)", "Canary / Progressive rollout",
         "Exploratory", "ATDD / BDD / Acceptance"]),
    ("data",       "Domain-specific",  "specialised conformance",
        ["Data-quality / validation", "Accessibility / WCAG"]),
    ("meta",       "Meta · audits the suite itself", "tests the tests",
        ["Mutation", "Coverage", "Assertion quality"]),
]

# Cross-family relationships. Rendered as inline italic notes under the
# technique they describe (no arcs — Tufte principle 10, word-data integration).
# (technique, note, kind)   kind in {"variant", "audit"}
LINKS = [
    ("Pirate / Conformance",            "symmetric variant of Differential",     "variant"),
    ("Metamorphic",                     "relational variant of Property-based",  "variant"),
    ("Fuzz",                            "structured = Property-based; security sibling of Red-team", "variant"),
    ("Characterization",                "Golden applied to legacy where correct is unknown", "variant"),
    ("Mutation",                        "audits any suite above",                "audit"),
    ("Coverage",                        "audits any suite above",                "audit"),
    ("Assertion quality",               "audits any suite above",                "audit"),
    ("Doc ↔ Code sync",                 "guards the docs-vs-code boundary",      "variant"),
    ("VCR cassette",                    "guards the HTTP boundary",              "variant"),
    ("Contract (Pact)",                 "guards a consumer-producer boundary",   "variant"),
]
NOTE_FOR = {tech: (note, kind) for tech, note, kind in LINKS}

# ============================================================================
# helpers
# ============================================================================

def t(x, y, s, size=12, fill=INK, weight="400", anchor="start",
      family=SERIF, ls=None, italic=False):
    extra  = f' letter-spacing="{ls}"' if ls else ""
    style  = ' font-style="italic"' if italic else ""
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" '
            f'font-family="{family}" font-weight="{weight}" fill="{fill}" '
            f'text-anchor="{anchor}"{extra}{style}>{escape(s)}</text>')


def line(x1, y1, x2, y2, stroke, w=1, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{stroke}" stroke-width="{w}"{d} stroke-linecap="round"/>')


def path(d, stroke, w=1, dash=None, fill="none"):
    da = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{w}"'
            f'{da} stroke-linecap="round"/>')


def svg_open(w, h):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
            f'viewBox="0 0 {w} {h}">\n<rect width="{w}" height="{h}" '
            f'fill="{PAPER}"/>')


# ============================================================================
# View A — refined cluster map
# ============================================================================
def view_cluster_map():
    W = 1520
    MARGIN = 30
    COLS = 4
    GUTTER = 26
    COL_W = (W - 2 * MARGIN - (COLS - 1) * GUTTER) / COLS

    HDR_H   = 36   # header + subhead per cluster
    LINE_H  = 22   # one technique
    NOTE_H  = 14   # italic relationship note line under a technique
    PAD_TOP = 8
    PAD_BOT = 18
    GAP_V   = 22   # between clusters

    def cluster_h(items):
        n = len(items)
        notes = sum(1 for it in items if it in NOTE_FOR)
        return HDR_H + PAD_TOP + n * LINE_H + notes * NOTE_H + PAD_BOT

    p = [svg_open(W, 100)]  # placeholder height; we recompute

    # --- header band ---------------------------------------------------------
    p.append(t(MARGIN, 56, "A map of testing techniques",
               size=28, weight="700"))
    p.append(t(MARGIN, 84,
               "Every technique the skill knows about, grouped by its oracle "
               "(how you know the right answer).",
               size=13.5, fill=SECOND))
    p.append(t(MARGIN, 102,
               "Notes in red read “is a kind of”;  notes in blue read "
               "“audits the suites above”.",
               size=12, fill=MUTED, italic=True))

    # trust-boundary strip (thin, one row, no colored fills)
    sb_y = 124
    seg_w = (W - 2 * MARGIN) / 3
    labels = [
        "INBOUND  ·  parse, don’t validate",
        "TYPED INTERIOR  ·  behaviour on the public API",
        "OUTBOUND  ·  contract / VCR / E2E",
    ]
    p.append(line(MARGIN, sb_y, W - MARGIN, sb_y, RULE, 0.75))
    for i, lab in enumerate(labels):
        x = MARGIN + i * seg_w
        if i > 0:
            p.append(line(x, sb_y - 8, x, sb_y + 8, RULE, 0.75))
        p.append(t(x + seg_w / 2, sb_y - 6, lab, size=10.5, fill=SECOND,
                   anchor="middle", family=SANS, ls="0.08em"))

    # Step Zero banner (single thin frame, restrained)
    sz_y = sb_y + 18
    sz_h = 40
    p.append(line(MARGIN, sz_y, W - MARGIN, sz_y, INK, 0.75))
    p.append(line(MARGIN, sz_y + sz_h, W - MARGIN, sz_y + sz_h, INK, 0.75))
    p.append(t(MARGIN + 4, sz_y + 17, "STEP ZERO",
               size=11, fill=ACCENT, weight="700",
               family=SANS, ls="0.12em"))
    p.append(t(MARGIN + 100, sz_y + 17,
               "before any test — correctness-by-construction",
               size=12.5, fill=INK, weight="600"))
    p.append(t(MARGIN + 4, sz_y + 33,
               "If a tighter type makes the bad state unrepresentable, "
               "encode the type and delete the test.",
               size=11.5, fill=SECOND, italic=True))

    grid_top = sz_y + sz_h + GAP_V

    # --- pack clusters into balanced columns ---------------------------------
    col_y = [grid_top] * COLS
    placed = {}   # key -> (x, y, h)

    for key, head, sub, items in FAMILIES:
        c = col_y.index(min(col_y))
        x = MARGIN + c * (COL_W + GUTTER)
        y = col_y[c]
        h = cluster_h(items)
        placed[key] = (x, y, h)
        col_y[c] = y + h + GAP_V

        # header bar — typographic, not coloured
        p.append(t(x, y + 14, head, size=13.5, weight="700",
                   family=SERIF, fill=INK))
        p.append(t(x, y + 30, sub, size=11, fill=MUTED, italic=True))
        p.append(line(x, y + 36, x + COL_W, y + 36, RULE, 0.75))

        cy = y + HDR_H + PAD_TOP + 12
        for item in items:
            p.append(t(x + 4, cy, "·", size=14, fill=MUTED))
            p.append(t(x + 16, cy, item, size=12.5, fill=INK, family=SANS))
            cy += LINE_H
            if item in NOTE_FOR:
                note, kind = NOTE_FOR[item]
                colour = ACCENT if kind == "variant" else LINK
                p.append(t(x + 22, cy - LINE_H + NOTE_H,
                           "↳ " + note,
                           size=10.5, fill=colour, italic=True, family=SERIF))
                cy += NOTE_H

    grid_bottom = max(col_y)
    leg_y = grid_bottom

    H = leg_y + MARGIN
    # patch the opening svg height
    p[0] = svg_open(W, int(H))
    p.append("</svg>")
    return "\n".join(p), (W, int(H))


# ============================================================================
# View B — horizontal taxonomy tree
# ============================================================================
def view_tree():
    W = 1520
    MARGIN_L = 36
    MARGIN_R = 36

    # 3 columns: root  | family  | techniques
    ROOT_X    = MARGIN_L + 8
    FAMILY_X  = MARGIN_L + 220
    TECH_X    = MARGIN_L + 540
    MARGIN_L + 920
    LINE_H    = 22
    FAM_GAP   = 18  # extra gap between families

    p = [svg_open(W, 100)]
    p.append(t(MARGIN_L, 56, "Testing techniques · taxonomy by oracle",
               size=26, weight="700"))
    p.append(t(MARGIN_L, 82,
               "Read left → right: root, then family of oracle, then the "
               "techniques in that family. The right column notes the closest "
               "relatives outside the family.",
               size=13, fill=SECOND))

    top = 124
    # root marker
    root_y = top + 12
    p.append(t(ROOT_X, root_y, "Testing techniques",
               size=14, weight="700", family=SERIF, fill=INK))
    p.append(line(ROOT_X, root_y + 8, ROOT_X + 130, root_y + 8, INK, 0.75))

    # walk families
    tech_y_positions = {}   # technique -> y for cross-links
    family_y_centres = {}   # key -> (top_y, bottom_y, mid_y)

    y = top
    for key, head, sub, items in FAMILIES:
        fam_top = y
        # family node
        p.append(t(FAMILY_X, y + 14, head,
                   size=13, weight="700", family=SERIF, fill=INK))
        p.append(t(FAMILY_X, y + 30, sub,
                   size=10.5, fill=MUTED, italic=True))
        # connector from root to family — only once, at the family's vertical centre
        y + 14
        # technique nodes
        ty = y + 14
        for it in items:
            tech_y_positions[it] = ty
            p.append(t(TECH_X + 14, ty, it,
                       size=12.5, fill=INK, family=SANS))
            # family -> technique branch
            p.append(line(FAMILY_X + 200, ty - 4, TECH_X + 10, ty - 4,
                          RULE, 0.6))
            ty += LINE_H
        fam_bottom = ty - LINE_H + 4
        # root -> family branch (vertical drop + horizontal)
        # we draw later because root is fixed; just record
        family_y_centres[key] = (fam_top + 14, fam_bottom, (fam_top + fam_bottom) / 2)
        y = ty + FAM_GAP

    grid_bottom = y

    # draw root->family branches
    fam_centres_y = [c[2] for c in family_y_centres.values()]
    if fam_centres_y:
        top_c, bot_c = min(fam_centres_y), max(fam_centres_y)
        # vertical spine from root
        spine_x = (ROOT_X + 130 + FAMILY_X) / 2
        p.append(line(ROOT_X + 130, root_y - 4, spine_x, root_y - 4, INK, 0.75))
        p.append(line(spine_x, root_y - 4, spine_x, top_c - 4, INK, 0.75))
        p.append(line(spine_x, top_c - 4, spine_x, bot_c - 4, RULE, 0.6))
        for cx in fam_centres_y:
            p.append(line(spine_x, cx - 4, FAMILY_X - 6, cx - 4, RULE, 0.6))

    # --- cross-links (relationships) — inline italic notes on each related row
    for tech, (note, kind) in NOTE_FOR.items():
        if tech not in tech_y_positions:
            continue
        sy = tech_y_positions[tech] - 4
        stroke = ACCENT if kind == "variant" else LINK
        p.append(t(TECH_X + 380, sy + 3, "↳ " + note,
                   size=11, fill=stroke, italic=True))

    # legend
    leg_y = grid_bottom + 4
    p.append(line(MARGIN_L, leg_y, W - MARGIN_R, leg_y, RULE, 0.75))
    leg_y += 22
    p.append(t(MARGIN_L, leg_y,
               "Notes in red read “is a kind of”;  notes in blue read “audits the suites above”.",
               size=11.5, fill=SECOND, italic=True))
    leg_y += 26
    H = leg_y + 14
    p[0] = svg_open(W, int(H))
    p.append("</svg>")
    return "\n".join(p), (W, int(H))


# ============================================================================
def main():
    import cairosvg
    here = pathlib.Path(__file__).parent
    views = {
        "map-1-cluster-refined": view_cluster_map,
        "map-2-taxonomy-tree":   view_tree,
    }
    for name, fn in views.items():
        svg, (w, h) = fn()
        (here / f"{name}.svg").write_text(svg, encoding="utf-8")
        cairosvg.svg2png(
            bytestring=svg.encode(),
            write_to=str(here / f"{name}.png"),
            output_width=w * 2,
            output_height=h * 2,
            background_color=PAPER,
        )
        print(f"wrote {name}.svg / .png  ({w}x{h})")


if __name__ == "__main__":
    main()
