"""Integrity tooling: sealing, manifests, forbidden-pattern scans, report-vs-data consistency.
Each function exists because of a concrete failure in the RH project (see docs/02 failure table)."""
from __future__ import annotations
import csv, hashlib, json, os, re
from datetime import datetime, timezone


def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def seal(results_path: str, script_path: str | None = None) -> dict:
    """Blind-result seal: hash results (+ script) BEFORE anyone compares to the primary run."""
    d = {"sealed_file": os.path.basename(results_path), "sha256": sha256_file(results_path),
         "sealed_at_utc": datetime.now(timezone.utc).isoformat(), "status": "SEALED"}
    if script_path:
        d["script_sha256"] = sha256_file(script_path)
    with open(results_path + ".seal.json", "w", encoding="utf-8") as f:
        json.dump(d, f, indent=2)
    return d


def verify_seal(results_path: str) -> bool:
    with open(results_path + ".seal.json", encoding="utf-8") as f:
        return json.load(f)["sha256"] == sha256_file(results_path)


def build_manifest(root: str, out: str = "ARTIFACT_HASH_MANIFEST.sha256"):
    lines = []
    exclude_dirs = {".git", ".pytest_cache", "__pycache__", ".lake", "build"}
    for dp, dirs, fs in os.walk(root):
        dirs[:] = sorted(d for d in dirs if d not in exclude_dirs)
        for fn in sorted(fs):
            if fn.endswith(".bundle") or fn.endswith(".pyc"):
                continue
            p = os.path.join(dp, fn)
            if os.path.abspath(p) == os.path.abspath(os.path.join(root, out)):
                continue
            lines.append(f"{sha256_file(p)}  {os.path.relpath(p, root).replace(os.sep, '/')}")
    with open(os.path.join(root, out), "w", encoding="utf-8") as f:
        f.write("\n".join(sorted(lines, key=lambda l: l.split('  ', 1)[1])) + "\n")
    return len(lines)


def verify_manifest(root: str, manifest: str = "ARTIFACT_HASH_MANIFEST.sha256") -> list:
    bad = []
    for line in open(os.path.join(root, manifest), encoding="utf-8"):
        if not line.strip():
            continue
        h, rel = line.rstrip("\n").split("  ", 1)
        p = os.path.join(root, rel)
        if not os.path.exists(p) or sha256_file(p) != h:
            bad.append(rel)
    return bad


# ---- forbidden-construct scan (RH-T056R8: float64 corrupted 1e-16 resolution) -------------
DEFAULT_FORBIDDEN = [r"\bnumpy\.float64\b", r"\bscipy\.linalg\b", r"\bnp\.linalg\b", r"\bfloat\(", r"import\s+scipy"]


def scan_forbidden(path: str, patterns=None) -> list:
    pats = patterns or DEFAULT_FORBIDDEN
    hits = []
    for i, line in enumerate(open(path, encoding="utf-8", errors="replace"), 1):
        code = line.split("#", 1)[0]
        for p in pats:
            if re.search(p, code):
                hits.append((i, p, line.strip()))
    return hits


# ---- synthetic / duplicated data detector (RH-T056, T056R) ------------------------------
def find_duplicate_rows(csv_path: str, ignore_cols=("cell_id", "id")) -> list:
    seen, dups = {}, []
    with open(csv_path, newline="", encoding="utf-8") as f:
        for n, row in enumerate(csv.DictReader(f), 2):
            key = tuple(v for k, v in sorted(row.items()) if k not in ignore_cols)
            if key in seen:
                dups.append((seen[key], n))
            else:
                seen[key] = n
    return dups


def check_power_law_fabrication(values, ns, tol=1e-12) -> bool:
    """True if values are an EXACT c*N^-p curve (likely generated, not computed). Real eigenvalues never fit to 1e-12."""
    import math
    if len(values) < 3:
        return False
    xs = [math.log(n) for n in ns]; ys = [math.log(abs(v)) for v in values]
    mx, my = sum(xs) / len(xs), sum(ys) / len(ys)
    sl = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sum((x - mx) ** 2 for x in xs)
    res = max(abs(y - (my + sl * (x - mx))) for x, y in zip(xs, ys))
    return res < tol


# ---- report vs CSV contradiction gate (RH-T056R6) ---------------------------------------
def report_vs_csv(report_text: str, csv_path: str, flag_col: str, claim_regex: str, expected_value: str) -> list:
    """If report matches `claim_regex` (a success claim) but CSV rows contradict (flag_col != expected) -> issue."""
    issues = []
    if re.search(claim_regex, report_text, re.I):
        with open(csv_path, newline="", encoding="utf-8") as f:
            for n, row in enumerate(csv.DictReader(f), 2):
                if row.get(flag_col) != expected_value:
                    issues.append(f"REPORT_CSV_CONTRADICTION row {n}: {flag_col}={row.get(flag_col)!r}")
    return issues


BANNED_PHRASES = ["conclusively proven", "rh solved", "unconditionally verified proof", "certified absolute truth"]


def banned_language(text: str, extra=()):
    t = text.lower()
    return [p for p in list(BANNED_PHRASES) + list(extra) if p in t]


def wilson_interval(k: int, n: int, z: float = 1.96):
    """Required whenever you say 'X of N trials' - never report a bare 100%."""
    if n == 0:
        return (0.0, 1.0)
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * ((p * (1 - p) / n + z * z / (4 * n * n)) ** 0.5) / d
    return (max(0.0, c - h), min(1.0, c + h))
