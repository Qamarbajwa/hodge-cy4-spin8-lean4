"""Experiment 14 (Wall 3): Tensor-Cube Gram, Universal Sp(8) Schur Complement,
Cl(0,7) Half-Spinor Generation of 7_-, and Negative Spin(2,4) Separation on A^3.

Certifies with exact SymPy / int64 arithmetic on H^2(A)^{otimes 3} (dim 21,952):
  1. Exact 19x19 Tensor-Cube Gram Matrix & 12_+ (+) 7_- Schur Complement:
     - On the 19 Mumford-invariant sectors of D_cyc, Gram_19 is diagonal:
       diag([4096] + [36864]*9 + [147456]*3 + [110592]*6).
     - Every class in the 12-dim parity-even subspace 12_+ (including 5-dim Sym^3 NS and
       T_cup_up) has identically 0 inner product with all 7 parity-odd classes in 7_-.
     - The Schur complement of 12_+ in Gram(12_+ U 7_-) is diag(73728, 73728, 73728,
       294912, 221184, 221184, 221184) (4096-normalized: diag(18, 18, 18, 72, 54, 54, 54)).
  2. Cl(0,7) Half-Spinor Casimir Generation of the 7_- Schur Complement:
     - Replacing T_ch by the Cl(0,7) bivector Casimir difference DeltaC = C_+ - C_- = -T_ch
       on 1 or 3 legs of D_cyc generates all 7 parity-odd classes of 7_- (rank 7).
  3. Negative Kuga-Satake Spin(2,4) Separation on A^3:
     - Under the diagonal Lie action D^(3)(g) of the 15-dim spin(2,4) = su(2,2) algebra,
       13 of 15 generators fail to preserve the 7_- Cl(0,7) Schur complement on A^3.

Outputs: reports/millennium_ext/clifford_triple_product_schur.json
"""

from __future__ import annotations

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
)


def _build_d_cyc(e_real: sp.Matrix, pairs28: List[Tuple[int, int]]) -> np.ndarray:
    e_np = np.array(e_real.tolist(), dtype=np.int64)
    p2i = {p: i for i, p in enumerate(pairs28)}
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
    assert int(np.count_nonzero(d_cyc)) == 340
    assert int(np.sum(d_cyc * d_cyc)) == 352
    return d_cyc


def run_clifford_triple_product_schur() -> Dict[str, Any]:
    data = build_mumford_real_generators()
    cas = verify_end_q_and_casimirs(data)
    e_real = data["E_real"]
    pairs28: List[Tuple[int, int]] = cas["tups2_8"]
    q0, q_sd, q_asd, q_ric = cas["projs"]
    i2 = sp.eye(2)
    i8 = sp.eye(8)
    h2 = sp.Matrix([[1, 0], [0, -1]])
    eps2 = sp.Matrix([[0, 1], [-1, 0]])

    d_cyc = _build_d_cyc(e_real, pairs28)
    q_np = {
        "0": np.array(q0.tolist(), dtype=np.int64),
        "sd": np.array(q_sd.tolist(), dtype=np.int64),
        "asd": np.array(q_asd.tolist(), dtype=np.int64),
        "ric": np.array(q_ric.tolist(), dtype=np.int64),
    }

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
    d_secs = [
        np.einsum("ia,jb,kc,abc->ijk", q_np[a], q_np[b], q_np[c], d_cyc).ravel()
        for a, b, c in sectors
    ]
    m19 = np.vstack(d_secs)  # 19 x 21952
    g19 = m19 @ m19.T
    expected_diag = [4096] + [36864] * 9 + [147456] * 3 + [110592] * 6
    assert np.array_equal(g19, np.diag(expected_diag))

    # 1. Exact 12_+ (+) 7_- orthogonal basis in R^{21952} and Schur complement
    even12_coeffs = np.array([
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1],
    ], dtype=np.int64)
    odd7_coeffs = np.array([
        [0, 1, -1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 1, -1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 1, -1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, -1, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, -1, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, -1, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, -1],
    ], dtype=np.int64)

    v_even12 = even12_coeffs @ m19  # 12 x 21952
    v_odd7 = odd7_coeffs @ m19     # 7 x 21952
    gram_12 = v_even12 @ v_even12.T
    gram_7 = v_odd7 @ v_odd7.T
    cross_12_7 = v_even12 @ v_odd7.T
    assert np.all(cross_12_7 == 0)

    expected_gram12 = [4096, 73728, 36864, 73728, 36864, 73728, 36864, 294912, 147456, 221184, 221184, 221184]
    expected_schur7 = [73728, 73728, 73728, 294912, 221184, 221184, 221184]
    assert np.array_equal(gram_12, np.diag(expected_gram12))
    assert np.array_equal(gram_7, np.diag(expected_schur7))

    # 2. Cl(0,7) Half-Spinor Casimir Generation of the 7_- Schur Complement
    jp = [
        sp.Matrix([[0, -1, 0, 0], [1, 0, 0, 0], [0, 0, 0, -1], [0, 0, 1, 0]]),
        sp.Matrix([[0, 0, -1, 0], [0, 0, 0, 1], [1, 0, 0, 0], [0, -1, 0, 0]]),
        sp.Matrix([[0, 0, 0, -1], [0, 0, -1, 0], [0, 1, 0, 0], [1, 0, 0, 0]]),
    ]
    jm = [
        sp.Matrix([[0, -1, 0, 0], [1, 0, 0, 0], [0, 0, 0, 1], [0, 0, -1, 0]]),
        sp.Matrix([[0, 0, -1, 0], [0, 0, 0, -1], [1, 0, 0, 0], [0, 1, 0, 0]]),
        sp.Matrix([[0, 0, 0, -1], [0, 0, 1, 0], [0, -1, 0, 0], [1, 0, 0, 0]]),
    ]
    biv_plus = [sp.kronecker_product(i2, g) for g in jp]
    biv_minus = [sp.kronecker_product(i2, g) for g in jm]
    c_plus = -sum((ext2_action(g, pairs28) ** 2 for g in biv_plus), sp.zeros(28, 28))
    c_minus = -sum((ext2_action(g, pairs28) ** 2 for g in biv_minus), sp.zeros(28, 28))
    delta_c = np.array((c_plus - c_minus).tolist(), dtype=np.int64)
    assert np.array_equal(delta_c, 2 * (q_np["sd"] - q_np["asd"]))

    i28_np = np.eye(28, dtype=np.int64)
    # Apply DeltaC = C_+ - C_- on 1 leg (with Q_0 or Q_ric) or 3 legs of D_cyc:
    cl07_odd_gens = [
        np.einsum("ia,jb,kc,abc->ijk", q_np["0"], delta_c, i28_np, d_cyc).ravel(),
        np.einsum("ia,jb,kc,abc->ijk", delta_c, q_np["0"], i28_np, d_cyc).ravel(),
        np.einsum("ia,jb,kc,abc->ijk", delta_c, i28_np, q_np["0"], d_cyc).ravel(),
        np.einsum("ia,jb,kc,abc->ijk", delta_c, delta_c, delta_c, d_cyc).ravel(),
        np.einsum("ia,jb,kc,abc->ijk", delta_c, i28_np, q_np["ric"], d_cyc).ravel(),
        np.einsum("ia,jb,kc,abc->ijk", delta_c, q_np["ric"], i28_np, d_cyc).ravel(),
        np.einsum("ia,jb,kc,abc->ijk", q_np["ric"], delta_c, i28_np, d_cyc).ravel(),
    ]
    for idx, gen in enumerate(cl07_odd_gens):
        if idx == 3:
            assert np.array_equal(gen, 8 * v_odd7[idx])
        else:
            assert np.array_equal(2 * gen, v_odd7[idx])

    # 3. Negative Kuga-Satake Spin(2,4) Separation on A^3
    j_c = sp.kronecker_product(eps2, sp.kronecker_product(h2, i2))
    vars64 = sp.symbols("x0:64")
    x_mat = sp.Matrix(8, 8, vars64)
    eqs = [x_mat.trace(), (j_c * x_mat).trace()]
    c1 = x_mat.T * e_real + e_real * x_mat
    c2 = x_mat * j_c - j_c * x_mat
    for i in range(8):
        for j in range(8):
            if c1[i, j] != 0:
                eqs.append(c1[i, j])
            if c2[i, j] != 0:
                eqs.append(c2[i, j])
    a_eq, _ = sp.linear_eq_to_matrix(eqs, vars64)
    su22_gens: List[sp.Matrix] = []
    for v in a_eq.nullspace():
        den = sp.lcm([sp.fraction(z)[1] for z in v])
        su22_gens.append(sp.Matrix(8, 8, [int(z * den) for z in v]))
    assert len(su22_gens) == 15
    d_su22 = [np.array(ext2_action(g, pairs28).tolist(), dtype=np.int64) for g in su22_gens]

    # Check how many of the 15 spin(2,4) generators fail to preserve 7_- under D^(3)(g)
    # Using exact orthogonal projector onto 7_-: v in span(v_odd7) iff (I - P_{7_-}) D^(3)(g) v == 0
    # Integer check: for each v_odd7[k], compute w = D^(3)(g) v_odd7[k];
    # w is in span(v_odd7) iff (v_odd7 @ v_odd7.T)^{-1} ... equivalently scale by lcm(expected_schur7):
    # w in span(v_odd7) iff L * w == sum_m (L / norm2_m) * <w, v_odd7[m]> * v_odd7[m]!
    v_odd_tensors = [v.reshape(28, 28, 28) for v in v_odd7]
    lcm_7 = 884736  # lcm(73728, 294912, 221184) = 884736
    assert all(lcm_7 % n2 == 0 for n2 in expected_schur7)
    weights_7 = [lcm_7 // n2 for n2 in expected_schur7]

    failing_spin24_a3 = 0
    for d in d_su22:
        preserves = True
        for vt in v_odd_tensors:
            w = (
                np.einsum("ia,abc->ibc", d, vt)
                + np.einsum("jb,abc->ajc", d, vt)
                + np.einsum("kc,abc->abk", d, vt)
            ).ravel()
            proj_num = np.zeros(21952, dtype=np.int64)
            for m_idx in range(7):
                dot_m = int(np.dot(w, v_odd7[m_idx]))
                proj_num += (weights_7[m_idx] * dot_m) * v_odd7[m_idx]
            if not np.array_equal(lcm_7 * w, proj_num):
                preserves = False
                break
        if not preserves:
            failing_spin24_a3 += 1

    assert failing_spin24_a3 == 13

    return {
        "tensor_cube_gram_and_schur": {
            "gram_19_diag": expected_diag,
            "gram_12_even_diag": expected_gram12,
            "schur_7_odd_diag": expected_schur7,
            "schur_7_odd_normalized_diag": [x // 4096 for x in expected_schur7],
            "cross_gram_12_7_is_zero": True,
        },
        "cl07_casimir_generation_of_7_minus": {
            "cl07_generators_span_rank": 7,
            "scale_factor_on_odd7": 8,
            "single_leg_generators": 6,
            "triple_leg_generators": 1,
        },
        "kuga_satake_spin24_a3_separation": {
            "spin24_lie_dim": 15,
            "spin24_gens_failing_7_minus_on_a3": failing_spin24_a3,
            "spin24_preserves_7_minus_on_a3": False,
        },
    }


def main() -> int:
    report = run_clifford_triple_product_schur()
    out_dir = Path(__file__).resolve().parents[2] / "reports" / "millennium_ext"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "clifford_triple_product_schur.json"
    out_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"CLIFFORD_TRIPLE_PRODUCT_SCHUR_VERIFIED: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
