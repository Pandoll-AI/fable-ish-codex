#!/usr/bin/env python3
"""Stop-time completion gate for fable-ish."""

from __future__ import annotations

import contextlib
import io
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from ledger import emit_json, load_ledger, read_stdin_json, update_ledger
from verify_state import dashboard, should_block_stop, warning_after_max_blocks


def has_activity(ledger) -> bool:
    return bool(
        ledger.get("changed_files_seen")
        or ledger.get("verification_results")
        or ledger.get("failures")
        or ledger.get("exit_criteria")
        or ledger.get("carried_over_unverified")
    )


FAIL_OPEN_PREFIX = (
    "fable-ish plugin bookkeeping/output issue; failed open. "
    "This is a plugin issue, not evidence that your verification failed:"
)


def failure_payload(exc: Exception) -> dict[str, object]:
    return {"systemMessage": f"{FAIL_OPEN_PREFIX} {exc}"}


def main() -> dict[str, object]:
    input_data = read_stdin_json()
    if input_data.get("stop_hook_active") is True:
        return {
            "systemMessage": "fable-ish stop hook is already active; allowing stop to avoid a continuation loop.",
            "hookSpecificOutput": {
                "hookEventName": "Stop",
                "additionalContext": "fable-ish: stop hook was already active, so no additional block was issued.",
            },
        }
    ledger = load_ledger(input_data)
    status = dashboard(ledger)
    block, reason = should_block_stop(ledger)
    if block:
        def bump(entry):
            entry["stop_blocks"] = int(entry.get("stop_blocks") or 0) + 1

        update_ledger(input_data, bump)
        return {"decision": "block", "reason": f"{reason} [{status}]"}

    warning = warning_after_max_blocks(ledger)
    if not warning and not has_activity(ledger):
        return {}
    context = f"{warning}\n{status}" if warning else status
    payload: dict[str, object] = {
        "hookSpecificOutput": {
            "hookEventName": "Stop",
            "additionalContext": context,
        }
    }
    if warning:
        payload["systemMessage"] = warning
    return payload


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
