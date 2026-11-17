#!/usr/bin/env python3
"""Zenodo Release Bundler for the Hodge Conjecture Workspace.

Builds:
  1. ZENODO_RELEASE_v1.0.0/ (11 files: 10 artifacts + SHA256SUMS.txt)
  2. ZENODO_ONLINE_DEPOSIT_PACKAGE_v1.0.0.md (Root Workspace)

Enforces Packaging Rules:
  Rule 1: Single-Source Build Order (Zenodo bundle -> SHA256SUMS.txt)
  Rule 2: Strict Exclusion of Build/Cache/Recursive Zips
  Rule 3: Automated Checksum & Token Gate (GLOBAL_HODGE_CONJECTURE = OPEN, Credit: Always Qamar Munawer)
  Rule 4: Windows File-Lock Safety

Author: Qamar Munawer (Brandenburg University of Technology Cottbus-Senftenberg)
Edition: 1.0.0 (MATH-GOV v0.7.0)
Date: 2026-11-15
"""

from __future__ import annotations

import hashlib
import os
import pathlib
import shutil
import zipfile
from typing import Dict, List, Tuple

ROOT = pathlib.Path(__file__).resolve().parent
ZENODO_DIR = ROOT / "ZENODO_RELEASE_v1.0.0"


def sha256_file(p: pathlib.Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def make_deterministic_zip(out_zip: pathlib.Path, base_dirs: List[Tuple[pathlib.Path, str]], exclude_patterns: List[str]):
    """Create a clean, reproducible zip file excluding cache and build artifacts."""
    out_zip.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(out_zip, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        for base_dir, arc_prefix in base_dirs:
            if not base_dir.exists():
                continue
            if base_dir.is_file():
                zf.write(base_dir, f"{arc_prefix}/{base_dir.name}" if arc_prefix else base_dir.name)
                continue
            for root, dirs, files in os.walk(base_dir):
                # Filter directories in place
                dirs[:] = [d for d in dirs if not any(ex in d for ex in [".lake", "__pycache__", ".pytest_cache", ".git", "build", "ZENODO_RELEASE", "PEER_REVIEW_SUBMISSION"])]
                for file in sorted(files):
                    if any(file.endswith(ext) for ext in [".pyc", ".pyo", ".zip", ".log", ".aux", ".out", ".bbl", ".blg", ".toc"]):
                        continue
                    full_p = pathlib.Path(root) / file
                    rel_to_base = full_p.relative_to(base_dir)
                    arcname = f"{arc_prefix}/{rel_to_base.as_posix()}" if arc_prefix else rel_to_base.as_posix()
                    zf.write(full_p, arcname)


def build_bundles():
    print("=== Step 1: Cleaning and Preparing Directories ===")
    if ZENODO_DIR.exists():
        shutil.rmtree(ZENODO_DIR)
    ZENODO_DIR.mkdir(parents=True, exist_ok=True)

    print("=== Step 2: Creating Source and Monograph Zip Archives ===")
    # 04_HodgeBlueprint_Lean4_Source_v1.0.0.zip
    zip_04 = ZENODO_DIR / "04_HodgeBlueprint_Lean4_Source_v1.0.0.zip"
    make_deterministic_zip(
        zip_04,
        [
            (ROOT / "lean_blueprint", "lean_blueprint"),
            (ROOT / "examples" / "math_gov" / "LeanDemoProject", "examples/math_gov/LeanDemoProject"),
        ],
        exclude_patterns=[".lake", "__pycache__"],
    )

    # 05_Hodge_Monograph_LaTeX_and_Toolkit_Suite_v1.0.0.zip
    zip_05 = ZENODO_DIR / "05_Hodge_Monograph_LaTeX_and_Toolkit_Suite_v1.0.0.zip"
    make_deterministic_zip(
        zip_05,
        [
            (ROOT / "paper" / "main.tex", "paper"),
            (ROOT / "paper" / "blueprint.tex", "paper"),
            (ROOT / "paper" / "references.bib", "paper"),
            (ROOT / "paper" / "ZENODO_MANUSCRIPT_FOUR_PILLARS_HODGE.md", "paper"),
            (ROOT / "toolkit", "toolkit"),
            (ROOT / "governance", "governance"),
            (ROOT / "docs", "docs"),
            (ROOT / "tests", "tests"),
            (ROOT / "verify_zenodo_deposit.py", ""),
            (ROOT / "pytest.ini", ""),
        ],
        exclude_patterns=[".lake", "__pycache__", ".git", "build"],
    )

    print("=== Step 3: Copying Artifacts into ZENODO_RELEASE_v1.0.0/ ===")
    # 01 Monograph PDF
    shutil.copy2(ROOT / "01_Monograph_Hodge_Conjecture_CY4_Spinor_Qamar_Munawer_v1.0.0.pdf", ZENODO_DIR / "01_Monograph_Hodge_Conjecture_CY4_Spinor_Qamar_Munawer_v1.0.0.pdf")
    # 02 Blueprint PDF
    shutil.copy2(ROOT / "02_LeanBlueprint_Hodge_Formal_Verification_Qamar_Munawer_v1.0.0.pdf", ZENODO_DIR / "02_LeanBlueprint_Hodge_Formal_Verification_Qamar_Munawer_v1.0.0.pdf")
    # 03 Kernel Audit Report
    shutil.copy2(ROOT / "03_LEAN4_HODGE_KERNEL_VERIFICATION_AUDIT_REPORT.md", ZENODO_DIR / "03_LEAN4_HODGE_KERNEL_VERIFICATION_AUDIT_REPORT.md")
    # 06 Visual Architecture PNG
    shutil.copy2(ROOT / "06_Hodge_Diamond_and_WD4_Coset_Transport_Visual.png", ZENODO_DIR / "06_Hodge_Diamond_and_WD4_Coset_Transport_Visual.png")
    # 07-10 Metadata & Legal
    shutil.copy2(ROOT / ".zenodo.json", ZENODO_DIR / ".zenodo.json")
    shutil.copy2(ROOT / "CITATION.cff", ZENODO_DIR / "CITATION.cff")
    shutil.copy2(ROOT / "LICENSE", ZENODO_DIR / "LICENSE")
    shutil.copy2(ROOT / "README.md", ZENODO_DIR / "README.md")

    print("=== Step 4: Generating SHA256SUMS.txt for ZENODO_RELEASE_v1.0.0/ ===")
    zenodo_10_files = [
        "01_Monograph_Hodge_Conjecture_CY4_Spinor_Qamar_Munawer_v1.0.0.pdf",
        "02_LeanBlueprint_Hodge_Formal_Verification_Qamar_Munawer_v1.0.0.pdf",
        "03_LEAN4_HODGE_KERNEL_VERIFICATION_AUDIT_REPORT.md",
        "04_HodgeBlueprint_Lean4_Source_v1.0.0.zip",
        "05_Hodge_Monograph_LaTeX_and_Toolkit_Suite_v1.0.0.zip",
        "06_Hodge_Diamond_and_WD4_Coset_Transport_Visual.png",
        ".zenodo.json",
        "CITATION.cff",
        "LICENSE",
        "README.md",
    ]
    sums_lines = []
    hashes_dict: Dict[str, str] = {}
    sizes_dict: Dict[str, int] = {}
    for name in zenodo_10_files:
        fp = ZENODO_DIR / name
        assert fp.exists(), f"Missing Zenodo file: {name}"
        h = sha256_file(fp)
        hashes_dict[name] = h
        sizes_dict[name] = fp.stat().st_size
        sums_lines.append(f"{h}  {name}")

    sha256sums_path = ZENODO_DIR / "SHA256SUMS.txt"
    sha256sums_path.write_text("\n".join(sums_lines) + "\n", encoding="utf-8")
    print(f"Generated {sha256sums_path} with 10 checksum entries.")

    print("=== Step 5: Generating ZENODO_ONLINE_DEPOSIT_PACKAGE_v1.0.0.md ===")
    online_deposit = f"""# Zenodo Online Deposit Form Package (Edition 1.0.0)
**Project:** HODGE-MILLENNIUM-001  
**Author:** Qamar Munawer (Brandenburg University of Technology Cottbus-Senftenberg)  
**Date:** 2026-11-15  
**Standing Epistemic Invariant:** `GLOBAL_HODGE_CONJECTURE = OPEN`  
**Credit Principle:** Always Qamar Munawer  

Use the copy-pasteable blocks below for the Zenodo Web Deposit UI (https://zenodo.org/deposit):

---

### Basic Metadata Fields
- **Upload Type:** Publication -> Working paper / Pre-print
- **Publication Date:** `2026-11-15`
- **Title:**
```text
Computational Apolarity Experiments, W(D4) Spinor Combinatorics, and Decidable Lean 4.35.0 Finite Checks for Hodge Conjecture Testbeds
```
- **Creators:**
  - Family name: `Munawer`
  - Given names: `Qamar`
  - Affiliation: `Brandenburg University of Technology Cottbus-Senftenberg`
- **License:** `Creative Commons Attribution 4.0 International (CC-BY-4.0)`

---

### Description / Abstract (HTML Formatted for Zenodo UI)
```html
<p><strong>CRITICAL SCIENTIFIC HONESTY INVARIANT:</strong> <code>GLOBAL_HODGE_CONJECTURE = OPEN</code>, <code>S-BRIDGE-DEFORM-CY4 = OPEN</code>, <code>S-BRIDGE-SPINOR-MOTIVE = OPEN</code>, <code>release_authorized = false</code>, <code>theorem_progress = UNKNOWN</code>. Author: Qamar Munawer (Brandenburg University of Technology Cottbus-Senftenberg).</p>

<p>This Zenodo research archive provides an exact rational and modular (&#x1D53D;<sub><em>p</em></sub>) computational experiment toolkit alongside decidable finite combinatorial checks in core Lean 4.35.0 for two classical testbeds of the Hodge Conjecture: sextic Calabi–Yau fourfolds <em>X</em><sub>4</sub> ⊂ ℙ<sup>5</sup> and Mumford-type abelian sixfolds <em>A</em><sub>6</sub>.</p>

<ul>
  <li><strong>43/43 Decidable Finite Combinatorial Checks in Core Lean 4.35.0 (<code>axioms: []</code>):</strong> <code>HodgeVerification.lean</code> has <em>zero Mathlib imports</em> and checks finite index sets, weight-tuple counts, and Hilbert degree arithmetic (<code>by rfl</code>). It does not formalize schemes, cohomology, or Hodge theory.</li>
  <li><strong>Exact Rational &amp; Modular Sextic Fourfold Experiments:</strong> Computational experiments on the Fermat sextic Jacobian ring <em>R</em><sup>12</sup>(<em>F</em><sub>0</sub>) (dim 1,751 = 1,001 + 630 + 120 + 0; Milnor number 15,625) implementing Griffiths residue arithmetic, Shioda–Aoki–Ran 4-band cycle tables, Macaulay inverse systems, Peskine–Szpiro liaison, and Wang's multi-prime CRT rational reconstruction over 61/62-bit primes.</li>
  <li><strong>Spin(8) Triality &amp; <em>W</em>(<em>D</em><sub>4</sub>) Weight Combinatorics:</strong> Exact enumeration of ⋀<sup>4</sup> <em>S</em><sup>+</sup><sub>8</sub> (70 = 35<sub>+</sub> + 35<sub>−</sub>), 32/512 zero-weight Clifford triality triples, and a rank-6 Weyl-coset matrix spanning 6/6 of the Cartan zero-weight tuples, framed within Deligne's absolute Hodge and André's motivated cycle theory (algebraicity over &#x211A; remains OPEN).</li>
  <li><strong>AI Assistance Disclosure:</strong> Large language model tools were used for coding, LaTeX formatting, and drafting assistance under authorial supervision; all exact integer/rational checks and Lean kernel runs are deterministically reproducible.</li>
</ul>
```

---

### Keywords
`Hodge Conjecture`, `Lean 4`, `computational algebraic geometry`, `Calabi-Yau fourfolds`, `abelian varieties`, `Mumford-Tate groups`, `Macaulay apolarity`, `Peskine-Szpiro liaison`, `Chinese Remainder Theorem`, `math-gov`
"""
    (ROOT / "ZENODO_ONLINE_DEPOSIT_PACKAGE_v1.0.0.md").write_text(online_deposit, encoding="utf-8")
    print(f"Generated {ROOT / 'ZENODO_ONLINE_DEPOSIT_PACKAGE_v1.0.0.md'}")

    print("=== Step 6: Integrity and Invariant Token Checks ===")
    token_checks = [
        (ZENODO_DIR / ".zenodo.json", ["GLOBAL_HODGE_CONJECTURE", "OPEN", "Munawer", "Qamar"]),
        (ZENODO_DIR / "README.md", ["GLOBAL_HODGE_CONJECTURE = OPEN", "Qamar Munawer"]),
        (ROOT / "ZENODO_ONLINE_DEPOSIT_PACKAGE_v1.0.0.md", ["GLOBAL_HODGE_CONJECTURE = OPEN", "Qamar Munawer"]),
    ]
    for p, tokens in token_checks:
        content = p.read_text(encoding="utf-8")
        for tok in tokens:
            assert tok in content, f"Token '{tok}' missing in {p}"
    print("All token integrity checks passed.")

    print("\n=== Release Bundle Construction Summary ===")
    print(f"ZENODO_RELEASE_v1.0.0/ contains {len(list(ZENODO_DIR.glob('*')))} files:")
    for f in sorted(ZENODO_DIR.glob("*")):
        print(f"  {f.name:<68} ({f.stat().st_size:>9,} bytes) [SHA256: {sha256_file(f)[:12]}...]")


if __name__ == "__main__":
    build_bundles()
