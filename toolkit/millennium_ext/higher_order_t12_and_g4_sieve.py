"""Track 2 RTX A2000 Exact Explorer:
1. Order-12 Griffiths-Dwork Infinitesimal Jets (mod t^12) across Bands 1, 2, and 3.
2. Unmixed Z_{2,2,2} / Z_{3,1,1} Wiebe-Scheja-Storch Colon Ideals vs Non-Unmixed Embedded
   Ideal Obstruction <z_0^2, z_0*z_1, z_2, z_4> in R(F_0).
3. Codimension-3 Calabi-Yau Complete Intersections X_{2,2,4} and X_{2,3,3} in P^7:
   exact primitive Hodge diamonds, 8-var auxiliary Gorenstein Hilbert series, and
   weighted Cayley-trick Jacobian dimensions via 3-prime int64 CUDA CRT.
"""

from __future__ import annotations

import json
import sys
from fractions import Fraction
from pathlib import Path
from typing import Any, Dict, List, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parent))
from counterexample_sieve import (  # noqa: E402
    _mons_weighted,
    poly_pow_int,
)
from gpu_exact_linalg import DEFAULT_3_PRIMES, gpu_modp_rank_with_stats  # noqa: E402
from multi_order_gd_crt import (  # noqa: E402
    PRIMES_62,
    Monom6,
    PolyMod,
    gauss_manin_step_mod,
    joint_jet_ranks_mod,
    monomials6,
    rref_rank_mod,
)


P62 = PRIMES_62[0]


def gpu_safe_3prime_rank(mat: List[List[int]]) -> Dict[str, Any]:
    """Run exact int64 CUDA rank over DEFAULT_3_PRIMES with per-prime pre-reduction."""
    if not mat or not mat[0]:
        return {"rank": 0, "prime_ranks": {}, "agreement": True, "device": "cuda:0"}
    prime_ranks: Dict[str, int] = {}
    last_info: Dict[str, Any] = {}
    max_peak = 0.0
    for p in DEFAULT_3_PRIMES:
        reduced = [[c % p for c in row] for row in mat]
        rk, info = gpu_modp_rank_with_stats(reduced, p=p)
        prime_ranks[str(p)] = rk
        last_info = info
        if info["peak_vram_mb"] > max_peak:
            max_peak = info["peak_vram_mb"]
    vals = list(prime_ranks.values())
    return {
        "rank": max(vals),
        "prime_ranks": prime_ranks,
        "agreement": len(set(vals)) == 1,
        "device": last_info.get("device"),
        "gpu_name": last_info.get("gpu_name"),
        "peak_vram_mb": max_peak,
    }


def run_t12_jets() -> Dict[str, Any]:
    max_order = 11  # mod t^12: t^0 .. t^11
    cases = {
        "band1_quadric": (
            {(4, 0, 4, 0, 4, 0): 1},
            {(2, 4, 0, 0, 0, 0): 1, (3, 3, 0, 0, 0, 0): 1, (4, 2, 0, 0, 0, 0): 1},
        ),
        "band2_curve_join": (
            {(2, 2, 2, 2, 2, 2): 1},
            {(4, 1, 0, 1, 0, 0): 1, (0, 0, 1, 4, 1, 0): 1, (0, 1, 0, 0, 1, 4): 1},
        ),
        "band3_surface_curve": (
            {(4, 2, 2, 2, 1, 1): 1},
            {(0, 4, 0, 0, 1, 1): 1, (0, 0, 4, 0, 1, 1): 1, (0, 0, 0, 4, 1, 1): 1},
        ),
    }
    out: Dict[str, Any] = {}
    for name, (lam0_raw, w_raw) in cases.items():
        prime_terms: List[List[int]] = []
        prime_ranks_t11: List[List[int]] = []
        shadow_terms: List[List[int]] = []
        for p in PRIMES_62:
            lam0: PolyMod = {m: c % p for m, c in lam0_raw.items()}
            wdir: PolyMod = {m: c % p for m, c in w_raw.items()}
            j_strict = [lam0]
            j_shadow = [lam0]
            for _ in range(max_order):
                j_strict.append(gauss_manin_step_mod(wdir, j_strict[-1], p, True))
                j_shadow.append(gauss_manin_step_mod(wdir, j_shadow[-1], p, False))
            prime_terms.append([len(x) for x in j_strict])
            shadow_terms.append([len(x) for x in j_shadow])
            prime_ranks_t11.append(joint_jet_ranks_mod(j_strict, p, 6))

        # Verify top-order t^0..t^11 d=6 system on RTX A2000 over integer jet
        j_int = [{m: c for m, c in lam0_raw.items()}]
        w_int = {m: c for m, c in w_raw.items()}
        for _ in range(max_order):
            prod: Dict[Monom6, int] = {}
            for m1, c1 in w_int.items():
                for m2, c2 in j_int[-1].items():
                    pm = tuple(m1[i] + m2[i] for i in range(6))  # type: ignore[assignment]
                    prod[pm] = prod.get(pm, 0) + c1 * c2
            nxt: Dict[Monom6, int] = {}
            for pm, pc in prod.items():
                for i in range(6):
                    if pm[i] >= 5:
                        if pm[i] > 5:
                            nm = list(pm)
                            nm[i] -= 6
                            om = tuple(nm)  # type: ignore[assignment]
                            if all(e <= 4 for e in om):
                                nxt[om] = nxt.get(om, 0) + pc * (pm[i] - 5)
                        break
            j_int.append({k: v for k, v in nxt.items() if v != 0})
        t_cols: Dict[Tuple[int, Monom6], int] = {}
        t_sparse: List[Dict[int, int]] = []
        for m in monomials6(6):
            rd: Dict[int, int] = {}
            for k_idx, lam in enumerate(j_int):
                for lm, lc in lam.items():
                    pm = tuple(m[i] + lm[i] for i in range(6))  # type: ignore[assignment]
                    if all(e <= 4 for e in pm):
                        ci = t_cols.setdefault((k_idx, pm), len(t_cols))
                        rd[ci] = rd.get(ci, 0) + lc
            if rd:
                t_sparse.append(rd)
        dense_d6 = [[rd.get(j, 0) for j in range(len(t_cols))] for rd in t_sparse]
        gpu_res = gpu_safe_3prime_rank(dense_d6)

        out[name] = {
            "max_order": max_order,
            "strict_term_counts_t0_to_t11": prime_terms[0],
            "unreduced_shadow_counts_t0_to_t11": shadow_terms[0],
            "crt_3prime_t11_rank_agreement": (
                prime_ranks_t11[0] == prime_ranks_t11[1] == prime_ranks_t11[2]
            ),
            "ranks_t11_d0_to_d6": prime_ranks_t11[0],
            "gpu_t11_d6_crt": gpu_res,
        }
    return out


def analyze_g4_and_embedded_ideals() -> Dict[str, Any]:
    """Compare unmixed G>=3 regular sequences in R(F_0) against embedded-point non-unmixed ideal."""
    m_by_d = {d: monomials6(d) for d in range(7)}
    idx_by_d = {d: {m: i for i, m in enumerate(ms)} for d, ms in m_by_d.items()}

    def profile_in_r(gens: List[Dict[Monom6, int]]) -> List[int]:
        prof: List[int] = []
        for d in range(7):
            cols = idx_by_d[d]
            rows: List[List[int]] = []
            for g in gens:
                dg = sum(next(iter(g)))
                if d < dg:
                    continue
                for m in m_by_d[d - dg]:
                    row = [0] * len(cols)
                    for gm, gc in g.items():
                        pm = tuple(m[i] + gm[i] for i in range(6))  # type: ignore[assignment]
                        if pm in cols:
                            row[cols[pm]] = (row[cols[pm]] + gc) % P62
                    if any(row):
                        rows.append(row)
            prof.append(len(cols) - rref_rank_mod(rows, P62))
        return prof

    def mono(idx: int, e: int) -> Monom6:
        v = [0] * 6
        v[idx] = e
        return tuple(v)  # type: ignore[return-value]

    # 1. Z_{2,2,2}: 3 quadric pairs (100% unmixed codim-3 CI inside F_0)
    z222 = [
        {(1, 1, 0, 0, 0, 0): 1},
        {mono(0, 4): 1, mono(1, 4): P62 - 1},
        {(0, 0, 1, 1, 0, 0): 1},
        {mono(2, 4): 1, mono(3, 4): P62 - 1},
        {(0, 0, 0, 0, 1, 1): 1},
        {mono(4, 4): 1, mono(5, 4): P62 - 1},
    ]
    # 2. Z_{3,1,1}: unmixed cubic-pair scheme <z0*z1, z0^3 - z1^3, z2, z4> on F_0^{signed}
    z311 = [
        {(1, 1, 0, 0, 0, 0): 1},
        {mono(0, 3): 1, mono(1, 3): P62 - 1},
        {mono(2, 1): 1},
        {mono(4, 1): 1},
    ]
    # 3. Non-unmixed embedded-point ideal <z0^2, z0*z1, z2, z4> = <z0, z2, z4> ∩ <z0^2, z1, z2, z4>
    emb = [
        {mono(0, 2): 1},
        {(1, 1, 0, 0, 0, 0): 1},
        {mono(2, 1): 1},
        {mono(4, 1): 1},
    ]
    p_z222 = profile_in_r(z222)
    p_z311 = profile_in_r(z311)
    p_emb = profile_in_r(emb)

    # First differences Delta(p) inspect growth / Gotzmann regularity
    return {
        "z222_quotient_profile_d0_to_d6": p_z222,
        "z311_quotient_profile_d0_to_d6": p_z311,
        "embedded_non_unmixed_profile_d0_to_d6": p_emb,
        "z222_sum_d0_to_d6": sum(p_z222),
        "z311_sum_d0_to_d6": sum(p_z311),
        "embedded_sum_d0_to_d6": sum(p_emb),
        "z311_equals_embedded_failure": p_z311 != p_emb,
    }


def hirzebruch_prim_hodge_diamond_pN(N: int, ds: List[int]) -> List[int]:
    """Exact float-free primitive middle Hodge numbers for smooth X_{ds} subset P^N (dim = N - len(ds) = 4)."""
    dim = N - len(ds)
    max_x = N + 1

    def pw(poly: List[Fraction], e: int) -> List[Fraction]:
        res = [Fraction(1)] + [Fraction(0)] * max_x
        for _ in range(e):
            nxt = [Fraction(0)] * (max_x + 1)
            for i in range(max_x + 1):
                for j in range(min(len(poly), max_x + 1 - i)):
                    nxt[i + j] += res[i] * poly[j]
            res = nxt
        return res

    def pinv(poly: List[Fraction]) -> List[Fraction]:
        out = [Fraction(0)] * (max_x + 1)
        out[0] = Fraction(1) / poly[0]
        for i in range(1, max_x + 1):
            s = Fraction(0)
            for k in range(1, i + 1):
                s -= poly[k] * out[i - k]
            out[i] = s / poly[0]
        return out

    def pmul(p: List[Fraction], q: List[Fraction]) -> List[Fraction]:
        out = [Fraction(0)] * (max_x + 1)
        for i in range(max_x + 1):
            for j in range(max_x + 1 - i):
                out[i + j] += p[i] * q[j]
        return out

    pts: List[Tuple[Fraction, Fraction]] = []
    for y in range(dim + 2):
        A = [Fraction(1), Fraction(-1)] + [Fraction(0)] * (max_x - 1)
        B = [Fraction(1), Fraction(y)] + [Fraction(0)] * (max_x - 1)
        cur = pinv(pmul(A, B))
        for d in ds:
            Bd = pw(B, d)
            Ad = pw(A, d)
            n_k = [Bd[i] - Ad[i] for i in range(max_x + 1)]
            d_k = [Bd[i] + y * Ad[i] for i in range(max_x + 1)]
            cur = pmul(cur, pmul(n_k, pinv(d_k)))
        pts.append((Fraction(y), cur[N]))

    coeffs = [Fraction(0)] * (dim + 1)
    for j in range(dim + 1):
        poly = [Fraction(1)] + [Fraction(0)] * dim
        denom = Fraction(1)
        for m in range(dim + 1):
            if m == j:
                continue
            denom *= pts[j][0] - pts[m][0]
            nxt = [Fraction(0)] * (dim + 1)
            for k in range(dim + 1):
                nxt[k] += -pts[m][0] * poly[k]
                if k + 1 <= dim:
                    nxt[k + 1] += poly[k]
            poly = nxt
        for k in range(dim + 1):
            coeffs[k] += pts[j][1] * poly[k] / denom

    return [int((-1) ** p * coeffs[p]) - 1 for p in range(dim + 1)]


def weighted_cayley_p7_dims(ds: List[int], max_w: int = 4) -> Dict[str, Any]:
    """Weighted Cayley-trick Jacobian dimensions for X_{ds} subset P^7 via int64 CUDA CRT."""
    N = 7
    n_vars = N + 1
    r_codim = len(ds)
    d_max = max(ds)
    deg_F = d_max + 1
    y_wts = [deg_F - d for d in ds]
    wts = [1] * n_vars + y_wts
    # F = sum_k y_k sum_i c_{k,i} z_i^{d_k}, using c_{k,i} = (i+1)^{k} + k + 1
    dims: List[int] = []
    gpu_last: Dict[str, Any] = {}
    for w in range(max_w + 1):
        cols = _mons_weighted(wts, w)
        idx = {m: i for i, m in enumerate(cols)}
        rows: List[List[int]] = []
        for k, d in enumerate(ds):
            if w >= d:
                for m in _mons_weighted(wts, w - d):
                    row = [0] * len(cols)
                    for i in range(n_vars):
                        nm = list(m)
                        nm[i] += d
                        ci = idx[tuple(nm)]
                        row[ci] = row[ci] + pow(i + 1, k + 1)
                    rows.append(row)
        if w >= deg_F - 1:
            for m in _mons_weighted(wts, w - (deg_F - 1)):
                for i in range(n_vars):
                    row = [0] * len(cols)
                    for k, d in enumerate(ds):
                        nm = list(m)
                        nm[n_vars + k] += 1
                        nm[i] += d - 1
                        ci = idx[tuple(nm)]
                        row[ci] = row[ci] + d * pow(i + 1, k + 1)
                    rows.append(row)
        crt = gpu_safe_3prime_rank(rows)
        gpu_last = crt
        dims.append(len(cols) - crt["rank"])
    return {
        "multidegree": ds,
        "ambient": "P^7",
        "weights": wts,
        "weighted_jacobian_dims": dims,
        "gpu_last_w_crt": gpu_last,
    }


def analyze_p7_complete_intersections() -> List[Dict[str, Any]]:
    specs = [[2, 2, 4], [2, 3, 3]]
    out: List[Dict[str, Any]] = []
    for ds in specs:
        hd = hirzebruch_prim_hodge_diamond_pN(7, ds)
        d_max = max(ds)
        aux = poly_pow_int([1] * (d_max - 1), 8)
        wc = weighted_cayley_p7_dims(ds, max_w=4)
        out.append({
            "multidegree": ds,
            "ambient": "P^7",
            "calabi_yau_canonical": (sum(ds) == 8),
            "hodge_prim_diamond": hd,
            "hodge_prim_palindromic": (hd == list(reversed(hd))),
            "hodge_prim_total_dim": sum(hd),
            "aux_8var_hilbert_length": len(aux),
            "aux_8var_hilbert_sum": sum(aux),
            "aux_8var_palindromic": (aux == list(reversed(aux))),
            "aux_8var_hilbert": aux,
            "weighted_cayley": wc,
        })
    return out


def main() -> int:
    t12 = run_t12_jets()
    g4_emb = analyze_g4_and_embedded_ideals()
    p7_ci = analyze_p7_complete_intersections()
    res = {
        "order_12_jets": t12,
        "g4_and_embedded_obstructions": g4_emb,
        "p7_codim3_complete_intersections": p7_ci,
    }
    out_dir = Path(__file__).resolve().parents[2] / "reports" / "millennium_ext"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "t12_g4_and_p7_ci_sieve.json").write_text(
        json.dumps(res, indent=2), encoding="utf-8"
    )
    print(json.dumps(res, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
