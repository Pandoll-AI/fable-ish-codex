#!/usr/bin/env python3
"""Stop-time decision helper for fable-ish."""

from __future__ import annotations

from typing import Any


MAX_STOP_BLOCKS = 2


def has_successful_verification(ledger: dict[str, Any]) -> bool:
    return any(result.get("success") is True for result in ledger.get("verification_results", []))


def has_meaningful_deep_verification(ledger: dict[str, Any]) -> bool:
    """Build/typecheck/lint alone do not prove changed behavior for deep work.

    Accept a successful verification only when it either targets a changed
    path directly or is not a build-only command.
    """
    for result in ledger.get("verification_results", []):
        if result.get("success") is not True:
            continue
        if result.get("coverage_relation") == "direct":
            return True
        if not result.get("build_only"):
            return True
    return False


def has_any_verification(ledger: dict[str, Any]) -> bool:
    return bool(ledger.get("verification_commands") or ledger.get("verification_results"))


def open_criteria(ledger: dict[str, Any]) -> list[dict[str, Any]]:
    return [c for c in ledger.get("exit_criteria", []) if c.get("status") == "open"]


def docs_only(ledger: dict[str, Any]) -> bool:
    kinds = set(ledger.get("change_kinds", []))
    return bool(ledger.get("changed_files_seen")) and kinds and kinds <= {"docs"}


def dashboard(ledger: dict[str, Any]) -> str:
    kinds = ",".join(ledger.get("change_kinds") or []) or "-"
    results = ledger.get("verification_results") or []
    ok = sum(1 for result in results if result.get("success") is True)
    parts = [
        f"mode={ledger.get('task_mode') or 'quick'}",
        f"changed={len(ledger.get('changed_paths') or [])} ({kinds})",
        f"verifications={len(results)} (ok={ok})",
        f"coverage={ledger.get('coverage_relation') or 'none'}",
        f"failures={len(ledger.get('failures') or [])}",
    ]
    criteria = ledger.get("exit_criteria") or []
    if criteria:
        parts.append(f"criteria open={len(open_criteria(ledger))}/{len(criteria)}")
    carried = ledger.get("carried_over_unverified") or []
    if carried:
        parts.append("carried-over unverified: " + ", ".join(carried[:5]))
    return "fable-ish status: " + "; ".join(parts)


def should_block_stop(ledger: dict[str, Any]) -> tuple[bool, str]:
    mode = ledger.get("task_mode") or "quick"
    stop_blocks = int(ledger.get("stop_blocks") or 0)
    changed = bool(ledger.get("changed_files_seen"))

    if stop_blocks >= MAX_STOP_BLOCKS:
        return False, "fable-ish allowed stop after two verification reminders; report any missing verification clearly."
    if mode == "quick":
        return False, ""
    if docs_only(ledger):
        return False, ""
    if mode == "blocked":
        return True, "fable-ish: resolve or narrow the blocked risk before final response."
    if mode == "deep":
        # Model-declared criteria take precedence over the fixed fallback:
        # the gate enforces the model's own stated exit conditions.
        pending = open_criteria(ledger)
        if pending:
            listing = "; ".join(f"{c.get('id')}: {c.get('statement')}" for c in pending[:5])
            return True, (
                "fable-ish: declared exit criteria still open — "
                f"{listing}. Observe the evidence and run fable_criteria.py satisfy, "
                "or revise with a reason."
            )
        criteria = ledger.get("exit_criteria") or []
        if criteria and any(c.get("status") == "satisfied" for c in criteria):
            return False, ""
        if not has_meaningful_deep_verification(ledger):
            if changed:
                return True, (
                    "fable-ish: run the narrowest verification for the changed behavior before final response; "
                    "build/typecheck alone does not prove behavior for deep work."
                )
            if not has_any_verification(ledger):
                return True, "fable-ish: add one observable proof or explicitly record why this deep task has no runnable verifier."
    if mode == "normal" and changed and not has_successful_verification(ledger):
        return True, "fable-ish: run one relevant verification command for the changed files, or state why no verifier applies."
    return False, ""


def warning_after_max_blocks(ledger: dict[str, Any]) -> str:
    if int(ledger.get("stop_blocks") or 0) >= MAX_STOP_BLOCKS and not has_successful_verification(ledger):
        return "fable-ish: verification evidence is still missing. Include that gap in the final report."
    return ""
