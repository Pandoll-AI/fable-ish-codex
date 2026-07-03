#!/usr/bin/env python3
"""Pre-tool guardrails for fable-ish."""

from __future__ import annotations

import contextlib
import io
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from classify_task import classify_tool_risk
from ledger import add_unique, emit_json, read_stdin_json, update_ledger


FAIL_OPEN_PREFIX = (
    "fable-ish plugin bookkeeping/output issue; failed open. "
    "This is a plugin issue, not evidence that your verification failed:"
)


def failure_payload(exc: Exception) -> dict[str, object]:
    return {"systemMessage": f"{FAIL_OPEN_PREFIX} {exc}"}


def decision_payload(decision: str, reason: str) -> dict[str, object]:
    return {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": decision,
            "permissionDecisionReason": reason,
        }
    }


def main() -> dict[str, object]:
    input_data = read_stdin_json()
    decision, flags, reason = classify_tool_risk(input_data)
    if flags:
        update_ledger(input_data, lambda ledger: add_unique(ledger, "risk_flags", flags))
    if decision in {"deny", "ask"}:
        return decision_payload(decision, reason)
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
