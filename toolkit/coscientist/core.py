"""Deterministic fail-closed research-gate kernel for Co-Scientist Dark Factory OS.

Adapted from COSCIENTIST_DF_v0_1 reference kernel and bound to MATH-GOV v0.6 OS:
- Enforces strict separation between narrative/Elo ranking and external formal verification.
- Enforces strict caller-authority roles (policy_service, tournament_service, independent_verification_service).
- Blocks non-adjacent stage transitions, backwards jumps, self-verification, and ungrounded verification.
- Enforces quarantine revocation with no bypass.
"""

from __future__ import annotations
from dataclasses import dataclass, field, replace
from enum import Enum
from hashlib import sha256
from typing import Dict, List, Tuple, Optional, Any


class Denied(ValueError):
    """Fail-closed gate denial."""


class Stage(str, Enum):
    DRAFT = "DRAFT"
    SCREENED = "SCREENED"
    GROUNDED = "GROUNDED"
    REVIEWED = "REVIEWED"
    ELIGIBLE = "ELIGIBLE"
    RANKED = "RANKED"
    PROPOSAL_READY = "PROPOSAL_READY"
    QUARANTINED = "QUARANTINED"


ORDER = (
    Stage.DRAFT,
    Stage.SCREENED,
    Stage.GROUNDED,
    Stage.REVIEWED,
    Stage.ELIGIBLE,
    Stage.RANKED,
    Stage.PROPOSAL_READY,
)


@dataclass(frozen=True)
class Hypothesis:
    hypothesis_id: str
    statement: str
    content_digest: str
    parent_ids: Tuple[str, ...] = ()
    stage: Stage = Stage.DRAFT
    evidence_state: str = "UNCHECKED"
    formal_state: str = "UNTESTED"
    empirical_state: str = "NOT_APPLICABLE"
    elo: float = 1200.0
    domain_metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class GateSignals:
    goal_safe: bool = False
    hypothesis_safe: bool = False
    source_verified: bool = False
    reflection_completed: bool = False
    tournament_assessed: bool = False
    report_discloses_limits: bool = False


@dataclass(frozen=True)
class VerificationReceipt:
    hypothesis_id: str
    exact_target_digest: str
    evidence_digest: str
    claim_type: str  # MATH_PROOF or EMPIRICAL_REPLICATION
    builder_identity: str
    verifier_identity: str
    independently_verified: bool
    protected_suite_passed: bool
    semantic_review_passed: bool
    verifier_authority_bound: bool
    lean_theorem_ref: Optional[str] = None
    allowed_axioms_only: bool = True


def digest(text: str) -> str:
    """Computes canonical SHA-256 hex digest of UTF-8 text."""
    return sha256(text.encode("utf-8")).hexdigest()


class ResearchGateKernel:
    """Fail-closed state machine governing research candidate progression and independent verification."""

    def __init__(self) -> None:
        self._items: Dict[str, Hypothesis] = {}
        self._verified: Dict[str, VerificationReceipt] = {}
        self._matches: List[Tuple[str, str, str]] = []
        self.audit: List[str] = []

    def get(self, hypothesis_id: str) -> Hypothesis:
        try:
            return self._items[hypothesis_id]
        except KeyError as e:
            raise Denied("UNKNOWN_HYPOTHESIS") from e

    def list_hypotheses(self) -> List[Hypothesis]:
        return list(self._items.values())

    def get_receipt(self, hypothesis_id: str) -> Optional[VerificationReceipt]:
        return self._verified.get(hypothesis_id)

    def add(
        self,
        hypothesis_id: str,
        statement: str,
        parent_ids: Tuple[str, ...] = (),
        domain_metadata: Optional[Dict[str, Any]] = None,
    ) -> Hypothesis:
        if not hypothesis_id or not statement.strip() or hypothesis_id in self._items:
            raise Denied("INVALID_OR_DUPLICATE_CANDIDATE")
        if len(set(parent_ids)) != len(parent_ids) or hypothesis_id in parent_ids:
            raise Denied("INVALID_LINEAGE")
        for parent_id in parent_ids:
            self.get(parent_id)
        candidate = Hypothesis(
            hypothesis_id=hypothesis_id,
            statement=statement,
            content_digest=digest(statement),
            parent_ids=parent_ids,
            domain_metadata=dict(domain_metadata) if domain_metadata else {},
        )
        self._items[hypothesis_id] = candidate
        self.audit.append(f"ADD {hypothesis_id} {candidate.content_digest}")
        return candidate

    def evolve(
        self,
        parent_id: str,
        new_id: str,
        new_statement: str,
        domain_metadata: Optional[Dict[str, Any]] = None,
    ) -> Hypothesis:
        self.get(parent_id)
        # Crucial invariant: child starts fresh in DRAFT with reset Elo (1200.0) and zero proof inheritance.
        return self.add(new_id, new_statement, (parent_id,), domain_metadata=domain_metadata)

    def advance(
        self,
        hypothesis_id: str,
        target: Stage,
        signals: GateSignals,
        *,
        caller: str,
    ) -> Hypothesis:
        item = self.get(hypothesis_id)
        if caller != "policy_service":
            raise Denied("ONLY_POLICY_SERVICE_CAN_ADVANCE")
        if item.stage not in ORDER or target not in ORDER:
            raise Denied("QUARANTINE_OR_UNKNOWN_STAGE")
        pos = ORDER.index(item.stage)
        if pos + 1 >= len(ORDER) or target != ORDER[pos + 1]:
            raise Denied("NON_ADJACENT_OR_REVERSE_TRANSITION")
        if not (signals.goal_safe and signals.hypothesis_safe):
            raise Denied("SAFETY_NOT_ALLOWED")
        if (
            target in (Stage.GROUNDED, Stage.REVIEWED, Stage.ELIGIBLE, Stage.RANKED, Stage.PROPOSAL_READY)
            and not signals.source_verified
        ):
            raise Denied("SOURCE_PROVENANCE_UNVERIFIED")
        if (
            target in (Stage.REVIEWED, Stage.ELIGIBLE, Stage.RANKED, Stage.PROPOSAL_READY)
            and not signals.reflection_completed
        ):
            raise Denied("SOURCE_GROUNDED_REFLECTION_MISSING")
        if target in (Stage.RANKED, Stage.PROPOSAL_READY) and not signals.tournament_assessed:
            raise Denied("TOURNAMENT_EVIDENCE_MISSING")
        if target == Stage.PROPOSAL_READY and not signals.report_discloses_limits:
            raise Denied("REPORT_LIMITATIONS_MISSING")

        updated = replace(item, stage=target)
        self._items[hypothesis_id] = updated
        self.audit.append(f"ADVANCE {hypothesis_id} {target.value}")
        return updated

    def quarantine(self, hypothesis_id: str, *, caller: str, reason: str = "") -> Hypothesis:
        if caller != "policy_service":
            raise Denied("ONLY_POLICY_SERVICE_CAN_QUARANTINE")
        updated = replace(
            self.get(hypothesis_id),
            stage=Stage.QUARANTINED,
            formal_state="REVOKED",
            empirical_state="REVOKED",
        )
        self._items[hypothesis_id] = updated
        self._verified.pop(hypothesis_id, None)
        suffix = f" REASON={reason}" if reason else ""
        self.audit.append(f"QUARANTINE {hypothesis_id}{suffix}")
        return updated

    def record_match(
        self,
        left_id: str,
        right_id: str,
        outcome: str,
        *,
        caller: str,
    ) -> Tuple[float, float]:
        if caller != "tournament_service":
            raise Denied("UNAUTHORIZED_TOURNAMENT_WRITER")
        if left_id == right_id or outcome not in ("LEFT", "RIGHT", "TIE", "ABSTAIN"):
            raise Denied("INVALID_MATCH")
        a, b = self.get(left_id), self.get(right_id)
        if a.stage not in (Stage.ELIGIBLE, Stage.RANKED) or b.stage not in (Stage.ELIGIBLE, Stage.RANKED):
            raise Denied("UNSCREENED_MATCH_PARTICIPANT")
        if outcome == "ABSTAIN":
            self._matches.append((left_id, right_id, outcome))
            return a.elo, b.elo
        score_a = 1.0 if outcome == "LEFT" else 0.0 if outcome == "RIGHT" else 0.5
        expected_a = 1 / (1 + 10 ** ((b.elo - a.elo) / 400))
        new_a = a.elo + 32 * (score_a - expected_a)
        new_b = b.elo - 32 * (score_a - expected_a)
        self._items[left_id] = replace(a, elo=new_a)
        self._items[right_id] = replace(b, elo=new_b)
        self._matches.append((left_id, right_id, outcome))
        self.audit.append(f"MATCH {left_id} {right_id} {outcome}")
        return new_a, new_b

    def verify_claim(self, receipt: VerificationReceipt, *, caller: str) -> str:
        item = self.get(receipt.hypothesis_id)
        if caller != "independent_verification_service":
            raise Denied("WRONG_VERIFICATION_AUTHORITY")
        if item.stage in (Stage.DRAFT, Stage.QUARANTINED):
            raise Denied("UNSCREENED_OR_QUARANTINED_CANDIDATE")
        if item.content_digest != receipt.exact_target_digest:
            raise Denied("EXACT_TARGET_MISMATCH")
        if not receipt.evidence_digest or len(receipt.evidence_digest) != 64:
            raise Denied("MISSING_EVIDENCE_DIGEST")
        if not receipt.verifier_identity or receipt.verifier_identity == receipt.builder_identity:
            raise Denied("SELF_VERIFICATION_FORBIDDEN")
        if not (
            receipt.independently_verified
            and receipt.protected_suite_passed
            and receipt.semantic_review_passed
            and receipt.verifier_authority_bound
            and receipt.allowed_axioms_only
        ):
            raise Denied("VERIFICATION_PREREQUISITES_MISSING")
        if receipt.claim_type not in ("MATH_PROOF", "EMPIRICAL_REPLICATION"):
            raise Denied("UNSUPPORTED_CLAIM_TYPE")

        self._verified[item.hypothesis_id] = receipt
        state = "APPROVED_PROOF" if receipt.claim_type == "MATH_PROOF" else "INDEPENDENTLY_REPLICATED"
        if receipt.claim_type == "MATH_PROOF":
            item = replace(item, formal_state=state, evidence_state="VERIFIED_IMMUTABLE")
        else:
            item = replace(item, empirical_state=state, evidence_state="VERIFIED_IMMUTABLE")
        self._items[item.hypothesis_id] = item
        self.audit.append(f"CLAIM_VERIFIED {item.hypothesis_id} {state} VERIFIER={receipt.verifier_identity}")
        return state

    def proposal_is_verified(self, hypothesis_id: str) -> bool:
        """Proposal progression or high Elo is never a shortcut to external verification."""
        return hypothesis_id in self._verified
