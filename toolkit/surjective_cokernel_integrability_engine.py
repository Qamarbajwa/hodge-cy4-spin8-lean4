r"""Surjective Cokernel Annihilation & Rank-Independent All-Order Integrability Engine (Event 27).

Formalizes three exact structural theorems on the Fermat sextic Calabi-Yau fourfold
X^4_6 \subset \mathbb{P}^5 under first-order and all-order complex deformations
F_t = F_0 + t u with u \in R^6(F_0):

1. SurjectiveCokernelAnnihilationEngine:
   For the symmetry-breaking 9-partition direction u_{dense} \in R^6(F_0),
   rk(M_{u_{dense}} : R^{12}(F_0) -> R^{18}(F_0)) = 426 = \dim R^{18}(F_0),
   so \dim \operatorname{coker}(M_{u_{dense}}) = 0. Therefore every higher-order
   Gauss-Manin obstruction [S^{(k)}(u_{dense})] \in \operatorname{coker}(M_{u_{dense}}) = {0}
   vanishes identically for all k >= 2 across all 1,325 kernel basis vectors.
   Constructively extracts explicit recursive Koszul lifts (Lambda_1, Lambda_2, A^{(1)}, A^{(2)}, A^{(3)})
   through Orders 1..3 for deterministic kernel basis vectors.

2. RankIndependentSecondOrderEngine:
   For any monomial x^b \in R^6(F_0), exact Rank-Nullity yields
     dim ker(M_{x^b}) - dim coker(M_{x^b}) = (1751 - r) - (426 - r) = 1325.
   Evaluates Psi^{(2)}_{x^b} : \ker(M_{x^b}) -> \operatorname{coker}(M_{x^b}) across
   all 9 unordered monomial partitions (and all 426 monomials in R^6(F_0)),
   confirming \dim \ker(Psi^{(2)}_{x^b}) >= 1,325 across all 426 monomials.

3. FormalHodgeSeriesToHilbertAudit:
   Records the certified formal power series integrability theorem on the Zariski-open
   surjective locus while preserving the open Hilbert-scheme degree stabilization boundary
   on global Bridge A (S-BRIDGE-DEFORM-CY4).

Zero floating-point constructs: 100% exact integers, tuples, and fractions.Fraction.
"""

from __future__ import annotations

from collections import Counter
from fractions import Fraction
from pathlib import Path
import sys
from typing import Any, Dict, List, Optional, Tuple

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from toolkit.calabi_yau_jacobian_engine import CalabiYauJacobianEngine
from toolkit.higher_order_gauss_manin_sieve import (
    GaussManinJetTower,
    Monomial,
    PolyDict,
    _SparseTrackedSpan,
    poly_add,
    poly_mod_jacobian,
    poly_mul,
    poly_neg,
    poly_partial,
    poly_sub,
)
from toolkit.integrity import scan_forbidden
from toolkit.universal_obstruction_cancellation_engine import REPS_9_SHIFTED


# ==============================================================================
# MODULE 1: SURJECTIVE COKERNEL ANNIHILATION & ALL-ORDER RECURSIVE LIFT
# ==============================================================================


class SurjectiveCokernelAnnihilationEngine:
    """Proves coker(M_{u_dense}) = {0} and solves Orders 1..3 recursively."""

    def __init__(self, tower: Optional[GaussManinJetTower] = None) -> None:
        self.tower = tower if tower is not None else GaussManinJetTower()
        self.u_dense: PolyDict = {
            r: Fraction(idx + 1, 1) for idx, r in enumerate(REPS_9_SHIFTED)
        }

    def run_audit(self, sample_count: int = 6) -> Dict[str, Any]:
        """Builds the tracked surjective span and extracts recursive lifts."""
        cols: List[Tuple[int, Monomial, Dict[int, Fraction]]] = []
        for a in self.tower.m12:
            prod_mod = poly_mod_jacobian(
                poly_mul({a: Fraction(1, 1)}, self.u_dense),
                self.tower.jac_deg,
            )
            vec = {self.tower.m18_idx[m]: c for m, c in prod_mod.items()}
            cols.append((len(vec), a, vec))

        # Sparsity sorting keeps elimination exact and rapid over Q
        cols.sort(key=lambda item: (item[0], item[1]))

        span = _SparseTrackedSpan()
        monomial_ker_vectors: List[PolyDict] = []
        multi_term_ker_vectors: List[PolyDict] = []
        ker_count = 0

        for _, a, vec in cols:
            rem, combo = span._reduce(vec)
            if not rem:
                ker_count += 1
                lam0: PolyDict = {a: Fraction(1, 1)}
                for col_id, coeff in combo.items():
                    if coeff != 0:
                        _, mono = span.labels[col_id]
                        nv = lam0.get(mono, Fraction(0, 1)) - coeff
                        if nv == 0:
                            lam0.pop(mono, None)
                        else:
                            lam0[mono] = nv
                if len(lam0) == 1:
                    monomial_ker_vectors.append(lam0)
                else:
                    multi_term_ker_vectors.append(lam0)
            else:
                span.add_column(("lam", a), vec)

        rk = span.rank
        dim_r18 = len(self.tower.m18)
        coker_dim = dim_r18 - rk
        assert dim_r18 == 426
        assert rk == 426
        assert coker_dim == 0
        assert ker_count == 1325
        assert len(monomial_ker_vectors) + len(multi_term_ker_vectors) == 1325

        # Deterministically sample both pure-monomial and multi-term kernel vectors
        half = sample_count // 2
        selected: List[PolyDict] = (
            monomial_ker_vectors[:half]
            + multi_term_ker_vectors[: sample_count - half]
        )
        if len(selected) < sample_count:
            pool = monomial_ker_vectors[half:] + multi_term_ker_vectors[sample_count - half :]
            selected.extend(pool[: sample_count - len(selected)])
        assert len(selected) == sample_count

        sample_lift_records: List[Dict[str, Any]] = []
        all_exact = True

        for idx, lam0 in enumerate(selected):
            # Order 1 (t^0): u * lam0 = sum_{i=0}^5 A^{(1)}_i x_i^5
            u_lam0 = poly_mul(self.u_dense, lam0)
            assert not poly_mod_jacobian(u_lam0, self.tower.jac_deg)
            A1 = self.tower.extract_koszul_syzygy(u_lam0)
            assert self.tower.reconstruct_from_syzygy(A1) == u_lam0

            # Order 2 (t^1): S^{(2)} = sum A^{(1)}_i d_i u, M_u(lam1) = S^{(2)} mod J_18
            S2 = self.tower.contract_with_du(A1, self.u_dense)
            S2_mod = poly_mod_jacobian(S2, self.tower.jac_deg)
            s2_vec = {self.tower.m18_idx[m]: c for m, c in S2_mod.items()}
            ok2, sol2 = span.solve(s2_vec)
            assert ok2
            lam1: PolyDict = {
                mono: coeff for (_, mono), coeff in sol2.items() if coeff != 0
            }
            R2 = poly_sub(S2, poly_mul(self.u_dense, lam1))
            assert not poly_mod_jacobian(R2, self.tower.jac_deg)
            A2 = self.tower.extract_koszul_syzygy(poly_neg(R2))
            order2_exact = poly_mul(self.u_dense, lam1) == poly_add(
                self.tower.reconstruct_from_syzygy(A2), S2
            )
            assert order2_exact

            # Order 3 (t^2): S^{(3)} = sum A^{(2)}_i d_i u, M_u(lam2) = S^{(3)} mod J_18
            S3 = self.tower.contract_with_du(A2, self.u_dense)
            S3_mod = poly_mod_jacobian(S3, self.tower.jac_deg)
            s3_vec = {self.tower.m18_idx[m]: c for m, c in S3_mod.items()}
            ok3, sol3 = span.solve(s3_vec)
            assert ok3
            lam2: PolyDict = {
                mono: coeff for (_, mono), coeff in sol3.items() if coeff != 0
            }
            R3 = poly_sub(S3, poly_mul(self.u_dense, lam2))
            assert not poly_mod_jacobian(R3, self.tower.jac_deg)
            A3 = self.tower.extract_koszul_syzygy(poly_neg(R3))
            order3_exact = poly_mul(self.u_dense, lam2) == poly_add(
                self.tower.reconstruct_from_syzygy(A3), S3
            )
            assert order3_exact

            if not (order2_exact and order3_exact):
                all_exact = False

            sample_lift_records.append(
                {
                    "sample_index": idx,
                    "lam0_terms": len(lam0),
                    "lam1_terms": len(lam1),
                    "lam2_terms": len(lam2),
                    "order1_syzygy_terms": sum(len(p) for p in A1),
                    "order2_syzygy_terms": sum(len(p) for p in A2),
                    "order3_syzygy_terms": sum(len(p) for p in A3),
                    "orders_1_2_3_exact": order2_exact and order3_exact,
                }
            )

        assert all_exact is True

        return {
            "dense_u_rank": rk,
            "dim_R18": dim_r18,
            "dense_u_cokernel_dim": coker_dim,
            "dense_u_surjective": coker_dim == 0,
            "dense_u_kernel_dim": ker_count,
            "monomial_kernel_vectors_count": len(monomial_ker_vectors),
            "multi_term_kernel_vectors_count": len(multi_term_ker_vectors),
            "all_order_unobstructed_kernel_dim": ker_count,
            "recursive_sample_vectors_tested": len(sample_lift_records),
            "recursive_orders_1_2_3_all_exact": all_exact,
            "sample_lift_records": sample_lift_records,
        }


# ==============================================================================
# MODULE 2: RANK-INDEPENDENT SECOND-ORDER CANCELLATION ENGINE
# ==============================================================================


class RankIndependentSecondOrderEngine:
    """Computes exact Rank-Nullity and second-order Psi^(2) kernel dimensions across 9 partitions and 426 monomials."""

    def __init__(self, cy_engine: Optional[CalabiYauJacobianEngine] = None) -> None:
        self.cy = cy_engine if cy_engine is not None else CalabiYauJacobianEngine()
        self.m6: List[Monomial] = [tuple(m) for m in self.cy.generate_monomial_basis(6)]  # type: ignore[misc]
        self.m12: List[Monomial] = [tuple(m) for m in self.cy.generate_monomial_basis(12)]  # type: ignore[misc]
        self.m18: List[Monomial] = [tuple(m) for m in self.cy.generate_monomial_basis(18)]  # type: ignore[misc]
        self.m18_set = set(self.m18)

    def _evaluate_monomial_psi2(self, b: Monomial) -> Dict[str, Any]:
        """Computes exact rk(M_{x^b}), coker(M_{x^b}), and Psi^{(2)}_{x^b} rank."""
        im_b = set()
        ker_monomials: List[Monomial] = []
        for a in self.m12:
            ab = (
                a[0] + b[0],
                a[1] + b[1],
                a[2] + b[2],
                a[3] + b[3],
                a[4] + b[4],
                a[5] + b[5],
            )
            if ab in self.m18_set:
                im_b.add(ab)
            else:
                ker_monomials.append(a)

        r = len(im_b)
        ker_m_dim = len(self.m12) - r
        coker_m_dim = len(self.m18) - r
        assert ker_m_dim - coker_m_dim == 1325

        # Since x^b is a single monomial and x^a in ker(M_{x^b}) is a monomial,
        # S^{(2)}(x^a, x^b) = b_{i_0} * x^{a + 2b - 6 e_{i_0}} is a single scalar * monomial,
        # so its projection to coker(M_{x^b}) spans distinct monomial classes directly.
        coker_hits = set()
        for a in ker_monomials:
            ab = (
                a[0] + b[0],
                a[1] + b[1],
                a[2] + b[2],
                a[3] + b[3],
                a[4] + b[4],
                a[5] + b[5],
            )
            i0 = next(i for i in range(6) if ab[i] >= 5)
            if b[i0] == 0:
                continue
            s2 = (
                a[0] + 2 * b[0] - (6 if i0 == 0 else 0),
                a[1] + 2 * b[1] - (6 if i0 == 1 else 0),
                a[2] + 2 * b[2] - (6 if i0 == 2 else 0),
                a[3] + 2 * b[3] - (6 if i0 == 3 else 0),
                a[4] + 2 * b[4] - (6 if i0 == 4 else 0),
                a[5] + 2 * b[5] - (6 if i0 == 5 else 0),
            )
            if s2 in self.m18_set and s2 not in im_b:
                coker_hits.add(s2)

        psi2_rank = len(coker_hits)
        assert psi2_rank <= coker_m_dim
        ker_psi2_dim = ker_m_dim - psi2_rank
        assert ker_psi2_dim >= 1325

        return {
            "monomial": b,
            "partition": tuple(sorted(b, reverse=True)),
            "rank": r,
            "ker_M_dim": ker_m_dim,
            "coker_M_dim": coker_m_dim,
            "psi2_rank": psi2_rank,
            "ker_psi2_dim": ker_psi2_dim,
        }

    def run_audit(self) -> Dict[str, Any]:
        # 1. Exact Rank-Nullity index check across all 9 partitions and 426 monomials in R^6(F_0)
        part_counts = Counter(tuple(sorted(b, reverse=True)) for b in self.m6)
        assert len(part_counts) == 9

        partition_records: List[Dict[str, Any]] = []
        for rep in REPS_9_SHIFTED:
            rec = self._evaluate_monomial_psi2(rep)
            rec["multiplicity"] = part_counts[rec["partition"]]
            partition_records.append(rec)

        ranks_list = [rec["rank"] for rec in partition_records]
        coker_dims = [rec["coker_M_dim"] for rec in partition_records]
        psi2_ranks = [rec["psi2_rank"] for rec in partition_records]
        ker_psi2_dims = [rec["ker_psi2_dim"] for rec in partition_records]

        assert ranks_list == [155, 165, 207, 248, 264, 279, 297, 316, 336]
        assert coker_dims == [271, 261, 219, 178, 162, 147, 129, 110, 90]
        assert psi2_ranks == [52, 93, 0, 31, 55, 30, 48, 71, 90]
        assert ker_psi2_dims == [1544, 1493, 1544, 1472, 1432, 1442, 1406, 1364, 1325]

        # 3. Exhaustive check across all 426 monomials in R^6(F_0)
        all_monomial_min_ker_psi2 = 1751
        all_monomial_max_ker_psi2 = 0
        count_ge_1325 = 0
        index_diff_all_exact = True
        for b in self.m6:
            rec = self._evaluate_monomial_psi2(b)
            if rec["ker_M_dim"] - rec["coker_M_dim"] != 1325:
                index_diff_all_exact = False
            kp = rec["ker_psi2_dim"]
            if kp >= 1325:
                count_ge_1325 += 1
            if kp < all_monomial_min_ker_psi2:
                all_monomial_min_ker_psi2 = kp
            if kp > all_monomial_max_ker_psi2:
                all_monomial_max_ker_psi2 = kp

        assert index_diff_all_exact is True
        assert count_ge_1325 == len(self.m6) == 426
        assert all_monomial_min_ker_psi2 == 1325
        assert all_monomial_max_ker_psi2 == 1544

        return {
            "rank_nullity_index_exact_for_all_426": index_diff_all_exact,
            "universal_cancellation_lower_bound": 1325,
            "partitions_count": len(partition_records),
            "partition_ranks": ranks_list,
            "partition_coker_dims": coker_dims,
            "partition_psi2_ranks": psi2_ranks,
            "partition_ker_psi2_dims": ker_psi2_dims,
            "partition_records": partition_records,
            "all_426_monomials_checked": len(self.m6),
            "all_426_monomials_ge_1325_count": count_ge_1325,
            "min_ker_psi2_dim": all_monomial_min_ker_psi2,
            "max_ker_psi2_dim": all_monomial_max_ker_psi2,
        }


# ==============================================================================
# MODULE 3: FORMAL HODGE SERIES TO HILBERT DEGREE BOUND HONESTY AUDIT
# ==============================================================================


class FormalHodgeSeriesToHilbertAudit:
    """Separates proven all-order formal cohomology integrability from Hilbert degree bounds."""

    def run_audit(self) -> Dict[str, Any]:
        return {
            "zariski_open_surjective_locus_exists": True,
            "formal_power_series_integrable_dim": 1325,
            "rank_independent_order2_lower_bound": 1325,
            "cdk_1995_hodge_locus_algebraic_in_moduli": True,
            "global_non_fermat_hilbert_stabilization_proved": False,
            "effective_hilbert_degree_bound_known": False,
            "global_hodge_conjecture": "OPEN",
            "release_authorized": False,
        }


# ==============================================================================
# FACADE ENGINE
# ==============================================================================


class SurjectiveCokernelIntegrabilityEngine:
    """Unified Event 27 verification facade."""

    def __init__(self) -> None:
        self.surj = SurjectiveCokernelAnnihilationEngine()
        self.rank_indep = RankIndependentSecondOrderEngine()
        self.honesty = FormalHodgeSeriesToHilbertAudit()

    def run_full_audit(self, sample_count: int = 6) -> Dict[str, Any]:
        surj_res = self.surj.run_audit(sample_count=sample_count)
        rank_res = self.rank_indep.run_audit()
        honesty_res = self.honesty.run_audit()
        return {
            "surjective_cokernel": surj_res,
            "rank_independent_second_order": rank_res,
            "formal_to_hilbert_honesty": honesty_res,
            "scan_forbidden_violations": scan_forbidden(__file__),
        }


if __name__ == "__main__":
    engine = SurjectiveCokernelIntegrabilityEngine()
    report = engine.run_full_audit()
    sc = report["surjective_cokernel"]
    ri = report["rank_independent_second_order"]
    hn = report["formal_to_hilbert_honesty"]
    print("=== SURJECTIVE COKERNEL ANNIHILATION & ALL-ORDER INTEGRABILITY ENGINE (EVENT 27) ===")
    print(
        f"Surjective Cokernel: rk(M_u)={sc['dense_u_rank']}/{sc['dim_R18']}, "
        f"coker={sc['dense_u_cokernel_dim']}, ker={sc['dense_u_kernel_dim']}, "
        f"samples={sc['recursive_sample_vectors_tested']} (Orders 1..3 exact={sc['recursive_orders_1_2_3_all_exact']})"
    )
    print(
        f"Rank-Nullity & Psi^(2): index_diff=1325 ({ri['rank_nullity_index_exact_for_all_426']}), "
        f"9 partitions coker={ri['partition_coker_dims']}, "
        f"ker(Psi^2)={ri['partition_ker_psi2_dims']}, "
        f"all 426 monomials >=1325 ({ri['all_426_monomials_ge_1325_count']}/426)"
    )
    print(
        f"Honesty Boundary: formal_integrable={hn['formal_power_series_integrable_dim']}, "
        f"hilbert_stabilization={hn['global_non_fermat_hilbert_stabilization_proved']}, "
        f"GLOBAL_HODGE={hn['global_hodge_conjecture']}, scan_forbidden={report['scan_forbidden_violations']}"
    )
