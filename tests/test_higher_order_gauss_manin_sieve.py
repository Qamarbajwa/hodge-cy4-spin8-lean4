"""Adversarial Reviewer Suite for Higher-Order Gauss-Manin Koszul Jet Tower & CDK Bridge A.

Tests:
  1. Exact Second-Order Koszul Syzygy Reconstruction: sum A^{(2)}_i(u) x_i^5 == -R^{(2)}(u) over all 407 kernel vectors of Pi and all 336 Order-2 survivors of lambda_stealth.
  2. All-Order 2-Plane Integrability Check: 56/56 canonical fixed-plane, 27/27 moving-plane, 54/54 linear (a_0+a_1+a_2=1), and 407/407 full kernel vectors satisfy Phi^(1) = Phi^(2) = Phi^(3) = 0.
  3. Stealth Class Caught at Order 3 Filtration: strict [347, 336, 334] hierarchy (fixed-J18 [347, 297, 295]) catching u_1=(1,1,0,1,2,1) & u_2=(1,1,2,1,0,1) at Order 3 with Phi^(2)=0.
  4. Adversarial Bridge A Audit: CDK_BASE_MODULI_ALGEBRAICITY_VERIFIED=True vs effective_hilbert_degree_bound_known=False blocks promotion to PROVED / CLOSED_VERIFIED.
  5. Zero-Float & 22/22 Zero-Axiom Lean 4.35.0 Kernel Check.
"""

import unittest
from fractions import Fraction
from pathlib import Path

from toolkit.higher_order_gauss_manin_sieve import (
    GaussManinJetTower,
    HigherOrderGaussManinEngine,
    poly_neg,
)
from toolkit.hodge_proof_closure_reviewer import (
    HodgeProofClosureReviewer,
    LEAN_THEOREM_SPECS,
)
from toolkit.integrity import scan_forbidden


class TestHigherOrderGaussManinSieve(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root = Path(__file__).resolve().parent.parent
        cls.engine = HigherOrderGaussManinEngine()
        cls.report = cls.engine.run_full_audit()

    def test_01_exact_second_order_syzygy_reconstruction(self):
        """Verifies exact unquotiented identity sum_{i=0}^5 A^(2)_i(u) x_i^5 == -R^(2)(u)."""
        tower = self.engine.tower

        # All 407 kernel vectors of the 2-plane cycle lambda_Pi = x_0^4 x_1^4 x_2^4
        lam_pi = {(4, 4, 4, 0, 0, 0): Fraction(1, 1)}
        im_pi = tower.build_im_span(lam_pi)
        im_mov_pi = tower.extend_span_with_v_mov_pi(im_pi)
        ker_pi = tower.ivhs_kernel_basis(lam_pi)
        self.assertEqual(len(ker_pi), 407)

        for u in ker_pi:
            res = tower.evaluate_jet_tower_for_vector(
                u,
                lam_pi,
                im_span=im_pi,
                allow_moving_plane_pi=True,
                im_mov_span=im_mov_pi,
            )
            self.assertTrue(res["a2_syzygy_reconstruction_exact"])
            self.assertEqual(
                tower.reconstruct_from_syzygy(res["A2_syzygy"]),
                poly_neg(res["R2_deg18"]),
            )

        # All 336 Order-2-unobstructed vectors of lambda_stealth
        lam_st = {(4, 3, 3, 2, 0, 0): Fraction(1, 1), (0, 3, 4, 1, 4, 0): Fraction(1, 1)}
        im_st = tower.build_im_span(lam_st)
        ker_st = tower.ivhs_kernel_basis(lam_st)
        reconstructed_st = 0
        for u in ker_st:
            res = tower.evaluate_jet_tower_for_vector(
                u,
                lam_st,
                im_span=im_st,
                allow_moving_plane_pi=False,
            )
            if res["order2_unobstructed"]:
                self.assertTrue(res["a2_syzygy_reconstruction_exact"])
                self.assertEqual(
                    tower.reconstruct_from_syzygy(res["A2_syzygy"]),
                    poly_neg(res["R2_deg18"]),
                )
                reconstructed_st += 1
        self.assertEqual(reconstructed_st, 336)

    def test_02_all_order_2plane_integrability_check(self):
        """Confirms 56/56 fixed, 27/27 moving, 54/54 linear, and 407/407 full kernel pass Order 3."""
        pl = self.report["plane_order3_audit"]
        self.assertEqual(pl["ivhs_rank"], 19)
        self.assertEqual(pl["K1_dim"], 407)
        self.assertEqual(pl["K2_dim"], 407)
        self.assertEqual(pl["K3_dim"], 407)
        self.assertEqual(pl["canonical_fixed_plane_total"], 56)
        self.assertEqual(pl["canonical_fixed_plane_s2_in_J18"], 56)
        self.assertEqual(pl["canonical_fixed_plane_s3_in_J18"], 56)
        self.assertEqual(pl["canonical_fixed_plane_order3_unobstructed"], 56)
        self.assertEqual(pl["moving_plane_27_total"], 27)
        self.assertEqual(pl["moving_plane_27_order3_unobstructed"], 27)
        self.assertEqual(pl["linear_moving_plane_54_total"], 54)
        self.assertEqual(pl["linear_moving_plane_54_order3_unobstructed"], 54)
        self.assertEqual(pl["a2_syzygy_reconstructions_verified"], 407)
        self.assertTrue(pl["plane_order3_all_407_unobstructed"])

    def test_03_stealth_class_caught_at_order_3_filtration(self):
        """Confirms strict filtration K^(1) > K^(2) > K^(3) and Order-3 stealth witnesses."""
        flt = self.report["jet_filtration_benchmark"]
        self.assertTrue(flt["strict_order3_hierarchy_demonstrated"])

        st = flt["stealth_class"]
        self.assertEqual(st["ivhs_rank"], 76)
        self.assertEqual(st["moving_cycle_filtration"], [347, 336, 334])
        self.assertEqual(st["strict_fixed_J18_filtration"], [347, 297, 295])
        self.assertEqual(st["pruned_at_order_2_count"], 11)
        self.assertEqual(st["caught_at_order_3_count"], 2)

        witnesses = {w["u_monomial"]: w for w in st["caught_at_order_3_witnesses"]}
        self.assertIn((1, 1, 0, 1, 2, 1), witnesses)
        self.assertIn((1, 1, 2, 1, 0, 1), witnesses)

        w1 = witnesses[(1, 1, 0, 1, 2, 1)]
        w2 = witnesses[(1, 1, 2, 1, 0, 1)]
        self.assertEqual(w1["order2_regime"], "fixed_j18")
        self.assertEqual(w2["order2_regime"], "fixed_j18")
        self.assertEqual(w1["S3_mod_jacobian"], {"(3, 0, 4, 4, 4, 3)": "-2"})
        self.assertEqual(w2["S3_mod_jacobian"], {"(3, 0, 4, 4, 4, 3)": "-2"})
        self.assertEqual((w1["base_rank"], w1["augmented_rank"]), (348, 349))
        self.assertEqual((w2["base_rank"], w2["augmented_rank"]), (332, 333))

        ch = flt["chain_class"]
        self.assertEqual(ch["ivhs_rank"], 68)
        self.assertEqual(ch["moving_cycle_filtration"], [342, 331, 331])
        self.assertEqual(ch["pruned_at_order_2_count"], 11)

    def test_04_adversarial_bridge_a_cdk_moduli_vs_fiber_audit(self):
        """Confirms CDK 1995 base-moduli algebraicity still blocks Bridge A without Hilbert degree bound."""
        cdk = self.report["cdk_bridge_a_audit"]
        self.assertEqual(cdk["bridge_a_status"], "ADVERSARIALLY_BLOCKED_OPEN_BRIDGE")
        self.assertTrue(cdk["CDK_BASE_MODULI_ALGEBRAICITY_VERIFIED"])
        self.assertFalse(cdk["effective_hilbert_degree_bound_known"])
        self.assertFalse(cdk["fiber_algebraic_cycle_constructed"])
        self.assertEqual(self.report["global_hodge_conjecture"], "OPEN")
        self.assertFalse(self.report["release_authorized"])
        self.assertEqual(self.report["theorem_progress"], "UNKNOWN")

        reviewer = HodgeProofClosureReviewer(repo_root=self.root)
        for bad_target in ("PROVED", "CLOSED_VERIFIED"):
            dec = reviewer.attempt_bridge_promotion(
                "S-BRIDGE-DEFORM-CY4",
                bad_target,
                "Since Phi^(k) = 0 for all k >= 1 and CDK 1995 proves Sigma_lambda is algebraic, X_t has a cycle.",
            )
            self.assertFalse(dec["accepted"])
            self.assertEqual(dec["verdict"], "REJECTED_BY_ADVERSARIAL_REVIEWER")
            self.assertEqual(dec["resulting_status"], "ADVERSARIALLY_BLOCKED_OPEN_BRIDGE")
            self.assertTrue(dec["audit_evidence"]["CDK_BASE_MODULI_ALGEBRAICITY_VERIFIED"])
            self.assertFalse(dec["audit_evidence"]["effective_hilbert_degree_bound_known"])

    def test_05_twenty_two_zero_axiom_lean4_theorems_and_zero_floats(self):
        """Verifies zero float violations and 22/22 zero-axiom Lean 4.35.0 proofs."""
        hits = scan_forbidden(str(self.root / "toolkit" / "higher_order_gauss_manin_sieve.py"))
        self.assertEqual(hits, [])

        reviewer = HodgeProofClosureReviewer(repo_root=self.root)
        lean = reviewer.verify_lean_blueprint(fast=True)
        self.assertTrue(lean["zero_cheating_clean"])
        self.assertTrue(lean["all_axioms_empty"])
        self.assertGreaterEqual(lean["theorems_verified_count"], 22)
        self.assertGreaterEqual(len(LEAN_THEOREM_SPECS), 22)
        self.assertEqual(lean["axioms_by_theorem"]["max_ivhs_monomial_rank_eq"], [])
        self.assertEqual(lean["axioms_by_theorem"]["canonical_fixed_plane_subspace_dim_eq"], [])


if __name__ == "__main__":
    unittest.main()
