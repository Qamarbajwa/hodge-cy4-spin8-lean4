"""Adversarial Reviewer tests for Event 31: Computational Experiment Frontiers & 43/43 Lean Finite Checks."""

from __future__ import annotations

import sys
from pathlib import Path

_REPO_ROOT = str(Path(__file__).resolve().parent.parent)
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

from toolkit.cmi_five_condition_attack_engine import (
    CMIFiveConditionAttackEngine,
    IrreducibleSixVarCrossCoupledCY4Engine,
    KugaSatakeTrialityTransferEngine,
    LiaisonGotzmannDegreeCompressor,
)
from toolkit.governance.lean_step_runner import check_step, sha as sha_bytes
from toolkit.integrity import scan_forbidden


def test_01_condition_1_liaison_gotzmann_socle_bypass() -> None:
    res = LiaisonGotzmannDegreeCompressor().verify_liaison_compression()
    assert res["plane_liaison_d1_1_d2_1"]["ranks"] == [3, 6, 10, 15, 18, 19]
    assert res["plane_liaison_d1_1_d2_1"]["gotzmann_regularity"] == 1
    q = res["quadric_liaison_d1_2_d2_2"]
    assert q["deg_Z22"] == 22
    assert q["ci_degree"] == 24
    assert q["deg_Q2"] == 2
    assert q["above_socle_ceiling_22_gt_12"] is True
    assert q["residual_inside_socle_2_le_12"] is True
    assert q["ranks"] == [4, 9, 16, 24, 30, 32]
    assert q["annihilator_dims"] == [2, 12, 40, 102, 216, 394]
    assert q["gotzmann_regularity"] == 2
    assert q["ann2_quadratic_generator_x0_x3_present"] is True
    assert q["exact_shadow_inversion_M_Z22_eq_neg_M_Q2"] is True
    assert res["families_verified_count"] == 5


def test_02_condition_2_non_separable_6var_coupled_cy4() -> None:
    res = IrreducibleSixVarCrossCoupledCY4Engine().verify_coupled_cy4_stabilization()
    assert res["all_6_vars_coupled"] is True
    assert res["cube_ideal_dw_in_i_pi_squared"] is True
    assert res["hilbert_d12_verified"] is True
    assert res["hilbert_d5_to_d10_all_3_primes_agree"] is True
    assert res["macaulay_ranks"] == [3, 6, 10, 15, 18, 19]
    assert res["rank_sum_with_deg0"] == 72
    assert res["ann_R1_dim"] == 3
    assert res["gotzmann_regularity"] == 1


def test_03_conditions_3_4_kuga_satake_triality_and_weyl_inversion() -> None:
    res = KugaSatakeTrialityTransferEngine().verify_triality_transfer_and_weyl_inversion()
    assert res["triality_zero_triples"] == 32
    assert res["sym2_v8_orbit_rank"] == 35
    assert res["sym2_sminus_orbit_rank"] == 35
    assert res["total_wedge4_transfer_rank"] == 70
    assert res["zero_weight_k22_rank"] == 6
    assert res["b_weyl_matrix_rank"] == 6
    assert res["b_weyl_invertible_over_Q"] is True


def test_04_condition_5_open_frontier_and_zero_floats() -> None:
    master = CMIFiveConditionAttackEngine().run_full_audit()
    assert master["condition_5_open_frontier"]["universal_quantifier_status"] == "OPEN"
    assert master["scan_forbidden_hits"] == 0
    assert scan_forbidden(str(Path(__file__).resolve())) == []
    assert master["honesty_boundary"]["GLOBAL_HODGE_CONJECTURE"] == "OPEN"
    assert master["honesty_boundary"]["release_authorized"] is False


def test_05_lean_node12_13_finite_checks_zero_axioms() -> None:
    bp_bytes = (Path(_REPO_ROOT) / "lean_blueprint" / "HodgeVerification.lean").read_bytes()
    lean_dir = Path(_REPO_ROOT) / "examples" / "math_gov" / "LeanDemoProject"
    demo_bytes = (lean_dir / "HodgeVerification.lean").read_bytes()
    assert bp_bytes == demo_bytes
    lean_sha = sha_bytes(demo_bytes)
    specs = [
        (
            "finite_non_fermat_pair_milnor_and_ranks_eq",
            "(nf_pair_milnor == 25 && "
            "nf_total_milnor == milnor_number && "
            "1 :: nf_plane_ranks == deformed_macaulay_flat_hilbert && "
            "([1, 2, 3, 4, 5, 6].map nf_sum_pairs == [6, 21, 56, 126, 246, 426]) && "
            "nf_sum_pairs 12 == h22_prim && "
            "nf_sum_pairs 18 == h31_prim && "
            "6 - 3 == 3 && "
            "6 - 4 == 2) = true",
        ),
        (
            "noether_macaulay_gorenstein_symmetry_eq",
            "(cy4_socle_degree == 24 && "
            "cy4_middle_degree == 12 && "
            "cy4_hilbert_series.length == 25 && "
            "cy4_hilbert_series == cy4_hilbert_series.reverse && "
            "nf_sum_pairs 0 == 1 && "
            "nf_sum_pairs 12 == h22_prim && "
            "nf_sum_pairs 24 == 1) = true",
        ),
        (
            "weyl_d4_spinor_weight_decomposition_eq",
            "(four_tuples.length == 70 && "
            "wedge4_spinor_self_dual_dim + wedge4_spinor_anti_self_dual_dim == four_tuples.length && "
            "zero_weight_tuples.length == 6 && "
            "mumford_stacked_root_rank == zero_weight_tuples.length && "
            "weyl_d4_group_order == 192 && "
            "triality_zero_triples.length == 32) = true",
        ),
    ]
    for name, stmt in specs:
        res = check_step(str(lean_dir), "HodgeVerification.lean", name, stmt, lean_sha)
        assert res["lean_kernel_check_passed"] is True, res
        assert res["axioms"] == [], res
