# Changelog

## Unreleased

## 1.0.6 - 2026-07-03

- Fixed a ledger lost-update race between concurrent hooks with a file lock;
  the concurrency test now asserts ledger integrity (was 17-20/24 recorded,
  now 24/24).
- Back-merged distribution improvements (fail-open run pattern, exit-code and
  status parsing) into the canonical source and applied the pattern to all
  hooks.
- Added `scripts/sync_dist.py` and `tests/test_dist_sync.py`; the AGENTS.md
  sync rule is now mechanical instead of prose.
- Added declared exit criteria: `scripts/fable_criteria.py`
  declare/revise/satisfy invocations are recorded by PostToolUse and enforced
  by the stop gate for deep work, so the gate enforces the model's own stated
  exit conditions.
- Escalated `normal` tasks to `deep` mid-session when risky paths change
  (auth, migrations, money paths, CI workflows).
- Deep work no longer passes the stop gate on build/typecheck/lint alone; stop
  responses include a one-line status dashboard; unverified changes carry over
  to the next prompt as visible, non-blocking context.
- Irreversible outward commands (package publish, migration deploy,
  infrastructure apply, production deploy) now request confirmation (`ask`)
  instead of passing silently; the 0.1.4 decision to drop automatic denial is
  unchanged.
- Tightened success and coverage heuristics: removed bare `done`/`valid` from
  success matching and replaced substring path matching with token-boundary
  matching.
- Documented the Fable/Opus model-attribution caveat across the
  reconstruction evidence docs.

## 1.0.5 - 2026-06-18

- Added domain-steering guidance so user-provided rules, edge cases,
  constraints, and correction criteria drive implementation and verification.
- Added work-kind selection guidance for build, fix, test, operate, understand,
  plan, analyze, and document tasks.
- Expanded verification guidance for documentation, data analysis, and
  operational proof selection.

## 0.1.4 - 2026-06-16

- Removed automatic PreToolUse blocking for deployment commands such as Vercel,
  Netlify, Firebase, kubectl, and Helm.
- Removed automatic PreToolUse blocking for `supabase db push`.
- Removed automatic PreToolUse blocking for package publish, migration deploy,
  and infrastructure apply/up commands.
- Excluded safe `ship` and `yeet` workflow commands from PreToolUse command
  restrictions.
- Removed the optional Codex Rules prompt for Vercel production deploy commands.

## 0.1.3 - 2026-06-15

- Removed automatic blocking for `git push`, secret-output commands, and permission approval requests.
- Reduced PreToolUse and PostToolUse hook console noise.
- Hardened ledger writes with unique temporary files to avoid concurrent PostToolUse JSON write races.
- Treated explicit exit-code-zero output as success before scanning for failure words.

## 0.1.2 - 2026-06-14

- Fixed new-prompt ledger reset to clear `changed_paths` and reset `coverage_relation` to `none`.
- Updated plugin manifest version to match the release stream.

## 0.1.1 - 2026-06-14

- Added optional Codex Rules examples for high-risk command policy.
- Added a permission profile example for secret-file protection.
- Expanded Korean review-only and no-edit prompt classification.
- Documented `fablish` as a common typo alias while preserving the canonical `fable-ish` name.
- Added timeout protection to hook subprocess tests.
- Recorded changed paths and coarse verification coverage relation in the ledger.
- Made the Stop hook avoid re-blocking when Codex reports an active stop hook continuation.

## 0.1.0 - 2026-06-14

- Converted the original `fable-ish` Codex skill into a Codex plugin bundle.
- Preserved the `fable-ish` plugin name, skill name, and skill directory name.
- Added plugin manifest metadata under `.codex-plugin/plugin.json`.
- Added Codex lifecycle hooks under `hooks/hooks.json`.
- Added standard-library Python hooks for prompt classification, tool guardrails, approval guardrails, post-tool evidence tracking, and stop-time verification review.
- Added a small JSON ledger stored under `PLUGIN_DATA`, with OS temp fallback.
- Replaced the long skill-only instruction set with a focused workflow skill and three references.
- Added unittest coverage for hook wire shapes and stop behavior.
- Removed the old `codex-skill/` skill-only bundle and legacy zip artifact.

### Notes

- Plugin-bundled hooks rely on Codex hook trust. Review and trust them with `/hooks` after install.
- Hooks are guardrails, not a complete sandbox or security boundary.
- The local plugin validator currently rejects manifest-level `hooks`, so this plugin uses the default `hooks/hooks.json` discovery path.
