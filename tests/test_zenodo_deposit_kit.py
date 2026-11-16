"""Unit & Integration Tests for the Zenodo Publication Archive & MATH-GOV Verification Kit."""

import json
import subprocess
import sys
import unittest
from pathlib import Path

from toolkit.integrity import scan_forbidden
from verify_zenodo_deposit import run_zenodo_verification


class TestZenodoDepositKit(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root = Path(__file__).resolve().parent.parent
        cls.zenodo_path = cls.root / ".zenodo.json"
        cls.cff_path = cls.root / "CITATION.cff"
        cls.readme_path = cls.root / "README_ZENODO.md"
        cls.manuscript_path = cls.root / "paper" / "ZENODO_MANUSCRIPT_FOUR_PILLARS_HODGE.md"

    def test_01_zenodo_json_and_citation_cff_validity(self):
        """Verifies valid .zenodo.json schema, CITATION.cff metadata, and Millennium honesty flags."""
        zenodo = json.loads(self.zenodo_path.read_text(encoding="utf-8"))
        for key in ("title", "upload_type", "publication_type", "creators", "description", "license", "keywords"):
            self.assertIn(key, zenodo)

        self.assertEqual(zenodo["upload_type"], "publication")
        self.assertEqual(zenodo["license"], "CC-BY-4.0")
        self.assertGreaterEqual(len(zenodo["creators"]), 1)
        self.assertGreaterEqual(len(zenodo["keywords"]), 5)

        desc = zenodo["description"]
        for marker in (
            "GLOBAL_HODGE_CONJECTURE = OPEN",
            "release_authorized = false",
            "theorem_progress = UNKNOWN",
            "HodgeVerification.lean",
            "43 decidable finite",
            "zero Mathlib imports",
        ):
            self.assertIn(marker, desc)
        self.assertEqual(zenodo.get("related_identifiers", []), [])

        cff_text = self.cff_path.read_text(encoding="utf-8")
        for token in (
            "cff-version: 1.2.0",
            "license: CC-BY-4.0",
            "Munawer",
            "Brandenburg University of Technology Cottbus-Senftenberg",
            "43 decidable",
            "zero Mathlib",
            "GLOBAL_HODGE_CONJECTURE",
            "OPEN",
            "UNKNOWN",
        ):
            self.assertIn(token, cff_text)

        readme_text = self.readme_path.read_text(encoding="utf-8")
        for token in (
            "verify_zenodo_deposit.py",
            "GLOBAL_HODGE_CONJECTURE",
            "release_authorized",
            "UNKNOWN",
            "1,751",
            "43 Decidable Finite",
            "zero Mathlib imports",
            "cmi_five_condition_attack_engine.py",
        ):
            self.assertIn(token, readme_text)

    def test_02_manuscript_completeness_and_honesty_audit(self):
        """Verifies the 7-section Zenodo manuscript matches exact verified mathematical figures and honesty bounds."""
        text = self.manuscript_path.read_text(encoding="utf-8")
        for sec_num in range(1, 8):
            self.assertIn(f"## {sec_num}.", text)

        required_numbers = [
            "70",
            "924",
            "400",
            "1,751",
            "15,625",
            "19",
            "407",
            "141",
            "285",
            "1,001",
            "630",
            "120",
            "85",
            "68",
            "69",
            "304",
            "305",
            "72",
            "359",
            "332",
            "125",
            "353",
            "1,750",
            "1,756",
        ]
        for num in required_numbers:
            self.assertIn(num, text, f"Expected verified number '{num}' missing from manuscript")

        for sec_token in (
            "### 4.4",
            "### 5.5",
            "### 5.6",
            "### 5.7",
            "### 5.8",
            "### 5.9",
            "### 5.10",
            "### 5.11",
            "### 5.12",
            "### 5.13",
            "43 decidable",
            "zero Mathlib",
            "AI Assistance Disclosure",
            "modular_crt_linear_solver.py",
            "cmi_five_condition_attack_engine.py",
            "CyclotomicPlaneWavepacketEngine",
            "JointGeneratorShadowSolver",
            "SignedFermatTangentialTransportEngine",
            "GeometricLiaisonCompressionEngine",
            "PicardLefschetzNodalBridgeEngine",
            "SpinorToWeilSpecializationEngine",
            "ObstructionCancellationRecombinationEngine",
            "GlobalBandApolarityDictionary",
            "WeylCosetWeilSpanningEngine",
            "UniversalRankNullityCancellationEngine",
            "GorensteinModuliRankCensus",
            "TuranCoordinatePlaneCoverageEngine",
            "SurjectiveCokernelAnnihilationEngine",
            "RankIndependentSecondOrderEngine",
            "FormalHodgeSeriesToHilbertAudit",
            "TwentyPlaneIncidenceAndCollisionEngine",
            "FifteenMatchingBandOneBlockEngine",
            "DeterminantalMacaulayStabilizationAudit",
            "CollisionHigherDegreeDeterminantalEngine",
            "FiniteNonFermatMacaulayEngine",
            "NonSeparableBridgeAHonestyAudit",
            "Appendix A.1",
            "Appendix A.2",
            "Appendix A.3",
        ):
            self.assertIn(sec_token, text, f"Expected manuscript content '{sec_token}' missing")

        for honesty_marker in ("GLOBAL_HODGE_CONJECTURE", "OPEN", "release_authorized", "UNKNOWN"):
            self.assertIn(honesty_marker, text)

        self.assertEqual(scan_forbidden(str(self.root / "verify_zenodo_deposit.py")), [])

    def test_03_verify_zenodo_deposit_fast_execution(self):
        """Runs verify_zenodo_deposit (--fast API and CLI) checking math replay, Lean 4 axioms == [], & manifest."""
        cert = run_zenodo_verification(fast=True)
        self.assertTrue(cert["all_checks_passed"])
        self.assertEqual(cert["global_hodge_conjecture"], "OPEN")
        self.assertFalse(cert["release_authorized"])
        self.assertEqual(cert["theorem_progress"], "UNKNOWN")
        self.assertEqual(cert["step_1_zero_float_audit"]["toolkit_engines_scanned"], 20)
        self.assertEqual(cert["step_1_zero_float_audit"]["files_scanned"], 21)
        self.assertEqual(cert["step_1_zero_float_audit"]["total_float_violations"], 0)
        self.assertEqual(cert["step_2_math_invariant_replay"]["pillar_4_order3_plane_unobstructed"], "407/407")
        self.assertEqual(cert["step_2_math_invariant_replay"]["pillar_4_stealth_jet_filtration"], [347, 336, 334])
        self.assertEqual(cert["step_2_math_invariant_replay"]["pillar_4_macaulay_plane_ann_R1"], 3)
        self.assertEqual(cert["step_2_math_invariant_replay"]["pillar_4_macaulay_signed_ann_R2"], 9)
        self.assertTrue(cert["step_2_math_invariant_replay"]["pillar_4_macaulay_18_partitions_verified"])
        self.assertEqual(cert["step_2_math_invariant_replay"]["pillar_4_gotzmann_pi_G"], 1)
        self.assertEqual(cert["step_2_math_invariant_replay"]["pillar_4_gotzmann_signed_G"], 5)
        self.assertTrue(cert["step_2_math_invariant_replay"]["pillar_4_deformed_moving_18_cancelled"])
        self.assertTrue(cert["step_2_math_invariant_replay"]["pillar_4_deformed_fixed_359_diagonal_flat"])
        self.assertTrue(cert["step_2_math_invariant_replay"]["pillar_4_deformed_canonical_56_flat"])
        self.assertTrue(cert["step_2_math_invariant_replay"]["pillar_4_deformed_chain_stealth_unliftable"])
        self.assertEqual(cert["step_2_math_invariant_replay"]["pillar_4_deformed_gotzmann_hilbert_sum"], 72)
        self.assertEqual(cert["step_2_math_invariant_replay"]["pillar_4_deformed_gotzmann_Gt"], 1)
        self.assertEqual(cert["step_2_math_invariant_replay"]["pillar_4_cyclotomic_wavepacket_monomials"], 125)
        self.assertTrue(cert["step_2_math_invariant_replay"]["pillar_4_cyclotomic_wavepacket_ideal_match"])
        self.assertEqual(cert["step_2_math_invariant_replay"]["pillar_4_joint_transport_rank_gain"], 6)
        self.assertEqual(cert["step_2_math_invariant_replay"]["pillar_4_joint_transport_subspace_gain"], 6)
        self.assertEqual(cert["step_2_math_invariant_replay"]["pillar_4_joint_transport_nilpotent_gain"], 0)
        self.assertEqual(cert["step_2_math_invariant_replay"]["pillar_4_wall1_signed_tangential_leibniz"], "407/407")
        self.assertEqual(cert["step_2_math_invariant_replay"]["pillar_4_wall1_signed_joint_solvable"], "407/407")
        self.assertEqual(cert["step_2_math_invariant_replay"]["pillar_4_wall1_unsigned_unlifted"], 48)
        self.assertEqual(cert["step_2_math_invariant_replay"]["pillar_4_wall2_liaison_ranks"], [3, 6, 10, 15, 18, 19])
        self.assertEqual(cert["step_2_math_invariant_replay"]["pillar_4_wall3_nodal_orbit_size"], 30)
        self.assertEqual(cert["step_2_math_invariant_replay"]["pillar_3_wall4_d3_su22_zero_dim"], 8)
        self.assertEqual(cert["step_2_math_invariant_replay"]["pillar_3_wall4_su22_invariants_dim"], 3)
        self.assertEqual(cert["step_2_math_invariant_replay"]["pillar_4_recombination_kernel_gain"], "391->394 (+3)")
        self.assertEqual(cert["step_2_math_invariant_replay"]["pillar_4_recombination_quadric_d_gen"], 4)
        self.assertEqual(cert["step_2_math_invariant_replay"]["pillar_4_global_18_partition_max_d_gen"], 4)
        self.assertEqual(cert["step_2_math_invariant_replay"]["pillar_3_weyl_coset_pure_weil_count"], 16)
        self.assertEqual(cert["step_2_math_invariant_replay"]["pillar_3_weyl_coset_k22_spanned"], "6/6")
        self.assertEqual(cert["step_2_math_invariant_replay"]["pillar_4_univ_ker_lower_bounds"], [1325, 575, 204])
        self.assertEqual(cert["step_2_math_invariant_replay"]["pillar_4_gorenstein_moduli_rank_range"], [155, 336])
        self.assertEqual(cert["step_2_math_invariant_replay"]["pillar_4_turan_pigeonhole_min_K"], 5)
        self.assertEqual(cert["step_2_math_invariant_replay"]["pillar_4_surjective_coker_dim"], 0)
        self.assertEqual(cert["step_2_math_invariant_replay"]["pillar_4_all_order_formal_ker_dim"], 1325)
        self.assertEqual(cert["step_2_math_invariant_replay"]["pillar_4_psi2_partition_ker_range"], [1325, 1544])
        self.assertEqual(cert["step_2_math_invariant_replay"]["pillar_4_twenty_plane_collision_excess"], 135)
        self.assertEqual(cert["step_2_math_invariant_replay"]["pillar_4_high_support_annihilator_dim"], 181)
        self.assertEqual(cert["step_2_math_invariant_replay"]["pillar_4_fifteen_matching_union"], 1001)
        self.assertEqual(cert["step_2_math_invariant_replay"]["pillar_4_fifteen_matching_incidences"], 1875)
        self.assertTrue(cert["step_2_math_invariant_replay"]["pillar_4_recomb_m1_to_m6_stabilized"])
        self.assertEqual(cert["step_2_math_invariant_replay"]["pillar_4_quad_syzygies_stabilized"], 4)
        self.assertEqual(cert["step_2_math_invariant_replay"]["pillar_4_finite_non_fermat_plane_ranks"], [3, 6, 10, 15, 18, 19])
        self.assertEqual(cert["step_2_math_invariant_replay"]["pillar_4_finite_non_fermat_quad_ranks"], [4, 9, 16, 24, 30, 32])
        self.assertFalse(cert["step_2_math_invariant_replay"]["pillar_4_universal_non_fermat_determinantal_proved"])
        self.assertTrue(cert["step_2_math_invariant_replay"]["pillar_4_cdk_moduli_algebraic"])
        self.assertFalse(cert["step_2_math_invariant_replay"]["pillar_4_effective_hilbert_bound"])
        self.assertEqual(cert["step_2_math_invariant_replay"]["pillar_4_crt_non_fermat_1751x426_rank"], 426)
        self.assertTrue(cert["step_2_math_invariant_replay"]["pillar_4_crt_non_fermat_1751x426_under_2s"])
        self.assertEqual(cert["step_2_math_invariant_replay"]["pillar_4_crt_dense_moduli_1751x426_rank"], 426)
        self.assertEqual(cert["step_2_math_invariant_replay"]["pillar_4_cmi1_liaison_z22_ranks"], [4, 9, 16, 24, 30, 32])
        self.assertEqual(cert["step_2_math_invariant_replay"]["pillar_4_cmi2_coupled_cy4_ranks"], [3, 6, 10, 15, 18, 19])
        self.assertEqual(cert["step_2_math_invariant_replay"]["pillar_3_cmi34_ks_triality_rank"], 70)
        self.assertEqual(cert["step_2_math_invariant_replay"]["pillar_3_cmi34_weyl_basis_rank"], 6)
        self.assertEqual(cert["step_2_math_invariant_replay"]["pillar_4_cmi5_open_frontier"], "OPEN")
        self.assertEqual(cert["step_3_lean4_zero_axiom_check"]["core_checks_verified"], 43)
        self.assertEqual(cert["step_3_lean4_zero_axiom_check"]["extended_certificates_verified"], 3)
        self.assertEqual(cert["step_3_lean4_zero_axiom_check"]["lean_theorems_verified"], 46)
        self.assertTrue(cert["step_3_lean4_zero_axiom_check"]["all_axioms_empty"])
        self.assertEqual(cert["step_4_governance_and_manifest"]["manifest_mismatches"], [])

        proc = subprocess.run(
            [sys.executable, str(self.root / "verify_zenodo_deposit.py"), "--fast", "--json-only"],
            cwd=str(self.root),
            capture_output=True,
            text=True,
            timeout=120,
            check=False,
        )
        self.assertEqual(proc.returncode, 0, msg=f"stderr: {proc.stderr}")
        cli_cert = json.loads(proc.stdout)
        self.assertTrue(cli_cert["all_checks_passed"])
        self.assertEqual(cli_cert["certificate_sha256"], cert["certificate_sha256"])

    def test_04_prior_art_audit_and_manuscript_cleanliness(self):
        """Verifies prior_art_audit_receipt.json, UNIVERSAL_SOLVED_VS_UNSOLVED_AUDIT.md, and title page cleanliness."""
        prior_art_path = self.root / "prior_art_audit_receipt.json"
        self.assertTrue(prior_art_path.exists(), "prior_art_audit_receipt.json must exist")
        prior_art = json.loads(prior_art_path.read_text(encoding="utf-8"))
        self.assertIn("repositories_scanned", prior_art)
        self.assertIn("leanprover-community/mathlib4", prior_art["repositories_scanned"])
        self.assertIn("google-deepmind/formal-conjectures", prior_art["repositories_scanned"])
        self.assertIn("ImperialCollegeLondon/FLT", prior_art["repositories_scanned"])
        self.assertIn("targets", prior_art)
        self.assertGreaterEqual(len(prior_art["targets"]), 6)

        audit_doc_path = self.root / "docs" / "UNIVERSAL_SOLVED_VS_UNSOLVED_AUDIT.md"
        self.assertTrue(audit_doc_path.exists(), "docs/UNIVERSAL_SOLVED_VS_UNSOLVED_AUDIT.md must exist")
        audit_text = audit_doc_path.read_text(encoding="utf-8")
        for bucket in (
            "[SOLVED-CLASSICAL-LITERATURE]",
            "[SOLVED-COMPUTATIONAL-FINITE]",
            "[SOLVED-LEAN4-FINITE-RFL]",
            "[UNSOLVED-OPEN-GLOBAL]",
        ):
            self.assertIn(bucket, audit_text)

        # Verify removal of department name and telemetry flags from paper/main.tex
        main_tex = (self.root / "paper" / "main.tex").read_text(encoding="utf-8")
        self.assertNotIn("Department of Mathematics", main_tex)
        self.assertIn("Brandenburg University of Technology Cottbus--Senftenberg", main_tex)
        # Ensure title block does not contain robotic telemetry flags
        title_block = main_tex[: main_tex.find(r"\maketitle")]
        self.assertNotIn("GLOBAL_HODGE_CONJECTURE", title_block)
        self.assertNotIn("release_authorized", title_block)
        self.assertNotIn("theorem_progress", title_block)

        # Verify journal paper as well
        journal_tex = (self.root / "paper" / "journal_submission" / "Munawer_Hodge_Apolarity_Spin8_Lean4_Journal.tex").read_text(encoding="utf-8")
        self.assertNotIn("Department of Mathematics", journal_tex)
        self.assertIn("Brandenburg University of Technology Cottbus--Senftenberg", journal_tex)
        journal_title_block = journal_tex[: journal_tex.find(r"\maketitle")]
        self.assertNotIn("GLOBAL_HODGE_CONJECTURE", journal_title_block)


if __name__ == "__main__":
    unittest.main()
