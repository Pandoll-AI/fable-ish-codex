#!/usr/bin/env python3
"""Sample contract tests for fable-ish Codex hooks."""

from __future__ import annotations

import concurrent.futures
import importlib.util
import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class HookTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.tmpdir = tempfile.TemporaryDirectory(prefix="fable-ish-test-")
        self.env = os.environ.copy()
        self.env["PLUGIN_ROOT"] = str(ROOT)
        self.env["PLUGIN_DATA"] = self.tmpdir.name
        self.env["PYTHONDONTWRITEBYTECODE"] = "1"
        self.base = {"session_id": self.id(), "cwd": str(ROOT)}

    def tearDown(self) -> None:
        self.tmpdir.cleanup()

    def run_hook(self, script: str, payload: dict) -> dict:
        stdout = self.run_hook_raw(script, json.dumps(payload))
        try:
            return json.loads(stdout)
        except json.JSONDecodeError as exc:
            self.fail(f"{script} returned invalid JSON: {stdout!r}")
            raise exc

    def run_hook_raw(self, script: str, stdin: str) -> str:
        proc = subprocess.run(
            ["python3", str(ROOT / script)],
            input=stdin,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=self.env,
            check=False,
            timeout=10,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        return proc.stdout.strip() or "{}"

    def ledger_path(self) -> Path:
        import hashlib

        raw = f"{self.base['session_id']}|{self.base['cwd']}"
        key = hashlib.sha256(raw.encode("utf-8", "replace")).hexdigest()[:24]
        return Path(self.tmpdir.name) / "ledgers" / f"{key}.json"

    def read_ledger(self) -> dict:
        return json.loads(self.ledger_path().read_text(encoding="utf-8"))

    def test_quick_mode_does_not_block_stop(self) -> None:
        prompt = {**self.base, "hook_event_name": "UserPromptSubmit", "prompt": "간단히 설명만 해줘"}
        out = self.run_hook("hooks/user_prompt_submit.py", prompt)
        self.assertIn("quick", out["hookSpecificOutput"]["additionalContext"])
        self.assertEqual(self.run_hook("hooks/stop_gate.py", {**self.base, "hook_event_name": "Stop"}), {})

    def test_normal_code_change_requires_then_accepts_verification(self) -> None:
        self.run_hook(
            "hooks/user_prompt_submit.py",
            {**self.base, "hook_event_name": "UserPromptSubmit", "prompt": "Implement a small code fix"},
        )
        self.run_hook(
            "hooks/post_tool_use.py",
            {
                **self.base,
                "hook_event_name": "PostToolUse",
                "tool_name": "apply_patch",
                "tool_input": {
                    "command": "*** Begin Patch\n*** Update File: app.py\n+x\n*** End Patch\n"
                },
                "tool_response": {"success": True},
            },
        )
        blocked = self.run_hook("hooks/stop_gate.py", {**self.base, "hook_event_name": "Stop"})
        self.assertEqual(blocked.get("decision"), "block")

        self.run_hook(
            "hooks/post_tool_use.py",
            {
                **self.base,
                "hook_event_name": "PostToolUse",
                "tool_name": "Bash",
                "tool_input": {"command": "python3 -m py_compile app.py"},
                "tool_response": {"success": True, "stdout": "success"},
            },
        )
        self.assertEqual(self.run_hook("hooks/stop_gate.py", {**self.base, "hook_event_name": "Stop"}), {})

    def test_deep_stop_blocks_at_most_twice(self) -> None:
        self.run_hook(
            "hooks/user_prompt_submit.py",
            {
                **self.base,
                "hook_event_name": "UserPromptSubmit",
                "prompt": "Do a deep production-ready refactor",
            },
        )
        first = self.run_hook("hooks/stop_gate.py", {**self.base, "hook_event_name": "Stop"})
        self.assertEqual(first.get("decision"), "block")
        self.run_hook(
            "hooks/user_prompt_submit.py",
            {**self.base, "hook_event_name": "UserPromptSubmit", "prompt": first["reason"]},
        )

        second = self.run_hook("hooks/stop_gate.py", {**self.base, "hook_event_name": "Stop"})
        self.assertEqual(second.get("decision"), "block")
        self.run_hook(
            "hooks/user_prompt_submit.py",
            {**self.base, "hook_event_name": "UserPromptSubmit", "prompt": second["reason"]},
        )

        third = self.run_hook("hooks/stop_gate.py", {**self.base, "hook_event_name": "Stop"})
        self.assertIn("verification", third.get("systemMessage", ""))

    def test_stop_hook_active_does_not_block_again(self) -> None:
        self.run_hook(
            "hooks/user_prompt_submit.py",
            {
                **self.base,
                "hook_event_name": "UserPromptSubmit",
                "prompt": "Do a deep production-ready refactor",
            },
        )
        out = self.run_hook("hooks/stop_gate.py", {**self.base, "hook_event_name": "Stop", "stop_hook_active": True})
        self.assertNotEqual(out.get("decision"), "block")
        self.assertIn("already active", out.get("systemMessage", ""))

    def test_korean_review_only_is_quick(self) -> None:
        out = self.run_hook(
            "hooks/user_prompt_submit.py",
            {**self.base, "hook_event_name": "UserPromptSubmit", "prompt": "수정하지 말고 리뷰만 해줘"},
        )
        self.assertIn("quick", out["hookSpecificOutput"]["additionalContext"])

    def test_skill_mentions_fablish_typo_alias(self) -> None:
        skill = (ROOT / "skills/fable-ish/SKILL.md").read_text(encoding="utf-8")
        self.assertIn("name: fable-ish", skill)
        self.assertIn("fablish", skill)

    def test_dangerous_and_safe_commands(self) -> None:
        denied = self.run_hook(
            "hooks/pre_tool_use.py",
            {
                **self.base,
                "hook_event_name": "PreToolUse",
                "tool_name": "Bash",
                "tool_input": {"command": "rm -rf build"},
            },
        )
        self.assertEqual(denied["hookSpecificOutput"]["permissionDecision"], "deny")

        allowed = self.run_hook(
            "hooks/pre_tool_use.py",
            {
                **self.base,
                "hook_event_name": "PreToolUse",
                "tool_name": "Bash",
                "tool_input": {"command": "npm test"},
            },
        )
        self.assertEqual(allowed, {})

    def test_remote_push_secret_output_deploy_db_push_and_publish_are_allowed(self) -> None:
        for command in (
            "git push origin main",
            "cat .env",
            "printenv",
            "echo $API_KEY",
            "vercel --prod",
            "netlify deploy --production",
            "firebase deploy",
            "kubectl apply -f deploy.yaml",
            "helm upgrade app chart",
            "supabase db push",
            "prisma db push",
            "prisma migrate deploy",
            "alembic upgrade head",
            "rails db:migrate",
            "sequelize db:migrate",
            "knex migrate:latest",
            "drizzle-kit migrate",
            "terraform apply -auto-approve",
            "pulumi up --yes",
            "npm publish",
            "pnpm publish",
            "yarn npm publish",
            "twine upload dist/*",
            "gem push pkg.gem",
        ):
            with self.subTest(command=command):
                allowed = self.run_hook(
                    "hooks/pre_tool_use.py",
                    {
                        **self.base,
                        "hook_event_name": "PreToolUse",
                        "tool_name": "Bash",
                        "tool_input": {"command": command},
                    },
                )
                self.assertEqual(allowed, {})

    def test_infrastructure_destroy_remains_blocked(self) -> None:
        for command in ("terraform destroy", "pulumi destroy"):
            with self.subTest(command=command):
                denied = self.run_hook(
                    "hooks/pre_tool_use.py",
                    {
                        **self.base,
                        "hook_event_name": "PreToolUse",
                        "tool_name": "Bash",
                        "tool_input": {"command": command},
                    },
                )
                self.assertEqual(denied["hookSpecificOutput"]["permissionDecision"], "deny")

    def test_apply_patch_aliases_are_checked(self) -> None:
        for tool_name in ("apply_patch", "Edit", "Write"):
            with self.subTest(tool_name=tool_name):
                denied = self.run_hook(
                    "hooks/pre_tool_use.py",
                    {
                        **self.base,
                        "hook_event_name": "PreToolUse",
                        "tool_name": tool_name,
                        "tool_input": {"command": "*** Begin Patch\n*** Update File: .env\n+x\n*** End Patch\n"},
                    },
                )
                self.assertEqual(denied["hookSpecificOutput"]["permissionDecision"], "deny")

    def test_new_prompt_resets_old_risk_flags(self) -> None:
        risky = self.run_hook(
            "hooks/user_prompt_submit.py",
            {
                **self.base,
                "hook_event_name": "UserPromptSubmit",
                "prompt": "Deploy production after checking auth",
            },
        )
        self.assertIn("Risk flags", risky["hookSpecificOutput"]["additionalContext"])

        quick = self.run_hook(
            "hooks/user_prompt_submit.py",
            {**self.base, "hook_event_name": "UserPromptSubmit", "prompt": "간단히 설명만 해줘"},
        )
        self.assertNotIn("Risk flags", quick["hookSpecificOutput"]["additionalContext"])

    def test_new_prompt_resets_changed_paths_and_coverage(self) -> None:
        self.run_hook(
            "hooks/user_prompt_submit.py",
            {**self.base, "hook_event_name": "UserPromptSubmit", "prompt": "Implement a small code fix"},
        )
        self.run_hook(
            "hooks/post_tool_use.py",
            {
                **self.base,
                "hook_event_name": "PostToolUse",
                "tool_name": "apply_patch",
                "tool_input": {
                    "command": "*** Begin Patch\n*** Update File: old_task.py\n+x\n*** End Patch\n"
                },
                "tool_response": {"success": True},
            },
        )
        self.run_hook(
            "hooks/post_tool_use.py",
            {
                **self.base,
                "hook_event_name": "PostToolUse",
                "tool_name": "Bash",
                "tool_input": {"command": "python3 -m py_compile old_task.py"},
                "tool_response": {"success": True, "stdout": "success"},
            },
        )
        before = self.read_ledger()
        self.assertEqual(before["changed_paths"], ["old_task.py"])
        self.assertEqual(before["coverage_relation"], "direct")

        self.run_hook(
            "hooks/user_prompt_submit.py",
            {**self.base, "hook_event_name": "UserPromptSubmit", "prompt": "간단히 설명만 해줘"},
        )
        after = self.read_ledger()
        self.assertEqual(after["changed_paths"], [])
        self.assertEqual(after["coverage_relation"], "none")

    def test_successful_zero_error_output_is_not_recorded_as_failure(self) -> None:
        self.run_hook(
            "hooks/user_prompt_submit.py",
            {**self.base, "hook_event_name": "UserPromptSubmit", "prompt": "Implement a small code fix"},
        )
        out = self.run_hook(
            "hooks/post_tool_use.py",
            {
                **self.base,
                "hook_event_name": "PostToolUse",
                "tool_name": "Bash",
                "tool_input": {"command": "npm run lint"},
                "tool_response": {"success": True, "stdout": "0 errors, 0 warnings"},
            },
        )
        self.assertEqual(out, {})

    def test_successful_exit_zero_output_with_failure_words_is_not_failure(self) -> None:
        self.run_hook(
            "hooks/user_prompt_submit.py",
            {**self.base, "hook_event_name": "UserPromptSubmit", "prompt": "Implement a small code fix"},
        )
        out = self.run_hook(
            "hooks/post_tool_use.py",
            {
                **self.base,
                "hook_event_name": "PostToolUse",
                "tool_name": "Bash",
                "tool_input": {"command": "sed -n '1,10p' hook.py"},
                "tool_response": {
                    "stdout": "Process exited with code 0\nemit_json({'systemMessage': 'hook failed open'})"
                },
            },
        )
        self.assertEqual(out, {})

    def test_exit_code_colon_marks_verification_success_and_allows_stop(self) -> None:
        self.run_hook(
            "hooks/user_prompt_submit.py",
            {**self.base, "hook_event_name": "UserPromptSubmit", "prompt": "Implement a small code fix"},
        )
        self.run_hook(
            "hooks/post_tool_use.py",
            {
                **self.base,
                "hook_event_name": "PostToolUse",
                "tool_name": "apply_patch",
                "tool_input": {
                    "command": "*** Begin Patch\n*** Update File: api/page-meta.ts\n+x\n*** End Patch\n"
                },
                "tool_response": {"success": True},
            },
        )
        self.run_hook(
            "hooks/post_tool_use.py",
            {
                **self.base,
                "hook_event_name": "PostToolUse",
                "tool_name": "Bash",
                "tool_input": {"command": "npx eslint api/page-meta.ts"},
                "tool_response": {"stdout": "exit code: 0"},
            },
        )

        ledger = self.read_ledger()
        self.assertIs(ledger["verification_results"][-1]["success"], True)
        self.assertEqual(self.run_hook("hooks/stop_gate.py", {**self.base, "hook_event_name": "Stop"}), {})

    def test_compiled_successfully_marks_verification_success_and_allows_stop(self) -> None:
        self.run_hook(
            "hooks/user_prompt_submit.py",
            {**self.base, "hook_event_name": "UserPromptSubmit", "prompt": "Implement a small code fix"},
        )
        self.run_hook(
            "hooks/post_tool_use.py",
            {
                **self.base,
                "hook_event_name": "PostToolUse",
                "tool_name": "apply_patch",
                "tool_input": {
                    "command": "*** Begin Patch\n*** Update File: app/page.tsx\n+x\n*** End Patch\n"
                },
                "tool_response": {"success": True},
            },
        )
        self.run_hook(
            "hooks/post_tool_use.py",
            {
                **self.base,
                "hook_event_name": "PostToolUse",
                "tool_name": "Bash",
                "tool_input": {"command": "npm run build"},
                "tool_response": {"stdout": "Compiled successfully"},
            },
        )

        ledger = self.read_ledger()
        self.assertIs(ledger["verification_results"][-1]["success"], True)
        self.assertEqual(self.run_hook("hooks/stop_gate.py", {**self.base, "hook_event_name": "Stop"}), {})

    def test_status_success_marks_verification_success_and_allows_stop(self) -> None:
        self.run_hook(
            "hooks/user_prompt_submit.py",
            {**self.base, "hook_event_name": "UserPromptSubmit", "prompt": "Implement a small code fix"},
        )
        self.run_hook(
            "hooks/post_tool_use.py",
            {
                **self.base,
                "hook_event_name": "PostToolUse",
                "tool_name": "apply_patch",
                "tool_input": {
                    "command": "*** Begin Patch\n*** Update File: package.json\n+x\n*** End Patch\n"
                },
                "tool_response": {"success": True},
            },
        )
        self.run_hook(
            "hooks/post_tool_use.py",
            {
                **self.base,
                "hook_event_name": "PostToolUse",
                "tool_name": "Bash",
                "tool_input": {"command": "npm run build"},
                "tool_response": {"status": "success"},
            },
        )

        ledger = self.read_ledger()
        self.assertIs(ledger["verification_results"][-1]["success"], True)
        self.assertEqual(self.run_hook("hooks/stop_gate.py", {**self.base, "hook_event_name": "Stop"}), {})

    def test_invalid_text_is_not_treated_as_success(self) -> None:
        self.run_hook(
            "hooks/user_prompt_submit.py",
            {**self.base, "hook_event_name": "UserPromptSubmit", "prompt": "Implement a small code fix"},
        )
        self.run_hook(
            "hooks/post_tool_use.py",
            {
                **self.base,
                "hook_event_name": "PostToolUse",
                "tool_name": "apply_patch",
                "tool_input": {
                    "command": "*** Begin Patch\n*** Update File: app.py\n+x\n*** End Patch\n"
                },
                "tool_response": {"success": True},
            },
        )
        self.run_hook(
            "hooks/post_tool_use.py",
            {
                **self.base,
                "hook_event_name": "PostToolUse",
                "tool_name": "Bash",
                "tool_input": {"command": "python3 -m json.tool bad.json"},
                "tool_response": {"stdout": "invalid json"},
            },
        )
        blocked = self.run_hook("hooks/stop_gate.py", {**self.base, "hook_event_name": "Stop"})
        self.assertEqual(blocked.get("decision"), "block")

    def test_post_hook_always_returns_json_for_bad_stdin(self) -> None:
        stdout = self.run_hook_raw("hooks/post_tool_use.py", "{not json")
        self.assertIsInstance(json.loads(stdout), dict)

    def test_stop_hook_always_returns_json_for_bad_stdin(self) -> None:
        stdout = self.run_hook_raw("hooks/stop_gate.py", "{not json")
        self.assertIsInstance(json.loads(stdout), dict)

    def test_stop_hook_failure_payload_names_plugin_issue(self) -> None:
        spec = importlib.util.spec_from_file_location("stop_gate_under_test", ROOT / "hooks/stop_gate.py")
        self.assertIsNotNone(spec)
        self.assertIsNotNone(spec.loader)
        stop_gate = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(stop_gate)

        payload = stop_gate.failure_payload(RuntimeError("boom"))
        message = payload.get("systemMessage", "")
        self.assertIn("plugin bookkeeping/output issue", message)
        self.assertIn("not evidence that your verification failed", message)

    def test_concurrent_post_hooks_return_json_without_ledger_race(self) -> None:
        payloads = [
            {
                **self.base,
                "hook_event_name": "PostToolUse",
                "tool_name": "apply_patch",
                "tool_input": {
                    "command": f"*** Begin Patch\n*** Update File: app_{idx}.py\n+x\n*** End Patch\n"
                },
                "tool_response": {"success": True},
            }
            for idx in range(24)
        ]

        def run(payload: dict) -> dict:
            proc = subprocess.run(
                ["python3", str(ROOT / "hooks/post_tool_use.py")],
                input=json.dumps(payload),
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=self.env,
                check=False,
                timeout=10,
            )
            self.assertEqual(proc.returncode, 0, proc.stderr)
            return json.loads(proc.stdout.strip() or "{}")

        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
            outputs = list(pool.map(run, payloads))

        self.assertTrue(all(output == {} for output in outputs))


if __name__ == "__main__":
    unittest.main()
