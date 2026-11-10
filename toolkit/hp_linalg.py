"""High-precision finite-section engine (generalised from RH-T056R8R3).

Pattern used in the RH project:
    operator Q  --Galerkin finite section-->  matrix Q_N  --parity projection-->  Q_even
    --restrict to competing trial subspaces-->  Rayleigh-Ritz ground energies  -->  ratio R = lam_B / lam_A

Everything is pure mpmath. float64 / scipy are deliberately NOT used because the RH ground
states were ~1e-59, far below float64 resolution (this exact mistake invalidated RH-T056R8).
"""
from __future__ import annotations
import mpmath as mp


def ground_eig(M):
    """Smallest eigenvalue of a symmetric mpmath matrix (mp.eigsy)."""
    return min(mp.eigsy(M, eigvals_only=True))


def symmetrize(M):
    n = M.rows
    for i in range(n):
        for j in range(i + 1, n):
            s = (M[i, j] + M[j, i]) / 2
            M[i, j] = M[j, i] = s
    return M


def even_projection(Q, M):
    """Project a (2M+1)x(2M+1) matrix indexed -M..M onto the even-parity subspace
    basis e0=|0>, ek=(|k>+|-k>)/sqrt2. Result is (M+1)x(M+1)."""
    E = mp.matrix(M + 1, M + 1)
    s2 = mp.sqrt(2)
    E[0, 0] = Q[M, M]
    for k in range(1, M + 1):
        E[0, k] = E[k, 0] = (Q[M, M + k] + Q[M, M - k]) / s2
    for j in range(1, M + 1):
        for k in range(1, M + 1):
            E[j, k] = mp.mpf(1) / 2 * (Q[M + j, M + k] + Q[M + j, M - k] + Q[M - j, M + k] + Q[M - j, M - k])
    return symmetrize(E)


def principal_block(Q, dim):
    """Competitor 'A': ordinary nested extension = leading principal block."""
    return mp.matrix([[Q[i, j] for j in range(dim)] for i in range(dim)])


def augmented_subspace(Q, n_inner, profile):
    """Competitor 'B': span{e_0..e_n_inner} + one extra vector v_perp built from `profile`
    (orthogonalised against the inner span, normalised). Same dimension n_inner+2 as principal_block(n_inner+2)."""
    Mo = Q.rows - 1
    a = [mp.mpf(0)] * (Mo + 1)
    for k in range(n_inner + 1, Mo + 1):
        a[k] = profile(k)
    nrm = mp.sqrt(sum(x * x for x in a))
    v = [x / nrm for x in a]
    d = n_inner + 2
    B = mp.matrix(d, d)
    for i in range(n_inner + 1):
        for j in range(n_inner + 1):
            B[i, j] = Q[i, j]
        c = sum(Q[i, k] * v[k] for k in range(n_inner + 1, Mo + 1))
        B[i, d - 1] = B[d - 1, i] = c
    B[d - 1, d - 1] = sum(v[j] * Q[j, k] * v[k] for j in range(n_inner + 1, Mo + 1) for k in range(n_inner + 1, Mo + 1))
    return symmetrize(B)


def ritz(Q, V):
    """General Rayleigh-Ritz: V is a list of column vectors (assumed orthonormal)."""
    Vm = mp.matrix(V).T if isinstance(V, list) else V
    return symmetrize(Vm.T * Q * Vm)


def precision_ladder(builder, ladder=(80, 120, 160), expected=None, rtol="1e-15"):
    """Run builder(dps)->eigenvalue at several precisions; require mutual agreement
    (and agreement with `expected` if given). Returns dict with per-tier result and pass flag."""
    out, vals = [], []
    for dps in ladder:
        mp.mp.dps = dps
        v = builder(dps)
        vals.append(v)
        row = {"dps": dps, "value": mp.nstr(v, 40)}
        if expected is not None:
            rel = abs(v - mp.mpf(expected)) / abs(mp.mpf(expected))
            row["rel_err"] = mp.nstr(rel, 5)
            row["passed"] = bool(rel < mp.mpf(rtol))
        out.append(row)
    ref = vals[-1]
    stable = all(abs(v - ref) / abs(ref) < mp.mpf(rtol) for v in vals)
    ok = stable and all(r.get("passed", True) for r in out)
    return {"tiers": out, "stable_across_ladder": stable, "passed": ok}


def decide_ratio(lam_B, lam_A, tol="1e-40"):
    """Preregistered ratio decision rule: R = lam_B/lam_A."""
    if abs(lam_A) < mp.mpf(tol) and abs(lam_B) < mp.mpf(tol):
        return "NUMERICALLY_UNRESOLVED"
    R = lam_B / lam_A
    if R > 1:
        return "A_LOWER"
    if R < 1:
        return "B_LOWER"
    return "NUMERICALLY_UNRESOLVED"
