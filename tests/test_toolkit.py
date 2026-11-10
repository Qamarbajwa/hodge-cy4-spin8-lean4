import os, sys, tempfile, unittest
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from toolkit.claims import Claim, State, GovernanceError
from toolkit import integrity as ig


class T(unittest.TestCase):
    def test_no_skip(self):
        c = Claim("C1", "stmt", writer_id="w")
        with self.assertRaises(GovernanceError):
            c.promote(State.CANDIDATE_LEMMA, evidence="PROOF")

    def test_numeric_ceiling(self):
        c = Claim("C1", "s", writer_id="w")
        c.promote(State.CONJECTURE, evidence="SYMBOLIC"); c.promote(State.SUPPORTED_CONJECTURE, evidence="NUMERICAL")
        with self.assertRaises(GovernanceError):
            c.promote(State.CANDIDATE_LEMMA, evidence="NUMERICAL")

    def test_independence(self):
        c = Claim("C1", "s", writer_id="w")
        for s in range(2, 7):
            c.promote(State(s), evidence="PROOF")
        with self.assertRaises(GovernanceError):
            c.promote(State.INDEPENDENTLY_VERIFIED, evidence="PROOF", verifier_id="w")
        c.promote(State.INDEPENDENTLY_VERIFIED, evidence="PROOF", verifier_id="v")

    def test_unjustified_blocks(self):
        c = Claim("C1", "s", writer_id="w"); c.add_assumption("a", "UNJUSTIFIED")
        with self.assertRaises(GovernanceError):
            c.promote(State.CONJECTURE, evidence="SYMBOLIC")

    def test_identity(self):
        c = Claim("C1", "s")
        with self.assertRaises(GovernanceError):
            c.assert_identity("weaker s")

    def test_fabrication_detector(self):
        ns = [10, 20, 40, 80]
        self.assertTrue(ig.check_power_law_fabrication([5 * n ** -2.0 for n in ns], ns))
        self.assertFalse(ig.check_power_law_fabrication([0.05, 0.011, 0.0029, 0.0004], ns))

    def test_wilson(self):
        lo, hi = ig.wilson_interval(20, 20)
        self.assertLess(lo, 1.0); self.assertEqual(hi, 1.0)

    def test_seal_and_manifest(self):
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "r.json"); open(p, "w").write("{}")
            ig.seal(p); self.assertTrue(ig.verify_seal(p))
            open(p, "w").write("{ }"); self.assertFalse(ig.verify_seal(p))

    def test_report_csv(self):
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "x.csv"); open(p, "w").write("id,B_beats_A1\n1,YES\n2,NO\n")
            self.assertTrue(ig.report_vs_csv("All cells succeed: B beats A1", p, "B_beats_A1", r"succeed", "YES"))


if __name__ == "__main__":
    unittest.main()
