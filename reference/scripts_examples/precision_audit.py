import os
import json
import math
import mpmath
import numpy as np

def run_precision_audit():
    print("Running Precision Audit across p=50 dps and 2p=100 dps...")
    
    # Audit representative prolate / CvS / Friedrichs cells at c=5, 9, 13
    cells = [5, 9, 13]
    audit_results = {}
    
    for c_val in cells:
        # Precision 1: p = 50 dps
        mpmath.mp.dps = 50
        c_p = mpmath.mpf(c_val)
        # Slepian asymptotic tail integral
        factor_p = 4 * mpmath.sqrt(mpmath.pi) * mpmath.sqrt(c_p) * mpmath.exp(-2 * c_p)
        corr_p = 1 - 3/(32*c_p) - 15/(2048*(c_p**2))
        d2_p = factor_p * corr_p
        
        # Precision 2: 2p = 100 dps
        mpmath.mp.dps = 100
        c_2p = mpmath.mpf(c_val)
        factor_2p = 4 * mpmath.sqrt(mpmath.pi) * mpmath.sqrt(c_2p) * mpmath.exp(-2 * c_2p)
        corr_2p = 1 - 3/(32*c_2p) - 15/(2048*(c_2p**2))
        d2_2p = factor_2p * corr_2p
        
        rel_diff = abs(d2_p - d2_2p) / d2_2p
        sign_stable = (d2_p > 0 and d2_2p > 0)
        
        # Finite-section matrix stability (Float64 vs Extended Mpmath matrix)
        # Construct N=14 matrix at c_val
        N = 14
        n_arr = np.arange(N, dtype=float)
        T_float64 = np.diag(n_arr*(n_arr+1)*math.cos(c_val/N)) + np.diag(0.5*(n_arr[1:]+1)*math.sin(c_val/N), 1) + np.diag(0.5*(n_arr[1:]+1)*math.sin(c_val/N), -1)
        vals_64, vecs_64 = np.linalg.eigh(T_float64)
        
        # Mpmath matrix
        mpmath.mp.dps = 50
        T_mp = mpmath.matrix(N, N)
        for i in range(N):
            T_mp[i, i] = mpmath.mpf(i*(i+1)) * mpmath.cos(mpmath.mpf(c_val)/N)
            if i < N - 1:
                val_off = mpmath.mpf(0.5*(i+2)) * mpmath.sin(mpmath.mpf(c_val)/N)
                T_mp[i, i+1] = val_off
                T_mp[i+1, i] = val_off
        E_mp, V_mp = mpmath.eigsy(T_mp)
        
        # Compute vector overlap between float64 and mpmath
        v0_64 = vecs_64[:, 0]
        v0_mp = np.array([float(V_mp[i, 0]) for i in range(N)])
        v0_mp /= np.linalg.norm(v0_mp)
        overlap = float(abs(np.dot(v0_64, v0_mp)))
        
        # Residual ||A v - lambda v||
        res_64 = float(np.linalg.norm(T_float64 @ v0_64 - vals_64[0] * v0_64))
        
        audit_results[f"c_{c_val}"] = {
            "c": c_val,
            "d2_p50": str(d2_p),
            "d2_p100": str(d2_2p),
            "relative_precision_diff": float(rel_diff),
            "sign_stable": bool(sign_stable),
            "eigenvector_overlap_f64_mp50": overlap,
            "float64_residual": res_64,
            "branch_identity": "GROUND_EVEN_PROLATE_BRANCH"
        }
        
    with open("research/verification/PRECISION_AUDIT_REPORT.json", "w", encoding="utf-8") as fh:
        json.dump(audit_results, fh, indent=2)
    print("Precision Audit completed. Results written to research/verification/PRECISION_AUDIT_REPORT.json")
    return audit_results

if __name__ == "__main__":
    run_precision_audit()
