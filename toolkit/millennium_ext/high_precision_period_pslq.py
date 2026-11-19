"""Experiment 4: High-Precision (85-90 Digit) Period Homotopy, PSLQ & LLL Recovery.

Combines 85-90 digit `mpmath` numerical period evaluation with exact PSLQ/LLL
rational reconstruction and SymPy symbolic verification (zero floating-point
dependence in the certified algebraic/integer identities):
1. Part A (Wall 1 - Dwork Sextic Pencil):
   - Evaluates all 5 Fermat-centered Frobenius periods y_1..y_5 at transcendental
     psi_0 = pi/10 to 85 decimal digits, confirming < 1e-78 agreement with 5F4.
   - Recovers the exact 5th-order Picard-Fuchs integer ODE via 85-digit PSLQ
     with residual < 1e-75 and checks symbolic agreement with prod(6*t - k).
   - Evaluates the LCS period varpi_0(z) at transcendental z_0 = 1 / (6^6 * e)
     and recovers the exact LCS Picard-Fuchs ODE via 85-digit PSLQ.
   - Verifies exact factorial divisibility (6n)! % (n!)^6 == 0 for n = 0..20.
2. Part B (Wall 3 - 4-Dimensional Weil U(2, 2) Period Family off E_i^4):
   - Evaluates the exact Weil U(2, 2) family H -> Omega(H) at 90 digits across
     4 stages (CM E_i^4 -> Block-1D -> Diag transcendental -> Generic U(2, 2)).
   - Tracks the exact Picard number collapse rho: 16 -> 7 -> 6 -> 1 via fast
     90-digit incremental LLL and computes exact rational Sym^2(NS) ranks and
     Weil-class coverage in exterior-4 Q^8 (70-dim).
   - Proves symbolically over Z[i, h_00..h_11, bar_h_00..bar_h_11] that all 16
     Riemann Bilinear Relations and all 17 Hodge (4,0)+(3,1) equations for both
     w_Re and w_Im vanish identically across the entire 4-dim Weil family.
"""

from __future__ import annotations

import itertools
import json
import math
import sys
import time
from fractions import Fraction
from pathlib import Path
from typing import Any, Dict, List, Sequence, Tuple

import mpmath as mp
import sympy as sp

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mumford_cm_specializer import rational_nullspace, rational_rank


PAIRS_2_8: List[Tuple[int, int]] = list(itertools.combinations(range(8), 2))
TUPLES_4_8: List[Tuple[int, int, int, int]] = list(itertools.combinations(range(8), 4))
TUP4_IDX: Dict[Tuple[int, int, int, int], int] = {t: i for i, t in enumerate(TUPLES_4_8)}


# ---------------------------------------------------------------------------
# Part A Helpers: Dwork Sextic 85-Digit Periods & Exact Integer Integrality
# ---------------------------------------------------------------------------

def dwork_fermat_theta_pows(
    r: int, psi: mp.mpf, max_j: int = 5, terms: int = 220
) -> List[mp.mpf]:
    """Computes theta_x^j y_r(psi) (j = 0..max_j, x = psi^6) from Frobenius series."""
    x = psi ** 6
    c = mp.mpf(1)
    vals = [mp.mpf(0)] * (max_j + 1)
    for n in range(terms):
        e = mp.mpf(n) + mp.mpf(r) / 6
        term = c * (psi ** r)
        for j in range(max_j + 1):
            vals[j] += term * (e ** j)
        num = mp.mpf(6 * n + r) ** 5
        den = mp.mpf(1)
        for k in range(1, 6):
            den *= mp.mpf(6 * n + 6 + r - k)
        c = c * num / den * x
    return vals


def dwork_lcs_theta_pows(
    z: mp.mpf, max_j: int = 5, terms: int = 220
) -> List[mp.mpf]:
    """Computes theta_z^j varpi_0(z) (j = 0..max_j) from sum (6n)!/(n!)^6 z^n."""
    c = mp.mpf(1)
    vals = [mp.mpf(0)] * (max_j + 1)
    for n in range(terms):
        nz = mp.mpf(n)
        for j in range(max_j + 1):
            vals[j] += c * (nz ** j)
        num = mp.mpf(1)
        for offset in range(1, 7):
            num *= mp.mpf(6 * n + offset)
        den = mp.mpf(n + 1) ** 6
        c = c * num / den * z
    return vals


def run_part_a_dwork_pf() -> Dict[str, Any]:
    mp.mp.dps = 85
    psi0 = mp.pi / 10
    x0 = psi0 ** 6

    fermat_periods_check: Dict[str, Any] = {}
    tv_r1: List[mp.mpf] = []
    for r in range(1, 6):
        tv = dwork_fermat_theta_pows(r, psi0, max_j=5, terms=220)
        if r == 1:
            tv_r1 = tv
        a_params = [mp.mpf(r) / 6] * 5
        b_params = [mp.mpf(1) + mp.mpf(r - k) / 6 for k in range(1, 6) if k != r]
        y_hyp = (psi0 ** r) * mp.hyper(a_params, b_params, x0)
        diff = abs(tv[0] - y_hyp)
        assert diff < mp.mpf("1e-78"), f"y_{r} mismatch: {diff}"
        fermat_periods_check[f"y_{r}"] = {
            "val_prefix": mp.nstr(tv[0], 24),
            "hyper_diff": mp.nstr(diff, 4),
        }

    # PSLQ recovery of 6^5 * x * theta_x^5 - prod_{k=1}^5 (6*theta_x - k) = 0
    vec_f = [x0 * tv_r1[5], tv_r1[5], tv_r1[4], tv_r1[3], tv_r1[2], tv_r1[1], tv_r1[0]]
    rel_f = mp.pslq(vec_f, tol=mp.mpf("1e-60"), maxcoeff=10 ** 9, maxsteps=2000)
    assert rel_f is not None
    res_f = abs(sum(c * v for c, v in zip(rel_f, vec_f)))
    assert res_f < mp.mpf("1e-75")

    t_sym = sp.Symbol("t")
    pf_poly = sp.Poly(sp.expand(sp.prod(6 * t_sym - k for k in range(1, 6))), t_sym)
    raw_expected_f = [-7776] + [int(c) for c in pf_poly.all_coeffs()]
    g_f = math.gcd(*[abs(x) for x in raw_expected_f])
    assert g_f == 12
    expected_f = [x // g_f for x in raw_expected_f]
    rel_f_norm = [-int(c) for c in rel_f] if rel_f[0] > 0 else [int(c) for c in rel_f]
    assert rel_f_norm == expected_f, f"PF mismatch: {rel_f_norm} vs {expected_f}"

    # PSLQ recovery at LCS point z_0 = 1 / (6^6 * e)
    z0 = mp.mpf(1) / (mp.mpf(6 ** 6) * mp.e)
    tv_z = dwork_lcs_theta_pows(z0, max_j=5, terms=220)
    vec_l = [tv_z[5], z0 * tv_z[5], z0 * tv_z[4], z0 * tv_z[3], z0 * tv_z[2], z0 * tv_z[1], z0 * tv_z[0]]
    rel_l = mp.pslq(vec_l, tol=mp.mpf("1e-60"), maxcoeff=10 ** 9, maxsteps=2000)
    assert rel_l is not None
    res_l = abs(sum(c * v for c, v in zip(rel_l, vec_l)))
    assert res_l < mp.mpf("1e-75")
    lcs_poly = sp.Poly(sp.expand(6 * sp.prod(6 * t_sym + k for k in range(1, 6))), t_sym)
    raw_expected_l = [1] + [-int(c) for c in lcs_poly.all_coeffs()]
    g_l = math.gcd(*[abs(x) for x in raw_expected_l])
    expected_l = [x // g_l for x in raw_expected_l]
    rel_l_norm = [-int(c) for c in rel_l] if rel_l[0] < 0 else [int(c) for c in rel_l]
    assert rel_l_norm == expected_l, f"LCS mismatch: {rel_l_norm} vs {expected_l}"

    # Exact integer divisibility (6n)! / (n!)^6 for n = 0..20
    fact_vals: Dict[int, int] = {0: 1}
    for k in range(1, 121):
        fact_vals[k] = fact_vals[k - 1] * k
    integrality = []
    for n in range(21):
        num_i = fact_vals[6 * n]
        den_i = fact_vals[n] ** 6
        assert num_i % den_i == 0
        if n <= 8:
            integrality.append({"n": n, "coeff": num_i // den_i})

    return {
        "dps": 85,
        "psi0": "pi/10",
        "z0": "1/(6^6 * e)",
        "fermat_frobenius_periods": fermat_periods_check,
        "pslq_fermat_pf_ode_coeffs": rel_f_norm,
        "pslq_fermat_pf_residual": mp.nstr(res_f, 4),
        "pslq_lcs_pf_ode_coeffs": rel_l_norm,
        "pslq_lcs_pf_residual": mp.nstr(res_l, 4),
        "lcs_integrality_n0_to_n20_verified": True,
        "lcs_coeffs_n0_to_n8": integrality,
    }


# ---------------------------------------------------------------------------
# Part B Helpers: 90-Digit Weil U(2, 2) Deformation, Fast LLL & Exact Sym^2(NS)
# ---------------------------------------------------------------------------

def det4_divfree(M: Sequence[Sequence[Any]]) -> Any:
    def det3(a: Sequence[Any], b: Sequence[Any], c: Sequence[Any]) -> Any:
        return (
            a[0] * (b[1] * c[2] - b[2] * c[1])
            - a[1] * (b[0] * c[2] - b[2] * c[0])
            + a[2] * (b[0] * c[1] - b[1] * c[0])
        )

    r0, r1, r2, r3 = M
    return (
        r0[0] * det3(r1[1:], r2[1:], r3[1:])
        - r0[1] * det3([r1[0], r1[2], r1[3]], [r2[0], r2[2], r2[3]], [r3[0], r3[2], r3[3]])
        + r0[2] * det3([r1[0], r1[1], r1[3]], [r2[0], r2[1], r2[3]], [r3[0], r3[1], r3[3]])
        - r0[3] * det3(r1[:3], r2[:3], r3[:3])
    )


def make_weil_basis_mp(H: Sequence[Sequence[mp.mpc]]) -> List[List[mp.mpc]]:
    I = mp.mpc(0, 1)

    def vec(pairs: Sequence[Tuple[int, mp.mpc]]) -> List[mp.mpc]:
        v = [mp.mpc(0)] * 8
        for idx, val in pairs:
            v[idx] += val
        return v

    u = [
        vec([(0, mp.mpc(1)), (1, -I)]),
        vec([(2, mp.mpc(1)), (3, -I)]),
        vec([(4, mp.mpc(1)), (5, I)]),
        vec([(6, mp.mpc(1)), (7, I)]),
    ]
    ub = [[mp.conj(x) for x in v] for v in u]

    def lin(terms: Sequence[Tuple[mp.mpc, List[mp.mpc]]]) -> List[mp.mpc]:
        out = [mp.mpc(0)] * 8
        for coef, v in terms:
            for k in range(8):
                out[k] += coef * v[k]
        return out

    return [
        lin([(mp.mpc(1), u[0]), (H[0][0], u[2]), (H[1][0], u[3])]),
        lin([(mp.mpc(1), u[1]), (H[0][1], u[2]), (H[1][1], u[3])]),
        lin([(mp.mpc(1), ub[2]), (H[0][0], ub[0]), (H[0][1], ub[1])]),
        lin([(mp.mpc(1), ub[3]), (H[1][0], ub[0]), (H[1][1], ub[1])]),
    ]


def symp_E_gen(x: Sequence[Any], y: Sequence[Any]) -> Any:
    return sum(x[2 * a] * y[2 * a + 1] - x[2 * a + 1] * y[2 * a] for a in range(4))


def build_weil_classes_int() -> Tuple[Dict[Tuple[int, ...], int], Dict[Tuple[int, ...], int]]:
    u_vecs = [
        [(0, 1 + 0j), (1, -1j)],
        [(2, 1 + 0j), (3, -1j)],
        [(4, 1 + 0j), (5, 1j)],
        [(6, 1 + 0j), (7, 1j)],
    ]
    w_re: Dict[Tuple[int, ...], int] = {}
    w_im: Dict[Tuple[int, ...], int] = {}
    for p0 in u_vecs[0]:
        for p1 in u_vecs[1]:
            for p2 in u_vecs[2]:
                for p3 in u_vecs[3]:
                    tup = (p0[0], p1[0], p2[0], p3[0])
                    c = p0[1] * p1[1] * p2[1] * p3[1]
                    re_i = int(round(c.real))
                    im_i = int(round(c.imag))
                    if re_i != 0:
                        w_re[tup] = re_i
                    if im_i != 0:
                        w_im[tup] = im_i
    return w_re, w_im


def eval_h11_eqs_mp(W: Sequence[Sequence[mp.mpc]]) -> List[List[mp.mpf]]:
    rows: List[List[mp.mpf]] = []
    for a in range(4):
        for b in range(a + 1, 4):
            row_re: List[mp.mpf] = []
            row_im: List[mp.mpf] = []
            for i, j in PAIRS_2_8:
                val = W[a][i] * W[b][j] - W[a][j] * W[b][i]
                row_re.append(mp.re(val))
                row_im.append(mp.im(val))
            rows.append(row_re)
            rows.append(row_im)
    return rows


def lll_mp_fast_exact(B_in: Sequence[Sequence[int]], delta: mp.mpf | None = None) -> List[List[int]]:
    """Fast drift-free 90-digit incremental LLL refreshing only rows k-1 and k on swaps."""
    if delta is None:
        delta = mp.mpf("0.75")
    n = len(B_in)
    m = len(B_in[0])
    B = [list(row) for row in B_in]
    Bstar: List[List[mp.mpf]] = [[mp.mpf(0)] * m for _ in range(n)]
    mu: List[List[mp.mpf]] = [[mp.mpf(0)] * n for _ in range(n)]
    Bnorm: List[mp.mpf] = [mp.mpf(0)] * n

    def gs_row(i: int) -> None:
        v = [mp.mpf(x) for x in B[i]]
        for j in range(i):
            mu[i][j] = sum(mp.mpf(B[i][c]) * Bstar[j][c] for c in range(m)) / Bnorm[j]
            mij = mu[i][j]
            for c in range(m):
                v[c] -= mij * Bstar[j][c]
        Bstar[i] = v
        Bnorm[i] = sum(x * x for x in v)

    for i in range(n):
        gs_row(i)

    k = 1
    while k < n:
        changed = False
        for j in range(k - 1, -1, -1):
            if abs(mu[k][j]) > mp.mpf("0.5"):
                q = int(mp.nint(mu[k][j]))
                if q != 0:
                    Bk = B[k]
                    Bj = B[j]
                    for c in range(m):
                        Bk[c] -= q * Bj[c]
                    for l in range(j):
                        mu[k][l] -= q * mu[j][l]
                    mu[k][j] -= q
                    changed = True
        if changed:
            gs_row(k)
        if Bnorm[k] >= (delta - mu[k][k - 1] ** 2) * Bnorm[k - 1]:
            k += 1
        else:
            B[k], B[k - 1] = B[k - 1], B[k]
            gs_row(k - 1)
            gs_row(k)
            for i in range(k + 1, n):
                mu[i][k - 1] = (
                    sum(mp.mpf(B[i][c]) * Bstar[k - 1][c] for c in range(m)) / Bnorm[k - 1]
                )
                mu[i][k] = sum(mp.mpf(B[i][c]) * Bstar[k][c] for c in range(m)) / Bnorm[k]
            k = max(k - 1, 1)
    return B


def wedge2_to_vec70(u28: Sequence[int], v28: Sequence[int]) -> List[Fraction]:
    out = [Fraction(0)] * 70
    for idx1, (a, b) in enumerate(PAIRS_2_8):
        cu = u28[idx1]
        if cu == 0:
            continue
        for idx2, (c, d) in enumerate(PAIRS_2_8):
            cv = v28[idx2]
            if cv == 0:
                continue
            if a == c or a == d or b == c or b == d:
                continue
            lst = [a, b, c, d]
            invs = sum(1 for x in range(4) for y in range(x + 1, 4) if lst[x] > lst[y])
            sgn = -1 if invs % 2 else 1
            key = tuple(sorted(lst))
            out[TUP4_IDX[key]] += Fraction(sgn * cu * cv)
    return out


def vec70_in_span(vecs: Sequence[Sequence[Fraction]], target: Sequence[Fraction]) -> bool:
    if not vecs:
        return all(x == 0 for x in target)
    base_rk = rational_rank(vecs)
    aug_rk = rational_rank(list(vecs) + [list(target)])
    return aug_rk == base_rk


def run_symbolic_weil_u22_proof() -> Dict[str, Any]:
    """Symbolically proves RBR=0 and Hodge (4,0)+(3,1) vanishing of w_Re, w_Im for ALL H."""
    h00, h01, h10, h11 = sp.symbols("h00 h01 h10 h11")
    hb00, hb01, hb10, hb11 = sp.symbols("hb00 hb01 hb10 hb11")
    ii = sp.I

    def svec(pairs: Sequence[Tuple[int, Any]]) -> List[Any]:
        v = [sp.Integer(0)] * 8
        for idx, val in pairs:
            v[idx] += val
        return v

    u = [
        svec([(0, 1), (1, -ii)]),
        svec([(2, 1), (3, -ii)]),
        svec([(4, 1), (5, ii)]),
        svec([(6, 1), (7, ii)]),
    ]
    ub = [
        svec([(0, 1), (1, ii)]),
        svec([(2, 1), (3, ii)]),
        svec([(4, 1), (5, -ii)]),
        svec([(6, 1), (7, -ii)]),
    ]

    def lin(terms: Sequence[Tuple[Any, List[Any]]]) -> List[Any]:
        return [sum(coef * v[k] for coef, v in terms) for k in range(8)]

    W = [
        lin([(1, u[0]), (h00, u[2]), (h10, u[3])]),
        lin([(1, u[1]), (h01, u[2]), (h11, u[3])]),
        lin([(1, ub[2]), (h00, ub[0]), (h01, ub[1])]),
        lin([(1, ub[3]), (h10, ub[0]), (h11, ub[1])]),
    ]
    Wb = [
        lin([(1, ub[0]), (hb00, ub[2]), (hb10, ub[3])]),
        lin([(1, ub[1]), (hb01, ub[2]), (hb11, ub[3])]),
        lin([(1, u[2]), (hb00, u[0]), (hb01, u[1])]),
        lin([(1, u[3]), (hb10, u[0]), (hb11, u[1])]),
    ]

    rbr_checks = 0
    for a in range(4):
        for b in range(4):
            val = sp.expand(symp_E_gen(W[a], W[b]))
            assert val == 0, f"Symbolic RBR failed at ({a},{b}): {val}"
            rbr_checks += 1

    w_re_int, w_im_int = build_weil_classes_int()

    def eval_sym_4form(T: Dict[Tuple[int, ...], int], v0: Any, v1: Any, v2: Any, v3: Any) -> Any:
        tot = sp.Integer(0)
        for (i0, i1, i2, i3), coef in T.items():
            M = [
                [v0[i0], v0[i1], v0[i2], v0[i3]],
                [v1[i0], v1[i1], v1[i2], v1[i3]],
                [v2[i0], v2[i1], v2[i2], v2[i3]],
                [v3[i0], v3[i1], v3[i2], v3[i3]],
            ]
            tot += coef * det4_divfree(M)
        return sp.expand(tot)

    hodge_checks = 0
    for form_dict in (w_re_int, w_im_int):
        v40 = eval_sym_4form(form_dict, W[0], W[1], W[2], W[3])
        assert v40 == 0, f"(4,0) nonzero symbolically: {v40}"
        hodge_checks += 1
        for a, b, c in itertools.combinations(range(4), 3):
            for d in range(4):
                v31 = eval_sym_4form(form_dict, W[a], W[b], W[c], Wb[d])
                assert v31 == 0, f"(3,1) nonzero symbolically: {v31}"
                hodge_checks += 1

    return {
        "rbr_equations_proved_identically_zero": rbr_checks,
        "hodge_40_and_31_equations_proved_zero": hodge_checks,
    }


def run_part_b_weil_u22() -> Dict[str, Any]:
    sym_res = run_symbolic_weil_u22_proof()

    mp.mp.dps = 90
    I = mp.mpc(0, 1)
    w_re_int, w_im_int = build_weil_classes_int()
    w_re_70 = [Fraction(w_re_int.get(t, 0)) for t in TUPLES_4_8]
    w_im_70 = [Fraction(w_im_int.get(t, 0)) for t in TUPLES_4_8]

    def eval_mp_4form(
        T: Dict[Tuple[int, ...], int],
        v0: List[mp.mpc],
        v1: List[mp.mpc],
        v2: List[mp.mpc],
        v3: List[mp.mpc],
    ) -> mp.mpc:
        tot = mp.mpc(0)
        for (i0, i1, i2, i3), coef in T.items():
            M = [
                [v0[i0], v0[i1], v0[i2], v0[i3]],
                [v1[i0], v1[i1], v1[i2], v1[i3]],
                [v2[i0], v2[i1], v2[i2], v2[i3]],
                [v3[i0], v3[i1], v3[i2], v3[i3]],
            ]
            tot += coef * det4_divfree(M)
        return tot

    H_stages = [
        ("stage0_ei4_cm", [[mp.mpc(0), mp.mpc(0)], [mp.mpc(0), mp.mpc(0)]], 16),
        ("stage1_block1d_transcendental", [[mp.pi / 10, mp.mpc(0)], [mp.mpc(0), mp.mpc(0)]], 7),
        ("stage2_diag_transcendental", [[mp.pi / 10, mp.mpc(0)], [mp.mpc(0), mp.e / 10]], 6),
        (
            "stage3_generic_weil_u22",
            [
                [mp.pi / 11 + I * mp.sqrt(2) / 13, mp.log(2) / 17 + I * mp.sqrt(3) / 19],
                [mp.log(3) / 23 + I * mp.sqrt(5) / 29, mp.e / 31 + I * mp.sqrt(7) / 37],
            ],
            1,
        ),
    ]

    v_theta_28 = [1 if p in ((0, 1), (2, 3), (4, 5), (6, 7)) else 0 for p in PAIRS_2_8]
    S = 10 ** 32
    stage_records: List[Dict[str, Any]] = []

    for name, H, expected_rho in H_stages:
        t0 = time.perf_counter()
        W = make_weil_basis_mp(H)
        Wb = [[mp.conj(x) for x in v] for v in W]
        max_rbr = max(abs(symp_E_gen(W[a], W[b])) for a in range(4) for b in range(4))
        assert max_rbr < mp.mpf("1e-80")

        max_w_re = abs(eval_mp_4form(w_re_int, W[0], W[1], W[2], W[3]))
        max_w_im = abs(eval_mp_4form(w_im_int, W[0], W[1], W[2], W[3]))
        for a, b, c in itertools.combinations(range(4), 3):
            for d in range(4):
                max_w_re = max(max_w_re, abs(eval_mp_4form(w_re_int, W[a], W[b], W[c], Wb[d])))
                max_w_im = max(max_w_im, abs(eval_mp_4form(w_im_int, W[a], W[b], W[c], Wb[d])))
        assert max_w_re < mp.mpf("1e-80") and max_w_im < mp.mpf("1e-80")

        # Sylvester positive-definiteness check of -i E(w_a, bar(w_b))
        H_pol = mp.matrix(
            [[mp.re(-I * symp_E_gen(W[a], Wb[b])) for b in range(4)] for a in range(4)]
        )
        lead_minors = [mp.det(H_pol[:k, :k]) for k in range(1, 5)]
        assert all(m > mp.mpf("0.1") for m in lead_minors)

        rows_h11 = eval_h11_eqs_mp(W)
        B_lll: List[List[int]] = []
        for j in range(28):
            vec = [0] * 28 + [int(mp.nint(rows_h11[r][j] * S)) for r in range(12)]
            vec[j] = 1
            B_lll.append(vec)
        M_red = lll_mp_fast_exact(B_lll)

        ns_vecs: List[List[int]] = []
        min_non_ns = mp.mpf(10)
        max_ns_res = mp.mpf(0)
        for r in range(28):
            v28 = M_red[r][:28]
            res = max(abs(sum(v28[j] * rows_h11[k][j] for j in range(28))) for k in range(12))
            if res < mp.mpf("1e-80") and max(abs(x) for x in v28) < 10 ** 6:
                ns_vecs.append(v28)
                max_ns_res = max(max_ns_res, res)
            elif res > 0:
                min_non_ns = min(min_non_ns, res)

        assert len(ns_vecs) == expected_rho, f"{name}: rho={len(ns_vecs)} != {expected_rho}"
        if expected_rho == 1:
            assert ns_vecs[0] == v_theta_28 or ns_vecs[0] == [-x for x in v_theta_28]
            assert min_non_ns > mp.mpf("1e-25")

        sym2_vecs = [
            wedge2_to_vec70(ns_vecs[a], ns_vecs[b])
            for a in range(len(ns_vecs))
            for b in range(a, len(ns_vecs))
        ]
        sym2_rk = rational_rank(sym2_vecs)
        cov_re = vec70_in_span(sym2_vecs, w_re_70)
        cov_im = vec70_in_span(sym2_vecs, w_im_70)
        elapsed_s = round(time.perf_counter() - t0, 3)

        stage_records.append({
            "stage": name,
            "rho": len(ns_vecs),
            "sym2_ns_rank": sym2_rk,
            "covers_w_re": cov_re,
            "covers_w_im": cov_im,
            "max_rbr_residual": mp.nstr(max_rbr, 4),
            "max_w_re_hodge_residual": mp.nstr(max_w_re, 4),
            "max_w_im_hodge_residual": mp.nstr(max_w_im, 4),
            "max_lll_ns_residual": mp.nstr(max_ns_res, 4),
            "min_non_ns_gap": mp.nstr(min_non_ns, 4),
            "elapsed_s": elapsed_s,
        })

    assert stage_records[0]["rho"] == 16 and stage_records[0]["sym2_ns_rank"] == 36
    assert stage_records[0]["covers_w_re"] and stage_records[0]["covers_w_im"]
    assert stage_records[3]["rho"] == 1 and stage_records[3]["sym2_ns_rank"] == 1
    assert not stage_records[3]["covers_w_re"] and not stage_records[3]["covers_w_im"]

    return {
        "dps": 90,
        "lll_scale_log10": 32,
        "symbolic_proof": sym_res,
        "weil_u22_deformation_ladder": stage_records,
    }


def main() -> int:
    t0 = time.perf_counter()
    part_a = run_part_a_dwork_pf()
    part_b = run_part_b_weil_u22()
    total_s = round(time.perf_counter() - t0, 3)

    out = {
        "total_elapsed_s": total_s,
        "part_a_dwork_picard_fuchs_pslq": part_a,
        "part_b_weil_u22_period_lll": part_b,
    }
    rep_path = (
        Path(__file__).resolve().parent.parent.parent
        / "reports"
        / "millennium_ext"
        / "high_precision_period_pslq.json"
    )
    rep_path.parent.mkdir(parents=True, exist_ok=True)
    rep_path.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print("HIGH_PRECISION_PERIOD_PSLQ_SUMMARY:")
    print(f"  Part A Fermat PSLQ ODE: {part_a['pslq_fermat_pf_ode_coeffs']} (res={part_a['pslq_fermat_pf_residual']})")
    print(f"  Part A LCS    PSLQ ODE: {part_a['pslq_lcs_pf_ode_coeffs']} (res={part_a['pslq_lcs_pf_residual']})")
    for st in part_b["weil_u22_deformation_ladder"]:
        print(
            f"  {st['stage']}: rho={st['rho']}, sym2_rk={st['sym2_ns_rank']}, "
            f"cov=({st['covers_w_re']},{st['covers_w_im']}), nonNS_gap={st['min_non_ns_gap']} ({st['elapsed_s']}s)"
        )
    print(f"  Total elapsed: {total_s}s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
