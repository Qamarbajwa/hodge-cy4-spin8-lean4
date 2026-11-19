# Integration Blueprint: Google Cloud's Project Chrysalis for Hodge Conjecture Research

*Reference Architecture for Governed, Self-Evolving AI Agents in Advanced Mathematical Discovery.*

---

## 1. What is Project Chrysalis?

**Project Chrysalis** is Google Cloud's advanced reference architecture for **governed, self-evolving multi-agent AI systems**, built upon Gemini and the Google Agent Development Kit (ADK). 

While initially designed for autonomous, zero-downtime Site Reliability Engineering (SRE) and distributed systems, its underlying architecture solves the most critical obstacle in autonomous mathematical discovery: **how an AI agent can dynamically synthesize code and reconfigure its investigation strategy without violating formal invariants or hallucinating invalid steps.**

### Core Chrysalis Pillars
1. **Runtime Code & Tool Synthesis:** Agents dynamically generate, verify, and mount executable diagnostic/computational tools in memory rather than being constrained by static pre-written scripts.
2. **Self-Critique & Credit Assignment:** Evaluates the marginal utility of each deduction/step, isolating productive avenues from dead-ends.
3. **Signed Semantic Invariant Memory:** Cryptographically seals discovered structural invariants into memory so failed hypotheses are never repeated.
4. **Dynamic DAG Orchestration:** Re-architects multi-agent hierarchies in memory as Directed Acyclic Graphs (DAGs) to adapt to complex analytical landscapes.
5. **The Four Security/Governance Gates (Defense-in-Depth):**
   - **Gate 1 (Model Armor):** Input/output verification and prompt defense.
   - **Gate 2 (Cloud KMS & Binary Authorization):** Cryptographic signing of all runtime-generated tools/code before execution.
   - **Gate 3 (Open Policy Agent - OPA):** Policy-as-Code enforcing what operations/mutations are legally permitted.
   - **Gate 4 (Dual-Custody Human Approval):** Critical decisions require explicit human cryptographic sign-off.

---

## 2. Why Project Chrysalis is Profoundly Beneficial for the Hodge Lab

Solving a General Hodge Conjecture requires massive symbolic/geometric exploration while maintaining 100% mathematical integrity. Chrysalis provides the exact runtime infrastructure required:

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                        CHANCE OF HALLUCINATION / FALSE PROOF                           │
│  Standard AI Chat: HIGH (Uncontrolled synthesis, drifts, ignores torsion obstructions)   │
│  Chrysalis-Governed Lab: ZERO (Binary Authorization + Policy-as-Code + OPA Gates)      │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

| Chrysalis Capability | How It Powers the Hodge Conjecture Lab |
| :--- | :--- |
| **1. Runtime Tool Synthesis** | When investigating a specific family of 4-folds (e.g., Weil-type abelian varieties or complete intersections in Grassmanians), the system automatically synthesizes specialized Lie algebra generators, Picard-Fuchs differential equations, or Gröbner bases on the fly inside a sandboxed container. |
| **2. Signed Invariant Memory** | Directly implements our **`PERMANENT_NO_GO_LEDGER.md`**. When an agent tests a candidate cycle construction that hits an obstruction (e.g., non-algebraic torsion via Atiyah-Hirzebruch $Sq^3$, or non-projective Kähler degeneration), the negative certificate is cryptographically signed and stored in semantic memory. No subagent can ever repeat that failed line of attack. |
| **3. Policy-as-Code (OPA)** | Encodes our **5 Hodge Verification Gates** into Open Policy Agent rules. Any proposed lemma or theorem that lacks projectivity, confuses $\mathbb{Z}$ with $\mathbb{Q}$, or leaps from currents to varieties without support proof is blocked at the infrastructure level. |
| **4. Cloud-Scale Moduli Exploration** | Leverages Google Cloud (Vertex AI, Cloud Run, and BigQuery) to run parallel counterfactual simulations and period calculations across thousands of moduli points in milliseconds. |
| **5. Dual-Custody Approval** | Prevents premature or false claims. No agent can alter `PROBLEM_IDENTITY_REGISTER.yaml` or promote a proof claim without explicit dual-custody cryptographic sign-off from the Lead Researcher. |

---

## 3. Where and How to Integrate Project Chrysalis into the Workspace

Project Chrysalis is integrated across three concrete layers:

```
┌───────────────────────────────────────────────────────────────────────────┐
│  L5: GOVERNANCE & DUAL CUSTODY                                            │
│      • Cloud KMS & Binary Auth: Signs all mathematical certificates        │
│      • Dual-Custody Approval Token: Required for state promotion          │
│      • Maps to: governance/PROJECT_STATE.yaml & GOVERNANCE.md             │
├───────────────────────────────────────────────────────────────────────────┤
│  L3 / L4: POLICY-AS-CODE (OPA)                                            │
│      • Enforces the 5 Hodge Verification Gates via OPA rego rules         │
│      • Maps to: policies/hodge_gates.rego & ASSUMPTION_LEDGER.yaml        │
├───────────────────────────────────────────────────────────────────────────┤
│  L1 / L2: AGENT RUNTIME & DYNAMIC TOOL MOUNTING                           │
│      • Isolated sandboxed execution (Worker -> Reviewer -> Acceptor)      │
│      • Dynamic synthesis of symbolic geometry scripts (SymPy / SageMath)   │
│      • Maps to: toolkit/chrysalis_bridge.py & reference/universal_gov/    │
└───────────────────────────────────────────────────────────────────────────┘
```

### Concrete Placement in Directory Structure:
1. **`policies/hodge_gates.rego`**: Open Policy Agent policy file defining the mathematical tripwires as executable cloud policies.
2. **`toolkit/chrysalis_bridge.py`**: Python adapter connecting the local Python research toolkit (`hodge_diamond.py`, `shioda_fermat.py`, `hp_linalg.py`) to the Chrysalis Agent Development Kit (ADK) event bus and Cloud KMS signing.
3. **`docs/05_project_chrysalis_integration.md`**: This master architectural specification.
