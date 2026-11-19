"""Strict One-by-One Gating Script for the 8-Step Native Mathlib4 Micro-Ladder.

Reads `dist/mathlib4_micro_ladder/queue_state.json` and checks
`gh pr list --repo leanprover-community/mathlib4 --author Qamarbajwa` across open,
merged, and closed PRs before allowing any manual push of the next step:
- If `queue_state.json` has `"armed": false`, reports `STATUS: DISARMED` and exits 0.
- If ANY PR by `Qamarbajwa` on `leanprover-community/mathlib4` is currently `OPEN`, prints
  `STATUS: WAIT_FOR_CURRENT_PR_ACCEPTANCE` and refuses to output a push instruction.
- Never executes `gh pr create` or posts automated comments against external repositories.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any, Dict, List


REPO_ROOT = Path(__file__).resolve().parent.parent
LADDER_DIR = REPO_ROOT / "dist" / "mathlib4_micro_ladder"
STATE_PATH = LADDER_DIR / "queue_state.json"


def load_steps() -> Dict[str, Any]:
    return json.loads(STATE_PATH.read_text(encoding="utf-8"))


def query_prs(state: str) -> List[Dict[str, Any]]:
    proc = subprocess.run(
        [
            "gh",
            "pr",
            "list",
            "--repo",
            "leanprover-community/mathlib4",
            "--author",
            "Qamarbajwa",
            "--state",
            state,
            "--limit",
            "50",
            "--json",
            "number,title,headRefName,state,url,mergedAt",
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"gh pr list failed ({proc.returncode}): {proc.stderr.strip()}")
    data = json.loads(proc.stdout or "[]")
    return data if isinstance(data, list) else []


def main() -> int:
    state = load_steps()
    steps: List[Dict[str, Any]] = state.get("steps", [])

    open_prs = query_prs("open")
    if open_prs:
        print("STATUS: WAIT_FOR_CURRENT_PR_ACCEPTANCE")
        print(f"OPEN_PRS_COUNT={len(open_prs)}")
        for pr in open_prs:
            print(f"  OPEN #{pr['number']} [{pr['headRefName']}] {pr['title']} -> {pr['url']}")
        print("GATE: Refusing to stage or suggest any next step while an upstream PR is still OPEN.")
        return 1

    print(f"OPEN_PRS_COUNT=0")
    print(f"QUEUE_ARMED={state.get('armed')}")
    if not state.get("armed", False):
        print("STATUS: DISARMED (staged safely; no upstream PRs will be pushed)")
        return 0

    merged_prs = query_prs("merged")
    merged_branches = {pr.get("headRefName", "") for pr in merged_prs}

    next_step = None
    for item in steps:
        if item["branch"] not in merged_branches:
            next_step = item
            break

    if next_step is None:
        print("STATUS: ALL_8_STEPS_MERGED")
        return 0

    step_dir = LADDER_DIR / next_step["dir"]
    patch_file = step_dir / "patch.lean"
    letter_file = step_dir / "pr_letter.txt"
    if not patch_file.exists() or not letter_file.exists():
        raise FileNotFoundError(f"Missing step artifacts under {step_dir}")

    print(f"STATUS: READY_FOR_MANUAL_STEP_{next_step['step']}")
    print(f"NEXT_STEP={next_step['dir']}")
    print(f"BRANCH={next_step['branch']}")
    print(f"PATCH_FILE={patch_file}")
    print(f"LETTER_FILE={letter_file}")
    print("MANUAL_GIT_PUSH_COMMAND:")
    print(
        f"  git checkout -b {next_step['branch']} origin/master && "
        f"# merge contents of {patch_file.relative_to(REPO_ROOT).as_posix()} into {next_step['target_file']} && "
        f"git commit -am \"{next_step['title']}\" && "
        f"git push -u origin {next_step['branch']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
