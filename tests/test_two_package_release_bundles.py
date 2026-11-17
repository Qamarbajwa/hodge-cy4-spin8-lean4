#!/usr/bin/env python3
"""Automated Pytest Gate for the Cleaned Zenodo Release Bundle.

Verifies:
  1. All 11 files in ZENODO_RELEASE_v1.0.0/ exist and are non-empty.
  2. PEER_REVIEW_SUBMISSION_v1.0.0/ and MATHLIB4_HODGE_UPSTREAM_PR_MANIFEST_v1.0.0.md are absent.
  3. SHA256SUMS.txt matches actual SHA-256 hashes of all 10 payload artifacts.
  4. Modest scope tokens (GLOBAL_HODGE_CONJECTURE = OPEN, Qamar Munawer, zero Mathlib / AI disclosure) are present.

Author: Qamar Munawer (Brandenburg University of Technology Cottbus-Senftenberg)
"""

from __future__ import annotations

import hashlib
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
ZENODO_DIR = ROOT / "ZENODO_RELEASE_v1.0.0"
PEER_REVIEW_DIR = ROOT / "PEER_REVIEW_SUBMISSION_v1.0.0"


def sha256_of(p: pathlib.Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def test_zenodo_bundle_contents():
    assert not PEER_REVIEW_DIR.exists(), "Unready PEER_REVIEW_SUBMISSION_v1.0.0 directory must remain removed"
    assert not (ROOT / "MATHLIB4_HODGE_UPSTREAM_PR_MANIFEST_v1.0.0.md").exists()

    expected_files = [
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
        "SHA256SUMS.txt",
    ]
    actual_files = sorted([f.name for f in ZENODO_DIR.glob("*")])
    assert len(actual_files) == 11, f"Expected 11 files, found {len(actual_files)}: {actual_files}"
    for name in expected_files:
        fp = ZENODO_DIR / name
        assert fp.exists(), f"Missing file in Zenodo bundle: {name}"
        assert fp.stat().st_size > 0, f"File is empty: {name}"


def test_sha256sums_match():
    sums_file = ZENODO_DIR / "SHA256SUMS.txt"
    sums_lines = sums_file.read_text(encoding="utf-8").strip().splitlines()
    assert len(sums_lines) == 10
    sums_map = {}
    for line in sums_lines:
        parts = line.split(maxsplit=1)
        sums_map[parts[1].strip()] = parts[0].strip()

    for name, expected_hash in sums_map.items():
        actual_hash = sha256_of(ZENODO_DIR / name)
        assert actual_hash == expected_hash, f"SHA256SUMS mismatch for {name}: {actual_hash} != {expected_hash}"


def test_honesty_tokens_scope_modesty_and_ai_disclosure():
    checks = [
        (ZENODO_DIR / ".zenodo.json", ["GLOBAL_HODGE_CONJECTURE", "OPEN", "Munawer", "zero Mathlib"]),
        (ZENODO_DIR / "README.md", ["GLOBAL_HODGE_CONJECTURE = OPEN", "Qamar Munawer", "AI Assistance Disclosure", "zero Mathlib"]),
        (ROOT / "ZENODO_ONLINE_DEPOSIT_PACKAGE_v1.0.0.md", ["GLOBAL_HODGE_CONJECTURE = OPEN", "Qamar Munawer", "AI Assistance Disclosure", "zero Mathlib"]),
    ]
    for p, tokens in checks:
        text = p.read_text(encoding="utf-8")
        for tok in tokens:
            assert tok in text, f"Token '{tok}' missing in {p}"
