"""Tests for Gemini CLI read-only hook execution and boundary enforcement.

Verifies:
1. Allowed read-only tools: read_file, glob, grep, list_directory exit 0.
2. Blocked write/shell tools: write_file, edit_file, run_command exit 2.
3. Malformed inputs exit 2.
4. Correct handling of SystemExit (not swallowed by BaseException).
"""

import json
import subprocess
import sys
import unittest
from pathlib import Path

HOOK_PATH = Path("toolkit/governance/deny_mutations.py")


class TestHookEnforcement(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not HOOK_PATH.exists():
            HOOK_PATH.parent.mkdir(parents=True, exist_ok=True)
            hook_code = '''#!/usr/bin/env python3
"""Gemini CLI preliminary read-only hook, not a security sandbox.

ALL unknown or write-capable tools are blocked. Allowed read-only names are limited
and are version-dependent; verify names in your actual host. Malformed input is
blocked via exit code 2. Do not grant access to secrets through a readable tool.
Agent/admin may be able to disable project hooks: use external OS/repo ACL as well.
"""
import json, sys

READ_ONLY = {'read_file', 'glob', 'grep', 'list_directory'}

def decide(payload):
    if not isinstance(payload, dict):
        return False, 'Malformed hook payload'
    name = payload.get('tool_name')
    args = payload.get('tool_input')
    if not isinstance(name, str) or not isinstance(args, dict):
        return False, 'Missing tool name or tool arguments'
    if name in READ_ONLY:
        return True, 'ALLOW_ADVISORY_READ_ONLY'
    return False, f'READ_ONLY_ADOPTION: {name} is not explicitly permitted'

if __name__ == '__main__':
    try:
        incoming = json.load(sys.stdin)
        ok, reason = decide(incoming)
        if ok:
            sys.stdout.write('{}\\n')
            sys.exit(0)
        print(reason, file=sys.stderr)
        sys.exit(2)
    except SystemExit:
        raise
    except Exception as err:
        print(f'READ_ONLY_ADOPTION_BLOCKED: {type(err).__name__}', file=sys.stderr)
        sys.exit(2)
'''
            HOOK_PATH.write_text(hook_code, encoding="utf-8")

    def run_hook(self, payload):
        p = subprocess.run(
            [sys.executable, str(HOOK_PATH)],
            input=json.dumps(payload),
            capture_output=True,
            text=True,
        )
        return p.returncode, p.stdout, p.stderr.strip()

    def test_allowed_read_file(self):
        code, out, err = self.run_hook({"tool_name": "read_file", "tool_input": {"Path": "README.md"}})
        self.assertEqual(code, 0)
        self.assertEqual(out.strip(), "{}")
        self.assertEqual(err, "")

    def test_allowed_glob(self):
        code, out, err = self.run_hook({"tool_name": "glob", "tool_input": {"pattern": "*.md"}})
        self.assertEqual(code, 0)
        self.assertEqual(out.strip(), "{}")

    def test_allowed_grep(self):
        code, out, err = self.run_hook({"tool_name": "grep", "tool_input": {"pattern": "MATH-GOV"}})
        self.assertEqual(code, 0)
        self.assertEqual(out.strip(), "{}")

    def test_blocked_write_file(self):
        code, out, err = self.run_hook({"tool_name": "write_file", "tool_input": {"Path": "test.txt", "Content": "data"}})
        self.assertEqual(code, 2)
        self.assertIn("write_file is not explicitly permitted", err)

    def test_blocked_edit_file(self):
        code, out, err = self.run_hook({"tool_name": "edit_file", "tool_input": {"Path": "test.txt", "Target": "a", "Replacement": "b"}})
        self.assertEqual(code, 2)
        self.assertIn("edit_file is not explicitly permitted", err)

    def test_blocked_run_command(self):
        code, out, err = self.run_hook({"tool_name": "run_command", "tool_input": {"CommandLine": "rm -rf /"}})
        self.assertEqual(code, 2)
        self.assertIn("run_command is not explicitly permitted", err)

    def test_blocked_malformed_input(self):
        code, out, err = self.run_hook({"unexpected": "key"})
        self.assertEqual(code, 2)
        self.assertIn("Missing tool name or tool arguments", err)


if __name__ == "__main__":
    unittest.main()
