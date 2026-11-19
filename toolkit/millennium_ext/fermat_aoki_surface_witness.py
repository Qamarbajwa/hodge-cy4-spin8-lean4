"""Track 1 Exact Explorer: Newton-Aoki Complete-Intersection Surface Z_{5d} ⊂ X_{5d}^4,
Coset Stabilizer Annihilation (m = 25, 35, 55), and Band-4 Witnesses (m = 24..35, 49).

Strictly float-free (exact integer polynomial arithmetic + int64 CUDA verification).
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parent))
from fermat_band4_scout import (  # noqa: E402
    coprime_units,
    glued_surface_join_witness,
    has_prime_ap_vanish,
    is_band1,
    is_band2,
    is_band3,
    is_paired_diagonal,
    s6_orbit_size,
    sorted_hodge22_tuples,
)
from gpu_exact_linalg import gpu_filter_hodge22_batch  # noqa: E402


Monom5 = Tuple[int, int, int, int, int]
Poly5 = Dict[Monom5, int]


def poly5_add(a: Poly5, b: Poly5, sign: int = 1) -> Poly5:
    out = dict(a)
    for m, c in b.items():
        v = out.get(m, 0) + sign * c
        if v:
            out[m] = v
        else:
            out.pop(m, None)
    return out


def poly5_mul(a: Poly5, b: Poly5) -> Poly5:
    out: Poly5 = {}
    for m1, c1 in a.items():
        for m2, c2 in b.items():
            m: Monom5 = tuple(m1[i] + m2[i] for i in range(5))  # type: ignore[assignment]
            v = out.get(m, 0) + c1 * c2
            if v:
                out[m] = v
            else:
                out.pop(m, None)
    return out


def poly5_scale(k: int, a: Poly5) -> Poly5:
    return {m: k * c for m, c in a.items() if k * c != 0}


def poly5_pow(a: Poly5, exp: int) -> Poly5:
    res: Poly5 = {(0, 0, 0, 0, 0): 1}
    for _ in range(exp):
        res = poly5_mul(res, a)
    return res


def verify_newton_aoki_p5_identity() -> Dict[str, Any]:
    """Verify symbolically over Z[y_0..y_4]:
       p_5 - 5 e_5 == e_1 * (e_1^4 - 5 e_1^2 e_2 + 5 e_1 e_3 + 5 e_2^2 - 5 e_4) - 5 e_2 e_3.
    """
    import itertools

    def var5(i: int) -> Poly5:
        v = [0, 0, 0, 0, 0]
        v[i] = 1
        return {tuple(v): 1}  # type: ignore[dict-item]

    ys = [var5(i) for i in range(5)]

    def elem_sym(k: int) -> Poly5:
        acc: Poly5 = {}
        for idxs in itertools.combinations(range(5), k):
            term: Poly5 = {(0, 0, 0, 0, 0): 1}
            for idx in idxs:
                term = poly5_mul(term, ys[idx])
            acc = poly5_add(acc, term)
        return acc

    e1, e2, e3, e4, e5 = (elem_sym(k) for k in range(1, 6))
    p5: Poly5 = {}
    for i in range(5):
        v = [0, 0, 0, 0, 0]
        v[i] = 5
        p5[tuple(v)] = 1  # type: ignore[index]

    lhs = poly5_add(p5, poly5_scale(5, e5), sign=-1)
    q4 = poly5_pow(e1, 4)
    q4 = poly5_add(q4, poly5_scale(5, poly5_mul(poly5_pow(e1, 2), e2)), sign=-1)
    q4 = poly5_add(q4, poly5_scale(5, poly5_mul(e1, e3)), sign=1)
    q4 = poly5_add(q4, poly5_scale(5, poly5_pow(e2, 2)), sign=1)
    q4 = poly5_add(q4, poly5_scale(5, e4), sign=-1)

    rhs = poly5_add(poly5_mul(e1, q4), poly5_scale(5, poly5_mul(e2, e3)), sign=-1)
    diff = poly5_add(lhs, rhs, sign=-1)
    return {
        "lhs_terms": len(lhs),
        "rhs_terms": len(rhs),
        "q4_terms": len(q4),
        "exact_z_polynomial_identity": len(diff) == 0,
    }


def extract_cyclic_coset_cone(m: int, r: Tuple[int, ...]) -> Dict[str, Any] | None:
    """Decompose `r` into 5-term step-(m/5) coset + anchor divisible by 5."""
    if m % 5 != 0 or m == 0:
        return None
    step = m // 5
    rset = set(r)
    for x in r:
        coset = [(x + k * step) % m for k in range(5)]
        if all(c > 0 and c in rset for c in coset):
            rem = list(r)
            for c in coset:
                rem.remove(c)
            if len(rem) == 1 and rem[0] > 0 and rem[0] % 5 == 0:
                anchor = rem[0]
                coset_idxs = []
                used = set()
                for c in coset:
                    for idx, val in enumerate(r):
                        if idx not in used and val == c:
                            coset_idxs.append(idx)
                            used.add(idx)
                            break
                anchor_idx = [i for i in range(6) if i not in used][0]
                return {
                    "base_x": x,
                    "step": step,
                    "coset": coset,
                    "anchor": anchor,
                    "coset_indices": coset_idxs,
                    "anchor_index": anchor_idx,
                }
    return None


def verify_coset_stabilizer_annihilation(
    m: int, reps: List[Tuple[int, ...]]
) -> Dict[str, Any]:
    """Verify H_coset(5d) = {5*k_i on coset (sum k_i = 0), d*(1,1,1,1,1), d on anchor}."""
    d = m // 5
    # Exact basis generators valid for EVERY m = 5*d:
    # 1. Pairwise difference mod d on coset: 5*(e_0 - e_j) (since 5*d ≡ 0 mod 5d)
    # 2. Uniform d-shift on coset: d*(e_0 + e_1 + e_2 + e_3 + e_4) (5x*d + 10*d^2 ≡ 0 mod 5d)
    # 3. Anchor step: d*e_anchor (since 5 | anchor)
    coset_gens_k = [
        (5, m - 5, 0, 0, 0),
        (5, 0, m - 5, 0, 0),
        (5, 0, 0, m - 5, 0),
        (5, 0, 0, 0, m - 5),
        (d, d, d, d, d),
    ]
    orbit_checks: List[Dict[str, Any]] = []
    all_ok = True
    for r in reps:
        info = extract_cyclic_coset_cone(m, r)
        if info is None:
            all_ok = False
            continue
        c_idxs = info["coset_indices"]
        a_idx = info["anchor_index"]
        gens_h: List[List[int]] = []
        for gk in coset_gens_k:
            h = [0] * 6
            for pos, idx in enumerate(c_idxs):
                h[idx] = gk[pos] % m
            gens_h.append(h)
        h_anchor = [0] * 6
        h_anchor[a_idx] = d % m
        gens_h.append(h_anchor)

        dots_mod_m = [sum(r[i] * h[i] for i in range(6)) % m for h in gens_h]
        ok = all(x == 0 for x in dots_mod_m)
        if not ok:
            all_ok = False
        orbit_checks.append({
            "rep": list(r),
            "weight": s6_orbit_size(r),
            "coset": info["coset"],
            "anchor": info["anchor"],
            "anchor_index": a_idx,
            "stabilizer_generators_count": len(gens_h),
            "all_annihilated_mod_m": ok,
        })
    return {
        "m": m,
        "step_d": d,
        "orbit_count": len(reps),
        "total_weight": sum(s6_orbit_size(r) for r in reps),
        "all_orbits_annihilated": all_ok,
        "orbits": orbit_checks,
    }


def analyze_band4_constructively(m: int) -> Dict[str, Any]:
    t0 = time.time()
    units = coprime_units(m)
    reps = sorted_hodge22_tuples(m)
    gpu_matched, gpu_stats = gpu_filter_hodge22_batch(reps, units, m, target_weight=3)
    if len(gpu_matched) != len(reps):
        raise RuntimeError(f"GPU mismatch at m={m}: {len(gpu_matched)} vs {len(reps)}")

    b1 = b2 = b3 = b4 = 0
    paired_reps: List[List[int]] = []
    glued_witnesses: List[Dict[str, Any]] = []
    coset_reps: List[Tuple[int, ...]] = []
    unresolved: List[List[int]] = []

    for r in reps:
        w = s6_orbit_size(r)
        if is_band1(m, r):
            b1 += w
        elif is_band2(m, r):
            b2 += w
        elif is_band3(m, r):
            b3 += w
        else:
            b4 += w
            if is_paired_diagonal(r):
                paired_reps.append(list(r))
            else:
                gw = glued_surface_join_witness(m, r, units)
                if gw is not None:
                    glued_witnesses.append({"rep": list(r), "weight": w, **gw})
                elif extract_cyclic_coset_cone(m, r) is not None:
                    coset_reps.append(r)
                else:
                    unresolved.append(list(r))

    coset_stab = verify_coset_stabilizer_annihilation(m, coset_reps) if coset_reps else None
    return {
        "m": m,
        "elapsed_sec": round(time.time() - t0, 3),
        "gpu_galois_stats": gpu_stats,
        "h22_prim": b1 + b2 + b3 + b4,
        "band1": b1,
        "band2": b2,
        "band3": b3,
        "band4": b4,
        "paired_count": len(paired_reps),
        "paired_weight": sum(s6_orbit_size(tuple(r)) for r in paired_reps),
        "glued_count": len(glued_witnesses),
        "glued_weight": sum(g["weight"] for g in glued_witnesses),
        "coset_cone_count": len(coset_reps),
        "coset_cone_weight": sum(s6_orbit_size(r) for r in coset_reps),
        "unresolved_count": len(unresolved),
        "paired_reps": paired_reps,
        "glued_witnesses": glued_witnesses,
        "coset_stabilizer_verification": coset_stab,
        "prime_ap_fallback_flag": [has_prime_ap_vanish(m, r) for r in coset_reps[:4]],
    }


def main() -> int:
    newton_check = verify_newton_aoki_p5_identity()
    assert newton_check["exact_z_polynomial_identity"] is True

    degrees = [24, 25, 26, 27, 28, 30, 35, 49, 55]
    per_degree = [analyze_band4_constructively(m) for m in degrees]

    # Separate Lean compact witness report from full JSON summary
    summary = {
        "newton_aoki_p5_identity": newton_check,
        "degrees_analyzed": degrees,
        "per_degree_summary": [
            {
                k: v
                for k, v in d.items()
                if k not in ("glued_witnesses", "paired_reps")
            }
            for d in per_degree
        ],
        "compact_witness_tables": {
            str(d["m"]): {
                "paired_reps": d["paired_reps"],
                "glued_witnesses": d["glued_witnesses"],
            }
            for d in per_degree
            if d["m"] in (26, 27, 28)
        },
    }

    out_dir = Path(__file__).resolve().parents[2] / "reports" / "millennium_ext"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "fermat_aoki_surface_m25_to_m55.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8"
    )
    print(json.dumps(
        {
            "newton_aoki_p5_identity": newton_check,
            "summary": summary["per_degree_summary"],
        },
        indent=2,
    ))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
