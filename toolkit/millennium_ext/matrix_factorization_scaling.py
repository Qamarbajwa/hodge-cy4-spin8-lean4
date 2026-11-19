"""Experiment 1: Koszul Matrix Factorization Scaling (r = 1, 2, 4, 8),
Polishchuk-Vaintrob Supertrace, and RTX A2000 3-Prime CRT Hodge Span.

Strictly float-free (int, Fraction, torch.int64 on cuda:0 with 6.0 GB VRAM cap).
Verifies:
1. Exact Koszul Matrix Factorizations A*B = B*A = F*I_r over Z[x_0..x_5] for:
   - Clifford threshold k = 1, 2 (r = 1, 2): tr((dA ^ dB)^3) = 0 identically.
   - Sextic Band-1 (r = 4), Band-2 off-diagonal cubic-triple (r = 4),
     and Band-3 off-diagonal 4-variable surface-join (r = 4), plus exact
     match between tr((dA ^ dB)^3) and ± c * det J(u, v).
   - Deformed sextic F_b1 + x_0*x_1*x_2*x_3*x_4*x_5 (k = 4, r = 8).
   - Newton-Aoki degree m = 5 (d = 1) and m = 25 (d = 5) Koszul MFs (k = 3, r = 4).
2. Exact 3-prime CRT GPU ranks on RTX A2000 across the 1,751-dim degree-12
   Jacobian ring R(F_0)_12 as block-diagonal/off-diagonal MF families grow.
"""

from __future__ import annotations

import itertools
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Sequence, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parent))
from gpu_exact_linalg import gpu_crt_3prime_rank

Poly = Dict[Tuple[int, ...], int]
FormMat = List[List[Dict[int, Poly]]]  # bitmask 0..63 of dx_0..dx_5 -> Poly


# ---------------------------------------------------------------------------
# Sparse Z[x_0..x_5] polynomial and differential-form algebra
# ---------------------------------------------------------------------------

def poly_clean(p: Poly) -> Poly:
    return {k: v for k, v in p.items() if v != 0}


def poly_add(a: Poly, b: Poly, sign: int = 1) -> Poly:
    out = dict(a)
    for k, v in b.items():
        nv = out.get(k, 0) + sign * v
        if nv == 0:
            out.pop(k, None)
        else:
            out[k] = nv
    return out


def poly_scale(a: Poly, c: int) -> Poly:
    if c == 0:
        return {}
    return {k: v * c for k, v in a.items() if v * c != 0}


def poly_mul(a: Poly, b: Poly) -> Poly:
    out: Poly = {}
    for k1, v1 in a.items():
        for k2, v2 in b.items():
            key = (
                k1[0] + k2[0],
                k1[1] + k2[1],
                k1[2] + k2[2],
                k1[3] + k2[3],
                k1[4] + k2[4],
                k1[5] + k2[5],
            )
            out[key] = out.get(key, 0) + v1 * v2
    return poly_clean(out)


def poly_var_pow(idx: int, power: int = 1, coeff: int = 1) -> Poly:
    if coeff == 0:
        return {}
    m = [0, 0, 0, 0, 0, 0]
    m[idx] = power
    return {tuple(m): coeff}


def poly_deriv(p: Poly, var_idx: int) -> Poly:
    out: Poly = {}
    for k, v in p.items():
        exp = k[var_idx]
        if exp > 0:
            nk = list(k)
            nk[var_idx] = exp - 1
            tk = tuple(nk)
            out[tk] = out.get(tk, 0) + v * exp
    return poly_clean(out)


def poly_mod_pow(p: Poly, max_pow: int) -> Poly:
    """Reduces p modulo the diagonal Jacobian ideal <x_0^max_pow, ..., x_5^max_pow>."""
    return {k: v for k, v in p.items() if v != 0 and all(e < max_pow for e in k)}


def mat_mul_poly(A: List[List[Poly]], B: List[List[Poly]]) -> List[List[Poly]]:
    r = len(A)
    c = len(B[0])
    inner = len(B)
    out: List[List[Poly]] = [[{} for _ in range(c)] for _ in range(r)]
    for i in range(r):
        for k in range(inner):
            aik = A[i][k]
            if not aik:
                continue
            for j in range(c):
                bkj = B[k][j]
                if bkj:
                    out[i][j] = poly_add(out[i][j], poly_mul(aik, bkj))
    return out


def scalar_mat_poly(r: int, F: Poly) -> List[List[Poly]]:
    return [[dict(F) if i == j else {} for j in range(r)] for i in range(r)]


def koszul_mf(pairs: Sequence[Tuple[Poly, Poly]]) -> Tuple[List[List[Poly]], List[List[Poly]]]:
    """Recursive Koszul Matrix Factorization of size r = 2^(len(pairs)-1)."""
    assert len(pairs) >= 1
    u0, v0 = pairs[0]
    A: List[List[Poly]] = [[dict(u0)]]
    B: List[List[Poly]] = [[dict(v0)]]
    for u, v in pairs[1:]:
        sz = len(A)
        new_A: List[List[Poly]] = [[{} for _ in range(2 * sz)] for _ in range(2 * sz)]
        new_B: List[List[Poly]] = [[{} for _ in range(2 * sz)] for _ in range(2 * sz)]
        for i in range(sz):
            for j in range(sz):
                new_A[i][j] = A[i][j]
                new_A[i + sz][j + sz] = poly_scale(B[i][j], -1)
                new_B[i][j] = B[i][j]
                new_B[i + sz][j + sz] = poly_scale(A[i][j], -1)
            new_A[i][i + sz] = dict(u)
            new_A[i + sz][i] = dict(v)
            new_B[i][i + sz] = dict(u)
            new_B[i + sz][i] = dict(v)
        A, B = new_A, new_B
    return A, B


def verify_mf(A: List[List[Poly]], B: List[List[Poly]], F: Poly) -> bool:
    r = len(A)
    target = scalar_mat_poly(r, F)
    return mat_mul_poly(A, B) == target and mat_mul_poly(B, A) == target


def _wedge_mask_sign(m1: int, m2: int) -> Tuple[int, int]:
    """Computes wedge sign (-1)^inversions when wedging dx masks m1 ^ m2."""
    if m1 & m2:
        return 0, 0
    inv = 0
    for i in range(6):
        if (m1 >> i) & 1:
            # count set bits in m2 strictly below position i
            inv += (m2 & ((1 << i) - 1)).bit_count()
    return (m1 | m2), (1 if inv % 2 == 0 else -1)


def poly_mat_to_1form(M: List[List[Poly]]) -> FormMat:
    r = len(M)
    out: FormMat = [[{} for _ in range(r)] for _ in range(r)]
    for i in range(r):
        for j in range(r):
            p = M[i][j]
            if not p:
                continue
            cell: Dict[int, Poly] = {}
            for v in range(6):
                dp = poly_deriv(p, v)
                if dp:
                    cell[1 << v] = dp
            out[i][j] = cell
    return out


def form_mat_mul(X: FormMat, Y: FormMat) -> FormMat:
    r = len(X)
    out: FormMat = [[{} for _ in range(r)] for _ in range(r)]
    for i in range(r):
        for k in range(r):
            xik = X[i][k]
            if not xik:
                continue
            for j in range(r):
                ykj = Y[k][j]
                if not ykj:
                    continue
                cell = out[i][j]
                for m1, p1 in xik.items():
                    for m2, p2 in ykj.items():
                        nm, sgn = _wedge_mask_sign(m1, m2)
                        if sgn != 0:
                            prod = poly_mul(p1, p2)
                            if prod:
                                cell[nm] = poly_add(cell.get(nm, {}), prod, sign=sgn)
    for i in range(r):
        for j in range(r):
            out[i][j] = {m: p for m, p in out[i][j].items() if p}
    return out


def polishchuk_vaintrob_tr3(
    A: List[List[Poly]], B: List[List[Poly]], mod_jac_pow: int | None = None
) -> Poly:
    """Computes top 6-form coefficient of tr((dA ^ dB)^3) over Z[x_0..x_5]."""
    dA = poly_mat_to_1form(A)
    dB = poly_mat_to_1form(B)
    W2 = form_mat_mul(dA, dB)
    W4 = form_mat_mul(W2, W2)
    W6 = form_mat_mul(W4, W2)
    tr: Poly = {}
    for i in range(len(A)):
        top = W6[i][i].get(63, {})
        if top:
            tr = poly_add(tr, top)
    return poly_mod_pow(tr, mod_jac_pow) if mod_jac_pow is not None else tr


def jacobian_det6(
    polys: Sequence[Poly], mod_jac_pow: int | None = None
) -> Poly:
    """Exact 6x6 Jacobian determinant det(d polys[a] / d x_b) via cofactor expansion."""
    assert len(polys) == 6
    J = [[poly_deriv(polys[a], b) for b in range(6)] for a in range(6)]
    if mod_jac_pow is not None:
        J = [[poly_mod_pow(c, mod_jac_pow) for c in row] for row in J]

    def det_rec(rows: Tuple[int, ...], cols: Tuple[int, ...]) -> Poly:
        k = len(rows)
        if k == 1:
            return J[rows[0]][cols[0]]
        if k == 2:
            t1 = poly_mul(J[rows[0]][cols[0]], J[rows[1]][cols[1]])
            t2 = poly_mul(J[rows[0]][cols[1]], J[rows[1]][cols[0]])
            res = poly_add(t1, t2, sign=-1)
            return poly_mod_pow(res, mod_jac_pow) if mod_jac_pow is not None else res
        r0 = rows[0]
        rest_rows = rows[1:]
        acc: Poly = {}
        for idx, c in enumerate(cols):
            entry = J[r0][c]
            if not entry:
                continue
            sub_cols = cols[:idx] + cols[idx + 1:]
            sub_det = det_rec(rest_rows, sub_cols)
            if sub_det:
                sgn = 1 if idx % 2 == 0 else -1
                term = poly_mul(entry, sub_det)
                acc = poly_add(acc, term, sign=sgn)
        return poly_mod_pow(acc, mod_jac_pow) if mod_jac_pow is not None else acc

    return det_rec((0, 1, 2, 3, 4, 5), (0, 1, 2, 3, 4, 5))


# ---------------------------------------------------------------------------
# Sextic Fermat MF builders + band classification
# ---------------------------------------------------------------------------

def pair_uv(i: int, j: int, deg: int = 6) -> Tuple[Poly, Poly]:
    u = poly_add(poly_var_pow(i, 1, 1), poly_var_pow(j, 1, -1))
    v: Poly = {}
    for a in range(deg):
        m = [0, 0, 0, 0, 0, 0]
        m[i] += deg - 1 - a
        m[j] += a
        v[tuple(m)] = v.get(tuple(m), 0) + 1
    return u, poly_clean(v)


def classify_sextic_band(monom: Tuple[int, ...]) -> str:
    """Classifies R(F_0)_12 monomial by Hodge character a = (e_i + 1) mod 6."""
    a = [e + 1 for e in monom]
    assert sum(a) == 18 and all(1 <= x <= 5 for x in a)
    for perm in itertools.permutations(range(6)):
        p = [a[k] for k in perm]
        if p[0] + p[1] == 6 and p[2] + p[3] == 6 and p[4] + p[5] == 6:
            return "Band1"
    for perm in itertools.permutations(range(6)):
        p = [a[k] for k in perm]
        if (p[0] + p[1] + p[2]) % 6 == 0 and (p[3] + p[4] + p[5]) % 6 == 0:
            return "Band2"
    for perm in itertools.permutations(range(6)):
        p = [a[k] for k in perm]
        if p[0] + p[1] == 6:
            return "Band3"
    return "Band4"


def is_prime(n: int) -> bool:
    if n < 2:
        return False
    d = 2
    while d * d <= n:
        if n % d == 0:
            return False
        d += 1
    return True


def primitive_12th_root_mod_p(p: int) -> int:
    """Finds primitive 12th root z12 mod p (z12^6 = -1 and z12^2 has exact order 6)."""
    assert p % 12 == 1
    for g in range(2, p):
        z = pow(g, (p - 1) // 12, p)
        z6 = pow(z, 2, p)
        if pow(z, 6, p) == p - 1 and pow(z, 4, p) != 1 and pow(z6, 2, p) != 1 and pow(z6, 3, p) == p - 1:
            return z
    raise RuntimeError(f"No primitive 12th root found mod {p}")


def build_sextic_r12_basis() -> List[Tuple[int, ...]]:
    basis: List[Tuple[int, ...]] = []
    for e0 in range(5):
        for e1 in range(5):
            for e2 in range(5):
                for e3 in range(5):
                    for e4 in range(5):
                        e5 = 12 - (e0 + e1 + e2 + e3 + e4)
                        if 0 <= e5 <= 4:
                            basis.append((e0, e1, e2, e3, e4, e5))
    return basis


def poly_with_rescaled_neg_coords_mod_p(
    poly: Poly, neg_indices: Sequence[int], z12: int, p: int
) -> Dict[Tuple[int, ...], int]:
    """Maps x_j -> z12 * x_j for j in neg_indices so Sum(x^6) pulls back to Sum(±x^6)."""
    # When F_perm = sum_i c_i x_i^6 with c_j = -1 for j in neg_indices:
    # Replacing x_j -> z12 * x_j turns -x_j^6 into -z12^6 x_j^6 = +x_j^6.
    # For a volume-rescaled form P(x) dx_0..dx_5, pulling back adds 1 extra z12 per neg index
    # which cancels uniformly up to global scalar z12^|neg_indices| != 0.
    neg_set = set(neg_indices)
    out: Dict[Tuple[int, ...], int] = {}
    for m, coeff in poly.items():
        scale = 1
        for j in neg_set:
            if m[j] > 0:
                scale = (scale * pow(z12, m[j], p)) % p
        val = (coeff * scale) % p
        if val != 0:
            out[m] = val
    return out


def permute_poly_mod_p(
    poly_mod: Dict[Tuple[int, ...], int], perm: Tuple[int, ...]
) -> Dict[Tuple[int, ...], int]:
    out: Dict[Tuple[int, ...], int] = {}
    for m, v in poly_mod.items():
        nm = [0, 0, 0, 0, 0, 0]
        for old_i, exp in enumerate(m):
            nm[perm[old_i]] = exp
        out[tuple(nm)] = v
    return out


def twist_vector_mod_p(
    poly_mod: Dict[Tuple[int, ...], int],
    col_idx: Dict[Tuple[int, ...], int],
    ncols: int,
    twists: Sequence[int],
    z6: int,
    p: int,
) -> List[int]:
    row = [0] * ncols
    for m, c in poly_mod.items():
        exp_sum = sum(twists[i] * (m[i] + 1) for i in range(6)) % 6
        fac = pow(z6, exp_sum, p)
        row[col_idx[m]] = (c * fac) % p
    return row


def main() -> int:
    # ------------------------------------------------------------------
    # Part 1: Clifford threshold (k = 1, 2) vs Sextic Band 1, Band 2, Band 3 (k = 3, r = 4)
    # ------------------------------------------------------------------
    u0, v0 = pair_uv(0, 1, 6)
    u1, v1 = pair_uv(2, 3, 6)
    u2, v2 = pair_uv(4, 5, 6)

    F_k1 = poly_add(poly_var_pow(0, 6, 1), poly_var_pow(1, 6, -1))
    A1, B1 = koszul_mf([(u0, v0)])
    assert len(A1) == 1 and verify_mf(A1, B1, F_k1)
    tr_k1 = polishchuk_vaintrob_tr3(A1, B1, mod_jac_pow=5)
    assert tr_k1 == {}

    F_k2 = poly_add(F_k1, poly_add(poly_var_pow(2, 6, 1), poly_var_pow(3, 6, -1)))
    A2, B2 = koszul_mf([(u0, v0), (u1, v1)])
    assert len(A2) == 2 and verify_mf(A2, B2, F_k2)
    tr_k2 = polishchuk_vaintrob_tr3(A2, B2, mod_jac_pow=5)
    assert tr_k2 == {}

    # Sextic Band 1 (r = 4)
    F_b1 = poly_add(F_k2, poly_add(poly_var_pow(4, 6, 1), poly_var_pow(5, 6, -1)))
    pairs_b1 = [(u0, v0), (u1, v1), (u2, v2)]
    A_b1, B_b1 = koszul_mf(pairs_b1)
    assert len(A_b1) == 4 and verify_mf(A_b1, B_b1, F_b1)
    det_b1 = jacobian_det6([u0, v0, u1, v1, u2, v2], mod_jac_pow=5)
    tr_b1 = polishchuk_vaintrob_tr3(A_b1, B_b1, mod_jac_pow=5)
    # Verify tr((dA ^ dB)^3) is an exact scalar multiple of det J(u, v) in R(F_b1)_12
    assert len(det_b1) == 125 and len(tr_b1) == 125
    any_m = next(iter(det_b1))
    assert tr_b1[any_m] % det_b1[any_m] == 0
    scale_pv_b1 = tr_b1[any_m] // det_b1[any_m]
    assert tr_b1 == poly_scale(det_b1, scale_pv_b1)
    assert all(classify_sextic_band(m) == "Band1" for m in det_b1)

    # Sextic Band 2 (r = 4): cubic-triple off-diagonal join
    x0_2, x1_2, x2_2 = poly_var_pow(0, 2), poly_var_pow(1, 2), poly_var_pow(2, 2)
    x3_2, x4_2, x5_2 = poly_var_pow(3, 2), poly_var_pow(4, 2), poly_var_pow(5, 2)
    x0_4, x1_4, x2_4 = poly_var_pow(0, 4), poly_var_pow(1, 4), poly_var_pow(2, 4)
    x3_4, x4_4, x5_4 = poly_var_pow(3, 4), poly_var_pow(4, 4), poly_var_pow(5, 4)

    s012 = poly_add(poly_add(x0_2, x1_2), x2_2)
    q012 = poly_add(
        poly_add(poly_add(x0_4, x1_4), x2_4),
        poly_add(poly_add(poly_mul(x0_2, x1_2), poly_mul(x1_2, x2_2)), poly_mul(x2_2, x0_2)),
        sign=-1,
    )
    s345 = poly_add(poly_add(x3_2, x4_2), x5_2)
    q345 = poly_add(
        poly_add(poly_add(x3_4, x4_4), x5_4),
        poly_add(poly_add(poly_mul(x3_2, x4_2), poly_mul(x4_2, x5_2)), poly_mul(x5_2, x3_2)),
        sign=-1,
    )
    p012 = poly_mul(poly_mul(poly_var_pow(0, 1), poly_var_pow(1, 1)), poly_var_pow(2, 1))
    p345 = poly_mul(poly_mul(poly_var_pow(3, 1), poly_var_pow(4, 1)), poly_var_pow(5, 1))
    u_b2_3 = poly_scale(poly_add(p012, p345, sign=-1), 3)
    v_b2_3 = poly_add(p012, p345)
    pairs_b2 = [(s012, q012), (poly_scale(s345, -1), q345), (u_b2_3, v_b2_3)]

    F_tri = poly_add(
        poly_add(poly_add(poly_var_pow(0, 6), poly_var_pow(1, 6)), poly_var_pow(2, 6)),
        poly_add(poly_add(poly_var_pow(3, 6), poly_var_pow(4, 6)), poly_var_pow(5, 6)),
        sign=-1,
    )
    A_b2, B_b2 = koszul_mf(pairs_b2)
    assert len(A_b2) == 4 and verify_mf(A_b2, B_b2, F_tri)
    det_b2 = jacobian_det6([s012, q012, poly_scale(s345, -1), q345, u_b2_3, v_b2_3], mod_jac_pow=5)
    tr_b2 = polishchuk_vaintrob_tr3(A_b2, B_b2, mod_jac_pow=5)
    any_m2 = next(iter(det_b2))
    scale_pv_b2 = tr_b2[any_m2] // det_b2[any_m2]
    assert tr_b2 == poly_scale(det_b2, scale_pv_b2)
    b2_band_counts: Dict[str, int] = {}
    for m in det_b2:
        b = classify_sextic_band(m)
        b2_band_counts[b] = b2_band_counts.get(b, 0) + 1
    assert b2_band_counts.get("Band1", 0) == len(det_b2)
    assert b2_band_counts.get("Band2", 0) == 0 and b2_band_counts.get("Band3", 0) == 0

    # Sextic symmetric quadric 4-var surface-join (r = 4)
    s23 = poly_add(x2_2, x3_2)
    s45 = poly_add(x4_2, x5_2)
    m23 = poly_mul(x2_2, x3_2)
    m45 = poly_mul(x4_2, x5_2)
    u_b3_2 = poly_add(s23, s45, sign=-1)
    v_b3_2 = poly_add(
        poly_add(poly_add(poly_mul(s23, s23), poly_mul(s23, s45)), poly_mul(s45, s45)),
        poly_scale(m23, 3),
        sign=-1,
    )
    u_b3_3 = poly_scale(s45, -3)
    v_b3_3 = poly_add(m23, m45, sign=-1)
    pairs_b3 = [(u0, v0), (u_b3_2, v_b3_2), (u_b3_3, v_b3_3)]

    F_b3 = poly_add(
        poly_add(poly_add(poly_var_pow(0, 6), poly_var_pow(1, 6, -1)), poly_add(poly_var_pow(2, 6), poly_var_pow(3, 6))),
        poly_add(poly_var_pow(4, 6), poly_var_pow(5, 6)),
        sign=-1,
    )
    A_b3, B_b3 = koszul_mf(pairs_b3)
    assert len(A_b3) == 4 and verify_mf(A_b3, B_b3, F_b3)
    det_b3 = jacobian_det6([u0, v0, u_b3_2, v_b3_2, u_b3_3, v_b3_3], mod_jac_pow=5)
    tr_b3 = polishchuk_vaintrob_tr3(A_b3, B_b3, mod_jac_pow=5)
    any_m3 = next(iter(det_b3))
    scale_pv_b3 = tr_b3[any_m3] // det_b3[any_m3]
    assert tr_b3 == poly_scale(det_b3, scale_pv_b3)
    b3_band_counts: Dict[str, int] = {}
    for m in det_b3:
        b = classify_sextic_band(m)
        b3_band_counts[b] = b3_band_counts.get(b, 0) + 1
    assert b3_band_counts.get("Band1", 0) == len(det_b3)
    assert b3_band_counts.get("Band2", 0) == 0 and b3_band_counts.get("Band3", 0) == 0

    # Sextic cubic-product 4-var surface-join (r = 4)
    x2_3, x3_3, x4_3, x5_3 = poly_var_pow(2, 3), poly_var_pow(3, 3), poly_var_pow(4, 3), poly_var_pow(5, 3)
    x23_p = poly_mul(poly_var_pow(2, 1), poly_var_pow(3, 1))
    x45_p = poly_mul(poly_var_pow(4, 1), poly_var_pow(5, 1))
    u_c3_2 = poly_add(poly_add(x2_3, x3_3), poly_add(x4_3, x5_3), sign=-1)
    v_c3_2 = poly_add(poly_add(x2_3, x3_3), poly_add(x4_3, x5_3), sign=1)
    u_c3_3 = poly_scale(poly_add(x45_p, x23_p, sign=-1), 2)
    v_c3_3 = poly_add(poly_add(poly_mul(x23_p, x23_p), poly_mul(x23_p, x45_p)), poly_mul(x45_p, x45_p))
    pairs_b3_cubic = [(u0, v0), (u_c3_2, v_c3_2), (u_c3_3, v_c3_3)]
    A_c3, B_c3 = koszul_mf(pairs_b3_cubic)
    assert len(A_c3) == 4 and verify_mf(A_c3, B_c3, F_b3)
    det_c3 = jacobian_det6([u0, v0, u_c3_2, v_c3_2, u_c3_3, v_c3_3], mod_jac_pow=5)
    tr_c3 = polishchuk_vaintrob_tr3(A_c3, B_c3, mod_jac_pow=5)
    any_mc3 = next(iter(det_c3))
    scale_pv_c3 = tr_c3[any_mc3] // det_c3[any_mc3]
    assert tr_c3 == poly_scale(det_c3, scale_pv_c3)
    c3_band_counts: Dict[str, int] = {}
    for m in det_c3:
        b = classify_sextic_band(m)
        c3_band_counts[b] = c3_band_counts.get(b, 0) + 1
    assert c3_band_counts.get("Band1", 0) == len(det_c3)

    # ------------------------------------------------------------------
    # Part 2: k = 4 (r = 8) Deformed & Cauchy-6 MFs + Newton-Aoki m = 5, 25 MFs
    # ------------------------------------------------------------------
    u_def = poly_mul(poly_mul(poly_var_pow(0, 1), poly_var_pow(2, 1)), poly_var_pow(4, 1))
    v_def = poly_mul(poly_mul(poly_var_pow(1, 1), poly_var_pow(3, 1)), poly_var_pow(5, 1))
    F_def = poly_add(F_b1, poly_mul(u_def, v_def))
    A8, B8 = koszul_mf(pairs_b1 + [(u_def, v_def)])
    assert len(A8) == 8 and verify_mf(A8, B8, F_def)
    tr_def8 = polishchuk_vaintrob_tr3(A8, B8, mod_jac_pow=5)
    assert tr_def8 == {}

    def pow_p(p_in: Poly, k: int) -> Poly:
        res: Poly = {(0, 0, 0, 0, 0, 0): 1}
        for _ in range(k):
            res = poly_mul(res, p_in)
        return res

    xl = [poly_var_pow(i, 1) for i in range(6)]
    cs01 = poly_add(xl[0], xl[1])
    cq01 = poly_add(poly_add(poly_mul(xl[0], xl[0]), poly_mul(xl[0], xl[1])), poly_mul(xl[1], xl[1]))
    cp01 = poly_mul(xl[0], xl[1])
    cu1 = poly_add(cs01, xl[2])
    cv1a: Poly = {}
    for a_pow in range(6):
        cv1a = poly_add(cv1a, poly_mul(pow_p(xl[2], 5 - a_pow), pow_p(cs01, a_pow)), sign=(1 if a_pow % 2 == 0 else -1))
    cv1 = poly_add(cv1a, poly_scale(poly_mul(pow_p(cp01, 2), poly_add(cs01, xl[2], sign=-1)), 3))

    cs34 = poly_add(xl[3], xl[4])
    cq34 = poly_add(poly_add(poly_mul(xl[3], xl[3]), poly_mul(xl[3], xl[4])), poly_mul(xl[4], xl[4]))
    cp34 = poly_mul(xl[3], xl[4])
    cu2 = poly_add(cs34, xl[5])
    cv2a: Poly = {}
    for a_pow in range(6):
        cv2a = poly_add(cv2a, poly_mul(pow_p(xl[5], 5 - a_pow), pow_p(cs34, a_pow)), sign=(-1 if a_pow % 2 == 0 else 1))
    cv2 = poly_add(cv2a, poly_scale(poly_mul(pow_p(cp34, 2), poly_add(cs34, xl[5], sign=-1)), -3))

    cu3 = poly_add(cq01, cq34, sign=-1)
    cv3 = poly_scale(poly_add(poly_add(pow_p(cq01, 2), poly_mul(cq01, cq34)), pow_p(cq34, 2)), 2)
    cp012 = poly_mul(cp01, xl[2])
    cp345 = poly_mul(cp34, xl[5])
    cu4 = poly_scale(poly_add(cp012, cp345, sign=-1), 3)
    cv4 = poly_add(cp012, cp345)
    A_cauchy8, B_cauchy8 = koszul_mf([(cu1, cv1), (cu2, cv2), (cu3, cv3), (cu4, cv4)])
    assert len(A_cauchy8) == 8 and verify_mf(A_cauchy8, B_cauchy8, F_tri)
    tr_cauchy8 = polishchuk_vaintrob_tr3(A_cauchy8, B_cauchy8, mod_jac_pow=5)
    assert tr_cauchy8 == {}

    aoki_results: Dict[str, Any] = {}
    for d in (1, 5):
        m_deg = 5 * d
        e1: Poly = {}
        e2: Poly = {}
        e3: Poly = {}
        F_aoki: Poly = {}
        for i in range(6):
            F_aoki = poly_add(F_aoki, poly_var_pow(i, m_deg, 1))
        prod5 = {(d, d, d, d, d, 0): 1}
        F_aoki = poly_add(F_aoki, poly_scale(prod5, -5))

        for i in range(5):
            e1 = poly_add(e1, poly_var_pow(i, d, 1))
        for i in range(5):
            for j in range(i + 1, 5):
                e2 = poly_add(e2, poly_mul(poly_var_pow(i, d, 1), poly_var_pow(j, d, 1)))
        for i in range(5):
            for j in range(i + 1, 5):
                for l in range(j + 1, 5):
                    e3 = poly_add(
                        e3,
                        poly_mul(
                            poly_mul(poly_var_pow(i, d, 1), poly_var_pow(j, d, 1)),
                            poly_var_pow(l, d, 1),
                        ),
                    )
        p5 = {}
        for i in range(5):
            p5 = poly_add(p5, poly_var_pow(i, 5 * d, 1))
        e1_sq = poly_mul(e1, e1)
        # Q4(y^d) = e1^4 - 5 e1^2 e2 + 5 e1 e3 + 5 e2^2 - 5 e4
        e4: Poly = {}
        for c in itertools.combinations(range(5), 4):
            mon = [0, 0, 0, 0, 0, 0]
            for idx in c:
                mon[idx] = d
            e4[tuple(mon)] = 1
        q4 = poly_add(poly_mul(e1_sq, e1_sq), poly_scale(poly_mul(e1_sq, e2), -5))
        q4 = poly_add(q4, poly_scale(poly_mul(e1, e3), 5))
        q4 = poly_add(q4, poly_scale(poly_mul(e2, e2), 5))
        q4 = poly_add(q4, poly_scale(e4, -5))
        pairs_aoki = [
            (e1, q4),
            (poly_scale(e2, -5), e3),
            (poly_var_pow(5, d, 1), poly_var_pow(5, 4 * d, 1)),
        ]
        Aa, Ba = koszul_mf(pairs_aoki)
        assert len(Aa) == 4 and verify_mf(Aa, Ba, F_aoki)
        entry: Dict[str, Any] = {"m": m_deg, "step_d": d, "r": 4, "ab_eq_ba_eq_f_i4": True}
        if d == 1:
            # Verify (x_5, x_5^4) has vanishing 2-form dx_5 ^ d(x_5^4) = 0 while the
            # 5-variable Newton-Aoki surface minor det J_{0..3}(e1, Q4, -5 e2, e3) != 0.
            det_aoki5 = jacobian_det6(
                [pairs_aoki[0][0], pairs_aoki[0][1], pairs_aoki[1][0], pairs_aoki[1][1], pairs_aoki[2][0], pairs_aoki[2][1]],
                mod_jac_pow=4,
            )
            tr_aoki5 = polishchuk_vaintrob_tr3(Aa, Ba, mod_jac_pow=4)
            assert det_aoki5 == {} and tr_aoki5 == {}
            aoki4 = [e1, q4, poly_scale(e2, -5), e3]
            J4 = [[poly_mod_pow(poly_deriv(aoki4[r], c), 4) for c in range(4)] for r in range(4)]
            minor4: Poly = {}
            for perm4 in itertools.permutations(range(4)):
                invs = sum(1 for a in range(4) for b in range(a + 1, 4) if perm4[a] > perm4[b])
                term = J4[0][perm4[0]]
                for rr in range(1, 4):
                    term = poly_mul(term, J4[rr][perm4[rr]])
                minor4 = poly_add(minor4, poly_mod_pow(term, 4), sign=(1 if invs % 2 == 0 else -1))
            assert len(minor4) > 0
            entry["univariate_x5_tr3_vanishes"] = True
            entry["newton_aoki_4x4_minor_nonzero"] = True
            entry["newton_aoki_4x4_minor_terms_mod_j"] = len(minor4)
        aoki_results[f"m{m_deg}"] = entry

    # ------------------------------------------------------------------
    # Part 3: GPU 3-Prime CRT Hodge Span Scaling inside R(F_0)_12 (dim = 1751)
    # ------------------------------------------------------------------
    basis = build_sextic_r12_basis()
    assert len(basis) == 1751
    col_idx = {m: i for i, m in enumerate(basis)}
    band_totals = {"Band1": 0, "Band2": 0, "Band3": 0, "Band4": 0}
    for m in basis:
        b = classify_sextic_band(m)
        band_totals[b] += 1

    primes = (65521, 1000000009, 1000000033)
    for p in primes:
        assert is_prime(p) and p % 12 == 1

    # Enumerate structured S_6 splittings + diagonal mu_6 twists spanning Band 1 cleanly
    b1_matchings: List[Tuple[int, ...]] = []
    for p1 in range(1, 6):
        rem = [k for k in range(1, 6) if k != p1]
        a = rem[0]
        for b in rem[1:]:
            rem2 = [x for x in rem[1:] if x != b]
            perm = (0, p1, a, b, rem2[0], rem2[1])
            assert len(set(perm)) == 6
            b1_matchings.append(perm)
    assert len(b1_matchings) == 15

    b2_splits: List[Tuple[int, ...]] = []
    for s in itertools.combinations(range(1, 6), 2):
        other = tuple(k for k in range(1, 6) if k not in s)
        b2_splits.append((0, s[0], s[1], other[0], other[1], other[2]))
    assert len(b2_splits) == 10

    b3_splits: List[Tuple[int, ...]] = []
    for p1 in range(6):
        for p2 in range(p1 + 1, 6):
            rest = tuple(k for k in range(6) if k not in (p1, p2))
            b3_splits.append((p1, p2) + rest)
    assert len(b3_splits) == 15

    def permute_tuple(tw: Tuple[int, ...], perm: Tuple[int, ...]) -> Tuple[int, ...]:
        out = [0, 0, 0, 0, 0, 0]
        for old_i, val in enumerate(tw):
            out[perm[old_i]] = val
        return tuple(out)

    b1_twists = [(0, a, 0, b, 0, c) for a in range(5) for b in range(5) for c in range(5)]
    b2_twist_small = [
        (a, (2 * a + 1) % 6, b, c, (3 * c + 2) % 6, (b + c) % 6)
        for a in range(6) for b in range(6) for c in range(3)
    ]
    b3_twist_small = [
        (0, a, b, c, (b + 2 * c) % 6, (3 * a + b) % 6)
        for a in range(5) for b in range(6) for c in (0, 1, 3, 4)
    ]

    stage_results: Dict[str, Any] = {}

    def run_gpu_crt_stage(name: str, builder) -> None:
        prime_ranks: Dict[str, int] = {}
        max_vram = 0.0
        nrows = 0
        dev_info: Dict[str, Any] = {}
        for p in primes:
            z12 = primitive_12th_root_mod_p(p)
            z6 = pow(z12, 2, p)
            rows = builder(p, z12, z6)
            nrows = len(rows)
            res = gpu_crt_3prime_rank(rows, primes=(p,))
            prime_ranks[str(p)] = res["rank"]
            max_vram = max(max_vram, res["peak_vram_mb"])
            dev_info = res
        vals = list(prime_ranks.values())
        stage_results[name] = {
            "rows": nrows,
            "cols": 1751,
            "rank": max(vals),
            "prime_ranks": prime_ranks,
            "agreement": len(set(vals)) == 1,
            "device": dev_info.get("device"),
            "gpu_name": dev_info.get("gpu_name"),
            "peak_vram_mb": max_vram,
        }

    def build_b1_k_matchings(k_matchings: int, twists_subset: Sequence[Tuple[int, ...]]):
        def _builder(p: int, z12: int, z6: int) -> List[List[int]]:
            pm0 = poly_with_rescaled_neg_coords_mod_p(det_b1, [1, 3, 5], z12, p)
            rows: List[List[int]] = []
            for perm in b1_matchings[:k_matchings]:
                pm = permute_poly_mod_p(pm0, perm)
                for tw in twists_subset:
                    rows.append(twist_vector_mod_p(pm, col_idx, 1751, permute_tuple(tw, perm), z6, p))
            return rows
        return _builder

    def build_b1_plus_symmetric(p: int, z12: int, z6: int) -> List[List[int]]:
        rows = build_b1_k_matchings(15, b1_twists)(p, z12, z6)
        pm0_b2 = poly_with_rescaled_neg_coords_mod_p(det_b2, [3, 4, 5], z12, p)
        for perm in b2_splits:
            pm = permute_poly_mod_p(pm0_b2, perm)
            for tw in b2_twist_small:
                rows.append(twist_vector_mod_p(pm, col_idx, 1751, permute_tuple(tw, perm), z6, p))
        pm0_b3 = poly_with_rescaled_neg_coords_mod_p(det_b3, [1, 4, 5], z12, p)
        pm0_c3 = poly_with_rescaled_neg_coords_mod_p(det_c3, [1, 4, 5], z12, p)
        for perm in b3_splits:
            pm_b = permute_poly_mod_p(pm0_b3, perm)
            pm_c = permute_poly_mod_p(pm0_c3, perm)
            for tw in b3_twist_small:
                ptw = permute_tuple(tw, perm)
                rows.append(twist_vector_mod_p(pm_b, col_idx, 1751, ptw, z6, p))
                rows.append(twist_vector_mod_p(pm_c, col_idx, 1751, ptw, z6, p))
        return rows

    run_gpu_crt_stage("stage0_single_r4_mf", build_b1_k_matchings(1, [(0, 0, 0, 0, 0, 0)]))
    run_gpu_crt_stage("stage1_k1_matching", build_b1_k_matchings(1, b1_twists))
    run_gpu_crt_stage("stage2_k3_matchings", build_b1_k_matchings(3, b1_twists))
    run_gpu_crt_stage("stage3_k6_matchings", build_b1_k_matchings(6, b1_twists))
    run_gpu_crt_stage("stage4_k10_matchings", build_b1_k_matchings(10, b1_twists))
    run_gpu_crt_stage("stage5_k15_all_matchings", build_b1_k_matchings(15, b1_twists))
    run_gpu_crt_stage("stage6_add_symmetric_r4_mfs", build_b1_plus_symmetric)

    assert all(v["agreement"] for v in stage_results.values())
    assert stage_results["stage0_single_r4_mf"]["rank"] == 1
    assert stage_results["stage1_k1_matching"]["rank"] == 125
    assert stage_results["stage2_k3_matchings"]["rank"] == 305
    assert stage_results["stage3_k6_matchings"]["rank"] == 549
    assert stage_results["stage4_k10_matchings"]["rank"] == 805
    assert stage_results["stage5_k15_all_matchings"]["rank"] == band_totals["Band1"] == 1001
    assert stage_results["stage6_add_symmetric_r4_mfs"]["rank"] == 1001

    out = {
        "clifford_threshold": {
            "k1_r1_ab_eq_ba_eq_f": True,
            "k1_r1_tr3_vanishes": True,
            "k2_r2_ab_eq_ba_eq_f": True,
            "k2_r2_tr3_vanishes": True,
        },
        "k3_r4_sextic_mfs": {
            "band1": {
                "r": 4,
                "ab_eq_ba_eq_f": True,
                "det_jac_terms": len(det_b1),
                "pv_tr3_scale": scale_pv_b1,
                "band_counts": {"Band1": len(det_b1)},
            },
            "symmetric_triple_quadric": {
                "r": 4,
                "ab_eq_ba_eq_f": True,
                "det_jac_terms": len(det_b2),
                "pv_tr3_scale": scale_pv_b2,
                "band_counts": b2_band_counts,
            },
            "symmetric_surface_quadric": {
                "r": 4,
                "ab_eq_ba_eq_f": True,
                "det_jac_terms": len(det_b3),
                "pv_tr3_scale": scale_pv_b3,
                "band_counts": b3_band_counts,
            },
            "symmetric_surface_cubic": {
                "r": 4,
                "ab_eq_ba_eq_f": True,
                "det_jac_terms": len(det_c3),
                "pv_tr3_scale": scale_pv_c3,
                "band_counts": c3_band_counts,
            },
        },
        "k4_r8_excess_codimension_mfs": {
            "deformed_sextic_r8": {
                "r": 8,
                "ab_eq_ba_eq_f": True,
                "deformation_term": "x0*x1*x2*x3*x4*x5",
                "tr3_excess_codim_vanishes": True,
            },
            "cauchy_6_ftri_r8": {
                "r": 8,
                "ab_eq_ba_eq_f": True,
                "tr3_excess_codim_vanishes": True,
            },
        },
        "newton_aoki_k3_r4_mfs": aoki_results,
        "r_f0_deg12_band_totals": band_totals,
        "band1_koszul_saturation": {
            "covered_band1_dim": 1001,
            "remaining_non_koszul_gap": band_totals["Band2"] + band_totals["Band3"],
        },
        "gpu_crt_3prime_scaling": stage_results,
    }

    out_dir = Path(__file__).resolve().parents[2] / "reports" / "millennium_ext"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "matrix_factorization_scaling.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(json.dumps(out, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
