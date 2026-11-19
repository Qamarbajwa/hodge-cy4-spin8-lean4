"""Experiment 2: 50/50 Block Schur-Complement Bias Audit on Spin(8) Gram Matrices
and 6-Stage Diagonal / Off-Diagonal Coverage Ladder on A_0 = E_i^4.

Strictly float-free (exact rational Fraction and integer arithmetic).
Outputs: reports/millennium_ext/schur_5050_diagonal_audit.json
"""

from __future__ import annotations

import itertools
import json
import sys
from fractions import Fraction
from pathlib import Path
from typing import Any, Dict, List, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mumford_cm_specializer import (
    ExtForm,
    clear_denoms,
    ext_add,
    ext_wedge,
    rational_nullspace,
    rational_rank,
    root_subsystem_gram6,
    so8_weights,
    zero_index_tuples,
)


# ---------------------------------------------------------------------------
# Exact rational matrix algebra helpers
# ---------------------------------------------------------------------------

def mat_det(mat: List[List[Fraction]]) -> Fraction:
    n = len(mat)
    m = [r[:] for r in mat]
    det = Fraction(1)
    for col in range(n):
        piv = next((i for i in range(col, n) if m[i][col] != 0), -1)
        if piv < 0:
            return Fraction(0)
        if piv != col:
            m[col], m[piv] = m[piv], m[col]
            det = -det
        pv = m[col][col]
        det *= pv
        for i in range(col + 1, n):
            if m[i][col] != 0:
                fac = m[i][col] / pv
                for j in range(col, n):
                    m[i][j] -= fac * m[col][j]
    return det


def mat_mul(A: List[List[Fraction]], B: List[List[Fraction]]) -> List[List[Fraction]]:
    r, k, c = len(A), len(B), len(B[0])
    return [
        [sum(A[i][t] * B[t][j] for t in range(k)) for j in range(c)]
        for i in range(r)
    ]


def mat_sub(A: List[List[Fraction]], B: List[List[Fraction]]) -> List[List[Fraction]]:
    return [[A[i][j] - B[i][j] for j in range(len(A[0]))] for i in range(len(A))]


def mat_scale(A: List[List[Fraction]], s: Fraction) -> List[List[Fraction]]:
    return [[s * x for x in row] for row in A]


def mat_adj3(D: List[List[Fraction]]) -> List[List[Fraction]]:
    assert len(D) == 3 and len(D[0]) == 3
    cof = [[Fraction(0) for _ in range(3)] for _ in range(3)]
    for i in range(3):
        for j in range(3):
            rs = [r for r in range(3) if r != i]
            cs = [c for c in range(3) if c != j]
            minor = D[rs[0]][cs[0]] * D[rs[1]][cs[1]] - D[rs[0]][cs[1]] * D[rs[1]][cs[0]]
            sgn = 1 if (i + j) % 2 == 0 else -1
            # Adjugate is transpose of cofactor matrix
            cof[j][i] = sgn * minor
    return cof


def extract_block(
    M: List[List[Fraction]], rows: List[int], cols: List[int]
) -> List[List[Fraction]]:
    return [[M[r][c] for c in cols] for r in rows]


def frac_mat_to_int(M: List[List[Fraction]]) -> List[List[int]]:
    out: List[List[int]] = []
    for row in M:
        irow: List[int] = []
        for x in row:
            assert x.denominator == 1
            irow.append(int(x.numerator))
        out.append(irow)
    return out


def frac_mat_to_str(M: List[List[Fraction]]) -> List[List[str]]:
    return [[str(x) for x in row] for row in M]


def audit_schur_5050_spin8() -> Dict[str, Any]:
    w = so8_weights()
    z_tups = zero_index_tuples(w)
    alpha1 = (2, -2, 0, 0)
    alpha2 = (0, 2, -2, 0)
    alpha3 = (0, 0, 2, -2)
    alpha4 = (0, 0, 2, 2)
    all_pos = [
        (2, -2, 0, 0), (2, 2, 0, 0),
        (2, 0, -2, 0), (2, 0, 2, 0),
        (2, 0, 0, -2), (2, 0, 0, 2),
        (0, 2, -2, 0), (0, 2, 2, 0),
        (0, 2, 0, -2), (0, 2, 0, 2),
        (0, 0, 2, -2), (0, 0, 2, 2),
    ]
    d4_all = all_pos + [tuple(-x for x in r) for r in all_pos]  # type: ignore[misc]

    mats = {
        "G_D4": root_subsystem_gram6(w, z_tups, d4_all),
        "G_A13": root_subsystem_gram6(w, z_tups, [alpha1, alpha3, alpha4]),
        "G_A2_pair12": root_subsystem_gram6(w, z_tups, [alpha1, alpha2]),
    }
    splits = {
        "contiguous_012_345": ([0, 1, 2], [3, 4, 5]),
        "interleaved_024_135": ([0, 2, 4], [1, 3, 5]),
    }

    report: Dict[str, Any] = {}
    for mname, M in mats.items():
        det_M = mat_det(M)
        assert det_M.denominator == 1
        m_res: Dict[str, Any] = {
            "matrix": frac_mat_to_int(M),
            "det_full": int(det_M.numerator),
            "splits": {},
        }
        for sname, (obs, hid) in splits.items():
            A = extract_block(M, obs, obs)
            B = extract_block(M, obs, hid)
            C = extract_block(M, hid, obs)
            D = extract_block(M, hid, hid)
            det_A = mat_det(A)
            det_D = mat_det(D)
            rk_A = rational_rank(A)
            rk_D = rational_rank(D)
            s_entry: Dict[str, Any] = {
                "obs_indices": obs,
                "hid_indices": hid,
                "A": frac_mat_to_int(A),
                "B": frac_mat_to_int(B),
                "C": frac_mat_to_int(C),
                "D": frac_mat_to_int(D),
                "det_A": int(det_A.numerator),
                "det_D": int(det_D.numerator),
                "rank_A": rk_A,
                "rank_D": rk_D,
            }
            if det_D != 0:
                adj_D = mat_adj3(D)
                assert mat_mul(D, adj_D) == mat_scale(
                    [[Fraction(1 if i == j else 0) for j in range(3)] for i in range(3)], det_D
                )
                D_inv = mat_scale(adj_D, Fraction(1) / det_D)
                bias = mat_mul(mat_mul(B, D_inv), C)
                S = mat_sub(A, bias)
                det_S = mat_det(S)
                assert det_M == det_D * det_S
                scaled_S = mat_sub(mat_scale(A, det_D), mat_mul(mat_mul(B, adj_D), C))
                assert scaled_S == mat_scale(S, det_D)
                tr_A = sum(A[i][i] for i in range(3))
                tr_S = sum(S[i][i] for i in range(3))
                tr_bias = sum(bias[i][i] for i in range(3))
                s_entry.update({
                    "hidden_block_singular": False,
                    "bias_nonzero": any(bias[i][j] != 0 for i in range(3) for j in range(3)),
                    "S_rational": frac_mat_to_str(S),
                    "detD_times_S_int": frac_mat_to_int(scaled_S),
                    "bias_rational": frac_mat_to_str(bias),
                    "trace_A": str(tr_A),
                    "trace_S": str(tr_S),
                    "trace_bias": str(tr_bias),
                    "det_S": str(det_S),
                    "schur_det_identity_holds": True,
                })
            else:
                hker = [clear_denoms(v) for v in rational_nullspace(D)]
                s_entry.update({
                    "hidden_block_singular": True,
                    "hidden_kernel_basis": hker,
                    "naive_schur_blocked_by_zero_detD": True,
                })
            m_res["splits"][sname] = s_entry
        report[mname] = m_res
    return report


# ---------------------------------------------------------------------------
# Part B: 6-Stage Diagonal & 50/50 Off-Diagonal Ladder on A_0 = E_i^4
# ---------------------------------------------------------------------------

def form_to_vec70(f: ExtForm, idx4: Dict[Tuple[int, ...], int]) -> List[Fraction]:
    v = [Fraction(0)] * 70
    for k, c in f.items():
        v[idx4[k]] = c
    return v


def form_from_sparse_int(pairs: List[Tuple[Tuple[int, ...], int]]) -> ExtForm:
    return {k: Fraction(v) for k, v in pairs if v != 0}


def find_sparse_dual_annihilator(
    rows: List[List[Fraction]],
    target: List[Fraction],
    basis4: List[Tuple[int, ...]],
) -> Tuple[int, List[List[Any]]]:
    """Finds a small integer dual functional lambda with lambda * row = 0 and lambda * target != 0."""
    ns = rational_nullspace(rows)
    best_vec: List[int] | None = None
    best_score = (10 ** 9, 10 ** 9)
    for v in ns:
        dot_t = sum(a * b for a, b in zip(v, target))
        if dot_t != 0:
            iv = clear_denoms(v)
            nnz = sum(1 for x in iv if x != 0)
            l1 = sum(abs(x) for x in iv)
            score = (nnz, l1)
            if score < best_score:
                best_score = score
                best_vec = iv
    assert best_vec is not None
    # Verify orthogonality to all rows and non-vanishing on target
    for r in rows:
        assert sum(Fraction(a) * b for a, b in zip(best_vec, r)) == 0
    tdot = sum(Fraction(a) * b for a, b in zip(best_vec, target))
    assert tdot != 0 and tdot.denominator == 1
    sparse = [[list(basis4[i]), best_vec[i]] for i in range(70) if best_vec[i] != 0]
    return int(tdot.numerator), sparse


def audit_ei4_coverage_ladder() -> Dict[str, Any]:
    basis4 = list(itertools.combinations(range(8), 4))
    idx4 = {k: i for i, k in enumerate(basis4)}

    diag_omega: List[ExtForm] = [{(2 * a, 2 * a + 1): Fraction(1)} for a in range(4)]
    div_plus: Dict[Tuple[int, int], ExtForm] = {
        (a, b): {(2 * a, 2 * b): Fraction(1), (2 * a + 1, 2 * b + 1): Fraction(1)}
        for a in range(4) for b in range(a + 1, 4)
    }
    div_minus: Dict[Tuple[int, int], ExtForm] = {
        (a, b): {(2 * a, 2 * b + 1): Fraction(1), (2 * a + 1, 2 * b): Fraction(-1)}
        for a in range(4) for b in range(a + 1, 4)
    }

    theta: ExtForm = {}
    for d in diag_omega:
        theta = ext_add(theta, d)

    w_re = ext_add(
        ext_wedge(div_minus[(0, 2)], div_minus[(1, 3)]),
        ext_wedge(div_plus[(0, 2)], div_plus[(1, 3)]),
        sign=-1,
    )
    w_im = ext_add(
        ext_wedge(div_plus[(0, 2)], div_minus[(1, 3)]),
        ext_wedge(div_minus[(0, 2)], div_plus[(1, 3)]),
        sign=1,
    )
    v_wre = form_to_vec70(w_re, idx4)
    v_wim = form_to_vec70(w_im, idx4)

    stages: List[Tuple[str, int, List[ExtForm]]] = [
        ("stage0_rho1_theta_only", 1, [theta]),
        ("stage1_rho4_pure_diagonals", 4, list(diag_omega)),
        ("stage2_rho10_diag_plus_50pct_dplus", 10, list(diag_omega) + list(div_plus.values())),
        ("stage3_rho10_diag_plus_50pct_dminus", 10, list(diag_omega) + list(div_minus.values())),
        (
            "stage4_rho8_minimal_cross_pair",
            8,
            list(diag_omega)
            + [div_plus[(0, 2)], div_plus[(1, 3)], div_minus[(0, 2)], div_minus[(1, 3)]],
        ),
        (
            "stage5_rho16_full_ns_ei4",
            16,
            list(diag_omega) + list(div_plus.values()) + list(div_minus.values()),
        ),
    ]

    ladder: List[Dict[str, Any]] = []
    for name, rho_dim, gens in stages:
        pair_vecs: List[List[Fraction]] = []
        for i in range(len(gens)):
            for j in range(i, len(gens)):
                pair_vecs.append(form_to_vec70(ext_wedge(gens[i], gens[j]), idx4))
        rk = rational_rank(pair_vecs)
        covers_re = rational_rank(pair_vecs + [v_wre]) == rk
        covers_im = rational_rank(pair_vecs + [v_wim]) == rk
        entry: Dict[str, Any] = {
            "stage": name,
            "divisor_dim": rho_dim,
            "wedge_pair_count": len(pair_vecs),
            "sym2_h4_rank": rk,
            "covers_w_re": covers_re,
            "covers_w_im": covers_im,
        }
        if not covers_re:
            val_re, sp_re = find_sparse_dual_annihilator(pair_vecs, v_wre, basis4)
            entry["dual_annihilator_w_re"] = {"dot_w_re": val_re, "sparse": sp_re}
        if not covers_im:
            val_im, sp_im = find_sparse_dual_annihilator(pair_vecs, v_wim, basis4)
            entry["dual_annihilator_w_im"] = {"dot_w_im": val_im, "sparse": sp_im}
        ladder.append(entry)

    return {
        "ambient_h4_dim": 70,
        "ladder": ladder,
    }


def main() -> int:
    out = {
        "part_a_spin8_schur_5050_bias": audit_schur_5050_spin8(),
        "part_b_ei4_diagonal_offdiag_ladder": audit_ei4_coverage_ladder(),
    }
    out_dir = Path(__file__).resolve().parents[2] / "reports" / "millennium_ext"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "schur_5050_diagonal_audit.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(json.dumps(out, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
