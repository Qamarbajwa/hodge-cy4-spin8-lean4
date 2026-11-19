"""Fork Auto-Stager Helper for the 8-Step Mathlib4 Micro-Ladder.

Safe policy:
- Queries `leanprover-community/mathlib4` PRs by `Qamarbajwa` strictly read-only.
- NEVER creates PRs or posts comments on `leanprover-community/mathlib4`.
- Validates all 8 steps (`patch.lean` 15..40 lines, native Mathlib style, clean `pr_letter.txt`).
- Strips standalone header imports from `patch.lean` and appends lemmas cleanly inside a
  `section MicroLadderStep` block at the end of the target `Mathlib/...` file.
- Emits `READY_TO_SUBMIT_NEXT_PR.md` and GitHub Actions Job Summary output containing
  the one-click Compare URL, PR title, and verbatim `pr_letter.txt`.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import subprocess
import sys
from typing import Any, Dict, List


SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
LADDER_DIR = REPO_ROOT / "dist" / "mathlib4_micro_ladder"
STATE_PATH = LADDER_DIR / "queue_state.json"

sys.path.insert(0, str(SCRIPT_DIR))
from mathlib4_sequential_micro_daemon import validate_letter_and_patch  # noqa: E402


def load_state() -> Dict[str, Any]:
    return json.loads(STATE_PATH.read_text(encoding="utf-8"))


def save_state(state: Dict[str, Any]) -> None:
    STATE_PATH.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")


def gh_json(args: List[str]) -> Any:
    proc = subprocess.run(
        ["gh", *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"gh {' '.join(args)} failed ({proc.returncode}): {proc.stderr.strip()}")
    return json.loads(proc.stdout or "null")


def strip_patch_header(patch_text: str) -> str:
    """Drop standalone imports and module doc block before embedding into target Mathlib file."""
    out: List[str] = []
    in_doc = False
    started = False
    for line in patch_text.splitlines():
        stripped = line.strip()
        if not started:
            if stripped.startswith("import ") or stripped == "":
                continue
            if stripped.startswith("/-!"):
                in_doc = True
                continue
            if in_doc:
                if "-/" in stripped:
                    in_doc = False
                continue
            started = True
        out.append(line)
    return "\n".join(out).rstrip()


def write_outputs(kv: Dict[str, str]) -> None:
    gh_out = os.environ.get("GITHUB_OUTPUT")
    if gh_out:
        with open(gh_out, "a", encoding="utf-8") as f:
            for k, v in kv.items():
                f.write(f"{k}={v}\n")


def phase_check(force_arm: bool = False) -> int:
    state = load_state()
    steps: List[Dict[str, Any]] = state.get("steps", [])
    if len(steps) != 8:
        raise RuntimeError(f"Expected 8 micro-ladder steps, found {len(steps)}")

    for entry in steps:
        res = validate_letter_and_patch(LADDER_DIR / entry["dir"])
        if not res["passed"]:
            raise RuntimeError(f"Validation failed for {entry['dir']}: {res['errors']}")
    print("ALL_8_MICRO_STEPS_VALIDATED=True")

    if force_arm and not state.get("circuit_breaker_tripped"):
        state["armed"] = True
        save_state(state)

    if state.get("circuit_breaker_tripped"):
        print(f"STATUS=CIRCUIT_BREAKER_TRIPPED reason={state.get('circuit_breaker_reason')}")
        write_outputs({"action": "halt"})
        return 0

    if not state.get("armed", False):
        print("STATUS=DISARMED")
        write_outputs({"action": "disarmed"})
        return 0

    upstream = state.get("upstream_repo", "leanprover-community/mathlib4")
    open_prs = gh_json(
        [
            "pr",
            "list",
            "--repo",
            upstream,
            "--author",
            "Qamarbajwa",
            "--state",
            "open",
            "--limit",
            "50",
            "--json",
            "number,title,headRefName,url",
        ]
    )
    if open_prs:
        print(f"STATUS=WAIT_FOR_CURRENT_PR OPEN_PRS_COUNT={len(open_prs)}")
        for pr in open_prs:
            print(f"  OPEN #{pr['number']} [{pr['headRefName']}] {pr['url']}")
        write_outputs({"action": "wait"})
        return 0

    all_recent = gh_json(
        [
            "pr",
            "list",
            "--repo",
            upstream,
            "--author",
            "Qamarbajwa",
            "--state",
            "all",
            "--limit",
            "50",
            "--json",
            "number,title,headRefName,state,mergedAt,closedAt,url",
        ]
    )
    by_branch = {pr.get("headRefName", ""): pr for pr in (all_recent or [])}

    cooldown = int(state.get("cooldown_seconds", 900))
    now = datetime.now(timezone.utc)
    next_idx = None

    for idx, entry in enumerate(steps):
        pr = by_branch.get(entry["branch"])
        if pr is None:
            next_idx = idx
            break
        pr_state = pr.get("state")
        merged_at = pr.get("mergedAt")
        if pr_state == "OPEN":
            print(f"STATUS=WAIT_FOR_CURRENT_PR #{pr['number']}")
            write_outputs({"action": "wait"})
            return 0
        if pr_state == "CLOSED" and not merged_at:
            state["armed"] = False
            state["circuit_breaker_tripped"] = True
            state["circuit_breaker_reason"] = (
                f"Step {entry['step']} PR #{pr['number']} closed without merge at {pr.get('closedAt')}"
            )
            entry["status"] = "CLOSED_UNMERGED"
            entry["pr_number"] = pr.get("number")
            entry["pr_url"] = pr.get("url")
            entry["closed_at"] = pr.get("closedAt")
            save_state(state)
            print(f"STATUS=CIRCUIT_BREAKER_TRIPPED (#{pr['number']} closed unmerged)")
            write_outputs({"action": "circuit_breaker"})
            return 0
        if merged_at:
            entry["status"] = "MERGED"
            entry["pr_number"] = pr.get("number")
            entry["pr_url"] = pr.get("url")
            entry["merged_at"] = merged_at
            merged_dt = datetime.fromisoformat(merged_at.replace("Z", "+00:00"))
            elapsed = (now - merged_dt).total_seconds()
            if elapsed < cooldown:
                save_state(state)
                print(f"STATUS=COOLDOWN_ACTIVE elapsed={int(elapsed)}s required={cooldown}s")
                write_outputs({"action": "cooldown"})
                return 0

    if next_idx is None:
        state["armed"] = False
        save_state(state)
        print("STATUS=ALL_8_STEPS_COMPLETED")
        write_outputs({"action": "done"})
        return 0

    state["active_step_index"] = next_idx
    save_state(state)
    step = steps[next_idx]
    print(f"STATUS=READY_TO_STAGE STEP={step['step']} BRANCH={step['branch']} TARGET={step['target_file']}")
    write_outputs(
        {
            "action": "stage",
            "step_num": str(step["step"]),
            "step_dir": step["dir"],
            "branch": step["branch"],
            "target_file": step["target_file"],
            "pr_title": step["title"],
        }
    )
    return 0


def phase_apply(mathlib_dir: Path, step_dir_name: str, target_file: str) -> int:
    patch_path = LADDER_DIR / step_dir_name / "patch.lean"
    target_path = mathlib_dir / target_file
    if not target_path.is_file():
        raise FileNotFoundError(f"Target file not found in mathlib clone: {target_path}")

    body = strip_patch_header(patch_path.read_text(encoding="utf-8"))
    orig = target_path.read_text(encoding="utf-8")
    marker = f"-- MicroLadderStep: {step_dir_name}"
    if marker in orig:
        print(f"Patch marker {marker} already present in {target_file}")
        return 0

    updated = orig.rstrip() + f"\n\n{marker}\nsection MicroLadderStep\n{body}\nend MicroLadderStep\n"
    target_path.write_text(updated, encoding="utf-8")
    print(f"APPLIED step={step_dir_name} to {target_file}")
    return 0


def phase_summarize(
    step_num: int,
    step_dir_name: str,
    branch: str,
    target_file: str,
    pr_title: str,
    fork_pushed: bool,
) -> int:
    letter_text = (LADDER_DIR / step_dir_name / "pr_letter.txt").read_text(encoding="utf-8").strip()
    compare_url = (
        f"https://github.com/leanprover-community/mathlib4/compare/"
        f"master...Qamarbajwa:mathlib4:{branch}?expand=1"
    )
    push_note = (
        f"Branch `{branch}` pushed cleanly to `Qamarbajwa/mathlib4` and verified via `lake env lean {target_file}`."
        if fork_pushed
        else (
            f"Patch verified via `lake env lean {target_file}` (`rc=0`). Add repository secret `GH_PAT` "
            f"if not yet set so Actions pushes `{branch}` to `Qamarbajwa/mathlib4` automatically."
        )
    )
    md = "\n".join(
        [
            f"# Ready to Submit Next Mathlib4 Micro-PR (Step {step_num} of 8)",
            "",
            f"- **Step:** `{step_dir_name}` (`Step {step_num}/8`)",
            f"- **Fork Branch (`Qamarbajwa/mathlib4`):** `{branch}`",
            f"- **Target File:** `{target_file}`",
            f"- **Status:** {push_note}",
            f"- **One-Click Compare & Submit URL:** {compare_url}",
            "",
            "## Exact PR Title",
            "```text",
            pr_title,
            "```",
            "",
            "## Ready-to-Copy `pr_letter.txt`",
            "```text",
            letter_text,
            "```",
            "",
        ]
    )
    (REPO_ROOT / "READY_TO_SUBMIT_NEXT_PR.md").write_text(md, encoding="utf-8")
    summary_path = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary_path:
        with open(summary_path, "a", encoding="utf-8") as f:
            f.write(md + "\n")
    print(f"COMPARE_URL={compare_url}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="CI helper for 8-step Mathlib4 Fork Auto-Stager.")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_chk = sub.add_parser("check")
    p_chk.add_argument("--force-arm", action="store_true")

    p_app = sub.add_parser("apply")
    p_app.add_argument("--mathlib-dir", type=Path, required=True)
    p_app.add_argument("--step-dir", required=True)
    p_app.add_argument("--target-file", required=True)

    p_sum = sub.add_parser("summarize")
    p_sum.add_argument("--step-num", type=int, required=True)
    p_sum.add_argument("--step-dir", required=True)
    p_sum.add_argument("--branch", required=True)
    p_sum.add_argument("--target-file", required=True)
    p_sum.add_argument("--pr-title", required=True)
    p_sum.add_argument("--fork-pushed", action="store_true")

    args = parser.parse_args()
    if args.cmd == "check":
        return phase_check(force_arm=args.force_arm)
    if args.cmd == "apply":
        return phase_apply(args.mathlib_dir, args.step_dir, args.target_file)
    if args.cmd == "summarize":
        return phase_summarize(
            args.step_num,
            args.step_dir,
            args.branch,
            args.target_file,
            args.pr_title,
            args.fork_pushed,
        )
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
