#!/usr/bin/env python3
"""Declare, revise, and satisfy fable-ish exit criteria.

The CLI only validates and echoes. The model never sees its own session_id,
so it cannot locate the session ledger; the PostToolUse hook observes these
invocations and applies them to the correct ledger (sentinel-command pattern).
"""

from __future__ import annotations

import shlex
import sys
from typing import Any

CRITERIA_KINDS = {"test", "validator", "runtime", "browser", "ci", "data-wait"}
SHELL_CONTROL_TOKENS = {";", "&", "|", "&&", "||"}
SCRIPT_MARKERS = ("fable_criteria.py", "fable-criteria")


def parse_args(args: list[str]) -> dict[str, Any] | None:
    if not args:
        return None
    op = args[0]
    rest = list(args[1:])

    def take_flag(name: str) -> str:
        if name in rest:
            index = rest.index(name)
            if index + 1 < len(rest):
                value = rest[index + 1]
                del rest[index : index + 2]
                return value
            del rest[index]
        return ""

    if op == "declare":
        kind = take_flag("--kind") or "test"
        if not rest or kind not in CRITERIA_KINDS:
            return None
        return {"op": "declare", "statement": " ".join(rest), "kind": kind}
    if op == "revise":
        reason = take_flag("--reason")
        if len(rest) < 2 or not reason:
            return None
        return {"op": "revise", "id": rest[0], "statement": " ".join(rest[1:]), "reason": reason}
    if op == "satisfy":
        evidence = take_flag("--evidence")
        if len(rest) != 1 or not evidence:
            return None
        return {"op": "satisfy", "id": rest[0], "evidence": evidence}
    if op == "list":
        return {"op": "list"}
    return None


def parse_invocation(command: str) -> dict[str, Any] | None:
    """Parse a shell command if it is a pure fable_criteria invocation.

    Commands with shell control operators or substitution are rejected so the
    criteria exemption cannot smuggle a second command past the guardrails.
    """
    try:
        tokens = shlex.split(command or "")
    except ValueError:
        return None
    if any(token in SHELL_CONTROL_TOKENS or "$(" in token or "`" in token for token in tokens):
        return None
    index = next(
        (i for i, token in enumerate(tokens) if token.endswith(SCRIPT_MARKERS[0]) or token == SCRIPT_MARKERS[1]),
        None,
    )
    if index is None:
        return None
    return parse_args(tokens[index + 1 :])


def next_criterion_id(criteria: list[dict[str, Any]]) -> str:
    highest = 0
    for criterion in criteria:
        raw = str(criterion.get("id") or "")
        if raw.startswith("c") and raw[1:].isdigit():
            highest = max(highest, int(raw[1:]))
    return f"c{highest + 1}"


def apply_action(ledger: dict[str, Any], action: dict[str, Any]) -> str:
    criteria = ledger.setdefault("exit_criteria", [])
    op = action.get("op")
    if op == "declare":
        criterion_id = next_criterion_id(criteria)
        criteria.append(
            {
                "id": criterion_id,
                "statement": action["statement"],
                "kind": action["kind"],
                "status": "open",
                "evidence": "",
                "reason": "",
            }
        )
        return f"fable-ish: exit criterion {criterion_id} recorded ({action['kind']}): {action['statement']}"
    if op in {"revise", "satisfy"}:
        criterion = next((c for c in criteria if c.get("id") == action.get("id")), None)
        if criterion is None:
            return f"fable-ish: exit criterion {action.get('id')} not found; declare it first."
        if op == "revise":
            criterion["statement"] = action["statement"]
            criterion["reason"] = action["reason"]
            criterion["status"] = "open"
            return (
                f"fable-ish: exit criterion {criterion['id']} revised "
                f"(reason: {action['reason']}): {action['statement']}"
            )
        criterion["status"] = "satisfied"
        criterion["evidence"] = action["evidence"]
        return f"fable-ish: exit criterion {criterion['id']} satisfied: {action['evidence']}"
    if op == "list":
        if not criteria:
            return "fable-ish: no exit criteria declared for this task."
        lines = [f"{c.get('id')} [{c.get('status')}] {c.get('statement')}" for c in criteria]
        return "fable-ish exit criteria: " + " | ".join(lines)
    return "fable-ish: unsupported criteria action."


USAGE = """usage:
  fable_criteria.py declare "<observable criterion>" [--kind test|validator|runtime|browser|ci|data-wait]
  fable_criteria.py revise <id> "<new criterion>" --reason "<why the bar moved>"
  fable_criteria.py satisfy <id> --evidence "<what was actually observed>"
  fable_criteria.py list
The fable-ish PostToolUse hook records this invocation in the session ledger."""


def main(argv: list[str]) -> int:
    action = parse_args(list(argv))
    if action is None:
        print(USAGE)
        return 2
    if action["op"] == "declare":
        print(f"fable-ish: declaring exit criterion ({action['kind']}): {action['statement']}")
    elif action["op"] == "revise":
        print(f"fable-ish: revising {action['id']} (reason: {action['reason']}): {action['statement']}")
    elif action["op"] == "satisfy":
        print(f"fable-ish: marking {action['id']} satisfied: {action['evidence']}")
    else:
        print("fable-ish: criteria list requested; see hook context for current state.")
    print("Recorded by the fable-ish hook if hooks are active.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
