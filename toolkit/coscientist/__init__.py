"""Co-Scientist Dark Factory Autonomous Scientific Research Engine for Hodge Conjecture Discovery.

Based on Gottweis et al. (Nature 2026) multi-agent architecture bound to MATH-GOV v0.6 OS.
Provides fail-closed state machines, 6 specialized agent contracts, blinded Elo tournaments,
and exact Lean 4 / rational algebraic verification adapters.
"""

from .core import (
    Denied,
    Stage,
    Hypothesis,
    GateSignals,
    VerificationReceipt,
    ResearchGateKernel,
    digest,
)
from .agents import (
    GenerationAgent,
    ReflectionAgent,
    ProximityAgent,
    EvolutionAgent,
    TournamentAgent,
    MetaReviewAgent,
)
from .math_adapter import (
    MathProofAdapter,
    LeanVerificationResult,
)
from .dark_factory_loop import (
    DarkFactoryEngine,
    ResearchGoal,
)

__all__ = [
    "Denied",
    "Stage",
    "Hypothesis",
    "GateSignals",
    "VerificationReceipt",
    "ResearchGateKernel",
    "digest",
    "GenerationAgent",
    "ReflectionAgent",
    "ProximityAgent",
    "EvolutionAgent",
    "TournamentAgent",
    "MetaReviewAgent",
    "MathProofAdapter",
    "LeanVerificationResult",
    "DarkFactoryEngine",
    "ResearchGoal",
]
