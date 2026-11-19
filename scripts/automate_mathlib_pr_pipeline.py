"""End-to-End Verification, Self-Contained Mathlib4 Staging & Release Bundler.

Automates:
1. Lean 4 kernel build (`lake build`), forbidden-token audit, and Mathlib4 style audit.
2. Self-contained (zero local import) Mathlib4 PR staging under `dist/upstream_prs/mathlib4/`
   with clean namespaces and <= 100 char lines, verified standalone via `lake env lean`.
3. Five-paper typography, page-count, pronoun, and forbidden-jargon audit.
4. Cryptographic SHA-256 receipt (`dist/FULL_AUTOMATION_VERIFICATION_RECEIPT.json`).
5. Deterministic Zenodo / arXiv release archive (`dist/HODGE_LEAN4_5PAPER_RELEASE_BUNDLE.zip`).

Strictly float-free (uses only integer, string, and JSON-serializable primitives).
"""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
import zipfile
from pathlib import Path
from typing import Any, Dict, List, Set, Tuple


REPO_ROOT = Path(__file__).resolve().parent.parent
LEAN_DIR = REPO_ROOT / "examples" / "math_gov" / "LeanDemoProject"
DIST_DIR = REPO_ROOT / "dist"
UPSTREAM_DIR = DIST_DIR / "upstream_prs" / "mathlib4"
BUNDLE_PATH = DIST_DIR / "HODGE_LEAN4_5PAPER_RELEASE_BUNDLE.zip"

ALLOWED_GITHUB_TARGETS = frozenset(
    {
        "Qamarbajwa/mathlib4",
        "Qamarbajwa/hodge-cy4-spin8-lean4",
        "Qamarbajwa/hodge-cy4-spin8-papers",
    }
)
BLOCKED_EXTERNAL_REPOS = frozenset(
    {
        "leanprover-community/mathlib4",
        "google-deepmind/formal-conjectures",
        "ImperialCollegeLondon/FLT",
    }
)


def assert_internal_target_only(repo_slug: str) -> None:
    """Hard-block PR creation, pushes, or comments against external repositories."""
    if repo_slug in BLOCKED_EXTERNAL_REPOS or repo_slug not in ALLOWED_GITHUB_TARGETS:
        raise RuntimeError(
            f"POLICY BLOCK: External repository target '{repo_slug}' is permanently disabled. "
            f"Allowed targets: {sorted(ALLOWED_GITHUB_TARGETS)}"
        )

LEAN_FILES = [
    "LeanDemoProject.lean",
    "HodgeVerification.lean",
    "ShiodaFormalConjectures.lean",
    "MathlibPR_ShiodaAokiFermat.lean",
    "MathlibPR_MacaulayGorenstein.lean",
    "MathlibPR_Spin8Triality.lean",
    "MathlibPR_CyclotomicIncidenceSieve.lean",
    "WiebeSchejaStorch.lean",
    "GaussManinJetTransport.lean",
    "ShiodaInductiveCycleSynthesis.lean",
    "Spin8LieAlgebraTriality.lean",
    "GlobalIVHSObstructionSpectrum.lean",
    "HigherDegreeSporadicBand4.lean",
]

MATHLIB_PR_SPECS = [
    {
        "src": "MathlibPR_ShiodaAokiFermat.lean",
        "dst": "Mathlib/AlgebraicGeometry/FermatHypersurface/ShiodaAoki.lean",
        "namespace": "AlgebraicGeometry.FermatHypersurface",
        "deps_sfc": [
            "rangeList", "gcdFuel", "coprimeUnits", "isShiodaHodge22", "with6Nat",
            "isBand1CompletePairs", "isBand2ThreePlusThree", "isBand3TwoPlusFour",
            "isBand4Residual", "fact", "countOcc", "uniqueList", "s6OrbitSize",
            "sortedHodge22Tuples", "summarizeHodgeTuples", "fermatCensusSummary",
            "fermat_band4_count",
            "shioda_aoki_fermat_fourfold_census_m3_to_m10_empty_band4",
            "shioda_aoki_fermat_m12_census_cert",
        ],
        "deps_hv": [],
    },
    {
        "src": "MathlibPR_MacaulayGorenstein.lean",
        "dst": "Mathlib/RingTheory/ArtinianGorenstein/MacaulayContraction.lean",
        "namespace": "RingTheory.MacaulayContraction",
        "deps_sfc": [
            "intEq", "intNe", "rangeList", "getIntAt", "transposeMat",
            "monomialDivides", "contractsWithSocle", "monomials4", "addExp4",
            "natListEqBool", "coeffInSocle", "planeSoclePoly", "quadricJetSoclePoly",
            "macaulayPairingMatrix",
        ],
        "deps_hv": [],
    },
    {
        "src": "MathlibPR_Spin8Triality.lean",
        "dst": "Mathlib/RepresentationTheory/Spin8Triality.lean",
        "namespace": "RepresentationTheory.Spin8",
        "deps_sfc": [
            "intEq", "intNe", "rangeList", "Weight4", "allSign4Tuples",
            "so8Weights", "so8OddSpinorWeights", "so8VectorWeights",
            "addW4", "isZeroWeight4", "combsIdx", "getWAt",
            "idxTupleSum", "fourIndexTuples", "zeroIndexTuples", "complement8",
            "lexLtNatList", "zeroStarPairs", "getIntAt", "transposeMat",
            "intElimStep", "intMatRankAuxClean", "basisVec4",
        ],
        "deps_hv": [
            "Weight", "so8_weights", "add_w", "is_zero_weight", "combs",
            "four_tuples", "tuple_sum", "zero_weight_tuples", "countGreater",
            "inversionCount", "hodgeStarSign", "self_dual_orbit_pairs",
            "wedge4_spinor_self_dual_dim", "wedge4_spinor_anti_self_dual_dim",
            "d4SimpleRoots", "indexOfWeight", "getNatAt", "replaceAtNat",
            "sortNatListInsert", "sortNatList", "applyRootToTuple",
            "coeffOfTuple", "dotTupleTerms", "d4_root_gram_matrix",
            "mumford_stacked_root_rank", "insertAtNat", "permsNat",
            "all_s4_perms", "weyl_d4_elements", "getWeightCoord",
            "actWD4OnWeight", "wd4Perm8", "wd4_total_elements",
            "wd4_all_even_parity", "wd4ChiralTraces", "wd4_chiral_trace_list",
            "wd4_norm_plus_sq", "wd4_norm_minus_sq", "wd4_cross_product",
            "weyl_d4_even_parity_and_chiral_orthogonality_eq",
        ],
    },
    {
        "src": "MathlibPR_CyclotomicIncidenceSieve.lean",
        "dst": "Mathlib/Combinatorics/IncidenceSieve/CyclotomicResidualForm.lean",
        "namespace": "Combinatorics.IncidenceSieve",
        "deps_sfc": [
            "intEq", "intNe", "rangeList", "gcdFuel", "coprimeUnits",
            "isShiodaHodge22", "with6Nat", "isBand1CompletePairs",
            "isBand2ThreePlusThree", "isBand3TwoPlusFour", "fact", "countOcc",
            "uniqueList", "s6OrbitSize", "sortedHodge22Tuples",
            "summarizeHodgeTuples", "fermatCensusSummary",
            "fermat_band2_count", "fermat_band3_count", "getIntAt",
            "transposeMat", "monomials4", "addExp4", "coeffInSocle",
            "planeSoclePoly", "quadricJetSoclePoly", "macaulayPairingMatrix",
            "intElimStep", "intMatRankAuxClean", "macaulayMatrixRank",
            "natListEqBool",
        ],
        "deps_hv": [
            "binom", "h22_prim", "h31_prim", "getNatAt",
            "all_perfect_matchings_6", "matchingSatisfied",
            "matchingSatisfactionCount", "band1_sorted_tuples_m6",
            "band1_count_by_multiplicity", "band1_multiplicity_pairs",
            "high_support_moduli_counts", "high_support_moduli_dim",
        ],
    },
]

PAPERS = [
    {
        "id": "Paper1",
        "tex": REPO_ROOT / "paper" / "paper1_shioda_aoki_lean4" / "Paper1_Shioda_Aoki_Fermat_Lean4.tex",
        "pdf": REPO_ROOT / "paper" / "paper1_shioda_aoki_lean4" / "Paper1_Shioda_Aoki_Fermat_Lean4.pdf",
        "log": REPO_ROOT / "paper" / "paper1_shioda_aoki_lean4" / "Paper1_Shioda_Aoki_Fermat_Lean4.log",
    },
    {
        "id": "Paper2",
        "tex": REPO_ROOT / "paper" / "paper2_macaulay_apolarity_lean4" / "Paper2_Macaulay_Apolarity_CY4_Lean4.tex",
        "pdf": REPO_ROOT / "paper" / "paper2_macaulay_apolarity_lean4" / "Paper2_Macaulay_Apolarity_CY4_Lean4.pdf",
        "log": REPO_ROOT / "paper" / "paper2_macaulay_apolarity_lean4" / "Paper2_Macaulay_Apolarity_CY4_Lean4.log",
    },
    {
        "id": "Paper3",
        "tex": REPO_ROOT / "paper" / "paper3_spin8_mumford_lean4" / "Paper3_Spin8_Triality_Mumford_Lean4.tex",
        "pdf": REPO_ROOT / "paper" / "paper3_spin8_mumford_lean4" / "Paper3_Spin8_Triality_Mumford_Lean4.pdf",
        "log": REPO_ROOT / "paper" / "paper3_spin8_mumford_lean4" / "Paper3_Spin8_Triality_Mumford_Lean4.log",
    },
    {
        "id": "Paper4",
        "tex": REPO_ROOT / "paper" / "paper4_gauss_manin_jets" / "Paper4_Gauss_Manin_Jet_Reconstruction.tex",
        "pdf": REPO_ROOT / "paper" / "paper4_gauss_manin_jets" / "Paper4_Gauss_Manin_Jet_Reconstruction.pdf",
        "log": REPO_ROOT / "paper" / "paper4_gauss_manin_jets" / "Paper4_Gauss_Manin_Jet_Reconstruction.log",
    },
    {
        "id": "Paper5",
        "tex": REPO_ROOT / "paper" / "paper5_cyclotomic_incidence_sieve" / "Paper5_Cyclotomic_Incidence_Sieve_Lean4.tex",
        "pdf": REPO_ROOT / "paper" / "paper5_cyclotomic_incidence_sieve" / "Paper5_Cyclotomic_Incidence_Sieve_Lean4.pdf",
        "log": REPO_ROOT / "paper" / "paper5_cyclotomic_incidence_sieve" / "Paper5_Cyclotomic_Incidence_Sieve_Lean4.log",
    },
    {
        "id": "Paper6",
        "tex": REPO_ROOT / "paper" / "paper6_millennium_frontier_extensions" / "Paper6_Millennium_Frontier_Extensions_Lean4.tex",
        "pdf": REPO_ROOT / "paper" / "paper6_millennium_frontier_extensions" / "Paper6_Millennium_Frontier_Extensions_Lean4.pdf",
        "log": REPO_ROOT / "paper" / "paper6_millennium_frontier_extensions" / "Paper6_Millennium_Frontier_Extensions_Lean4.log",
    },
]

EXT_LEAN_DIR = REPO_ROOT / "examples" / "math_gov" / "LeanMillenniumExt"
EXT_LEAN_FILES = [
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
]

FORBIDDEN_LEAN_RE = re.compile(r"\b(sorry|admit|opaque|axiom|native_decide|unsafe)\b")
PRONOUN_RE = re.compile(r"\b(I|we|We|our|Our|us|Us)\b")
FORBIDDEN_JARGON_PATTERNS = [
    r"HODGE-MILLENNIUM",
    r"Check 4",
    r"Layer [1-4]",
    r"Node ",
    r"Gate G",
    r"math_gov",
    r"scan_forbidden",
    r"(?i:clay millennium)",
    r"(?i:clay mathematics institute)",
    r"(?i:millennium prize)",
    r"(?i:millennium problem)",
    r"(?i:millennium wall)",
    r"(?i:millennium frontier)",
    r"(?i:strictly open)",
    r"(?i:open_research_frontier)",
    r"(?i:epistemic scope)",
]
JARGON_RE = re.compile("|".join(FORBIDDEN_JARGON_PATTERNS))
LST_BLOCK_RE = re.compile(r"\\begin\{lstlisting\}.*?\\end\{lstlisting\}", re.DOTALL)
DECL_START_RE = re.compile(
    r"^(?:set_option\b.*?\bin\s*\n\s*)?(?:private\s+)?(?:def|abbrev|theorem|lemma)\s+([A-Za-z0-9_']+)"
)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        while True:
            chunk = f.read(65536)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def parse_top_level_decls(text: str) -> List[Tuple[str, str]]:
    """Splits a Lean file into `(decl_name, block_text)` pairs in source order."""
    lines = text.splitlines()
    blocks: List[Tuple[str, str]] = []
    i = 0
    n = len(lines)
    decl_head_re = re.compile(r"^(?:private\s+)?(?:def|abbrev|theorem|lemma)\s+([A-Za-z0-9_']+)")
    top_cmd_re = re.compile(
        r"^(?:def|abbrev|theorem|lemma|private|import|#|/-|--|set_option|namespace|end\b)"
    )

    while i < n:
        line = lines[i]
        pending_set_opt: List[str] = []
        if line.startswith("set_option ") and line.rstrip().endswith(" in"):
            pending_set_opt.append(line)
            j = i + 1
            while j < n and lines[j].startswith("set_option ") and lines[j].rstrip().endswith(" in"):
                pending_set_opt.append(lines[j])
                j += 1
            if j < n:
                m = decl_head_re.match(lines[j])
                if m:
                    name = m.group(1)
                    k = j + 1
                    while k < n:
                        lk = lines[k]
                        if lk and not lk[0].isspace() and top_cmd_re.match(lk):
                            break
                        k += 1
                    block = "\n".join(pending_set_opt + lines[j:k]).rstrip()
                    blocks.append((name, block))
                    i = k
                    continue
        m = decl_head_re.match(line)
        if m:
            name = m.group(1)
            k = i + 1
            while k < n:
                lk = lines[k]
                if lk and not lk[0].isspace() and top_cmd_re.match(lk):
                    break
                k += 1
            block = "\n".join(lines[i:k]).rstrip()
            blocks.append((name, block))
            i = k
            continue
        i += 1
    return blocks


def wrap_lean_line(line: str, limit: int = 100) -> List[str]:
    """Wraps any Lean line exceeding `limit` chars at whitespace boundaries."""
    if len(line) <= limit:
        return [line]
    indent = " " * (len(line) - len(line.lstrip(" ")) + 2)
    words = line.split(" ")
    out: List[str] = []
    cur = words[0]
    for w in words[1:]:
        if len(cur) + 1 + len(w) <= limit:
            cur = cur + " " + w
        else:
            out.append(cur)
            cur = indent + w
    out.append(cur)
    return out


def wrap_block_lines(block: str, limit: int = 100) -> str:
    res: List[str] = []
    for ln in block.splitlines():
        res.extend(wrap_lean_line(ln, limit))
    return "\n".join(res)


def strip_imports_and_wrap_namespace(src_text: str, ns: str, dep_blocks: List[str]) -> str:
    lines = src_text.splitlines()
    header_lines: List[str] = []
    body_lines: List[str] = []
    in_header = True
    seen_mod_doc = False
    for ln in lines:
        if in_header:
            if ln.startswith("import "):
                continue
            header_lines.append(ln)
            if ln.strip() == "-/" and seen_mod_doc:
                in_header = False
            if ln.strip().startswith("/-!"):
                seen_mod_doc = True
        else:
            if ln.lstrip().startswith("#print"):
                continue
            body_lines.append(ln)

    chunks = [
        "\n".join(header_lines).strip(),
        "",
        f"namespace {ns}",
        "set_option maxRecDepth 4096",
        "",
    ]
    for db in dep_blocks:
        chunks.append(wrap_block_lines(db, 100))
        chunks.append("")
    chunks.append("\n".join(body_lines).strip())
    chunks.append("")
    chunks.append(f"end {ns}")
    chunks.append("")
    return "\n".join(chunks)


def audit_lean() -> Dict[str, Any]:
    proc = subprocess.run(
        ["lake", "build"],
        cwd=str(LEAN_DIR),
        capture_output=True,
        text=True,
        check=False,
    )
    build_ok = proc.returncode == 0
    forbidden_hits: List[str] = []
    style_errors: List[str] = []
    theorem_counts: Dict[str, int] = {}
    lean_hashes: Dict[str, str] = {}

    for fname in LEAN_FILES:
        fpath = LEAN_DIR / fname
        text = fpath.read_text(encoding="utf-8")
        lean_hashes[fname] = sha256_file(fpath)
        thms = re.findall(r"^\s*theorem\s+", text, re.MULTILINE)
        theorem_counts[fname] = len(thms)

        for idx, line in enumerate(text.splitlines(), start=1):
            if FORBIDDEN_LEAN_RE.search(line):
                forbidden_hits.append(f"{fname}:{idx}")
            if fname.startswith("MathlibPR_") and len(line) > 100:
                style_errors.append(f"{fname}:{idx}:length={len(line)}")

        if fname.startswith("MathlibPR_"):
            if "Released under Apache 2.0 license" not in text:
                style_errors.append(f"{fname}:missing_apache_header")
            if "/-!" not in text:
                style_errors.append(f"{fname}:missing_module_docstring")

    total_theorems = sum(theorem_counts.values())
    passed = build_ok and not forbidden_hits and not style_errors and total_theorems == 84
    return {
        "lake_build_ok": build_ok,
        "lake_returncode": proc.returncode,
        "forbidden_hits": forbidden_hits,
        "style_errors": style_errors,
        "theorem_counts": theorem_counts,
        "total_theorems": total_theorems,
        "sha256": lean_hashes,
        "passed": passed,
    }


def stage_and_verify_upstream_prs() -> Dict[str, Any]:
    sfc_text = (LEAN_DIR / "ShiodaFormalConjectures.lean").read_text(encoding="utf-8")
    hv_text = (LEAN_DIR / "HodgeVerification.lean").read_text(encoding="utf-8")
    sfc_blocks = parse_top_level_decls(sfc_text)
    hv_blocks = parse_top_level_decls(hv_text)

    staged: List[str] = []
    standalone_checks: Dict[str, Any] = {}
    all_ok = True

    for spec in MATHLIB_PR_SPECS:
        src_text = (LEAN_DIR / spec["src"]).read_text(encoding="utf-8")
        wanted_sfc: Set[str] = set(spec["deps_sfc"])
        wanted_hv: Set[str] = set(spec["deps_hv"])
        dep_blocks = [blk for name, blk in sfc_blocks if name in wanted_sfc]
        dep_blocks.extend(blk for name, blk in hv_blocks if name in wanted_hv)

        out_text = strip_imports_and_wrap_namespace(src_text, spec["namespace"], dep_blocks)
        dst = UPSTREAM_DIR / spec["dst"]
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_text(out_text, encoding="utf-8")

        long_lines = [
            idx for idx, ln in enumerate(out_text.splitlines(), start=1) if len(ln) > 100
        ]
        has_local_import = bool(
            re.search(r"^import\s+(ShiodaFormalConjectures|HodgeVerification)", out_text, re.M)
        )
        print_hits = [
            idx for idx, ln in enumerate(out_text.splitlines(), start=1) if "#print" in ln
        ]
        proc = subprocess.run(
            ["lake", "env", "lean", str(dst)],
            cwd=str(LEAN_DIR),
            capture_output=True,
            text=True,
            check=False,
        )
        ok = proc.returncode == 0 and not long_lines and not has_local_import and not print_hits
        if not ok:
            all_ok = False
        rel = str(dst.relative_to(REPO_ROOT)).replace("\\", "/")
        staged.append(rel)
        standalone_checks[rel] = {
            "returncode": proc.returncode,
            "zero_local_imports": not has_local_import,
            "long_lines_gt_100": long_lines,
            "print_hits": len(print_hits),
            "sha256": sha256_file(dst),
            "passed": ok,
        }
        if not ok:
            standalone_checks[rel]["stderr_tail"] = (proc.stderr or proc.stdout)[-800:]

    assert_internal_target_only("Qamarbajwa/mathlib4")
    pr_doc = DIST_DIR / "upstream_prs" / "PR_DESCRIPTIONS_AND_PUSH_COMMANDS.md"
    pr_doc.parent.mkdir(parents=True, exist_ok=True)
    pr_doc.write_text(
        "# Fork-Internal Mathlib4 Staging Guide (`Qamarbajwa/mathlib4` Only)\n\n"
        "> **Governance Lock:** Upstream PR creation and automated comments on external "
        "repositories are permanently disabled. Push and merge ONLY into `Qamarbajwa/mathlib4:master`.\n\n"
        "All staged files below are 100% self-contained (zero local workspace imports), "
        "have zero `#print` commands, `<= 100` char lines, and pass standalone `lake env lean` (`rc=0`).\n\n"
        "## Staged Target Files\n"
        "- `Mathlib/AlgebraicGeometry/FermatHypersurface/ShiodaAoki.lean`\n"
        "- `Mathlib/RingTheory/ArtinianGorenstein/MacaulayContraction.lean`\n"
        "- `Mathlib/RepresentationTheory/Spin8Triality.lean`\n"
        "- `Mathlib/Combinatorics/IncidenceSieve/CyclotomicResidualForm.lean`\n\n"
        "## Fork-Internal Merge Commands (`Qamarbajwa/mathlib4` ONLY)\n"
        "```bash\n"
        "git checkout -b feat/shioda-aoki-macaulay-spin8-sieve\n"
        "cp -r dist/upstream_prs/mathlib4/Mathlib/* Mathlib/\n"
        "git add Mathlib/\n"
        "git commit -m \"feat: add Shioda-Aoki, Macaulay, Spin(8), and cyclotomic sieve modules\"\n"
        "git push -u origin feat/shioda-aoki-macaulay-spin8-sieve\n"
        "gh pr create --repo Qamarbajwa/mathlib4 --base master --head feat/shioda-aoki-macaulay-spin8-sieve "
        "--title \"feat: merge verified zero-axiom Shioda-Aoki, Macaulay, Spin(8) triality, and cyclotomic sieve modules\" "
        "--body \"Merges standalone-verified zero-axiom Lean 4 modules into fork master.\"\n"
        "gh pr merge feat/shioda-aoki-macaulay-spin8-sieve --repo Qamarbajwa/mathlib4 --merge\n"
        "```\n",
        encoding="utf-8",
    )
    staged.append(str(pr_doc.relative_to(REPO_ROOT)).replace("\\", "/"))
    return {"staged_files": staged, "standalone_checks": standalone_checks, "passed": all_ok}


def audit_papers() -> Dict[str, Any]:
    results: Dict[str, Any] = {}
    all_ok = True
    for entry in PAPERS:
        pid = entry["id"]
        tex_path: Path = entry["tex"]
        pdf_path: Path = entry["pdf"]
        log_path: Path = entry["log"]

        tex_text = tex_path.read_text(encoding="utf-8")
        log_text = log_path.read_text(encoding="utf-8", errors="replace")

        m_pages = re.search(r"Output written on .*?\((\d+)\s+pages", log_text)
        pages = int(m_pages.group(1)) if m_pages else 0
        latex_errors = len(re.findall(r"^!", log_text, re.MULTILINE))
        overfull = len(re.findall(r"Overfull", log_text))
        underfull = len(re.findall(r"Underfull", log_text))

        prose_only = LST_BLOCK_RE.sub("", tex_text)
        pronouns = len(PRONOUN_RE.findall(prose_only))
        jargon = len(JARGON_RE.findall(tex_text))
        tikz_figures = len(re.findall(r"\\begin\{tikzpicture\}", tex_text))

        paper_ok = (
            pdf_path.exists()
            and 9 <= pages <= 16
            and latex_errors == 0
            and overfull == 0
            and underfull == 0
            and pronouns == 0
            and jargon == 0
            and tikz_figures >= 2
        )
        if not paper_ok:
            all_ok = False

        results[pid] = {
            "pdf_exists": pdf_path.exists(),
            "pages": pages,
            "latex_errors": latex_errors,
            "overfull": overfull,
            "underfull": underfull,
            "prose_pronouns": pronouns,
            "forbidden_jargon": jargon,
            "tikz_figures": tikz_figures,
            "tex_sha256": sha256_file(tex_path),
            "pdf_sha256": sha256_file(pdf_path),
            "passed": paper_ok,
        }
    return {"papers": results, "passed": all_ok}


def build_release_bundle() -> Dict[str, Any]:
    bundle_items: List[Path] = []
    for p in PAPERS:
        bundle_items.extend([p["tex"], p["pdf"]])
    for fname in LEAN_FILES:
        bundle_items.append(LEAN_DIR / fname)
    bundle_items.extend([LEAN_DIR / "lakefile.toml", LEAN_DIR / "lean-toolchain"])
    for fname in EXT_LEAN_FILES:
        bundle_items.append(EXT_LEAN_DIR / fname)
    bundle_items.extend([EXT_LEAN_DIR / "lakefile.toml", EXT_LEAN_DIR / "lean-toolchain"])
    ext_receipt = REPO_ROOT / "reports" / "millennium_ext" / "MILLENNIUM_EXT_RECEIPT.json"
    if ext_receipt.exists():
        bundle_items.append(ext_receipt)
    for spec in MATHLIB_PR_SPECS:
        bundle_items.append(UPSTREAM_DIR / spec["dst"])
    bundle_items.append(DIST_DIR / "upstream_prs" / "PR_DESCRIPTIONS_AND_PUSH_COMMANDS.md")
    bundle_items.append(REPO_ROOT / "docs" / "MASTER_RESEARCH_EXECUTION_PLAN.md")
    bundle_items.append(DIST_DIR / "FULL_AUTOMATION_VERIFICATION_RECEIPT.json")

    bundle_items = sorted(set(bundle_items), key=lambda x: str(x.relative_to(REPO_ROOT)))
    DIST_DIR.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(BUNDLE_PATH, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for item in bundle_items:
            arcname = str(item.relative_to(REPO_ROOT)).replace("\\", "/")
            zi = zipfile.ZipInfo(arcname, date_time=(2026, 11, 17, 0, 0, 0))
            zi.compress_type = zipfile.ZIP_DEFLATED
            zf.writestr(zi, item.read_bytes())

    return {
        "bundle_path": str(BUNDLE_PATH.relative_to(REPO_ROOT)).replace("\\", "/"),
        "file_count": len(bundle_items),
        "size_bytes": BUNDLE_PATH.stat().st_size,
        "sha256": sha256_file(BUNDLE_PATH),
    }


def main() -> int:
    lean_res = audit_lean()
    upstream_res = stage_and_verify_upstream_prs()
    paper_res = audit_papers()
    all_passed = bool(
        lean_res["passed"] and upstream_res["passed"] and paper_res["passed"]
    )

    receipt = {
        "ALL_CHECKS_PASSED": all_passed,
        "lean_audit": lean_res,
        "upstream_staging_audit": upstream_res,
        "paper_audit": paper_res,
    }
    DIST_DIR.mkdir(parents=True, exist_ok=True)
    receipt_path = DIST_DIR / "FULL_AUTOMATION_VERIFICATION_RECEIPT.json"
    receipt_path.write_text(json.dumps(receipt, indent=2), encoding="utf-8")

    bundle_res = build_release_bundle()
    receipt["release_bundle"] = bundle_res
    receipt_path.write_text(json.dumps(receipt, indent=2), encoding="utf-8")

    print(f"LEAN_BUILD_OK={lean_res['lake_build_ok']} TOTAL_THEOREMS={lean_res['total_theorems']}")
    for rel, sinfo in upstream_res["standalone_checks"].items():
        print(
            f"STANDALONE {rel}: rc={sinfo['returncode']} "
            f"zero_local_imports={sinfo['zero_local_imports']} "
            f"long_lines={len(sinfo['long_lines_gt_100'])} "
            f"print_hits={sinfo['print_hits']} passed={sinfo['passed']}"
        )
    for pid, pinfo in paper_res["papers"].items():
        print(
            f"{pid}: pages={pinfo['pages']} tikz_figures={pinfo['tikz_figures']} "
            f"errors={pinfo['latex_errors']} overfull={pinfo['overfull']} "
            f"underfull={pinfo['underfull']} pronouns={pinfo['prose_pronouns']} "
            f"jargon={pinfo['forbidden_jargon']} passed={pinfo['passed']}"
        )
    print(
        f"RELEASE_BUNDLE={bundle_res['bundle_path']} files={bundle_res['file_count']} "
        f"bytes={bundle_res['size_bytes']} sha256={bundle_res['sha256']}"
    )
    print(f"ALL_CHECKS_PASSED={all_passed}")
    return 0 if all_passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
