#!/usr/bin/env python3
"""No-op approval hook retained for compatibility."""

from __future__ import annotations

import contextlib
import io
import json
import sys


FAIL_OPEN_PREFIX = (
    "fable-ish plugin bookkeeping/output issue; failed open. "
    "This is a plugin issue, not evidence that your verification failed:"
)


def main() -> dict[str, object]:
    sys.stdin.read()
    return {}


def run() -> int:
    captured_stdout = io.StringIO()
    try:
        with contextlib.redirect_stdout(captured_stdout):
            payload = main()
    except Exception as exc:
        payload = {"systemMessage": f"{FAIL_OPEN_PREFIX} {exc}"}
    sys.stdout.write(json.dumps(payload, ensure_ascii=True) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(run())
