#!/usr/bin/env python
"""
Clean-room E4 independent verifier for Protocol RH-T056R8R3.
Implemented from the mathematical contract ONLY.
Author: E4 verifier agent (clean-room, no access to primary scripts or results)
"""

import json
import hashlib
import time
import csv
import os
import sys

import mpmath as mp
from connes_cvs import build_galerkin_matrix

# ============================================================
# Utility: SHA256 hash of a file
# ============================================================
def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


# ============================================================
# Even-parity projection (from contract §Even Unitary Projection)
# ============================================================
def even_projection(Q_full, M):
    """
    Project the (2M+1)x(2M+1) matrix Q_full onto the even-parity subspace.
    Returns Q_even of dimension (M+1)x(M+1).
    
    Basis:
      e_0 = |0>  (index M in full matrix)
      e_k = (|k> + |-k>) / sqrt(2)  for k=1..M
    
    Even-projected matrix entries:
      Q_even[0,0] = Q_full[M, M]
      Q_even[0,k] = (Q_full[M, M+k] + Q_full[M, M-k]) / sqrt(2)   for k>=1
      Q_even[j,k] = (Q_full[M+j, M+k] + Q_full[M+j, M-k]
                    + Q_full[M-j, M+k] + Q_full[M-j, M-k]) / 2    for j,k>=1
    Then symmetrize.
    """
    dim = M + 1
    sqrt2 = mp.sqrt(2)
    Q_even = mp.matrix(dim, dim)

    # (0,0)
    Q_even[0, 0] = Q_full[M, M]

    # (0, k) and (k, 0) for k >= 1
    for k in range(1, dim):
        val = (Q_full[M, M + k] + Q_full[M, M - k]) / sqrt2
        Q_even[0, k] = val
        Q_even[k, 0] = val  # will be symmetrized anyway

    # (j, k) for j,k >= 1
    for j in range(1, dim):
        for k in range(1, dim):
            Q_even[j, k] = (Q_full[M + j, M + k] + Q_full[M + j, M - k]
                          + Q_full[M - j, M + k] + Q_full[M - j, M - k]) / 2

    # Symmetrize
    for i in range(dim):
        for j in range(i + 1, dim):
            avg = (Q_even[i, j] + Q_even[j, i]) / 2
            Q_even[i, j] = avg
            Q_even[j, i] = avg

    return Q_even


# ============================================================
# Space A1: V_{n+1}^even — Fourier extension
# (contract §Space A1)
# ============================================================
def compute_lambda_A1(Q_even, n):
    """
    A1 subspace: top-left (n+2)x(n+2) block of Q_even.
    Returns (lambda_A1, all_eigenvalues_sorted).
    """
    dim_A1 = n + 2
    Q_A1 = mp.matrix(dim_A1, dim_A1)
    for i in range(dim_A1):
        for j in range(dim_A1):
            Q_A1[i, j] = Q_even[i, j]

    eigenvalues = mp.eigsy(Q_A1, eigvals_only=True)
    eigenvalues_sorted = sorted(eigenvalues, key=lambda x: mp.re(x))
    lambda_A1 = eigenvalues_sorted[0]
    return lambda_A1, eigenvalues_sorted


# ============================================================
# Space B: V_n^even + span{v_perp}  (t^2 augmentation)
# (contract §Space B)
# ============================================================
def compute_lambda_B(Q_even, n, M):
    """
    B subspace of dimension (n+2).
    
    t^2 boundary profile vector in even basis:
      a_k = (-1)^k * sqrt(2) / k^2   for k=1..M
      a_0 = 0
    
    Project out V_n^even (zero components 0..n):
      a_perp[k] = 0 for k=0..n
      a_perp[k] = a_k for k=n+1..M
    
    Normalize: v_perp = a_perp / ||a_perp||
    
    Assemble Q_B of dimension (n+2)x(n+2):
      Q_B[i,j] = Q_even[i,j]  for i,j in {0..n}
      Q_B[i, n+1] = sum_{k=n+1}^{M} Q_even[i,k] * v_perp[k]   for i in {0..n}
      Q_B[n+1, i] = Q_B[i, n+1]   (symmetry)
      Q_B[n+1, n+1] = sum_{j,k=n+1}^{M} v_perp[j] * Q_even[j,k] * v_perp[k]
    """
    sqrt2 = mp.sqrt(2)

    # Build a_perp (length M+1, indexed 0..M)
    a_perp = [mp.mpf(0)] * (M + 1)
    for k in range(n + 1, M + 1):
        a_perp[k] = ((-1) ** k) * sqrt2 / mp.mpf(k ** 2)

    # Normalize
    norm_sq = mp.mpf(0)
    for k in range(M + 1):
        norm_sq += a_perp[k] ** 2
    norm = mp.sqrt(norm_sq)

    v_perp = [a_perp[k] / norm for k in range(M + 1)]

    # Assemble Q_B
    dim_B = n + 2
    Q_B = mp.matrix(dim_B, dim_B)

    # Top-left (n+1)x(n+1) block
    for i in range(n + 1):
        for j in range(n + 1):
            Q_B[i, j] = Q_even[i, j]

    # Cross-terms: Q_B[i, n+1] for i in {0..n}
    for i in range(n + 1):
        val = mp.mpf(0)
        for k in range(n + 1, M + 1):
            val += Q_even[i, k] * v_perp[k]
        Q_B[i, dim_B - 1] = val
        Q_B[dim_B - 1, i] = val  # symmetry

    # Self-energy: Q_B[n+1, n+1]
    val = mp.mpf(0)
    for j in range(n + 1, M + 1):
        for k in range(n + 1, M + 1):
            val += v_perp[j] * Q_even[j, k] * v_perp[k]
    Q_B[dim_B - 1, dim_B - 1] = val

    eigenvalues = mp.eigsy(Q_B, eigvals_only=True)
    eigenvalues_sorted = sorted(eigenvalues, key=lambda x: mp.re(x))
    lambda_B = eigenvalues_sorted[0]
    return lambda_B, eigenvalues_sorted, v_perp


# ============================================================
# Gate A: Authentication Fixture
# c=13, N=80, T=400, dps in {80, 120, 160}
# ============================================================
def run_gate_a():
    print("=" * 70, flush=True)
    print("GATE A: Authentication Fixture", flush=True)
    print("c=13, N=80, T=400", flush=True)
    print("=" * 70, flush=True)

    expected_str = "2.5282661401965756026859551460395357984852932822457493202998634125895744410943922e-59"

    results = {}
    for dps_val in [80, 120, 160]:
        print(f"\n  Gate A: dps={dps_val} ...", flush=True)
        t0 = time.time()
        mp.mp.dps = dps_val

        expected = mp.mpf(expected_str)

        Q_full = build_galerkin_matrix(c=13, N=80, T=400, dps=dps_val)
        elapsed_build = time.time() - t0
        print(f"    Matrix built in {elapsed_build:.1f}s, dim={Q_full.rows}x{Q_full.cols}", flush=True)

        t1 = time.time()
        eigs = mp.eigsy(Q_full, eigvals_only=True)
        elapsed_eig = time.time() - t1
        eigs_sorted = sorted(eigs, key=lambda x: mp.re(x))
        lambda_min = eigs_sorted[0]

        rel_err = abs((lambda_min - expected) / expected)

        passed = rel_err < mp.mpf("1e-15")

        print(f"    lambda_min = {mp.nstr(lambda_min, 40)}", flush=True)
        print(f"    expected   = {mp.nstr(expected, 40)}", flush=True)
        print(f"    rel_error  = {mp.nstr(rel_err, 10)}", flush=True)
        print(f"    PASS: {passed}", flush=True)
        print(f"    Eigsolve in {elapsed_eig:.1f}s", flush=True)

        results[str(dps_val)] = {
            "lambda_min": mp.nstr(lambda_min, 60),
            "expected": expected_str,
            "rel_error": mp.nstr(rel_err, 15),
            "pass": passed,
            "build_time_s": round(elapsed_build, 1),
            "eigsolve_time_s": round(elapsed_eig, 1),
        }

    all_pass = all(r["pass"] for r in results.values())
    print(f"\n  Gate A overall: {'PASS' if all_pass else 'FAIL'}", flush=True)
    return results, all_pass


# ============================================================
# Gate B: Predecessor Calibration
# c=13, n=10, M=20, T=400, dps=80
# ============================================================
def run_gate_b():
    print("\n" + "=" * 70, flush=True)
    print("GATE B: Predecessor Calibration", flush=True)
    print("c=13, n=10, M=20, T=400, dps=80", flush=True)
    print("=" * 70, flush=True)

    mp.mp.dps = 80
    c, n, M, T = 13, 10, 20, 400

    t0 = time.time()
    Q_full = build_galerkin_matrix(c=c, N=M, T=T, dps=80)
    print(f"  Matrix built in {time.time() - t0:.1f}s, dim={Q_full.rows}x{Q_full.cols}", flush=True)

    Q_even = even_projection(Q_full, M)
    print(f"  Even projection done, dim={Q_even.rows}x{Q_even.cols}", flush=True)

    lambda_A1, eigs_A1 = compute_lambda_A1(Q_even, n)
    print(f"  lambda_A1 = {mp.nstr(lambda_A1, 30)}", flush=True)

    lambda_B, eigs_B, v_perp = compute_lambda_B(Q_even, n, M)
    print(f"  lambda_B  = {mp.nstr(lambda_B, 30)}", flush=True)

    R_B = lambda_B / lambda_A1
    classification = "FOURIER_EXTENSION_LOWER" if R_B > 1 else "T2_EXTENSION_LOWER"

    print(f"  R_B       = {mp.nstr(R_B, 15)}", flush=True)
    print(f"  Classification: {classification}", flush=True)

    passed = R_B > 1
    print(f"  Gate B: {'PASS' if passed else 'FAIL'} (R_B > 1 expected)", flush=True)

    result = {
        "lambda_A1": mp.nstr(lambda_A1, 50),
        "lambda_B": mp.nstr(lambda_B, 50),
        "R_B": mp.nstr(R_B, 20),
        "classification": classification,
        "pass": passed,
    }
    return result, passed


# ============================================================
# Primary 20-cell grid
# ============================================================
PRIMARY_CELLS = [
    {"cell_id": "R8R3-P01", "c": 9,  "n": 6,  "M": 20, "T": 400},
    {"cell_id": "R8R3-P02", "c": 9,  "n": 8,  "M": 20, "T": 400},
    {"cell_id": "R8R3-P03", "c": 9,  "n": 10, "M": 20, "T": 400},
    {"cell_id": "R8R3-P04", "c": 9,  "n": 12, "M": 24, "T": 400},
    {"cell_id": "R8R3-P05", "c": 11, "n": 6,  "M": 20, "T": 400},
    {"cell_id": "R8R3-P06", "c": 11, "n": 8,  "M": 20, "T": 400},
    {"cell_id": "R8R3-P07", "c": 11, "n": 10, "M": 20, "T": 400},
    {"cell_id": "R8R3-P08", "c": 11, "n": 12, "M": 24, "T": 400},
    {"cell_id": "R8R3-P09", "c": 13, "n": 6,  "M": 20, "T": 400},
    {"cell_id": "R8R3-P10", "c": 13, "n": 8,  "M": 20, "T": 400},
    {"cell_id": "R8R3-P11", "c": 13, "n": 10, "M": 20, "T": 400},
    {"cell_id": "R8R3-P12", "c": 13, "n": 12, "M": 24, "T": 400},
    {"cell_id": "R8R3-P13", "c": 15, "n": 6,  "M": 20, "T": 400},
    {"cell_id": "R8R3-P14", "c": 15, "n": 8,  "M": 20, "T": 400},
    {"cell_id": "R8R3-P15", "c": 15, "n": 10, "M": 20, "T": 400},
    {"cell_id": "R8R3-P16", "c": 15, "n": 12, "M": 24, "T": 400},
    {"cell_id": "R8R3-P17", "c": 17, "n": 6,  "M": 20, "T": 400},
    {"cell_id": "R8R3-P18", "c": 17, "n": 8,  "M": 20, "T": 400},
    {"cell_id": "R8R3-P19", "c": 17, "n": 10, "M": 20, "T": 400},
    {"cell_id": "R8R3-P20", "c": 17, "n": 12, "M": 24, "T": 400},
]


def run_primary_cell(cell):
    cell_id = cell["cell_id"]
    c = cell["c"]
    n = cell["n"]
    M = cell["M"]
    T = cell["T"]
    dps_val = 80

    print(f"\n  --- Cell {cell_id}: c={c}, n={n}, M={M}, T={T}, dps={dps_val} ---", flush=True)
    mp.mp.dps = dps_val

    t0 = time.time()
    Q_full = build_galerkin_matrix(c=c, N=M, T=T, dps=dps_val)
    elapsed_build = time.time() - t0
    print(f"    Matrix built in {elapsed_build:.1f}s, dim={Q_full.rows}x{Q_full.cols}", flush=True)

    Q_even = even_projection(Q_full, M)
    print(f"    Even projection done, dim={Q_even.rows}x{Q_even.cols}", flush=True)

    lambda_A1, eigs_A1 = compute_lambda_A1(Q_even, n)
    print(f"    lambda_A1 = {mp.nstr(lambda_A1, 30)}", flush=True)

    lambda_B, eigs_B, v_perp = compute_lambda_B(Q_even, n, M)
    print(f"    lambda_B  = {mp.nstr(lambda_B, 30)}", flush=True)

    R_B = lambda_B / lambda_A1
    classification = "FOURIER_EXTENSION_LOWER" if R_B > 1 else "T2_EXTENSION_LOWER"

    print(f"    R_B       = {mp.nstr(R_B, 15)}", flush=True)
    print(f"    Classification: {classification}", flush=True)

    return {
        "cell_id": cell_id,
        "c": c,
        "n": n,
        "M": M,
        "T": T,
        "dps": dps_val,
        "lambda_A1": mp.nstr(lambda_A1, 50),
        "lambda_B": mp.nstr(lambda_B, 50),
        "R_B": mp.nstr(R_B, 20),
        "classification": classification,
        "build_time_s": round(elapsed_build, 1),
    }


def run_primary_grid():
    print("\n" + "=" * 70, flush=True)
    print("PRIMARY 20-CELL GRID", flush=True)
    print("=" * 70, flush=True)

    results = []
    for i, cell in enumerate(PRIMARY_CELLS):
        print(f"\n  Cell {i+1}/20", flush=True)
        result = run_primary_cell(cell)
        results.append(result)
    return results


# ============================================================
# Compare against candidate CSV (ONLY after sealing own results)
# ============================================================
def compare_with_candidate(own_results, csv_path):
    print("\n" + "=" * 70, flush=True)
    print("COMPARISON WITH CANDIDATE CSV", flush=True)
    print(f"  Loading: {csv_path}", flush=True)
    print("=" * 70, flush=True)

    mp.mp.dps = 80

    # Read candidate CSV
    candidate = {}
    with open(csv_path, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            candidate[row["cell_id"]] = row

    comparisons = []
    for own in own_results:
        cell_id = own["cell_id"]
        if cell_id not in candidate:
            print(f"  WARNING: {cell_id} not found in candidate CSV", flush=True)
            comparisons.append({
                "cell_id": cell_id,
                "status": "MISSING_IN_CANDIDATE",
            })
            continue

        cand = candidate[cell_id]

        # Compare lambda_A1
        own_A1 = mp.mpf(own["lambda_A1"])
        cand_A1 = mp.mpf(cand.get("lambda_A1", "0"))

        if cand_A1 != 0:
            disc_A1 = abs((own_A1 - cand_A1) / cand_A1)
        else:
            disc_A1 = abs(own_A1 - cand_A1)

        # Compare lambda_B
        own_B = mp.mpf(own["lambda_B"])
        cand_B = mp.mpf(cand.get("lambda_B", "0"))

        if cand_B != 0:
            disc_B = abs((own_B - cand_B) / cand_B)
        else:
            disc_B = abs(own_B - cand_B)

        # Compare R_B
        own_R = mp.mpf(own["R_B"])
        cand_R = mp.mpf(cand.get("R_B", "0"))

        if cand_R != 0:
            disc_R = abs((own_R - cand_R) / cand_R)
        else:
            disc_R = abs(own_R - cand_R)

        # Compare classification
        own_class = own["classification"]
        cand_class = cand.get("classification", "")
        class_match = own_class == cand_class

        print(f"  {cell_id}: disc_A1={mp.nstr(disc_A1, 5)}, disc_B={mp.nstr(disc_B, 5)}, "
              f"disc_R={mp.nstr(disc_R, 5)}, class_match={class_match}", flush=True)

        comparisons.append({
            "cell_id": cell_id,
            "own_lambda_A1": own["lambda_A1"],
            "cand_lambda_A1": cand.get("lambda_A1", ""),
            "disc_lambda_A1": mp.nstr(disc_A1, 15),
            "own_lambda_B": own["lambda_B"],
            "cand_lambda_B": cand.get("lambda_B", ""),
            "disc_lambda_B": mp.nstr(disc_B, 15),
            "own_R_B": own["R_B"],
            "cand_R_B": cand.get("R_B", ""),
            "disc_R_B": mp.nstr(disc_R, 15),
            "own_classification": own_class,
            "cand_classification": cand_class,
            "classification_match": class_match,
            "status": "COMPARED",
        })

    return comparisons


# ============================================================
# MAIN
# ============================================================
def main():
    print("=" * 70, flush=True)
    print("RH-T056R8R3 CLEAN-ROOM E4 INDEPENDENT VERIFIER", flush=True)
    print(f"Start time: {time.strftime('%Y-%m-%dT%H:%M:%S')}", flush=True)
    print("=" * 70, flush=True)

    workspace = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # ---- Gate A ----
    gate_a_results, gate_a_pass = run_gate_a()

    # ---- Gate B ----
    gate_b_result, gate_b_pass = run_gate_b()

    if not gate_a_pass:
        print("\n*** GATE A FAILED — aborting. ***", flush=True)
        sys.exit(1)

    if not gate_b_pass:
        print("\n*** GATE B FAILED — aborting. ***", flush=True)
        sys.exit(1)

    # ---- Primary Grid ----
    primary_results = run_primary_grid()

    # ---- Seal results ----
    print("\n" + "=" * 70, flush=True)
    print("SEALING RESULTS", flush=True)
    print("=" * 70, flush=True)

    sealed_data = {
        "protocol_id": "RH-T056R8R3",
        "verifier": "cleanroom_e4",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "gate_a": gate_a_results,
        "gate_a_pass": gate_a_pass,
        "gate_b": gate_b_result,
        "gate_b_pass": gate_b_pass,
        "primary_cells": primary_results,
    }

    results_path = os.path.join(workspace, "RH-T056R8R3_CLEANROOM_E4_RESULTS.json")
    with open(results_path, "w") as f:
        json.dump(sealed_data, f, indent=2)

    results_hash = sha256_file(results_path)
    print(f"  Results file: {results_path}", flush=True)
    print(f"  Results SHA256: {results_hash}", flush=True)

    # ---- NOW compare against candidate ----
    csv_path = os.path.join(workspace, "RH-T056R8R3_PRIMARY_RESULTS.csv")
    if os.path.exists(csv_path):
        comparisons = compare_with_candidate(primary_results, csv_path)

        comparison_data = {
            "protocol_id": "RH-T056R8R3",
            "verifier": "cleanroom_e4",
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "sealed_results_sha256": results_hash,
            "comparisons": comparisons,
        }

        comparison_path = os.path.join(workspace, "RH-T056R8R3_CLEANROOM_E4_COMPARISON.json")
        with open(comparison_path, "w") as f:
            json.dump(comparison_data, f, indent=2)

        comparison_hash = sha256_file(comparison_path)
        print(f"\n  Comparison file: {comparison_path}", flush=True)
        print(f"  Comparison SHA256: {comparison_hash}", flush=True)

        # Summary
        all_match = all(c.get("classification_match", False) for c in comparisons if c.get("status") == "COMPARED")
        max_disc_R = max(
            (mp.mpf(c["disc_R_B"]) for c in comparisons if c.get("status") == "COMPARED"),
            default=mp.mpf(0)
        )
        print(f"\n  All classifications match: {all_match}", flush=True)
        print(f"  Max discrepancy in R_B: {mp.nstr(max_disc_R, 10)}", flush=True)
    else:
        print(f"\n  WARNING: Candidate CSV not found at {csv_path}", flush=True)
        print("  Skipping comparison step.", flush=True)

    print(f"\n  End time: {time.strftime('%Y-%m-%dT%H:%M:%S')}", flush=True)
    print("CLEAN-ROOM E4 VERIFICATION COMPLETE", flush=True)


if __name__ == "__main__":
    main()
