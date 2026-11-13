"""Comprehensive unit & integration tests for Co-Scientist Dark Factory OS.

Includes:
1. All 27 reference gate-kernel fail-closed tests from COSCIENTIST_DF_v0_1.
2. Multi-agent workflow tests (Generation, Reflection, Proximity, Tournament, Evolution, Meta-Review).
3. MathProofAdapter integration tests verifying exact rational engines and Lean 4 blueprint compilation.
"""

import unittest
from toolkit.coscientist import (
    Denied,
    GateSignals,
    ResearchGateKernel,
    Stage,
    VerificationReceipt,
    digest,
    DarkFactoryEngine,
    ResearchGoal,
)
from toolkit.coscientist.agents import GenerationSpec


GOOD = GateSignals(True, True, True, True, True, True)


class ResearchGateTests(unittest.TestCase):
    def setUp(self):
        self.k = ResearchGateKernel()
        self.k.add("A", "If x, then y under bounded assumptions")

    def advance_to(self, item_id, target):
        for state in (
            Stage.SCREENED,
            Stage.GROUNDED,
            Stage.REVIEWED,
            Stage.ELIGIBLE,
            Stage.RANKED,
            Stage.PROPOSAL_READY,
        ):
            if self.k.get(item_id).stage == target:
                return
            self.k.advance(item_id, state, GOOD, caller="policy_service")

    def receipt(self, item="A", **kw):
        base = dict(
            hypothesis_id=item,
            exact_target_digest=self.k.get(item).content_digest,
            evidence_digest="a" * 64,
            claim_type="MATH_PROOF",
            builder_identity="builder-x",
            verifier_identity="separate-verifier",
            independently_verified=True,
            protected_suite_passed=True,
            semantic_review_passed=True,
            verifier_authority_bound=True,
        )
        base.update(kw)
        return VerificationReceipt(**base)

    def test_starts_draft_and_unverified(self):
        self.assertEqual(self.k.get("A").stage, Stage.DRAFT)
        self.assertFalse(self.k.proposal_is_verified("A"))

    def test_safe_adjacent_move(self):
        self.assertEqual(
            self.k.advance("A", Stage.SCREENED, GOOD, caller="policy_service").stage,
            Stage.SCREENED,
        )

    def test_no_agent_state_write(self):
        with self.assertRaises(Denied):
            self.k.advance("A", Stage.SCREENED, GOOD, caller="generation_agent")

    def test_no_skip_to_ranked(self):
        with self.assertRaises(Denied):
            self.k.advance("A", Stage.RANKED, GOOD, caller="policy_service")

    def test_no_missing_safety(self):
        with self.assertRaises(Denied):
            self.k.advance("A", Stage.SCREENED, GateSignals(), caller="policy_service")

    def test_missing_source(self):
        self.k.advance("A", Stage.SCREENED, GOOD, caller="policy_service")
        with self.assertRaises(Denied):
            self.k.advance("A", Stage.GROUNDED, GateSignals(True, True), caller="policy_service")

    def test_missing_reflection(self):
        self.advance_to("A", Stage.GROUNDED)
        with self.assertRaises(Denied):
            self.k.advance("A", Stage.REVIEWED, GateSignals(True, True, True), caller="policy_service")

    def test_missing_tournament(self):
        self.advance_to("A", Stage.ELIGIBLE)
        with self.assertRaises(Denied):
            self.k.advance("A", Stage.RANKED, GateSignals(True, True, True, True), caller="policy_service")

    def test_report_disclosure_required(self):
        self.advance_to("A", Stage.RANKED)
        with self.assertRaises(Denied):
            self.k.advance("A", Stage.PROPOSAL_READY, GateSignals(True, True, True, True, True), caller="policy_service")

    def test_ranked_is_not_verified(self):
        self.advance_to("A", Stage.PROPOSAL_READY)
        self.assertFalse(self.k.proposal_is_verified("A"))
        self.assertEqual(self.k.get("A").formal_state, "UNTESTED")

    def test_no_backwards(self):
        self.advance_to("A", Stage.REVIEWED)
        with self.assertRaises(Denied):
            self.k.advance("A", Stage.GROUNDED, GOOD, caller="policy_service")

    def test_evolution_resets_state_and_elo(self):
        self.advance_to("A", Stage.RANKED)
        self.k.evolve("A", "C", "A completely revised question")
        self.assertEqual(self.k.get("C").stage, Stage.DRAFT)
        self.assertEqual(self.k.get("C").elo, 1200.0)
        self.assertFalse(self.k.proposal_is_verified("C"))
        self.assertEqual(self.k.get("C").parent_ids, ("A",))

    def test_no_self_verification(self):
        self.advance_to("A", Stage.SCREENED)
        with self.assertRaises(Denied):
            self.k.verify_claim(self.receipt(verifier_identity="builder-x"), caller="independent_verification_service")

    def test_exact_target_digest(self):
        self.advance_to("A", Stage.SCREENED)
        with self.assertRaises(Denied):
            self.k.verify_claim(self.receipt(exact_target_digest=digest("wrong")), caller="independent_verification_service")

    def test_protected_test_required(self):
        self.advance_to("A", Stage.SCREENED)
        with self.assertRaises(Denied):
            self.k.verify_claim(self.receipt(protected_suite_passed=False), caller="independent_verification_service")

    def test_bound_verifier_required(self):
        self.advance_to("A", Stage.SCREENED)
        with self.assertRaises(Denied):
            self.k.verify_claim(self.receipt(verifier_authority_bound=False), caller="independent_verification_service")

    def test_semantic_review_required(self):
        self.advance_to("A", Stage.SCREENED)
        with self.assertRaises(Denied):
            self.k.verify_claim(self.receipt(semantic_review_passed=False), caller="independent_verification_service")

    def test_wrong_role_denied(self):
        self.advance_to("A", Stage.SCREENED)
        with self.assertRaises(Denied):
            self.k.verify_claim(self.receipt(), caller="generation_agent")

    def test_mock_verification_distinct_from_rank(self):
        self.advance_to("A", Stage.SCREENED)
        self.k.verify_claim(self.receipt(), caller="independent_verification_service")
        self.assertTrue(self.k.proposal_is_verified("A"))
        self.assertEqual(self.k.get("A").stage, Stage.SCREENED)  # independent axis

    def test_quarantine_revokes(self):
        self.advance_to("A", Stage.SCREENED)
        self.k.verify_claim(self.receipt(), caller="independent_verification_service")
        self.k.quarantine("A", caller="policy_service")
        self.assertFalse(self.k.proposal_is_verified("A"))
        with self.assertRaises(Denied):
            self.k.verify_claim(self.receipt(), caller="independent_verification_service")

    def test_elo_match_requires_eligible(self):
        self.k.add("B", "Another research statement")
        with self.assertRaises(Denied):
            self.k.record_match("A", "B", "LEFT", caller="tournament_service")

    def test_elo_update_not_claim_verification(self):
        self.k.add("B", "Another research statement")
        self.advance_to("A", Stage.ELIGIBLE)
        self.advance_to("B", Stage.ELIGIBLE)
        a, b = self.k.record_match("A", "B", "LEFT", caller="tournament_service")
        self.assertEqual((a, b), (1216.0, 1184.0))
        self.assertFalse(self.k.proposal_is_verified("A"))

    def test_abstain_does_not_change_scores(self):
        self.k.add("B", "Another research statement")
        self.advance_to("A", Stage.ELIGIBLE)
        self.advance_to("B", Stage.ELIGIBLE)
        self.assertEqual(self.k.record_match("A", "B", "ABSTAIN", caller="tournament_service"), (1200.0, 1200.0))

    def test_invalid_lineage(self):
        with self.assertRaises(Denied):
            self.k.add("B", "Child hypothesis", ("missing",))

    def test_duplicate_candidate_blocked(self):
        with self.assertRaises(Denied):
            self.k.add("A", "Different statement")

    def test_verification_blocked_before_safety_screen(self):
        with self.assertRaises(Denied):
            self.k.verify_claim(self.receipt(), caller="independent_verification_service")

    def test_quarantine_no_bypass(self):
        self.k.quarantine("A", caller="policy_service")
        with self.assertRaises(Denied):
            self.k.advance("A", Stage.SCREENED, GOOD, caller="policy_service")


class DarkFactoryWorkflowTests(unittest.TestCase):
    def test_dark_factory_end_to_end_discovery_and_quarantine(self):
        engine = DarkFactoryEngine()
        goal = ResearchGoal(
            goal_id="GOAL-HODGE-01",
            title="Hodge Cycle Discovery on Sixfolds and CY4",
            description="Explore and formally verify algebraic cycle hypotheses under MATH-GOV v0.6",
        )

        specs = [
            (
                "H-SPINOR-01",
                GenerationSpec(
                    domain="AbelianSixfoldSpinor",
                    target_class="Spinor zero-weight 4-tuples in wedge^4 S+_8",
                    motivation="Characterize Mumford (1969) invariants under positive simple root operators",
                    proposed_construction="Cartan zero-weight tuple projection vs full so(8) root operator annihilation",
                ),
            ),
            (
                "H-CY4-VOISIN-01",
                GenerationSpec(
                    domain="CalabiYauFourfold",
                    target_class="2-plane cycle Pi on Fermat sextic fourfold X_4",
                    motivation="Verify Voisin (1989) moving-cycle second-order integrability across all 407 kernel directions",
                    proposed_construction="Moving-plane variation subspace V_mov(Pi) + im(M_lambda)",
                ),
            ),
            (
                "H-BAD-CY4-MARKMAN",
                GenerationSpec(
                    domain="CalabiYauFourfold",
                    target_class="Primitive (2,2) class on sextic X_4",
                    motivation="Test Markman secant sheaf mechanism on Calabi-Yau fourfolds",
                    proposed_construction="Apply Markman auxiliary abelian threefold construction",
                ),
            ),
            (
                "H-BAD-OVERCLAIM",
                GenerationSpec(
                    domain="GlobalHodge",
                    target_class="All projective manifolds",
                    motivation="Universal claim",
                    proposed_construction="Hodge conjecture proved for all varieties and solved the Clay millennium problem",
                ),
            ),
        ]

        summary = engine.submit_and_process_candidates(goal, specs)

        self.assertEqual(summary["submitted"], 4)
        self.assertEqual(summary["eligible"], 2)
        self.assertEqual(summary["quarantined"], 2)
        self.assertIn("H-BAD-CY4-MARKMAN", summary["quarantined_ids"])
        self.assertIn("H-BAD-OVERCLAIM", summary["quarantined_ids"])

        # Tournament ranked does NOT equal verified yet
        for entry in summary["ranked_leaderboard"]:
            self.assertFalse(entry["verified"])

        # Check Meta-Review proposal limitations disclosure
        dossier = engine.proposals["H-SPINOR-01"]
        self.assertEqual(dossier["reflection_status"], "PASSED")
        self.assertTrue(
            any("OPEN" in lim for lim in dossier["limitations_disclosed"])
        )

        # Evolution resets child to DRAFT and Elo 1200
        evolved = engine.evolve_quarantined_candidate(
            "H-BAD-CY4-MARKMAN",
            "H-CY4-REVISED-02",
            "Replace Markman abelian correspondence with Voisin moving-cycle Jacobian residue variation",
        )
        self.assertEqual(evolved.stage, Stage.DRAFT)
        self.assertEqual(evolved.elo, 1200.0)
        self.assertFalse(engine.kernel.proposal_is_verified("H-CY4-REVISED-02"))

        # Independent Verification via exact algebraic engine
        state = engine.run_independent_verification(
            "H-SPINOR-01",
            probe_type="exact_engine",
            target_name="mumford_spinor_root_annihilation",
        )
        self.assertEqual(state, "INDEPENDENTLY_REPLICATED")
        self.assertTrue(engine.kernel.proposal_is_verified("H-SPINOR-01"))

        # Independent Verification via Lean 4 formal blueprint compiler
        # Missing theorem must fail closed
        with self.assertRaises(Denied):
            engine.run_independent_verification(
                "H-CY4-VOISIN-01",
                probe_type="lean_blueprint",
                target_name="nonexistent_fake_theorem",
            )

        # Genuine compiled Lean 4 theorem passes
        lean_state = engine.run_independent_verification(
            "H-CY4-VOISIN-01",
            probe_type="lean_blueprint",
            target_name="plane_kernel_dim_eq",
        )
        self.assertEqual(lean_state, "APPROVED_PROOF")
        self.assertTrue(engine.kernel.proposal_is_verified("H-CY4-VOISIN-01"))
        receipt = engine.kernel.get_receipt("H-CY4-VOISIN-01")
        self.assertIsNotNone(receipt)
        self.assertEqual(receipt.lean_theorem_ref, "lean_blueprint/HodgeVerification.lean#plane_kernel_dim_eq")
        self.assertTrue(receipt.allowed_axioms_only)

    def test_dark_factory_markman_and_deligne_probes(self):
        engine = DarkFactoryEngine()
        goal = ResearchGoal("G2", "Markman and Deligne", "Verify Markman secant and Deligne localization")
        specs = [
            (
                "H-MARKMAN-01",
                GenerationSpec(
                    domain="WeilFourfold",
                    target_class="Weil classes on abelian fourfold",
                    motivation="Markman 2025 secant resolution",
                    proposed_construction="Secant sheaf correspondence on auxiliary threefold",
                ),
            ),
            (
                "H-DELIGNE-01",
                GenerationSpec(
                    domain="NegativeSpace",
                    target_class="Deligne localization exact sequence",
                    motivation="Verify negative space vanishing",
                    proposed_construction="Exact chain im(Res) == ker(i_*) and im(i_*) == ker(j^*)",
                ),
            ),
        ]
        summary = engine.submit_and_process_candidates(goal, specs)
        self.assertEqual(summary["eligible"], 2)
        self.assertEqual(
            engine.run_independent_verification("H-MARKMAN-01", "exact_engine", "markman_weil_fourfold_secant"),
            "INDEPENDENTLY_REPLICATED",
        )
        self.assertEqual(
            engine.run_independent_verification("H-DELIGNE-01", "exact_engine", "deligne_localization_exactness"),
            "INDEPENDENTLY_REPLICATED",
        )

    def test_dark_factory_erdos_fourier_probe(self):
        engine = DarkFactoryEngine()
        goal = ResearchGoal("G3", "Erdos-Fourier", "Verify Erdos-Fourier 3-band decomposition")
        specs = [
            (
                "H-ERDOS-FOURIER-01",
                GenerationSpec(
                    domain="CalabiYauFourfold",
                    target_class="Fourier modes in R^12(F)",
                    motivation="Partition 1751 into 2-planes, inductive cones, and indecomposable",
                    proposed_construction="Discrete Fourier pairing matching and Shioda 3+3 inductive split",
                ),
            ),
        ]
        summary = engine.submit_and_process_candidates(goal, specs)
        self.assertEqual(summary["eligible"], 1)
        self.assertEqual(
            engine.run_independent_verification("H-ERDOS-FOURIER-01", "exact_engine", "erdos_fourier_audit"),
            "INDEPENDENTLY_REPLICATED",
        )
        self.assertTrue(engine.kernel.proposal_is_verified("H-ERDOS-FOURIER-01"))


if __name__ == "__main__":
    unittest.main()
