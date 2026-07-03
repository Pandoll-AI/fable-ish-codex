#!/usr/bin/env python3
"""Sync canonical fable-ish sources to distribution targets.

Replaces the prose "MUST NOT drift" rule in AGENTS.md with a mechanical
boundary: run this script to propagate, run it with --check to detect drift.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SHIP_DIRS = ("hooks", "scripts", "skills", "rules", "examples", "tests", ".codex-plugin")
EXCLUDED_PARTS = {"__pycache__", ".DS_Store", ".pytest_cache"}
EXCLUDED_SUFFIXES = {".pyc", ".pyo"}


def plugin_version() -> str:
    manifest = json.loads((ROOT / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8"))
    return str(manifest.get("version") or "0.0.0")


def default_targets() -> list[Path]:
    home = Path.home()
    return [
        ROOT / "fable-ish-codex",
        home / "plugins" / "fable-ish-codex",
        home / ".codex" / "plugins" / "cache" / "personal" / "fable-ish-codex" / plugin_version(),
    ]


def ship_files() -> list[Path]:
    files: list[Path] = []
    for dir_name in SHIP_DIRS:
        base = ROOT / dir_name
        if not base.is_dir():
            continue
        for path in sorted(base.rglob("*")):
            if not path.is_file():
                continue
            relative = path.relative_to(ROOT)
            if any(part in EXCLUDED_PARTS for part in relative.parts):
                continue
            if path.suffix in EXCLUDED_SUFFIXES:
                continue
            files.append(relative)
    return files


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check_target(target: Path, files: list[Path]) -> list[str]:
    problems: list[str] = []
    if not target.is_dir():
        return [f"{target}: missing target directory"]
    for relative in files:
        source = ROOT / relative
        dest = target / relative
        if not dest.is_file():
            problems.append(f"{target / relative}: missing")
        elif file_hash(source) != file_hash(dest):
            problems.append(f"{target / relative}: content drift")
    return problems


def sync_target(target: Path, files: list[Path]) -> int:
    copied = 0
    for relative in files:
        source = ROOT / relative
        dest = target / relative
        if dest.is_file() and file_hash(source) == file_hash(dest):
            continue
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, dest)
        copied += 1
    return copied


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="report drift without copying; nonzero exit on drift")
    parser.add_argument("--target", action="append", type=Path, help="override sync targets (repeatable)")
    args = parser.parse_args(argv)

    targets = [path.expanduser() for path in args.target] if args.target else default_targets()
    files = ship_files()
    if not files:
        print("sync_dist: no shippable files found", file=sys.stderr)
        return 2

    if args.check:
        drift = False
        for target in targets:
            # The cache target for a not-yet-released version may legitimately
            # not exist; only existing targets are held to the no-drift rule.
            if not target.is_dir():
                print(f"check {target}: absent (skipped)")
                continue
            problems = check_target(target, files)
            if problems:
                drift = True
                for problem in problems:
                    print(problem)
            else:
                print(f"check {target}: in sync ({len(files)} files)")
        return 1 if drift else 0

    for target in targets:
        copied = sync_target(target, files)
        print(f"sync {target}: {copied} files copied, {len(files) - copied} already in sync")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
