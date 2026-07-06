#!/usr/bin/env python3
"""Drift detection between this repo and its install/cache targets."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from sync_dist import check_target, default_targets, ship_files


class DistSyncTestCase(unittest.TestCase):
    def test_existing_targets_do_not_drift(self) -> None:
        files = ship_files()
        problems: list[str] = []
        checked = 0
        for target in default_targets():
            # Install/cache locations are absent in a clean checkout (for
            # example public CI); only present targets are held to the rule.
            if not target.is_dir():
                continue
            checked += 1
            problems.extend(check_target(target, files))
        if checked == 0:
            self.skipTest("no install/cache targets present")
        self.assertEqual(problems, [], "run: python3 scripts/sync_dist.py")


if __name__ == "__main__":
    unittest.main()
