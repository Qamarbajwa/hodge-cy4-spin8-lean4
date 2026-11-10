"""Bounded actual degree649 entry probes; no650matrix or positivity claim."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/"research/certification_v2/degree650_entry_cost"


def child(kind):
    started=time.monotonic()
    if kind=="arch":
        from research.certification_v2.archimedean.arb_adapter import entry
        beta=json.loads((ROOT/"research/certification_v2/archimedean/PILOT_RECEIPT.json").read_text())["scalar_symbol_tail_floor"]["beta"]
        value=entry(649,649,1,400,beta=beta,bits=96,tolerance="1e-12",eval_limit=20000,panels=100)
        result={"status":"ACTUAL_HIGH_DEGREE_ARCH_ENTRY_ATTEMPT","degrees":[649,649],
                "configuration":{"bits":96,"panels":100,"eval_limit":20000,"tolerance":"1e-12"},"entry_result":value}
    else:
        from research.certification_v2.spatial_overlap import spatial_matrix
        # One actual active prime term already exercises the degree649 polynomial
        # bottleneck; this is not presented as a complete canonical entry.
        value=spatial_matrix([649],1,[(2,2)],digits=40,log_terms=35)
        result={"status":"ACTUAL_HIGH_DEGREE_ONE_PRIME_SPATIAL_ATTEMPT","degrees":[649,649],
                "terms":[[2,2]],"complete_active_set":False,"entry":value[0][0].encoded()}
    result["wall_seconds"]=round(time.monotonic()-started,3)
    (OUT/(kind+"_CHILD_RESULT.json")).write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--child",choices=("arch","spatial"))
    args=parser.parse_args()
    OUT.mkdir(exist_ok=True)
    if args.child:
        child(args.child)
        return
    from research.certification_v2.hybrid_finite_expansion import accepted_dependencies
    hashes=accepted_dependencies()
    path="research/certification_v2/probe_650_entry_cost.py"
    hashes[path]=hashlib.sha256((ROOT/path).read_bytes()).hexdigest()
    runs=[]
    for kind,timeout in (("arch",20),("spatial",10)):
        started=time.monotonic()
        result_path=OUT/(kind+"_CHILD_RESULT.json")
        if result_path.exists():
            raise ValueError("preserve existing cost evidence; select a fresh output revision before rerun")
        flags=subprocess.CREATE_NO_WINDOW if sys.platform=="win32" else 0
        try:
            proc=subprocess.run([sys.executable,"-m","research.certification_v2.probe_650_entry_cost","--child",kind],
                                cwd=ROOT,capture_output=True,timeout=timeout,creationflags=flags)
            row={"kind":kind,"exit_code":proc.returncode,"status":"COMPLETED" if proc.returncode==0 else "EXECUTION_FAILED",
                 "stderr":proc.stderr.decode(errors="replace")[-4000:]}
            if proc.returncode==0:
                row["result"]=json.loads(result_path.read_text())
        except subprocess.TimeoutExpired:
            row={"kind":kind,"status":"WALL_BUDGET_EXHAUSTED_CHILD_TERMINATED_NO_ENCLOSURE"}
        row.update({"wall_budget_seconds":timeout,"wall_seconds":round(time.monotonic()-started,3)})
        runs.append(row)
        print(kind,row["status"],row["wall_seconds"],flush=True)
        receipt={"status":"WRITER_ONLY_SCALABILITY_OBSTRUCTION_PROBE_AWAITING_REVIEW",
                 "input_sha256":hashes,"runs":runs,"NO_RH_PROOF":True,"full_operator_status":"BLOCKED",
                 "finite650_matrix_status":"NOT_CONSTRUCTED","coupling650_status":"NOT_CONSTRUCTED",
                 "meaning":"Timeout/failed enclosure is implementation cost evidence, not negative spectrum"}
        (OUT/"PILOT_RECEIPT.json").write_text(json.dumps(receipt,indent=2)+"\n",encoding="utf-8")


if __name__=="__main__":
    main()
