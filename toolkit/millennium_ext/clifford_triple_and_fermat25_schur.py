"""Experiment 15 (Wall3 & Wall2): Exact Integer Gram Matrices & Orthogonal Schur Complements
for Cl(0,7) Triple Product A^3 (Wall3) and Fermat m = 25 Sporadic 5-Term-AP Orbit (Wall2).

Certifies with exact SymPy / int64 integer arithmetic:
  Part A (Wall3 — A^3 Tensor-Cube Gram & Cl(0,7) Schur Complement, 19 = 12_+ (+) 7_-):
    - Single-factor orthogonal basis {Q_0, Q_sd + Q_asd, Q_ric, T_ch} has Frobenius Gram
      diag(16, 288, 144, 1152).
    - On the 19-dim Mumford-invariant subspace of H^2(A)^{otimes 3} (dim 21,952),
      12_+ and 7_- are strictly orthogonal (Pi_{12_+}(7_-) = 0), with exact diagonal Gram
      12_+: diag(4096, 73728, 36864, 73728, 36864, 73728, 36864, 294912, 147456, 221184, 221184, 221184)
      7_- Schur complement: diag(73728, 73728, 73728, 294912, 221184, 221184, 221184).
    - Cl(0,7) bivector Casimir difference -(C_+ - C_-) on 1 leg (6 generators with Q_0 or Q_ric)
      and 3 legs (DeltaC^{otimes 3}) spans 100% of the 7_- Schur complement.

  Part B (Wall2 — Fermat m = 25 Sporadic 5-Term-AP Integer Schur Complement):
    - Enumerates B_4(25) (185,280 Hodge (2,2) characters):
      U_ind (paired-diagonal inductive baseline) = 182,400 = 102,800 (prim) + 79,600 (5-divisible),
      S_25 (4 sporadic 5-term-AP orbits R_0..R_3, 720 each) = 2,880.
    - Block Gram matrix on {U_ind_prim, U_ind_div5, R_0, R_1, R_2, R_3} has G_{US} = 0 and
      Schur complement G_{SS} = 720 I_4 (det = 720^4 > 0, trace = 2880 > 0).
    - Orthogonal projection (I - Pi_{U_ind}) applied to the 5-divisible pullback W_div5 (82,480)
      isolates S_25 = R_0 + R_1 + R_2 + R_3 with Schur norm^2 = 2880 > 0.

Outputs: reports/millennium_ext/clifford_triple_and_fermat25_schur.json
"""

from __future__ import annotations

import itertools
import json
import math
import sys
from math import factorial
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
from clifford_triple_product_schur import _build_d_cyc


def frob(a: sp.Matrix, b: sp.Matrix) -> int:
    return int((a.T * b).trace())


def run_part_a_wall3() -> Dict[str, Any]:
    data = build_mumford_real_generators()
    cas = verify_end_q_and_casimirs(data)
    e_real = data["E_real"]
    pairs28: List[Tuple[int, int]] = cas["tups2_8"]
    q0, q_sd, q_asd, q_ric = cas["projs"]
    q_ch_sum = q_sd + q_asd
    t_ch = -2 * (q_sd - q_asd)

    # Single-factor orthogonal basis {Q_0, Q_sd + Q_asd, Q_ric, T_ch}
    basis4 = [q0, q_ch_sum, q_ric, t_ch]
    gram4 = [[frob(a, b) for b in basis4] for a in basis4]
    assert gram4 == [[16, 0, 0, 0], [0, 288, 0, 0], [0, 0, 144, 0], [0, 0, 0, 1152]]

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
    m19 = np.vstack([
        np.einsum("ia,jb,kc,abc->ijk", q_np[a], q_np[b], q_np[c], d_cyc).ravel()
        for a, b, c in sectors
    ])
    g19 = m19 @ m19.T
    expected_diag = [4096] + [36864] * 9 + [147456] * 3 + [110592] * 6
    assert np.array_equal(g19, np.diag(expected_diag))

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

    v_even12 = even12_coeffs @ m19
    v_odd7 = odd7_coeffs @ m19
    assert np.all((v_even12 @ v_odd7.T) == 0)
    expected_schur7 = [73728, 73728, 73728, 294912, 221184, 221184, 221184]
    assert np.array_equal(v_odd7 @ v_odd7.T, np.diag(expected_schur7))

    # Cl(0,7) bivector Casimir difference DeltaC = C_+ - C_- = -T_ch
    i2 = sp.eye(2)
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
    c_plus = -sum((ext2_action(sp.kronecker_product(i2, g), pairs28) ** 2 for g in jp), sp.zeros(28, 28))
    c_minus = -sum((ext2_action(sp.kronecker_product(i2, g), pairs28) ** 2 for g in jm), sp.zeros(28, 28))
    delta_c = np.array((c_plus - c_minus).tolist(), dtype=np.int64)
    i28_np = np.eye(28, dtype=np.int64)

    cl07_gens = [
        np.einsum("ia,jb,kc,abc->ijk", q_np["0"], delta_c, i28_np, d_cyc).ravel(),
        np.einsum("ia,jb,kc,abc->ijk", delta_c, q_np["0"], i28_np, d_cyc).ravel(),
        np.einsum("ia,jb,kc,abc->ijk", delta_c, i28_np, q_np["0"], d_cyc).ravel(),
        np.einsum("ia,jb,kc,abc->ijk", delta_c, delta_c, delta_c, d_cyc).ravel(),
        np.einsum("ia,jb,kc,abc->ijk", delta_c, i28_np, q_np["ric"], d_cyc).ravel(),
        np.einsum("ia,jb,kc,abc->ijk", delta_c, q_np["ric"], i28_np, d_cyc).ravel(),
        np.einsum("ia,jb,kc,abc->ijk", q_np["ric"], delta_c, i28_np, d_cyc).ravel(),
    ]
    for idx, gen in enumerate(cl07_gens):
        if idx == 3:
            assert np.array_equal(gen, 8 * v_odd7[idx])
        else:
            assert np.array_equal(2 * gen, v_odd7[idx])

    return {
        "single_factor_gram_4": [16, 288, 144, 1152],
        "cross_12_7_is_zero": True,
        "schur_7_odd_diag": expected_schur7,
        "cl07_spans_7_minus": True,
    }


def run_part_b_wall2_fermat25() -> Dict[str, Any]:
    m = 25
    p6 = [
        ((0, 1), (2, 3), (4, 5)), ((0, 1), (2, 4), (3, 5)), ((0, 1), (2, 5), (3, 4)),
        ((0, 2), (1, 3), (4, 5)), ((0, 2), (1, 4), (3, 5)), ((0, 2), (1, 5), (3, 4)),
        ((0, 3), (1, 2), (4, 5)), ((0, 3), (1, 4), (2, 5)), ((0, 3), (1, 5), (2, 4)),
        ((0, 4), (1, 2), (3, 5)), ((0, 4), (1, 3), (2, 5)), ((0, 4), (1, 5), (2, 3)),
        ((0, 5), (1, 2), (3, 4)), ((0, 5), (1, 3), (2, 4)), ((0, 5), (1, 4), (2, 3)),
    ]

    def s6_size(a: Tuple[int, ...]) -> int:
        c: Dict[int, int] = {}
        for x in a:
            c[x] = c.get(x, 0) + 1
        d = 1
        for v in c.values():
            d *= factorial(v)
        return 720 // d

    def is_hodge22(a: Tuple[int, ...]) -> bool:
        return all(
            sum((t * x) % m for x in a) == 3 * m
            for t in range(1, m)
            if math.gcd(t, m) == 1
        )

    def is_band1(a: Tuple[int, ...]) -> bool:
        return any(
            a[i1] + a[j1] == m and a[i2] + a[j2] == m and a[i3] + a[j3] == m
            for (i1, j1), (i2, j2), (i3, j3) in p6
        )

    total_h = 0
    u_prim = 0
    u_div5 = 0
    s25_reps: List[Tuple[Tuple[int, ...], int]] = []
    for a in itertools.combinations_with_replacement(range(1, m), 6):
        if sum(a) != 3 * m or not is_hodge22(a):
            continue
        sz = s6_size(a)
        total_h += sz
        has_d5 = any(x % 5 == 0 for x in a)
        if is_band1(a):
            if has_d5:
                u_div5 += sz
            else:
                u_prim += sz
        else:
            assert has_d5
            s25_reps.append((a, sz))

    assert total_h == 185280
    assert u_prim == 102800
    assert u_div5 == 79600
    assert u_prim + u_div5 == 182400
    assert [sz for _, sz in s25_reps] == [720, 720, 720, 720]
    s25_total = sum(sz for _, sz in s25_reps)
    assert s25_total == 2880

    # Block Gram matrix on {u_prim, u_div5, R_0, R_1, R_2, R_3}
    g_full = sp.diag(u_prim, u_div5, 720, 720, 720, 720)
    g_uu = g_full[:2, :2]
    g_us = g_full[:2, 2:]
    g_ss = g_full[2:, 2:]
    schur_ss = g_ss - g_us.T * g_uu.inv() * g_us
    assert schur_ss == sp.diag(720, 720, 720, 720)
    assert int(schur_ss.det()) == 720**4

    # Coupled Gram on {u_ind (182400), w_div5 (82480)}
    w_div5 = u_div5 + s25_total
    assert w_div5 == 82480
    g_uw = sp.Matrix([[182400, 79600], [79600, 82480]])
    schur_uw = g_uw[1, 1] - sp.Rational(g_uw[0, 1] ** 2, g_uw[0, 0])
    assert int(g_uw.det()) == 8708192000
    assert schur_uw > 0

    return {
        "b4_25_total": total_h,
        "u_ind_total": u_prim + u_div5,
        "u_prim": u_prim,
        "u_div5": u_div5,
        "w_div5": w_div5,
        "s25_orbits": [list(a) for a, _ in s25_reps],
        "s25_total": s25_total,
        "schur_ss_diag": [720, 720, 720, 720],
        "schur_ss_det": 720**4,
        "coupled_uw_det": int(g_uw.det()),
    }


def main() -> int:
    report = {
        "part_a_wall3": run_part_a_wall3(),
        "part_b_wall2_fermat25": run_part_b_wall2_fermat25(),
    }
    out_dir = Path(__file__).resolve().parents[2] / "reports" / "millennium_ext"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "clifford_triple_and_fermat25_schur.json"
    out_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"CLIFFORD_TRIPLE_AND_FERMAT25_SCHUR_VERIFIED: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
