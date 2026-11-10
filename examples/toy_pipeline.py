"""End-to-end toy demonstration of the whole pipeline on a problem with a KNOWN answer.
Run:  python -m examples.toy_pipeline      (from the kit root)

Toy operator: Q = 2I - (shift + shift^T) on frequency indices -M..M. Exact ground energy 2-2cos(pi/(2M+2)) (even mode).
Replace `build_Q` and the fixture with YOUR operator to reuse the pipeline."""
import json, os, sys
import mpmath as mp
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from toolkit import hp_linalg as hl, prereg as pr, integrity as ig


def build_Q(M, dps):
    mp.mp.dps = dps
    n = 2 * M + 1
    Q = mp.matrix(n, n)
    for i in range(n):
        Q[i, i] = 2
        if i + 1 < n:
            Q[i, i + 1] = Q[i + 1, i] = -1
    return Q


def exact_ground(M):
    return 2 - 2 * mp.cos(mp.pi / (2 * M + 2))


def main():
    mp.mp.dps = 50
    prereg = {
        "protocol_id": "TOY-001", "oracle": {"package": "none (analytic)"},
        "precision_requirements": {"ladder": [50, 80, 120]},
        "primary_statistic": "R = lam_B / lam_A",
        "contamination_declarations": {"results_seen_before_design": False},
        "decision_rules": {"A": "A lower everywhere", "B": "nonuniversal", "C": "B lower everywhere", "D": "inconclusive"},
        "primary_grid": [{"M": 12, "n": n} for n in (3, 5, 7)],
    }
    M0 = 12
    # Gate A: reference fixture across precision ladder
    fixture = lambda: hl.precision_ladder(
        lambda dps: hl.ground_eig(build_Q(M0, dps)),
        ladder=(50, 80, 120), expected=exact_ground(M0), rtol="1e-30")["passed"]
    # Gate B: variational calibration - every restricted energy must be >= exact full ground energy
    def calib():
        mp.mp.dps = 50
        E = hl.even_projection(build_Q(M0, 50), M0)
        full = hl.ground_eig(E)
        lamA = hl.ground_eig(hl.principal_block(E, 7))
        lamB = hl.ground_eig(hl.augmented_subspace(E, 5, lambda k: (-1) ** k / mp.mpf(k) ** 2))
        return lamA >= full - mp.mpf("1e-40") and lamB >= full - mp.mpf("1e-40")

    def cell(c):
        mp.mp.dps = 50
        E = hl.even_projection(build_Q(c["M"], 50), c["M"])
        n = c["n"]
        A = hl.ground_eig(hl.principal_block(E, n + 2))
        B = hl.ground_eig(hl.augmented_subspace(E, n, lambda k: (-1) ** k / mp.mpf(k) ** 2))
        return A, B

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "TOY_RESULTS.json")
    res = pr.run(prereg, fixture, calib, cell, out, script_path=__file__)
    print(json.dumps({"gates": res["gates"], "outcome": res["outcome"]}, indent=2))
    print("seal verifies:", ig.verify_seal(out))


if __name__ == "__main__":
    main()
