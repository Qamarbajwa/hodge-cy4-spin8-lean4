#!/usr/bin/env python3
"""
research/audits/audit_run_verifier_001.py

Runner used by RH-CERTIFICATION-PIPELINE-AUDIT-AND-REPAIR-001 (Phase 1).

Loads ONE historical interval verifier from a given worktree (checked out at the
verifier's own writer commit, so its governance revision/SHA guards pass unmodified),
wraps `build_certified_hybrid_matrices` to record every live eigenvalue computation,
runs `main()` in the requested mode, and writes a JSON capture.

The verifier source is NOT modified. Only a call-recording wrapper is installed
on the module attribute before main() runs.

Usage:
    python audit_run_verifier_001.py <worktree> <script_relpath> <mode: default|recompute> <out_json>
"""
import importlib.util
import io
import json
import os
import sys
import time
import traceback
import contextlib


def main():
    worktree, script_rel, mode, out_json = sys.argv[1:5]
    worktree = os.path.abspath(worktree)
    os.chdir(worktree)
    sys.path.insert(0, worktree)
    sys.path.insert(0, os.path.join(worktree, "scripts"))

    script_path = os.path.join(worktree, script_rel)
    spec = importlib.util.spec_from_file_location("audited_verifier", script_path)
    mod = importlib.util.module_from_spec(spec)

    captures = []
    record = {
        "script": script_rel,
        "mode": mode,
        "worktree": worktree,
        "live_calls": captures,
        "exit_status": None,
        "exception": None,
        "stdout_tail": None,
        "elapsed_s": None,
    }

    t0 = time.time()
    buf = io.StringIO()
    try:
        spec.loader.exec_module(mod)
        orig = getattr(mod, "build_certified_hybrid_matrices", None)
        if orig is None:
            raise RuntimeError("build_certified_hybrid_matrices not found in verifier module")

        def wrapped(L_val, *a, **kw):
            t = time.time()
            res = orig(L_val, *a, **kw)
            entry = {"L": float(L_val), "dt_s": time.time() - t}
            if isinstance(res, dict):
                for k in ("mu1_plus", "mu2_plus", "mu1_minus", "mu2_minus"):
                    if k in res:
                        entry[k] = float(res[k])
            captures.append(entry)
            return res

        mod.build_certified_hybrid_matrices = wrapped
        sys.argv = [script_path] + (["--recompute"] if mode == "recompute" else [])
        with contextlib.redirect_stdout(buf):
            mod.main()
        record["exit_status"] = "OK"
    except SystemExit as e:
        record["exit_status"] = f"SYSTEM_EXIT:{e.code}"
    except AssertionError as e:
        record["exit_status"] = "ASSERTION_FAILED"
        record["exception"] = f"AssertionError: {e}\n{traceback.format_exc()}"
    except Exception as e:  # noqa: BLE001
        record["exit_status"] = "EXCEPTION"
        record["exception"] = f"{type(e).__name__}: {e}\n{traceback.format_exc()}"
    record["elapsed_s"] = time.time() - t0
    out = buf.getvalue()
    record["stdout_tail"] = out[-6000:]

    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(record, f, indent=2)
    print(f"{script_rel} [{mode}] -> {record['exit_status']} ({record['elapsed_s']:.1f}s, {len(captures)} live calls)")


if __name__ == "__main__":
    main()
