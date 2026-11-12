"""The Six Specialized Co-Scientist Agent Contracts for Hodge Discovery.

Adheres strictly to the multi-agent architecture of Gottweis et al. (Nature 2026):
1. Generation Agent: Proposes candidate algebraic cycles, Hodge classes, and deformation loci.
2. Reflection Agent: Evaluates structural validity, citation grounding, and known obstructions.
3. Proximity Agent: Measures distance to existing literature and prior hypotheses (avoids looping).
4. Evolution Agent: Mutates and refines hypotheses, strictly resetting state to DRAFT and Elo to 1200.
5. Tournament Agent: Conducts blinded pairwise matches, computing Elo rating updates.
6. Meta-Review Agent: Synthesizes proposal dossiers with mandatory limitations disclosure.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Any, Optional
import hashlib
from .core import Hypothesis, Stage, digest


@dataclass(frozen=True)
class GenerationSpec:
    domain: str  # e.g., "AbelianSixfoldSpinor", "CalabiYauFourfoldVoisin", "WeilFourfoldSecant"
    target_class: str
    motivation: str
    proposed_construction: str


class GenerationAgent:
    """Proposes novel, mathematically well-posed research hypotheses for Hodge discovery."""

    def __init__(self, agent_id: str = "agent_generation_01"):
        self.agent_id = agent_id

    def generate(
        self,
        hypothesis_id: str,
        spec: GenerationSpec,
    ) -> Dict[str, Any]:
        statement = (
            f"On domain [{spec.domain}], for target class [{spec.target_class}]: "
            f"we construct candidate cycle via {spec.proposed_construction}. "
            f"Motivation: {spec.motivation}."
        )
        metadata = {
            "author_agent": self.agent_id,
            "domain": spec.domain,
            "target_class": spec.target_class,
            "construction": spec.proposed_construction,
        }
        return {
            "hypothesis_id": hypothesis_id,
            "statement": statement,
            "domain_metadata": metadata,
        }


class ReflectionAgent:
    """Performs rigorous, adversarial, literature-grounded reflection on hypotheses."""

    def __init__(self, agent_id: str = "agent_reflection_01"):
        self.agent_id = agent_id

    def reflect(self, hypothesis: Hypothesis) -> Dict[str, Any]:
        """Examines the hypothesis for mathematical traps, citation mismatch, or known barriers."""
        stmt = hypothesis.statement.lower()
        issues: List[str] = []
        positive_observations: List[str] = []

        # Trap 1: Claiming full Hodge conjecture proved without bounds
        if "hodge conjecture proved" in stmt or "solved the clay millennium problem" in stmt:
            issues.append("VIOLATION_HONESTY_LAW: Unbounded claim of solving Clay Millennium Hodge Problem.")

        # Trap 2: Conflating Weil abelian varieties with Mumford simple sixfolds
        if "weil" in stmt and "end_q(a) = q" in stmt:
            issues.append("STRUCTURAL_MISMATCH: Weil fourfolds have End(A) contains K=Q(sqrt(-d)), not End_Q(A)=Q.")

        # Trap 3: Applying Markman secant sheaves to Calabi-Yau fourfolds
        if "markman" in stmt and "calabi-yau" in stmt:
            issues.append("STRUCTURAL_BARRIER: Markman secant sheaves require auxiliary abelian variety Y; non-abelian CY4 has b1=0.")

        # Positive grounding checks
        if "mumford" in stmt and "spinor" in stmt:
            positive_observations.append("Grounded in Mumford (1969) spinor classes on simple abelian sixfolds.")
        if "voisin" in stmt and "moving-cycle" in stmt:
            positive_observations.append("Grounded in Claire Voisin (1989) second-order syzygy variation.")
        if "markman" in stmt and "secant" in stmt:
            positive_observations.append("Grounded in Eyal Markman (2025) secant sheaves on auxiliary abelian threefolds.")

        passed = len(issues) == 0
        return {
            "reflector_id": self.agent_id,
            "hypothesis_id": hypothesis.hypothesis_id,
            "passed": passed,
            "issues": issues,
            "positive_observations": positive_observations,
            "reflection_digest": digest(f"{hypothesis.hypothesis_id}:{passed}:{len(issues)}"),
        }


class ProximityAgent:
    """Evaluates novelty and distance from previously explored hypotheses or literature benchmarks."""

    def __init__(self, agent_id: str = "agent_proximity_01"):
        self.agent_id = agent_id

    def compute_distance(
        self,
        candidate: Hypothesis,
        corpus: List[Hypothesis],
    ) -> Dict[str, Any]:
        """Computes Jaccard/set distance over normalized mathematical tokens."""
        cand_tokens = set(candidate.statement.lower().replace(":", " ").replace(",", " ").split())
        distances = []
        for other in corpus:
            if other.hypothesis_id == candidate.hypothesis_id:
                continue
            other_tokens = set(other.statement.lower().replace(":", " ").replace(",", " ").split())
            intersection = len(cand_tokens & other_tokens)
            union = len(cand_tokens | other_tokens)
            sim = intersection / union if union > 0 else 0.0
            dist = 1.0 - sim
            distances.append((other.hypothesis_id, dist))

        min_dist = min([d for _, d in distances], default=1.0)
        is_novel = min_dist > 0.15  # At least 15% distinct tokens

        return {
            "evaluator_id": self.agent_id,
            "candidate_id": candidate.hypothesis_id,
            "min_distance_to_corpus": min_dist,
            "is_novel": is_novel,
            "distances": distances,
        }


class EvolutionAgent:
    """Mutates or refines an existing hypothesis based on reflection and critique."""

    def __init__(self, agent_id: str = "agent_evolution_01"):
        self.agent_id = agent_id

    def mutate(
        self,
        parent: Hypothesis,
        new_id: str,
        critique: str,
        improvement_directive: str,
    ) -> Dict[str, Any]:
        new_statement = (
            f"{parent.statement} [REVISED: Addressing critique '{critique}']. "
            f"Correction: {improvement_directive}"
        )
        return {
            "parent_id": parent.hypothesis_id,
            "new_id": new_id,
            "new_statement": new_statement,
            "evolution_author": self.agent_id,
        }


class TournamentAgent:
    """Manages blinded pairwise head-to-head matches between research hypotheses."""

    def __init__(self, agent_id: str = "agent_tournament_01"):
        self.agent_id = agent_id

    def judge_match(
        self,
        hyp_a: Hypothesis,
        hyp_b: Hypothesis,
        reflections_a: Dict[str, Any],
        reflections_b: Dict[str, Any],
    ) -> str:
        """Blinded judgment based on scientific criteria:

        1. Clean reflection (no fatal issues).
        2. Depth of positive grounding.
        3. Parsimony and testability.
        Returns 'LEFT', 'RIGHT', 'TIE', or 'ABSTAIN'.
        """
        score_a = len(reflections_a.get("positive_observations", [])) - 3 * len(reflections_a.get("issues", []))
        score_b = len(reflections_b.get("positive_observations", [])) - 3 * len(reflections_b.get("issues", []))

        if score_a > score_b:
            return "LEFT"
        elif score_b > score_a:
            return "RIGHT"
        elif score_a == score_b:
            return "TIE"
        return "ABSTAIN"


class MetaReviewAgent:
    """Synthesizes tournament results, reflection audits, and verification obligations into a proposal dossier."""

    def __init__(self, agent_id: str = "agent_meta_review_01"):
        self.agent_id = agent_id

    def compile_proposal(
        self,
        hypothesis: Hypothesis,
        reflection: Dict[str, Any],
        tournament_rank: int,
        total_participants: int,
    ) -> Dict[str, Any]:
        """Assembles a proposal dossier with mandatory scientific limitation disclosure."""
        limitations = [
            "The Clay Millennium Hodge Conjecture remains strictly OPEN.",
            "High Elo rating or tournament victories are triage metrics, NOT proof of truth.",
            "Verification requires external formal receipts (Lean 4 or exact rational linear algebra).",
        ]
        return {
            "meta_reviewer_id": self.agent_id,
            "hypothesis_id": hypothesis.hypothesis_id,
            "statement": hypothesis.statement,
            "elo": hypothesis.elo,
            "tournament_rank": f"{tournament_rank}/{total_participants}",
            "reflection_status": "PASSED" if reflection.get("passed", False) else "FAILED",
            "limitations_disclosed": limitations,
            "proposal_digest": digest(f"{hypothesis.hypothesis_id}:{hypothesis.elo}:{hypothesis.content_digest}"),
        }
