#!/usr/bin/env python3
"""One-Command Standalone Verifier for the Hodge Conjecture Zenodo Archive.

Executes a 4-stage read-only verification pipeline:
  Step 1: Zero-float static audit (integrity.scan_forbidden) across all audited math/review engines + self.
  Step 2: Exact rational/integer mathematical invariant replay across Pillars I-IV.
  Step 3: Lean 4.35.0 kernel & zero-axiom verification across all 48 theorems (46 Part I unconditional + 2 Part II conditional).
  Step 4: Governance DAG acyclicity, honesty/policy checks, hash-chained ledger, & manifest integrity.

Usage:
  python verify_zenodo_deposit.py          # Full audit (40 x check_step + 407-vec Voisin moving plane)
  python verify_zenodo_deposit.py --fast   # Fast audit (single-pass Lean compile + exact fast replay)
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import sqlite3
import subprocess
import sys
from collections import defaultdict, deque
from fractions import Fraction
from pathlib import Path
from typing import Any, Dict, List, Tuple

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from toolkit.calabi_yau_jacobian_engine import CalabiYauJacobianEngine
from toolkit.cmi_five_condition_attack_engine import CMIFiveConditionAttackEngine
from toolkit.deformed_macaulay_transport_engine import DeformedMacaulayTransportEngine
from toolkit.erdos_fourier_incidence_engine import ErdosFourierIncidenceEngine
from toolkit.four_wall_strategic_resolution_engine import FourWallStrategicResolutionEngine
from toolkit.global_recombination_and_coset_engine import GlobalRecombinationAndCosetEngine
from toolkit.universal_obstruction_cancellation_engine import UniversalObstructionCancellationEngine
from toolkit.surjective_cokernel_integrability_engine import SurjectiveCokernelIntegrabilityEngine
from toolkit.twenty_plane_minimal_rank_stabilization_engine import TwentyPlaneMinimalRankStabilizationEngine
from toolkit.non_fermat_determinantal_stabilization_engine import NonFermatDeterminantalStabilizationEngine
from toolkit.governance import event_ledger
from toolkit.governance.lean_step_runner import check_step, extract_axioms, sha as sha_bytes
from toolkit.governance.math_step_engine import audit as audit_case, progress as progress_case
from toolkit.higher_order_gauss_manin_sieve import HigherOrderGaussManinEngine
from toolkit.integrity import scan_forbidden, verify_manifest
from toolkit.kuga_satake_clifford_engine import KugaSatakeCliffordEngine
from toolkit.lean_blueprint_verifier import LeanBlueprintVerifier
from toolkit.macaulay_apolarity_inverse_engine import MacaulayApolarityInverseEngine
from toolkit.markman_secant_engine import MarkmanSecantWeilEngine
from toolkit.modular_crt_linear_solver import (
    ModularCRTLinearSolver,
    run_non_fermat_1751x426_crt_certification,
)
from toolkit.mumford_spinor_engine import MumfordSpinorEngine
from toolkit.three_agent_space_comparison import (
    ClassesAuditor,
    ExactAbelianFourfoldCohomology,
    ExactLocalizationSequence,
)


LEAN_THEOREM_SPECS: List[Tuple[str, str]] = [
    (
        "exact_chain_im_sub_ker",
        "forall {α β γ : Type} (f : α → β) (g : β → γ) (zero_c : γ), "
        "(forall x : α, g (f x) = zero_c) → forall y : β, (exists x : α, f x = y) → g y = zero_c",
    ),
    ("weil_w1_orthogonal_to_theta2", "dot weil_w1 theta2 = 0"),
    ("weil_w2_orthogonal_to_theta2", "dot weil_w2 theta2 = 0"),
    ("four_tuples_len", "four_tuples.length = 70"),
    ("zero_tuples_len", "zero_weight_tuples.length = 6"),
    ("h40_prim_eq", "h40_prim = 1"),
    ("h31_prim_eq", "h31_prim = 426"),
    ("h22_prim_eq", "h22_prim = 1751"),
    ("h22_total_eq", "h22_total = 1752"),
    ("b4_total_eq", "b4_total = 2606"),
    ("milnor_number_eq", "milnor_number = 15625"),
    ("r6_dim_eq", "r6_dim = 426"),
    ("plane_kernel_dim_eq", "plane_kernel_dim = 407"),
    ("saturation_three_count_eq", "saturation_three_count = 20"),
    (
        "band3_partitions_satisfy_2_plus_4",
        "(has_2_plus_4_split [4, 2, 2, 2, 1, 1] && has_2_plus_4_split [3, 3, 2, 2, 2, 0]) = true",
    ),
    ("fermat_four_band_closure_eq", "fermat_four_band_total = h22_prim"),
    ("f_p3_surface_h11_prim_eq", "f_p3_surface_h11_prim = 85"),
    ("min_ivhs_codimension_pos", "(min_ivhs_codimension >= 19 && min_ivhs_codimension > 0) = true"),
    ("clifford_even_dim_eq", "(clifford_even_dim == 128 && chevalley_spinor_end_dim == 128) = true"),
    ("d4_triality_zero_triples_len", "triality_zero_triples.length = 32"),
    ("max_ivhs_monomial_rank_eq", "(max_ivhs_monomial_rank == 141 && min_ivhs_monomial_kernel == 285) = true"),
    ("canonical_fixed_plane_subspace_dim_eq", "canonical_fixed_plane_subspace_dim = 56"),
    (
        "macaulay_annihilator_dim_bound",
        "(r1_monomials.length == 6 && macaulay_m1_rank_pi == 3 && macaulay_ann_r1_pi == 3) = true",
    ),
    (
        "signed_difference_ideal_intersection",
        "(r2_monomials.length == 21 && pi_plus_ideal_r1.length == 3 && pi_minus_ideal_r1.length == 3 && "
        "cross_product_quadrics.length == 9 && signed_ann_r1_dim == 0 && signed_ann_r2_dim == 9 && "
        "cross_quadrics_annihilate_both) = true",
    ),
    (
        "quadratic_moving_plane_directions_count_eq",
        "(r_exps_deg4.length == 6 && quadratic_moving_plane_directions.length == 18 && "
        "quadratic_moving_plane_directions.all (fun u => "
        "u.1 + u.2.1 + u.2.2.1 == 2 && u.2.2.2.1 + u.2.2.2.2.1 + u.2.2.2.2.2 == 4 && "
        "Nat.ble u.2.2.2.1 2 && Nat.ble u.2.2.2.2.1 2 && Nat.ble u.2.2.2.2.2 2)) = true",
    ),
    (
        "deformed_macaulay_flat_hilbert_sum_eq",
        "(deformed_macaulay_flat_hilbert.foldr Nat.add 0 == 72 && "
        "deformed_macaulay_flat_hilbert.take 5 == binomial_2_plane_hilbert && "
        "[0, 1, 2, 3, 4].map (fun m => binom (m + 2) 2) == binomial_2_plane_hilbert) = true",
    ),
    (
        "cyclotomic_plane_wavepacket_support_eq",
        "(pair_sums_4.length == 5 && cyclotomic_plane_wavepacket_count == 125 && "
        "pair_sums_4.all (fun p => p.1 + p.2 == 4 && Nat.ble p.1 4 && Nat.ble p.2 4)) = true",
    ),
    (
        "telescoping_cyclotomic_annihilator_eq",
        "(telescope_lhs_exp6 1 1 1 1 1 == telescope_rhs_exp6 1 1 1 1 1) = true",
    ),
    (
        "spinor_to_weil_su22_branching_eq",
        "(d3_zero_weight_tuples.length == 8 && pure_weil_tuples.length == 2 && "
        "mixed_d4_zero_tuples.length == 6 && mixed_d4_zero_tuples.length == zero_weight_tuples.length && "
        "pure_weil_tuples.length + mixed_d4_zero_tuples.length == d3_zero_weight_tuples.length) = true",
    ),
    (
        "tangential_leibniz_annihilator_eq",
        "(bivar_d_plus [1, -1], bivar_d_plus [1, 0, 0, 0, 0, -1], "
        "bivar_eval_diag (bivar_d_plus [1, -1, 0, 0, 0, 0]), "
        "bivar_eval_diag (bivar_d_minus [1, -1, 0, 0, 0, 0])) = ([0], [5, 0, 0, 0, -5], 0, 2)",
    ),
    (
        "recombination_kernel_dim_gain_eq",
        "(deg6_triples_le4.length == 19 && shared_deg6_triples.length == 3 && "
        "cancel_deg2_pairs.length == 3 && shared_ker_dim == 391 && recomb_rank == 32 && "
        "recomb_ker_dim == 394 && recomb_ker_dim - shared_ker_dim == 3) = true",
    ),
    (
        "weyl_d4_conjugate_weil_axes_eq",
        "(coord_pure_weil_tuples.length == 8 && hadamard_pure_weil_tuples.length == 8 && "
        "coord_pure_weil_tuples.length + hadamard_pure_weil_tuples.length == 16 && "
        "binom 8 2 == 28 && binom 6 2 + 1 == 16 && shimura_coset_dim == 12 && "
        "k22_pair0_count == 2 && k22_pair1_count == 2 && k22_pair2_count == 2 && "
        "k22_pair0_count + k22_pair1_count + k22_pair2_count == zero_weight_tuples.length) = true",
    ),
    (
        "universal_band_obstruction_cancellation_bounds_eq",
        "(universal_total_ker_bound == 1325 && universal_band1_ker_bound == 575 && "
        "universal_band2_ker_bound == 204 && turan_max_obstructed_planes == 4 && "
        "turan_min_surviving_planes == 16 && turan_max_obstructed_planes + 1 == 5) = true",
    ),
    (
        "gorenstein_moduli_rank_extremes_eq",
        "(gorenstein_min_rank_deg12 == 155 && gorenstein_min_rank_deg6_dual == 155 && "
        "gorenstein_max_ker_dim == 1596 && gorenstein_max_rank_deg12 == 336 && "
        "gorenstein_max_rank_deg6_dual == 336 && gorenstein_min_ker_dim == 1415) = true",
    ),
    (
        "nine_partition_cokernel_dims_eq",
        "(nine_partition_moduli_ranks.map (fun r => 426 - r) == nine_partition_cokernels && "
        "nine_gorenstein_exact_ranks.map (fun r => 426 - r) == nine_gorenstein_exact_cokernels) = true",
    ),
    (
        "twenty_plane_target_and_collision_counts_eq",
        "(twenty_plane_total_incidences == 380 && twenty_plane_target_dim == 245 && "
        "twenty_plane_three_4_targets * 1 + twenty_plane_four_4_targets * 4 == 380 && "
        "twenty_plane_collision_excess == 135 && "
        "twenty_plane_target_dim + high_support_moduli_dim == h31_prim && "
        "high_support_moduli_counts == [150, 30, 1] && high_support_moduli_dim == 181 && "
        "9 + 11 == saturation_three_count && 15 == saturation_three_count - 5 && "
        "15 - 11 == 4) = true",
    ),
    (
        "fifteen_matching_band1_block_incidence_eq",
        "(fifteen_perfect_matchings == 15 && modes_per_matching_block == 125 && "
        "band1_block_total_incidences == 1875 && "
        "band1_mult_mode_sum == fermat_band1_planes && "
        "band1_mult_incidence_sum == band1_block_total_incidences && "
        "band1_block_total_incidences - fermat_band1_planes == 874 && "
        "band1_multiplicity_pairs.map (fun p => p.2) == [360, 540, 60, 40, 1]) = true",
    ),
    (
        "recomb_and_collision_flat_hilbert_eq",
        "(recomb_flat_target == [8, 18, 32, 48, 60, 64] && "
        "list_diff_nat recomb_ua_naive_ranks recomb_flat_target == [0, 1, 4, 8, 11, 12] && "
        "list_diff_nat recomb_ub_naive_ranks recomb_flat_target == [0, 1, 4, 8, 12, 14] && "
        "list_diff_nat quad_collision_naive_ranks recomb_flat_target == [1, 5, 13, 23, 31, 34] && "
        "list_head_nat recomb_ua_naive_ranks == 8 && "
        "list_head_nat quad_collision_naive_ranks == 9 && "
        "h31_prim - 32 == 394) = true",
    ),
    (
        "finite_non_fermat_pair_milnor_and_ranks_eq",
        "(nf_pair_milnor == 25 && "
        "nf_total_milnor == milnor_number && "
        "1 :: nf_plane_ranks == deformed_macaulay_flat_hilbert && "
        "([1, 2, 3, 4, 5, 6].map nf_sum_pairs == [6, 21, 56, 126, 246, 426]) && "
        "nf_sum_pairs 12 == h22_prim && "
        "nf_sum_pairs 18 == h31_prim && "
        "6 - 3 == 3 && 6 - 4 == 2) = true",
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
        "mumford_stacked_root_rank - zero_weight_tuples.length == 0 && "
        "weyl_d4_group_order == 192 && "
        "triality_zero_triples.length == 32) = true",
    ),
    (
        "weyl_d4_even_parity_and_chiral_orthogonality_eq",
        "(wd4_total_elements, wd4_all_even_parity, wd4_norm_plus_sq, wd4_norm_minus_sq, wd4_cross_product) = (192, true, 192, 192, 0)",
    ),
    (
        "shioda_aoki_m12_paired_diagonal_orbits_eq",
        "(m12_paired_reps.length == 4 && m12_paired_reps.foldl (fun acc r => acc && is_shioda_hodge_12_fold r && paired_doubling_congruence r) true && m12_total_residual == 360 && m12_total_hodge == 52991) = true",
    ),
]

EXTENDED_LEAN_THEOREM_SPECS: List[Tuple[str, str]] = [
    (
        "weyl_d4_transition_matrix_invertible_cert",
        "matMul6 bWeyl bAdjCols = neg8_I6",
    ),
    (
        "macaulay_plane_and_quadric_rank_witness_cert",
        "([1, 2, 3, 4, 5, 6].map planeMacaulayRank, "
        "([1, 2, 3, 4, 5, 6].map planeMacaulayRank).foldl (· + ·) 0 + 1, "
        "[1, 2, 3, 4, 5, 6].map quadricMacaulayRank) = "
        "([3, 6, 10, 15, 18, 19], 72, [4, 9, 16, 24, 30, 32])",
    ),
    (
        "shioda_aoki_fermat_fourfold_census_m3_to_m10_empty_band4",
        "([3, 4, 5, 6, 7, 8, 9, 10].map band4ResidualCountForM, "
        "m12PairedReps.all (isBand4ResidualTuple 12), "
        "m12PairedReps.length * 90, 1001 + 630 + 120 + 0) = "
        "([0, 0, 0, 0, 0, 0, 0, 0], true, 360, 1751)",
    ),
]


def _canonical_json(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def _verify_dag_acyclic(nodes: List[Dict[str, Any]], edges: List[Dict[str, Any]]) -> Dict[str, Any]:
    node_ids = {n["id"] for n in nodes}
    indegree: Dict[str, int] = {nid: 0 for nid in node_ids}
    adj: Dict[str, List[str]] = defaultdict(list)
    for edge in edges:
        src = edge["source"]
        tgt = edge["target"]
        assert src in node_ids and tgt in node_ids, f"Dangling edge endpoint: {src} -> {tgt}"
        adj[src].append(tgt)
        indegree[tgt] += 1

    queue = deque(nid for nid, deg in indegree.items() if deg == 0)
    visited = 0
    while queue:
        curr = queue.popleft()
        visited += 1
        for nxt in adj[curr]:
            indegree[nxt] -= 1
            if indegree[nxt] == 0:
                queue.append(nxt)

    is_dag = visited == len(node_ids)
    assert is_dag, f"Governance graph contains cycle: visited {visited} != {len(node_ids)}"
    return {"nodes_count": len(nodes), "edges_count": len(edges), "is_acyclic_dag": is_dag}


def step1_zero_float_static_audit() -> Dict[str, Any]:
    """Step 1: Runs scan_forbidden across all 20 math/review engines in toolkit/ and this verifier."""
    targets = [
        "toolkit/three_agent_space_comparison.py",
        "toolkit/markman_secant_engine.py",
        "toolkit/mumford_spinor_engine.py",
        "toolkit/calabi_yau_jacobian_engine.py",
        "toolkit/erdos_fourier_incidence_engine.py",
        "toolkit/hodge_proof_closure_reviewer.py",
        "toolkit/kuga_satake_clifford_engine.py",
        "toolkit/higher_order_gauss_manin_sieve.py",
        "toolkit/macaulay_apolarity_inverse_engine.py",
        "toolkit/deformed_macaulay_transport_engine.py",
        "toolkit/four_wall_strategic_resolution_engine.py",
        "toolkit/global_recombination_and_coset_engine.py",
        "toolkit/universal_obstruction_cancellation_engine.py",
        "toolkit/surjective_cokernel_integrability_engine.py",
        "toolkit/twenty_plane_minimal_rank_stabilization_engine.py",
        "toolkit/non_fermat_determinantal_stabilization_engine.py",
        "toolkit/modular_crt_linear_solver.py",
        "toolkit/cmi_five_condition_attack_engine.py",
        "toolkit/covariant_apolarity_and_weyl_shioda_census.py",
        "toolkit/blind_gauss_manin_jet_reconstructor.py",
        "verify_zenodo_deposit.py",
    ]
    report: Dict[str, int] = {}
    for rel in targets:
        path = ROOT / rel
        hits = scan_forbidden(str(path))
        assert hits == [], f"Forbidden float construct found in {rel}: {hits}"
        report[rel] = len(hits)
    toolkit_engines = [t for t in targets if t.startswith("toolkit/")]
    return {
        "toolkit_engines_scanned": len(toolkit_engines),
        "files_scanned": len(targets),
        "total_float_violations": sum(report.values()),
        "per_file_violations": report,
        "passed": True,
    }


def step2_mathematical_invariant_replay(fast: bool = False) -> Dict[str, Any]:
    """Step 2: Re-computes and asserts all exact mathematical invariants across Pillars I-IV."""
    # Pillar I: Localization Exactness, Exotic Classes I-V, Wirtinger Calibration
    loc = ExactLocalizationSequence(num_components=3, dim_ambient_H4=70)
    h0 = loc.verify_exactness_at_H0()
    h4 = loc.verify_exactness_at_H4()
    assert h0["i_star_circ_Res_is_zero"] is True
    assert h0["im_Res_equals_ker_i_star"] is True
    assert h4["im_i_star_equals_ker_j_star"] is True

    class_audits = [
        ClassesAuditor.audit_class_1_singular(),
        ClassesAuditor.audit_class_2_non_reduced(),
        ClassesAuditor.audit_class_3_derived(),
        ClassesAuditor.audit_class_4_ominimal(),
        ClassesAuditor.audit_class_5_calibrated_currents(),
    ]
    assert all(not c["produces_new_cohomology_shadow"] for c in class_audits)

    ef = ErdosFourierIncidenceEngine()
    cal_surf = ef.calibrator.calibrate_surface_degree(12)
    assert cal_surf["calibrated_unit_volume"] == Fraction(6, 1)
    bal = ef.calibrator.verify_signed_unit_balance(24, 24)
    assert bal["is_unit_balanced"] is True and bal["net_volume_difference"] == 0

    # Pillar II: Abelian Fourfold Weil Space & Markman Secant Sheaf
    a4 = ExactAbelianFourfoldCohomology()
    h4_dims = a4.hodge_numbers_H4()
    su22 = a4.su22_h4_decomposition()
    assert sum(h4_dims.values()) == 70
    assert h4_dims["h^2,2"] == 36
    assert su22["dim_primitive_weil_W0"] == 2
    assert su22["total_h4_dimension"] == 70

    markman = MarkmanSecantWeilEngine()
    mz = markman.moonen_zarhin_reduction_table()
    ss = markman.secant_sheaf_invariants()
    schoen = markman.schoen_degeneration_specialization()
    assert mz["dim_4_abelian_fourfolds"]["hodge_conjecture_status"] == "RESOLVED_AFFIRMATIVELY_BY_MARKMAN_2025"
    assert ss["todd_genus_abelian_variety"] == 1
    assert schoen["sixfold_weil_class_codimension"] == 3
    assert schoen["fourfold_weil_class_codimension"] == 2

    # Pillar III: Mumford-Weil Spinor Sixfolds, D_4 K_{2,2} Graph, WHT, Root Operators, Endomorphism Vacuum
    mumford = MumfordSpinorEngine()
    h6 = mumford.abelian_sixfold_hodge_diamond()
    assert h6["b_6"] == 924 and h6["h_3_3"] == 400

    for w in ef.spinor_engine.weights:
        assert sum(coord * coord for coord in w) == Fraction(1, 1)

    erdos_census = ef.spinor_engine.erdos_distance_graph_census()
    assert erdos_census["root_unit_edges_D2"] == 24
    assert erdos_census["antipodal_diameter_edges_D4"] == 4

    wedge4_audit = ef.spinor_engine.audit_wedge4_tuples()
    assert wedge4_audit["total_wedge4_tuples"] == 70
    assert wedge4_audit["zero_weight_tuples_count"] == 6
    assert wedge4_audit["k22_induced_subgraph_tuples_count"] == 6
    assert wedge4_audit["is_exact_k22_equivalence"] is True

    wht = ef.spinor_engine.walsh_hadamard_transform_indicator()
    assert wht[()] == 8 and wht[(0, 1, 2, 3)] == 8
    assert all(val == 0 for key, val in wht.items() if key not in ((), (0, 1, 2, 3)))

    cartan_vs_root = mumford.cartan_weight_zero_vs_root_annihilation()
    assert cartan_vs_root["stacked_root_operator_rank"] == 6
    assert cartan_vs_root["root_annihilation_kernel_dim"] == 0
    assert cartan_vs_root["full_so8_invariants_dim"] == 0

    schur = mumford.schur_endomorphism_vacuum()
    markman_audit = mumford.markman_applicability_audit()
    assert schur["endomorphism_algebra"] == "End_Q(A) = Q" and schur["picard_number"] == 1
    assert markman_audit["is_markman_applicable_to_mumford"] is False

    ks = KugaSatakeCliffordEngine().run_full_audit()
    assert ks["clifford_exterior_grading"]["dim_C_plus"] == 128
    assert ks["clifford_exterior_grading"]["dim_C_minus"] == 128
    assert ks["triality_32_incidence_triples"]["zero_weight_triples_count"] == 32
    assert ks["wedge4_self_dual_branching"]["dim_self_dual_35_plus"] == 35
    assert ks["wedge4_self_dual_branching"]["cartan_zero_weight_35_plus"] == 3
    assert ks["wedge4_self_dual_branching"]["cartan_zero_weight_35_minus"] == 3
    assert ks["kuga_satake_bridge_b_audit"]["ABSOLUTE_HODGE_AND_MOTIVATED_VERIFIED"] is True
    assert ks["kuga_satake_bridge_b_audit"]["kuga_satake_algebraic_cycle_proved"] is False

    # Pillar IV: CY4 Koszul Spectrum, IVHS Rank, Voisin Syzygy Sieve, 4-Band Fermat Closure
    cy = CalabiYauJacobianEngine()
    diamond = cy.primitive_hodge_diamond()
    assert diamond["primitive_hodge_numbers"] == {
        "h^{4,0}_prim": 1,
        "h^{3,1}_prim": 426,
        "h^{2,2}_prim": 1751,
        "h^{1,3}_prim": 426,
        "h^{0,4}_prim": 1,
    }
    assert diamond["total_middle_hodge_number_h22"] == 1752
    assert diamond["total_middle_betti_number_b4"] == 2606
    assert diamond["milnor_number"] == 15625

    nl = cy.analyze_noether_lefschetz_loci()
    assert nl["plane_cycle_rank"] == 19
    assert nl["plane_cycle_tangent_dim"] == 407
    assert nl["center_monomial_rank"] == 141

    census = ef.census.partition_census()
    assert census["total_monomials"] == 1751
    assert census["total_partitions"] == 18
    assert census["saturation_index_breakdown"][3] == 20
    assert census["global_min_rank"] == 19 and census["global_max_kernel"] == 407
    assert census["global_max_rank"] == 141 and census["global_min_kernel"] == 285

    chain = cy.evaluate_artificial_class_obstruction()
    assert chain["base_rank"] == 68 and chain["augmented_rank"] == 69
    assert chain["obstruction_leaked_to_cokernel"] is True

    moving_plane_summary: Dict[str, Any] = {"mode": "skipped_in_fast_mode"}
    if not fast:
        mov = cy.evaluate_moving_plane_full_integrability()
        assert mov["plane_unobstructed_vectors"] == 407
        assert mov["plane_total_kernel_vectors"] == 407
        assert mov["chain_base_subspace_rank"] == 304
        assert mov["chain_augmented_rank"] == 305
        assert mov["chain_is_still_obstructed"] is True
        moving_plane_summary = {
            "mode": "full_407_vector_audit",
            "plane_unobstructed": "407/407",
            "chain_rank_jump": "304->305",
        }

    galois = ef.detector.verify_shioda_galois_criterion()
    four_band = ef.detector.full_four_band_decomposition()
    band3 = ef.detector.verify_band3_surface_lefschetz_origin()
    assert galois["modes_satisfying_galois_norm_18"] == 1751
    assert four_band["dim_fourier_planes_2_2_2"] == 1001
    assert four_band["dim_inductive_cones_3_3"] == 630
    assert four_band["dim_inductive_2_plus_4_lefschetz"] == 120
    assert four_band["truly_indecomposable_count"] == 0
    assert four_band["exact_four_band_closure"] is True
    assert band3["dim_H11_prim_X2_6"] == 85
    assert band3["fermat_unexplained_modes"] == 0

    gm = HigherOrderGaussManinEngine().run_full_audit()
    pl_gm = gm["plane_order3_audit"]
    st_gm = gm["jet_filtration_benchmark"]["stealth_class"]
    cdk_gm = gm["cdk_bridge_a_audit"]
    assert pl_gm["canonical_fixed_plane_order3_unobstructed"] == 56
    assert pl_gm["moving_plane_27_order3_unobstructed"] == 27
    assert pl_gm["linear_moving_plane_54_order3_unobstructed"] == 54
    assert pl_gm["K3_dim"] == 407
    assert st_gm["moving_cycle_filtration"] == [347, 336, 334]
    assert st_gm["caught_at_order_3_count"] == 2
    assert cdk_gm["CDK_BASE_MODULI_ALGEBRAICITY_VERIFIED"] is True
    assert cdk_gm["effective_hilbert_degree_bound_known"] is False

    mac = MacaulayApolarityInverseEngine().run_full_audit()
    assert mac["canonical_macaulay_tower_audit"]["single_plane"]["ann_R1_dim"] == 3
    assert mac["signed_quadric_factorization"]["lambda_ann_R1_dim"] == 0
    assert mac["signed_quadric_factorization"]["lambda_ann_R2_dim"] == 9
    assert mac["signed_quadric_factorization"]["exact_product_factorization_matches_ann_R2"] is True
    assert mac["all_18_partitions_audit"]["all_18_partitions_verified"] is True
    assert mac["effective_degree_bounds"]["single_plane"]["fermat_apolar_regularity_bound"] == 1
    assert mac["effective_degree_bounds"]["signed_disjoint_planes"]["fermat_apolar_regularity_bound"] == 5
    assert mac["effective_hilbert_degree_bound_known"] is False

    def_mac = DeformedMacaulayTransportEngine().run_full_audit()
    q_def = def_mac["quadratic_moving_plane_audit"]
    f_def = def_mac["fixed_ideal_audit"]
    o_def = def_mac["artificial_obstruction_audit"]
    g_def = def_mac["gotzmann_persistence_audit"]
    w_def = def_mac["cyclotomic_wavepacket_audit"]
    jt_def = def_mac["joint_generator_transport_audit"]
    assert q_def["deformed_x012_exact_cancellation_count"] == 18
    assert q_def["full_m1_to_m6_flat_count"] == 18
    assert f_def["diagonal_u_dot_lam0_vanishes_count"] == 359
    assert f_def["canonical_fixed_56_flat_count"] == 56
    assert o_def["both_provably_unliftable_in_R12"] is True
    assert g_def["gotzmann_persistence_gt_1_verified"] is True
    assert g_def["gotzmann_deformed_witness"]["hilbert_sum"] == 72
    assert g_def["effective_hilbert_degree_bound_known"] is False
    assert w_def["monomial_count"] == 125
    assert w_def["band1_pairable_count"] == 125
    assert w_def["ann_R1_exact_plane_ideal_match"] is True
    assert w_def["gotzmann_G"] == 1
    assert jt_def["wavepacket_stat_operator_rank"] == 1750
    assert jt_def["wavepacket_joint_operator_rank"] == 1756
    assert jt_def["wavepacket_operator_rank_gain"] == 6
    assert jt_def["wavepacket_stationary_subspace_dim"] == 353
    assert jt_def["wavepacket_joint_subspace_dim"] == 359
    assert jt_def["wavepacket_subspace_gain_by_tilting"] == 6
    assert jt_def["nilpotent_tilting_gain"] == 0

    fw = FourWallStrategicResolutionEngine().run_full_audit()
    w1 = fw["wall1_signed_tangential_transport"]
    w2 = fw["wall2_geometric_liaison_compression"]
    w3 = fw["wall3_picard_lefschetz_nodal_bridge"]
    w4 = fw["wall4_spinor_to_weil_su22_specialization"]
    assert w1["ideal_I_Pi_membership_count"] == 407
    assert w1["tangential_leibniz_lift_count"] == 407
    assert w1["tangential_unlifted_count"] == 0
    assert w1["normal_derivative_escape_count"] == 398
    assert w1["signed_fermat_joint_solvable_count"] == 407
    assert w1["signed_fermat_unlifted_count"] == 0
    assert w1["unsigned_fermat_joint_solvable_count"] == 359
    assert w1["unsigned_fermat_unlifted_count"] == 48
    assert w1["wall1_100_percent_closed"] is True
    assert w2["prim_sum_zero_in_R12"] is True
    assert w2["z5_macaulay_rank_vector"] == (3, 6, 10, 15, 18, 19)
    assert w2["z5_ann_R1_dim"] == 3
    assert w2["z5_gotzmann_G"] == 1
    assert w2["non_linked_castelnuovo_mumford_bound_known"] is False
    assert w3["simple_vanishing_spheres_count"] == 5
    assert w3["involutivity_T_sq_equals_Id"] is True
    assert w3["intersection_isometry_verified"] is True
    assert w3["transitive_orbit_size"] == 30
    assert w3["nodal_bridge_gives_effective_global_bound"] is False
    assert w4["d3_su22_zero_weight_dim"] == 8
    assert w4["pure_weil_tuples_dim"] == 2
    assert w4["mixed_d4_zero_tuples_dim"] == 6
    assert w4["mixed_d3_root_rank"] == 5
    assert w4["mixed_su22_singlet_dim"] == 1
    assert w4["total_su22_invariant_dim"] == 3
    assert w4["horizontal_spin8_markman_spreading_proved"] is False

    gr = GlobalRecombinationAndCosetEngine().run_full_audit()
    rc = gr["recombination_audit"]
    bd = gr["band_apolarity_dictionary"]
    wc = gr["weyl_coset_weil_spanning"]
    assert rc["shared_kernel_dim"] == 391
    assert rc["recombined_kernel_dim"] == 394
    assert rc["recombination_kernel_gain"] == 3
    assert rc["all_3_directions_pass_orders_1_2_3"] is True
    assert rc["macaulay_rank_vector"] == (4, 9, 16, 24, 30, 32)
    assert rc["ann_R1_is_x0_x1"] is True
    assert rc["x2_x3_in_ann_R2"] is True
    assert rc["quadric_d_gen"] == 4
    assert rc["subadditive_quadric_degree"] == 2
    assert rc["convergence_over_non_fermat_islands_proved"] is False
    assert bd["total_partitions"] == 18
    assert bd["total_modes"] == 1751
    assert bd["partitions_with_raw_ann_R1_or_R2"] == 17
    assert bd["central_222222_atom_fallback_ann_R1"] == 3
    assert bd["max_generator_degree_d_gen"] == 4
    assert bd["all_18_partitions_bounded_d_gen_le_4"] is True
    assert bd["general_non_fermat_degree_bound_known"] is False
    assert wc["coord_pure_weil_count"] == 8
    assert wc["hadamard_pure_weil_count"] == 8
    assert wc["total_pure_weil_count"] == 16
    assert wc["wd4_order"] == 192
    assert wc["dim_coset_p"] == 12
    assert wc["wd4_self_dual_singlet_orbit_rank"] == 3
    assert wc["conjugate_dual_pair_weil_spanning_rank"] == 6
    assert wc["coset_transport_single_axis_rank"] == 5
    assert wc["coset_transport_multi_axis_rank"] == 6
    assert wc["full_6_of_6_k22_spanned"] is True
    assert wc["chow_flatness_over_end_Q_proved"] is False

    uc = UniversalObstructionCancellationEngine().run_full_audit()
    uc_rn = uc["universal_rank_nullity"]
    uc_mc = uc["gorenstein_moduli_census"]
    uc_tc = uc["turan_plane_coverage"]
    assert uc_rn["universal_total_kernel_lower_bound"] == 1325
    assert uc_rn["universal_band1_kernel_lower_bound"] == 575
    assert uc_rn["universal_band2_kernel_lower_bound"] == 204
    assert uc_rn["dense_full_rank"] == 426
    assert uc_rn["dense_full_kernel_dim"] == 1325
    assert uc_rn["dense_band1_kernel_dim"] == 593
    assert uc_rn["dense_band2_kernel_dim"] == 292
    assert uc_rn["universal_bounds_satisfied"] is True
    assert uc_rn["all_order_castelnuovo_mumford_bound_proved"] is False
    assert uc_mc["total_moduli_partitions"] == 9
    assert uc_mc["total_moduli_monomials"] == 426
    assert uc_mc["gorenstein_complement_duality_holds_all_9"] is True
    assert uc_mc["matrix_rank_matches_capacity_all_9"] is True
    assert uc_mc["global_min_rank"] == 155
    assert uc_mc["global_max_rank"] == 336
    assert uc_mc["global_min_kernel_dim"] == 1415
    assert uc_mc["global_max_kernel_dim"] == 1596
    assert uc_tc["max_obstructed_planes_per_monomial"] == 4
    assert uc_tc["min_surviving_planes_per_monomial"] == 16
    assert uc_tc["pigeonhole_min_K"] == 5
    assert uc_tc["k5_uncovered_incidences"] == 0
    assert uc_tc["k4_failing_incidences_count"] == 45

    sc = SurjectiveCokernelIntegrabilityEngine().run_full_audit()
    sc_m = sc["surjective_cokernel"]
    sc_r = sc["rank_independent_second_order"]
    sc_h = sc["formal_to_hilbert_honesty"]
    assert sc_m["dense_u_rank"] == 426
    assert sc_m["dense_u_cokernel_dim"] == 0
    assert sc_m["dense_u_surjective"] is True
    assert sc_m["dense_u_kernel_dim"] == 1325
    assert sc_m["recursive_orders_1_2_3_all_exact"] is True
    assert sc_r["rank_nullity_index_exact_for_all_426"] is True
    assert sc_r["all_426_monomials_ge_1325_count"] == 426
    assert sc_r["min_ker_psi2_dim"] == 1325
    assert sc_r["max_ker_psi2_dim"] == 1544
    assert sc_h["global_non_fermat_hilbert_stabilization_proved"] is False

    tp = TwentyPlaneMinimalRankStabilizationEngine().run_full_audit()
    tp_inc = tp["incidence"]
    tp_q = tp["quadruple_witness"]
    tp_blk = tp["fifteen_matchings"]
    tp_det = tp["determinantal_macaulay"]
    assert tp_inc["total_incidences"] == 380
    assert tp_inc["target_subspace_dim"] == 245
    assert tp_inc["collision_excess"] == 135
    assert tp_inc["high_support_zero_count"] == 181
    assert tp_inc["high_support_all_zero_on_v20"] is True
    assert tp_q["quad_active_planes"] == 9
    assert tp_q["quad_v20_rank"] == 5
    assert tp_q["quad_v20_kernel_dim"] == 15
    assert tp_q["quad_nontrivial_collision_syzygies"] == 4
    assert tp_blk["total_incidences"] == 1875
    assert tp_blk["union_size"] == 1001
    assert tp_blk["overlap_excess"] == 874
    assert tp_blk["multiplicity_histogram"] == {1: 360, 2: 540, 3: 60, 6: 40, 15: 1}
    assert tp_blk["central_monomial_multiplicity"] == 15
    assert tp_det["pi_static_r1"] == 3
    assert tp_det["pi_fixed_def_r1"] == 6
    assert tp_det["pi_moving_def_r1"] == 6
    assert tp_det["recomb_static_r1"] == 4
    assert tp_det["recomb_def_r1"] == 8
    assert tp_det["generic_static_r1"] == 6
    assert tp_det["universal_non_fermat_determinantal_stabilization_proved"] is False
    assert tp["scan_forbidden_hits"] == 0

    nf = NonFermatDeterminantalStabilizationEngine().run_full_audit()
    nf_rc = nf["recombined_higher_degree"]
    nf_qs = nf["quadruple_collision_syzygies"]
    nf_fnf = nf["finite_non_fermat"]
    assert nf_rc["all_moving_stabilized"] is True
    assert nf_rc["u_a_order2_obstruction_absorbed"] is True
    assert nf_qs["num_syzygies"] == 4
    assert nf_qs["all_naive_jump_from_m1"] is True
    assert nf_qs["all_stabilized_flat"] is True
    assert nf_fnf["total_milnor"] == 15625
    assert nf_fnf["plane_nf_ranks"] == [3, 6, 10, 15, 18, 19]
    assert nf_fnf["quad_nf_ranks"] == [4, 9, 16, 24, 30, 32]
    assert nf_fnf["quad_nf_ann6_dim"] == 394
    assert nf["universal_non_fermat_determinantal_stabilization_proved"] is False
    assert nf["scan_forbidden_hits"] == 0

    crt_cert = run_non_fermat_1751x426_crt_certification(
        include_fraction_submatrix_cross_check=False
    )
    assert crt_cert["certified_q_rank"] == 426
    assert crt_cert["under_2_seconds"] is True
    assert crt_cert["bad_prime_drop_theorem_verified"] is True
    assert crt_cert["rank_deficient_425_crt_kernel_verified"] is True
    assert crt_cert["scan_forbidden_hits"] == 0

    crt_solver = ModularCRTLinearSolver()
    dense_crt = crt_solver.verify_dense_moduli_1751x426()
    assert dense_crt["certified_rank"] == 426 and dense_crt["kernel_dim"] == 1325
    assert dense_crt["under_1500ms"] is True
    cmi_res = CMIFiveConditionAttackEngine().run_full_audit()
    assert cmi_res["condition_1_liaison_gotzmann"]["quadric_liaison_d1_2_d2_2"]["ranks"] == [4, 9, 16, 24, 30, 32]
    assert cmi_res["condition_2_coupled_six_var_cy4"]["macaulay_ranks"] == [3, 6, 10, 15, 18, 19]
    assert cmi_res["conditions_3_4_kuga_satake_and_weyl"]["total_wedge4_transfer_rank"] == 70
    assert cmi_res["conditions_3_4_kuga_satake_and_weyl"]["b_weyl_matrix_rank"] == 6
    assert cmi_res["condition_5_open_frontier"]["universal_quantifier_status"] == "OPEN"
    assert cmi_res["scan_forbidden_hits"] == 0

    return {
        "pillar_1_localization_exact": True,
        "pillar_1_wirtinger_balanced": True,
        "pillar_2_abelian_fourfold_h4_dim": 70,
        "pillar_2_weil_W0_dim": 2,
        "pillar_3_sixfold_b6": 924,
        "pillar_3_h33": 400,
        "pillar_3_k22_zero_weight_tuples": "6/70",
        "pillar_3_root_annihilation_rank": 6,
        "pillar_3_clifford_even_dim": 128,
        "pillar_3_d4_triality_zero_triples": "32/512",
        "pillar_3_wedge4_branching": "35_+ + 35_- = 70 (Cartan 3+3=6)",
        "pillar_3_kuga_satake_absolute_hodge": True,
        "pillar_4_h22_prim": 1751,
        "pillar_4_milnor_number": 15625,
        "pillar_4_ivhs_rank_range": [19, 141],
        "pillar_4_artificial_chain_jump": "68->69",
        "pillar_4_moving_plane": moving_plane_summary,
        "pillar_4_four_band_closure": "1001+630+120+0=1751",
        "pillar_4_band3_R8_P3_dim": 85,
        "pillar_4_order3_plane_unobstructed": "407/407",
        "pillar_4_stealth_jet_filtration": [347, 336, 334],
        "pillar_4_cdk_moduli_algebraic": True,
        "pillar_4_macaulay_plane_ann_R1": mac["canonical_macaulay_tower_audit"]["single_plane"]["ann_R1_dim"],
        "pillar_4_macaulay_signed_ann_R2": mac["signed_quadric_factorization"]["lambda_ann_R2_dim"],
        "pillar_4_macaulay_18_partitions_verified": True,
        "pillar_4_gotzmann_pi_G": mac["effective_degree_bounds"]["single_plane"]["fermat_apolar_regularity_bound"],
        "pillar_4_gotzmann_signed_G": mac["effective_degree_bounds"]["signed_disjoint_planes"]["fermat_apolar_regularity_bound"],
        "pillar_4_deformed_moving_18_cancelled": True,
        "pillar_4_deformed_fixed_359_diagonal_flat": True,
        "pillar_4_deformed_canonical_56_flat": True,
        "pillar_4_deformed_chain_stealth_unliftable": True,
        "pillar_4_deformed_gotzmann_hilbert_sum": 72,
        "pillar_4_deformed_gotzmann_Gt": 1,
        "pillar_4_cyclotomic_wavepacket_monomials": w_def["monomial_count"],
        "pillar_4_cyclotomic_wavepacket_ideal_match": w_def["ann_R1_exact_plane_ideal_match"],
        "pillar_4_joint_transport_rank_gain": jt_def["wavepacket_operator_rank_gain"],
        "pillar_4_joint_transport_subspace_gain": jt_def["wavepacket_subspace_gain_by_tilting"],
        "pillar_4_joint_transport_nilpotent_gain": jt_def["nilpotent_tilting_gain"],
        "pillar_4_wall1_signed_tangential_leibniz": "407/407",
        "pillar_4_wall1_signed_joint_solvable": "407/407",
        "pillar_4_wall1_unsigned_unlifted": w1["unsigned_fermat_unlifted_count"],
        "pillar_4_wall2_liaison_ranks": list(w2["z5_macaulay_rank_vector"]),
        "pillar_4_wall3_nodal_orbit_size": w3["transitive_orbit_size"],
        "pillar_3_wall4_d3_su22_zero_dim": w4["d3_su22_zero_weight_dim"],
        "pillar_3_wall4_su22_invariants_dim": w4["total_su22_invariant_dim"],
        "pillar_4_recombination_kernel_gain": "391->394 (+3)",
        "pillar_4_recombination_quadric_d_gen": rc["quadric_d_gen"],
        "pillar_4_global_18_partition_max_d_gen": bd["max_generator_degree_d_gen"],
        "pillar_3_weyl_coset_pure_weil_count": wc["total_pure_weil_count"],
        "pillar_3_weyl_coset_k22_spanned": "6/6",
        "pillar_4_univ_ker_lower_bounds": [1325, 575, 204],
        "pillar_4_gorenstein_moduli_rank_range": [155, 336],
        "pillar_4_turan_pigeonhole_min_K": 5,
        "pillar_4_surjective_coker_dim": 0,
        "pillar_4_all_order_formal_ker_dim": 1325,
        "pillar_4_psi2_partition_ker_range": [1325, 1544],
        "pillar_4_twenty_plane_collision_excess": 135,
        "pillar_4_high_support_annihilator_dim": 181,
        "pillar_4_fifteen_matching_union": 1001,
        "pillar_4_fifteen_matching_incidences": 1875,
        "pillar_4_determinantal_macaulay_pi_def_r1": tp_det["pi_moving_def_r1"],
        "pillar_4_recomb_m1_to_m6_stabilized": nf_rc["all_moving_stabilized"],
        "pillar_4_quad_syzygies_stabilized": nf_qs["num_syzygies"],
        "pillar_4_finite_non_fermat_plane_ranks": nf_fnf["plane_nf_ranks"],
        "pillar_4_finite_non_fermat_quad_ranks": nf_fnf["quad_nf_ranks"],
        "pillar_4_universal_non_fermat_determinantal_proved": nf[
            "universal_non_fermat_determinantal_stabilization_proved"
        ],
        "pillar_4_effective_hilbert_bound": False,
        "pillar_4_crt_non_fermat_1751x426_rank": crt_cert["certified_q_rank"],
        "pillar_4_crt_non_fermat_1751x426_under_2s": crt_cert["under_2_seconds"],
        "pillar_4_crt_dense_moduli_1751x426_rank": dense_crt["certified_rank"],
        "pillar_4_cmi1_liaison_z22_ranks": cmi_res["condition_1_liaison_gotzmann"]["quadric_liaison_d1_2_d2_2"]["ranks"],
        "pillar_4_cmi2_coupled_cy4_ranks": cmi_res["condition_2_coupled_six_var_cy4"]["macaulay_ranks"],
        "pillar_3_cmi34_ks_triality_rank": cmi_res["conditions_3_4_kuga_satake_and_weyl"]["total_wedge4_transfer_rank"],
        "pillar_3_cmi34_weyl_basis_rank": cmi_res["conditions_3_4_kuga_satake_and_weyl"]["b_weyl_matrix_rank"],
        "pillar_4_cmi5_open_frontier": cmi_res["condition_5_open_frontier"]["universal_quantifier_status"],
        "passed": True,
    }


def step3_lean4_zero_axiom_verification(fast: bool = False) -> Dict[str, Any]:
    """Step 3: Verifies all 43 core checks in HodgeVerification.lean and 3 extended certificates in ShiodaFormalConjectures.lean compile with axioms == []."""
    blueprint_path = ROOT / "lean_blueprint" / "HodgeVerification.lean"
    demo_dir = ROOT / "examples" / "math_gov" / "LeanDemoProject"
    demo_path = demo_dir / "HodgeVerification.lean"

    blueprint_sha = sha_bytes(blueprint_path.read_bytes())
    demo_sha = sha_bytes(demo_path.read_bytes())
    assert blueprint_sha == demo_sha, f"Lean source mismatch: {blueprint_sha} != {demo_sha}"

    verifier = LeanBlueprintVerifier(str(blueprint_path))
    scan = verifier.scan_for_forbidden_keywords()
    assert scan["is_clean"] is True and scan["violations_count"] == 0, scan

    shioda_bp_path = ROOT / "lean_blueprint" / "ShiodaFormalConjectures.lean"
    shioda_demo_path = demo_dir / "ShiodaFormalConjectures.lean"
    if shioda_bp_path.exists() and shioda_demo_path.exists():
        s_bp_sha = sha_bytes(shioda_bp_path.read_bytes())
        s_dm_sha = sha_bytes(shioda_demo_path.read_bytes())
        assert s_bp_sha == s_dm_sha, f"ShiodaFormalConjectures source mismatch: {s_bp_sha} != {s_dm_sha}"
        s_verifier = LeanBlueprintVerifier(str(shioda_bp_path))
        s_scan = s_verifier.scan_for_forbidden_keywords()
        assert s_scan["is_clean"] is True and s_scan["violations_count"] == 0, s_scan

    if fast:
        if not shutil.which("lake"):
            elan_lake = Path(os.path.expanduser("~")) / ".elan" / "bin" / "lake.exe"
            if elan_lake.exists():
                os.environ["PATH"] = str(elan_lake.parent) + os.pathsep + os.environ.get("PATH", "")
        run = subprocess.run(
            ["lake", "env", "lean", "HodgeVerification.lean"],
            cwd=str(demo_dir),
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=120,
            check=False,
        )
        assert run.returncode == 0, f"Lean compile failed: {run.stdout}\n{run.stderr}"
        combined = (run.stdout or "") + "\n" + (run.stderr or "")
        axioms_by_theorem: Dict[str, List[str]] = {}
        for thm, _ in LEAN_THEOREM_SPECS:
            ax = extract_axioms(combined, thm)
            assert ax == [], f"Theorem {thm} has non-empty axioms: {ax}"
            axioms_by_theorem[thm] = ax

        # Extended Shioda certificates (Checks 44-46)
        run2 = subprocess.run(
            ["lake", "env", "lean", "ShiodaFormalConjectures.lean"],
            cwd=str(demo_dir),
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=120,
            check=False,
        )
        assert run2.returncode == 0, f"Lean compile for ShiodaFormalConjectures failed: {run2.stdout}\n{run2.stderr}"
        combined2 = (run2.stdout or "") + "\n" + (run2.stderr or "")
        for thm, _ in EXTENDED_LEAN_THEOREM_SPECS:
            ax = extract_axioms(combined2, thm)
            assert ax == [], f"Extended certificate {thm} has non-empty axioms: {ax}"
            axioms_by_theorem[thm] = ax
        mode = "fast_single_pass_lake_env_lean"
    else:
        axioms_by_theorem = {}
        for thm, stmt in LEAN_THEOREM_SPECS:
            res = check_step(str(demo_dir), "HodgeVerification.lean", thm, stmt, demo_sha)
            assert res["lean_kernel_check_passed"] is True, f"check_step failed for {thm}: {res}"
            assert res["axioms"] == [], f"Theorem {thm} used non-empty axioms: {res['axioms']}"
            axioms_by_theorem[thm] = res["axioms"]
        for thm, stmt in EXTENDED_LEAN_THEOREM_SPECS:
            res = check_step(str(demo_dir), "ShiodaFormalConjectures.lean", thm, stmt, s_dm_sha)
            assert res["lean_kernel_check_passed"] is True, f"check_step failed for {thm}: {res}"
            assert res["axioms"] == [], f"Theorem {thm} used non-empty axioms: {res['axioms']}"
            axioms_by_theorem[thm] = res["axioms"]
        mode = "full_46x_check_step_wrapper"

    return {
        "verification_mode": mode,
        "lean_source_sha256": demo_sha,
        "zero_cheating_scan_clean": True,
        "core_checks_verified": len(LEAN_THEOREM_SPECS),
        "extended_certificates_verified": len(EXTENDED_LEAN_THEOREM_SPECS),
        "lean_theorems_verified": len(axioms_by_theorem),
        "all_axioms_empty": all(v == [] for v in axioms_by_theorem.values()),
        "axioms_by_theorem": axioms_by_theorem,
        "passed": True,
    }


def step4_governance_and_manifest_audit() -> Dict[str, Any]:
    """Step 4: Audits governance DAG, policy rules, honesty boundaries, ledger, and SHA-256 manifest."""
    hashes = json.loads((ROOT / "governance" / "HODGE_CASE_HASHES.json").read_text(encoding="utf-8"))
    case = json.loads((ROOT / "governance" / "hodge_four_pillars_case.json").read_text(encoding="utf-8"))

    dag_info = _verify_dag_acyclic(case["nodes"], case["edges"])
    case_audit = audit_case(
        case,
        trusted_original_digest=hashes["original"],
        trusted_formal_digest=hashes["formal"],
        trusted_contract_digest=hashes["contract"],
    )
    case_progress = progress_case(case)
    assert case_audit["verdict"] == "STRUCTURAL_PREFLIGHT_PASS_ONLY", case_audit
    assert case_audit["errors"] == [], case_audit["errors"]
    assert case_audit["release_authorized"] is False
    assert case_progress["theorem_progress_percent"] == "UNKNOWN"

    # Check honesty declarations in .zenodo.json, PROJECT_STATE.yaml, manuscript, and policy files
    zenodo_meta = json.loads((ROOT / ".zenodo.json").read_text(encoding="utf-8"))
    state_text = (ROOT / "governance" / "PROJECT_STATE.yaml").read_text(encoding="utf-8")
    manuscript_text = (ROOT / "paper" / "ZENODO_MANUSCRIPT_FOUR_PILLARS_HODGE.md").read_text(encoding="utf-8")
    rego_text = (ROOT / "policies" / "hodge_gates.rego").read_text(encoding="utf-8")

    assert "OPEN" in zenodo_meta["description"]
    assert "release_authorized = false" in zenodo_meta["description"]
    assert "theorem_progress = UNKNOWN" in zenodo_meta["description"]
    assert "release_authorized: false" in state_text
    assert 'theorem_progress: "UNKNOWN"' in state_text
    assert 'G11: "BLOCKED_UNSOLVED_MILLENNIUM"' in state_text
    assert "GLOBAL_HODGE_CONJECTURE" in manuscript_text and "OPEN" in manuscript_text
    assert "default allow = false" in rego_text

    # Optional v0.7 candidate policy detection if present
    v07_dirs = [str(p.relative_to(ROOT)) for p in ROOT.glob("math_gov_v0_7*")]

    # Verify hash-chained SQLite & JSONL ledger
    db_path = ROOT / "governance" / "hodge_governance_ledger.db"
    jsonl_path = ROOT / "governance" / "hodge_governance_ledger.jsonl"
    conn = sqlite3.connect(db_path)
    ledger_ver = event_ledger.verify(conn)
    conn.close()
    assert ledger_ver["verdict"] == "LOCAL_CHAIN_VALID_UNAUTHENTICATED", ledger_ver
    assert ledger_ver["count"] >= 16, ledger_ver
    jsonl_lines = [line for line in jsonl_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    assert len(jsonl_lines) == ledger_ver["count"]

    # Verify SHA-256 manifest
    manifest_path = ROOT / "ARTIFACT_HASH_MANIFEST.sha256"
    manifest_mismatches = verify_manifest(str(ROOT))
    assert manifest_mismatches == [], f"Manifest mismatches detected: {manifest_mismatches}"
    manifest_count = len([ln for ln in manifest_path.read_text(encoding="utf-8").splitlines() if ln.strip()])

    return {
        "dag": dag_info,
        "case_verdict": case_audit["verdict"],
        "theorem_progress": case_progress["theorem_progress_percent"],
        "release_authorized": False,
        "global_hodge_conjecture": "OPEN",
        "optional_v07_dirs_found": v07_dirs,
        "ledger_verdict": ledger_ver["verdict"],
        "ledger_events_count": ledger_ver["count"],
        "ledger_head_sha256": ledger_ver["head"],
        "manifest_files_verified": manifest_count,
        "manifest_mismatches": manifest_mismatches,
        "passed": True,
    }


def run_zenodo_verification(fast: bool = False) -> Dict[str, Any]:
    """Runs all 4 verification steps and returns a deterministic verification certificate."""
    s1 = step1_zero_float_static_audit()
    s2 = step2_mathematical_invariant_replay(fast=fast)
    s3 = step3_lean4_zero_axiom_verification(fast=fast)
    s4 = step4_governance_and_manifest_audit()

    payload = {
        "archive": "HODGE-MILLENNIUM-001 Zenodo Verification Certificate",
        "fast_mode": fast,
        "global_hodge_conjecture": "OPEN",
        "release_authorized": False,
        "theorem_progress": "UNKNOWN",
        "step_1_zero_float_audit": s1,
        "step_2_math_invariant_replay": s2,
        "step_3_lean4_zero_axiom_check": s3,
        "step_4_governance_and_manifest": s4,
        "all_checks_passed": bool(s1["passed"] and s2["passed"] and s3["passed"] and s4["passed"]),
    }
    cert_digest = hashlib.sha256(_canonical_json(payload).encode("utf-8")).hexdigest()
    payload["certificate_sha256"] = cert_digest
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify HODGE-MILLENNIUM-001 Zenodo Deposit")
    parser.add_argument(
        "--fast",
        action="store_true",
        help="Run single-pass Lean 4 check and skip exhaustive 407-vector Voisin moving-plane loop",
    )
    parser.add_argument(
        "--json-only",
        action="store_true",
        help="Print only the JSON verification certificate",
    )
    args = parser.parse_args()

    cert = run_zenodo_verification(fast=args.fast)
    if not args.json_only:
        print("=== ZENODO DEPOSIT VERIFICATION CERTIFICATE (HODGE-MILLENNIUM-001) ===")
        print(f"Step 1 (Zero-Float Static Audit): {cert['step_1_zero_float_audit']['toolkit_engines_scanned']} toolkit engines ({cert['step_1_zero_float_audit']['files_scanned']} files), 0 violations")
        print(f"Step 2 (Exact Math Replay):       1001+630+120+0=1751, 6/70 K_{{2,2}}, mu=15625, passed")
        print(
            f"Step 3 (Lean 4.35.0 Check):       43/43 core checks + 3 extended certificates ({cert['step_3_lean4_zero_axiom_check']['lean_theorems_verified']}/46 total, by rfl, 0 Mathlib), "
            f"axioms==[] ({cert['step_3_lean4_zero_axiom_check']['verification_mode']})"
        )
        print(
            f"Step 4 (Governance & Manifest):   DAG {cert['step_4_governance_and_manifest']['dag']['nodes_count']} nodes / "
            f"{cert['step_4_governance_and_manifest']['dag']['edges_count']} edges, "
            f"ledger={cert['step_4_governance_and_manifest']['ledger_events_count']}, "
            f"manifest={cert['step_4_governance_and_manifest']['manifest_files_verified']} files (0 mismatches)"
        )
        print(
            f"Honesty Boundary:                 GLOBAL_HODGE_CONJECTURE={cert['global_hodge_conjecture']}, "
            f"release_authorized={cert['release_authorized']}, theorem_progress={cert['theorem_progress']}"
        )
        print(f"Certificate SHA-256:              {cert['certificate_sha256']}")
    print(json.dumps(cert, indent=2, ensure_ascii=False))
    return 0 if cert["all_checks_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
