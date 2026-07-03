#!/usr/bin/env python3
"""Drift detection between the canonical root and the distribution repo."""

from __future__ import annotations

import hashlib
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from sync_dist import ship_files


DIST = ROOT / "fable-ish-codex"


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class DistSyncTestCase(unittest.TestCase):
    @unittest.skipUnless(DIST.is_dir(), "distribution repo not checked out")
    def test_root_and_distribution_repo_do_not_drift(self) -> None:
        problems: list[str] = []
        for relative in ship_files():
            source = ROOT / relative
            dest = DIST / relative
            if not dest.is_file():
                problems.append(f"{relative}: missing in fable-ish-codex")
            elif file_hash(source) != file_hash(dest):
                problems.append(f"{relative}: content drift")
        self.assertEqual(problems, [], "run: python3 scripts/sync_dist.py")


if __name__ == "__main__":
    unittest.main()
