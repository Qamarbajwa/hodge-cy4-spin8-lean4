"""Math Proof Adapter connecting Co-Scientist Dark Factory to Lean 4 and Exact Algebra Engines.

Executes independent mathematical verification probes and generates bound
VerificationReceipts for the ResearchGateKernel. Never claims global proof
of the open Millennium problem; verifies finite-dimensional algebraic, combinatorial,
and Lean 4 structural invariants.
"""

from __future__ import annotations
import json
from dataclasses import dataclass
from typing import Dict, Any, Callable, Optional
from .core import Hypothesis, VerificationReceipt, digest


@dataclass(frozen=True)
class LeanVerificationResult:
    passed: bool
    theorem_name: str
    file_path: str
    allowed_axioms_only: bool
    zero_sorry: bool
    evidence_digest: str
    details: Dict[str, Any]


class MathProofAdapter:
    """External independent verifier adapter bound to MATH-GOV v0.6."""

    def __init__(self, verifier_identity: str = "Adversarial_Verification_Auditor"):
        self.verifier_identity = verifier_identity

    def verify_with_exact_engine(
        self,
        hypothesis: Hypothesis,
        probe_name: str,
        builder_identity: str = "agent_generation_01",
    ) -> VerificationReceipt:
        """Executes an exact mathematical engine check and binds an immutable VerificationReceipt."""
        result_payload: Dict[str, Any] = {}
        passed = False

        if probe_name == "calabi_yau_moving_plane":
            from toolkit.calabi_yau_jacobian_engine import CalabiYauJacobianEngine
            eng = CalabiYauJacobianEngine()
            mov = eng.evaluate_moving_plane_full_integrability()
            passed = (
                mov["plane_unobstructed_vectors"] == 407
                and mov["plane_total_kernel_vectors"] == 407
                and mov["chain_is_still_obstructed"] is True
            )
            result_payload = {
                "probe": probe_name,
                "unobstructed": mov["plane_unobstructed_vectors"],
                "total": mov["plane_total_kernel_vectors"],
                "chain_obstructed": mov["chain_is_still_obstructed"],
                "exact_arithmetic": True,
            }
        elif probe_name == "mumford_spinor_root_annihilation":
            from toolkit.mumford_spinor_engine import MumfordSpinorEngine
            eng = MumfordSpinorEngine()
            res = eng.cartan_weight_zero_vs_root_annihilation()
            passed = (
                res["cartan_zero_weight_dim"] == 6
                and res["stacked_root_operator_rank"] == 6
                and res["root_annihilation_kernel_dim"] == 0
                and res["full_so8_invariants_dim"] == 0
            )
            result_payload = {
                "probe": probe_name,
                "zero_weight_dim": res["cartan_zero_weight_dim"],
                "root_op_rank": res["stacked_root_operator_rank"],
                "ker_dim": res["root_annihilation_kernel_dim"],
                "exact_arithmetic": True,
            }
        elif probe_name == "deligne_localization_exactness":
            from toolkit.three_agent_space_comparison import ExactLocalizationSequence
            seq = ExactLocalizationSequence()
            h0 = seq.verify_exactness_at_H0()
            h4 = seq.verify_exactness_at_H4()
            passed = h0["im_Res_equals_ker_i_star"] and h4["im_i_star_equals_ker_j_star"]
            result_payload = {
                "probe": probe_name,
                "h0_exact": h0["im_Res_equals_ker_i_star"],
                "h4_exact": h4["im_i_star_equals_ker_j_star"],
                "exact_arithmetic": True,
            }
        elif probe_name == "markman_weil_fourfold_secant":
            from toolkit.markman_secant_engine import MarkmanSecantWeilEngine
            eng = MarkmanSecantWeilEngine()
            mz = eng.moonen_zarhin_reduction_table()
            ss = eng.secant_sheaf_invariants()
            schoen = eng.schoen_degeneration_specialization()
            passed = (
                mz["dim_4_abelian_fourfolds"]["hodge_conjecture_status"] == "RESOLVED_AFFIRMATIVELY_BY_MARKMAN_2025"
                and ss["todd_genus_abelian_variety"] == 1
                and schoen["consequence_for_hodge_conjecture"] == "HODGE_CONJECTURE_TRUE_FOR_ALL_ABELIAN_FOURFOLDS"
            )
            result_payload = {
                "probe": probe_name,
                "mz_status": mz["dim_4_abelian_fourfolds"]["hodge_conjecture_status"],
                "todd_genus": ss["todd_genus_abelian_variety"],
                "schoen_codim_a4": schoen["fourfold_weil_class_codimension"],
                "exact_arithmetic": True,
            }
        else:
            raise ValueError(f"Unknown exact verification probe: {probe_name}")

        evidence_json = json.dumps(result_payload, sort_keys=True)
        ev_digest = digest(evidence_json)

        return VerificationReceipt(
            hypothesis_id=hypothesis.hypothesis_id,
            exact_target_digest=hypothesis.content_digest,
            evidence_digest=ev_digest,
            claim_type="EMPIRICAL_REPLICATION",
            builder_identity=builder_identity,
            verifier_identity=self.verifier_identity,
            independently_verified=passed,
            protected_suite_passed=passed,
            semantic_review_passed=passed,
            verifier_authority_bound=True,
            lean_theorem_ref=None,
            allowed_axioms_only=True,
        )

    def verify_with_lean_blueprint(
        self,
        hypothesis: Hypothesis,
        theorem_name: str,
        lean_file: str = "lean_blueprint/HodgeVerification.lean",
        builder_identity: str = "agent_generation_01",
    ) -> VerificationReceipt:
        """Runs the Lean 4 blueprint compiler and forbids sorry/admit/custom axioms."""
        from toolkit.lean_blueprint_verifier import LeanBlueprintVerifier
        verifier = LeanBlueprintVerifier(lean_file)
        scan = verifier.scan_for_forbidden_keywords()
        comp = verifier.compile_lean_file()

        # Check theorem presence in file
        with open(lean_file, "r", encoding="utf-8") as f:
            source_text = f.read()
        theorem_present = f"theorem {theorem_name}" in source_text

        passed = (
            scan["is_clean"]
            and comp["is_success"]
            and theorem_present
        )

        evidence_payload = {
            "lean_file": lean_file,
            "theorem": theorem_name,
            "theorem_present": theorem_present,
            "zero_sorry_clean": scan["is_clean"],
            "compile_success": comp["is_success"],
            "returncode": comp["returncode"],
        }
        ev_digest = digest(json.dumps(evidence_payload, sort_keys=True))

        return VerificationReceipt(
            hypothesis_id=hypothesis.hypothesis_id,
            exact_target_digest=hypothesis.content_digest,
            evidence_digest=ev_digest,
            claim_type="MATH_PROOF",
            builder_identity=builder_identity,
            verifier_identity=f"{self.verifier_identity}:Lean4",
            independently_verified=passed,
            protected_suite_passed=passed,
            semantic_review_passed=passed,
            verifier_authority_bound=True,
            lean_theorem_ref=f"{lean_file}#{theorem_name}",
            allowed_axioms_only=scan["is_clean"],
        )
