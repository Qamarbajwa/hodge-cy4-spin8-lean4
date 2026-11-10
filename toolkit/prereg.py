"""Preregistered grid runner: decision rules are fixed in JSON BEFORE computation (see templates/PREREGISTRATION.template.json).

Workflow: validate -> gates (reference fixture, predecessor calibration) -> grid -> outcome -> seal.
The runner refuses to produce an outcome if a gate failed (fail-closed)."""
from __future__ import annotations
import json
import mpmath as mp
from . import integrity


def load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def validate(p: dict):
    need = ["protocol_id", "oracle", "precision_requirements", "primary_grid", "decision_rules",
            "primary_statistic", "contamination_declarations"]
    miss = [k for k in need if k not in p]
    if miss:
        raise ValueError(f"preregistration missing: {miss}")
    if not p["primary_grid"]:
        raise ValueError("empty grid")
    return True


def classify(n_a_lower: int, n_b_lower: int, n_unresolved: int, n_total: int) -> str:
    """Generic 4-outcome rule from RH-T056R8R3."""
    if n_unresolved > 0:
        return "Outcome_D_INCONCLUSIVE"
    if n_a_lower == n_total:
        return "Outcome_A_B_DISFAVORED_EVERYWHERE"
    if n_b_lower == n_total:
        return "Outcome_C_B_FAVORED_EVERYWHERE_REQUIRES_REPLICATION"
    return "Outcome_B_NONUNIVERSAL"


def run(prereg: dict, gate_fixture, gate_calibration, cell_eval, out_path: str, script_path: str | None = None):
    """gate_fixture() -> bool ; gate_calibration() -> bool ; cell_eval(cell) -> (lam_A, lam_B)."""
    validate(prereg)
    res = {"protocol_id": prereg["protocol_id"], "gates": {}, "cells": []}
    res["gates"]["fixture"] = bool(gate_fixture())
    res["gates"]["calibration"] = bool(gate_calibration())
    if not all(res["gates"].values()):
        res["outcome"] = "GATE_FAIL_NO_OUTCOME"
    else:
        from .hp_linalg import decide_ratio
        a = b = u = 0
        for cell in prereg["primary_grid"]:
            lamA, lamB = cell_eval(cell)
            d = decide_ratio(lamB, lamA)
            a += d == "A_LOWER"; b += d == "B_LOWER"; u += d == "NUMERICALLY_UNRESOLVED"
            res["cells"].append({"cell": cell, "lam_A": mp.nstr(lamA, 60), "lam_B": mp.nstr(lamB, 60),
                                 "R": mp.nstr(lamB / lamA, 25) if lamA != 0 else "inf", "decision": d})
        res["outcome"] = classify(a, b, u, len(prereg["primary_grid"]))
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(res, f, indent=2)
    res["seal"] = integrity.seal(out_path, script_path)
    return res
