"""Experiment 11 (Wall 3): Mumford A H^4(A) Uniqueness + Triple Self-Product A x A x A
19-Dimensional Hodge (3,3) Closure Collapse via Single Chiral Generator T_ch.

Certifies with exact SymPy / int64 integer arithmetic:
  1. H^4(A) = wedge^4(Z^8) (70-dim) invariant uniqueness under SL_2(R) x SO(4):
     - Theta^2 is annihilated by all 9 Lie generators of sl_2(R) + su(2)_+ + su(2)_-.
     - Dropping Theta^2 index (0,1,4,5), the 69 x 69 commutator/action system B_69 admits
       an exact integer inverse B_{69,inv} B_69 = 12 I_69 (200 nonzero entries, max |entry|=12),
       proving dim H^4(A)^{SL_2(R) x SO(4)} = 1.
  2. Exact 21,952-entry small-diagonal-to-divisor identity on A x A x A (H^2(A)^{otimes 3}):
     - 8 T_cup_up == v_ttt + 2*(v_1dd + v_2dd + v_3dd) + 8*D_cyc across all 28^3 entries,
       both totally S_3 symmetric; Sym^3 NS(A x A x A) has rank 5.
  3. Exact 19-sector decomposition, Casimir polynomial generation, 4-probe matrix slices,
     and 4-stage closure ladder 5 -> 11 -> 12 -> 19:
     - 24 Q_0 = T_th, 32 Q_sd = T_ch^2 - 8 T_ch, 32 Q_asd = T_ch^2 + 8 T_ch,
       16 Q_ric = 16 T_dd + 2 T_th - T_ch^2.
     - 64 triples (Q_a x Q_b x Q_c) on D_cyc split into 45 zero and 19 mutually orthogonal
       sectors (diagonal 19x19 Gram), verified by 4 canonical column probes.
     - Exact orthogonal {0,1} indicator bases realize 5 -> 11 -> 12 -> 19; all 7 parity-odd
       vectors (e_i - e_{flip(i)}) are orthogonal to Stage 2 (12-dim A_even^3).
  4. Exact Hodge (3,3) derivation vanishing, 81^3 boost scaling & 12+7 parity split on A^3.

Outputs: reports/millennium_ext/mumford_triple_product_hodge33.json
"""

from __future__ import annotations

import itertools
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

import numpy as np
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


def _ext4_action(mat8: sp.Matrix, tups4: List[Tuple[int, ...]], t4i: Dict[Tuple[int, ...], int]) -> np.ndarray:
    out = np.zeros((70, 70), dtype=np.int64)
    m_np = np.array(mat8.tolist(), dtype=np.int64)
    for col, tup in enumerate(tups4):
        for pos in range(4):
            i = tup[pos]
            for j in range(8):
                val = int(m_np[j, i])
                if val == 0 or (j in tup and j != i):
                    continue
                lst = list(tup)
                lst[pos] = j
                invs = sum(1 for a in range(4) for b in range(a + 1, 4) if lst[a] > lst[b])
                out[t4i[tuple(sorted(lst))], col] += val * (-1 if invs % 2 else 1)
    return out


def run_mumford_triple_product_experiment() -> Tuple[Dict[str, Any], Dict[str, Any]]:
    data = build_mumford_real_generators()
    cas = verify_end_q_and_casimirs(data)
    e_real = data["E_real"]
    all_gens = data["all_gens"]
    pairs28: List[Tuple[int, int]] = cas["tups2_8"]
    p2i = {p: i for i, p in enumerate(pairs28)}
    q0, q_sd, q_asd, q_ric = cas["projs"]
    i28 = sp.eye(28)

    e_np = np.array(e_real.tolist(), dtype=np.int64)
    e2 = wedge2_group(e_real, pairs28)
    e2_np = np.array(e2.tolist(), dtype=np.int64)
    q_np = {
        "0": np.array(q0.tolist(), dtype=np.int64),
        "sd": np.array(q_sd.tolist(), dtype=np.int64),
        "asd": np.array(q_asd.tolist(), dtype=np.int64),
        "ric": np.array(q_ric.tolist(), dtype=np.int64),
    }

    # 1. H^4(A) = wedge^4(Z^8) invariant uniqueness (dim = 1)
    tups4 = list(itertools.combinations(range(8), 4))
    t4i = {t: i for i, t in enumerate(tups4)}
    th2_vec = np.zeros(70, dtype=np.int64)
    for tup in [(0, 1, 4, 5), (0, 2, 4, 6), (0, 3, 4, 7), (1, 2, 5, 6), (1, 3, 5, 7), (2, 3, 6, 7)]:
        th2_vec[t4i[tup]] = -2

    ext4_gens = [_ext4_action(g, tups4, t4i) for g in all_gens]
    for g4 in ext4_gens:
        assert np.all(g4 @ th2_vec == 0)

    drop_col = t4i[(0, 1, 4, 5)]
    keep_cols = [c for c in range(70) if c != drop_col]
    cand_rows = []
    cand_labels: List[Tuple[int, int]] = []
    for gi, g4 in enumerate(ext4_gens):
        for r in range(70):
            row = g4[r, keep_cols]
            if np.any(row != 0):
                cand_rows.append(row)
                cand_labels.append((gi, r))

    _, piv_idx = sp.Matrix(np.array(cand_rows).T.tolist()).rref()
    assert len(piv_idx) == 69
    b69_labels = [cand_labels[i] for i in piv_idx]
    b69 = sp.Matrix([cand_rows[i].tolist() for i in piv_idx])
    det69 = int(b69.det())
    assert det69 != 0
    b69_inv_rat = b69.inv()
    scale69 = int(sp.lcm([sp.fraction(x)[1] for x in b69_inv_rat]))
    assert scale69 == 12
    b69_inv_int = sp.Matrix(69, 69, [int(x * scale69) for x in b69_inv_rat])
    assert b69_inv_int * b69 == 12 * sp.eye(69)
    assert b69 * b69_inv_int == 12 * sp.eye(69)
    nnz_b69_inv = sum(1 for x in b69_inv_int if x != 0)
    max_abs_b69_inv = max(abs(int(x)) for x in b69_inv_int)
    assert nnz_b69_inv == 200 and max_abs_b69_inv == 12

    # 2. Exact 21,952-entry small-diagonal-to-divisor identity on A^3
    th_terms = [(k, k + 4, 1) for k in range(4)]
    t_cup = np.zeros((28, 28, 28), dtype=np.int64)
    for i in range(28):
        for j in range(28):
            t4, s1 = _wedge_tup(pairs28[i], pairs28[j])
            if t4 is None:
                continue
            for k in range(28):
                t6, s2 = _wedge_tup(t4, pairs28[k])
                if t6 is None:
                    continue
                val = 0
                for a, b, c1 in th_terms:
                    t8, s3 = _wedge_tup(t6, (a, b))
                    if t8 is not None:
                        val += c1 * s1 * s2 * s3
                t_cup[i, j, k] = val

    t_cup_up = np.einsum("ia,jb,kc,abc->ijk", e2_np, e2_np, e2_np, t_cup)
    d_cyc = np.zeros((28, 28, 28), dtype=np.int64)
    nz_e = [(i, j, int(e_np[i, j])) for i in range(8) for j in range(8) if e_np[i, j] != 0]
    for i, j, c1 in nz_e:
        for k, l, c2 in nz_e:
            if j == k:
                continue
            for m_, n, c3 in nz_e:
                if i == m_ or l == n:
                    continue
                sgn = -1
                if i < m_:
                    p1 = p2i[(i, m_)]
                else:
                    p1 = p2i[(m_, i)]
                    sgn = -sgn
                if j < k:
                    p2 = p2i[(j, k)]
                else:
                    p2 = p2i[(k, j)]
                    sgn = -sgn
                if l < n:
                    p3 = p2i[(l, n)]
                else:
                    p3 = p2i[(n, l)]
                    sgn = -sgn
                d_cyc[p1, p2, p3] += sgn * c1 * c2 * c3

    assert int(np.count_nonzero(t_cup_up)) == 360
    assert int(np.count_nonzero(d_cyc)) == 340
    assert int(np.sum(d_cyc * d_cyc)) == 352
    assert np.array_equal(t_cup_up, t_cup_up.transpose(1, 0, 2))
    assert np.array_equal(t_cup_up, t_cup_up.transpose(0, 2, 1))
    assert np.array_equal(d_cyc, d_cyc.transpose(1, 0, 2))
    assert np.array_equal(d_cyc, d_cyc.transpose(0, 2, 1))

    th_vec = np.zeros(28, dtype=np.int64)
    for k in range(4):
        th_vec[p2i[(k, k + 4)]] = 2
    v_ttt = np.einsum("i,j,k->ijk", th_vec, th_vec, th_vec)
    v_1dd = np.einsum("i,jk->ijk", th_vec, -2 * e2_np)
    v_2dd = np.einsum("j,ik->ijk", th_vec, -2 * e2_np)
    v_3dd = np.einsum("k,ij->ijk", th_vec, -2 * e2_np)

    assert np.array_equal(8 * t_cup_up, v_ttt + 2 * (v_1dd + v_2dd + v_3dd) + 8 * d_cyc)
    mat_sym3 = np.vstack([x.ravel() for x in (v_ttt, v_1dd, v_2dd, v_3dd, d_cyc)])
    nz_s3 = np.any(mat_sym3 != 0, axis=0)
    assert int(sp.Matrix(mat_sym3[:, nz_s3].tolist()).rank()) == 5
    mat_sym3_plus = np.vstack([mat_sym3, t_cup_up.ravel()])
    nz_s3p = np.any(mat_sym3_plus != 0, axis=0)
    assert int(sp.Matrix(mat_sym3_plus[:, nz_s3p].tolist()).rank()) == 5

    # 3. Casimir polynomials, 19-sector decomposition, 4-probe slices, and 5 -> 11 -> 12 -> 19 ladder
    t_th = 24 * q0
    t_dd = 4 * i28 - 4 * q0
    t_ch = -2 * (q_sd - q_asd)
    assert 24 * q0 == t_th
    assert 32 * q_sd == t_ch**2 - 8 * t_ch
    assert 32 * q_asd == t_ch**2 + 8 * t_ch
    assert 16 * q_ric == 16 * t_dd + 2 * t_th - t_ch**2

    sectors: List[Tuple[str, str, str]] = [
        ("0", "0", "0"),
        ("0", "sd", "sd"), ("0", "asd", "asd"), ("0", "ric", "ric"),
        ("sd", "0", "sd"), ("asd", "0", "asd"), ("ric", "0", "ric"),
        ("sd", "sd", "0"), ("asd", "asd", "0"), ("ric", "ric", "0"),
        ("sd", "sd", "sd"), ("asd", "asd", "asd"), ("ric", "ric", "ric"),
        ("sd", "asd", "ric"), ("sd", "ric", "asd"),
        ("asd", "sd", "ric"), ("asd", "ric", "sd"),
        ("ric", "sd", "asd"), ("ric", "asd", "sd"),
    ]
    sec_set = set(sectors)
    d_secs = []
    for a in ("0", "sd", "asd", "ric"):
        for b in ("0", "sd", "asd", "ric"):
            for c in ("0", "sd", "asd", "ric"):
                proj = np.einsum("ia,jb,kc,abc->ijk", q_np[a], q_np[b], q_np[c], d_cyc)
                if (a, b, c) in sec_set:
                    assert np.any(proj != 0)
                else:
                    assert np.all(proj == 0)

    for a, b, c in sectors:
        d_secs.append(np.einsum("ia,jb,kc,abc->ijk", q_np[a], q_np[b], q_np[c], d_cyc).ravel())
    m19 = np.vstack(d_secs)
    g19 = m19 @ m19.T
    expected_diag = [4096] + [36864] * 9 + [147456] * 3 + [110592] * 6
    assert np.array_equal(g19, np.diag(expected_diag))

    probe_cols = {"0": 3, "sd": 0, "asd": 0, "ric": 4}
    probe_nz_counts: Dict[str, int] = {}
    probe_nonzero_blocks: Dict[str, List[Tuple[str, str, int]]] = {}
    for nm, col_idx in probe_cols.items():
        v = q_np[nm][:, col_idx]
        mv = np.tensordot(v, d_cyc, axes=([0], [0]))
        nz_list = []
        z_cnt = 0
        for b in ("0", "sd", "asd", "ric"):
            for c in ("0", "sd", "asd", "ric"):
                blk = q_np[b] @ mv @ q_np[c]
                n2 = int(np.sum(blk * blk))
                if n2 != 0:
                    nz_list.append((b, c, n2))
                else:
                    z_cnt += 1
        assert len(nz_list) + z_cnt == 16
        probe_nz_counts[nm] = len(nz_list)
        probe_nonzero_blocks[nm] = nz_list
    assert probe_nz_counts == {"0": 4, "sd": 5, "asd": 5, "ric": 5}

    def vec19(x: Dict[str, int], y: Dict[str, int], z: Dict[str, int]) -> List[int]:
        return [x[a] * y[b] * z[c] for (a, b, c) in sectors]

    e_0 = {"0": 1, "sd": 0, "asd": 0, "ric": 0}
    e_p = {"0": 0, "sd": 1, "asd": 1, "ric": 1}
    e_ch_p = {"0": 0, "sd": 1, "asd": 1, "ric": 0}
    e_r = {"0": 0, "sd": 0, "asd": 0, "ric": 1}
    e_sd = {"0": 0, "sd": 1, "asd": 0, "ric": 0}
    e_asd = {"0": 0, "sd": 0, "asd": 1, "ric": 0}
    full4 = [e_0, e_sd, e_asd, e_r]
    even3 = [e_0, e_ch_p, e_r]

    st0 = [v for v in (vec19(x, y, z) for x in [e_0, e_p] for y in [e_0, e_p] for z in [e_0, e_p]) if any(v)]
    st1 = [[1 if j == i else 0 for j in range(19)] for i in range(10)] + [[1 if j >= 10 else 0 for j in range(19)]]
    st2 = [v for v in (vec19(x, y, z) for x in even3 for y in even3 for z in even3) if any(v)]
    st3 = [v for v in (vec19(x, y, z) for x in full4 for y in full4 for z in full4) if any(v)]

    def ind_vec(idxs: List[int]) -> List[int]:
        return [1 if j in idxs else 0 for j in range(19)]

    st12_inter = [
        ind_vec([0]), ind_vec([1, 2]), ind_vec([3]), ind_vec([4, 5]),
        ind_vec([6]), ind_vec([7, 8]), ind_vec([9]), ind_vec(list(range(10, 19))),
    ]
    st12_join = [ind_vec([j]) for j in range(10)] + [
        ind_vec([10, 11]), ind_vec([12]), ind_vec([13, 15]),
        ind_vec([14, 16]), ind_vec([17, 18]),
    ]

    for basis in (st0, st12_inter, st1, st2, st12_join, st3):
        assert all(
            sum(a * b for a, b in zip(basis[i], basis[j])) == 0
            for i in range(len(basis))
            for j in range(i + 1, len(basis))
        )
    assert [len(st0), len(st12_inter), len(st1), len(st2), len(st12_join), len(st3)] == [5, 8, 11, 12, 15, 19]
    # Verify exact closure diamond inclusions: st0 <= st12_inter <= {st1, st2} <= st12_join <= st3
    for sub, sup in (
        (st0, st12_inter),
        (st12_inter, st1),
        (st12_inter, st2),
        (st1, st12_join),
        (st2, st12_join),
        (st12_join, st3),
    ):
        assert int(sp.Matrix(sub + sup).rank()) == len(sup)

    # Verify st1 spans pairwise pullbacks
    st1_gen = (
        list(st0)
        + [vec19(e_0, y, z) for y in full4 for z in full4]
        + [vec19(x, e_0, z) for x in full4 for z in full4]
        + [vec19(x, y, e_0) for x in full4 for y in full4]
    )
    assert int(sp.Matrix(st1_gen).rank()) == 11
    assert int(sp.Matrix(st1 + st1_gen).rank()) == 11

    sw = {"0": "0", "ric": "ric", "sd": "asd", "asd": "sd"}
    odd7 = []
    for idx, (a, b, c) in enumerate(sectors):
        jdx = sectors.index((sw[a], sw[b], sw[c]))
        if idx < jdx:
            v = [1 if k == idx else (-1 if k == jdx else 0) for k in range(19)]
            odd7.append(v)
    assert len(odd7) == 7
    for ov in odd7:
        for ev in st2:
            assert sum(a * b for a, b in zip(ov, ev)) == 0
    odd4_triple = [v for v in odd7 if sum(abs(x) for x in v[10:]) > 0]
    assert len(odd4_triple) == 4
    for ov in odd4_triple:
        for jv in st12_join:
            assert sum(a * b for a, b in zip(ov, jv)) == 0

    # 4. Hodge (3,3) derivation vanishing, 81^3 = 729*729 boost scaling, and 12+7 parity split
    for g in all_gens:
        dg = np.array(ext2_action(g, pairs28).tolist(), dtype=np.int64)
        res = (
            np.einsum("ia,ajk->ijk", dg, d_cyc)
            + np.einsum("jb,ibk->ijk", dg, d_cyc)
            + np.einsum("kc,ijc->ijk", dg, d_cyc)
        )
        assert np.all(res == 0)

    j_mum3 = sp.kronecker_product(sp.Matrix([[4, 5], [-5, -4]]), sp.eye(4))
    g_sl2_3 = sp.Matrix([[5, 4], [4, 5]])
    q_4_3 = sp.Matrix([[1, -2, -2, 0], [2, 1, 0, -2], [2, 0, 1, 2], [0, 2, -2, 1]])
    g_mum9 = sp.kronecker_product(g_sl2_3, q_4_3)
    d2_j3 = np.array(ext2_action(j_mum3, pairs28).tolist(), dtype=np.int64)
    w_sl2 = np.array(wedge2_group(sp.kronecker_product(g_sl2_3, sp.eye(4)), pairs28).tolist(), dtype=np.int64)
    w_q4 = np.array(wedge2_group(sp.kronecker_product(sp.eye(2), q_4_3), pairs28).tolist(), dtype=np.int64)
    w2_g9 = np.array(wedge2_group(g_mum9, pairs28).tolist(), dtype=np.int64)
    assert np.array_equal(w2_g9, w_sl2 @ w_q4)
    deriv_j3 = (
        np.einsum("ia,ajk->ijk", d2_j3, d_cyc)
        + np.einsum("jb,ibk->ijk", d2_j3, d_cyc)
        + np.einsum("kc,ijc->ijk", d2_j3, d_cyc)
    )
    assert np.all(deriv_j3 == 0)
    assert np.array_equal(np.einsum("ia,jb,kc,abc->ijk", w_sl2, w_sl2, w_sl2, d_cyc), 729 * d_cyc)
    assert np.array_equal(np.einsum("ia,jb,kc,abc->ijk", w_q4, w_q4, w_q4, d_cyc), 729 * d_cyc)
    boost_d_cyc = np.einsum("ia,jb,kc,abc->ijk", w2_g9, w2_g9, w2_g9, d_cyc)
    assert np.array_equal(boost_d_cyc, (81**3) * d_cyc)

    refl4 = sp.kronecker_product(sp.eye(2), sp.diag(1, 1, 1, -1))
    p_flip = np.array(wedge2_group(refl4, pairs28).tolist(), dtype=np.int64)
    assert np.array_equal(p_flip, np.diag(np.diag(p_flip)))
    assert np.array_equal(np.einsum("ia,jb,kc,abc->ijk", p_flip, p_flip, p_flip, d_cyc), d_cyc)

    fixed_cnt = sum(1 for a, b, c in sectors if (sw[a], sw[b], sw[c]) == (a, b, c))
    swapped_cnt = len(odd7)
    assert fixed_cnt == 5 and swapped_cnt == 7

    report = {
        "h4_70dim_invariant_uniqueness": {
            "dim_h4_invariants": 1,
            "drop_col": drop_col,
            "b69_det": det69,
            "b69_inv_scale": scale69,
            "b69_inv_nnz": nnz_b69_inv,
            "b69_inv_max_abs": max_abs_b69_inv,
        },
        "a3_small_diagonal_divisor_identity": {
            "t_cup_up_nnz": 360,
            "d_cyc_nnz": 340,
            "d_cyc_norm2": 352,
            "s3_totally_symmetric": True,
            "identity_8_tcup_holds_all_21952": True,
            "sym3_ns_rank": 5,
            "sym3_ns_plus_tcup_rank": 5,
        },
        "a3_19sector_and_closure_ladder": {
            "casimir_poly_reconstruction_exact": True,
            "nonzero_sectors": 19,
            "zero_sectors": 45,
            "gram19_diagonal_values": expected_diag,
            "probe_nonzero_counts": probe_nz_counts,
            "probe_nonzero_blocks": probe_nonzero_blocks,
            "closure_diamond_dims": {
                "stage0_div": 5,
                "stage1_pairwise": 11,
                "stage2_even": 12,
                "stage1_inter_2": 8,
                "stage1_join_2": 15,
                "stage3_full": 19,
            },
            "odd7_orthogonal_to_stage2_12": True,
            "odd4_triple_orthogonal_to_join15": True,
        },
        "a3_hodge33_moduli_and_parity": {
            "all_9_gens_kill_d_cyc": True,
            "d2_j_mum3_kills_d_cyc": True,
            "boost_factorization_729x729_exact": True,
            "w2_g_mum9_scales_d_cyc_531441": True,
            "p_flip_x3_fixes_d_cyc": True,
            "sector_parity_split": {"fixed": 5, "swapped_pairs": 7, "even": 12, "odd": 7},
        },
    }

    b69_sparse_rows = [
        [(c, int(b69_inv_int[r, c])) for c in range(69) if b69_inv_int[r, c] != 0]
        for r in range(69)
    ]
    lean_data = {
        "drop_col": drop_col,
        "b69_labels": b69_labels,
        "b69_inv_sparse_rows": b69_sparse_rows,
    }
    return report, lean_data


def main() -> int:
    report, _ = run_mumford_triple_product_experiment()
    out_dir = Path(__file__).resolve().parents[2] / "reports" / "millennium_ext"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "mumford_triple_product_hodge33.json"
    out_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"MUMFORD_TRIPLE_PRODUCT_HODGE33_VERIFIED: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
