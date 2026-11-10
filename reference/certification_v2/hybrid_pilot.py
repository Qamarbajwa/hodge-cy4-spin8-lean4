"""Writer-only canonical hybrid finite compression pilot at exact L=1,T=400.

Run with .rh-v2-runtime/Scripts/python.exe -m
research.certification_v2.hybrid_pilot. No full operator certificate is emitted.
"""
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path
import time

from research.certification_v2.exact_interval_ldl import Interval, certify
from research.certification_v2.spatial_overlap import log_enclosure, prime_powers, spatial_matrix
from research.certification_v2.pole_entries import pole_matrix

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "research/certification_v2/hybrid_pilot"
DEGREES = [0, 1, 2, 3]


def sha(path):
    return hashlib.sha256((ROOT / path).read_bytes()).hexdigest()


def verified_input_hashes():
    bindings = {
        "research/certification_v2/IMPLEMENTATION_ACCEPTANCE.json": [
            "research/certification_v2/exact_interval_ldl.py",
            "research/certification_v2/spatial_overlap.py"],
        "research/certification_v2/CHAIN_REPAIR_ACCEPTANCE.json": [
            "research/certification_v2/pole_entries.py",
            "research/certification_v2/operator_identity/IDENTITY_FOUNDATION.md"],
        "research/certification_v2/ARCH_AND_COMPACT_ACCEPTANCE.json": [
            "research/certification_v2/archimedean/PILOT_RECEIPT.json"],
        "research/certification_v2/ARB_IMPLEMENTATION_ACCEPTANCE.json": [
            "research/certification_v2/archimedean/arb_adapter.py"],
    }
    hashes = {}
    for manifest, inputs in bindings.items():
        data = json.loads((ROOT / manifest).read_text(encoding="utf-8"))
        if data["terminal_status"] != "DONE" or not data["verdict"].startswith("ACCEPTED_"):
            raise ValueError("input lacks terminal accepted bounded implementation: " + manifest)
        hashes[manifest] = sha(manifest)
        for path in inputs:
            actual = sha(path)
            if actual != data["files_sha256"][path]:
                raise ValueError("accepted input hash mismatch: " + path)
            hashes[path] = actual
    return hashes


def assemble(degrees, arch, spatial, pole, beta):
    """H=beta I+K_(h-beta,[0,T])+M_prime+P_pole, in real spatial basis."""
    n = len(degrees)
    if any(len(component) != n or any(len(row) != n for row in component)
           for component in (arch, spatial, pole)):
        raise ValueError("component dimensions must agree")
    result = [[Interval.parse(arch[i][j]) + Interval.parse(spatial[i][j])
               + Interval.parse(pole[i][j]) + (beta if i == j else 0)
               for j in range(n)] for i in range(n)]
    if any(result[i][j] != result[j][i] for i in range(n) for j in range(n)):
        raise ValueError("symmetric enclosures required")
    return result


def encoded(matrix):
    return [[entry.encoded() for entry in row] for row in matrix]


def outward_dyadic(entry, bits=80):
    entry = Interval.parse(entry)
    denominator = 2**bits
    lower = entry.lo.numerator*denominator // entry.lo.denominator
    upper = -((-entry.hi.numerator*denominator) // entry.hi.denominator)
    return Interval(F(lower, denominator), F(upper, denominator))


def main():
    from research.certification_v2.archimedean.arb_adapter import entry
    input_hashes = verified_input_hashes()
    for path in ("research/certification_v2/hybrid_pilot.py",
                 "research/certification_v2/hybrid_pilot/DERIVATION.md",
                 "tests/test_hybrid_pilot_v2.py"):
        input_hashes[path] = sha(path)
    OUT.mkdir(exist_ok=True)
    # This proves completeness: all integers n>=8 have log(n)>2 and are inactive;
    # enumeration below8 includes all active prime powers2,3,4,5,7.
    log7, log8 = log_enclosure(7, 35), log_enclosure(8, 35)
    if not log7.hi < 2 < log8.lo:
        raise ValueError("active prime-power threshold proof failed")
    terms = prime_powers(7)
    beta_receipt = json.loads((ROOT / "research/certification_v2/archimedean/PILOT_RECEIPT.json").read_text())
    floor = beta_receipt["scalar_symbol_tail_floor"]
    if floor["cutoff"] != "400" or floor["status"] != "SCALAR_ARCH_SYMBOL_TAIL_FLOOR":
        raise ValueError("wrong tail floor receipt")
    beta = F(floor["beta"])
    spatial = spatial_matrix(DEGREES, 1, terms, digits=40, log_terms=35)
    pole = pole_matrix(DEGREES, 1, terms=32, digits=40)
    arch = [[Interval(0, 0) for _ in DEGREES] for _ in DEGREES]
    evaluations = []
    failed = False
    for a, i in enumerate(DEGREES):
        for b in range(a, len(DEGREES)):
            j = DEGREES[b]
            started = time.monotonic()
            result = entry(i, j, 1, 400, beta=beta, bits=96, tolerance="1e-12",
                           eval_limit=250000, panels=4000)
            record = {"degrees": [i, j], "result": result,
                      "wall_seconds": round(time.monotonic()-started, 3)}
            evaluations.append(record)
            (OUT / "ENTRY_PROGRESS.json").write_text(json.dumps({
                "status": "WRITER_ONLY_PROGRESS", "input_sha256": input_hashes,
                "entries": evaluations, "NO_RH_PROOF": True,
                "operator_status": "BLOCKED"}, indent=2)+"\n", encoding="utf-8")
            print("entry", i, j, result["status"], "seconds", record["wall_seconds"], flush=True)
            if result["status"] != "CUTOFF_ENTRY_ENCLOSED_TARGET_MET":
                failed = True
                break
            arch[a][b] = arch[b][a] = Interval.parse(result["entry"])
        if failed:
            break
    receipt = {
        "status": "WRITER_ONLY_AWAITING_INDEPENDENT_REVIEW_AND_ACCEPTANCE",
        "scope": "CANONICAL_HYBRID_FINITE_COMPRESSION_ONLY",
        "formula": "H=beta I + integral_[0,T](h-beta) FourierGram/pi + M_prime + P_pole",
        "basis": "phi_d=sqrt((2d+1)/(2L))*P_d(x/L); Fourier exp(-itx)",
        "Fourier_phase": "(-1)^((i-j)/2) for same parity, zero for opposite parity",
        "L": "1", "T": "400", "degrees": DEGREES, "beta": str(beta),
        "active_prime_powers": terms,
        "active_set_proof": {"log7": log7.encoded(), "log8": log8.encoded(),
                             "strict_test": "upper(log7)<2<lower(log8)",
                             "all_n_ge_8_inactive": True},
        "input_sha256": input_hashes, "entry_runs": evaluations,
        "NO_RH_PROOF": True, "restored_intervals": 0,
        "full_operator_status": "BLOCKED", "continuum_status": "NOT_ATTEMPTED",
        "complement_status": "MISSING",
        "preserved_implementation_failures": [
            "Initial direct exact rational LDL serialization exceeded Python's4300-digit conversion limit.",
            "Repaired locally by exact outward80-bit dyadic matrix entry rounding; no accepted source altered."],
    }
    if failed:
        receipt["finite_status"] = "INCONCLUSIVE_ARCH_ENTRY_TARGET_OR_BUDGET_FAILURE"
    else:
        assembled = assemble(DEGREES, arch, spatial, pole, beta)
        matrix = [[outward_dyadic(x) for x in row] for row in assembled]
        receipt["final_entry_rounding"] = {
            "method": "EXACT_INTEGER_FLOOR_LOWER_AND_CEILING_UPPER",
            "dyadic_bits": 80, "additional_width_strict_upper": "1/"+str(2**79),
            "reason": "bound exact LDL fraction-growth serialization cost; enclosure preserved"}
        receipt["components"] = {"arch_h_minus_beta_cutoff": encoded(arch),
                                 "spatial": encoded(spatial), "pole": encoded(pole)}
        receipt["hybrid_matrix"] = encoded(matrix)
        receipt["finite_ldl"] = certify(matrix)
        receipt["shifted_finite_ldl"] = certify(matrix, "1/10000")
        receipt["finite_status"] = receipt["finite_ldl"]["status"]
        receipt["sector_ldl"] = {
            parity: certify([[matrix[i][j] for j in indices] for i in indices])
            for parity, indices in (("even", [0, 2]), ("odd", [1, 3]))}
        receipt["negative_evidence"] = []
        for i, degree in enumerate(DEGREES):
            if matrix[i][i].hi < 0:
                receipt["negative_evidence"].append({"degree": degree,
                    "fact": "NEGATIVE_CANONICAL_HYBRID_FINITE_RAYLEIGH_QUOTIENT",
                    "entry": matrix[i][i].encoded(),
                    "does_not_refute_full_form": True})
    (OUT / "PILOT_RECEIPT.json").write_text(json.dumps(receipt, indent=2)+"\n", encoding="utf-8")
    print("finite_status", receipt["finite_status"], flush=True)


if __name__ == "__main__":
    main()
