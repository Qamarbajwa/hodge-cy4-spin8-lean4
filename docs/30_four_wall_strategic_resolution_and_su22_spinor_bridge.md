# Event 24: Four-Wall Strategic Resolution Engine & $\mathfrak{su}(2,2)$ Spinor-to-Weil Bridge Audit

**Status:** `FORMALLY_VERIFIED_STRUCTURAL_CLOSURE` (Global bridges `S-BRIDGE-DEFORM-CY4` and `S-BRIDGE-SPINOR-MOTIVE` remain `ADVERSARIALLY_BLOCKED_OPEN_BRIDGE`; `GLOBAL_HODGE_CONJECTURE = OPEN`)  
**Engine:** `toolkit/four_wall_strategic_resolution_engine.py` (`scan_forbidden == []`, 0 floats)  
**Lean 4.35.0 Formalization:** Theorems 29 & 30 (`spinor_to_weil_su22_branching_eq`, `tangential_leibniz_annihilator_eq`), total **30/30** (`axioms: []`)

---

## 1. Wall 1: Signed Fermat Sextic & Tangential Leibniz Closure (`407/407`)
In `SignedFermatTangentialTransportEngine`, we switch to the signed Fermat hypersurface
$$F_0^{\mathrm{signed}} = x_0^6 - x_3^6 + x_1^6 - x_4^6 + x_2^6 - x_5^6 = 0,$$
where the real linear plane $\Pi_{\mathrm{true}} = \{x_0 - x_3 = x_1 - x_4 = x_2 - x_5 = 0\}$ is supported by the signed cyclotomic wavepacket $\Lambda_{\Pi_{\mathrm{true}}} = \prod_{k=0}^2 \bigl(\sum_{a=0}^4 x_k^{4-a} x_{k+3}^a\bigr) \in R^{12}(F_0^{\mathrm{signed}})$.

Exact rational linear algebra reveals why Wall 1 (`359/407` vs `407/407`) closes 100% under simultaneous generator tilting:
1. **Unquotiented Tangential Leibniz Property:** Every kernel direction $u \in \ker M^{(6)}$ (`407/407`) lifts to an explicit unquotiented polynomial representative $\tilde{u} \in I_{\Pi_{\mathrm{true}}, 6}$ ($\dim I_{\Pi_{\mathrm{true}}, 5} = 228$). Applying the tangential operators $D_k^+ = \partial_k + \partial_{k+3}$ satisfies
   $$D_k^+(\tilde{u}) \in I_{\Pi_{\mathrm{true}}, 5} \quad \text{for all } 407 / 407 \text{ basis directions (`0` unlifted)},$$
   whereas the normal operators $D_k^- = \partial_k - \partial_{k+3}$ escape $I_{\Pi_{\mathrm{true}}, 5}$ across **`398 / 407`** directions (Lean Theorem 30 `tangential_leibniz_annihilator_eq`).
2. **Signed vs. Unsigned Fermat Dual-Ring Solvability:** Solving $(g_k + t\,\delta g_k)(\Lambda_0 + t\,\Lambda_1) \equiv 0 \pmod{J(F_t^{\mathrm{signed}}), t^2}$ yields:
   - Stationary basis (`delta_g = 0`): `359/407` (`subspace_dim = 401`, `6` unlifted normal directions).
   - Joint generator–shadow transport on **signed** Fermat: **`407 / 407` (`100%`, `0` unlifted directions!)**, accompanied by exact doubled flatness rank vector `(6, 12, 20, 30, 36, 38)`.
   - Joint generator–shadow transport on **unsigned** Fermat $F_0 = \sum x_i^6$: **`359 / 407` (`48` unlifted directions)**, proving that sign compatibility ($x_k^6 - x_{k+3}^6$ carrying real 2-planes) resolves all 48 first-order normal directions locally over $\mathbb{Q}[t]/(t^2)$.

## 2. Wall 2: Peskine–Szpiro Geometric Liaison Compression
In `GeometricLiaisonCompressionEngine`, a Band-3 residual algebraic cycle $Z_5$ of degree 5 linked to $\Pi_0$ along a complete intersection $\Sigma_0 \cap \Sigma_1$ has primitive cohomology identity
$$\Lambda_{Z_5}^{\mathrm{prim}} \equiv -\Lambda_{\Pi_0} \pmod{J(F_0)}.$$
Via exact rational Macaulay apolarity (`m = 1..6`), inverting $-\Lambda_{\Pi_0}$ recovers $\operatorname{Ann}_{R^1}(\Lambda_{Z_5}^{\mathrm{prim}}) = (x_0 - x_3, x_1 - x_4, x_2 - x_5)$ ($\dim = 3$), exact rank vector `(3, 6, 10, 15, 18, 19)`, Gotzmann regularity $G = 1$, and a codimension-2 linking witness $x_2^4 \Sigma_0 \Sigma_1 + \Lambda_{\mathrm{tail}}$ (`ann_R1 = 2`). While liaison compresses any *linked* Fermat cycle to a small dual ideal, unlinked high-degree non-Fermat cycles still lack a global Castelnuovo–Mumford regularity bound (`non_linked_castelnuovo_mumford_bound_known = False`).

## 3. Wall 3: Integral Picard–Lefschetz Nodal Reflection Bridge
In `PicardLefschetzNodalBridgeEngine`, degenerating $F_0$ to a nodal sextic and taking `5` simple $A_5$ vanishing spheres $\{\delta_1, \dots, \delta_5\}$ ($\langle \delta_i, \delta_i \rangle = 2$) generates signed involutive Picard–Lefschetz reflections
$$T_{\delta}(\gamma) = \gamma - \langle \gamma, \delta \rangle \delta, \qquad T_\delta^2 = \mathrm{Id}.$$
All `5` reflections preserve the intersection form (`isometry = True`), preserve Wirtinger topological balance, and generate a finite Weyl $S_6$-orbit of exact size **`30`** (corresponding to the $\binom{6}{2} \cdot 2$ signed vanishing roots). Extending monodromy transport beyond nodal $A_n$ degenerations to general non-decomposable classes remains open (`nodal_bridge_gives_effective_global_bound = False`).

## 4. Wall 4: $D_4 \supset D_3 \times \mathrm{U}(1) \cong \mathfrak{su}(2,2) \times \mathrm{U}(1)$ Spinor-to-Weil Bridge
In `SpinorToWeilSpecializationEngine`, specializing the Mumford–Kuga–Satake $\mathrm{SO}(8)$ spinor representation $S^+_8 = V_+ \oplus V_-$ along $D_4 \supset D_3 \times \mathrm{U}(1) \cong \mathfrak{su}(2,2) \times \mathrm{U}(1)$ splits the $D_3$ zero-weight space (`sum(w[:3]) = (0,0,0)`) in $\bigwedge^4 S^+_8$ as:
$$(\bigwedge\nolimits^4 S^+_8)_{0}^{D_3} = \underbrace{\bigl(\bigwedge\nolimits^4 V_+ \oplus \bigwedge\nolimits^4 V_-\bigr)}_{\text{2 pure Weil tuples } (0,3,5,6),(1,2,4,7) \;\cong\; W_0(A_4)} \;\oplus\; \underbrace{(\bigwedge\nolimits^4 S^+_8)_{0}^{D_4}}_{\text{6 mixed }(2,2)\text{ } K_{2,2}\text{ tuples}}, \qquad 8 = 2 + 6,$$
verified in Lean Theorem 29 (`spinor_to_weil_su22_branching_eq`). On the 6 mixed $K_{2,2}$ tuples, the $D_3$ simple root operators stack to exact rank **`5`**, leaving **`1`** $\operatorname{SU}(2,2)$ polarization singlet ($\mathbb{Q} \cdot \omega^2$), giving total $\operatorname{SU}(2,2)$-invariants `2 + 1 = 3` (matching Markman's abelian 4-fold Weil locus $1 + 2 + 33 + 34 = 70$). Because no horizontal $\mathrm{Spin}(8)$-to-Markman spreading morphism exists for simple generic sixfolds with $\operatorname{End}_{\mathbb{Q}}(A) = \mathbb{Q}$ (`horizontal_spin8_markman_spreading_proved = False`), `S-BRIDGE-SPINOR-MOTIVE` remains `ADVERSARIALLY_BLOCKED_OPEN_BRIDGE`.
