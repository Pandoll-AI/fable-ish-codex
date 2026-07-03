#!/usr/bin/env python3
"""Classify incoming Codex prompts for fable-ish."""

from __future__ import annotations

import contextlib
import io
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from classify_task import classify_prompt, context_for_mode
from ledger import add_unique, emit_json, load_ledger, read_stdin_json, update_ledger


FAIL_OPEN_PREFIX = (
    "fable-ish plugin bookkeeping/output issue; failed open. "
    "This is a plugin issue, not evidence that your verification failed:"
)

CONTINUATION_PREFIXES = (
    "fable-ish: run ",
    "fable-ish: add ",
    "fable-ish: resolve ",
    "fable-ish: declared ",
)


def failure_payload(exc: Exception) -> dict[str, object]:
    return {"systemMessage": f"{FAIL_OPEN_PREFIX} {exc}"}


def context_payload(context: str) -> dict[str, object]:
    return {
        "hookSpecificOutput": {
            "hookEventName": "UserPromptSubmit",
            "additionalContext": context,
        }
    }


def main() -> dict[str, object]:
    input_data = read_stdin_json()
    prompt = str(input_data.get("prompt") or input_data.get("user_prompt") or "")
    normalized_prompt = prompt.lstrip().lower()
    if normalized_prompt.startswith(CONTINUATION_PREFIXES):
        ledger = load_ledger(input_data)
        mode = str(ledger.get("task_mode") or "normal")
        risks = list(ledger.get("risk_flags") or [])
        return context_payload(context_for_mode(mode, risks))

    mode, risks, goal = classify_prompt(prompt)
    carried: list[str] = []

    def apply(ledger):
        nonlocal carried
        # The reset policy is deliberate (see CHANGELOG); unverified changes
        # from the previous prompt are carried forward as visible context so
        # they cannot silently evaporate, but they do not block the new turn.
        if ledger.get("changed_files_seen") and not any(
            result.get("success") is True for result in ledger.get("verification_results", [])
        ):
            carried = [path for path in ledger.get("changed_paths") or [] if path][:10]
        ledger["task_mode"] = mode
        ledger["goal"] = goal
        ledger["changed_files_seen"] = False
        ledger["changed_paths"] = []
        ledger["change_kinds"] = []
        ledger["coverage_relation"] = "none"
        ledger["risk_flags"] = []
        ledger["verification_commands"] = []
        ledger["verification_results"] = []
        ledger["exit_criteria"] = []
        ledger["carried_over_unverified"] = carried
        ledger["failures"] = []
        ledger["stop_blocks"] = 0
        add_unique(ledger, "risk_flags", risks)

    update_ledger(input_data, apply)

    if mode == "blocked":
        return {
            "decision": "block",
            "reason": "fable-ish blocked this prompt because it appears to request destructive or secret-exposing action. Narrow the request or provide explicit safe scope.",
        }

    context = context_for_mode(mode, risks)
    if carried:
        context += "\nUnverified changes from the previous prompt: " + ", ".join(carried) + "."
    return context_payload(context)


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
