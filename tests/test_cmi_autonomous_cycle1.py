"""Adversarial verification tests for CMI Conditions 1-5 Autonomous Cycle 1."""

from __future__ import annotations

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from toolkit.cmi_autonomous_cycle1_engine import (
    LiaisonRegularityObstructionAudit,
    MumfordChowSummandDisjointnessAudit,
    TrialityGaloisDescentAudit,
    run_autonomous_cycle1,
)
from toolkit.integrity import scan_forbidden


def test_zero_float_strict_audit():
    target = _REPO_ROOT / "toolkit" / "cmi_autonomous_cycle1_engine.py"
    assert scan_forbidden(target) == []


def test_condition1_liaison_and_regularity_gap():
    res = LiaisonRegularityObstructionAudit().evaluate_liaison_range(13, 60)
    assert res["all_arithmetically_covered"] is True
    assert res["arithmetically_uncovered"] == []
    assert res["sample_z22"]["residual_deg"] == 2
    assert res["quadric_section_ceiling"] == 21
    assert res["naive_degree_sufficiency_falsified"] is True


def test_condition3_and_condition4_triality_and_schur_separation():
    c3 = TrialityGaloisDescentAudit().verify_triality_s3_stability()
    assert c3["zero_weight_triples"] == 32
    assert c3["triality_operator_rank"] == 70
    assert c3["s3_order3_triality_preserves_32_triples"] is True
    assert c3["chiral_split"] == (35, 35)

    c4 = MumfordChowSummandDisjointnessAudit().verify_schur_separation()
    assert c4["b_weyl_rank"] == 6
    assert c4["b_weyl_invertible_over_Q"] is True
    assert c4["wd4_order"] == 192
    assert c4["full_so8_invariants_in_6d_zero_weight"] == 0
    assert c4["no_go_003_chern_sufficiency_enforced"] is True


def test_full_cycle1_zariski_lefschetz_and_dark_factory():
    out = run_autonomous_cycle1()
    assert out["global_hodge_conjecture"] == "OPEN"
    assert out["release_authorized"] is False
    assert out["scan_forbidden_clean"] is True

    c2 = out["condition_2_zariski_open_non_fermat"]
    assert c2["class1_multi_ip3_hilbert_verified"] is True
    assert c2["class1_multi_ip3_macaulay_ranks"] == [3, 6, 10, 15, 18, 19]
    assert c2["class2_ip1_dw_vanishes_on_pi"] is False
    assert c2["class2_restricted_hilbert_insufficiency_proved"] is True
    assert c2["class3_off_pi_r6_r12_dims"] == (426, 1751)
    assert c2["class3_off_pi_ivhs_rank"] == 426
    assert c2["zariski_open_surjectivity_certified"] is True

    c5 = out["condition_5_jacobian_lefschetz"]
    assert c5["all_steps_injective"] is True
    assert len(c5["lefschetz_step_injectivity_0_to_10"]) == 11
    assert c5["lefschetz_step_injectivity_0_to_10"][-1] == (10, 1506, 1506)

    dfs = out["dark_factory_summary"]
    assert dfs["submitted"] == 7
    assert dfs["eligible"] == 5
    assert dfs["quarantined"] == 2
    assert set(dfs["quarantined_ids"]) == {"H-TRAP-HONESTY", "H-TRAP-BARRIER"}
