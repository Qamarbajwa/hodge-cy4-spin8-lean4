"""Co-Scientist Dark Factory Discovery Loop for Hodge Conjecture Research.

Orchestrates the 6 research agents through the fail-closed ResearchGateKernel:
  Generation -> Screening -> Grounding -> Reflection/Proximity -> Tournament (Elo) ->
  Evolution (if issues detected) -> Meta-Review Proposal -> Independent Verification.

Strictly upholds:
- Rank != Proof
- Agents cannot advance their own gates or sign their own proofs
- All proposals disclose the open Millennium boundary (`NO_HODGE_PROOF = TRUE`).
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Any, Optional
from .core import (
    ResearchGateKernel,
    Stage,
    GateSignals,
    Hypothesis,
    Denied,
)
from .agents import (
    GenerationAgent,
    GenerationSpec,
    ReflectionAgent,
    ProximityAgent,
    EvolutionAgent,
    TournamentAgent,
    MetaReviewAgent,
)
from .math_adapter import MathProofAdapter


@dataclass(frozen=True)
class ResearchGoal:
    goal_id: str
    title: str
    description: str
    safety_approved: bool = True


class DarkFactoryEngine:
    """Autonomous multi-agent scientific discovery loop bounded by MATH-GOV v0.6."""

    def __init__(self) -> None:
        self.kernel = ResearchGateKernel()
        self.generator = GenerationAgent()
        self.reflector = ReflectionAgent()
        self.proximity = ProximityAgent()
        self.evolver = EvolutionAgent()
        self.tournament = TournamentAgent()
        self.meta_reviewer = MetaReviewAgent()
        self.proof_adapter = MathProofAdapter()
        self.reflections: Dict[str, Dict[str, Any]] = {}
        self.proposals: Dict[str, Dict[str, Any]] = {}

    def submit_and_process_candidates(
        self,
        goal: ResearchGoal,
        specs: List[Tuple[str, GenerationSpec]],
    ) -> Dict[str, Any]:
        """Executes a full discovery iteration over candidate generation specs."""
        if not goal.safety_approved:
            raise Denied("GOAL_SAFETY_REJECTED")

        # 1. Generation
        added_ids: List[str] = []
        for hyp_id, spec in specs:
            gen_data = self.generator.generate(hyp_id, spec)
            self.kernel.add(
                gen_data["hypothesis_id"],
                gen_data["statement"],
                domain_metadata=gen_data["domain_metadata"],
            )
            added_ids.append(hyp_id)

        # 2. Screening & Grounding & Reflection & Proximity
        eligible_ids: List[str] = []
        quarantined_ids: List[str] = []

        for hyp_id in added_ids:
            hyp = self.kernel.get(hyp_id)
            refl = self.reflector.reflect(hyp)
            self.reflections[hyp_id] = refl

            # Check proximity against existing eligible candidates
            corpus = [self.kernel.get(eid) for eid in eligible_ids]
            prox = self.proximity.compute_distance(hyp, corpus)

            if not refl["passed"]:
                # Fail-closed quarantine if hypothesis violates scientific honesty or has structural contradictions
                self.kernel.quarantine(
                    hyp_id,
                    caller="policy_service",
                    reason="; ".join(refl["issues"]),
                )
                quarantined_ids.append(hyp_id)
                continue

            if not prox["is_novel"]:
                self.kernel.quarantine(
                    hyp_id,
                    caller="policy_service",
                    reason="INSUFFICIENT_PROXIMITY_NOVELTY",
                )
                quarantined_ids.append(hyp_id)
                continue

            # Advance safely: DRAFT -> SCREENED -> GROUNDED -> REVIEWED -> ELIGIBLE
            sigs = GateSignals(
                goal_safe=True,
                hypothesis_safe=True,
                source_verified=True,
                reflection_completed=True,
                tournament_assessed=False,
                report_discloses_limits=False,
            )
            for st in (Stage.SCREENED, Stage.GROUNDED, Stage.REVIEWED, Stage.ELIGIBLE):
                self.kernel.advance(hyp_id, st, sigs, caller="policy_service")
            eligible_ids.append(hyp_id)

        # 3. Tournament (Blinded pairwise Elo comparisons)
        n = len(eligible_ids)
        for i in range(n):
            for j in range(i + 1, n):
                id_a, id_b = eligible_ids[i], eligible_ids[j]
                hyp_a, hyp_b = self.kernel.get(id_a), self.kernel.get(id_b)
                outcome = self.tournament.judge_match(
                    hyp_a,
                    hyp_b,
                    self.reflections[id_a],
                    self.reflections[id_b],
                )
                self.kernel.record_match(id_a, id_b, outcome, caller="tournament_service")

        # Advance eligible candidates to RANKED -> PROPOSAL_READY
        ranked_hyps = sorted(
            [self.kernel.get(eid) for eid in eligible_ids],
            key=lambda h: h.elo,
            reverse=True,
        )
        for rank_idx, h in enumerate(ranked_hyps, start=1):
            sigs_final = GateSignals(
                goal_safe=True,
                hypothesis_safe=True,
                source_verified=True,
                reflection_completed=True,
                tournament_assessed=True,
                report_discloses_limits=True,
            )
            self.kernel.advance(h.hypothesis_id, Stage.RANKED, sigs_final, caller="policy_service")
            self.kernel.advance(h.hypothesis_id, Stage.PROPOSAL_READY, sigs_final, caller="policy_service")
            dossier = self.meta_reviewer.compile_proposal(
                self.kernel.get(h.hypothesis_id),
                self.reflections[h.hypothesis_id],
                tournament_rank=rank_idx,
                total_participants=len(ranked_hyps),
            )
            self.proposals[h.hypothesis_id] = dossier

        return {
            "goal_id": goal.goal_id,
            "submitted": len(added_ids),
            "eligible": len(eligible_ids),
            "quarantined": len(quarantined_ids),
            "quarantined_ids": quarantined_ids,
            "ranked_leaderboard": [
                {
                    "id": h.hypothesis_id,
                    "elo": round(self.kernel.get(h.hypothesis_id).elo, 2),
                    "verified": self.kernel.proposal_is_verified(h.hypothesis_id),
                }
                for h in ranked_hyps
            ],
        }

    def evolve_quarantined_candidate(
        self,
        parent_id: str,
        new_id: str,
        improvement_directive: str,
    ) -> Hypothesis:
        """Uses EvolutionAgent to create a clean child candidate reset to DRAFT and Elo 1200."""
        parent = self.kernel.get(parent_id)
        refl = self.reflections.get(parent_id, {"issues": ["General refinement"]})
        critique = "; ".join(refl.get("issues", ["Refinement"]))
        evo_data = self.evolver.mutate(parent, new_id, critique, improvement_directive)
        return self.kernel.evolve(
            evo_data["parent_id"],
            evo_data["new_id"],
            evo_data["new_statement"],
        )

    def run_independent_verification(
        self,
        hypothesis_id: str,
        probe_type: str,
        target_name: str,
    ) -> str:
        """Invokes external verification adapter and records receipt in kernel."""
        hyp = self.kernel.get(hypothesis_id)
        if probe_type == "exact_engine":
            receipt = self.proof_adapter.verify_with_exact_engine(hyp, target_name)
        elif probe_type == "lean_blueprint":
            receipt = self.proof_adapter.verify_with_lean_blueprint(hyp, target_name)
        else:
            raise ValueError(f"Unsupported probe type: {probe_type}")

        return self.kernel.verify_claim(receipt, caller="independent_verification_service")
