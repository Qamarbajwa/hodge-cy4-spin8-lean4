package hodge.governance.gates

default allow = false

# Gate 1: Coefficient Sensitivity Gate (The Integral Trap)
# Reject claims that do not strictly require rational coefficients Q
deny[msg] {
    input.coefficients != "Q"
    input.coefficients != "rational"
    msg := "DENIED by Gate 1 (FLAG-HODGE-01): General claim over Z is invalid due to Atiyah-Hirzebruch torsion obstruction."
}

# Gate 2: Projectivity Dependency Gate (The Kähler Barrier)
# Reject claims that apply to arbitrary compact Kähler manifolds without projectivity
deny[msg] {
    input.space.is_projective == false
    msg := "DENIED by Gate 2 (FLAG-HODGE-02): Voisin (2002) disproved the Hodge conjecture on non-projective Kähler manifolds. Projective embedding is mandatory."
}

# Gate 3: Higher-Codimension Barrier (Codimension p >= 2)
# Reject claims that rely solely on Chern classes of vector bundles to generate cycles for p >= 2
deny[msg] {
    input.codimension >= 2
    input.construction.relies_only_on_vector_bundles == true
    msg := "DENIED by Gate 3 (FLAG-HODGE-03): Chern classes of vector bundles do not span the Chow ring for codimension >= 2 (Grothendieck/Mumford)."
}

# Gate 4: Zero Unjustified Assumptions
deny[msg] {
    count(input.unjustified_assumptions) > 0
    msg := sprintf("DENIED by Gate 4: Found %d unjustified assumptions. Promotion is blocked.", [count(input.unjustified_assumptions)])
}

# Gate 5: Dual-Custody Approval Gate
# No claim can be promoted to PROVED or THEOREM without explicit dual-custody approval token
deny[msg] {
    input.promoted_status == "PROVED"
    not input.dual_custody_approved
    msg := "DENIED by Chrysalis Gate 4: Autonomous agents cannot self-promote claims to PROVED without Lead Researcher cryptographic sign-off."
}

# Allow if and only if there are no denials
allow {
    count(deny) == 0
}
