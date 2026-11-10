"""Replace the supplied cutoff symbol supremum by accepted rational endpoint bounds."""
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path
import sys

from research.certification_v2.archimedean.real_adapter import h_zero
from research.certification_v2.compact_tail_bound import cutoff_tail_bound
from research.certification_v2.exact_interval_ldl import Interval

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "research/certification_v2/authenticated_symbol_tail"


def sha(path):
    return hashlib.sha256((ROOT/path).read_bytes()).hexdigest()


def endpoint_supremum(h0, hT, beta):
    """For known monotone h, exact endpoint box bound for max_[0,T]|h-beta|."""
    h0, hT = Interval.parse(h0), Interval.parse(hT)
    beta = F(beta)
    if h0.lo > hT.hi:
        raise ValueError("endpoint boxes contradict monotonicity")
    return max(abs(endpoint-beta) for endpoint in (h0.lo,h0.hi,hT.lo,hT.hi))


def accepted_hashes():
    manifests = {
        "research/certification_v2/ARCH_AND_COMPACT_ACCEPTANCE.json": [
            "research/certification_v2/archimedean/real_adapter.py",
            "research/certification_v2/archimedean/PILOT_RECEIPT.json",
            "research/certification_v2/compact_tail_bound.py"],
        "research/certification_v2/IMPLEMENTATION_ACCEPTANCE.json": [
            "research/certification_v2/spatial_overlap.py",
            "research/certification_v2/exact_interval_ldl.py"],
    }
    result = {}
    for manifest, files in manifests.items():
        data = json.loads((ROOT/manifest).read_text())
        if data["terminal_status"] != "DONE" or not data["verdict"].startswith("ACCEPTED_"):
            raise ValueError("component acceptance missing")
        result[manifest] = sha(manifest)
        for path in files:
            actual = sha(path)
            if actual != data["files_sha256"][path]:
                raise ValueError("accepted source hash mismatch: "+path)
            result[path] = actual
    return result


def main():
    # Existing exact cost kernel serializes large integers; increase only the
    # explicit runner serialization ceiling, not numerical precision or bounds.
    sys.set_int_max_str_digits(50000)
    hashes = accepted_hashes()
    for path in ("research/certification_v2/authenticated_symbol_tail.py",
                 "research/certification_v2/authenticated_symbol_tail/DERIVATION.md",
                 "tests/test_authenticated_symbol_tail_v2.py",
                 "research/certification_v2/COMPACT_TAIL_COST_RECEIPT.json"):
        hashes[path] = sha(path)
    floor = json.loads((ROOT/"research/certification_v2/archimedean/PILOT_RECEIPT.json").read_text())["scalar_symbol_tail_floor"]
    if floor["cutoff"] != "400" or floor["status"] != "SCALAR_ARCH_SYMBOL_TAIL_FLOOR":
        raise ValueError("wrong scalar exterior floor")
    h0 = h_zero(256)
    h400 = Interval.parse(floor["symbol_at_cutoff"])
    beta = F(floor["beta"])
    if beta != h400.lo:
        raise ValueError("beta does not match authenticated cutoff lower endpoint")
    M = endpoint_supremum(h0,h400,beta)
    rows = []
    for degree in (650,700):
        bound = cutoff_tail_bound("23/20",400,degree,M,terms=32)
        delta = F(bound["arch_compact_delta_upper"])
        rows.append({"degree_cutoff":degree,"L_upper":"23/20","T":"400",
                     "symbol_sup_authenticated":str(M),"kernel_result":bound,
                     "delta_float_diagnostic_only":float(delta),
                     "bound_scope":"ARCHIMEDEAN_COMPACT_REPLACEMENT_ONLY"})
    result = {
        "status":"WRITER_ONLY_AWAITING_INDEPENDENT_REVIEW_AND_ACCEPTANCE",
        "scope":"ONE_PREVIOUSLY_SUPPLIED_SYMBOL_SUPREMUM_REPLACED_BY_AUTHENTICATED_BOUND",
        "h0":h0.encoded(),"h400":h400.encoded(),"beta":str(beta),
        "symbol_sup_authenticated":str(M),
        "symbol_sup_float_diagnostic_only":float(M),
        "symbol_sup_derivation":"monotone h on nonnegative axis; maximum absolute displacement bounded by endpoint boxes",
        "exterior_floor_link":"same beta=h400.lo implies h(t)>=beta for |t|>=400 by accepted monotonicity/evenness",
        "monotonicity_status":"ACCEPTED_SYMBOL_COMPONENT_INPUT_NOT_REPROVED_HERE",
        "serialization_digit_ceiling":50000,"rows":rows,"input_sha256":hashes,
        "original_assumed_M10_evidence":"PRESERVED_UNCHANGED_HASH_BOUND",
        "remaining_obligations":["Canonical projection/domain hypotheses",
                                 "Pole compact replacement error",
                                 "Full complement lower bound",
                                 "Cross-coupling estimate",
                                 "Reference spectral upper bound and continuum certificate"],
        "NO_RH_PROOF":True,"restored_intervals":0,"full_operator_status":"BLOCKED",
    }
    OUT.mkdir(exist_ok=True)
    (OUT/"PILOT_RECEIPT.json").write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    print("authenticated M",float(M))
    for row in rows:
        print("degree",row["degree_cutoff"],"delta",row["delta_float_diagnostic_only"])


if __name__ == "__main__":
    main()
