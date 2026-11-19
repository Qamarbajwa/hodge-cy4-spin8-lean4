"""Strict Verification-Gated Zenodo Stager & Automated Uploader.

Enforces hard cryptographic and typographic gates prior to staging or uploading
any release files to Zenodo:
1. Reads `dist/FULL_AUTOMATION_VERIFICATION_RECEIPT.json` and
   `reports/millennium_ext/MILLENNIUM_EXT_RECEIPT.json` and requires:
   - `ALL_CHECKS_PASSED == True`, `lean_audit["lake_build_ok"] == True`,
     `lean_audit["total_theorems"] == 84`, `upstream_staging_audit["passed"] == True`,
   - `EXT_CHECKS_PASSED == True`, `baseline_lock["locked_baseline_intact"] == True`,
     `extension_lean_audit["passed"] == True`, `long_lines_gt_100 == []`,
     `unexpected_axiom_lines == []`.
2. Recomputes live SHA-256 checksums for Paper1..Paper6 PDFs and
   `HODGE_LEAN4_5PAPER_RELEASE_BUNDLE.zip`, refusing any paper unless:
   - `passed == True`, `latex_errors == 0`, `overfull == 0`, `underfull == 0`,
   - `prose_pronouns == 0`, `forbidden_jargon == 0`, `tikz_figures >= 2`,
   - live PDF SHA-256 matches `paper_audit["papers"][pid]["pdf_sha256"]`.
3. Explicitly blocks all legacy/disqualified PDFs (`01_Monograph_...pdf`,
   `02_LeanBlueprint_...pdf`, `Munawer_Hodge_Apolarity_Spin8_Lean4_Journal.pdf`).
4. Stages `dist/zenodo_verified_deposit_v1.0/` containing ONLY the 6 verified
   PDFs, `HODGE_LEAN4_5PAPER_RELEASE_BUNDLE.zip`,
   `FULL_AUTOMATION_VERIFICATION_RECEIPT.json`, `MILLENNIUM_EXT_RECEIPT.json`,
   and `zenodo_metadata.json`.
5. Automatically uploads the verified artifact files via the Zenodo REST API
   when `ZENODO_TOKEN`, `ZENODO_API_TOKEN`, `ZENODO_ACCESS_TOKEN`, or
   `ZENODO_SANDBOX_TOKEN` is set in environment, `.env`, or Windows Registry,
   verifies remote MD5 checksums, and writes `dist/ZENODO_UPLOAD_RECEIPT.json`.
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Dict, List, Tuple


REPO_ROOT = Path(__file__).resolve().parent.parent
DIST_DIR = REPO_ROOT / "dist"
RECEIPT_PATH = DIST_DIR / "FULL_AUTOMATION_VERIFICATION_RECEIPT.json"
EXT_RECEIPT_PATH = REPO_ROOT / "reports" / "millennium_ext" / "MILLENNIUM_EXT_RECEIPT.json"
DEPOSIT_DIR = DIST_DIR / "zenodo_verified_deposit_v1.0"
UPLOAD_RECEIPT_PATH = DIST_DIR / "ZENODO_UPLOAD_RECEIPT.json"

VERIFIED_PAPERS: List[Tuple[str, Path]] = [
    ("Paper1", REPO_ROOT / "paper" / "paper1_shioda_aoki_lean4" / "Paper1_Shioda_Aoki_Fermat_Lean4.pdf"),
    ("Paper2", REPO_ROOT / "paper" / "paper2_macaulay_apolarity_lean4" / "Paper2_Macaulay_Apolarity_CY4_Lean4.pdf"),
    ("Paper3", REPO_ROOT / "paper" / "paper3_spin8_mumford_lean4" / "Paper3_Spin8_Triality_Mumford_Lean4.pdf"),
    ("Paper4", REPO_ROOT / "paper" / "paper4_gauss_manin_jets" / "Paper4_Gauss_Manin_Jet_Reconstruction.pdf"),
    ("Paper5", REPO_ROOT / "paper" / "paper5_cyclotomic_incidence_sieve" / "Paper5_Cyclotomic_Incidence_Sieve_Lean4.pdf"),
    ("Paper6", REPO_ROOT / "paper" / "paper6_millennium_frontier_extensions" / "Paper6_Millennium_Frontier_Extensions_Lean4.pdf"),
]

BLOCKED_LEGACY_PATTERNS = (
    "01_Monograph",
    "02_LeanBlueprint",
    "Munawer_Hodge_Apolarity_Spin8_Lean4_Journal",
)


def file_hashes(path: Path) -> Tuple[str, str]:
    sha = hashlib.sha256()
    md5 = hashlib.md5()
    with path.open("rb") as f:
        while True:
            chunk = f.read(65536)
            if not chunk:
                break
            sha.update(chunk)
            md5.update(chunk)
    return sha.hexdigest(), md5.hexdigest()


def load_dotenv_tokens() -> Dict[str, str]:
    env_map: Dict[str, str] = {}
    for candidate in (REPO_ROOT / ".env", REPO_ROOT.parent / ".env"):
        if not candidate.exists():
            continue
        for raw in candidate.read_text(encoding="utf-8").splitlines():
            line = raw.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            env_map.setdefault(k.strip(), v.strip().strip('"').strip("'"))
    return env_map


def load_windows_registry_env(key: str) -> str:
    if sys.platform != "win32":
        return ""
    try:
        import winreg  # type: ignore

        for hive, subkey in (
            (winreg.HKEY_CURRENT_USER, r"Environment"),
            (
                winreg.HKEY_LOCAL_MACHINE,
                r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment",
            ),
        ):
            try:
                with winreg.OpenKey(hive, subkey) as reg_key:
                    val, _ = winreg.QueryValueEx(reg_key, key)
                    if isinstance(val, str) and val.strip():
                        return val.strip()
            except OSError:
                continue
    except Exception:
        return ""
    return ""


def resolve_zenodo_token() -> Tuple[str, str, str]:
    """Returns `(token, api_base, env_var_name)` or `("", "", "")` if unset."""
    dotenv_vals = load_dotenv_tokens()
    candidates = [
        ("ZENODO_TOKEN", "https://zenodo.org/api"),
        ("ZENODO_API_TOKEN", "https://zenodo.org/api"),
        ("ZENODO_ACCESS_TOKEN", "https://zenodo.org/api"),
        ("ZENODO_SANDBOX_TOKEN", "https://sandbox.zenodo.org/api"),
    ]
    for key, base in candidates:
        val = (
            os.environ.get(key)
            or dotenv_vals.get(key, "")
            or load_windows_registry_env(key)
        )
        if val.strip():
            return val.strip(), base, key
    return "", "", ""


def build_zenodo_metadata(total_theorems: int, version: str = "1.1.3") -> Dict[str, Any]:
    from datetime import datetime, timezone

    today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    return {
        "metadata": {
            "title": (
                "Formalized Lean 4 Series (Papers 1-6): Shioda-Aoki Characters, Artinian "
                "Gorenstein Apolarity, Spin(8) Triality, Order-8 Gauss-Manin Jets, "
                "Cyclotomic Incidence Sieves, and Conditional Fermat Bridges"
            ),
            "upload_type": "publication",
            "publication_type": "workingpaper",
            "publication_date": today_str,
            "version": version,
            "license": "cc-by-4.0",
            "language": "eng",
            "creators": [
                {
                    "name": "Munawer, Qamar",
                    "affiliation": "Brandenburg University of Technology Cottbus\u2013Senftenberg",
                }
            ],
            "keywords": [
                "Lean 4",
                "Fermat fourfolds",
                "Shioda-Aoki classification",
                "Macaulay inverse systems",
                "Wiebe-Scheja-Storch colon ideals",
                "Spin(8) triality",
                "Gauss-Manin jet transport",
                "Gotzmann persistence",
                "Cyclotomic incidence sieve",
                "Cayley trick",
            ],
            "description": (
                f"<p>Verified release archive accompanying the six-paper Lean 4.35.0 series "
                f"(13 baseline modules + 7 extension modules, {total_theorems} axiom-free kernel "
                f"declarations, and six peer-review-formatted manuscripts with 12 TikZ diagrams) "
                "covering Shioda-Aoki cyclotomic character combinatorics through m=60, "
                "m=25 cyclic-coset cones, Wiebe-Scheja-Storch transition determinants (G<=3 over Z), "
                "Spin(8) triality and idempotent Weil projectors, order-8 Gauss-Manin jet transport, "
                "non-Fermat 3-var quotient palindromicity, Cayley-trick complete-intersection "
                "profiles in P^6, Poly6 evaluation homomorphisms, and conditional Fermat "
                "algebraicity bridges.</p>"
                "<p><strong>Scope and Conditional Interfaces:</strong> Every unconditional Lean 4 theorem in "
                "this deposit proves exact finite-dimensional combinatorial, polynomial-quotient, or Lie-algebraic "
                "results, while classical Lefschetz, Griffiths, Shioda, and Aoki algebraic-geometry bridges are "
                "isolated inside explicit modular hypothesis structures (<code>FermatFourfoldHodgeBridge</code>).</p>"
            ),
            "notes": (
                "All 6 manuscripts passed pdflatex (0 errors, 0 overfull, 0 underfull, >= 2 TikZ figures each) "
                "and live SHA-256 verification against FULL_AUTOMATION_VERIFICATION_RECEIPT.json and "
                "MILLENNIUM_EXT_RECEIPT.json."
            ),
        }
    }


def verify_and_stage() -> Dict[str, Any]:
    if not RECEIPT_PATH.exists():
        raise RuntimeError(f"Missing verification receipt: {RECEIPT_PATH}")
    if not EXT_RECEIPT_PATH.exists():
        raise RuntimeError(f"Missing extension verification receipt: {EXT_RECEIPT_PATH}")

    receipt = json.loads(RECEIPT_PATH.read_text(encoding="utf-8"))
    if receipt.get("ALL_CHECKS_PASSED") is not True:
        raise RuntimeError("GATE BLOCKED: ALL_CHECKS_PASSED is not True in verification receipt.")

    lean_audit = receipt.get("lean_audit", {})
    if lean_audit.get("total_theorems") != 84 or lean_audit.get("lake_build_ok") is not True:
        raise RuntimeError("GATE BLOCKED: lean_audit must confirm lake_build_ok=True and total_theorems=84.")

    if receipt.get("upstream_staging_audit", {}).get("passed") is not True:
        raise RuntimeError("GATE BLOCKED: upstream_staging_audit did not pass.")

    ext_receipt = json.loads(EXT_RECEIPT_PATH.read_text(encoding="utf-8"))
    if ext_receipt.get("EXT_CHECKS_PASSED") is not True:
        raise RuntimeError("GATE BLOCKED: EXT_CHECKS_PASSED is not True in MILLENNIUM_EXT_RECEIPT.json.")
    if ext_receipt.get("baseline_lock", {}).get("locked_baseline_intact") is not True:
        raise RuntimeError("GATE BLOCKED: locked_baseline_intact is not True.")
    ext_lean = ext_receipt.get("extension_lean_audit", {})
    if (
        ext_lean.get("passed") is not True
        or ext_lean.get("lake_build_ok") is not True
        or ext_lean.get("long_lines_gt_100") != []
        or ext_lean.get("unexpected_axiom_lines") != []
    ):
        raise RuntimeError(f"GATE BLOCKED: extension_lean_audit failed: {ext_lean}")

    total_theorems = int(lean_audit["total_theorems"]) + int(ext_lean.get("extension_theorems", 0))

    papers_meta = receipt.get("paper_audit", {}).get("papers", {})
    verified_files: List[Dict[str, Any]] = []

    for pid, pdf_path in VERIFIED_PAPERS:
        for blocked in BLOCKED_LEGACY_PATTERNS:
            if blocked in pdf_path.name:
                raise RuntimeError(f"GATE BLOCKED: Disqualified legacy filename detected: {pdf_path.name}")
        if not pdf_path.exists():
            raise RuntimeError(f"GATE BLOCKED: Missing verified PDF for {pid}: {pdf_path}")

        info = papers_meta.get(pid)
        if not info:
            raise RuntimeError(f"GATE BLOCKED: {pid} missing from verification receipt.")

        checks_ok = (
            info.get("passed") is True
            and info.get("latex_errors") == 0
            and info.get("overfull") == 0
            and info.get("underfull") == 0
            and info.get("prose_pronouns") == 0
            and info.get("forbidden_jargon") == 0
            and int(info.get("tikz_figures", 0)) >= 2
        )
        if not checks_ok:
            raise RuntimeError(f"GATE BLOCKED: {pid} failed typographic or TikZ verification gate: {info}")

        live_sha, live_md5 = file_hashes(pdf_path)
        if live_sha != info.get("pdf_sha256"):
            raise RuntimeError(
                f"GATE BLOCKED: Live SHA-256 mismatch for {pid}: live={live_sha} receipt={info.get('pdf_sha256')}"
            )

        verified_files.append(
            {
                "id": pid,
                "src": pdf_path,
                "filename": pdf_path.name,
                "pages": info["pages"],
                "tikz_figures": info["tikz_figures"],
                "sha256": live_sha,
                "md5": live_md5,
                "size_bytes": pdf_path.stat().st_size,
            }
        )

    bundle_info = receipt.get("release_bundle", {})
    bundle_path = REPO_ROOT / bundle_info.get("bundle_path", "")
    if not bundle_path.exists():
        raise RuntimeError(f"GATE BLOCKED: Missing release bundle: {bundle_path}")
    bundle_sha, bundle_md5 = file_hashes(bundle_path)
    if bundle_sha != bundle_info.get("sha256"):
        raise RuntimeError(
            f"GATE BLOCKED: Release bundle SHA-256 mismatch: live={bundle_sha} receipt={bundle_info.get('sha256')}"
        )
    verified_files.append(
        {
            "id": "ReleaseBundle",
            "src": bundle_path,
            "filename": bundle_path.name,
            "sha256": bundle_sha,
            "md5": bundle_md5,
            "size_bytes": bundle_path.stat().st_size,
        }
    )

    for rec_id, rec_path in (
        ("VerificationReceipt", RECEIPT_PATH),
        ("MillenniumExtReceipt", EXT_RECEIPT_PATH),
    ):
        rec_sha, rec_md5 = file_hashes(rec_path)
        verified_files.append(
            {
                "id": rec_id,
                "src": rec_path,
                "filename": rec_path.name,
                "sha256": rec_sha,
                "md5": rec_md5,
                "size_bytes": rec_path.stat().st_size,
            }
        )

    if DEPOSIT_DIR.exists():
        shutil.rmtree(DEPOSIT_DIR)
    DEPOSIT_DIR.mkdir(parents=True, exist_ok=True)

    staged_manifest: List[Dict[str, Any]] = []
    for item in verified_files:
        dst = DEPOSIT_DIR / item["filename"]
        shutil.copy2(item["src"], dst)
        for blocked in BLOCKED_LEGACY_PATTERNS:
            if blocked in dst.name:
                raise RuntimeError(f"GATE BLOCKED: Legacy PDF found in deposit dir: {dst.name}")
        staged_manifest.append(
            {
                "id": item["id"],
                "filename": item["filename"],
                "size_bytes": item["size_bytes"],
                "sha256": item["sha256"],
                "md5": item["md5"],
            }
        )

    meta_payload = build_zenodo_metadata(total_theorems)
    meta_path = DEPOSIT_DIR / "zenodo_metadata.json"
    meta_path.write_text(json.dumps(meta_payload, indent=2), encoding="utf-8")

    return {
        "verified_files": verified_files,
        "staged_manifest": staged_manifest,
        "metadata_payload": meta_payload,
        "total_theorems": total_theorems,
        "deposit_dir": str(DEPOSIT_DIR.relative_to(REPO_ROOT)).replace("\\", "/"),
    }


def _zenodo_json(url: str, token: str, method: str = "GET", payload: Dict[str, Any] | None = None) -> Dict[str, Any]:
    import time

    headers = {"Authorization": f"Bearer {token}"}
    data = None
    if payload is not None:
        headers["Content-Type"] = "application/json"
        data = json.dumps(payload).encode("utf-8")
    for attempt in range(4):
        req = urllib.request.Request(url, data=data, headers=headers, method=method)
        try:
            with urllib.request.urlopen(req, timeout=150) as resp:
                raw = resp.read().decode("utf-8")
                return json.loads(raw) if raw.strip() else {}
        except urllib.error.HTTPError as exc:
            if exc.code in (429, 500, 502, 503, 504) and attempt < 3:
                time.sleep(3 * (attempt + 1))
                continue
            raise
        except (TimeoutError, OSError):
            if attempt < 3:
                time.sleep(3 * (attempt + 1))
                continue
            raise
    raise RuntimeError(f"Zenodo API request failed after retries: {method} {url}")


def upload_to_zenodo(
    token: str, api_base: str, staged: Dict[str, Any], parent_dep_id: int | None = None
) -> Dict[str, Any]:
    if parent_dep_id is not None:
        parent_dep = _zenodo_json(f"{api_base}/deposit/depositions/{parent_dep_id}", token)
        remote_md5s = {
            f.get("filename"): str(f.get("checksum", "")).replace("md5:", "")
            for f in parent_dep.get("files", [])
        }
        all_match = (
            parent_dep.get("state") == "done"
            and len(remote_md5s) == len(staged["verified_files"])
            and all(remote_md5s.get(item["filename"]) == item["md5"] for item in staged["verified_files"])
        )
        if all_match:
            dep_id = int(parent_dep["id"])
            return {
                "status": "PUBLISHED",
                "state": "done",
                "deposition_id": dep_id,
                "parent_deposition_id": parent_dep_id,
                "concept_doi": str(parent_dep.get("conceptdoi") or ""),
                "doi": str(parent_dep.get("doi") or f"10.5281/zenodo.{dep_id}"),
                "html_url": f"https://zenodo.org/deposit/{dep_id}",
                "record_url": f"https://zenodo.org/records/{dep_id}",
                "latest_url": f"https://zenodo.org/records/{parent_dep_id}/latest",
                "prereserved_doi": f"10.5281/zenodo.{dep_id}",
                "uploaded_files": [
                    {
                        "filename": item["filename"],
                        "size_bytes": item["size_bytes"],
                        "local_sha256": item["sha256"],
                        "local_md5": item["md5"],
                        "remote_checksum": f"md5:{item['md5']}",
                    }
                    for item in staged["verified_files"]
                ],
            }

        dep = None
        latest_draft_url = parent_dep.get("links", {}).get("latest_draft", "")
        if latest_draft_url:
            cand = _zenodo_json(latest_draft_url, token)
            if cand.get("state") == "unsubmitted":
                dep = cand
        if dep is None:
            # Check recent unsubmitted drafts sharing the same conceptrecid
            concept_id = str(parent_dep.get("conceptrecid") or "")
            recent = _zenodo_json(f"{api_base}/deposit/depositions?size=20", token)
            if isinstance(recent, list):
                for item in recent:
                    if item.get("state") == "unsubmitted" and str(item.get("conceptrecid") or "") == concept_id:
                        dep = item
                        break
        if dep is None:
            nv = _zenodo_json(
                f"{api_base}/deposit/depositions/{parent_dep_id}/actions/newversion",
                token,
                method="POST",
            )
            dep = _zenodo_json(nv["links"]["latest_draft"], token)

        dep_id = int(dep["id"])
        wanted_md5s = {item["filename"]: item["md5"] for item in staged["verified_files"]}
        already_matched: Dict[str, str] = {}
        for existing_f in dep.get("files", []):
            fname = str(existing_f.get("filename") or "")
            chk = str(existing_f.get("checksum") or "").replace("md5:", "")
            if fname in wanted_md5s and chk == wanted_md5s[fname]:
                already_matched[fname] = f"md5:{chk}"
                continue
            fid = existing_f.get("id")
            if fid:
                _zenodo_json(
                    f"{api_base}/deposit/depositions/{dep_id}/files/{fid}",
                    token,
                    method="DELETE",
                )
        dep = _zenodo_json(
            f"{api_base}/deposit/depositions/{dep_id}",
            token,
            method="PUT",
            payload=staged["metadata_payload"],
        )
    else:
        dep = _zenodo_json(
            f"{api_base}/deposit/depositions",
            token,
            method="POST",
            payload=staged["metadata_payload"],
        )
        dep_id = int(dep["id"])
        already_matched = {}

    bucket_url = dep["links"]["bucket"]
    uploaded: List[Dict[str, Any]] = []

    import time as _time
    for item in staged["verified_files"]:
        if item["filename"] in already_matched:
            uploaded.append(
                {
                    "filename": item["filename"],
                    "size_bytes": item["size_bytes"],
                    "local_sha256": item["sha256"],
                    "local_md5": item["md5"],
                    "remote_checksum": already_matched[item["filename"]],
                }
            )
            continue
        fpath = DEPOSIT_DIR / item["filename"]
        data = fpath.read_bytes()
        put_info: Dict[str, Any] | None = None
        for attempt in range(4):
            put_req = urllib.request.Request(
                f"{bucket_url}/{item['filename']}",
                data=data,
                headers={"Authorization": f"Bearer {token}", "Content-Type": "application/octet-stream"},
                method="PUT",
            )
            try:
                with urllib.request.urlopen(put_req, timeout=180) as put_resp:
                    put_info = json.loads(put_resp.read().decode("utf-8"))
                break
            except urllib.error.HTTPError as exc:
                if exc.code in (429, 500, 502, 503, 504) and attempt < 3:
                    _time.sleep(4 * (attempt + 1))
                    continue
                raise
            except (TimeoutError, OSError):
                if attempt < 3:
                    _time.sleep(4 * (attempt + 1))
                    continue
                raise
        assert put_info is not None
        remote_chk = put_info.get("checksum", "")
        expected_chk = f"md5:{item['md5']}"
        if remote_chk != expected_chk:
            raise RuntimeError(
                f"Remote MD5 mismatch for {item['filename']}: remote={remote_chk} local={expected_chk}"
            )
        uploaded.append(
            {
                "filename": item["filename"],
                "size_bytes": item["size_bytes"],
                "local_sha256": item["sha256"],
                "local_md5": item["md5"],
                "remote_checksum": remote_chk,
            }
        )

    pub = _zenodo_json(
        f"{api_base}/deposit/depositions/{dep_id}/actions/publish",
        token,
        method="POST",
    )
    pub_doi = str(pub.get("doi") or dep.get("metadata", {}).get("prereserve_doi", {}).get("doi", ""))
    concept_doi = str(pub.get("conceptdoi") or dep.get("conceptdoi") or "")
    rec_url = f"https://zenodo.org/records/{dep_id}"
    return {
        "status": "PUBLISHED",
        "state": str(pub.get("state") or "done"),
        "deposition_id": dep_id,
        "parent_deposition_id": parent_dep_id or dep_id,
        "concept_doi": concept_doi,
        "doi": pub_doi,
        "html_url": f"https://zenodo.org/deposit/{dep_id}",
        "record_url": rec_url,
        "latest_url": f"https://zenodo.org/records/{parent_dep_id or dep_id}/latest",
        "prereserved_doi": pub_doi,
        "uploaded_files": uploaded,
    }


def main() -> int:
    staged = verify_and_stage()
    token, api_base, env_name = resolve_zenodo_token()

    if token:
        parent_id: int | None = 24329780
        if UPLOAD_RECEIPT_PATH.exists():
            try:
                prev = json.loads(UPLOAD_RECEIPT_PATH.read_text(encoding="utf-8"))
                if prev.get("deposition_id"):
                    parent_id = int(prev["deposition_id"])
            except Exception:
                parent_id = 24329780
        upload_res = upload_to_zenodo(token, api_base, staged, parent_dep_id=parent_id)
        out: Dict[str, Any] = {
            "gate_passed": True,
            "api_base": api_base,
            "token_source": env_name,
            "total_verified_theorems": staged["total_theorems"],
            "deposit_dir": staged["deposit_dir"],
            "staged_manifest": staged["staged_manifest"],
            **upload_res,
        }
        UPLOAD_RECEIPT_PATH.write_text(json.dumps(out, indent=2), encoding="utf-8")
        print(f"ZENODO_GATE_PASSED=True FILES_STAGED={len(staged['staged_manifest'])}")
        print(f"ZENODO_UPLOAD_STATUS={upload_res['status']} STATE={upload_res['state']} DEPOSITION_ID={upload_res['deposition_id']}")
        print(f"ZENODO_DOI={upload_res['doi']} CONCEPT_DOI={upload_res['concept_doi']} RECORD_URL={upload_res['record_url']} LATEST_URL={upload_res['latest_url']}")
        return 0

    ps_cmd = '$env:ZENODO_TOKEN="<YOUR_ZENODO_TOKEN>"; python scripts/automate_verified_zenodo_upload.py'
    out = {
        "gate_passed": True,
        "status": "STAGED_AWAITING_TOKEN",
        "total_verified_theorems": staged["total_theorems"],
        "deposit_dir": staged["deposit_dir"],
        "blocked_legacy_patterns": list(BLOCKED_LEGACY_PATTERNS),
        "staged_manifest": staged["staged_manifest"],
        "upload_file_count": len(staged["staged_manifest"]),
        "powershell_upload_command": ps_cmd,
    }
    UPLOAD_RECEIPT_PATH.write_text(json.dumps(out, indent=2), encoding="utf-8")

    print(f"ZENODO_GATE_PASSED=True DEPOSIT_DIR={staged['deposit_dir']} FILES={len(staged['staged_manifest'])}")
    for item in staged["staged_manifest"]:
        print(f"  STAGED {item['filename']} bytes={item['size_bytes']} sha256={item['sha256']} md5={item['md5']}")
    print("ZENODO_UPLOAD_STATUS=STAGED_AWAITING_TOKEN (set ZENODO_TOKEN, ZENODO_API_TOKEN, or ZENODO_SANDBOX_TOKEN to upload)")
    print(f"POWERSHELL_UPLOAD_COMMAND: {ps_cmd}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
