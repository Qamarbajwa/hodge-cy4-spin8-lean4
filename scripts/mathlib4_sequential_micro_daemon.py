"""Sequential 8-step Mathlib4 Micro-PR Daemon & Validator.

Manages `dist/mathlib4_micro_ladder/queue_state.json` safely:
- Validates every micro-step's `patch.lean` (15..40 lines, native Mathlib style, zero
  `maxHeartbeats`, `#print axioms`, `gcdFuel`, `rangeList`, `sorry`, `admit`, `axiom`) and
  `pr_letter.txt` (simple English with `Step 1:` / `Step 2:`, zero `#`, em-dash, `--`,
  `**`, SHA-256 hashes, ending with `ai is being used as a tool`).
- Defaults to `"armed": false`. Never pushes or opens any upstream PR while disarmed.
- When explicitly armed (`--arm` + `--tick` / `--run`), enforces strict one-by-one order:
  waits while any PR is `OPEN`, trips a permanent circuit breaker on any unmerged `CLOSED`
  PR (setting `"armed": false`), and enforces a 900-second post-merge cooldown after each
  `MERGED` timestamp before opening the next step.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import re
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict, List


REPO_ROOT = Path(__file__).resolve().parent.parent
LADDER_DIR = REPO_ROOT / "dist" / "mathlib4_micro_ladder"
STATE_PATH = LADDER_DIR / "queue_state.json"

BANNED_PATCH_TOKENS = (
    "maxHeartbeats",
    "#print axioms",
    "gcdFuel",
    "rangeList",
    "sorry",
    "admit",
    "axiom ",
)
BANNED_LETTER_TOKENS = ("#", "\u2014", "--", "**")
SHA256_PATTERN = re.compile(r"(?:sha256|[0-9a-fA-F]{64})", re.IGNORECASE)
EXPECTED_CLOSING_LINE = "ai is being used as a tool"


def load_state() -> Dict[str, Any]:
    return json.loads(STATE_PATH.read_text(encoding="utf-8"))


def save_state(state: Dict[str, Any]) -> None:
    STATE_PATH.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")


def validate_letter_and_patch(step_dir: Path) -> Dict[str, Any]:
    """Validate `patch.lean` and `pr_letter.txt` inside a single micro-step directory."""
    errors: List[str] = []
    patch_path = step_dir / "patch.lean"
    letter_path = step_dir / "pr_letter.txt"

    if not patch_path.is_file():
        errors.append("missing patch.lean")
        patch_lines: List[str] = []
    else:
        patch_text = patch_path.read_text(encoding="utf-8")
        patch_lines = patch_text.splitlines()
        if not (15 <= len(patch_lines) <= 40):
            errors.append(f"patch.lean line count {len(patch_lines)} outside 15..40")
        for tok in BANNED_PATCH_TOKENS:
            if tok in patch_text:
                errors.append(f"banned patch token detected: {tok!r}")

    if not letter_path.is_file():
        errors.append("missing pr_letter.txt")
        letter_lines: List[str] = []
    else:
        letter_text = letter_path.read_text(encoding="utf-8")
        letter_lines = [ln.rstrip() for ln in letter_text.splitlines() if ln.strip()]
        for tok in BANNED_LETTER_TOKENS:
            if tok in letter_text:
                errors.append(f"banned letter token detected: {tok!r}")
        if SHA256_PATTERN.search(letter_text):
            errors.append("SHA-256 hash or sha256 text detected in pr_letter.txt")
        if "Step 1:" not in letter_text or "Step 2:" not in letter_text:
            errors.append("pr_letter.txt missing 'Step 1:' and/or 'Step 2:'")
        if not letter_lines or letter_lines[-1] != EXPECTED_CLOSING_LINE:
            errors.append(f"pr_letter.txt must end with exact line {EXPECTED_CLOSING_LINE!r}")

    return {
        "dir": step_dir.name,
        "patch_lines": len(patch_lines),
        "letter_nonempty_lines": len(letter_lines),
        "passed": len(errors) == 0,
        "errors": errors,
    }


def validate_all(state: Dict[str, Any]) -> bool:
    steps = state.get("steps", [])
    if len(steps) != 8:
        print(f"ERROR: expected 8 steps in queue_state.json, found {len(steps)}")
        return False

    all_ok = True
    for entry in steps:
        step_dir = LADDER_DIR / entry["dir"]
        res = validate_letter_and_patch(step_dir)
        status = "PASS" if res["passed"] else "FAIL"
        print(
            f"STEP {entry['step']} [{res['dir']}]: {status} "
            f"(patch_lines={res['patch_lines']}, letter_lines={res['letter_nonempty_lines']})"
        )
        for err in res["errors"]:
            print(f"  ERROR: {err}")
        if not res["passed"]:
            all_ok = False

    print(f"QUEUE_ARMED={state.get('armed')}")
    print(f"COOLDOWN_SECONDS={state.get('cooldown_seconds')}")
    print(f"CIRCUIT_BREAKER_TRIPPED={state.get('circuit_breaker_tripped')}")
    print(f"MICRO_LADDER_STAGED_AND_VALIDATED={all_ok}")
    return all_ok


def query_open_prs(upstream_repo: str) -> List[Dict[str, Any]]:
    proc = subprocess.run(
        [
            "gh",
            "pr",
            "list",
            "--repo",
            upstream_repo,
            "--author",
            "Qamarbajwa",
            "--state",
            "open",
            "--limit",
            "50",
            "--json",
            "number,title,headRefName,url",
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


def query_pr_view(upstream_repo: str, pr_number: int) -> Dict[str, Any]:
    proc = subprocess.run(
        [
            "gh",
            "pr",
            "view",
            str(pr_number),
            "--repo",
            upstream_repo,
            "--json",
            "number,state,mergedAt,closedAt,url",
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"gh pr view #{pr_number} failed ({proc.returncode}): {proc.stderr.strip()}")
    return json.loads(proc.stdout)


def parse_iso_utc(ts: str) -> datetime:
    return datetime.fromisoformat(ts.replace("Z", "+00:00"))


def tick(state: Dict[str, Any]) -> int:
    upstream_repo = state.get("upstream_repo", "leanprover-community/mathlib4")
    open_prs = query_open_prs(upstream_repo)
    print(f"OPEN_PRS_COUNT={len(open_prs)}")

    if state.get("circuit_breaker_tripped"):
        print(f"STATUS: CIRCUIT_BREAKER_TRIPPED ({state.get('circuit_breaker_reason')})")
        return 1

    if not state.get("armed", False):
        print("STATUS: DISARMED")
        print("ARMED=False")
        return 0

    if open_prs:
        print("STATUS: WAIT_FOR_OPEN_PR")
        for pr in open_prs:
            print(f"  OPEN #{pr['number']} [{pr['headRefName']}] {pr['url']}")
        return 0

    active_pr = state.get("active_pr_number")
    active_idx = int(state.get("active_step_index", 0))
    cooldown = int(state.get("cooldown_seconds", 900))
    steps = state["steps"]

    if active_pr is not None:
        info = query_pr_view(upstream_repo, int(active_pr))
        pr_state = info.get("state")
        merged_at = info.get("mergedAt")
        if pr_state == "OPEN":
            print(f"STATUS: WAIT_FOR_OPEN_PR #{active_pr}")
            return 0
        if pr_state == "CLOSED" and not merged_at:
            state["armed"] = False
            state["circuit_breaker_tripped"] = True
            state["circuit_breaker_reason"] = (
                f"PR #{active_pr} closed without merge at {info.get('closedAt')}"
            )
            steps[active_idx]["status"] = "CLOSED_UNMERGED"
            steps[active_idx]["closed_at"] = info.get("closedAt")
            save_state(state)
            print(f"STATUS: CIRCUIT_BREAKER_TRIPPED (#{active_pr} closed unmerged)")
            return 1
        if merged_at:
            elapsed = (datetime.now(timezone.utc) - parse_iso_utc(merged_at)).total_seconds()
            steps[active_idx]["status"] = "MERGED"
            steps[active_idx]["merged_at"] = merged_at
            save_state(state)
            if elapsed < cooldown:
                remaining = int(cooldown - elapsed)
                print(f"STATUS: COOLDOWN_ACTIVE remaining_seconds={remaining}")
                return 0
            state["active_pr_number"] = None
            state["active_step_index"] = active_idx + 1
            save_state(state)
            active_idx += 1

    if active_idx >= len(steps):
        state["armed"] = False
        save_state(state)
        print("STATUS: ALL_8_STEPS_COMPLETED")
        return 0

    next_step = steps[active_idx]
    print(f"STATUS: READY_FOR_STEP_{next_step['step']} branch={next_step['branch']}")
    print("NOTE: Armed execution must invoke explicit PR creation only when explicitly enabled.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Mathlib4 8-step sequential micro-PR daemon.")
    parser.add_argument("--validate", action="store_true", help="Validate all 8 staged micro-steps.")
    parser.add_argument("--arm", action="store_true", help="Set armed=true in queue_state.json.")
    parser.add_argument("--disarm", action="store_true", help="Set armed=false in queue_state.json.")
    parser.add_argument("--tick", action="store_true", help="Run one queue state check tick.")
    parser.add_argument("--run", action="store_true", help="Poll continuously at --poll-seconds.")
    parser.add_argument("--poll-seconds", type=int, default=60, help="Polling interval seconds.")
    parser.add_argument("--max-ticks", type=int, default=1, help="Max ticks in --run mode.")
    args = parser.parse_args()

    state = load_state()

    if args.arm and args.disarm:
        print("ERROR: cannot pass both --arm and --disarm")
        return 2

    if args.arm:
        if state.get("circuit_breaker_tripped"):
            print("ERROR: circuit breaker is tripped; clear manually before arming.")
            return 1
        state["armed"] = True
        save_state(state)
        print("QUEUE_ARMED=True")

    if args.disarm:
        state["armed"] = False
        save_state(state)
        print("QUEUE_ARMED=False")

    if args.validate or not (args.arm or args.disarm or args.tick or args.run):
        ok = validate_all(state)
        if not ok:
            return 1

    if args.tick:
        return tick(state)

    if args.run:
        for idx in range(args.max_ticks):
            state = load_state()
            rc = tick(state)
            if rc != 0 or not state.get("armed", False):
                return rc
            if idx + 1 < args.max_ticks:
                time.sleep(args.poll_seconds)

    return 0


if __name__ == "__main__":
    sys.exit(main())
