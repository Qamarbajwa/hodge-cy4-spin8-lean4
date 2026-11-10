"""Reusable canonical hybrid finite compression runner; bounded4/8-mode pilot."""
from fractions import Fraction as F
import argparse
import hashlib
import json
from pathlib import Path
import time

from research.certification_v2.exact_interval_ldl import Interval,certify
from research.certification_v2.hybrid_pilot import assemble,outward_dyadic
from research.certification_v2.pole_entries import pole_matrix
from research.certification_v2.spatial_overlap import spatial_matrix,prime_powers,log_enclosure

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/"research/certification_v2/hybrid_finite_expansion"


def sha(path):
    return hashlib.sha256((ROOT/path).read_bytes()).hexdigest()


def accepted_dependencies():
    manifest="research/certification_v2/hybrid_pilot/IMPLEMENTATION_ACCEPTANCE.json"
    data=json.loads((ROOT/manifest).read_text())
    if data["terminal_status"]!="DONE" or data["verdict"]!="ACCEPTED_BOUNDED_POINT_HYBRID_FINITE_COMPRESSION_ONLY":
        raise ValueError("accepted baseline missing")
    hashes={manifest:sha(manifest)}
    for path,expected in {**data["input_sha256"],**data["files_sha256"]}.items():
        hashes[path]=sha(path)
        if hashes[path]!=expected:
            raise ValueError("accepted baseline dependency changed: "+path)
    return hashes


def rounded_physical_matrix(degrees,arch,spatial,pole,beta):
    result=assemble(degrees,arch,spatial,pole,beta)
    # Paired shifts, even Fourier symbol and canonical parity poles commute with
    # reflection. These true off-parity entries are EXACTLY zero, not tiny noise.
    return [[Interval(0,0) if (i+j)%2 else outward_dyadic(result[a][b],80)
             for b,j in enumerate(degrees)] for a,i in enumerate(degrees)]


def encode(matrix):
    return [[x.encoded() for x in row] for row in matrix]


def baseline_overlap(matrix,baseline):
    if len(matrix)<4:
        raise ValueError("four-mode subblock required")
    old=[[Interval.parse(x) for x in row] for row in baseline["hybrid_matrix"]]
    return all(max(matrix[i][j].lo,old[i][j].lo)<=min(matrix[i][j].hi,old[i][j].hi)
               for i in range(4) for j in range(4))


def run(degrees,eval_limit=250000,bits=96,tolerance="1e-12",panels=4000):
    from research.certification_v2.archimedean.arb_adapter import entry
    degrees=list(degrees)
    if degrees!=list(range(len(degrees))) or len(degrees)<4:
        raise ValueError("consecutive canonical degrees including0..3 required")
    hashes=accepted_dependencies()
    for path in ("research/certification_v2/hybrid_finite_expansion.py",
                 "research/certification_v2/hybrid_finite_expansion/DERIVATION.md",
                 "tests/test_hybrid_finite_expansion_v2.py"):
        hashes[path]=sha(path)
    OUT.mkdir(exist_ok=True)
    size=len(degrees)
    beta_receipt=json.loads((ROOT/"research/certification_v2/archimedean/PILOT_RECEIPT.json").read_text())
    beta=F(beta_receipt["scalar_symbol_tail_floor"]["beta"])
    baseline=json.loads((ROOT/"research/certification_v2/hybrid_pilot/PILOT_RECEIPT.json").read_text())
    if beta!=F(baseline["beta"]) or baseline["L"]!="1" or baseline["T"]!="400":
        raise ValueError("baseline beta/cutoff/length mismatch")
    logs=[log_enclosure(n,35) for n in (7,8)]
    if not logs[0].hi<2<logs[1].lo:
        raise ValueError("active prime-power proof failed")
    terms=prime_powers(7)
    spatial=spatial_matrix(degrees,1,terms,digits=40,log_terms=35)
    pole=pole_matrix(degrees,1,terms=32,digits=40)
    arch=[[Interval(0,0) for _ in degrees] for _ in degrees]
    runs=[]
    failed=False
    for a,i in enumerate(degrees):
        for b in range(a,size):
            j=degrees[b]
            started=time.monotonic()
            result=entry(i,j,1,400,beta=beta,bits=bits,tolerance=tolerance,
                         eval_limit=eval_limit,panels=panels)
            record={"degrees":[i,j],"result":result,"wall_seconds":round(time.monotonic()-started,3)}
            runs.append(record)
            (OUT/"ENTRY_PROGRESS.json").write_text(json.dumps({
                "status":"WRITER_ONLY_PARTIAL_PROGRESS_NOT_DISPOSITION","degrees":degrees,
                "input_sha256":hashes,"entry_runs":runs,"NO_RH_PROOF":True,
                "full_operator_status":"BLOCKED"},indent=2)+"\n",encoding="utf-8")
            print("entry",i,j,result["status"],"seconds",record["wall_seconds"],flush=True)
            if result["status"]!="CUTOFF_ENTRY_ENCLOSED_TARGET_MET":
                failed=True
                break
            arch[a][b]=arch[b][a]=Interval.parse(result["entry"])
        if failed:
            break
    receipt={"status":"WRITER_ONLY_AWAITING_INDEPENDENT_REVIEW_AND_ACCEPTANCE",
             "scope":"CANONICAL_HYBRID_FINITE_COMPRESSION_POINT_L1_ONLY",
             "L":"1","T":"400","degrees":degrees,"beta":str(beta),
             "active_prime_powers":terms,"active_log7_log8_boxes":[x.encoded() for x in logs],
             "formula":"beta I+K_(h-beta,[0,T])+M_prime+P_pole",
             "basis":"real orthonormal Legendre phi_d; Fourier exp(-itx)",
             "phase":"(-1)^((i-j)/2) within parity, exact opposite-parity zero",
             "input_sha256":hashes,"entry_runs":runs,
             "configuration":{"bits":bits,"tolerance":tolerance,"panels":panels,
                              "per_entry_expensive_evaluation_cap":eval_limit},
             "NO_RH_PROOF":True,"restored_intervals":0,"full_operator_status":"BLOCKED",
             "matching_Q8_complement_status":"NOT_ESTABLISHED",
             "Q650_floor_compatibility":"INCOMPATIBLE_PROJECTION_NOT_USED",
             "full_coupling_status":"NOT_COMPUTED","Schur_status":"BLOCKED"}
    if failed:
        receipt["finite_status"]="INCONCLUSIVE_ENTRY_TARGET_OR_BUDGET_FAILURE"
        receipt["negative_evidence"]=["Entry enclosure failure retained; no uncomputed matrix certification."]
    else:
        matrix=rounded_physical_matrix(degrees,arch,spatial,pole,beta)
        receipt["components"]={"arch":encode(arch),"spatial":encode(spatial),"pole":encode(pole)}
        receipt["hybrid_matrix"]=encode(matrix)
        receipt["final_rounding"]={"method":"EXACT_FLOOR_LOWER_CEILING_UPPER_DYADIC80",
                                   "physical_off_parity":"EXACT_REFLECTION_IDENTITY_ZERO"}
        receipt["finite_ldl_shift0"]=certify(matrix)
        receipt["finite_ldl_shift1_over10000"]=certify(matrix,"1/10000")
        receipt["finite_status"]=receipt["finite_ldl_shift0"]["status"]
        receipt["sector_ldl_shift0"]={str(parity):certify([[matrix[i][j] for j in range(size) if j%2==parity]
                                               for i in range(size) if i%2==parity]) for parity in (0,1)}
        subblock=[row[:4] for row in matrix[:4]]
        receipt["baseline_subblock"]={"all16_boxes_overlap_accepted_baseline":baseline_overlap(matrix,baseline),
                                      "computed4_subblock_shift1_over10000":certify(subblock,"1/10000")}
        if not receipt["baseline_subblock"]["all16_boxes_overlap_accepted_baseline"]:
            raise ValueError("newly computed baseline subblock inconsistent with accepted boxes")
        receipt["negative_evidence"]=[]
        for label in ("finite_ldl_shift0","finite_ldl_shift1_over10000"):
            if receipt[label]["status"]!="FINITE_BOX_POSITIVE_DEFINITE":
                receipt["negative_evidence"].append({"check":label,"status":receipt[label]["status"],
                                                     "meaning":"inconclusive sufficient box test; no negative spectrum inferred"})
        for i,d in enumerate(degrees):
            if matrix[i][i].hi<0:
                receipt["negative_evidence"].append({"degree":d,"negative_hybrid_Rayleigh_box":matrix[i][i].encoded()})
    (OUT/"PILOT_RECEIPT.json").write_text(json.dumps(receipt,indent=2)+"\n",encoding="utf-8")
    print("finite_status",receipt["finite_status"],flush=True)
    return receipt


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--degree-count",type=int,choices=(4,8),default=8)
    args=parser.parse_args()
    run(range(args.degree_count))


if __name__=="__main__":
    main()
