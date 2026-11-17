"""Adversarial Reviewer Test Suite for FourWallStrategicResolutionEngine (Event 24)."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

_REPO_ROOT = str(Path(__file__).resolve().parent.parent)
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

from toolkit.four_wall_strategic_resolution_engine import FourWallStrategicResolutionEngine
from toolkit.integrity import scan_forbidden


class TestFourWallStrategicResolutionEngine(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.root = Path(_REPO_ROOT)
        cls.engine = FourWallStrategicResolutionEngine()
        cls.audit = cls.engine.run_full_audit()

    def test_01_wall1_signed_fermat_407_tangential_closure(self) -> None:
        """Wall 1: All 407/407 ker(M^{(6)}) directions lift on F_t^{signed} with 0 unlifted."""
        w1 = self.audit["wall1_signed_tangential_transport"]
        self.assertEqual(w1["ker6_total_directions"], 407)
        self.assertEqual(w1["ideal_I_Pi_membership_count"], 407)
        self.assertEqual(w1["dim_I_Pi_deg5"], 228)
        self.assertEqual(w1["tangential_leibniz_lift_count"], 407)
        self.assertEqual(w1["tangential_unlifted_count"], 0)
        self.assertEqual(w1["normal_derivative_escape_count"], 398)
        self.assertEqual(w1["signed_fermat_stationary_basis_solvable_count"], 359)
        self.assertEqual(w1["signed_fermat_stationary_subspace_dim"], 401)
        self.assertEqual(w1["signed_fermat_joint_solvable_count"], 407)
        self.assertEqual(w1["signed_fermat_joint_subspace_dim"], 407)
        self.assertEqual(w1["signed_fermat_unlifted_count"], 0)
        self.assertEqual(w1["unsigned_fermat_joint_solvable_count"], 359)
        self.assertEqual(w1["unsigned_fermat_unlifted_count"], 48)
        self.assertEqual(w1["newly_recovered_normal_gap"], 48)
        self.assertTrue(w1["wall1_100_percent_closed"])

        witness = w1["recovered_witness_from_48_gap"]
        self.assertFalse(witness["unsigned_joint_solvable"])
        self.assertTrue(witness["signed_joint_solvable"])
        self.assertTrue(witness["all_degrees_flat_double_rank"])
        self.assertEqual(
            witness["deformed_m1_to_m6_ranks"],
            {1: 6, 2: 12, 3: 20, 4: 30, 5: 36, 6: 38},
        )

    def test_02_wall2_geometric_liaison_sign_inversion(self) -> None:
        """Wall 2: Peskine-Szpiro liaison Z_5^{prim} = -Lambda_{Pi_0} recovers deg-1 plane ideal."""
        w2 = self.audit["wall2_geometric_liaison_compression"]
        self.assertEqual(w2["liaison_complete_intersection_degree"], 6)
        self.assertEqual(w2["minimal_plane_degree"], 1)
        self.assertEqual(w2["residual_surface_degree"], 5)
        self.assertTrue(w2["prim_sum_zero_in_R12"])
        self.assertEqual(tuple(w2["z5_macaulay_rank_vector"]), (3, 6, 10, 15, 18, 19))
        self.assertEqual(w2["z5_ann_R1_dim"], 3)
        self.assertTrue(w2["z5_ann_matches_deg1_plane_ideal"])
        self.assertEqual(w2["z5_gotzmann_G"], 1)
        self.assertTrue(w2["tail_x2_4_split_verified"])
        self.assertEqual(w2["tail_partial_ann_R1_dim"], 2)
        self.assertFalse(w2["non_linked_castelnuovo_mumford_bound_known"])

    def test_03_wall3_picard_lefschetz_nodal_bridge(self) -> None:
        """Wall 3: Exact integral Picard-Lefschetz reflections satisfy T^2=Id, isometry, & orbit transitivity."""
        w3 = self.audit["wall3_picard_lefschetz_nodal_bridge"]
        self.assertEqual(w3["ambient_lattice_rank"], 6)
        self.assertEqual(w3["simple_vanishing_spheres_count"], 5)
        self.assertEqual(w3["vanishing_sphere_self_intersection"], 2)
        self.assertTrue(w3["involutivity_T_sq_equals_Id"])
        self.assertTrue(w3["intersection_isometry_verified"])
        self.assertTrue(w3["wirtinger_balance_preserved"])
        self.assertEqual(w3["transitive_orbit_size"], 30)
        self.assertFalse(w3["nodal_bridge_gives_effective_global_bound"])

    def test_04_wall4_d4_to_su22_spinor_to_weil_branching(self) -> None:
        """Wall 4: D_4 -> D_3 = su(2,2) zero-weight branching 8 = 2 pure Weil + 6 mixed K_{2,2}, inv = 2+1 = 3."""
        w4 = self.audit["wall4_spinor_to_weil_su22_specialization"]
        self.assertEqual(w4["dim_V_plus"], 4)
        self.assertEqual(w4["dim_V_minus"], 4)
        self.assertEqual(w4["wedge4_total_dim"], 70)
        self.assertEqual(w4["d3_su22_zero_weight_dim"], 8)
        self.assertEqual(w4["pure_weil_tuples_dim"], 2)
        self.assertEqual(w4["mixed_d4_zero_tuples_dim"], 6)
        self.assertTrue(w4["pure_weil_matches_W0_A4_dim_2"])
        self.assertEqual(w4["mixed_d3_root_rank"], 5)
        self.assertEqual(w4["mixed_su22_singlet_dim"], 1)
        self.assertEqual(w4["total_su22_invariant_dim"], 3)
        self.assertFalse(w4["horizontal_spin8_markman_spreading_proved"])

    def test_05_honest_millennium_boundary_and_zero_floats(self) -> None:
        """Confirms Bridge A/B remain adversarially blocked, global target OPEN, and zero floats."""
        self.assertEqual(self.audit["event_id"], 24)
        self.assertEqual(self.audit["bridge_a_status"], "ADVERSARIALLY_BLOCKED_OPEN_BRIDGE")
        self.assertEqual(self.audit["bridge_b_status"], "ADVERSARIALLY_BLOCKED_OPEN_BRIDGE")
        self.assertEqual(self.audit["global_hodge_conjecture_status"], "OPEN")
        self.assertFalse(self.audit["release_authorized"])
        self.assertEqual(self.audit["theorem_progress"], "UNKNOWN")
        self.assertEqual(
            scan_forbidden(str(self.root / "toolkit" / "four_wall_strategic_resolution_engine.py")),
            [],
        )


if __name__ == "__main__":
    unittest.main()
