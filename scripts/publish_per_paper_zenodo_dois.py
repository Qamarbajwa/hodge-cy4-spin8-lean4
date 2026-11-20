"""Publish individual Zenodo DOIs for each of Paper 1 through Paper 6.

Enforces the same verification gates as `automate_verified_zenodo_upload.py`,
creates 6 separate Zenodo depositions (one per paper), uploads each paper's
verified PDF alongside its verification receipt, verifies remote MD5 checksums,
publishes each deposition, and writes `dist/ZENODO_PER_PAPER_DOIS_RECEIPT.json`.
"""

from __future__ import annotations

import json
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from automate_verified_zenodo_upload import (
    EXT_RECEIPT_PATH,
    RECEIPT_PATH,
    REPO_ROOT,
    VERIFIED_PAPERS,
    file_hashes,
    resolve_zenodo_token,
)

OUT_RECEIPT_PATH = REPO_ROOT / "dist" / "ZENODO_PER_PAPER_DOIS_RECEIPT.json"

PAPER_SPECS: Dict[str, Dict[str, Any]] = {
    "Paper1": {
        "title": "Constructive Formalization of Shioda-Aoki Fermat Fourfold Character Cohomology in Lean 4",
        "description": (
            "<p>Paper 1 of the Lean 4.35.0 Hodge Conjecture testbed series: constructive formalization of "
            "Shioda-Aoki Fermat fourfold character cohomology, Band 1-4 combinatorics, and inductive cycle "
            "synthesis with zero axioms.</p>"
            "<p><strong>Scope:</strong> Certifies finite-dimensional algebraic/combinatorial Fermat character "
            "structures; the global Clay Millennium Hodge Conjecture (<code>HODGE-MILLENNIUM-001</code>) remains strictly OPEN.</p>"
        ),
        "keywords": ["Lean 4", "Hodge Conjecture", "Fermat fourfolds", "Shioda-Aoki classification"],
    },
    "Paper2": {
        "title": "Constructive Formalization of Artinian Gorenstein Apolarity and Macaulay Contraction Ranks for Calabi-Yau Fourfolds in Lean 4",
        "description": (
            "<p>Paper 2 of the Lean 4.35.0 Hodge Conjecture testbed series: Artinian Gorenstein apolarity, "
            "Macaulay inverse systems, and Wiebe-Scheja-Storch colon-ideal transition determinants over Z.</p>"
            "<p><strong>Scope:</strong> Certifies finite polynomial-quotient structures; the global Clay Millennium "
            "Hodge Conjecture (<code>HODGE-MILLENNIUM-001</code>) remains strictly OPEN.</p>"
        ),
        "keywords": ["Lean 4", "Macaulay apolarity", "Artinian Gorenstein", "Wiebe-Scheja-Storch"],
    },
    "Paper3": {
        "title": "Constructive Formalization of Spin(8) Triality, W(D4) Chiral Orthogonality, and Mumford Spinor Representations in Lean 4",
        "description": (
            "<p>Paper 3 of the Lean 4.35.0 Hodge Conjecture testbed series: Spin(8) triality, W(D4) chiral "
            "orthogonality, and Mumford-Tate spinor representations in pure zero-axiom Lean 4.</p>"
            "<p><strong>Scope:</strong> Certifies finite Lie-algebraic and weight-lattice invariants; the global "
            "Clay Millennium Hodge Conjecture (<code>HODGE-MILLENNIUM-001</code>) remains strictly OPEN.</p>"
        ),
        "keywords": ["Lean 4", "Spin(8) triality", "Mumford fourfolds", "W(D4) root system"],
    },
    "Paper4": {
        "title": "Exact Float-Free Gauss-Manin Jet Reconstruction and Infinitesimal Voisin Integrability for Calabi-Yau Fourfolds",
        "description": (
            "<p>Paper 4 of the Lean 4.35.0 Hodge Conjecture testbed series: exact float-free Gauss-Manin jet "
            "reconstruction, Gotzmann flatness, and infinitesimal Voisin integrability for Calabi-Yau fourfolds.</p>"
            "<p><strong>Scope:</strong> Certifies finite-order Taylor jet structures; the global Clay Millennium "
            "Hodge Conjecture (<code>HODGE-MILLENNIUM-001</code>) remains strictly OPEN.</p>"
        ),
        "keywords": ["Lean 4", "Gauss-Manin connection", "Gotzmann persistence", "Calabi-Yau fourfolds"],
    },
    "Paper5": {
        "title": "Finite Cyclotomic Incidence Sieves, Multi-Block Collision Excess, and Residual Form Extraction in Lean 4",
        "description": (
            "<p>Paper 5 of the Lean 4.35.0 Hodge Conjecture testbed series: finite cyclotomic incidence sieves, "
            "multi-block collision excess, and residual form extraction in zero-axiom Lean 4.</p>"
            "<p><strong>Scope:</strong> Certifies finite cyclotomic incidence bounds; the global Clay Millennium "
            "Hodge Conjecture (<code>HODGE-MILLENNIUM-001</code>) remains strictly OPEN.</p>"
        ),
        "keywords": ["Lean 4", "Cyclotomic incidence sieve", "Residual forms", "Combinatorics"],
    },
    "Paper6": {
        "title": "Matrix-Operator Unification, High-Degree Fermat Orbits, Higher-Order Jets, and Weil Spectral Projectors in Lean 4",
        "description": (
            "<p>Paper 6 of the Lean 4.35.0 Hodge Conjecture testbed series (208 zero-axiom declarations across "
            "42 modules, 27/27 symbolic/GPU explorers): matrix-operator unification, Cl(0,7) chiral Schur "
            "complement (1152), Spin(7) Cayley calibration, CM graph realization (2 Z_CM = T_ch), Fermat "
            "m=25,35,49,55 conical Schur ladders, CY4 Koszul Hilbert profile, and finite Gysin exactness.</p>"
            "<p><strong>Scope:</strong> Certifies finite-dimensional algebraic/representation-theoretic results "
            "and conditional bridges; the global Clay Millennium Hodge Conjecture (<code>HODGE-MILLENNIUM-001</code>) "
            "remains strictly OPEN.</p>"
        ),
        "keywords": ["Lean 4", "Cl(0,7) Clifford algebra", "Schur complement", "Spin(7) Cayley", "Hodge Conjecture"],
    },
}


def _zenodo_json(url: str, token: str, payload: Dict[str, Any] | None = None, method: str = "GET") -> Dict[str, Any]:
    headers = {"Authorization": f"Bearer {token}"}
    data: bytes | None = None
    if payload is not None:
        headers["Content-Type"] = "application/json"
        data = json.dumps(payload).encode("utf-8")
    for attempt in range(4):
        req = urllib.request.Request(url, data=data, headers=headers, method=method)
        try:
            with urllib.request.urlopen(req, timeout=180) as resp:
                raw = resp.read().decode("utf-8")
                return json.loads(raw) if raw.strip() else {}
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            if exc.code in (429, 500, 502, 503, 504) and attempt < 3:
                time.sleep(3 * (attempt + 1))
                continue
            raise RuntimeError(f"Zenodo HTTP {exc.code} on {method} {url}: {body}") from exc
    raise RuntimeError(f"Zenodo request failed after retries: {method} {url}")


def _upload_file(bucket_url: str, token: str, path: Path) -> Dict[str, Any]:
    sha256, md5 = file_hashes(path)
    data = path.read_bytes()
    for attempt in range(4):
        req = urllib.request.Request(
            f"{bucket_url}/{path.name}",
            data=data,
            headers={"Authorization": f"Bearer {token}", "Content-Type": "application/octet-stream"},
            method="PUT",
        )
        try:
            with urllib.request.urlopen(req, timeout=180) as resp:
                info = json.loads(resp.read().decode("utf-8"))
            remote_chk = info.get("checksum", "")
            if remote_chk != f"md5:{md5}":
                raise RuntimeError(f"MD5 mismatch for {path.name}: {remote_chk} vs md5:{md5}")
            return {
                "filename": path.name,
                "size_bytes": path.stat().st_size,
                "local_sha256": sha256,
                "local_md5": md5,
                "remote_checksum": remote_chk,
            }
        except urllib.error.HTTPError as exc:
            if exc.code in (429, 500, 502, 503, 504) and attempt < 3:
                time.sleep(3 * (attempt + 1))
                continue
            raise
    raise RuntimeError(f"Failed uploading {path.name}")


def main() -> int:
    receipt = json.loads(RECEIPT_PATH.read_text(encoding="utf-8"))
    ext_receipt = json.loads(EXT_RECEIPT_PATH.read_text(encoding="utf-8"))
    if receipt.get("ALL_CHECKS_PASSED") is not True or ext_receipt.get("EXT_CHECKS_PASSED") is not True:
        raise RuntimeError("GATE BLOCKED: Verification receipts are not all passing.")

    token, api_base, env_name = resolve_zenodo_token()
    if not token:
        raise RuntimeError("ZENODO_TOKEN not found.")

    today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    papers_meta = receipt["paper_audit"]["papers"]
    results: Dict[str, Any] = {}

    for pid, pdf_path in VERIFIED_PAPERS:
        info = papers_meta[pid]
        live_sha, _ = file_hashes(pdf_path)
        if live_sha != info["pdf_sha256"]:
            raise RuntimeError(f"SHA-256 mismatch for {pid}: {live_sha} != {info['pdf_sha256']}")

        spec = PAPER_SPECS[pid]
        meta = {
            "metadata": {
                "title": spec["title"],
                "upload_type": "publication",
                "publication_type": "workingpaper",
                "publication_date": today_str,
                "version": "1.5.0-rosetta",
                "license": "cc-by-4.0",
                "language": "eng",
                "creators": [
                    {
                        "name": "Munawer, Qamar",
                        "affiliation": "Brandenburg University of Technology Cottbus\u2013Senftenberg",
                    }
                ],
                "keywords": spec["keywords"],
                "description": spec["description"],
                "notes": (
                    f"{pid} verified cleanly via pdflatex (0 errors, 0 overfull, 0 underfull). "
                    "Related collection DOI: 10.5281/zenodo.24398323 (concept 10.5281/zenodo.24329779)."
                ),
            }
        }

        dep = _zenodo_json(f"{api_base}/deposit/depositions", token, payload=meta, method="POST")
        dep_id = int(dep["id"])
        bucket_url = dep["links"]["bucket"]

        files_to_upload = [pdf_path, RECEIPT_PATH]
        if pid == "Paper6":
            files_to_upload.append(EXT_RECEIPT_PATH)

        uploaded = [_upload_file(bucket_url, token, fp) for fp in files_to_upload]
        pub = _zenodo_json(f"{api_base}/deposit/depositions/{dep_id}/actions/publish", token, method="POST")

        doi = str(pub.get("doi") or "")
        concept_doi = str(pub.get("conceptdoi") or "")
        rec_url = f"https://zenodo.org/records/{dep_id}"
        results[pid] = {
            "deposition_id": dep_id,
            "doi": doi,
            "concept_doi": concept_doi,
            "record_url": rec_url,
            "pdf_filename": pdf_path.name,
            "pdf_sha256": live_sha,
            "uploaded_files": uploaded,
        }
        print(f"{pid}: DOI={doi} CONCEPT_DOI={concept_doi} URL={rec_url}")

    out = {
        "status": "PUBLISHED",
        "api_base": api_base,
        "token_source": env_name,
        "published_utc": datetime.now(timezone.utc).isoformat(),
        "collection_doi": "10.5281/zenodo.24398323",
        "collection_concept_doi": "10.5281/zenodo.24329779",
        "papers": results,
    }
    OUT_RECEIPT_PATH.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"WROTE_RECEIPT={OUT_RECEIPT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
