"""Experiment 10 (Wall 3): Bipartite Wave-Function Correspondence Matrix Algebra
on Mumford's End_Q(A) = Q Fourfold Product A x A (H^2(A) tensor H^2(A), 28 x 28).

Reinterprets the 784-component (28 x 28) bipartite Hodge (2,2) correspondence
wave function on A x A as strict 28 x 28 correspondence operators T = B_2 C:
  1. Exact Cup-Product Lefschetz Pairing & Hodge-Riemann Sign Flip:
     - E_2 = wedge^2(E_real) is symmetric, involutive (E_2^2 = I_28), and commutes
       with all 4 Casimir projectors Q_0, Q_sd, Q_asd, Q_ric.
     - B_2(u, v) = coeff of vol_8 in u wedge v wedge Theta^2 satisfies B_2 = B_2^T
       and B_2 E_2 = 2 Q_0 - 2 I_28 (+6 on Theta vs -2 on all 27 primitive 2-forms).
     - Separable divisor lift C_th = th_vec * th_vec^T = 4 E_2 Q_0; diagonal C_dd = -2 E_2.
  2. Bose-Mesner Correspondence Algebra & 2D -> 1D Chiral Single-Generator Reduction:
     - T_th = 24 Q_0, T_dd = 4 I_28 - 4 Q_0, T_ch = -2(Q_sd - Q_asd),
       T_r0 = -2(Q_sd + Q_asd - 2 Q_ric).
     - Closed 2D divisor algebra A_div and 3D parity-even algebra A_even.
     - Single-generator chiral reduction: 8 T_r0 = 32 T_dd + 4 T_th - 3 T_ch^2.
  3. Z_2-Graded Superoperator Split (16_+ + 12_-), Reduced Density Blindness
     & Observable-Half Recovery Lift.
  4. Schmidt/Spectral Trace Moments, Semigroup Oscillation (T_ch^3 = 64 T_ch),
     and Moduli Commutativity with D^(2)(J_Mum3) and wedge^2(G_Mum9).

Outputs: reports/millennium_ext/wavefunction_bipartite_matrix.json
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

import sympy as sp

_THIS_DIR = Path(__file__).resolve().parent
if str(_THIS_DIR) not in sys.path:
    sys.path.insert(0, str(_THIS_DIR))

from mumford_sl2_so4_spinor import (
    build_mumford_real_generators,
    ext2_action,
    verify_end_q_and_casimirs,
    wedge2_group,
)


def _wedge_tup(t1: Tuple[int, ...], t2: Tuple[int, ...]) -> Tuple[Tuple[int, ...] | None, int]:
    if set(t1) & set(t2):
        return None, 0
    arr = list(t1) + list(t2)
    inv = sum(1 for i in range(len(arr)) for j in range(i + 1, len(arr)) if arr[i] > arr[j])
    return tuple(sorted(arr)), (-1 if inv % 2 else 1)


def _frob2(mat: sp.Matrix) -> int:
    return int((mat.T * mat).trace())


def run_bipartite_wavefunction_experiment() -> Dict[str, Any]:
    data = build_mumford_real_generators()
    cas = verify_end_q_and_casimirs(data)
    e_real = data["E_real"]
    pairs28: List[Tuple[int, int]] = cas["tups2_8"]
    p2i = {p: i for i, p in enumerate(pairs28)}
    q0, q_sd, q_asd, q_ric = cas["projs"]
    projs = [q0, q_sd, q_asd, q_ric]
    i28 = sp.eye(28)
    z28 = sp.zeros(28, 28)

    # 1. Cup-Product Lefschetz Pairing & Hodge-Riemann Sign Flip
    e2 = wedge2_group(e_real, pairs28)
    assert e2 == e2.T
    assert e2 * e2 == i28
    for q in projs:
        assert q == q.T
        assert e2 * q == q * e2

    # Theta = sum_{k=0}^3 e_k ^ e_{k+4}
    th_terms = [(k, k + 4, 1) for k in range(4)]
    th2: Dict[Tuple[int, ...], int] = {}
    for a, b, c1 in th_terms:
        for p, q, c2 in th_terms:
            t4, sgn = _wedge_tup((a, b), (p, q))
            if t4 is not None:
                th2[t4] = th2.get(t4, 0) + c1 * c2 * sgn

    b2 = sp.zeros(28, 28)
    for r in range(28):
        for c in range(28):
            t4, s1 = _wedge_tup(pairs28[r], pairs28[c])
            if t4 is None:
                continue
            val = 0
            for q4, coeff in th2.items():
                t8, s2 = _wedge_tup(t4, q4)
                if t8 is not None:
                    val += coeff * s1 * s2
            b2[r, c] = val

    assert b2 == b2.T
    m_be = b2 * e2
    assert m_be == 2 * q0 - 2 * i28
    assert m_be * q0 == 6 * q0
    for qa in (q_sd, q_asd, q_ric):
        assert m_be * qa == -2 * qa

    th_vec = sp.zeros(28, 1)
    for k in range(4):
        th_vec[p2i[(k, k + 4)], 0] = 2
    c_th = th_vec * th_vec.T
    c_dd = -2 * e2
    assert c_th == 4 * e2 * q0

    # 2. Bose-Mesner Correspondence Algebra & 2D -> 1D Chiral Single-Generator Reduction
    t_th = b2 * c_th
    t_dd = b2 * c_dd
    t_ch = b2 * (e2 * (q_sd - q_asd))
    t_r0 = b2 * (e2 * (q_sd + q_asd - 2 * q_ric))

    assert t_th == 24 * q0
    assert t_dd == 4 * i28 - 4 * q0
    assert t_ch == -2 * (q_sd - q_asd)
    assert t_r0 == -2 * (q_sd + q_asd - 2 * q_ric)

    # Closed 2D divisor subalgebra A_div
    assert t_th * t_th == 96 * t_th
    assert t_th * t_dd == -12 * t_th
    assert t_dd * t_dd == 4 * t_dd + 2 * t_th

    # Closed 3D parity-even subalgebra A_even
    assert t_r0 * t_th == z28
    assert t_r0 * t_dd == 4 * t_r0
    assert t_r0 * t_r0 == 32 * t_dd + 4 * t_th + 8 * t_r0

    # Single-generator chiral closure: 8 T_r0 = 32 T_dd + 4 T_th - 3 T_ch^2
    assert 8 * t_r0 == 32 * t_dd + 4 * t_th - 3 * (t_ch * t_ch)
    assert t_ch * t_th == z28
    assert t_ch * t_dd == 4 * t_ch
    assert t_ch * t_r0 == -8 * t_ch
    assert t_ch * (t_ch * t_ch - 64 * i28) == z28
    assert t_r0 * (t_r0 + 8 * i28) * (t_r0 - 16 * i28) == z28

    # 3. Z_2-Graded Superoperator Split (16_+ + 12_-), Reduced Density Blindness & Lift
    refl4 = sp.kronecker_product(sp.eye(2), sp.diag(1, 1, 1, -1))
    p_flip = wedge2_group(refl4, pairs28)
    ep = i28 + p_flip
    em = i28 - p_flip

    assert p_flip * p_flip == i28
    assert int(p_flip.trace()) == 4
    assert ep * ep == 2 * ep
    assert em * em == 2 * em
    assert ep * em == z28

    for m_even in (t_th, t_dd, t_r0):
        assert ep * m_even * em == z28
        assert em * m_even * ep == z28

    for q_chiral in (q_sd, q_asd):
        assert _frob2(ep * q_chiral * ep) == 576
        assert _frob2(em * q_chiral * em) == 576
        assert _frob2(ep * q_chiral * em) == 576
        assert _frob2(em * q_chiral * ep) == 576

    assert ep * t_ch * ep == z28
    assert em * t_ch * em == z28
    assert _frob2(ep * t_ch * em) == 9216
    assert _frob2(em * t_ch * ep) == 9216

    rho_ch = t_ch * t_ch.T
    assert rho_ch == t_ch * t_ch
    assert rho_ch == 16 * (q_sd + q_asd)
    assert p_flip * rho_ch * p_flip == rho_ch
    assert ep * rho_ch * em == z28

    k_obs = ep * t_ch * em
    assert k_obs + k_obs.T == 4 * t_ch

    # 4. Schmidt/Spectral Trace Moments, Semigroup Oscillation & Moduli Commutativity
    q0_traces = [int((q0**k).trace()) for k in range(1, 3)]
    t_dd_traces = [int((t_dd**k).trace()) for k in range(1, 4)]
    t_ch_traces = [int((t_ch**k).trace()) for k in range(1, 5)]
    t_r0_traces = [int((t_r0**k).trace()) for k in range(1, 5)]

    assert q0_traces == [4, 16]
    assert t_dd_traces == [96, 576, 0]
    assert t_ch_traces == [0, 1152, 0, 73728]
    assert t_r0_traces == [0, 3456, 27648, 663552]

    assert t_ch**3 == 64 * t_ch
    assert t_ch**4 == 64 * (t_ch**2)

    j_mum3 = sp.kronecker_product(sp.Matrix([[4, 5], [-5, -4]]), sp.eye(4))
    g_mum9 = sp.kronecker_product(
        sp.Matrix([[5, 4], [4, 5]]),
        sp.Matrix([[1, -2, -2, 0], [2, 1, 0, -2], [2, 0, 1, 2], [0, 2, -2, 1]]),
    )
    d2_j3 = ext2_action(j_mum3, pairs28)
    w2_g9 = wedge2_group(g_mum9, pairs28)
    for op in (t_th, t_dd, t_ch, t_r0):
        assert d2_j3 * op == op * d2_j3
        assert w2_g9 * op == op * w2_g9

    return {
        "lefschetz_pairing": {
            "e2_symmetric_involutive": True,
            "b2_symmetric": True,
            "b2_e2_eigenvalues_theta_vs_primitive": {"Q_0": 6, "Q_sd": -2, "Q_asd": -2, "Q_ric": -2},
            "c_th_separable_equals_4_e2_q0": True,
        },
        "correspondence_algebra": {
            "closed_2d_divisor_algebra": True,
            "closed_3d_parity_even_algebra": True,
            "single_generator_chiral_reduction": "8*T_r0 == 32*T_dd + 4*T_th - 3*T_ch^2",
            "t_ch_minpoly_zero": True,
            "t_r0_minpoly_zero": True,
        },
        "z2_graded_superoperator": {
            "p_flip_trace": 4,
            "even_dim": 16,
            "odd_dim": 12,
            "even_ops_block_diagonal": True,
            "q_sd_q_asd_block_frob2": [576, 576, 576, 576],
            "t_ch_purely_off_diagonal_frob2": 9216,
            "reduced_density_parity_blind": True,
            "observable_half_recovery_scale": 4,
        },
        "traces_and_moduli_invariance": {
            "q0_traces_1_2": q0_traces,
            "t_dd_traces_1_to_3": t_dd_traces,
            "t_ch_traces_1_to_4": t_ch_traces,
            "t_r0_traces_1_to_4": t_r0_traces,
            "t_ch_semigroup_oscillation_64": True,
            "d2_j3_and_w2_g9_commute_all_correspondences": True,
        },
    }


def main() -> int:
    report = run_bipartite_wavefunction_experiment()
    out_dir = Path(__file__).resolve().parents[2] / "reports" / "millennium_ext"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "wavefunction_bipartite_matrix.json"
    out_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"WAVEFUNCTION_BIPARTITE_MATRIX_VERIFIED: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
