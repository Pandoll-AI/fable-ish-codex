#!/usr/bin/env python3
"""Stop-time completion gate for fable-ish."""

from __future__ import annotations

import contextlib
import io
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from ledger import emit_json, load_ledger, read_stdin_json, save_ledger
from verify_state import should_block_stop, warning_after_max_blocks


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
    block, reason = should_block_stop(ledger)
    if block:
        ledger["stop_blocks"] = int(ledger.get("stop_blocks") or 0) + 1
        save_ledger(input_data, ledger)
        return {"decision": "block", "reason": reason}

    warning = warning_after_max_blocks(ledger)
    if warning:
        return {
            "systemMessage": warning,
            "hookSpecificOutput": {
                "hookEventName": "Stop",
                "additionalContext": warning,
            },
        }
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
