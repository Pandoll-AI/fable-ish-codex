#!/usr/bin/env python3
"""Record fable-ish tool evidence after supported tool calls."""

from __future__ import annotations

import contextlib
import io
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from classify_task import RISKY_PATH_RE
from fable_criteria import apply_action, parse_invocation
from ledger import add_unique, emit_json, read_stdin_json, update_ledger
from parse_tool_result import changed_kinds, changed_paths, command_from_input, detect_failure, verification_coverage, verification_record


FAIL_OPEN_PREFIX = (
    "fable-ish plugin bookkeeping/output issue; failed open. "
    "This is a plugin issue, not evidence that your verification failed:"
)


def failure_payload(exc: Exception) -> dict[str, object]:
    return {"systemMessage": f"{FAIL_OPEN_PREFIX} {exc}"}


def context_payload(message: str) -> dict[str, object]:
    return {
        "hookSpecificOutput": {
            "hookEventName": "PostToolUse",
            "additionalContext": message,
        }
    }


def main() -> dict[str, object]:
    input_data = read_stdin_json()
    tool_name = str(input_data.get("tool_name") or "")
    command = command_from_input(input_data)

    if tool_name == "Bash":
        criteria_action = parse_invocation(command)
        if criteria_action is not None:
            # Criteria bookkeeping only: quoted criterion text must not be
            # misread as a verification run, a file change, or a failure.
            message = ""

            def apply_criteria(ledger):
                nonlocal message
                message = apply_action(ledger, criteria_action)

            update_ledger(input_data, apply_criteria)
            return context_payload(message)

    kinds = changed_kinds(input_data)
    paths = changed_paths(input_data)
    failure = detect_failure(input_data)
    verification = verification_record(input_data)
    escalated = False

    def apply(ledger):
        nonlocal escalated
        if kinds:
            ledger["changed_files_seen"] = True
            add_unique(ledger, "changed_paths", [path.strip() for path in paths if path])
            add_unique(ledger, "change_kinds", kinds)
            if ledger.get("task_mode") == "normal" and any(
                RISKY_PATH_RE.search(path) for path in paths if path and path not in {"patch", "edit"}
            ):
                ledger["task_mode"] = "deep"
                add_unique(ledger, "risk_flags", ["risky-path"])
                escalated = True
        if verification:
            verification["coverage_relation"] = verification_coverage(command, ledger.get("changed_paths", []))
            ledger["verification_results"].append(verification)
            if command:
                ledger["verification_commands"].append(verification["command"])
            coverage_order = {"none": 0, "uncertain": 1, "generic": 2, "direct": 3}
            current = ledger.get("coverage_relation") or "none"
            observed = verification.get("coverage_relation") or "uncertain"
            if coverage_order.get(observed, 0) > coverage_order.get(current, 0):
                ledger["coverage_relation"] = observed
        if failure:
            ledger["failures"].append(failure)

    update_ledger(input_data, apply)

    context_lines = []
    if escalated:
        context_lines.append(
            "fable-ish: a risky path changed (auth/db/money/CI); task escalated to deep. "
            "Re-evaluate your exit criteria (scripts/fable_criteria.py declare/revise)."
        )
    if failure:
        context_lines.append(
            "fable-ish: tool failed; verify before final and re-evaluate declared exit criteria if the risk changed."
        )
    if context_lines:
        return context_payload("\n".join(context_lines))
    return {}


def run() -> int:
    captured_stdout = io.StringIO()
    try:
        with contextlib.redirect_stdout(captured_stdout):
            payload = main()
    except Exception as exc:
        payload = failure_payload(exc)
    emit_json(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(run())
