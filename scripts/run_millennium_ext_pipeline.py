"""Orchestrator & Receipt Generator for the Millennium Extension Workspace.

Runs:
1. Locked baseline verification check (reads `dist/FULL_AUTOMATION_VERIFICATION_RECEIPT.json`
   and ensures none of the 13 baseline `.lean` files were altered).
2. Builds `examples/math_gov/LeanMillenniumExt/` (`lake build`) and checks zero-axiom
   receipts and theorem counts across all 6 extension modules.
3. Replays all 4 Phase 1-5 Python exact explorers (`fermat_band4_scout.py`,
   `multi_order_gd_crt.py`, `nl_moduli_walk.py`, `counterexample_sieve.py`).
4. Writes `reports/millennium_ext/MILLENNIUM_EXT_RECEIPT.json`.
"""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List


REPO_ROOT = Path(__file__).resolve().parent.parent
BASELINE_RECEIPT = REPO_ROOT / "dist" / "FULL_AUTOMATION_VERIFICATION_RECEIPT.json"
BASELINE_LEAN_DIR = REPO_ROOT / "examples" / "math_gov" / "LeanDemoProject"
EXT_LEAN_DIR = REPO_ROOT / "examples" / "math_gov" / "LeanMillenniumExt"
REPORT_DIR = REPO_ROOT / "reports" / "millennium_ext"

EXT_FILES = [
    "MumfordWeilKernelVecs.lean",
    "HodgeBridgeInterfaces.lean",
    "ConditionalFermatHodge.lean",
    "FermatHighDegreeExt.lean",
    "FermatAokiSurfaceExt.lean",
    "ConditionalFermatHodgeExt.lean",
    "HigherOrderJetLifting.lean",
    "HigherOrderJetAndObstructionExt.lean",
    "CayleyCompleteInt.lean",
    "Poly6ToMvPoly.lean",
    "MumfordCMSpecializationExt.lean",
    "MatrixFactorizationAndSchurExt.lean",
    "NonKoszulMFAndWeilPeriodExt.lean",
    "WavefunctionMatrixUnificationExt.lean",
    "ConjugateHalfWaveAdaptationExt.lean",
    "LorentzianWeilBoostExt.lean",
    "StrictMatrixCurvatureExt.lean",
    "MumfordSL2SO4Ext.lean",
    "WavefunctionBipartiteMatrixExt.lean",
    "MumfordTripleProductExt.lean",
    "CliffordKugaSatakeChiralExt.lean",
    "SchurUniversalSp8ProjectionExt.lean",
    "CliffordTripleProductSchurExt.lean",
    "CliffordTripleAndFermat25SchurExt.lean",
]

THEOREM_DECL_RE = re.compile(r"^\s*(?:private\s+)?(?:theorem|lemma)\s+[A-Za-z0-9_']+", re.MULTILINE)
FORBIDDEN_LEAN_RE = re.compile(r"\b(sorry|admit|opaque|axiom|native_decide|unsafe)\b")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        while True:
            chunk = f.read(65536)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def verify_locked_baseline() -> Dict[str, Any]:
    receipt = json.loads(BASELINE_RECEIPT.read_text(encoding="utf-8"))
    expected = receipt["lean_audit"]["sha256"]
    mismatches: List[str] = []
    for fname, exp_sha in expected.items():
        actual_sha = sha256_file(BASELINE_LEAN_DIR / fname)
        if actual_sha != exp_sha:
            mismatches.append(fname)
    return {"locked_baseline_intact": len(mismatches) == 0, "mismatches": mismatches}


def build_extension_lean() -> Dict[str, Any]:
    clean_proc = subprocess.run(
        ["lake", "clean"],
        cwd=str(EXT_LEAN_DIR),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    proc = subprocess.run(
        ["lake", "build"],
        cwd=str(EXT_LEAN_DIR),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    out = (proc.stdout or "") + "\n" + (proc.stderr or "")
    thm_counts: Dict[str, int] = {}
    forbidden_hits: List[str] = []
    long_lines: List[str] = []
    hashes: Dict[str, str] = {}
    for fname in EXT_FILES:
        fpath = EXT_LEAN_DIR / fname
        text = fpath.read_text(encoding="utf-8")
        hashes[fname] = sha256_file(fpath)
        thm_counts[fname] = len(THEOREM_DECL_RE.findall(text))
        for idx, line in enumerate(text.splitlines(), 1):
            if FORBIDDEN_LEAN_RE.search(line) and not line.strip().startswith("#print axioms"):
                forbidden_hits.append(f"{fname}:{idx}")
            if len(line) > 100:
                long_lines.append(f"{fname}:{idx}:len={len(line)}")
    axiom_errors = [ln for ln in out.splitlines() if "depends on axioms:" in ln]
    verbatim_axiom_receipts = [
        ln.strip()
        for ln in out.splitlines()
        if "does not depend on any axioms" in ln
        and any(fn in ln for fn in EXT_FILES)
    ]
    return {
        "lake_clean_ok": clean_proc.returncode == 0,
        "lake_build_ok": proc.returncode == 0,
        "returncode": proc.returncode,
        "extension_theorems": sum(thm_counts.values()),
        "theorem_counts": thm_counts,
        "forbidden_hits": forbidden_hits,
        "long_lines_gt_100": long_lines,
        "unexpected_axiom_lines": axiom_errors,
        "verbatim_axiom_receipts": verbatim_axiom_receipts,
        "sha256": hashes,
        "passed": (
            clean_proc.returncode == 0
            and proc.returncode == 0
            and not forbidden_hits
            and not long_lines
            and not axiom_errors
        ),
    }


def run_symbolic_scripts() -> Dict[str, bool]:
    cuda_py = Path(r"C:\Users\arqam\AppData\Local\Programs\Python\Python313\python.exe")
    py_exe = str(cuda_py) if cuda_py.exists() else sys.executable
    scripts = [
        REPO_ROOT / "toolkit" / "millennium_ext" / "fermat_band4_scout.py",
        REPO_ROOT / "toolkit" / "millennium_ext" / "fermat_aoki_surface_witness.py",
        REPO_ROOT / "toolkit" / "millennium_ext" / "multi_order_gd_crt.py",
        REPO_ROOT / "toolkit" / "millennium_ext" / "higher_order_t12_and_g4_sieve.py",
        REPO_ROOT / "toolkit" / "millennium_ext" / "nl_moduli_walk.py",
        REPO_ROOT / "toolkit" / "millennium_ext" / "counterexample_sieve.py",
        REPO_ROOT / "toolkit" / "millennium_ext" / "mumford_cm_specializer.py",
        REPO_ROOT / "toolkit" / "millennium_ext" / "matrix_factorization_scaling.py",
        REPO_ROOT / "toolkit" / "millennium_ext" / "schur_5050_diagonal_audit.py",
        REPO_ROOT / "toolkit" / "millennium_ext" / "non_koszul_mf_closure.py",
        REPO_ROOT / "toolkit" / "millennium_ext" / "high_precision_period_pslq.py",
        REPO_ROOT / "toolkit" / "millennium_ext" / "wavefunction_matrix_unification.py",
        REPO_ROOT / "toolkit" / "millennium_ext" / "conjugate_half_wave_adaptation.py",
        REPO_ROOT / "toolkit" / "millennium_ext" / "lorentzian_weil_boost.py",
        REPO_ROOT / "toolkit" / "millennium_ext" / "strict_matrix_curvature.py",
        REPO_ROOT / "toolkit" / "millennium_ext" / "mumford_sl2_so4_spinor.py",
        REPO_ROOT / "toolkit" / "millennium_ext" / "wavefunction_bipartite_matrix.py",
        REPO_ROOT / "toolkit" / "millennium_ext" / "mumford_triple_product_hodge33.py",
        REPO_ROOT / "toolkit" / "millennium_ext" / "clifford_kuga_satake_chiral.py",
        REPO_ROOT / "toolkit" / "millennium_ext" / "schur_universal_sp8_projection.py",
        REPO_ROOT / "toolkit" / "millennium_ext" / "clifford_triple_product_schur.py",
        REPO_ROOT / "toolkit" / "millennium_ext" / "clifford_triple_and_fermat25_schur.py",
    ]
    res: Dict[str, bool] = {}
    for sc in scripts:
        p = subprocess.run([py_exe, str(sc)], cwd=str(REPO_ROOT), capture_output=True, text=True)
        res[sc.name] = (p.returncode == 0)
    return res


def main() -> int:
    base = verify_locked_baseline()
    ext = build_extension_lean()
    sym = run_symbolic_scripts()
    all_ok = base["locked_baseline_intact"] and ext["passed"] and all(sym.values())

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    receipt = {
        "EXT_CHECKS_PASSED": all_ok,
        "baseline_lock": base,
        "extension_lean_audit": ext,
        "symbolic_explorers": sym,
        "open_frontiers": [
            "Wall1: Global 426-dim NL locus connectedness",
            "Wall2: m=25 5-term-AP sporadic orbit cycle construction & m -> inf closure",
            "Wall3: Generic simple (End=Q, rho=1) Mumford 2-cycle construction",
            "Wall4: Universal smooth projective X subset P^N mechanism or counterexample",
            "Wall5: Full Mathlib4 Kahler / exponential sheaf / Griffiths residue / Chow discharge",
        ],
    }
    (REPORT_DIR / "MILLENNIUM_EXT_RECEIPT.json").write_text(json.dumps(receipt, indent=2), encoding="utf-8")
    print(f"BASELINE_LOCKED={base['locked_baseline_intact']}")
    print(
        f"EXT_LEAN_OK={ext['lake_build_ok']} EXT_THEOREMS={ext['extension_theorems']} "
        f"LONG_LINES={len(ext['long_lines_gt_100'])} UNEXPECTED_AXIOMS={len(ext['unexpected_axiom_lines'])}"
    )
    for rec_line in ext["verbatim_axiom_receipts"]:
        print(f"AXIOM_RECEIPT: {rec_line}")
    print(f"SYMBOLIC_SCRIPTS={sym}")
    print(f"EXT_CHECKS_PASSED={all_ok}")
    return 0 if all_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
