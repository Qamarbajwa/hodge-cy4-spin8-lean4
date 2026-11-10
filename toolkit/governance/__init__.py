"""MATH-GOV v0.6 Governance OS runtime and verification engine.

Provides fail-closed mathematical step/obligation verification, durable exact-byte
prompt/result ledgers, Lean 4 step verification runners, graph indexing and dependency tracking.
"""

from .event_ledger import append as append_event, verify as verify_event_ledger
from .math_step_engine import audit as audit_step_case, index_graph
from .step_verifier import check_formal_step
from .lean_step_runner import check_step as check_lean_step
