"""Experiment 7: Indefinite-Signature SU(2,2) Lorentzian Boosts, Matrix Mobius Spatial
Projection, and SO(35,35) Weil Light-Cone Invariance.

Combines exact integer/rational/SymPy verification with projected-gradient wave adaptation
on the boosted U(2,2) Weil fiber:
  1. Exact symmetric Pythagorean SU(2,2) boost G_9 = 9 * g in M_8(Z) with (c, s) = (5/3, 4/3)
     and U = (1/3)[[1+2i, 2], [-2, 1-2i]] in SU(2, Q(i)):
     - G_9^T eta_8 G_9 = 81 eta_8, G_9^T E_8 G_9 = 81 E_8, [G_9, Phi_8] = 0, det(G_9) = 9^8.
     - Minimal polynomial (G_9 - 27 I_8)(G_9 - 3 I_8) = 0 with null light-cone conjugate-half
       projectors N_+ = G_9 - 3 I_8, N_- = 27 I_8 - G_9 obeying N_+^T eta_8 N_+ = 0,
       N_-^T eta_8 N_- = 0, N_+ + N_- = 24 I_8, N_+ N_- = 0.
     - 50/50 light-cone rotation L_8 diagonalizing the radial boost G_rad3 to diag(18^4, 2^4).
  2. Boosted complex structure J_27 = (1/3) G_9 E_8 (eta_8 G_9^T eta_8):
     - J_27^2 = -729 I_8, J_27^T E_8 J_27 = 729 E_8, [J_27, Phi_8] = 0.
     - G_pos = -E_8 J_27 satisfies (G_pos - 243 I_8)(G_pos - 3 I_8) = 0 and 8 positive Bareiss
       minors with det = 27^8.
     - Matrix Mobius spatial projection trajectory H_k = g^k * 0 = ((3^(2k)-1)/(3^(2k)+1)) U
       remaining strictly inside the period unit ball I_2 - H_k^* H_k = 4*3^(2k)/(3^(2k)+1)^2 I_2 > 0.
  3. Induced 70 x 70 SO(35,35) exterior boost L_70 = /\\^4 (G_9 / 9):
     - Exact L_70^T = L_70, L_70^T Star L_70 = Star, tr(L_70) = 21286/81 with 5-tier light-cone
       spectrum {1/81 (1), 1/9 (16), 1 (36), 9 (16), 81 (1)}.
     - Pointwise invariance L_70 w_Re = w_Re, L_70 w_Im = w_Im, L_70 Theta^2 = Theta^2,
       L_70 P_192 = P_192 L_70 = P_192, D_27^(4) P_192 = 0, [D_27^(4), K_Phi^(4)] = 0.

Outputs: reports/millennium_ext/lorentzian_weil_boost.json
"""

from __future__ import annotations

import json
import math
import sys
from collections import Counter
from fractions import Fraction
from pathlib import Path
from typing import Any, Dict, List

import numpy as np
import sympy as sp

sys.path.insert(0, str(Path(__file__).resolve().parent))
from conjugate_half_wave_adaptation import build_weil_70_exact_operators
from wavefunction_matrix_unification import PAIRS_2_8, TUPLES_4_8, build_deriv_matrix_frac


Z2_INT = np.array([[1, 0], [0, -1]], dtype=np.int64)
X2_INT = np.array([[0, 1], [1, 0]], dtype=np.int64)


def det4_frac(mat: List[List[Fraction]]) -> Fraction:
    """Exact 4 x 4 determinant over Fraction."""
    def det3(a: List[List[Fraction]]) -> Fraction:
        return (
            a[0][0] * (a[1][1] * a[2][2] - a[1][2] * a[2][1])
            - a[0][1] * (a[1][0] * a[2][2] - a[1][2] * a[2][0])
            + a[0][2] * (a[1][0] * a[2][1] - a[1][1] * a[2][0])
        )

    acc = Fraction(0)
    for col in range(4):
        entry = mat[0][col]
        if entry == 0:
            continue
        sub = [[mat[r][c] for c in range(4) if c != col] for r in range(1, 4)]
        acc += (entry if col % 2 == 0 else -entry) * det3(sub)
    return acc


def build_base_and_boost_8x8() -> Dict[str, np.ndarray]:
    """Constructs E8, Phi8, eta8, symmetric SU(2,2) boost G9, and radial G_rad3."""
    e8 = np.zeros((8, 8), dtype=np.int64)
    phi8 = np.zeros((8, 8), dtype=np.int64)
    for a in range(4):
        e8[2 * a, 2 * a + 1] = 1
        e8[2 * a + 1, 2 * a] = -1
        sgn = 1 if a < 2 else -1
        phi8[2 * a, 2 * a + 1] = sgn
        phi8[2 * a + 1, 2 * a] = -sgn
    eta8 = -e8 @ phi8

    g9 = np.zeros((8, 8), dtype=np.int64)
    g_rad3 = np.zeros((8, 8), dtype=np.int64)
    for a in range(4):
        g9[2 * a : 2 * a + 2, 2 * a : 2 * a + 2] = 15 * np.eye(2, dtype=np.int64)
        g_rad3[2 * a : 2 * a + 2, 2 * a : 2 * a + 2] = 5 * np.eye(2, dtype=np.int64)

    u_entries = [[(1, 2), (2, 0)], [(-2, 0), (1, -2)]]
    for r in range(2):
        for c in range(2):
            re, im = u_entries[r][c]
            blk = 4 * (re * Z2_INT + im * X2_INT)
            g9[2 * r : 2 * r + 2, 4 + 2 * c : 6 + 2 * c] = blk
            g9[4 + 2 * c : 6 + 2 * c, 2 * r : 2 * r + 2] = blk.T
        g_rad3[2 * r : 2 * r + 2, 4 + 2 * r : 6 + 2 * r] = 4 * Z2_INT
        g_rad3[4 + 2 * r : 6 + 2 * r, 2 * r : 2 * r + 2] = 4 * Z2_INT

    z4 = np.zeros((4, 4), dtype=np.int64)
    z4[:2, :2] = Z2_INT
    z4[2:, 2:] = Z2_INT
    i4 = np.eye(4, dtype=np.int64)
    l8 = np.block([[i4, z4], [i4, -z4]])

    return {"E8": e8, "Phi8": phi8, "eta8": eta8, "G9": g9, "G_rad3": g_rad3, "L8": l8}


def verify_8x8_lorentzian_boost_and_light_cone(mats: Dict[str, np.ndarray]) -> Dict[str, Any]:
    """Verifies exact integer 8x8 Lorentzian boost, light-cone projectors, and 50/50 split."""
    e8, phi8, eta8, g9, g_rad3, l8 = (
        mats["E8"], mats["Phi8"], mats["eta8"], mats["G9"], mats["G_rad3"], mats["L8"]
    )
    i8 = np.eye(8, dtype=np.int64)

    assert np.array_equal(eta8, np.diag([1, 1, 1, 1, -1, -1, -1, -1]))
    assert np.array_equal(g9, g9.T)
    assert np.array_equal(g9.T @ eta8 @ g9, 81 * eta8)
    assert np.array_equal(g9.T @ e8 @ g9, 81 * e8)
    assert np.array_equal(g9 @ phi8, phi8 @ g9)
    assert np.array_equal(g9 @ (eta8 @ g9.T @ eta8), 81 * i8)

    det_g9 = int(sp.Matrix(g9.tolist()).det())
    assert det_g9 == 9 ** 8
    assert np.array_equal((g9 - 27 * i8) @ (g9 - 3 * i8), np.zeros((8, 8), dtype=np.int64))

    n_plus = g9 - 3 * i8
    n_minus = 27 * i8 - g9
    assert np.array_equal(n_plus @ n_plus, 24 * n_plus) and int(np.trace(n_plus)) == 96
    assert np.array_equal(n_minus @ n_minus, 24 * n_minus) and int(np.trace(n_minus)) == 96
    assert np.array_equal(n_plus + n_minus, 24 * i8)
    assert np.array_equal(n_plus @ n_minus, np.zeros((8, 8), dtype=np.int64))
    assert np.array_equal(n_plus.T @ eta8 @ n_plus, np.zeros((8, 8), dtype=np.int64))
    assert np.array_equal(n_minus.T @ eta8 @ n_minus, np.zeros((8, 8), dtype=np.int64))

    assert np.array_equal(l8 @ l8.T, 2 * i8)
    rad_diag = l8 @ g_rad3 @ l8.T
    assert np.array_equal(rad_diag, np.diag([18, 18, 18, 18, 2, 2, 2, 2]))

    return {
        "eta8_diag": [1, 1, 1, 1, -1, -1, -1, -1],
        "g9_symmetric": True,
        "g9_preserves_eta8_scale81": True,
        "g9_preserves_e8_scale81": True,
        "g9_commutes_phi8": True,
        "g9_det": det_g9,
        "null_light_cone_projectors_verified": True,
        "radial_5050_light_cone_diag": [18, 18, 18, 18, 2, 2, 2, 2],
    }


def verify_boosted_j27_mobius_and_adaptation(
    mats: Dict[str, np.ndarray], ops: Dict[str, Any]
) -> Dict[str, Any]:
    """Verifies boosted J27 Bareiss minors, Mobius unit-ball trajectory, and adaptation."""
    e8, phi8, eta8, g9 = mats["E8"], mats["Phi8"], mats["eta8"], mats["G9"]
    i8 = np.eye(8, dtype=np.int64)

    g_inv_81 = eta8 @ g9.T @ eta8
    j_num = g9 @ e8 @ g_inv_81
    assert np.all(j_num % 3 == 0)
    j27 = j_num // 3

    assert np.array_equal(j27 @ j27, -729 * i8)
    assert np.array_equal(j27.T @ e8 @ j27, 729 * e8)
    assert np.array_equal(j27 @ phi8, phi8 @ j27)

    g_pos = -e8 @ j27
    assert np.array_equal(g_pos, g_pos.T)
    assert np.array_equal((g_pos - 243 * i8) @ (g_pos - 3 * i8), np.zeros((8, 8), dtype=np.int64))
    g_pos_sp = sp.Matrix(g_pos.tolist())
    minors = [int(g_pos_sp[:k, :k].det()) for k in range(1, 9)]
    expected_minors = [123, 15129, 1860867, 228886641, 1356572043, 8040170889, 47652720147, 282429536481]
    assert minors == expected_minors and minors[-1] == 27 ** 8

    # Exact rational 2x2 Matrix Mobius spatial projection H_k = ((3^(2k)-1)/(3^(2k)+1)) U
    u_sp = sp.Matrix([[1 + 2 * sp.I, sp.Integer(2)], [sp.Integer(-2), 1 - 2 * sp.I]]) / 3
    assert sp.expand(u_sp.H * u_sp) == sp.eye(2)
    h_cur = sp.zeros(2, 2)
    mobius_traj: List[Dict[str, Any]] = []
    for k in range(7):
        num_k = 3 ** (2 * k) - 1
        den_k = 3 ** (2 * k) + 1
        expected_hk = sp.Rational(num_k, den_k) * u_sp
        assert sp.simplify(h_cur - expected_hk) == sp.zeros(2, 2)
        margin_mat = sp.eye(2) - h_cur.H * h_cur
        margin_expected = sp.Rational(4 * (3 ** (2 * k)), den_k ** 2)
        assert sp.simplify(margin_mat - margin_expected * sp.eye(2)) == sp.zeros(2, 2)
        mobius_traj.append(
            {
                "step_k": k,
                "u_coeff": f"{num_k}/{den_k}",
                "ball_margin": str(margin_expected),
                "metric_condition_number": 81 if k > 0 else 1,
            }
        )
        # Apply Mobius step (5 H_k + 4 U)(4 U^* H_k + 5 I_2)^{-1}
        h_cur = sp.simplify((5 * h_cur + 4 * u_sp) * (4 * u_sp.H * h_cur + 5 * sp.eye(2)).inv())

    # Exact D27^(2) annihilates Theta but breaks on D^+_{0,2}
    j27_f = [[Fraction(int(x)) for x in row] for row in j27]
    d2_27 = np.array([[int(x) for x in r] for r in build_deriv_matrix_frac(j27_f, 2)], dtype=np.int64)
    theta_28 = np.array([1 if p in ((0, 1), (2, 3), (4, 5), (6, 7)) else 0 for p in PAIRS_2_8], dtype=np.int64)
    dp02_28 = np.array([1 if p in ((0, 4), (1, 5)) else 0 for p in PAIRS_2_8], dtype=np.int64)
    assert np.all(d2_27 @ theta_28 == 0) and np.any(d2_27 @ dp02_28 != 0)

    # Boosted 70-dim projected gradient wave adaptation under D27^(4) and P_Weil
    d4_27_f = build_deriv_matrix_frac(j27_f, 4)
    d4_27_int = np.array([[int(x) for x in r] for r in d4_27_f], dtype=np.int64)
    d4_27 = d4_27_int.astype(np.float64) / 27.0
    p_weil = ops["P192"].astype(np.float64) / 192.0
    h_weil_27 = d4_27.T @ d4_27 + 4.0 * (np.eye(70) - p_weil)
    evals_27 = np.sort(np.linalg.eigvalsh(h_weil_27))
    assert float(np.sum(evals_27 < 1e-10)) == 2
    assert abs(float(evals_27[2]) - 4.0) < 1e-10
    eta_step = 1.0 / float(evals_27[-1])

    rng = np.random.default_rng(2026)
    psi_init = rng.normal(size=70)
    psi_init /= np.linalg.norm(psi_init)
    mask0 = np.array([0 in t for t in TUPLES_4_8])

    def run_adapt(mask: np.ndarray | None, steps: int = 3000) -> Dict[str, Any]:
        def proj(v: np.ndarray) -> np.ndarray:
            w = v * mask if mask is not None else v
            return w / np.linalg.norm(w)

        v = proj(psi_init)
        for _ in range(steps):
            v = proj(v - eta_step * (h_weil_27 @ v))
        return {
            "final_energy": float(f"{0.5 * float(v @ h_weil_27 @ v):.6e}"),
            "weil_fidelity": round(float(v @ p_weil @ v), 8),
            "hodge_residual": float(f"{float(np.linalg.norm(d4_27 @ v)):.6e}"),
        }

    adapt_full = run_adapt(None)
    adapt_half0 = run_adapt(mask0)
    assert adapt_full["final_energy"] < 1e-12 and adapt_full["weil_fidelity"] > 1.0 - 1e-10
    assert adapt_half0["final_energy"] > 1.75 and adapt_half0["weil_fidelity"] <= 0.5 + 1e-9

    return {
        "j27": j27,
        "d4_27_int": d4_27_int,
        "j27_sq_eq_neg729_i8": True,
        "j27_symplectic_and_commutes_phi8": True,
        "g_pos_minpoly_roots": [3, 243],
        "g_pos_bareiss_minors": minors,
        "d2_27_theta_zero_dp02_nonzero": True,
        "mobius_unit_ball_trajectory": mobius_traj,
        "boosted_adaptation": {
            "spectral_gap": round(float(evals_27[2]), 8),
            "max_eigenvalue": round(float(evals_27[-1]), 6),
            "eta_step": round(eta_step, 8),
            "full_70": adapt_full,
            "half_coord0_35": adapt_half0,
        },
    }


def verify_70dim_so35_35_exterior_boost(
    mats: Dict[str, np.ndarray], ops: Dict[str, Any], j27_info: Dict[str, Any]
) -> Dict[str, Any]:
    """Verifies exact 70 x 70 SO(35,35) boost L70 = /\\^4(G9/9) and Weil light-cone invariance."""
    g9 = mats["G9"]
    g_f = [[Fraction(int(g9[i, j]), 9) for j in range(8)] for i in range(8)]
    l70_f = [
        [det4_frac([[g_f[i][j] for j in tup_c] for i in tup_r]) for tup_c in TUPLES_4_8]
        for tup_r in TUPLES_4_8
    ]
    l70 = np.array([[float(x) for x in r] for r in l70_f], dtype=np.float64)

    star = ops["Star"].astype(np.float64)
    p192_f = ops["P192"].astype(np.float64)
    w_re_f = ops["w_re"].astype(np.float64)
    w_im_f = ops["w_im"].astype(np.float64)
    th2_f = ops["theta_sq"].astype(np.float64)

    assert np.allclose(l70, l70.T)
    assert np.allclose(l70.T @ star @ l70, star)
    assert np.allclose(l70 @ w_re_f, w_re_f)
    assert np.allclose(l70 @ w_im_f, w_im_f)
    assert np.allclose(l70 @ th2_f, th2_f)
    assert np.allclose(l70 @ p192_f, p192_f) and np.allclose(p192_f @ l70, p192_f)

    exact_trace = sum(l70_f[i][i] for i in range(70))
    assert exact_trace == Fraction(21286, 81)
    assert exact_trace * 6561 == 1724166

    ev_counts = Counter(round(float(x), 6) for x in np.linalg.eigvalsh(l70))
    assert dict(sorted(ev_counts.items())) == {
        round(1.0 / 81.0, 6): 1,
        round(1.0 / 9.0, 6): 16,
        1.0: 36,
        9.0: 16,
        81.0: 1,
    }

    d4_27_int = j27_info["d4_27_int"]
    p192_int = ops["P192"]
    k4_int = ops["K4"]
    assert np.all(d4_27_int @ ops["w_re"] == 0)
    assert np.all(d4_27_int @ ops["w_im"] == 0)
    assert np.all(d4_27_int @ ops["theta_sq"] == 0)
    assert np.all(d4_27_int @ p192_int == 0)
    assert np.array_equal(d4_27_int @ k4_int, k4_int @ d4_27_int)

    # Check sheared SO(35,35) action on a non-invariant pair u = (0,1,2,4), v = (3,5,6,7)
    idx_u = TUPLES_4_8.index((0, 1, 2, 4))
    idx_v = TUPLES_4_8.index((3, 5, 6, 7))
    e_u = np.zeros(70, dtype=np.float64)
    e_v = np.zeros(70, dtype=np.float64)
    e_u[idx_u] = 1.0
    e_v[idx_v] = 1.0
    lu = l70 @ e_u
    lv = l70 @ e_v
    assert not np.allclose(lu, e_u)
    cup_uv = float(e_u @ star @ e_v)
    cup_l = float(lu @ star @ lv)
    assert abs(cup_uv - (-1.0)) < 1e-10 and abs(cup_l - (-1.0)) < 1e-10

    return {
        "l70_symmetric": True,
        "l70_in_so35_35": True,
        "fixes_w_re_w_im_theta_sq": True,
        "l70_commutes_and_fixes_p192": True,
        "exact_trace_q": str(exact_trace),
        "exact_trace_g9_wedge4": 1724166,
        "spectrum_multiplicities": {"1/81": 1, "1/9": 16, "1": 36, "9": 16, "81": 1},
        "d27_kills_p192_and_commutes_k4": True,
        "sheared_noninvariant_cup_preserved": True,
    }


def main() -> int:
    mats = build_base_and_boost_8x8()
    ops = build_weil_70_exact_operators()
    boost_8 = verify_8x8_lorentzian_boost_and_light_cone(mats)
    j27_info = verify_boosted_j27_mobius_and_adaptation(mats, ops)
    so35_info = verify_70dim_so35_35_exterior_boost(mats, ops, j27_info)

    report = {
        "lorentzian_8x8_su22_boost": boost_8,
        "boosted_j27_and_mobius_spatial_projection": {
            k: v for k, v in j27_info.items() if k not in ("j27", "d4_27_int")
        },
        "so35_35_exterior_boost_and_weil_invariance": so35_info,
    }
    out_path = (
        Path(__file__).resolve().parents[2]
        / "reports"
        / "millennium_ext"
        / "lorentzian_weil_boost.json"
    )
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    b_adapt = j27_info["boosted_adaptation"]
    print(
        f"LORENTZIAN_WEIL_BOOST: detG9={boost_8['g9_det']} "
        f"J27_minors8_ok=True so35_35={so35_info['l70_in_so35_35']} "
        f"tr_L70={so35_info['exact_trace_q']} "
        f"E_full={b_adapt['full_70']['final_energy']} "
        f"E_half0={b_adapt['half_coord0_35']['final_energy']} "
        f"H3={j27_info['mobius_unit_ball_trajectory'][3]['u_coeff']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
