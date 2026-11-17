#!/usr/bin/env python3
"""Deterministic 4-Panel Architectural Visual Generator for HODGE-MILLENNIUM-001.

Generates ``06_Hodge_Diamond_and_WD4_Coset_Transport_Visual.png`` showing:
  Panel A: 4-Band Cyclotomic Decomposition of H^{2,2}_prim(X^4_6) (1001+630+120+0=1751)
           and the Palindromic Artinian Gorenstein Socle Profile (d = 0..24, peak 1751 at d=12).
  Panel B: Deformed Macaulay Rank Stabilization (m = 1..6): unlifted rank jump [9,23,45,71,91,98]
           collapsing onto the flat quadric target [8,18,32,48,60,64] under quadric recombination.
  Panel C: Multi-Axis W(D_4) Weyl-Coset & Clifford Triality Transfer on Lambda^4 S^+_8 = 35_+ + 35_-
           (16 pure Weil loci + 12D so(8)/u(4) coset spanning 6/6 of K_{2,2}).
  Panel D: Lean 4.35.0 Finite Combinatorial Checks (43 decidable `by rfl` declarations,
           zero Mathlib imports -> Open Bridges A & B -> GLOBAL_HODGE_CONJECTURE = OPEN).

Visualization helper script (separate from the zero-float Python verification engines).
Credit: Always Qamar Munawer (Brandenburg University of Technology Cottbus-Senftenberg).
"""

from __future__ import annotations

import pathlib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches


ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT_PNG = ROOT / "06_Hodge_Diamond_and_WD4_Coset_Transport_Visual.png"

# Exact palindromic Artinian Gorenstein Hilbert series for R(F_0) = Q[x_0..x_5]/(x_0^5..x_5^5)
CY4_HILBERT_SERIES = [
    1, 6, 21, 56, 126, 246, 426, 666, 951, 1246, 1506, 1686,
    1751,
    1686, 1506, 1246, 951, 666, 426, 246, 126, 56, 21, 6, 1,
]


def build_four_panel_figure(out_path: pathlib.Path = OUT_PNG) -> pathlib.Path:
    """Render the high-resolution 4-panel visual architecture PNG."""
    plt.rcParams.update({
        "font.family": "DejaVu Sans",
        "axes.edgecolor": "#334155",
        "axes.linewidth": 0.9,
    })

    fig, axes = plt.subplots(2, 2, figsize=(15.5, 11.2), dpi=240)
    fig.patch.set_facecolor("#F8FAFC")

    fig.suptitle(
        "HODGE-MILLENNIUM-001: Four-Pillar Structural Reductions, Deformed Apolarity & W(D4) Transport\n"
        "Edition 1.0.0 (MATH-GOV v0.7)  |  GLOBAL_HODGE_CONJECTURE = OPEN  |  Credit: Qamar Munawer (BTU Cottbus-Senftenberg)",
        fontsize=13.5,
        fontweight="bold",
        color="#0F172A",
        y=0.975,
    )

    # ------------------------------------------------------------------
    # PANEL A: Palindromic Gorenstein Socle Profile + 4-Band Split (d=12)
    # ------------------------------------------------------------------
    ax_a = axes[0, 0]
    ax_a.set_facecolor("#FFFFFF")
    degs = list(range(25))
    ax_a.fill_between(degs, CY4_HILBERT_SERIES, color="#DBEAFE", alpha=0.85)
    ax_a.plot(degs, CY4_HILBERT_SERIES, color="#1D4ED8", linewidth=2.2, marker="o", markersize=4)

    # Highlight R^6 (moduli = 426) and R^12 (H^{2,2}_prim = 1751)
    ax_a.scatter([6, 12, 18], [426, 1751, 426], color=["#059669", "#B91C1C", "#059669"], s=68, zorder=5)
    ax_a.annotate(
        "Moduli R^6(F_0)\ndim = 426\n(24 - 6 = 18 dual)",
        xy=(6, 426), xytext=(0.4, 720),
        fontsize=8.0, fontweight="bold", color="#065F46",
        arrowprops=dict(arrowstyle="->", color="#059669", lw=1.2),
        bbox=dict(boxstyle="round,pad=0.3", fc="#ECFDF5", ec="#059669", lw=0.8),
    )
    ax_a.annotate(
        "Peak Middle Slice R^12 = H^{2,2}_prim\ndim = 1,751 (mu = 5^6 = 15,625)\n"
        "B1: 1,001 | B2: 630 | B3: 120 | B4: 0",
        xy=(12, 1751), xytext=(12.6, 1460),
        fontsize=7.7, fontweight="bold", color="#7F1D1D",
        arrowprops=dict(arrowstyle="->", color="#B91C1C", lw=1.2),
        bbox=dict(boxstyle="round,pad=0.32", fc="#FEF2F2", ec="#DC2626", lw=0.9),
    )

    # Inset horizontal stacked bar of the 4-band split (1001 + 630 + 120 + 0)
    inset = ax_a.inset_axes([0.05, 0.72, 0.37, 0.14])
    inset.barh([0], [1001], color="#1D4ED8", label="B1: 1001")
    inset.barh([0], [630], left=[1001], color="#0284C7", label="B2: 630")
    inset.barh([0], [120], left=[1631], color="#14B8A6", label="B3: 120")
    inset.set_xlim(0, 1751)
    inset.set_yticks([])
    inset.set_xticks([0, 1001, 1751])
    inset.tick_params(axis="x", labelsize=6.8)
    inset.set_title("4-Band Split (1001+630+120+0 = 1751)", fontsize=7.3, fontweight="bold", pad=2)
    for b, lbl in [(500, "1001"), (1316, "630"), (1691, "120")]:
        inset.text(b, 0, lbl, va="center", ha="center", color="white", fontsize=6.9, fontweight="bold")

    ax_a.set_title("Panel A: Artinian Gorenstein Profile & 4-Band Partition of X^4_6", fontsize=10.5, fontweight="bold", color="#0F172A")
    ax_a.set_xlabel("Polynomial Degree d in R(F_0) = Q[x_0..x_5]/(x_0^5..x_5^5)  [Socle d=24]", fontsize=8.8)
    ax_a.set_ylabel("dim_Q R^d(F_0)", fontsize=9)
    ax_a.set_xlim(-0.5, 24.5)
    ax_a.set_ylim(0, 2000)
    ax_a.grid(True, linestyle="--", alpha=0.35)

    # ------------------------------------------------------------------
    # PANEL B: Deformed Macaulay Rank Stabilization (m = 1..6)
    # ------------------------------------------------------------------
    ax_b = axes[0, 1]
    ax_b.set_facecolor("#FFFFFF")
    m_vals = [1, 2, 3, 4, 5, 6]
    unlifted = [9, 23, 45, 71, 91, 98]
    quadric_target = [8, 18, 32, 48, 60, 64]
    plane_target = [3, 6, 10, 15, 18, 19]

    ax_b.plot(m_vals, unlifted, marker="^", linewidth=2.2, color="#DC2626", linestyle="--",
              label="Unlifted Obstructed Jump: [9, 23, 45, 71, 91, 98] (Sum=337)")
    ax_b.plot(m_vals, quadric_target, marker="s", linewidth=2.4, color="#059669",
              label="Moving Quadric Target: [8, 18, 32, 48, 60, 64] (Sum=230)")
    ax_b.plot(m_vals, plane_target, marker="o", linewidth=2.0, color="#2563EB",
              label="2-Plane / Coupled CY4 Anchor: [3, 6, 10, 15, 18, 19] (+1 at m=0 -> 72)")

    ax_b.fill_between(m_vals, quadric_target, unlifted, color="#FEE2E2", alpha=0.65,
                      label="Cancelled 2nd-Order Obstruction Excess (Delta=107)")

    for x, y_u, y_q in zip(m_vals, unlifted, quadric_target):
        ax_b.text(x, y_u + 2.8, str(y_u), ha="center", fontsize=8, color="#991B1B", fontweight="bold")
        ax_b.text(x, y_q - 6.2, str(y_q), ha="center", fontsize=8, color="#065F46", fontweight="bold")

    ax_b.text(
        1.05, 84,
        "407/407 Tangential Leibniz Closure\n1,325-dim Universal Kernel\n0.56s 61-bit CRT Non-Fermat Cert",
        fontsize=7.7, color="#1E3A8A",
        bbox=dict(boxstyle="round,pad=0.32", fc="#EFF6FF", ec="#3B82F6", lw=0.8),
    )

    ax_b.set_title("Panel B: Deformed Macaulay Rank Stabilization & Obstruction Cancellation", fontsize=10.5, fontweight="bold", color="#0F172A")
    ax_b.set_xlabel("Testing Degree m in Macaulay Matrix M^(m)_Lambda", fontsize=8.8)
    ax_b.set_ylabel("Exact Q / Z/pZ Matrix Rank", fontsize=9)
    ax_b.set_xticks(m_vals)
    ax_b.set_ylim(0, 118)
    ax_b.grid(True, linestyle="--", alpha=0.35)
    ax_b.legend(loc="upper left", bbox_to_anchor=(0.01, 0.72), fontsize=7.0, framealpha=0.95)

    # ------------------------------------------------------------------
    # PANEL C: Multi-Axis W(D_4) Weyl-Coset & Triality Transport (Schematic)
    # ------------------------------------------------------------------
    ax_c = axes[1, 0]
    ax_c.set_facecolor("#FFFFFF")
    ax_c.set_xlim(0, 10)
    ax_c.set_ylim(0, 10)
    ax_c.axis("off")
    ax_c.set_title("Panel C: Mumford Spinor Sixfold A_6, Clifford Triality & W(D_4) Coset Spanning", fontsize=10.5, fontweight="bold", color="#0F172A")

    def draw_box(ax, xy, w, h, title, body, fc, ec, title_c="#0F172A"):
        rect = mpatches.FancyBboxPatch(
            xy, w, h, boxstyle="round,pad=0.18,rounding_size=0.25",
            facecolor=fc, edgecolor=ec, linewidth=1.4,
        )
        ax.add_patch(rect)
        ax.text(xy[0] + w / 2, xy[1] + h - 0.42, title, ha="center", va="top",
                fontsize=8.6, fontweight="bold", color=title_c)
        ax.text(xy[0] + w / 2, xy[1] + h / 2 - 0.35, body, ha="center", va="center",
                fontsize=7.8, color="#1E293B", linespacing=1.25)

    draw_box(
        ax_c, (0.4, 7.1), 4.1, 2.3,
        "Schur Vacuum Trap (Mumford 1969)",
        "End_g(S^+_8) = Q  =>  rho(A_6) = 1\n"
        "Stacked root rank = 6  =>  ker = 0\n"
        "Zero trivial so(8)-singlets in K_{2,2}",
        "#FEF2F2", "#DC2626", "#991B1B",
    )
    draw_box(
        ax_c, (5.5, 7.1), 4.1, 2.3,
        "C^+(V_8) Triality Transfer (Thm 19)",
        "dim C^+(V_8) = 128  |  32 zero-wt triples\n"
        "Transfers K3 classes across 70 / 70\n"
        "of Lambda^4 S^+_8 = 35_+ + 35_-",
        "#EFF6FF", "#2563EB", "#1E40AF",
    )
    draw_box(
        ax_c, (0.4, 3.8), 4.1, 2.3,
        "SU(2,2) x U(1) Branching (Thm 29)",
        "Restrict D_4 -> D_3 x U(1)\n"
        "8 = 2 (Pure Weil W_0) + 6 (Mixed K_{2,2})\n"
        "Isolates 2 + 1 = 3 SU(2,2) Singlets",
        "#F0FDF4", "#16A34A", "#166534",
    )
    draw_box(
        ax_c, (5.5, 3.8), 4.1, 2.3,
        "W(D_4) Weyl-Coset Inversion (Thm 32)",
        "|W(D_4)| = 192  |  12D so(8)/u(4) coset\n"
        "16 coordinate + Hadamard Weil loci\n"
        "Spans 6 / 6 (rank 6 det!=0 B_Weyl)",
        "#ECFDF5", "#059669", "#065F46",
    )
    draw_box(
        ax_c, (0.6, 0.45), 8.8, 2.25,
        "OPEN BRIDGE B: S-BRIDGE-SPINOR-MOTIVE (Not Yet Algebraic Over Q)",
        "Triality + W(D_4) span aligns with Deligne Absolute Hodge & Andre Motivated theory,\n"
        "but algebraic realization in CH^*(A_6)_Q remains OPEN:\n"
        "requires kuga_satake_algebraic_cycle_over_Q & chow_flatness_mumford_sixfold.",
        "#FFFBEB", "#D97706", "#92400E",
    )

    arrow_kw = dict(arrowstyle="->,head_width=0.25,head_length=0.25", color="#334155", lw=1.4)
    ax_c.annotate("", xy=(5.45, 8.25), xytext=(4.55, 8.25), arrowprops=arrow_kw)
    ax_c.annotate("", xy=(2.45, 6.2), xytext=(2.45, 7.05), arrowprops=arrow_kw)
    ax_c.annotate("", xy=(5.45, 4.95), xytext=(4.55, 4.95), arrowprops=arrow_kw)
    ax_c.annotate("", xy=(7.55, 6.2), xytext=(7.55, 7.05), arrowprops=arrow_kw)
    ax_c.annotate("", xy=(5.0, 2.8), xytext=(5.0, 3.75), arrowprops=dict(arrowstyle="->", color="#B45309", lw=1.6, linestyle="--"))

    # ------------------------------------------------------------------
    # PANEL D: Lean 4.35.0 Combinatorial & Epistemic Architecture
    # ------------------------------------------------------------------
    ax_d = axes[1, 1]
    ax_d.set_facecolor("#FFFFFF")
    ax_d.set_xlim(0, 10)
    ax_d.set_ylim(0, 10)
    ax_d.axis("off")
    ax_d.set_title("Panel D: Computational Toolkit, Combinatorial Lean Checks & Open Bridges", fontsize=10.5, fontweight="bold", color="#0F172A")

    draw_box(
        ax_d, (0.3, 7.35), 9.4, 2.05,
        "COMBINATORIAL LEAN CHECKS (43 by-rfl Checks, 0 Mathlib) & 19 Zero-Float Engines",
        "HodgeVerification.lean (core Lean 4.35.0, axioms == [], finite index/degree arithmetic only)\n"
        "Exact Rational & F_p Computational Experiments on Sextic Fourfolds & Mumford Weight Sets\n"
        "407/407 Leibniz | 1,325 Kernel Dim | 61-bit CRT + Wang Lift | Z_22 -> Q_2 Liaison | W(D_4) 6/6 Span",
        "#EFF6FF", "#1D4ED8", "#1E3A8A",
    )
    draw_box(
        ax_d, (0.3, 4.05), 4.45, 2.45,
        "OPEN BRIDGE A (CY4 Realization)",
        "Unresolved Geometric Obstacles:\n"
        "1. Effective Hilbert degree bound (CY4)\n"
        "2. Global non-Fermat Macaulay stabilization\n"
        "Status: S-BRIDGE-DEFORM-CY4 = OPEN",
        "#FFF7ED", "#EA580C", "#9A3412",
    )
    draw_box(
        ax_d, (5.25, 4.05), 4.45, 2.45,
        "OPEN BRIDGE B (Spinor Motive)",
        "Unresolved Motivic Obstacles:\n"
        "3. Kuga-Satake algebraic cycle over Q\n"
        "4. Chow flatness on Mumford sixfold A_6\n"
        "Status: S-BRIDGE-SPINOR-MOTIVE = OPEN",
        "#FFF7ED", "#EA580C", "#9A3412",
    )
    draw_box(
        ax_d, (0.3, 0.55), 9.4, 2.6,
        "SCIENTIFIC SCOPE & STANDING EPISTEMIC BOUNDARY",
        "Lean checks verify finite index combinatorics only (no schemes, sheaves, or Hodge theory formalized).\n"
        "Classical theorems attributed to Griffiths, Shioda-Aoki-Ran, Macaulay, Peskine-Szpiro, Deligne, Wang.\n"
        "STANDING INVARIANT: GLOBAL_HODGE_CONJECTURE = OPEN | release_authorized = false | theorem_progress = UNKNOWN",
        "#FEF2F2", "#B91C1C", "#7F1D1D",
    )

    ax_d.annotate("", xy=(2.6, 6.6), xytext=(2.6, 7.3), arrowprops=arrow_kw)
    ax_d.annotate("", xy=(7.4, 6.6), xytext=(7.4, 7.3), arrowprops=arrow_kw)
    ax_d.annotate("", xy=(2.6, 3.25), xytext=(2.6, 4.0), arrowprops=arrow_kw)
    ax_d.annotate("", xy=(7.4, 3.25), xytext=(7.4, 4.0), arrowprops=arrow_kw)

    plt.tight_layout(rect=[0.01, 0.01, 0.99, 0.935])
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=240)
    plt.close(fig)
    return out_path


if __name__ == "__main__":
    p = build_four_panel_figure()
    print(f"Generated visual architecture figure: {p} ({p.stat().st_size} bytes)")
