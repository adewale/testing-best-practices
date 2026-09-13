#!/usr/bin/env python3
"""Generate an SVG map of how testing techniques relate.

Techniques are grouped by their *oracle* (how you know the expected answer),
which is the deepest "relatedness" axis. Overlaid on top: the skill's
trust-boundary lens, the Step-Zero "types replace tests" foundation, and the
meta layer that audits the suite itself.

Sources:
  - testing-best-practices/references/test-types.md   (canonical tiers)
  - research/NOVEL_TESTING_TYPES.md                   (23 niche families)
  - skill-development/evals/taxonomy.md               (technique tags)
"""

from html import escape

W = 1480
MARGIN = 26
COLS = 4
GUTTER = 20
COL_W = (W - 2 * MARGIN - (COLS - 1) * GUTTER) / COLS

HEADER_H = 34
CHIP_H = 30
CHIP_GAP = 8
PAD_TOP = 12
PAD_BOT = 14
CLUSTER_GAP = 18

# --- palette: (header, body, chip-border) -------------------------------------
PAL = {
    "foundation": ("#2563eb", "#eff4ff", "#bfd2fb"),
    "specified":  ("#4f46e5", "#eef0fe", "#c7caf6"),
    "property":   ("#0d9488", "#e7faf6", "#a7e9df"),
    "reference":  ("#0891b2", "#e6fafe", "#a5e9f4"),
    "recorded":   ("#7c3aed", "#f2edfe", "#d6c6fb"),
    "contract":   ("#9333ea", "#f6ecfe", "#e0c6fb"),
    "resilience": ("#d97706", "#fef6e6", "#f7dca0"),
    "security":   ("#dc2626", "#feeceb", "#f6b9b4"),
    "human":      ("#16a34a", "#e9faef", "#a9e7bd"),
    "ai":         ("#db2777", "#fdebf3", "#f6b9d6"),
    "data":       ("#65a30d", "#f1fae0", "#cfe89a"),
    "meta":       ("#475569", "#eef1f5", "#c6cfdb"),
}

# --- clusters: (key, title, subtitle, [chips]) --------------------------------
CLUSTERS = [
    ("foundation", "Tier 1 · Foundation", "always required", [
        "Unit", "Smoke", "Regression (test-before-fix)",
    ]),
    ("specified", "Specified oracle", "you assert exact values", [
        "Table-driven", "Integration", "End-to-End (E2E)",
    ]),
    ("property", "Property / invariant oracle", "assert relations, not values", [
        "Property-based (PBT)", "Metamorphic", "Combinatorial / Pairwise",
        "Bounded-exhaustive",
    ]),
    ("reference", "Reference oracle", "compare to another impl", [
        "Differential", "Pirate / Conformance", "Compatibility (matrix)",
    ]),
    ("recorded", "Recorded oracle", "capture once, replay", [
        "Golden / Snapshot / Approval", "Characterization (legacy)",
        "VCR cassette (HTTP)", "Visual / Screenshot",
    ]),
    ("contract", "Contract / model / spec oracle", "derive from a spec", [
        "Contract (Pact)", "Doc <-> Code sync", "Model-based / Stateful",
        "Spec-based / Formal", "Concolic / Symbolic exec",
    ]),
    ("resilience", "Resilience / non-functional", "stress the system, not logic", [
        "Load", "Stress", "Soak / Endurance",
        "Performance / Benchmark", "Chaos engineering",
    ]),
    ("security", "Security oracle", "find what shouldn't happen", [
        "Penetration / Security scan", "Adversarial / Red-team",
        "Coverage-guided fuzzing",
    ]),
    ("human", "Release-stage & human-driven", "process, not code", [
        "Sanity (vs Smoke)", "Canary / Progressive rollout",
        "Exploratory (session-based)", "ATDD / BDD / Acceptance",
    ]),
    ("ai", "AI-system oracle", "non-deterministic outputs", [
        "LLM eval-driven", "Prompt regression", "Vibes / Semantic assertion",
        "Guardrail", "AI-generated-code verification",
    ]),
    ("data", "Domain-specific", "specialized conformance", [
        "Data-quality / validation", "Accessibility / WCAG",
    ]),
    ("meta", "Meta · audits the suite itself", "tests the tests", [
        "Mutation", "Coverage", "Assertion quality",
    ]),
]

# Greedy column packing balanced by height.
def cluster_height(n):
    return HEADER_H + PAD_TOP + n * CHIP_H + (n - 1) * CHIP_GAP + PAD_BOT


def text(x, y, s, size=13, color="#111827", weight="400", anchor="start",
         family="-apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif"):
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" '
            f'font-family="{family}" font-weight="{weight}" fill="{color}" '
            f'text-anchor="{anchor}">{escape(s)}</text>')


def rrect(x, y, w, h, r, fill, stroke="none", sw=1):
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" '
            f'rx="{r}" ry="{r}" fill="{fill}" stroke="{stroke}" '
            f'stroke-width="{sw}"/>')


def render():
    parts = []

    # --- top band: title + trust-boundary lens -------------------------------
    title_h = 92
    band_y = MARGIN
    parts.append(text(MARGIN, band_y + 24, "How testing techniques relate",
                      size=26, weight="700", color="#0f172a"))
    parts.append(text(MARGIN, band_y + 46,
                      "Grouped by oracle (how you know the right answer). "
                      "Color = oracle family. Badges trace the skill’s trust-boundary lens.",
                      size=13, color="#475569"))

    # trust-boundary strip
    strip_y = band_y + 60
    strip_h = 30
    seg_w = (W - 2 * MARGIN) / 3
    segs = [
        ("INBOUND boundary  ->  parse, don’t validate", "#0e7490", "#cffafe"),
        ("TYPED INTERIOR  ->  behavior on public API", "#4338ca", "#e0e7ff"),
        ("OUTBOUND boundary  ->  contract / VCR / E2E", "#7c3aed", "#ede9fe"),
    ]
    for i, (label, fg, bg) in enumerate(segs):
        x = MARGIN + i * seg_w
        parts.append(rrect(x + (4 if i else 0), strip_y, seg_w - 8, strip_h, 6, bg))
        parts.append(text(x + seg_w / 2, strip_y + 20, label, size=12.5,
                          weight="600", color=fg, anchor="middle"))

    grid_top = band_y + title_h + 18

    # --- Step Zero full-width banner -----------------------------------------
    sz_h = 40
    parts.append(rrect(MARGIN, grid_top, W - 2 * MARGIN, sz_h, 8, "#0f172a"))
    parts.append(text(MARGIN + 16, grid_top + 17, "STEP ZERO  ·  before any test",
                      size=13, weight="700", color="#7dd3fc"))
    parts.append(text(MARGIN + 16, grid_top + 33,
                      "Correctness-by-construction — if a tighter type makes the "
                      "bad state unrepresentable, encode the type and delete the test.",
                      size=12.5, color="#e2e8f0"))

    grid_top += sz_h + CLUSTER_GAP

    # --- pack clusters into balanced columns ---------------------------------
    col_y = [grid_top] * COLS
    placed = []  # (key, title, subtitle, chips, x, y, h)
    for key, title, subtitle, chips in CLUSTERS:
        c = col_y.index(min(col_y))
        x = MARGIN + c * (COL_W + GUTTER)
        y = col_y[c]
        h = cluster_height(len(chips))
        placed.append((key, title, subtitle, chips, x, y, h))
        col_y[c] = y + h + CLUSTER_GAP

    for key, title, subtitle, chips, x, y, h in placed:
        hdr, body, cb = PAL[key]
        # body
        parts.append(rrect(x, y, COL_W, h, 10, body, stroke=cb, sw=1))
        # header
        parts.append(f'<path d="M{x:.1f},{y+10:.1f} a10,10 0 0 1 10,-10 '
                     f'h{COL_W-20:.1f} a10,10 0 0 1 10,10 v{HEADER_H-10} '
                     f'h{-COL_W:.1f} z" fill="{hdr}"/>')
        parts.append(text(x + 12, y + 16, title, size=13.5, weight="700",
                          color="#ffffff"))
        parts.append(text(x + 12, y + 29, subtitle, size=10.5, weight="500",
                          color="#ffffff"))
        # chips
        cy = y + HEADER_H + PAD_TOP
        for chip in chips:
            parts.append(rrect(x + 10, cy, COL_W - 20, CHIP_H, 7, "#ffffff",
                               stroke=cb, sw=1))
            parts.append(text(x + 22, cy + CHIP_H / 2 + 4.5, chip, size=12.5,
                              color="#1f2937"))
            cy += CHIP_H + CHIP_GAP

    grid_bottom = max(col_y)

    # --- relationships legend box --------------------------------------------
    rel_y = grid_bottom + 4
    rel_lines = [
        "How the families connect:",
        "•  Pirate = a symmetric Differential test (the data IS the spec; no impl is privileged).",
        "•  Metamorphic = a relational Property test; Combinatorial/Bounded-exhaustive = input-space coverage strategies for it.",
        "•  Characterization = a Golden/Snapshot test on legacy code where “correct” is unknown — it records what IS, not what SHOULD be.",
        "•  Coverage-guided fuzzing explores execution feedback; Property-based testing generates from declared strategies. They complement each other.",
        "•  Contract / VCR / Doc-sync all guard a boundary against drift between two sides that must agree.",
        "•  Meta layer (Mutation / Coverage / Assertion-quality) doesn’t test the code — it tests whether the suite above would catch a bug.",
        "•  Tiering: solid Tier 1 always; Tier 2 (PBT, small risk-triggered fuzz targets, E2E, contract, VCR, characterization,",
        "    differential, golden, pirate, doc-sync) when triggered; Tier 3 with caution (visual, mutation, performance, long fuzz campaigns).",
        "    Non-functional & release-stage families sit outside the functional tiers.",
    ]
    rel_h = 16 + len(rel_lines) * 18 + 10
    parts.append(rrect(MARGIN, rel_y, W - 2 * MARGIN, rel_h, 10, "#f8fafc",
                       stroke="#e2e8f0", sw=1))
    ty = rel_y + 22
    for i, line in enumerate(rel_lines):
        parts.append(text(MARGIN + 16, ty, line,
                          size=12.5 if i else 13.5,
                          weight="700" if i == 0 else "400",
                          color="#0f172a" if i == 0 else "#334155"))
        ty += 18

    total_h = rel_y + rel_h + MARGIN

    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" '
        f'height="{total_h:.0f}" viewBox="0 0 {W} {total_h:.0f}" '
        f'font-family="-apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif">',
        rrect(0, 0, W, total_h, 0, "#ffffff"),
    ]
    svg.extend(parts)
    svg.append("</svg>")
    return "\n".join(svg)


if __name__ == "__main__":
    import pathlib

    import cairosvg

    out = pathlib.Path(__file__).with_name("testing-techniques-map.svg")
    svg = render()
    out.write_text(svg, encoding="utf-8")
    cairosvg.svg2png(
        bytestring=svg.encode(),
        write_to=str(out.with_suffix(".png")),
        output_width=W * 2,
        background_color="#ffffff",
    )
    print(f"wrote {out.name} / .png ({out.stat().st_size} SVG bytes)")
