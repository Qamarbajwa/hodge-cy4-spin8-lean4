"""Command-Line Interface to execute Google Cloud Project Chrysalis Autonomous Lab."""

import argparse
import json
from toolkit.chrysalis_engine import ChrysalisAutonomousLab


def main():
    parser = argparse.ArgumentParser(description="Google Cloud Project Chrysalis Hodge Autonomous Lab Runner")
    parser.add_argument("--mode", type=str, default="hypersurface", choices=["hypersurface", "weil", "schoen", "kummer", "mt", "normal_function"], help="Execution mode: hypersurface, weil, schoen, kummer, mt, or normal_function")
    parser.add_argument("--dim", type=int, default=4, help="Complex dimension n of variety (e.g. 4 for fourfolds)")
    parser.add_argument("--deg", type=int, default=3, help="Degree d of hypersurface (e.g. 3 for cubic, 4 for quartic)")
    parser.add_argument("--d", type=int, default=1, help="Field discriminant for Weil abelian fourfold K=Q(sqrt(-d))")
    parser.add_argument("--family", type=str, default="Cubic Fourfold Moduli Family", help="Name of moduli family")
    parser.add_argument("--token", type=str, default=None, help="Optional dual-custody cryptographic token")
    args = parser.parse_args()

    print("================================================================================")
    print("   GOOGLE CLOUD PROJECT CHRYSALIS — AUTONOMOUS HODGE CONJECTURE LAB           ")
    print("================================================================================")
    print(f"Execution Mode: {args.mode.upper()}")
    print(f"Dual-Custody Token: {'PRESENT' if args.token else 'NONE (Exploratory mode)'}")
    print("Initializing Chrysalis 5-Actor DAG: Router -> Worker -> Reviewer -> Acceptor -> Watchdog...")

    lab = ChrysalisAutonomousLab(dual_custody_token=args.token)

    if args.mode == "weil":
        print(f"Target: Abelian Fourfold of Weil Type (K = Q(sqrt(-{args.d})), Dimension n=4)")
        result = lab.run_weil_fourfold_audit(field_d=args.d)
    elif args.mode == "schoen":
        print(f"Target: Schoen-Prym CM Boundary A_0 = E^4 (K = Q(sqrt(-{args.d})), Dimension n=4)")
        result = lab.run_schoen_prym_audit(field_d=args.d)
    elif args.mode == "kummer":
        print(f"Target: Desingularized Kummer Fourfold X = Km~(A) (K = Q(sqrt(-{args.d})), Dimension n=4)")
        result = lab.run_kummer_audit(field_d=args.d)
    elif args.mode == "mt":
        print(f"Target: Mumford-Tate Group MT(A) = SU(2, 2) on General Weil Fourfold (K = Q(sqrt(-{args.d})), Dimension n=4)")
        result = lab.run_mumford_tate_audit(field_d=args.d)
    elif args.mode == "normal_function":
        print(f"Target: Higher Normal Function & Singular Cycle Sieve (K = Q(sqrt(-{args.d})), Dimension n=4)")
        result = lab.run_normal_function_audit(field_d=args.d)
    else:
        print(f"Target: {args.family} (Dimension n={args.dim}, Degree d={args.deg})")
        result = lab.run_hodge_moduli_cycle(
            dimension_n=args.dim,
            degree_d=args.deg,
            family_name=args.family,
        )

    print("\n--- Chrysalis Cycle Execution Receipts ---")
    for r in lab.receipts:
        print(f"[{r.timestamp_utc}] {r.phase:<20} | Actor: {r.actor_id:<22} | Status: {r.status}")
        print(f"    Signature: {r.sha256_signature[:24]}...")

    print("\n================================================================================")
    print("FINAL CHRYSALIS STATUS:", result["status"])
    if args.mode == "weil":
        print(f"Primitive Weil Dimension: {result.get('primitive_weil_dimension')}")
        print(f"Orthogonal to Divisor Products: {result.get('strictly_orthogonal_to_divisors')}")
        print(f"Conclusion: {result.get('conclusion')}")
    elif args.mode == "schoen":
        print(f"Schoen Boundary Cycle Solved: {result.get('schoen_cycle_solved')}")
        print(f"Cycle Coefficients: {result.get('cycle_coefficients')}")
        print(f"Deformation Obstruction Norm: {result.get('obstruction_norm')}")
        print(f"Conclusion: {result.get('conclusion')}")
    elif args.mode == "kummer":
        print(f"Total Singularities: {result.get('total_singularities')}")
        print(f"Exceptional Surfaces Contract to Zero: {result.get('exceptional_surfaces_contract_to_zero')}")
        print(f"Exceptional Pairing with Weil Class: {result.get('exceptional_pairing_all_zero')}")
        print(f"Conclusion: {result.get('conclusion')}")
    elif args.mode == "mt":
        print(f"Poincare Intersection Eigenvalues: {result.get('poincare_intersection_eigenvalues')}")
        print(f"Q_11 (w1 . w1): {result.get('q11_self_intersection')}")
        print(f"Smooth Surface Obstructed: {result.get('smooth_surface_obstructed')}")
        print(f"Conclusion: {result.get('conclusion')}")
    elif args.mode == "normal_function":
        print(f"IVHS Rank on Moduli M_Weil: {result.get('ivhs_rank')}/4")
        print(f"Green-Griffiths-Kerr Min Curvature: {result.get('ggk_min_curvature')}")
        print(f"Chow Group cl Image Dimension: {result.get('dim_chow_image')}")
        print(f"Primitive Weil Algebraic Cycles: {result.get('primitive_weil_cycles')}")
        print(f"Conclusion: {result.get('conclusion')}")
    else:
        print(f"Boundary Algebraic Cycles Proved: {result.get('boundary_cycles_algebraic')}")
    print(f"Cryptographic Invariant Seal: {result.get('signed_invariant_sha256')}")
    print("================================================================================")


if __name__ == "__main__":
    main()
