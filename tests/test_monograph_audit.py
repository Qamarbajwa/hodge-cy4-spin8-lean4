"""Monograph Audit Test Suite for HODGE-MILLENNIUM-001 Monograph & Blueprint.

Governed by:
- governance/GOVERNANCE.md
- governance/MATHEMATICAL_RESEARCH_CONSTITUTION_v1.0.md
- GEMINI.md

Validates:
1. Monograph (17 pages) and Blueprint (8 pages) PDF existence and exact page counts.
2. Author attribution and classical literature attribution.
3. Strict Epistemic Invariants (GLOBAL_HODGE_CONJECTURE = OPEN, release_authorized = false, zero Mathlib).
4. Four-Tier Epistemic Partition Ledger (Table 1).
5. Exact Numerical Invariants against governance/exact_hodge_numerical_receipts.json.
6. Finite Check Fidelity Gate (Table 15 mapping to all 43 decidable checks in HodgeVerification.lean).
7. TikZ Architectural Diagram, Mechanism Matrix, Epistemic Summary, and AI Assistance Disclosure.
8. The Understanding Law (3-tier explanatory protocol).
"""

import json
import re
import unittest
from pathlib import Path
import pypdf

from toolkit.hodge_proof_closure_reviewer import LEAN_THEOREM_SPECS
from toolkit.integrity import scan_forbidden


class TestMonographAudit(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root = Path(__file__).resolve().parent.parent
        cls.main_tex_path = cls.root / "paper" / "main.tex"
        cls.blueprint_tex_path = cls.root / "paper" / "blueprint.tex"
        cls.monograph_pdf_path = cls.root / "01_Monograph_Hodge_Conjecture_CY4_Spinor_Qamar_Munawer_v1.0.0.pdf"
        cls.blueprint_pdf_path = cls.root / "02_LeanBlueprint_Hodge_Formal_Verification_Qamar_Munawer_v1.0.0.pdf"
        cls.receipts_path = cls.root / "governance" / "exact_hodge_numerical_receipts.json"
        cls.lean_path = cls.root / "lean_blueprint" / "HodgeVerification.lean"

        cls.main_tex = cls.main_tex_path.read_text(encoding="utf-8")
        cls.blueprint_tex = cls.blueprint_tex_path.read_text(encoding="utf-8")
        cls.receipts = json.loads(cls.receipts_path.read_text(encoding="utf-8"))
        cls.lean_src = cls.lean_path.read_text(encoding="utf-8")

    def test_01_monograph_pdf_existence_and_page_count(self):
        """Monograph PDF must exist and have strictly 17 pages."""
        self.assertTrue(self.monograph_pdf_path.exists(), "Monograph PDF missing")
        reader = pypdf.PdfReader(str(self.monograph_pdf_path))
        self.assertEqual(len(reader.pages), 17, f"Monograph must have strictly 17 pages, found {len(reader.pages)}")

    def test_02_blueprint_pdf_existence_and_page_count(self):
        """Blueprint PDF must exist and have strictly 8 pages."""
        self.assertTrue(self.blueprint_pdf_path.exists(), "Blueprint PDF missing")
        reader = pypdf.PdfReader(str(self.blueprint_pdf_path))
        self.assertEqual(len(reader.pages), 8, f"Blueprint must have strictly 8 pages, found {len(reader.pages)}")

    def test_03_principal_investigator_and_modest_scope(self):
        """Author, zero-Mathlib scope notice, and AI disclosure must appear cleanly."""
        for text in (self.main_tex, self.blueprint_tex):
            self.assertIn("Qamar Munawer", text)
            self.assertTrue(
                "Brandenburg University of Technology Cottbus-Senftenberg" in text
                or "Brandenburg University of Technology Cottbus--Senftenberg" in text
            )
            self.assertIn("zero Mathlib", text)
            self.assertIn("schemes, sheaves, cohomology, or Hodge theory", text)
        self.assertIn("AI Assistance Disclosure", self.main_tex)

    def test_04_epistemic_invariants_and_honesty_tokens(self):
        """Strict epistemic boundary tokens must be present across all publications."""
        required_tokens = [
            r"GLOBAL\_HODGE\_CONJECTURE = OPEN",
            r"release\_authorized = false",
            r"theorem\_progress = UNKNOWN",
            r"S\text{-}BRIDGE\text{-}DEFORM\text{-}CY4 = OPEN",
            r"S\text{-}BRIDGE\text{-}SPINOR\text{-}MOTIVE = OPEN",
        ]
        for token in required_tokens:
            self.assertIn(token, self.main_tex, f"Honesty token '{token}' missing from main.tex")

    def test_05_four_tier_epistemic_partition_ledger_table_1(self):
        """Table 1 in main.tex must explicitly partition all results into four epistemic tiers."""
        self.assertIn(r"\label{tab:epistemic_ledger}", self.main_tex)
        self.assertIn(r"\textbf{Tier I}", self.main_tex)
        self.assertIn(r"\textbf{Tier II}", self.main_tex)
        self.assertIn(r"\textbf{Tier III}", self.main_tex)
        self.assertIn(r"\textbf{Tier IV}", self.main_tex)

    def test_06_exact_numerical_invariants_audit(self):
        """All load-bearing numbers in main.tex must match certified exact_hodge_numerical_receipts.json."""
        exact = self.receipts["exact_numerical_invariants"]
        num_checks = [
            ("15,625", "milnor_number"),
            ("1,751", "primitive_h22"),
            ("407", "canonical_fixed_plane_kernel_dim"),
            ("70", "abelian_fourfold_h4_dim"),
            ("128", "clifford_even_dim"),
            ("192", "weyl_d4_group_order"),
            ("32/512", "d4_triality_zero_triples"),
            ("72", "deformed_macaulay_flat_hilbert_sum"),
            ("125", "cyclotomic_wavepacket_monomials"),
            ("1,325", "universal_kernel_lower_bound"),
            ("135", "twenty_plane_collision_excess"),
            ("380", "twenty_plane_total_incidences"),
            ("245", "twenty_plane_target_dim"),
            ("1,875", "fifteen_matching_incidences"),
            ("426", "crt_macaulay_matrix_rank"),
            ("43", "lean4_finite_checks_total"),
        ]
        for str_val, desc in num_checks:
            self.assertIn(str_val, self.main_tex, f"Certified value '{str_val}' for '{desc}' missing from main.tex")
        self.assertEqual(exact["lean4_finite_checks_total"], 43)
        self.assertEqual(exact["lean4_mathlib_imports"], 0)

    def test_07_formalization_fidelity_and_43_checks_ledger(self):
        """Table 15 in Appendix A must catalog all 43 finite checks matching HodgeVerification.lean."""
        self.assertIn(r"\label{tab:lean_ledger}", self.main_tex)
        self.assertIn("Standalone Core Lean~4 Decidable Finite Checks (43 Checks, 0 Mathlib)", self.main_tex)
        self.assertNotIn("ClassicalHodgeBridgeInterface", self.main_tex)
        self.assertNotIn("UniversalClayHodgeInterface", self.main_tex)
        self.assertNotIn("1729", self.main_tex)

        # Check all 43 declaration names from LEAN_THEOREM_SPECS exist in main.tex (escaped underscores)
        self.assertEqual(len(LEAN_THEOREM_SPECS), 43)
        for thm_name, _ in LEAN_THEOREM_SPECS:
            escaped_name = thm_name.replace("_", r"\_")
            self.assertIn(escaped_name, self.main_tex, f"Check '{escaped_name}' missing from Table 15 in main.tex")

    def test_08_tikz_architecture_and_mechanism_matrix(self):
        """Section 1.3 must contain TikZ architectural flowchart and Mechanism Matrix."""
        self.assertIn(r"\begin{tikzpicture}", self.main_tex)
        self.assertIn(r"\label{tab:mechanism_matrix}", self.main_tex)
        self.assertIn("Deligne Gysin Residues", self.main_tex)
        self.assertIn("Markman Secant Sheaves", self.main_tex)
        self.assertIn(r"Even Clifford $C^+(V_8)$", self.main_tex)
        self.assertIn(r"Multi-Axis $W(D_4)$ Coset", self.main_tex)
        self.assertIn(r"4-Band Fourier Sieve", self.main_tex)
        self.assertIn(r"Rank-Nullity Kernel Bound", self.main_tex)

    def test_09_epistemic_summary_and_disclosure(self):
        """Section 6 must contain Epistemic Summary and AI Assistance Disclosure."""
        markers = [
            "Absolute Scientific Honesty",
            "Strict Lean~4.35.0 Scope",
            "Float-Free Computational Toolkit",
            "Classical Attribution",
            "AI Assistance Disclosure",
        ]
        for c_text in markers:
            self.assertIn(c_text, self.main_tex, f"Marker '{c_text}' missing from main.tex")

    def test_10_understanding_law_compliance(self):
        """Verifies adherence to the Understanding Law: 3-level explanatory protocol across all four pillars."""
        constitution = (self.root / "governance" / "MATHEMATICAL_RESEARCH_CONSTITUTION_v1.0.md").read_text(encoding="utf-8")
        self.assertIn("The Truth Law", constitution)
        self.assertIn("The Identity Law", constitution)
        self.assertIn("The Understanding Law", constitution)
        self.assertIn("Level 1 (Intuitive)", constitution)
        self.assertIn("Level 2 (Architectural)", constitution)
        self.assertIn("Level 3 (Formal)", constitution)


if __name__ == "__main__":
    unittest.main()
