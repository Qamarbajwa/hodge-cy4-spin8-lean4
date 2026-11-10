# ASSUMPTION MINIMIZATION STAGE PROTOCOL
**Governing Standard:** `MATHEMATICAL_RESEARCH_CONSTITUTION_v1.0 §13`  

---

## 1. Purpose

Following the successful verification of a theorem candidate $A \wedge B \wedge C \implies T$, the project initiates an automatic **Assumption Minimization Sweep** to eliminate non-essential technical hypotheses and expose the sharpest mathematical frontier.

---

## 2. Hypothesis Pruning Workflow

For every hypothesis $H_i$ in the initial proof:
1. **Omission Test:** Attempt to carry through the deduction without $H_i$.
2. **Weakening Test:** Replace $H_i$ with a weaker condition (e.g. replace $C^\infty$ with $H^1$, replace compact support with exponential decay, replace point-wise bounds with $L^1$ integral bounds).
3. **Classification:**
   - `ESSENTIAL`: Dropping $H_i$ permits a concrete counterexample.
   - `REMOVABLE`: Theorem holds with $H_i$ deleted.
   - `PROOF_ARTIFACT`: $H_i$ was needed only for a specific proof technique (e.g., Fourier series truncation) but not for the underlying structural truth.
   - `UNKNOWN`: Status open pending further analysis.

---

## 3. Artifact Output

The stage produces an updated `ASSUMPTION_MINIMIZATION_RECEIPT.yaml` documenting the minimal hypothesis set $H_{\text{min}}$ before canonicalization.
