"""
Clean-Room E4 Independent Verification Script for Protocol RH-T056R8R3
Governing Standard: MASTER_AUTONOMOUS_PROJECT_GOVERNANCE_DEVELOPMENT_EVOLUTION_v2.5.md / Governance v2.9.4
Author: Clean-Room Independent Scientific Verifier (Clean-Room E4)
"""

import os
import sys
import json
import hashlib
import time
from datetime import datetime, timezone
import mpmath as mp
from connes_cvs import build_galerkin_matrix, compute_ground_state


def compute_file_sha256(filepath):
    """Computes SHA256 hex digest of a file."""
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def project_even(Q_full, M):
    """
    Even Unitary Projection:
    Given full Galerkin matrix Q_full of dimension (2M+1) x (2M+1)
    (with frequency indices -M, ..., 0, ..., M, center at index M):
    The even-parity subspace has dimension M+1 with basis:
    - e_0 = |0> (zero frequency, row/col index M)
    - e_k = (|k> + |-k>) / sqrt(2) for k = 1, ..., M

    Entries of Q_even ((M+1) x (M+1)):
    Q_even[0, 0] = Q_full[M, M]
    Q_even[0, k] = (Q_full[M, M+k] + Q_full[M, M-k]) / sqrt(2) for k >= 1
    Q_even[k, 0] = Q_even[0, k]
    Q_even[j, k] = 0.5 * (Q_full[M+j, M+k] + Q_full[M+j, M-k] + Q_full[M-j, M+k] + Q_full[M-j, M-k]) for j,k >= 1
    Symmetrize: Q_even[i,j] = 0.5 * (Q_even[i,j] + Q_even[j,i])
    """
    Q_even = mp.matrix(M + 1, M + 1)
    Q_even[0, 0] = Q_full[M, M]
    sqrt2 = mp.sqrt(2)

    for k in range(1, M + 1):
        val = (Q_full[M, M + k] + Q_full[M, M - k]) / sqrt2
        Q_even[0, k] = val
        Q_even[k, 0] = val

    for j in range(1, M + 1):
        for k in range(1, M + 1):
            Q_even[j, k] = mp.mpf('0.5') * (
                Q_full[M + j, M + k]
                + Q_full[M + j, M - k]
                + Q_full[M - j, M + k]
                + Q_full[M - j, M - k]
            )

    for i in range(M + 1):
        for j in range(i + 1, M + 1):
            sym = mp.mpf('0.5') * (Q_even[i, j] + Q_even[j, i])
            Q_even[i, j] = sym
            Q_even[j, i] = sym

    return Q_even


def construct_matrix_A1(Q_even, n_inner):
    """
    Subspace A1: Standard One-Step Fourier Extension
    Dimension: n_inner + 2 (indices 0, 1, ..., n_inner + 1 in the even basis)
    Subspace matrix Q_A1: top-left (n_inner + 2) x (n_inner + 2) principal submatrix of Q_even.
    """
    dim = n_inner + 2
    Q_A1 = mp.matrix(dim, dim)
    for i in range(dim):
        for j in range(dim):
            Q_A1[i, j] = Q_even[i, j]
    return Q_A1


def construct_matrix_B(Q_even, n_inner, M_outer):
    """
    Subspace B: Single t^2 Boundary Augmentation
    Dimension: n_inner + 2
    Augmented basis: V_n^even + span{v_perp}, where V_n^even has dimension n_inner + 1 (indices 0, ..., n_inner).
    a_k = (-1)^k * sqrt(2) / k^2 for k = 1, ..., M_outer, and a_0 = 0.
    a_perp[k] = 0 for k = 0, ..., n_inner, and a_perp[k] = a_k for k = n_inner + 1, ..., M_outer.
    v_perp = a_perp / sqrt(sum(x^2 for x in a_perp)).
    
    Q_B of size (n_inner + 2) x (n_inner + 2):
    - Top-left (n_inner + 1) x (n_inner + 1) block: Q_even[i, j] for i, j in 0..n_inner.
    - Border cross-terms: Q_B[i, n_inner + 1] = sum_{k=n_inner + 1}^{M_outer} Q_even[i, k] * v_perp[k]
    - Q_B[n_inner + 1, i] = Q_B[i, n_inner + 1]
    - Diagonal corner self-energy: Q_B[n_inner + 1, n_inner + 1] = sum_{j, k = n_inner + 1}^{M_outer} v_perp[j] * Q_even[j, k] * v_perp[k]
    """
    dim = n_inner + 2
    a_perp = [mp.mpf(0)] * (M_outer + 1)
    sqrt2 = mp.sqrt(2)
    for k in range(n_inner + 1, M_outer + 1):
        sign = mp.mpf(1) if (k % 2 == 0) else mp.mpf(-1)
        a_perp[k] = sign * sqrt2 / mp.mpf(k * k)

    norm_sq = sum(a_perp[k] * a_perp[k] for k in range(n_inner + 1, M_outer + 1))
    norm = mp.sqrt(norm_sq)
    v_perp = [a_perp[k] / norm for k in range(M_outer + 1)]

    Q_B = mp.matrix(dim, dim)

    # Top-left block
    for i in range(n_inner + 1):
        for j in range(n_inner + 1):
            Q_B[i, j] = Q_even[i, j]

    # Border cross-terms
    for i in range(n_inner + 1):
        cross = mp.mpf(0)
        for k in range(n_inner + 1, M_outer + 1):
            cross += Q_even[i, k] * v_perp[k]
        Q_B[i, n_inner + 1] = cross
        Q_B[n_inner + 1, i] = cross

    # Corner self-energy
    corner = mp.mpf(0)
    for j in range(n_inner + 1, M_outer + 1):
        for k in range(n_inner + 1, M_outer + 1):
            corner += v_perp[j] * Q_even[j, k] * v_perp[k]
    Q_B[n_inner + 1, n_inner + 1] = corner

    # Symmetrize
    for i in range(dim):
        for j in range(i + 1, dim):
            sym = mp.mpf('0.5') * (Q_B[i, j] + Q_B[j, i])
            Q_B[i, j] = sym
            Q_B[j, i] = sym

    return Q_B


def compute_lowest_eigenvalue(matrix):
    """Computes the ground (minimum) eigenvalue of a symmetric mpmath matrix using mpmath.eigsy."""
    evals = mp.eigsy(matrix, eigvals_only=True)
    return min(evals)


def compute_gate_a_ground_state(Q):
    """Extracts ground state eigenvalue using compute_ground_state or eigsy."""
    res = compute_ground_state(Q)
    if isinstance(res, (tuple, list)):
        return res[0]
    return res


def run_cleanroom_verification():
    start_time = time.time()
    print("=" * 80, flush=True)
    print("STARTING CLEAN-ROOM INDEPENDENT E4 VERIFICATION: RH-T056R8R3", flush=True)
    print(f"Timestamp: {datetime.now(timezone.utc).isoformat()}", flush=True)
    print("=" * 80, flush=True)

    base_dir = os.path.dirname(os.path.abspath(__file__))
    prereg_path = os.path.join(base_dir, "RH-T056R8R3_PREREGISTRATION.json")
    with open(prereg_path, "r", encoding="utf-8") as f:
        prereg = json.load(f)

    results = {
        "protocol_id": "RH-T056R8R3",
        "verification_type": "CLEAN_ROOM_INDEPENDENT_E4",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "oracle": {
            "package": "connes-cvs",
            "version": "0.3.1"
        },
        "gates": {},
        "primary_grid": [],
        "verdict_summary": {}
    }

    # -------------------------------------------------------------------------
    # GATE A: Public Reference Fixture
    # c = 13, N = 80, T = 400 across precision ladder dps in {80, 120, 160}
    # -------------------------------------------------------------------------
    print("\n--- EXECUTING GATE A: Public Reference Fixture (c=13, N=80, T=400) ---", flush=True)
    gate_a_expected = mp.mpf("2.5282661401965756026859551460395357984852932822457493202998634125895744410943922e-59")
    gate_a_precisions = [80, 120, 160]
    gate_a_results = []
    gate_a_passed = True

    for dps_val in gate_a_precisions:
        mp.dps = dps_val
        t0 = time.time()
        print(f"Gate A: Building Galerkin matrix (c=13, N=80, T=400, dps={dps_val})...", flush=True)
        Q_gate_a = build_galerkin_matrix(13, 80, 400, dps=dps_val)
        print(f"Gate A: Computing ground state eigenvalue (dps={dps_val})...", flush=True)
        lambda_min = compute_gate_a_ground_state(Q_gate_a)
        t_elapsed = time.time() - t0

        rel_err = abs(lambda_min - gate_a_expected) / gate_a_expected
        passed = bool(rel_err < mp.mpf("1e-15"))
        if not passed:
            gate_a_passed = False

        print(f"  dps={dps_val}: lambda_min = {mp.nstr(lambda_min, 30)}", flush=True)
        print(f"  rel_err = {mp.nstr(rel_err, 15)}, passed = {passed}, elapsed = {t_elapsed:.2f}s", flush=True)

        gate_a_results.append({
            "dps": dps_val,
            "lambda_min": mp.nstr(lambda_min, 80),
            "expected": mp.nstr(gate_a_expected, 80),
            "relative_error": mp.nstr(rel_err, 25),
            "passed": passed,
            "elapsed_seconds": t_elapsed
        })

    results["gates"]["gate_a"] = {
        "passed": gate_a_passed,
        "ladder_results": gate_a_results
    }
    print(f"Gate A Overall Result: {'PASS' if gate_a_passed else 'FAIL'}", flush=True)

    # -------------------------------------------------------------------------
    # GATE B: Predecessor Calibration
    # c = 13, n = 10, M = 20, T = 400, dps = 80
    # Expected R_B > 1.0 (~51.25)
    # -------------------------------------------------------------------------
    print("\n--- EXECUTING GATE B: Predecessor Calibration (c=13, n=10, M=20, T=400, dps=80) ---", flush=True)
    mp.dps = 80
    t0 = time.time()
    Q_full_b = build_galerkin_matrix(13, 20, 400, dps=80)
    Q_even_b = project_even(Q_full_b, 20)
    Q_A1_b = construct_matrix_A1(Q_even_b, 10)
    Q_B_b = construct_matrix_B(Q_even_b, 10, 20)

    lambda_A1_b = compute_lowest_eigenvalue(Q_A1_b)
    lambda_B_b = compute_lowest_eigenvalue(Q_B_b)
    R_B_b = lambda_B_b / lambda_A1_b
    t_elapsed_b = time.time() - t0

    gate_b_passed = bool(R_B_b > mp.mpf(1.0))
    print(f"Gate B: lambda_A1 = {mp.nstr(lambda_A1_b, 25)}", flush=True)
    print(f"Gate B: lambda_B  = {mp.nstr(lambda_B_b, 25)}", flush=True)
    print(f"Gate B: R_B       = {mp.nstr(R_B_b, 20)}", flush=True)
    print(f"Gate B: passed (R_B > 1.0) = {gate_b_passed}, elapsed = {t_elapsed_b:.2f}s", flush=True)

    results["gates"]["gate_b"] = {
        "passed": gate_b_passed,
        "c": 13,
        "n_inner": 10,
        "M_outer": 20,
        "T": 400,
        "dps": 80,
        "lambda_A1": mp.nstr(lambda_A1_b, 80),
        "lambda_B": mp.nstr(lambda_B_b, 80),
        "R_B": mp.nstr(R_B_b, 30),
        "elapsed_seconds": t_elapsed_b
    }

    # -------------------------------------------------------------------------
    # PRIMARY 20-CELL GRID
    # c in {9, 11, 13, 15, 17}, n_inner in {6, 8, 10, 12}, T=400, dps=80
    # M_outer = max(20, 2 * n_inner)
    # -------------------------------------------------------------------------
    print("\n--- EXECUTING PRIMARY 20-CELL GRID ---", flush=True)
    mp.dps = 80

    primary_cells = prereg["primary_grid_20_cells"]
    
    # We cache Galerkin matrices per (c, M_outer) to avoid redundant computation
    matrix_cache = {}

    fourier_lower_count = 0
    t2_lower_count = 0
    unresolved_count = 0

    for idx, cell in enumerate(primary_cells, 1):
        cell_id = cell["cell_id"]
        c_val = cell["c"]
        n_inner = cell["n_inner"]
        M_outer = cell["M_outer"]
        T_val = cell["T"]

        print(f"[{idx}/20] Cell {cell_id}: c={c_val}, n={n_inner}, M={M_outer}, T={T_val}...", flush=True)
        t_cell_start = time.time()

        cache_key = (c_val, M_outer, T_val, 80)
        if cache_key not in matrix_cache:
            print(f"  Building Galerkin matrix Q_{{c={c_val}, M={M_outer}, T={T_val}}} (dps=80)...", flush=True)
            Q_full = build_galerkin_matrix(c_val, M_outer, T_val, dps=80)
            Q_even = project_even(Q_full, M_outer)
            matrix_cache[cache_key] = (Q_full, Q_even)
        else:
            Q_full, Q_even = matrix_cache[cache_key]

        Q_A1 = construct_matrix_A1(Q_even, n_inner)
        Q_B = construct_matrix_B(Q_even, n_inner, M_outer)

        lambda_A1 = compute_lowest_eigenvalue(Q_A1)
        lambda_B = compute_lowest_eigenvalue(Q_B)
        R_B = lambda_B / lambda_A1

        if R_B > mp.mpf(1.0):
            decision = "FOURIER_EXTENSION_LOWER"
            fourier_lower_count += 1
        elif R_B < mp.mpf(1.0):
            decision = "T2_EXTENSION_LOWER"
            t2_lower_count += 1
        else:
            decision = "NUMERICALLY_UNRESOLVED"
            unresolved_count += 1

        t_cell_elapsed = time.time() - t_cell_start
        print(f"  lambda_A1 = {mp.nstr(lambda_A1, 20)}", flush=True)
        print(f"  lambda_B  = {mp.nstr(lambda_B, 20)}", flush=True)
        print(f"  R_B       = {mp.nstr(R_B, 20)} -> {decision} ({t_cell_elapsed:.2f}s)", flush=True)

        results["primary_grid"].append({
            "cell_id": cell_id,
            "c": c_val,
            "n_inner": n_inner,
            "M_outer": M_outer,
            "T": T_val,
            "dps": 80,
            "lambda_A1": mp.nstr(lambda_A1, 80),
            "lambda_B": mp.nstr(lambda_B, 80),
            "R_B": mp.nstr(R_B, 30),
            "decision": decision,
            "elapsed_seconds": t_cell_elapsed
        })

    # Determine Grid Outcome
    if fourier_lower_count == 20:
        outcome = "Outcome_A"
        outcome_desc = "T2_BOUNDARY_DISFAVORED_ACROSS_ALL_RESOLVED_PREREGISTERED_PRIMARY_CELLS"
    elif t2_lower_count == 20:
        outcome = "Outcome_C"
        outcome_desc = "T2_BOUNDARY_FAVORED_ACROSS_ALL_RESOLVED_PREREGISTERED_PRIMARY_CELLS_REQUIRES_REPLICATION"
    elif unresolved_count > 0:
        outcome = "Outcome_D"
        outcome_desc = "PRIMARY_GRID_NUMERICALLY_INCONCLUSIVE"
    else:
        outcome = "Outcome_B"
        outcome_desc = "T2_BOUNDARY_EFFECT_NONUNIVERSAL_ON_PREREGISTERED_GRID"

    total_time = time.time() - start_time
    results["verdict_summary"] = {
        "total_cells": len(primary_cells),
        "fourier_lower_count": fourier_lower_count,
        "t2_lower_count": t2_lower_count,
        "unresolved_count": unresolved_count,
        "outcome": outcome,
        "outcome_description": outcome_desc,
        "total_elapsed_seconds": total_time
    }

    # Write BLIND_RESULTS.json
    out_file = os.path.join(base_dir, "BLIND_RESULTS.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    print("\n" + "=" * 80, flush=True)
    print(f"VERIFICATION COMPLETE: {outcome} ({outcome_desc})", flush=True)
    print(f"Summary: Fourier Lower = {fourier_lower_count}/20, t2 Lower = {t2_lower_count}/20, Unresolved = {unresolved_count}/20", flush=True)
    print(f"Results written to: {out_file}", flush=True)
    print(f"Total time: {total_time:.2f}s", flush=True)
    print("=" * 80, flush=True)

    # Compute SHA256 of BLIND_RESULTS.json and seal it
    results_sha256 = compute_file_sha256(out_file)
    seal_path = os.path.join(base_dir, "BLIND_RESULT_SEAL.json")
    seal_data = {
        "protocol_id": "RH-T056R8R3",
        "sealed_file": "BLIND_RESULTS.json",
        "sha256": results_sha256,
        "sealed_at_utc": datetime.now(timezone.utc).isoformat(),
        "script_sha256": compute_file_sha256(__file__),
        "status": "SEALED"
    }
    with open(seal_path, "w", encoding="utf-8") as f:
        json.dump(seal_data, f, indent=2)

    print(f"Blind results sealed at: {seal_path}", flush=True)
    print(f"BLIND_RESULTS.json SHA256: {results_sha256}", flush=True)


if __name__ == "__main__":
    run_cleanroom_verification()
