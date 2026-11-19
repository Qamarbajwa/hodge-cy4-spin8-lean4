"""Experiment 6: Fixed-Container Projected Wave Adaptation & Conjugate-Half Obstruction.

Strictly deterministic, combining exact integer/rational verification over Z and Q with
fixed-container projected gradient adaptation in Float64 over:
  1. The 70-dim Weil U(2,2) Hodge container (/\\^4 R^8, S^69) under D_H^(4) and P_Weil:
     - Universal 50/50 half-node barrier: for every coordinate 35/35 split (c = 0..7),
       A_c^2 = 96 A_c, D_c^2 = 96 D_c, B_c B_c^T = 96 A_c, tr(A_c) = tr(D_c) = 192,
       proving spec(P_Weil|_{V_c}) = {1/2, 1/2, 0^33} and an unbreakable >= 1/2 defect.
     - Z_2 chiral parity conjugate intertwining (38 even + 32 odd):
       K_ee = K_oo = 0, P_eo = 0, K_eo P_odd K_eo^T = 16 P_even, K_eo^T P_even K_eo = 16 P_odd.
     - Hodge-star 50/50 self-dual / anti-self-dual split (35 + 35):
       Star^2 = I_70, tr(Star) = 0, Star P_192 = P_192 Star = P_192.
     - Projected gradient adaptation across full S^69 vs 50%-sliced constraints.
  2. The 1,751-dim R(F_0)_12 fixed polynomial container (Band1=1001, Band2=630, Band3=120)
     and exact 8x8 Z_2-graded super-differential Q_A^2 = 0, Q_B^2 = 0, (Q_A + Q_B)^2 = 2 F_1 I_8.

Outputs: reports/millennium_ext/conjugate_half_wave_adaptation.json
"""

from __future__ import annotations

import json
import sys
from fractions import Fraction
from pathlib import Path
from typing import Any, Callable, Dict, List, Tuple

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from high_precision_period_pslq import build_weil_classes_int
from matrix_factorization_scaling import build_sextic_r12_basis, classify_sextic_band
from non_koszul_mf_closure import Poly3, p3_add, p3_adj, p3_mat_mul, p3_scale
from wavefunction_matrix_unification import (
    TUPLES_4_8,
    build_deriv_matrix_frac,
    mat_add_scaled_eye,
    mat_mul_frac,
)


def build_weil_70_exact_operators() -> Dict[str, Any]:
    """Constructs exact integer matrices D43, K4, P192, Star, w_re, w_im, theta_sq on /\\^4 Z^8."""
    j43_int = [
        [0, 47, -6, -2, -10, -10, -10, 10],
        [-47, 0, 2, -6, -10, 10, 10, 10],
        [6, -2, 0, 53, 20, -10, -10, -20],
        [2, 6, -53, 0, -10, -20, -20, 10],
        [-10, -10, 20, -10, 0, 50, 7, 0],
        [-10, 10, -10, -20, -50, 0, 0, 7],
        [-10, 10, -10, -20, -7, 0, 0, 50],
        [10, 10, -20, 10, 0, -7, -50, 0],
    ]
    phi8_int = [[0] * 8 for _ in range(8)]
    for a in range(4):
        sgn = 1 if a < 2 else -1
        phi8_int[2 * a][2 * a + 1] = sgn
        phi8_int[2 * a + 1][2 * a] = -sgn

    d43_frac = build_deriv_matrix_frac([[Fraction(x) for x in r] for r in j43_int], 4)
    k4_frac = build_deriv_matrix_frac([[Fraction(x) for x in r] for r in phi8_int], 4)
    k4_2 = mat_mul_frac(k4_frac, k4_frac)
    p192_frac = mat_mul_frac(k4_2, mat_add_scaled_eye(k4_2, Fraction(4)))

    d43 = np.array([[int(x) for x in r] for r in d43_frac], dtype=np.int64)
    k4 = np.array([[int(x) for x in r] for r in k4_frac], dtype=np.int64)
    p192 = np.array([[int(x) for x in r] for r in p192_frac], dtype=np.int64)

    star = np.zeros((70, 70), dtype=np.int64)
    t4_idx = {t: i for i, t in enumerate(TUPLES_4_8)}
    for i, t in enumerate(TUPLES_4_8):
        comp = tuple(sorted(set(range(8)) - set(t)))
        lst = list(t) + list(comp)
        invs = sum(1 for a in range(8) for b in range(a + 1, 8) if lst[a] > lst[b])
        star[t4_idx[comp], i] = -1 if invs % 2 else 1

    w_re_d, w_im_d = build_weil_classes_int()
    w_re = np.array([int(w_re_d.get(t, 0)) for t in TUPLES_4_8], dtype=np.int64)
    w_im = np.array([int(w_im_d.get(t, 0)) for t in TUPLES_4_8], dtype=np.int64)

    # Theta^2 in /\\^4 Z^8 has +2 on disjoint symplectic pairs from {(0,1),(2,3),(4,5),(6,7)}
    theta_pairs = [(0, 1), (2, 3), (4, 5), (6, 7)]
    theta_sq = np.zeros(70, dtype=np.int64)
    for i, (a, b) in enumerate(theta_pairs):
        for c, d in theta_pairs[i + 1 :]:
            theta_sq[t4_idx[tuple(sorted((a, b, c, d)))]] = 2

    return {
        "D43": d43,
        "K4": k4,
        "P192": p192,
        "Star": star,
        "w_re": w_re,
        "w_im": w_im,
        "theta_sq": theta_sq,
    }


def verify_exact_conjugate_half_matrix_laws(ops: Dict[str, Any]) -> Dict[str, Any]:
    """Verifies exact integer matrix identities for 50/50 barriers, chiral parity, and Hodge star."""
    d43, k4, p192, star = ops["D43"], ops["K4"], ops["P192"], ops["Star"]
    w_re, w_im = ops["w_re"], ops["w_im"]

    p_rank2 = 24 * (np.outer(w_re, w_re) + np.outer(w_im, w_im))
    assert np.array_equal(p192, p_rank2)
    assert np.array_equal(p192, p192.T)
    nnz_p192 = int(np.count_nonzero(p192))
    assert nnz_p192 == 128

    coord_splits_ok = True
    for c in range(8):
        i_in = [i for i, t in enumerate(TUPLES_4_8) if c in t]
        i_out = [i for i, t in enumerate(TUPLES_4_8) if c not in t]
        assert len(i_in) == 35 and len(i_out) == 35
        a_blk = p192[np.ix_(i_in, i_in)]
        b_blk = p192[np.ix_(i_in, i_out)]
        d_blk = p192[np.ix_(i_out, i_out)]
        ok = (
            np.array_equal(a_blk @ a_blk, 96 * a_blk)
            and np.array_equal(d_blk @ d_blk, 96 * d_blk)
            and np.array_equal(b_blk @ b_blk.T, 96 * a_blk)
            and int(np.trace(a_blk)) == 192
            and int(np.trace(d_blk)) == 192
        )
        assert ok
        coord_splits_ok = coord_splits_ok and ok

    mask0 = np.array([1 if 0 in t else 0 for t in TUPLES_4_8], dtype=np.int64)
    v_half = w_re * mask0
    v_half_norm_sq = int(v_half @ v_half)
    v_half_p192 = int(v_half @ p192 @ v_half)
    d43_vhalf_vec = d43 @ v_half
    d43_vhalf_sq = int(d43_vhalf_vec @ d43_vhalf_vec)
    assert v_half_norm_sq == 4 and v_half_p192 == 384 and d43_vhalf_sq == 19432
    assert Fraction(v_half_p192, 192 * v_half_norm_sq) == Fraction(1, 2)
    assert int(w_re @ p192 @ w_re) == 1536 and np.all(d43 @ w_re == 0)

    # Exact Z_2 chiral parity split (38 even vs 32 odd)
    i_even = [i for i, t in enumerate(TUPLES_4_8) if sum(x % 2 for x in t) % 2 == 0]
    i_odd = [i for i, t in enumerate(TUPLES_4_8) if sum(x % 2 for x in t) % 2 == 1]
    assert len(i_even) == 38 and len(i_odd) == 32
    k_ee = k4[np.ix_(i_even, i_even)]
    k_oo = k4[np.ix_(i_odd, i_odd)]
    k_eo = k4[np.ix_(i_even, i_odd)]
    p_even = p192[np.ix_(i_even, i_even)]
    p_odd = p192[np.ix_(i_odd, i_odd)]
    p_eo = p192[np.ix_(i_even, i_odd)]
    assert np.all(k_ee == 0) and np.all(k_oo == 0) and np.all(p_eo == 0)
    assert np.array_equal(p_even @ p_even, 192 * p_even) and int(np.trace(p_even)) == 192
    assert np.array_equal(p_odd @ p_odd, 192 * p_odd) and int(np.trace(p_odd)) == 192
    assert np.array_equal(k_eo @ p_odd @ k_eo.T, 16 * p_even)
    assert np.array_equal(k_eo.T @ p_even @ k_eo, 16 * p_odd)

    # Exact Hodge star 35/35 involution
    assert np.array_equal(star @ star, np.eye(70, dtype=np.int64))
    assert np.array_equal(star, star.T)
    assert int(np.trace(star)) == 0
    assert np.array_equal(star @ p192, p192) and np.array_equal(p192 @ star, p192)

    return {
        "p192_exact_rank2_outer_sum": True,
        "p192_nonzero_entries": nnz_p192,
        "all_8_coord_splits_35_35_50pct_barrier": coord_splits_ok,
        "half_node_norm_sq": v_half_norm_sq,
        "half_node_p192_form": v_half_p192,
        "half_node_d43_sq": d43_vhalf_sq,
        "half_node_rayleigh_quotient": str(Fraction(d43_vhalf_sq, 43 * 43 * v_half_norm_sq)),
        "parity_dims": [len(i_even), len(i_odd)],
        "chiral_intertwining_verified": True,
        "hodge_star_sd_projector_verified": True,
    }


def run_weil_70dim_projected_wave_adaptation(ops: Dict[str, Any]) -> Dict[str, Any]:
    """Runs projected gradient wave adaptation on S^69 under full and 50%-sliced constraints."""
    d4 = ops["D43"].astype(np.float64) / 43.0
    k4 = ops["K4"].astype(np.float64)
    p_weil = ops["P192"].astype(np.float64) / 192.0
    star = ops["Star"].astype(np.float64)
    w_re = ops["w_re"].astype(np.float64)
    theta_sq = ops["theta_sq"].astype(np.float64)

    h_weil = d4.T @ d4 + 4.0 * (np.eye(70) - p_weil)
    evals = np.sort(np.linalg.eigvalsh(h_weil))
    assert float(np.sum(evals < 1e-10)) == 2
    spectral_gap = float(evals[2])
    assert abs(spectral_gap - 4.0) < 1e-10

    coord_min_evals: List[float] = []
    for c in range(8):
        mask = np.array([c in t for t in TUPLES_4_8])
        ev_c = np.linalg.eigvalsh(h_weil[np.ix_(mask, mask)])
        coord_min_evals.append(round(float(ev_c[0]), 6))
        assert float(ev_c[0]) > 3.5

    mask0 = np.array([0 in t for t in TUPLES_4_8])
    mask_even = np.array([sum(x % 2 for x in t) % 2 == 0 for t in TUPLES_4_8])
    p_sd = 0.5 * (np.eye(70) + star)
    p_asd = 0.5 * (np.eye(70) - star)

    def normalize(vec: np.ndarray) -> np.ndarray:
        nrm = float(np.linalg.norm(vec))
        return vec / nrm if nrm > 0.0 else vec

    def safe_leakage(kv: np.ndarray, out_proj: Callable[[np.ndarray], np.ndarray]) -> float:
        kn = float(np.linalg.norm(kv))
        if kn < 1e-12:
            return 0.0
        return float(np.linalg.norm(out_proj(kv)) ** 2 / (kn * kn))

    constraints: Dict[str, Tuple[Callable[[np.ndarray], np.ndarray], Callable[[np.ndarray], float]]] = {
        "full_70": (normalize, lambda kv: 0.0),
        "half_coord0_35": (lambda v: normalize(v * mask0), lambda kv: safe_leakage(kv, lambda z: z * (~mask0))),
        "half_sd_35": (lambda v: normalize(p_sd @ v), lambda kv: safe_leakage(kv, lambda z: p_asd @ z)),
        "half_asd_35": (lambda v: normalize(p_asd @ v), lambda kv: safe_leakage(kv, lambda z: p_sd @ z)),
        "half_even_38": (lambda v: normalize(v * mask_even), lambda kv: safe_leakage(kv, lambda z: z * (~mask_even))),
    }

    rng = np.random.default_rng(2026)
    psi_init = normalize(rng.normal(size=70))
    eta = 0.03
    steps = 250

    runs: Dict[str, Any] = {}
    for label, (proj_fn, leak_fn) in constraints.items():
        v = proj_fn(psi_init)
        e0 = 0.5 * float(v @ h_weil @ v)
        for _ in range(steps):
            v = proj_fn(v - eta * (h_weil @ v))
        e_final = 0.5 * float(v @ h_weil @ v)
        fidelity = float(v @ p_weil @ v)
        hodge_res = float(np.linalg.norm(d4 @ v))
        k_leak = leak_fn(k4 @ v)
        runs[label] = {
            "initial_energy": round(e0, 8),
            "final_energy": float(f"{e_final:.6e}"),
            "weil_fidelity": round(fidelity, 8),
            "hodge_residual": float(f"{hodge_res:.6e}"),
            "conjugate_k_leakage": round(k_leak, 8),
        }

    assert runs["full_70"]["final_energy"] < 1e-14 and runs["full_70"]["weil_fidelity"] > 1.0 - 1e-12
    assert runs["half_coord0_35"]["final_energy"] > 1.84 and runs["half_coord0_35"]["weil_fidelity"] <= 0.5 + 1e-9
    assert runs["half_sd_35"]["final_energy"] < 1e-14 and runs["half_sd_35"]["weil_fidelity"] > 1.0 - 1e-12
    assert abs(runs["half_asd_35"]["final_energy"] - 2.0) < 1e-6 and runs["half_asd_35"]["weil_fidelity"] < 1e-12
    assert runs["half_even_38"]["final_energy"] < 1e-14 and runs["half_even_38"]["conjugate_k_leakage"] > 1.0 - 1e-12

    # Discrete integer-bridge step: psi_0 = w_re + theta_sq -> psi_1 = 2*w_re + theta_sq
    norm0_sq = int(round(float((w_re + theta_sq) @ (w_re + theta_sq))))
    norm1_sq = int(round(float((2 * w_re + theta_sq) @ (2 * w_re + theta_sq))))
    fid0 = float((w_re + theta_sq) @ p_weil @ (w_re + theta_sq)) / norm0_sq
    fid1 = float((2 * w_re + theta_sq) @ p_weil @ (2 * w_re + theta_sq)) / norm1_sq
    assert abs(fid0 - 0.25) < 1e-12 and abs(fid1 - 4.0 / 7.0) < 1e-12

    return {
        "eta": eta,
        "steps": steps,
        "spectral_gap_h_weil": round(spectral_gap, 8),
        "coord_half_slice_min_evals": coord_min_evals,
        "discrete_bridge_fidelity_step": [str(Fraction(1, 4)), str(Fraction(4, 7))],
        "trajectory_outcomes": runs,
    }


def run_r12_1751dim_wave_to_mf_adaptation_and_superdiff() -> Dict[str, Any]:
    """Compares Koszul-only vs full Koszul+non-Koszul adaptation on R(F_0)_12 and checks Z2 Q^2."""
    basis = build_sextic_r12_basis()
    assert len(basis) == 1751
    col_idx = {m: i for i, m in enumerate(basis)}
    bands = [classify_sextic_band(m) for m in basis]
    b1_mask = np.array([b == "Band1" for b in bands], dtype=bool)
    assert int(b1_mask.sum()) == 1001

    m_b1 = (2, 2, 2, 2, 2, 2)
    m_b2_a = (0, 0, 3, 3, 3, 3)
    m_b2_b = (1, 1, 1, 1, 4, 4)
    m_b3 = (0, 2, 2, 2, 3, 3)
    assert classify_sextic_band(m_b1) == "Band1"
    assert classify_sextic_band(m_b2_a) == "Band2" and classify_sextic_band(m_b2_b) == "Band2"
    assert classify_sextic_band(m_b3) == "Band3"

    psi_target = np.zeros(1751, dtype=np.float64)
    psi_target[col_idx[m_b1]] = 1.0
    psi_target[col_idx[m_b2_a]] = 2.0
    psi_target[col_idx[m_b2_b]] = 2.0
    psi_target[col_idx[m_b3]] = 1.0
    psi_target /= np.linalg.norm(psi_target)
    b1_target_overlap = float(np.sum(psi_target[b1_mask] ** 2))
    assert abs(b1_target_overlap - 0.1) < 1e-12

    rng = np.random.default_rng(77)
    init_raw = rng.normal(size=1751)
    eta = 0.15
    steps = 200

    def adapt_on_mask(mask: np.ndarray | None) -> Dict[str, Any]:
        def proj(v: np.ndarray) -> np.ndarray:
            w = v * mask if mask is not None else v
            nrm = float(np.linalg.norm(w))
            return w / nrm

        psi = proj(init_raw)
        for _ in range(steps):
            grad = psi - psi_target
            psi = proj(psi - eta * grad)
        loss = 0.5 * float(np.linalg.norm(psi - psi_target) ** 2)
        align = float(psi @ psi_target) ** 2
        return {"final_loss": round(loss, 8), "target_alignment_sq": round(align, 8)}

    res_koszul = adapt_on_mask(b1_mask)
    res_full = adapt_on_mask(None)
    assert res_koszul["final_loss"] > 0.68 and abs(res_koszul["target_alignment_sq"] - 0.1) < 1e-6
    assert res_full["final_loss"] < 1e-12 and res_full["target_alignment_sq"] > 1.0 - 1e-12

    # Exact over-Z 8x8 Z_2-graded super-differential Q = Q_A + Q_B for 4x4 mixed (1,1,1,3) MF
    p_x0: Poly3 = {(1, 0, 0): 1}
    p_x1: Poly3 = {(0, 1, 0): 1}
    p_x2: Poly3 = {(0, 0, 1): 1}
    a1: List[List[Poly3]] = [
        [p3_add(p3_scale(p_x0, -1), p3_scale(p_x2, -2)), p_x1, p_x0, {}],
        [p3_scale(p_x1, 2), p3_add(p_x0, p_x2, -1), {}, p_x0],
        [p3_add(p3_scale(p_x0, -2), p3_scale(p_x2, -1)), p_x1, p3_scale(p_x2, -1), p_x1],
        [
            {(2, 1, 0): 2, (0, 1, 2): -1},
            {(3, 0, 0): 1, (2, 0, 1): -1, (1, 2, 0): -1},
            {(0, 3, 0): -1, (0, 1, 2): -1},
            {(0, 0, 3): -1},
        ],
    ]
    adj_a1 = p3_adj(a1)
    b1 = [[p3_scale(adj_a1[i][j], -1) for j in range(4)] for i in range(4)]

    q_a: List[List[Poly3]] = [[{} for _ in range(8)] for _ in range(8)]
    q_b: List[List[Poly3]] = [[{} for _ in range(8)] for _ in range(8)]
    q_full: List[List[Poly3]] = [[{} for _ in range(8)] for _ in range(8)]
    for i in range(4):
        for j in range(4):
            q_a[i][4 + j] = a1[i][j]
            q_b[4 + i][j] = b1[i][j]
            q_full[i][4 + j] = a1[i][j]
            q_full[4 + i][j] = b1[i][j]

    qa2 = p3_mat_mul(q_a, q_a)
    qb2 = p3_mat_mul(q_b, q_b)
    q2 = p3_mat_mul(q_full, q_full)
    f2_target: Poly3 = {(6, 0, 0): 2, (0, 6, 0): 2, (0, 0, 6): -2}
    assert all(cell == {} for row in qa2 for cell in row)
    assert all(cell == {} for row in qb2 for cell in row)
    for i in range(8):
        for j in range(8):
            assert q2[i][j] == (f2_target if i == j else {})

    return {
        "r12_total_dim": 1751,
        "band1_target_overlap": round(b1_target_overlap, 6),
        "koszul_only_adaptation": res_koszul,
        "full_mixture_adaptation": res_full,
        "z2_graded_8x8_superdifferential": {
            "qa_sq_zero": True,
            "qb_sq_zero": True,
            "q_full_sq_eq_2f1_i8": True,
        },
    }


def main() -> int:
    ops = build_weil_70_exact_operators()
    exact_laws = verify_exact_conjugate_half_matrix_laws(ops)
    weil_adapt = run_weil_70dim_projected_wave_adaptation(ops)
    mf_adapt = run_r12_1751dim_wave_to_mf_adaptation_and_superdiff()

    report = {
        "exact_conjugate_half_matrix_laws": exact_laws,
        "weil_70dim_projected_wave_adaptation": weil_adapt,
        "r12_wave_to_mf_adaptation_and_superdiff": mf_adapt,
    }
    out_path = (
        Path(__file__).resolve().parents[2]
        / "reports"
        / "millennium_ext"
        / "conjugate_half_wave_adaptation.json"
    )
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    print(
        f"CONJUGATE_HALF_WAVE_ADAPTATION: splits8={exact_laws['all_8_coord_splits_35_35_50pct_barrier']} "
        f"E_full={weil_adapt['trajectory_outcomes']['full_70']['final_energy']} "
        f"E_half0={weil_adapt['trajectory_outcomes']['half_coord0_35']['final_energy']} "
        f"fid_half0={weil_adapt['trajectory_outcomes']['half_coord0_35']['weil_fidelity']} "
        f"E_koszul={mf_adapt['koszul_only_adaptation']['final_loss']} "
        f"E_mix={mf_adapt['full_mixture_adaptation']['final_loss']} "
        f"Q2_ok={mf_adapt['z2_graded_8x8_superdifferential']['q_full_sq_eq_2f1_i8']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
