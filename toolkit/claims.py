"""Claim lifecycle + theorem triad (generalised from the RH project's Mathematical Research Constitution v1.0).

Rules enforced in code:
  * 13 ordered states, no skipping (Constitution sec. 2).
  * Correctness / Novelty / Significance are separate fields, never collapsed (sec. 3).
  * Writer may not be the verifier (Independence Law).
  * An UNJUSTIFIED assumption blocks promotion (Assumption Drift Monitor).
  * Numerical evidence alone can never move a claim past SUPPORTED_CONJECTURE.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import IntEnum


class State(IntEnum):
    IDEA = 1
    CONJECTURE = 2
    SUPPORTED_CONJECTURE = 3
    CANDIDATE_LEMMA = 4
    CANDIDATE_THEOREM = 5
    INTERNALLY_CHECKED = 6
    INDEPENDENTLY_VERIFIED = 7
    FORMALLY_VERIFIED = 8
    HUMAN_UNDERSTOOD = 9
    NOVELTY_CHECKED = 10
    EXTERNAL_EXPERT_REVIEW = 11
    COMMUNITY_ACCEPTED = 12
    CANONICALIZED = 13


assert len(State) == 13  # State Count Invariant

CORRECTNESS = {"UNCHECKED", "INTERNALLY_CHECKED", "VERIFIED", "PROVED_CONDITIONAL", "FALSE_OR_COUNTEREXAMPLE"}
NOVELTY = {"UNAUDITED", "KNOWN", "KNOWN_EQUIVALENT", "KNOWN_STRONGER", "POSSIBLY_NEW", "AUTHENTICATED_NOVEL"}
SIGNIFICANCE = {"UNASSESSED", "TECHNICAL_LEMMA", "STRUCTURAL_BRIDGE", "MAJOR_THEOREM", "FOUNDATIONAL_BREAKTHROUGH"}
ASSUMPTION_KINDS = {"ORIGINAL", "DERIVED", "KNOWN_CONSEQUENCE", "TEMPORARY", "ADDITIONAL", "UNJUSTIFIED"}
EVIDENCE_KINDS = {"NUMERICAL", "SYMBOLIC", "PROOF", "FORMAL"}


class GovernanceError(Exception):
    pass


@dataclass
class Claim:
    claim_id: str
    statement: str                      # frozen canonical statement (Identity Law)
    state: State = State.IDEA
    correctness: str = "UNCHECKED"
    novelty: str = "UNAUDITED"
    significance: str = "UNASSESSED"
    assumptions: dict = field(default_factory=dict)   # name -> kind
    writer_id: str = ""
    history: list = field(default_factory=list)       # permanent, never deleted (Memory Law)

    def __post_init__(self):
        self._canon = self.statement

    # ---- identity law -------------------------------------------------
    def assert_identity(self, statement: str):
        if statement != self._canon:
            raise GovernanceError("Identity Law: statement drifted; reclassify as a NEW claim instead.")

    # ---- assumptions --------------------------------------------------
    def add_assumption(self, name: str, kind: str):
        if kind not in ASSUMPTION_KINDS:
            raise GovernanceError(f"unknown assumption kind {kind}")
        self.assumptions[name] = kind
        self.history.append(("assumption", name, kind))

    # ---- promotion ----------------------------------------------------
    def promote(self, to: State, *, evidence: str, verifier_id: str = ""):
        if evidence not in EVIDENCE_KINDS:
            raise GovernanceError(f"evidence must be one of {EVIDENCE_KINDS}")
        if to != self.state + 1:
            raise GovernanceError(f"no skipping: {self.state.name} -> {to.name} not allowed")
        if "UNJUSTIFIED" in self.assumptions.values():
            raise GovernanceError("UNJUSTIFIED assumption blocks promotion")
        if self.correctness == "FALSE_OR_COUNTEREXAMPLE":
            raise GovernanceError("claim is falsified; open a new claim")
        if to > State.SUPPORTED_CONJECTURE and evidence == "NUMERICAL":
            raise GovernanceError("Truth Law: numerical evidence is heuristic support, never proof")
        if to >= State.INDEPENDENTLY_VERIFIED and (not verifier_id or verifier_id == self.writer_id):
            raise GovernanceError("Independence Law: verifier must differ from writer")
        self.history.append(("promote", self.state.name, to.name, evidence, verifier_id))
        self.state = to

    def falsify(self, counterexample: str):
        self.correctness = "FALSE_OR_COUNTEREXAMPLE"
        self.history.append(("falsified", counterexample))

    def set_triad(self, *, correctness=None, novelty=None, significance=None):
        for v, allowed, nm in ((correctness, CORRECTNESS, "correctness"),
                               (novelty, NOVELTY, "novelty"),
                               (significance, SIGNIFICANCE, "significance")):
            if v is not None:
                if v not in allowed:
                    raise GovernanceError(f"bad {nm}: {v}")
                setattr(self, nm, v)
