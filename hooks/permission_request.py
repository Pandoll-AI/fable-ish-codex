#!/usr/bin/env python3
"""No-op approval hook retained for compatibility."""

from __future__ import annotations

import json
import sys


def main() -> int:
    sys.stdin.read()
    print(json.dumps({}))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(json.dumps({"systemMessage": f"fable-ish permission hook failed open: {exc}"}))
        raise SystemExit(0)
