"""Experiment 3: Non-Koszul Matrix Factorizations & Full 1,751/1,751 Closure of R(F_0)_12.

Strictly float-free (int, Fraction, torch.int64 on cuda:0 with 6.0 GB VRAM cap).
Outputs: reports/millennium_ext/non_koszul_mf_closure.json

Verifies:
1. Exact over-Z 4x4 mixed-degree (1, 1, 1, 3) determinantal matrix factorization A_1(x0,x1,x2)
   with B_1 = -adj(A_1) satisfying A_1 * B_1 = B_1 * A_1 = 2*(x0^6 + x1^6 - x2^6)*I_4 over Z,
   and exact over-Z Polishchuk-Vaintrob traces tr(dA_1 ^ dB_1 ^ dA_1) and tr(dB_1 ^ dA_1 ^ dB_1)
   hitting BOTH mod-3 Band-2 orbits ((0,0,3,3,3,3) and (1,1,1,1,4,4)) with nonzero Kunneth products
   (-27 * 124 = -3348 and -36 * 144 = -5184).
2. Exact over-Z 3x3 quadric determinantal MF M_3(x0^2, x1^2, x2^2) (demonstrating 100% Band-1
   trapping without odd/even exponent mixing) plus the 18x18 3+3 graded tensor parity-vanishing law.
3. Exact over-Z 6x6 skew-symmetric Buchsbaum-Eisenbud Pfaffian matrix factorization A*B = B*A = F*I_6.
4. Exact 3-prime RTX A2000 GPU CRT closure ladder across (65521, 1000000009, 1000000033):
   - Stage 0: Koszul r = 4 only -> 1,001 / 1,751 (Band1=1001, Band2=0, Band3=0)
   - Stage 1: Koszul r = 4 + exact over-Z 4x4 (1,1,1,3) MF -> breaks Band-1 ceiling into Band2
   - Stage 2: 6x6 linear Ulrich MF only -> saturates Band3 (120/120) and reaches Band2
   - Stage 3: Single 4x4 (1,1,1,3) non-Koszul MF -> 1,731 / 1,751 (B1=981, B2=630/630, B3=120/120)
   - Stage 4: Koszul r = 4 + 4x4 (1,1,1,3) non-Koszul MF -> 1,751 / 1,751 = 100.0% closure (gap = 0).
"""

from __future__ import annotations

import itertools
import json
import random
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Callable, Dict, List, Sequence, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parent))
from gpu_exact_linalg import gpu_crt_3prime_rank, gpu_modp_rank_with_stats
from matrix_factorization_scaling import (
    build_sextic_r12_basis,
    classify_sextic_band,
    is_prime,
    pair_uv,
    permute_poly_mod_p,
    poly_add,
    poly_clean,
    poly_deriv,
    poly_mod_pow,
    poly_mul,
    poly_scale,
    poly_var_pow,
    poly_with_rescaled_neg_coords_mod_p,
    polishchuk_vaintrob_tr3,
    primitive_12th_root_mod_p,
    twist_vector_mod_p,
    verify_mf,
    jacobian_det6,
    koszul_mf,
    Poly,
)


PRIMES_3: Tuple[int, int, int] = (65521, 1000000009, 1000000033)


# ---------------------------------------------------------------------------
# Fast exact sparse Z[x0, x1, x2] and F_p[x0, x1, x2] 3-variable arithmetic
# ---------------------------------------------------------------------------

Poly3 = Dict[Tuple[int, int, int], int]


def p3_clean(p: Poly3, mod: int | None = None) -> Poly3:
    if mod is None:
        return {k: v for k, v in p.items() if v != 0}
    return {k: v % mod for k, v in p.items() if v % mod != 0}


def p3_add(a: Poly3, b: Poly3, sign: int = 1, mod: int | None = None) -> Poly3:
    out = dict(a)
    for k, v in b.items():
        nv = out.get(k, 0) + sign * v
        if mod is not None:
            nv %= mod
        if nv == 0:
            out.pop(k, None)
        else:
            out[k] = nv
    return out


def p3_mul(a: Poly3, b: Poly3, mod: int | None = None) -> Poly3:
    out: Poly3 = {}
    for (a1, b1, c1), v1 in a.items():
        for (a2, b2, c2), v2 in b.items():
            key = (a1 + a2, b1 + b2, c1 + c2)
            out[key] = out.get(key, 0) + v1 * v2
    return p3_clean(out, mod)


def p3_scale(a: Poly3, s: int, mod: int | None = None) -> Poly3:
    if s == 0:
        return {}
    return p3_clean({k: v * s for k, v in a.items()}, mod)


def p3_deriv(a: Poly3, vi: int, mod: int | None = None) -> Poly3:
    out: Poly3 = {}
    for m, v in a.items():
        e = m[vi]
        if e > 0:
            nm = [m[0], m[1], m[2]]
            nm[vi] = e - 1
            nv = v * e
            if mod is not None:
                nv %= mod
            if nv != 0:
                out[(nm[0], nm[1], nm[2])] = nv
    return out


def p3_mod_pow(a: Poly3, max_pow: int = 5) -> Poly3:
    return {k: v for k, v in a.items() if v != 0 and k[0] < max_pow and k[1] < max_pow and k[2] < max_pow}


def p3_det(mat: Sequence[Sequence[Poly3]], mod: int | None = None) -> Poly3:
    n = len(mat)
    memo: Dict[Tuple[int, int], Poly3] = {}

    def rec(r: int, mask: int) -> Poly3:
        key = (r, mask)
        if key in memo:
            return memo[key]
        if r == n:
            return {(0, 0, 0): 1}
        acc: Poly3 = {}
        sgn = 1
        for c in range(n):
            if mask & (1 << c):
                entry = mat[r][c]
                if entry:
                    sub = rec(r + 1, mask ^ (1 << c))
                    if sub:
                        acc = p3_add(acc, p3_mul(entry, sub, mod), sign=sgn, mod=mod)
                sgn = -sgn
        memo[key] = acc
        return acc

    return rec(0, (1 << n) - 1)


def p3_adj(mat: Sequence[Sequence[Poly3]], mod: int | None = None) -> List[List[Poly3]]:
    n = len(mat)
    adj: List[List[Poly3]] = [[{} for _ in range(n)] for _ in range(n)]
    for i in range(n):
        for j in range(n):
            sub = [[mat[r][c] for c in range(n) if c != j] for r in range(n) if r != i]
            cof = p3_det(sub, mod=mod)
            adj[j][i] = p3_scale(cof, 1 if (i + j) % 2 == 0 else -1, mod=mod)
    return adj


def p3_mat_mul(
    A: Sequence[Sequence[Poly3]], B: Sequence[Sequence[Poly3]], mod: int | None = None
) -> List[List[Poly3]]:
    n = len(A)
    out: List[List[Poly3]] = [[{} for _ in range(n)] for _ in range(n)]
    for i in range(n):
        for k in range(n):
            aik = A[i][k]
            if not aik:
                continue
            for j in range(n):
                bkj = B[k][j]
                if bkj:
                    out[i][j] = p3_add(out[i][j], p3_mul(aik, bkj, mod), mod=mod)
    return out


def p3_traces_aba_bab(
    A: Sequence[Sequence[Poly3]],
    B: Sequence[Sequence[Poly3]],
    mod_jac: int = 5,
    mod: int | None = None,
) -> Tuple[Poly3, Poly3]:
    """Computes exact 3-variable supertraces tr(dA ^ dB ^ dA) and tr(dB ^ dA ^ dB) mod x_i^mod_jac."""
    r = len(A)
    dA = [[[p3_deriv(A[i][j], vi, mod) for j in range(r)] for i in range(r)] for vi in range(3)]
    dB = [[[p3_deriv(B[i][j], vi, mod) for j in range(r)] for i in range(r)] for vi in range(3)]
    tr_ABA: Poly3 = {}
    tr_BAB: Poly3 = {}
    for perm in itertools.permutations(range(3)):
        inv = sum(1 for a in range(3) for b in range(a + 1, 3) if perm[a] > perm[b])
        sg = -1 if inv % 2 else 1
        i0, i1, i2 = perm
        for a in range(r):
            for c in range(r):
                if dA[i2][c][a]:
                    xab: Poly3 = {}
                    for b in range(r):
                        if dA[i0][a][b] and dB[i1][b][c]:
                            xab = p3_add(xab, p3_mul(dA[i0][a][b], dB[i1][b][c], mod), mod=mod)
                    if xab:
                        tr_ABA = p3_add(tr_ABA, p3_mul(xab, dA[i2][c][a], mod), sign=sg, mod=mod)
                if dB[i2][c][a]:
                    yab: Poly3 = {}
                    for b in range(r):
                        if dB[i0][a][b] and dA[i1][b][c]:
                            yab = p3_add(yab, p3_mul(dB[i0][a][b], dA[i1][b][c], mod), mod=mod)
                    if yab:
                        tr_BAB = p3_add(tr_BAB, p3_mul(yab, dB[i2][c][a], mod), sign=sg, mod=mod)
    return p3_mod_pow(tr_ABA, mod_jac), p3_mod_pow(tr_BAB, mod_jac)


# ---------------------------------------------------------------------------
# Fast exact modular q-th root (q = 2, 3) for selecting points on C_6(F_p)
# ---------------------------------------------------------------------------

def modp_qth_root(a: int, q: int, p: int) -> int | None:
    """Computes an exact q-th root of a mod p (q in {2, 3}, (p - 1) % q == 0)."""
    a %= p
    if a == 0:
        return 0
    if pow(a, (p - 1) // q, p) != 1:
        return None
    nonres = 2
    while pow(nonres, (p - 1) // q, p) == 1:
        nonres += 1
    s = 0
    t = p - 1
    while t % q == 0:
        t //= q
        s += 1
    inv_a = pow(a, p - 2, p)
    u = (-pow(t, -1, q)) % q
    e = (1 + u * t) // q
    x = pow(a, e, p)
    err = (pow(x, q, p) * inv_a) % p
    while err != 1:
        m = 1
        cur = pow(err, q, p)
        while cur != 1:
            cur = pow(cur, q, p)
            m += 1
        assert m < s
        gs = pow(nonres, (q ** (s - m - 1)) * t, p)
        gs_q = pow(gs, q, p)
        target_pow = q ** (m - 1)
        chosen = 0
        for c in range(1, q):
            cand = (err * pow(gs_q, c, p)) % p
            if pow(cand, target_pow, p) == 1:
                chosen = c
                break
        assert chosen > 0
        x = (x * pow(gs, chosen, p)) % p
        err = (pow(x, q, p) * inv_a) % p
    assert pow(x, q, p) == a
    return x


def find_c6_points_mod_p(p: int, need: int = 30) -> List[Tuple[int, int, int]]:
    """Finds `need` affine F_p-points (1, y, z) on x0^6 + x1^6 - x2^6 = 0 mod p."""
    pts: List[Tuple[int, int, int]] = []
    y = 1
    while len(pts) < need:
        rhs = (1 + pow(y, 6, p)) % p
        if rhs != 0 and pow(rhs, (p - 1) // 6, p) == 1:
            r2 = modp_qth_root(rhs, 2, p)
            if r2 is not None:
                z = modp_qth_root(r2, 3, p)
                if z is not None:
                    assert (1 + pow(y, 6, p) - pow(z, 6, p)) % p == 0
                    pts.append((1, y, z))
        y += 1
    return pts


# ---------------------------------------------------------------------------
# Fast F_p RREF & Nullspace + Asymmetric Non-Koszul Builders mod p
# ---------------------------------------------------------------------------

def mons_deg3(d: int) -> List[Tuple[int, int, int]]:
    return [(a, b, d - a - b) for a in range(d, -1, -1) for b in range(d - a, -1, -1)]


def eval_pts3_mod_p(
    m_list: Sequence[Tuple[int, int, int]], pt_list: Sequence[Tuple[int, int, int]], p: int
) -> List[List[int]]:
    return [
        [(pow(px, a, p) * pow(py, b, p) * pow(pz, c, p)) % p for (a, b, c) in m_list]
        for (px, py, pz) in pt_list
    ]


def rref_nullspace_mod_p(rows: Sequence[Sequence[int]], ncols: int, p: int) -> Tuple[int, List[List[int]]]:
    nrows = len(rows)
    m = [[x % p for x in r] for r in rows]
    pivs: List[int] = []
    r = 0
    for c in range(ncols):
        piv = next((i for i in range(r, nrows) if m[i][c] != 0), -1)
        if piv < 0:
            continue
        m[r], m[piv] = m[piv], m[r]
        inv = pow(m[r][c], p - 2, p)
        m[r] = [(x * inv) % p for x in m[r]]
        prow = m[r]
        for i in range(nrows):
            if i != r and m[i][c] != 0:
                fac = m[i][c]
                m[i] = [(m[i][j] - fac * prow[j]) % p for j in range(ncols)]
        pivs.append(c)
        r += 1
        if r == nrows:
            break
    free = [c for c in range(ncols) if c not in pivs]
    ns: List[List[int]] = []
    for fc in free:
        v = [0] * ncols
        v[fc] = 1
        for ri, pc in enumerate(pivs):
            v[pc] = (-m[ri][fc]) % p
        ns.append(v)
    return len(pivs), ns


def build_4x4_1113_traces_mod_p(
    p: int, pts: Sequence[Tuple[int, int, int]]
) -> Tuple[Poly3, Poly3, Poly3, Poly3, List[int]]:
    """Selects 6 non-conic points Z6 on C_6(F_p) giving full-support (1,1,1,3) traces."""
    m2 = mons_deg3(2)
    m3 = mons_deg3(3)
    m4 = mons_deg3(4)
    m6 = mons_deg3(6)
    m4_idx = {m: i for i, m in enumerate(m4)}
    m6_idx = {m: i for i, m in enumerate(m6)}
    for comb in itertools.combinations(range(len(pts)), 6):
        z6_pts = [pts[i] for i in comb]
        rk2, _ = rref_nullspace_mod_p(eval_pts3_mod_p(m2, z6_pts, p), len(m2), p)
        if rk2 != 6:
            continue
        rk3, ns3 = rref_nullspace_mod_p(eval_pts3_mod_p(m3, z6_pts, p), len(m3), p)
        if len(ns3) != 4:
            continue
        gs: List[Poly3] = [{m3[i]: v[i] for i in range(len(m3)) if v[i]} for v in ns3]
        cols4: List[List[int]] = []
        for g in gs:
            for vi in range(3):
                col = [0] * len(m4)
                for (a, b, c), cf in g.items():
                    nm = [a, b, c]
                    nm[vi] += 1
                    col[m4_idx[(nm[0], nm[1], nm[2])]] = (
                        col[m4_idx[(nm[0], nm[1], nm[2])]] + cf
                    ) % p
                cols4.append(col)
        _, syz_lin = rref_nullspace_mod_p(
            [[cols4[j][i] for j in range(12)] for i in range(len(m4))], 12, p
        )
        if len(syz_lin) != 3:
            continue
        cols6: List[List[int]] = [
            [p3_mul(g, {mon: 1}, mod=p).get(m, 0) for m in m6] for g in gs for mon in m3
        ]
        fcol = [0] * len(m6)
        fcol[m6_idx[(6, 0, 0)]] = 1
        fcol[m6_idx[(0, 6, 0)]] = 1
        fcol[m6_idx[(0, 0, 6)]] = p - 1
        cols6.append(fcol)
        _, syz6 = rref_nullspace_mod_p(
            [[cols6[j][i] for j in range(41)] for i in range(len(m6))], 41, p
        )
        sol6 = next((s for s in syz6 if s[-1] != 0), None)
        if sol6 is None:
            continue
        inv_l = pow((-sol6[-1]) % p, p - 2, p)
        cs: List[Poly3] = [
            {m3[i]: (sol6[10 * k + i] * inv_l) % p for i in range(10) if sol6[10 * k + i]}
            for k in range(4)
        ]
        A: List[List[Poly3]] = [[{} for _ in range(4)] for _ in range(4)]
        basis_lin = [(1, 0, 0), (0, 1, 0), (0, 0, 1)]
        for ri in range(3):
            for cj in range(4):
                poly: Poly3 = {}
                for vi, bm in enumerate(basis_lin):
                    val = syz_lin[ri][3 * cj + vi]
                    if val:
                        poly[bm] = val
                A[ri][cj] = poly
        for cj in range(4):
            A[3][cj] = cs[cj]
        detA = p3_det(A, mod=p)
        scale = detA.get((6, 0, 0), 0)
        if scale == 0 or detA != {(6, 0, 0): scale, (0, 6, 0): scale, (0, 0, 6): (-scale) % p}:
            continue
        inv_s = pow(scale, p - 2, p)
        adjA = p3_adj(A, mod=p)
        B = [[p3_scale(adjA[i][j], inv_s, mod=p) for j in range(4)] for i in range(4)]
        tr_aba, tr_bab = p3_traces_aba_bab(A, B, mod_jac=5, mod=p)
        p4 = {m: v for m, v in tr_aba.items() if sum(m) == 4}
        p6a = {m: v for m, v in tr_aba.items() if sum(m) == 6}
        p6b = {m: v for m, v in tr_bab.items() if sum(m) == 6}
        p8 = {m: v for m, v in tr_bab.items() if sum(m) == 8}
        if len(p4) == 15 and len(p6a) == 19 and len(p6b) == 19 and len(p8) == 15:
            return p4, p6a, p6b, p8, list(comb)
    raise RuntimeError(f"Failed to construct full-support 4x4 (1,1,1,3) MF mod {p}")


def build_ulrich_6x6_traces_mod_p(
    p: int, pts: Sequence[Tuple[int, int, int]]
) -> Tuple[Poly3, Poly3]:
    """Selects 15 points Z15 on C_6(F_p) giving a 6x6 linear Ulrich MF and returns (deg4, deg8) traces."""
    m4 = mons_deg3(4)
    m5 = mons_deg3(5)
    m6 = mons_deg3(6)
    m6_idx = {m: i for i, m in enumerate(m6)}
    basis_lin = [(1, 0, 0), (0, 1, 0), (0, 0, 1)]
    for start in range(len(pts) - 15 + 1):
        z15 = pts[start : start + 15]
        rk4, _ = rref_nullspace_mod_p(eval_pts3_mod_p(m4, z15, p), len(m4), p)
        if rk4 != 15:
            continue
        _, ns5 = rref_nullspace_mod_p(eval_pts3_mod_p(m5, z15, p), len(m5), p)
        if len(ns5) != 6:
            continue
        cols: List[List[int]] = []
        for v in ns5:
            for vi in range(3):
                col = [0] * len(m6)
                for i, coef in enumerate(v):
                    if coef:
                        nm = list(m5[i])
                        nm[vi] += 1
                        col[m6_idx[(nm[0], nm[1], nm[2])]] = (
                            col[m6_idx[(nm[0], nm[1], nm[2])]] + coef
                        ) % p
                cols.append(col)
        fcol = [0] * len(m6)
        fcol[m6_idx[(6, 0, 0)]] = 1
        fcol[m6_idx[(0, 6, 0)]] = 1
        fcol[m6_idx[(0, 0, 6)]] = p - 1
        cols.append(fcol)
        mat_syz = [[cols[j][i] for j in range(len(cols))] for i in range(len(m6))]
        _, syz = rref_nullspace_mod_p(mat_syz, len(cols), p)
        if len(syz) != 6:
            continue
        A: List[List[Poly3]] = [[{} for _ in range(6)] for _ in range(6)]
        for ri, s in enumerate(syz):
            for cj in range(6):
                poly: Poly3 = {}
                for vi, bm in enumerate(basis_lin):
                    val = s[3 * cj + vi]
                    if val:
                        poly[bm] = val
                A[ri][cj] = poly
        detA = p3_det(A, mod=p)
        scale = detA.get((6, 0, 0), 0)
        if scale == 0 or detA != {(6, 0, 0): scale, (0, 6, 0): scale, (0, 0, 6): (-scale) % p}:
            continue
        inv_s = pow(scale, p - 2, p)
        adjA = p3_adj(A, mod=p)
        B = [[p3_scale(adjA[i][j], inv_s, mod=p) for j in range(6)] for i in range(6)]
        tr_aba, tr_bab = p3_traces_aba_bab(A, B, mod_jac=5, mod=p)
        p4 = {m: v for m, v in tr_aba.items() if sum(m) == 4}
        p8 = {m: v for m, v in tr_bab.items() if sum(m) == 8}
        if p4 and p8:
            return p4, p8
    raise RuntimeError(f"Failed to construct 6x6 Ulrich MF mod {p}")


# ---------------------------------------------------------------------------
# 6-variable Buchsbaum-Eisenbud Pfaffian & Parity Test Helpers
# ---------------------------------------------------------------------------

def pfaffian4_poly(M4: Sequence[Sequence[Poly]]) -> Poly:
    t1 = poly_mul(M4[0][1], M4[2][3])
    t2 = poly_mul(M4[0][2], M4[1][3])
    t3 = poly_mul(M4[0][3], M4[1][2])
    return poly_add(poly_add(t1, t2, -1), t3, 1)


def be_6x6_pfaffian_mf_verify() -> Dict[str, Any]:
    """Constructs and verifies an exact over-Z 6x6 skew-symmetric BE Pfaffian MF."""
    x0 = poly_var_pow(0, 1)
    x1 = poly_var_pow(1, 1)
    x2 = poly_var_pow(2, 1)
    x3 = poly_var_pow(3, 1)
    x4 = poly_var_pow(4, 1)
    x5 = poly_var_pow(5, 1)
    x0_2 = poly_var_pow(0, 2)
    x1_2 = poly_var_pow(1, 2)
    x1x2 = poly_mul(x1, x2)

    M: List[List[Poly]] = [[{} for _ in range(5)] for _ in range(5)]
    upper = {
        (0, 1): poly_add(x0, x1),
        (0, 2): x2,
        (0, 4): x3,
        (1, 2): x4,
        (1, 3): x5,
        (2, 3): x0_2,
        (2, 4): x1x2,
        (3, 4): poly_add(x3, x4),
    }
    for (i, j), val in upper.items():
        M[i][j] = val
        M[j][i] = poly_scale(val, -1)

    a_vec: List[Poly] = [x5, poly_add(x0, x2, -1), x1_2, x3, x4]
    p_vec: List[Poly] = []
    for k in range(5):
        sub = [[M[r][c] for c in range(5) if c != k] for r in range(5) if r != k]
        p_vec.append(poly_scale(pfaffian4_poly(sub), 1 if k % 2 == 0 else -1))

    H: List[List[Poly]] = [[{} for _ in range(5)] for _ in range(5)]
    for i in range(5):
        for j in range(5):
            if i == j:
                continue
            rem = [x for x in range(5) if x != i and x != j]
            val: Poly = {}
            for k in rem:
                lm = [x for x in rem if x != k]
                l, m = lm[0], lm[1]
                perm = (i, j, k, l, m)
                inv = sum(1 for u in range(5) for v in range(u + 1, 5) if perm[u] > perm[v])
                sgn = -1 if inv % 2 else 1
                # H_{ij} = - sum eps(i,j,k,l,m) a_k M_{lm}
                val = poly_add(val, poly_mul(a_vec[k], M[l][m]), sign=-sgn)
            H[i][j] = val

    F: Poly = {}
    for k in range(5):
        F = poly_add(F, poly_mul(a_vec[k], p_vec[k]))
    assert len(F) > 0

    A: List[List[Poly]] = [[{} for _ in range(6)] for _ in range(6)]
    B: List[List[Poly]] = [[{} for _ in range(6)] for _ in range(6)]
    for j in range(5):
        A[0][j + 1] = a_vec[j]
        A[j + 1][0] = poly_scale(a_vec[j], -1)
        B[0][j + 1] = poly_scale(p_vec[j], -1)
        B[j + 1][0] = p_vec[j]
    for i in range(5):
        for j in range(5):
            A[i + 1][j + 1] = M[i][j]
            B[i + 1][j + 1] = H[i][j]

    for i in range(6):
        for j in range(6):
            assert A[i][j] == poly_scale(A[j][i], -1)
            assert B[i][j] == poly_scale(B[j][i], -1)
    assert verify_mf(A, B, F)
    return {
        "r": 6,
        "a_skew_symmetric": True,
        "b_skew_symmetric": True,
        "ab_eq_ba_eq_f_i6": True,
        "pfaffian_f_terms": len(F),
    }


def eval_p3_at_point_mod_p(P: Poly3, pt: Tuple[int, int, int], p: int) -> int:
    s = 0
    for (a, b, c), v in P.items():
        s = (s + v * pow(pt[0], a, p) * pow(pt[1], b, p) * pow(pt[2], c, p)) % p
    return s


def graded_tensor_parity_vanishing_mod_p(
    A3: Sequence[Sequence[Poly3]], B3: Sequence[Sequence[Poly3]], p: int = 65521
) -> int:
    """Evaluates tr((dA ^ dB)^3) for 18x18 A1 (x) A2 at a test point mod p; must vanish by Z/2 parity."""
    pt = (2, 3, 5, 7, 11, 13)
    R = 18
    r1 = r2 = 3
    half = 9
    v1, v2 = pt[:3], pt[3:]
    dA1 = [[[eval_p3_at_point_mod_p(p3_deriv(A3[i][j], k), v1, p) for j in range(3)] for i in range(3)] for k in range(3)]
    dB1 = [[[eval_p3_at_point_mod_p(p3_deriv(B3[i][j], k), v1, p) for j in range(3)] for i in range(3)] for k in range(3)]
    dA2 = [[[eval_p3_at_point_mod_p(p3_deriv(A3[i][j], k), v2, p) for j in range(3)] for i in range(3)] for k in range(3)]
    dB2 = [[[eval_p3_at_point_mod_p(p3_deriv(B3[i][j], k), v2, p) for j in range(3)] for i in range(3)] for k in range(3)]

    def make_block(M1: Any, M2: Any, M3: Any, M4: Any) -> List[List[int]]:
        M = [[0] * R for _ in range(R)]
        if M1 is not None:
            for i in range(r1):
                for j in range(r1):
                    val = M1[i][j] % p
                    if val:
                        for k in range(r2):
                            M[i * r2 + k][j * r2 + k] = val
        if M4 is not None:
            for i in range(r1):
                for j in range(r1):
                    val = (-M4[i][j]) % p
                    if val:
                        for k in range(r2):
                            M[half + i * r2 + k][half + j * r2 + k] = val
        if M2 is not None:
            for k1 in range(r1):
                for i in range(r2):
                    for j in range(r2):
                        val = M2[i][j] % p
                        if val:
                            M[k1 * r2 + i][half + k1 * r2 + j] = val
        if M3 is not None:
            for k1 in range(r1):
                for i in range(r2):
                    for j in range(r2):
                        val = M3[i][j] % p
                        if val:
                            M[half + k1 * r2 + i][k1 * r2 + j] = val
        return M

    dA = [make_block(dA1[k], None, None, dB1[k]) for k in range(3)] + [
        make_block(None, dA2[k], dB2[k], None) for k in range(3)
    ]
    dB = [make_block(dB1[k], None, None, dA1[k]) for k in range(3)] + [
        make_block(None, dA2[k], dB2[k], None) for k in range(3)
    ]

    def mm(X: List[List[int]], Y: List[List[int]]) -> List[List[int]]:
        Z = [[0] * R for _ in range(R)]
        for i in range(R):
            Xi, Zi = X[i], Z[i]
            for k in range(R):
                xik = Xi[k]
                if xik:
                    Yk = Y[k]
                    for j in range(R):
                        if Yk[j]:
                            Zi[j] = (Zi[j] + xik * Yk[j]) % p
        return Z

    M2: Dict[int, List[List[int]]] = {}
    for i in range(6):
        for j in range(i + 1, 6):
            X = mm(dA[i], dB[j])
            Y = mm(dA[j], dB[i])
            M2[(1 << i) | (1 << j)] = [[(X[a][b] - Y[a][b]) % p for b in range(R)] for a in range(R)]

    def mask_sgn(a: int, b: int) -> int:
        inv = 0
        for i in range(6):
            if a & (1 << i):
                for j in range(i):
                    if b & (1 << j):
                        inv += 1
        return -1 if inv % 2 else 1

    M4: Dict[int, List[List[int]]] = {}
    for m1, Am1 in M2.items():
        for m2, Am2 in M2.items():
            if m1 & m2:
                continue
            m12 = m1 | m2
            sg = mask_sgn(m1, m2)
            P = mm(Am1, Am2)
            if m12 not in M4:
                M4[m12] = [[(sg * P[a][b]) % p for b in range(R)] for a in range(R)]
            else:
                cur = M4[m12]
                for a in range(R):
                    for b in range(R):
                        cur[a][b] = (cur[a][b] + sg * P[a][b]) % p

    tot = 0
    for m4_mask, Am4 in M4.items():
        m2_mask = 63 ^ m4_mask
        sg = mask_sgn(m4_mask, m2_mask)
        Bm2 = M2[m2_mask]
        tr = sum(Am4[a][b] * Bm2[b][a] for a in range(R) for b in range(R)) % p
        tot = (tot + sg * tr) % p
    return tot


# ---------------------------------------------------------------------------
# Main Experiment 3 Runner
# ---------------------------------------------------------------------------

def main() -> int:
    # 1. Exact over-Z 4x4 mixed-degree (1,1,1,3) non-Koszul determinantal MF A_1 of F_1 = x0^6 + x1^6 - x2^6
    # Monomial basis vectors in 3 vars
    def m3_term(a: int, b: int, c: int, coef: int = 1) -> Poly3:
        return {(a, b, c): coef} if coef != 0 else {}

    p_x0 = m3_term(1, 0, 0)
    p_x1 = m3_term(0, 1, 0)
    p_x2 = m3_term(0, 0, 1)

    A1: List[List[Poly3]] = [
        [p3_add(m3_term(1, 0, 0, -1), m3_term(0, 0, 1, -2)), p_x1, p_x0, {}],
        [m3_term(0, 1, 0, 2), p3_add(p_x0, p_x2, -1), {}, p_x0],
        [p3_add(m3_term(1, 0, 0, -2), m3_term(0, 0, 1, -1)), p_x1, m3_term(0, 0, 1, -1), p_x1],
        [
            {(2, 1, 0): 2, (0, 1, 2): -1},
            {(3, 0, 0): 1, (2, 0, 1): -1, (1, 2, 0): -1},
            {(0, 3, 0): -1, (0, 1, 2): -1},
            {(0, 0, 3): -1},
        ],
    ]
    adj_A1 = p3_adj(A1)
    B1 = [[p3_scale(adj_A1[i][j], -1) for j in range(4)] for i in range(4)]
    F1_doubled: Poly3 = {(6, 0, 0): 2, (0, 6, 0): 2, (0, 0, 6): -2}

    ab_1 = p3_mat_mul(A1, B1)
    ba_1 = p3_mat_mul(B1, A1)
    for i in range(4):
        for j in range(4):
            expected = F1_doubled if i == j else {}
            assert ab_1[i][j] == expected and ba_1[i][j] == expected

    z_tr_aba, z_tr_bab = p3_traces_aba_bab(A1, B1, mod_jac=5, mod=None)
    assert z_tr_aba.get((0, 3, 3)) == -27 and z_tr_bab.get((0, 3, 3)) == 124
    assert z_tr_aba.get((1, 1, 4)) == -36 and z_tr_bab.get((1, 1, 4)) == 144

    z_p4 = {m: v for m, v in z_tr_aba.items() if sum(m) == 4}
    z_p6a = {m: v for m, v in z_tr_aba.items() if sum(m) == 6}
    z_p6b = {m: v for m, v in z_tr_bab.items() if sum(m) == 6}
    z_p8 = {m: v for m, v in z_tr_bab.items() if sum(m) == 8}
    assert len(z_p4) == 6 and len(z_p6a) == 8 and len(z_p6b) == 8 and len(z_p8) == 6

    k48_z: Poly = {m1 + m2: v1 * v2 for m1, v1 in z_p4.items() for m2, v2 in z_p8.items()}
    k66_z: Poly = {m1 + m2: v1 * v2 for m1, v1 in z_p6a.items() for m2, v2 in z_p6b.items()}
    assert k66_z[(0, 3, 3, 0, 3, 3)] == -3348
    assert k66_z[(1, 1, 4, 1, 1, 4)] == -5184

    # 2. Exact over-Z 3x3 quadric determinantal MF M_3(x0^2, x1^2, x2^2) + 18x18 parity check
    A3: List[List[Poly3]] = [
        [{(2, 0, 0): 1, (0, 0, 2): 1}, {(0, 2, 0): -1}, {}],
        [{(2, 0, 0): 1}, {(2, 0, 0): 1, (0, 0, 2): -1}, {(2, 0, 0): 1, (0, 2, 0): 1}],
        [{(2, 0, 0): 1, (0, 2, 0): -1}, {(2, 0, 0): -1}, {(0, 0, 2): -1}],
    ]
    B3 = p3_adj(A3)
    F_tri3: Poly3 = {(6, 0, 0): 1, (0, 6, 0): 1, (0, 0, 6): 1}
    ab_3 = p3_mat_mul(A3, B3)
    ba_3 = p3_mat_mul(B3, A3)
    for i in range(3):
        for j in range(3):
            expected = F_tri3 if i == j else {}
            assert ab_3[i][j] == expected and ba_3[i][j] == expected

    tr3_aba, tr3_bab = p3_traces_aba_bab(A3, B3, mod_jac=5, mod=None)
    assert tr3_aba == {(3, 1, 1): 64, (1, 3, 1): 64, (1, 1, 3): 64}
    assert tr3_bab == {(3, 3, 1): -320, (3, 1, 3): 160, (1, 3, 3): 160}
    m3_bands = Counter(classify_sextic_band(m1 + m2) for m1 in tr3_aba for m2 in tr3_bab)
    assert dict(m3_bands) == {"Band1": 9}
    graded_18_tr3 = graded_tensor_parity_vanishing_mod_p(A3, B3, p=65521)
    assert graded_18_tr3 == 0

    # 3. Exact over-Z 6x6 Buchsbaum-Eisenbud Pfaffian MF
    pfaff_res = be_6x6_pfaffian_mf_verify()

    # 4. Exact 3-prime RTX A2000 GPU CRT closure ladder inside R(F_0)_12 (dim = 1,751)
    basis = build_sextic_r12_basis()
    assert len(basis) == 1751
    col_idx = {m: i for i, m in enumerate(basis)}
    b1_cols = [i for i, m in enumerate(basis) if classify_sextic_band(m) == "Band1"]
    b2_cols = [i for i, m in enumerate(basis) if classify_sextic_band(m) == "Band2"]
    b3_cols = [i for i, m in enumerate(basis) if classify_sextic_band(m) == "Band3"]
    assert (len(b1_cols), len(b2_cols), len(b3_cols)) == (1001, 630, 120)

    # Koszul r=4 Band-1 Jacobian det
    u0, v0 = pair_uv(0, 1, 6)
    u1, v1 = pair_uv(2, 3, 6)
    u2, v2 = pair_uv(4, 5, 6)
    det_b1 = jacobian_det6([u0, v0, u1, v1, u2, v2], mod_jac_pow=5)

    b1_matchings: List[Tuple[int, ...]] = []
    for p1 in range(1, 6):
        rem = [k for k in range(1, 6) if k != p1]
        a = rem[0]
        for b in rem[1:]:
            rem2 = [x for x in rem[1:] if x != b]
            b1_matchings.append((0, p1, a, b, rem2[0], rem2[1]))
    b1_twists = [(0, a, 0, b, 0, c) for a in range(5) for b in range(5) for c in range(5)]

    def permute_tuple(tw: Sequence[int], perm: Tuple[int, ...]) -> List[int]:
        out = [0, 0, 0, 0, 0, 0]
        for old_i, val in enumerate(tw):
            out[perm[old_i]] = val
        return out

    splits_all: List[Tuple[int, ...]] = []
    for s1 in itertools.combinations(range(6), 3):
        s2 = tuple(i for i in range(6) if i not in s1)
        splits_all.append(s1 + s2)
    splits_sym = [perm for perm in splits_all if perm[0] == 0]
    assert len(splits_all) == 20 and len(splits_sym) == 10

    for p in PRIMES_3:
        assert is_prime(p) and p % 12 == 1

    # Per-prime cached row collections
    per_prime_cache: Dict[int, Dict[str, List[List[int]]]] = {}
    selected_points_meta: Dict[str, Any] = {}
    for p in PRIMES_3:
        z12 = primitive_12th_root_mod_p(p)
        z6 = pow(z12, 2, p)
        pts = find_c6_points_mod_p(p, need=40)

        # Koszul Band-1 rows
        pm0_b1 = poly_with_rescaled_neg_coords_mod_p(det_b1, [1, 3, 5], z12, p)
        rows_koszul: List[List[int]] = []
        for perm in b1_matchings:
            pm = permute_poly_mod_p(pm0_b1, perm)
            for tw in b1_twists:
                rows_koszul.append(twist_vector_mod_p(pm, col_idx, 1751, permute_tuple(tw, perm), z6, p))

        # Exact over-Z 4x4 (1,1,1,3) A_1 rows (all 20 splits + deterministic twists)
        k48_zf0 = poly_with_rescaled_neg_coords_mod_p(
            {m: v % p for m, v in k48_z.items() if v % p}, [2, 5], z12, p
        )
        k66_zf0 = poly_with_rescaled_neg_coords_mod_p(
            {m: v % p for m, v in k66_z.items() if v % p}, [2, 5], z12, p
        )
        rng_z = random.Random(101)
        rows_z_nonkoszul: List[List[int]] = []
        for perm in splits_all:
            pm48 = permute_poly_mod_p(k48_zf0, perm)
            for _ in range(100):
                tw = [0, rng_z.randrange(6), rng_z.randrange(6), 0, rng_z.randrange(6), rng_z.randrange(6)]
                rows_z_nonkoszul.append(twist_vector_mod_p(pm48, col_idx, 1751, tw, z6, p))
        for perm in splits_sym:
            pm66 = permute_poly_mod_p(k66_zf0, perm)
            for _ in range(120):
                tw = [0, rng_z.randrange(6), rng_z.randrange(6), 0, rng_z.randrange(6), rng_z.randrange(6)]
                rows_z_nonkoszul.append(twist_vector_mod_p(pm66, col_idx, 1751, tw, z6, p))

        # 6x6 linear Ulrich MF rows
        u_p4, u_p8 = build_ulrich_6x6_traces_mod_p(p, pts)
        u_prod = {m1 + m2: (v1 * v2) % p for m1, v1 in u_p4.items() for m2, v2 in u_p8.items()}
        u_f0 = poly_with_rescaled_neg_coords_mod_p(u_prod, [2, 5], z12, p)
        rng_u = random.Random(42)
        rows_ulrich: List[List[int]] = []
        for perm in splits_all:
            pm = permute_poly_mod_p(u_f0, perm)
            for _ in range(160):
                tw = [0, rng_u.randrange(6), rng_u.randrange(6), 0, rng_u.randrange(6), rng_u.randrange(6)]
                rows_ulrich.append(twist_vector_mod_p(pm, col_idx, 1751, tw, z6, p))

        # Asymmetric full-support 4x4 (1,1,1,3) non-Koszul MF rows
        p4_a, p6a_a, p6b_a, p8_a, z6_idxs = build_4x4_1113_traces_mod_p(p, pts)
        k48_a = poly_with_rescaled_neg_coords_mod_p(
            {m1 + m2: (v1 * v2) % p for m1, v1 in p4_a.items() for m2, v2 in p8_a.items()},
            [2, 5],
            z12,
            p,
        )
        k66_a = poly_with_rescaled_neg_coords_mod_p(
            {m1 + m2: (v1 * v2) % p for m1, v1 in p6a_a.items() for m2, v2 in p6b_a.items()},
            [2, 5],
            z12,
            p,
        )
        rng_a = random.Random(7)
        rows_asym: List[List[int]] = []
        for perm in splits_all:
            pm48 = permute_poly_mod_p(k48_a, perm)
            for _ in range(180):
                tw = [0, rng_a.randrange(6), rng_a.randrange(6), 0, rng_a.randrange(6), rng_a.randrange(6)]
                rows_asym.append(twist_vector_mod_p(pm48, col_idx, 1751, tw, z6, p))
        for perm in splits_sym:
            pm66 = permute_poly_mod_p(k66_a, perm)
            for _ in range(250):
                tw = [0, rng_a.randrange(6), rng_a.randrange(6), 0, rng_a.randrange(6), rng_a.randrange(6)]
                rows_asym.append(twist_vector_mod_p(pm66, col_idx, 1751, tw, z6, p))

        per_prime_cache[p] = {
            "koszul": rows_koszul,
            "z_4x4_1113": rows_z_nonkoszul,
            "ulrich_6x6": rows_ulrich,
            "asym_4x4_1113": rows_asym,
        }
        selected_points_meta[str(p)] = {
            "c6_sample_points_checked": len(pts),
            "selected_z6_indices": z6_idxs,
        }

    def eval_stage(name: str, row_fn: Callable[[int], List[List[int]]]) -> Dict[str, Any]:
        prime_ranks: Dict[str, int] = {}
        prime_b1: Dict[str, int] = {}
        prime_b2: Dict[str, int] = {}
        prime_b3: Dict[str, int] = {}
        max_vram = 0.0
        nrows = 0
        dev_info: Dict[str, Any] = {}
        for p in PRIMES_3:
            rows = row_fn(p)
            nrows = len(rows)
            rk, info = gpu_modp_rank_with_stats(rows, p=p)
            rk1, info1 = gpu_modp_rank_with_stats([[r[c] for c in b1_cols] for r in rows], p=p)
            rk2, info2 = gpu_modp_rank_with_stats([[r[c] for c in b2_cols] for r in rows], p=p)
            rk3, info3 = gpu_modp_rank_with_stats([[r[c] for c in b3_cols] for r in rows], p=p)
            prime_ranks[str(p)] = rk
            prime_b1[str(p)] = rk1
            prime_b2[str(p)] = rk2
            prime_b3[str(p)] = rk3
            max_vram = max(
                max_vram,
                info["peak_vram_mb"],
                info1["peak_vram_mb"],
                info2["peak_vram_mb"],
                info3["peak_vram_mb"],
            )
            dev_info = info
        agree = (
            len(set(prime_ranks.values())) == 1
            and len(set(prime_b1.values())) == 1
            and len(set(prime_b2.values())) == 1
            and len(set(prime_b3.values())) == 1
        )
        assert agree, f"3-prime disagreement at {name}: {prime_ranks} {prime_b1} {prime_b2} {prime_b3}"
        tot_rk = next(iter(prime_ranks.values()))
        return {
            "stage": name,
            "rows": nrows,
            "cols": 1751,
            "total_rank": tot_rk,
            "band1_rank": next(iter(prime_b1.values())),
            "band2_rank": next(iter(prime_b2.values())),
            "band3_rank": next(iter(prime_b3.values())),
            "remaining_gap": 1751 - tot_rk,
            "prime_ranks": prime_ranks,
            "agreement": agree,
            "device": dev_info.get("device"),
            "gpu_name": dev_info.get("gpu_name"),
            "peak_vram_mb": max_vram,
        }

    ladder = [
        eval_stage("stage0_koszul_r4_only", lambda p: per_prime_cache[p]["koszul"]),
        eval_stage(
            "stage1_exact_z_4x4_1113_plus_koszul",
            lambda p: per_prime_cache[p]["koszul"] + per_prime_cache[p]["z_4x4_1113"],
        ),
        eval_stage("stage2_ulrich_6x6_only", lambda p: per_prime_cache[p]["ulrich_6x6"]),
        eval_stage("stage3_single_4x4_1113_nonkoszul", lambda p: per_prime_cache[p]["asym_4x4_1113"]),
        eval_stage(
            "stage4_koszul_plus_4x4_1113_full_closure",
            lambda p: per_prime_cache[p]["koszul"] + per_prime_cache[p]["asym_4x4_1113"],
        ),
    ]

    assert ladder[0]["total_rank"] == 1001
    assert ladder[0]["band1_rank"] == 1001 and ladder[0]["band2_rank"] == 0 and ladder[0]["band3_rank"] == 0
    assert ladder[1]["band2_rank"] > 0
    assert ladder[2]["band3_rank"] == 120
    assert ladder[3]["total_rank"] == 1731
    assert ladder[3]["band2_rank"] == 630 and ladder[3]["band3_rank"] == 120
    assert ladder[4]["total_rank"] == 1751
    assert ladder[4]["band1_rank"] == 1001 and ladder[4]["band2_rank"] == 630 and ladder[4]["band3_rank"] == 120
    assert ladder[4]["remaining_gap"] == 0

    out = {
        "exact_z_4x4_mixed_1113_c6": {
            "matrix_a1_degrees": [[1, 1, 1, 1], [1, 1, 1, 1], [1, 1, 1, 1], [3, 3, 3, 3]],
            "ab_eq_ba_eq_2f1_i4": True,
            "tr_aba_terms_mod_j": len(z_tr_aba),
            "tr_bab_terms_mod_j": len(z_tr_bab),
            "kunneth_band2_003333_product": k66_z[(0, 3, 3, 0, 3, 3)],
            "kunneth_band2_111144_product": k66_z[(1, 1, 4, 1, 1, 4)],
        },
        "exact_z_3x3_quadric_m3": {
            "r": 3,
            "ab_eq_ba_eq_f_i3": True,
            "tr_aba_terms_mod_j": len(tr3_aba),
            "tr_bab_terms_mod_j": len(tr3_bab),
            "kunneth_band_distribution": dict(m3_bands),
            "graded_18x18_naive_tr3_vanishes_by_z2_parity": graded_18_tr3 == 0,
        },
        "exact_z_6x6_buchsbaum_eisenbud_pfaffian": pfaff_res,
        "selected_nonkoszul_fp_witnesses": selected_points_meta,
        "gpu_crt_3prime_closure_ladder": ladder,
    }

    rep_path = (
        Path(__file__).resolve().parent.parent.parent
        / "reports"
        / "millennium_ext"
        / "non_koszul_mf_closure.json"
    )
    rep_path.parent.mkdir(parents=True, exist_ok=True)
    rep_path.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print("NON_KOSZUL_MF_CLOSURE_SUMMARY:")
    for st in ladder:
        print(
            f"  {st['stage']}: {st['total_rank']}/1751 "
            f"(B1={st['band1_rank']}/1001, B2={st['band2_rank']}/630, B3={st['band3_rank']}/120, "
            f"gap={st['remaining_gap']}, agree={st['agreement']}, vram={st['peak_vram_mb']} MB)"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
