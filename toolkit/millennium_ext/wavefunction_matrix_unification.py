"""Experiment 5: Unified Wave-Function-to-Matrix Operator Audit.

Strictly float-free (int, Fraction, and exact symbolic SymPy rationals).
Outputs: reports/millennium_ext/wavefunction_matrix_unification.json

Unifies all three analytic/oscillatory wave-function constructions in the project
into exact integer/rational/cyclotomic matrix operators:
1. Pillar I (Cyclotomic Fermat Wave Function -> 6x6 Unitary DFT Matrix U_6 over Z[zeta_6]):
   Verify U_6 * U_6^dagger = U_6^dagger * U_6 = 6 * I_6 identically over Z[zeta_6].
2. Pillar II (Dwork Picard-Fuchs Wave Function -> 5x5 Companion Connection Matrices M_PF(x), M_LCS(z)):
   - Fermat window (|psi| < 1): at x = 0, (6*M_PF(0) - I)...(6*M_PF(0) - 5*I) = 0, eigenvalues
     {1/6, 2/6, 3/6, 4/6, 5/6}, trace = 5/2, det = 5/324.
   - LCS window (|psi| > 1): at z = 0, M_LCS(0)^4 != 0 and M_LCS(0)^5 = 0 (MUM nilpotent block).
3. Pillar III (Weil U(2, 2) Hodge Wave Function -> 8x8 J_43, 28x28 D_H^(2), 70x70 D_H^(4), P_Weil):
   - Exact rational complex structure J_H = J_43 / 43 for H_int = [[1+i, 1-2i], [-1+i, 2+i]] / 10:
     J_43^2 = -1849*I_8, J_43^T E_8 J_43 = 1849*E_8, [J_43, Phi_8] = 0, -E_8*J_43 symmetric positive-definite.
   - 28x28 D_H^(2) on /\\^2 Q^8: exact rank = 12 (dim ker = 16 = h^{1,1}), minimal poly D(D^2 + 4) = 0,
     D_H^(2)(Theta) = 0, D_H^(2)(D^+_{0,2}) != 0.
   - 70x70 D_H^(4) & K_Phi^(4) on /\\^4 Q^8: exact rank(D_H^(4)) = 34 (dim ker = 36 = h^{2,2}),
     minimal poly D(D^2 + 4)(D^2 + 16) = 0, [D_H^(4), K_Phi^(4)] = 0.
   - 70x70 algebraic Weil projector P_Weil = (1/192) K_Phi^2 (K_Phi^2 + 4 I):
     P_Weil^2 = P_Weil, tr(P_Weil) = 2, rank(P_Weil) = 2, D_H^(4) * P_Weil = 0,
     P_Weil(w_Re) = w_Re, P_Weil(w_Im) = w_Im, P_Weil(Theta^2) = 0,
     K_Phi^(4) rotates w_Re <-> w_Im by +-4, and divisor Mukai vectors exp(c*Theta) always
     have P_Weil(ch_2) = 0 in the 128-dim H^even(A_H, Q).
4. Aggregates whole-project verified receipts into a unified matrix scorecard.
"""

from __future__ import annotations

import itertools
import json
import sys
from fractions import Fraction
from pathlib import Path
from typing import Any, Dict, List, Sequence, Tuple

import sympy as sp

sys.path.insert(0, str(Path(__file__).resolve().parent))
from high_precision_period_pslq import build_weil_classes_int
from mumford_cm_specializer import rational_rank


PAIRS_2_8: List[Tuple[int, int]] = list(itertools.combinations(range(8), 2))
P2_IDX: Dict[Tuple[int, int], int] = {t: i for i, t in enumerate(PAIRS_2_8)}
TUPLES_4_8: List[Tuple[int, int, int, int]] = list(itertools.combinations(range(8), 4))
T4_IDX: Dict[Tuple[int, int, int, int], int] = {t: i for i, t in enumerate(TUPLES_4_8)}


# ---------------------------------------------------------------------------
# Generic exact rational linear algebra helpers
# ---------------------------------------------------------------------------

def mat_mul_frac(A: Sequence[Sequence[Fraction]], B: Sequence[Sequence[Fraction]]) -> List[List[Fraction]]:
    r = len(A)
    c = len(B[0]) if B else 0
    m = len(B)
    out = [[Fraction(0)] * c for _ in range(r)]
    for i in range(r):
        Ai = A[i]
        Oi = out[i]
        for k in range(m):
            aik = Ai[k]
            if aik:
                Bk = B[k]
                for j in range(c):
                    if Bk[j]:
                        Oi[j] += aik * Bk[j]
    return out


def mat_add_scaled_eye(A: Sequence[Sequence[Fraction]], s: Fraction) -> List[List[Fraction]]:
    n = len(A)
    return [[A[i][j] + (s if i == j else Fraction(0)) for j in range(n)] for i in range(n)]


def mat_vec_frac(A: Sequence[Sequence[Fraction]], v: Sequence[Fraction]) -> List[Fraction]:
    return [sum(A[i][j] * v[j] for j in range(len(v))) for i in range(len(A))]


def is_zero_mat_frac(A: Sequence[Sequence[Fraction]]) -> bool:
    return all(x == 0 for row in A for x in row)


# ---------------------------------------------------------------------------
# Pillar I: Z[zeta_6] 6x6 Unitary Matrix U_6
# ---------------------------------------------------------------------------

def z6_mul(a: Tuple[int, int], b: Tuple[int, int]) -> Tuple[int, int]:
    """Multiplies (a0 + a1*zeta6) * (b0 + b1*zeta6) with zeta6^2 = zeta6 - 1."""
    return (a[0] * b[0] - a[1] * b[1], a[0] * b[1] + a[1] * b[0] + a[1] * b[1])


def z6_add(a: Tuple[int, int], b: Tuple[int, int]) -> Tuple[int, int]:
    return (a[0] + b[0], a[1] + b[1])


def z6_conj(a: Tuple[int, int]) -> Tuple[int, int]:
    """Complex conjugate bar(a0 + a1*zeta6) = (a0 + a1) - a1*zeta6."""
    return (a[0] + a[1], -a[1])


def z6_pow(k: int) -> Tuple[int, int]:
    table = [(1, 0), (0, 1), (-1, 1), (-1, 0), (0, -1), (1, -1)]
    return table[k % 6]


def verify_pillar_1_cyclotomic_u6() -> Dict[str, Any]:
    U6 = [[z6_pow(j * k) for k in range(6)] for j in range(6)]
    U6_dag = [[z6_conj(U6[k][j]) for k in range(6)] for j in range(6)]

    def mm_z6(A: List[List[Tuple[int, int]]], B: List[List[Tuple[int, int]]]) -> List[List[Tuple[int, int]]]:
        out = [[(0, 0) for _ in range(6)] for _ in range(6)]
        for i in range(6):
            for j in range(6):
                acc = (0, 0)
                for k in range(6):
                    acc = z6_add(acc, z6_mul(A[i][k], B[k][j]))
                out[i][j] = acc
        return out

    P1 = mm_z6(U6, U6_dag)
    P2 = mm_z6(U6_dag, U6)
    target = [[(6, 0) if i == j else (0, 0) for j in range(6)] for i in range(6)]
    assert P1 == target and P2 == target
    return {
        "ring": "Z[zeta_6]",
        "matrix_size": [6, 6],
        "unitary_u_udag_eq_6i": True,
        "unitary_udag_u_eq_6i": True,
        "abs_det_squared_expected": 6 ** 6,
    }


# ---------------------------------------------------------------------------
# Pillar II: Dwork Picard-Fuchs 5x5 Companion Connection Matrices
# ---------------------------------------------------------------------------

def verify_pillar_2_picard_fuchs_5x5() -> Dict[str, Any]:
    x_sym, z_sym, t_sym = sp.symbols("x z t")

    # Fermat window ODE: 648*(1 - x)*t^5 - 1620*t^4 + 1530*t^3 - 675*t^2 + 137*t - 10 = 0
    den_f = sp.Integer(648) * (1 - x_sym)
    M_fermat_x = sp.Matrix([
        [0, 1, 0, 0, 0],
        [0, 0, 1, 0, 0],
        [0, 0, 0, 1, 0],
        [0, 0, 0, 0, 1],
        [sp.Integer(10) / den_f, -sp.Integer(137) / den_f, sp.Integer(675) / den_f,
         -sp.Integer(1530) / den_f, sp.Integer(1620) / den_f],
    ])
    cp_f = sp.factor(sp.Poly(M_fermat_x.charpoly(t_sym).as_expr(), t_sym).as_expr())
    expected_f = sp.expand(t_sym ** 5 - (1 / den_f) * (1620 * t_sym ** 4 - 1530 * t_sym ** 3 + 675 * t_sym ** 2 - 137 * t_sym + 10))
    assert sp.simplify(cp_f - expected_f) == 0

    # Integer matrix 6*M_PF(0) satisfies prod_{k=1}^5 (6*M_PF(0) - k*I_5) = 0
    M6_0 = (6 * M_fermat_x.subs(x_sym, 0)).applyfunc(lambda v: Fraction(int(sp.Rational(v).p), int(sp.Rational(v).q)))
    prod_mat = [[Fraction(1) if i == j else Fraction(0) for j in range(5)] for i in range(5)]
    M6_list = [[M6_0[i, j] for j in range(5)] for i in range(5)]
    for k in range(1, 6):
        factor_mat = mat_add_scaled_eye(M6_list, Fraction(-k))
        prod_mat = mat_mul_frac(prod_mat, factor_mat)
    assert is_zero_mat_frac(prod_mat)

    M_f0_f = [[M6_list[i][j] / 6 for j in range(5)] for i in range(5)]
    tr_f0 = sum(M_f0_f[i][i] for i in range(5))
    det_f0 = Fraction(int(sp.Rational(M_fermat_x.subs(x_sym, 0).det()).p), int(sp.Rational(M_fermat_x.subs(x_sym, 0).det()).q))
    assert tr_f0 == Fraction(5, 2) and det_f0 == Fraction(5, 324)

    # LCS window ODE: (1 - 46656*z)*t^5 - z*(116640*t^4 + 110160*t^3 + 48600*t^2 + 9864*t + 720) = 0
    den_l = 1 - sp.Integer(46656) * z_sym
    M_lcs_z = sp.Matrix([
        [0, 1, 0, 0, 0],
        [0, 0, 1, 0, 0],
        [0, 0, 0, 1, 0],
        [0, 0, 0, 0, 1],
        [720 * z_sym / den_l, 9864 * z_sym / den_l, 48600 * z_sym / den_l,
         110160 * z_sym / den_l, 116640 * z_sym / den_l],
    ])
    cp_l = sp.Poly(M_lcs_z.charpoly(t_sym).as_expr(), t_sym).as_expr()
    expected_l = t_sym ** 5 - (z_sym / den_l) * (116640 * t_sym ** 4 + 110160 * t_sym ** 3 + 48600 * t_sym ** 2 + 9864 * t_sym + 720)
    assert sp.simplify(cp_l - expected_l) == 0

    M_l0 = [[Fraction(1) if j == i + 1 else Fraction(0) for j in range(5)] for i in range(5)]
    p4 = M_l0
    for _ in range(3):
        p4 = mat_mul_frac(p4, M_l0)
    p5 = mat_mul_frac(p4, M_l0)
    assert not is_zero_mat_frac(p4) and is_zero_mat_frac(p5)

    return {
        "fermat_window_5x5_charpoly_verified": True,
        "fermat_indicial_cayley_hamilton_zero": True,
        "fermat_indicial_eigenvalues_6x": [1, 2, 3, 4, 5],
        "fermat_indicial_trace": str(tr_f0),
        "fermat_indicial_det": str(det_f0),
        "lcs_window_5x5_charpoly_verified": True,
        "lcs_z0_nilpotent_order_5": True,
    }


# ---------------------------------------------------------------------------
# Pillar III: Weil U(2, 2) Exact Rational Matrix Ladder (8x8, 28x28, 70x70, 128-dim)
# ---------------------------------------------------------------------------

def build_deriv_matrix_frac(X_frac: Sequence[Sequence[Fraction]], k: int) -> List[List[Fraction]]:
    tups = list(itertools.combinations(range(8), k))
    t_idx = {t: i for i, t in enumerate(tups)}
    n = len(tups)
    D = [[Fraction(0)] * n for _ in range(n)]
    for col, tup in enumerate(tups):
        for pos in range(k):
            i = tup[pos]
            for j in range(8):
                val = X_frac[i][j]
                if val == 0:
                    continue
                if j in tup and j != i:
                    continue
                lst = list(tup)
                lst[pos] = j
                invs = sum(1 for a in range(k) for b in range(a + 1, k) if lst[a] > lst[b])
                sgn = -1 if invs % 2 else 1
                row = t_idx[tuple(sorted(lst))]
                D[row][col] += val * sgn
    return D


def wedge2_to_vec70(u28: Sequence[Fraction], v28: Sequence[Fraction]) -> List[Fraction]:
    out = [Fraction(0)] * 70
    for idx1, (a, b) in enumerate(PAIRS_2_8):
        cu = u28[idx1]
        if cu == 0:
            continue
        for idx2, (c, d) in enumerate(PAIRS_2_8):
            cv = v28[idx2]
            if cv == 0 or a == c or a == d or b == c or b == d:
                continue
            lst = [a, b, c, d]
            invs = sum(1 for x in range(4) for y in range(x + 1, 4) if lst[x] > lst[y])
            sgn = -1 if invs % 2 else 1
            out[T4_IDX[tuple(sorted(lst))]] += Fraction(sgn) * cu * cv
    return out


def verify_pillar_3_weil_operators() -> Dict[str, Any]:
    # Exact 8x8 matrices from H_int = [[1+i, 1-2i], [-1+i, 2+i]] / 10
    J43_int = [
        [0, 47, -6, -2, -10, -10, -10, 10],
        [-47, 0, 2, -6, -10, 10, 10, 10],
        [6, -2, 0, 53, 20, -10, -10, -20],
        [2, 6, -53, 0, -10, -20, -20, 10],
        [-10, -10, 20, -10, 0, 50, 7, 0],
        [-10, 10, -10, -20, -50, 0, 0, 7],
        [-10, 10, -10, -20, -7, 0, 0, 50],
        [10, 10, -20, 10, 0, -7, -50, 0],
    ]
    E8_int = [[0] * 8 for _ in range(8)]
    Phi8_int = [[0] * 8 for _ in range(8)]
    for a in range(4):
        E8_int[2 * a][2 * a + 1] = 1
        E8_int[2 * a + 1][2 * a] = -1
        sgn_phi = 1 if a < 2 else -1
        Phi8_int[2 * a][2 * a + 1] = sgn_phi
        Phi8_int[2 * a + 1][2 * a] = -sgn_phi

    J_frac = [[Fraction(x, 43) for x in row] for row in J43_int]
    E_frac = [[Fraction(x) for x in row] for row in E8_int]
    Phi_frac = [[Fraction(x) for x in row] for row in Phi8_int]

    # Check J_H^2 = -I_8, J_H^T E J_H = E, [J_H, Phi_8] = 0
    J2 = mat_mul_frac(J_frac, J_frac)
    assert J2 == [[Fraction(-1) if i == j else Fraction(0) for j in range(8)] for i in range(8)]
    JT = [[J_frac[j][i] for j in range(8)] for i in range(8)]
    assert mat_mul_frac(mat_mul_frac(JT, E_frac), J_frac) == E_frac
    assert mat_mul_frac(J_frac, Phi_frac) == mat_mul_frac(Phi_frac, J_frac)

    # G_pos = -E8 * J43 symmetric positive definite
    neg_E = [[-E8_int[i][j] for j in range(8)] for i in range(8)]
    G_sym = sp.Matrix(neg_E) * sp.Matrix(J43_int)
    assert G_sym == G_sym.T
    minors = [int(G_sym[:k, :k].det()) for k in range(1, 9)]
    assert minors == [47, 2209, 115197, 6007401, 226594950, 8547002500, 316068152450, 11688200277601]
    assert minors[-1] == 43 ** 8 and all(m > 0 for m in minors)

    # 28x28 D_H^(2) on /\^2 Q^8
    D2 = build_deriv_matrix_frac(J_frac, 2)
    rk_D2 = rational_rank(D2)
    assert rk_D2 == 12
    D2_2 = mat_mul_frac(D2, D2)
    D2_3 = mat_mul_frac(D2_2, D2)
    poly_D2 = [[D2_3[i][j] + 4 * D2[i][j] for j in range(28)] for i in range(28)]
    assert is_zero_mat_frac(poly_D2)

    theta_28 = [Fraction(1) if p in ((0, 1), (2, 3), (4, 5), (6, 7)) else Fraction(0) for p in PAIRS_2_8]
    dp02_28 = [
        Fraction(1) if p in ((0, 4), (1, 5)) else Fraction(0) for p in PAIRS_2_8
    ]
    assert all(x == 0 for x in mat_vec_frac(D2, theta_28))
    assert any(x != 0 for x in mat_vec_frac(D2, dp02_28))

    # 70x70 D_H^(4) and K_Phi^(4) on /\^4 Q^8
    D4 = build_deriv_matrix_frac(J_frac, 4)
    K4 = build_deriv_matrix_frac(Phi_frac, 4)
    rk_D4 = rational_rank(D4)
    assert rk_D4 == 34
    assert mat_mul_frac(D4, K4) == mat_mul_frac(K4, D4)

    # Minimal polynomial check: D4 * (D4^2 + 4*I) * (D4^2 + 16*I) == 0
    D4_2 = mat_mul_frac(D4, D4)
    min_poly_D4 = mat_mul_frac(
        mat_mul_frac(D4, mat_add_scaled_eye(D4_2, Fraction(4))),
        mat_add_scaled_eye(D4_2, Fraction(16)),
    )
    assert is_zero_mat_frac(min_poly_D4)

    # Algebraic spectral projector P_Weil = (1/192) K4^2 (K4^2 + 4*I)
    K4_2 = mat_mul_frac(K4, K4)
    P_raw = mat_mul_frac(K4_2, mat_add_scaled_eye(K4_2, Fraction(4)))
    P_weil = [[P_raw[i][j] / 192 for j in range(70)] for i in range(70)]
    assert mat_mul_frac(P_weil, P_weil) == P_weil
    tr_P = sum(P_weil[i][i] for i in range(70))
    rk_P = rational_rank(P_weil)
    assert tr_P == Fraction(2) and rk_P == 2
    assert is_zero_mat_frac(mat_mul_frac(D4, P_weil))

    w_re_d, w_im_d = build_weil_classes_int()
    v_re = [Fraction(w_re_d.get(t, 0)) for t in TUPLES_4_8]
    v_im = [Fraction(w_im_d.get(t, 0)) for t in TUPLES_4_8]
    v_th2 = wedge2_to_vec70(theta_28, theta_28)

    assert mat_vec_frac(P_weil, v_re) == v_re
    assert mat_vec_frac(P_weil, v_im) == v_im
    assert all(x == 0 for x in mat_vec_frac(P_weil, v_th2))
    assert all(x == 0 for x in mat_vec_frac(D4, v_re))
    assert all(x == 0 for x in mat_vec_frac(D4, v_im))
    assert all(x == 0 for x in mat_vec_frac(D4, v_th2))

    # Exact K_Phi rotation action between w_Re and w_Im
    kv_re = mat_vec_frac(K4, v_re)
    kv_im = mat_vec_frac(K4, v_im)
    if kv_re == [4 * x for x in v_im]:
        k_sign = +4
        assert kv_im == [-4 * x for x in v_re]
    else:
        assert kv_re == [-4 * x for x in v_im]
        assert kv_im == [4 * x for x in v_re]
        k_sign = -4

    # 128-dim H^even Mukai-vector projection check:
    # Divisor Chern character exp(c*Theta) always has ch_2 = (c^2/2) * Theta^2 -> P_Weil(ch_2) = 0;
    # A genuine non-divisor object E with ch_2 = c0*Theta^2 + a*w_Re + b*w_Im ((a,b) != (0,0))
    # satisfies P_Weil(ch_2) = a*w_Re + b*w_Im and span{P_Weil(ch_2), K_Phi(P_Weil(ch_2))} = W_{Q(i)}.
    for c_div in (1, 2, -3):
        ch2_div = [Fraction(c_div * c_div, 2) * x for x in v_th2]
        assert all(x == 0 for x in mat_vec_frac(P_weil, ch2_div))

    mukai_ch2_sample = [v_th2[i] + 3 * v_re[i] - 2 * v_im[i] for i in range(70)]
    proj_mukai = mat_vec_frac(P_weil, mukai_ch2_sample)
    rot_mukai = mat_vec_frac(K4, proj_mukai)
    assert rational_rank([proj_mukai, rot_mukai, v_re, v_im]) == 2

    return {
        "j43_denominator": 43,
        "j43_sq_eq_neg1849_i8": True,
        "j43_symplectic_and_commutes_phi8": True,
        "polarization_g_pos_minors": minors,
        "h11_operator_d2_shape": [28, 28],
        "h11_operator_d2_rank": rk_D2,
        "h11_ker_dim": 28 - rk_D2,
        "h11_d2_minpoly_d_d2_plus_4": True,
        "theta_in_ker_d2": True,
        "dp02_killed_by_d2": True,
        "h22_operator_d4_shape": [70, 70],
        "h22_operator_d4_rank": rk_D4,
        "h22_ker_dim": 70 - rk_D4,
        "h22_d4_minpoly_d_d2p4_d2p16": True,
        "d4_commutes_with_kphi4": True,
        "p_weil_shape": [70, 70],
        "p_weil_idempotent": True,
        "p_weil_trace": int(tr_P),
        "p_weil_rank": rk_P,
        "d4_times_p_weil_zero": True,
        "kphi_rotates_wre_to_wim_factor": k_sign,
        "h_even_total_dim": 128,
        "divisor_mukai_p_weil_always_zero": True,
        "non_divisor_mukai_generates_2d_weil_plane": True,
    }


def main() -> int:
    p1 = verify_pillar_1_cyclotomic_u6()
    p2 = verify_pillar_2_picard_fuchs_5x5()
    p3 = verify_pillar_3_weil_operators()

    repo_root = Path(__file__).resolve().parent.parent.parent
    ext_dir = repo_root / "reports" / "millennium_ext"
    base_receipt = repo_root / "dist" / "FULL_AUTOMATION_VERIFICATION_RECEIPT.json"

    scorecard: Dict[str, Any] = {
        "pillars_verified_this_run": 3,
        "previous_reports_loaded": {},
    }
    if base_receipt.exists():
        bdata = json.loads(base_receipt.read_text(encoding="utf-8"))
        scorecard["locked_baseline_theorems"] = bdata["lean_audit"]["total_theorems"]
        scorecard["locked_baseline_passed"] = bdata["ALL_CHECKS_PASSED"]
    for rep_name in (
        "matrix_factorization_scaling.json",
        "schur_5050_diagonal_audit.json",
        "non_koszul_mf_closure.json",
        "high_precision_period_pslq.json",
    ):
        rp = ext_dir / rep_name
        if rp.exists():
            scorecard["previous_reports_loaded"][rep_name] = True

    out = {
        "pillar_1_cyclotomic_u6_wavefunction": p1,
        "pillar_2_picard_fuchs_5x5_companions": p2,
        "pillar_3_weil_u22_spectral_projectors": p3,
        "unified_project_scorecard": scorecard,
    }
    out_path = ext_dir / "wavefunction_matrix_unification.json"
    out_path.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(
        f"WAVEFUNCTION_MATRIX_UNIFICATION: U6_ok={p1['unitary_u_udag_eq_6i']} "
        f"PF5_ok={p2['fermat_indicial_cayley_hamilton_zero']} LCS_nilp5={p2['lcs_z0_nilpotent_order_5']} "
        f"rk(D2)={p3['h11_operator_d2_rank']}/28 rk(D4)={p3['h22_operator_d4_rank']}/70 "
        f"tr(P_Weil)={p3['p_weil_trace']} rk(P_Weil)={p3['p_weil_rank']} k_sign={p3['kphi_rotates_wre_to_wim_factor']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
