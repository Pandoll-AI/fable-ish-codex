# fable-ish Codex

[![English](https://img.shields.io/badge/lang-English-blue)](README.md)
[![Korean](https://img.shields.io/badge/lang-%ED%95%9C%EA%B5%AD%EC%96%B4-lightgrey)](README.ko.md)
![Version](https://img.shields.io/badge/version-0.1.4-blue)
![License](https://img.shields.io/badge/license-Apache--2.0-green)
![Codex Plugin](https://img.shields.io/badge/Codex-plugin-111111)
![Python](https://img.shields.io/badge/python-3.10%2B-3776AB)

`fable-ish-codex` is for people who miss Fable.

Fable is gone. What felt worth keeping was not a name or a persona, but a habit
of work: take a goal seriously, turn it into something verifiable, and do not
call it done just because the code exists.

This plugin does not try to recreate Fable as a model. It tries to carry forward
the part of the workflow that made Fable useful:

1. Turn the user's goal into a concrete work unit or invariant.
2. Decide what can break, based on the risk of the task.
3. Pick an observable exit proof before stopping.
4. Implement the smallest coherent slice.
5. Verify with the narrowest useful proof.
6. Re-check likely failure paths.
7. Stop only at a verified boundary, or name the remaining blocker.

In short: dynamic exit criteria, evidence-backed completion, risk-proportional
review, and plain reporting about what was actually verified.

`fable-ish-codex` is a lightweight Codex plugin for verification-gated coding work.
It packages the `fable-ish` skill with lifecycle hooks that classify task risk,
record tool evidence, and remind Codex to verify meaningful changes before final
reporting.

The plugin is intentionally small. It does not add a server, database, external
API dependency, background worker, or LLM classifier.

## What It Includes

- Plugin manifest: `.codex-plugin/plugin.json`
- Skill: `skills/fable-ish/SKILL.md`
- Hook configuration: `hooks/hooks.json`
- Hook entrypoints:
  - `hooks/user_prompt_submit.py`
  - `hooks/pre_tool_use.py`
  - `hooks/post_tool_use.py`
  - `hooks/stop_gate.py`
- Standard-library Python helpers under `scripts/`
- Optional command-policy examples under `rules/`
- Optional permission-profile examples under `examples/`
- Contract tests under `tests/`

## Behavior

- `UserPromptSubmit` classifies requests as `quick`, `normal`, `deep`, or
  `blocked`, then injects compact task guidance.
- `PreToolUse` blocks a small set of high-risk local actions such as destructive
  deletes, destructive Git cleanup, infrastructure destruction, and risky patch
  edits.
- `PostToolUse` records changed-file signals, verification commands, failures,
  and coarse coverage information in a small JSON ledger under `PLUGIN_DATA`.
- `Stop` asks Codex to continue when normal or deep work has no verification
  evidence, capped to avoid continuation loops.

By design, `git push`, secret-output commands, deployment commands, database
push commands, package publishing, migration deploy commands, infrastructure
apply/up commands, and permission approval requests are not blocked by this
plugin.

## Install

Install this repository as a Codex plugin through your preferred Codex plugin
installation flow. After installing or updating the plugin, restart Codex and
review/trust the bundled hooks in the Codex hooks UI before relying on them.

Codex discovers plugin hooks from:

```text
hooks/hooks.json
```

If hooks are disabled or not trusted, the skill still works as reusable guidance,
but the mechanical guardrails will not run.

## Optional Rules And Permissions

The hook layer is the default guardrail. For stronger local command policy, adapt
`rules/fable-ish.rules` into an active Codex rules layer.

For secret-file access policy, adapt `examples/permissions.toml` into your Codex
configuration. Secret output, deployment commands, database push commands,
package publishing, migration deploy commands, and infrastructure apply/up
commands are intentionally not blocked by the hooks.

## Validation

Run these checks from the repository root:

```bash
python3 -m json.tool .codex-plugin/plugin.json
python3 -m json.tool hooks/hooks.json
python3 -m py_compile hooks/*.py scripts/*.py tests/*.py
python3 -m unittest discover -s tests
```

If you have the Codex plugin and skill validator scripts locally, also run:

```bash
python3 /path/to/plugin-creator/scripts/validate_plugin.py .
python3 /path/to/skill-creator/scripts/quick_validate.py skills/fable-ish
```

## License And Citation

This project uses the Apache License 2.0.

You can use it, fork it, change it, and redistribute modified versions. Keep the
license and attribution notices that the license requires. If you use the project
or adapt its ideas in public work, please cite it with `CITATION.cff`.

## Limits

Codex hooks are guardrails, not a complete security boundary.

- Hooks must be reviewed and trusted before they run.
- `PreToolUse` does not intercept every possible execution path.
- `PostToolUse` cannot undo side effects from completed commands.
- The Stop hook is capped to avoid infinite continuation loops.
- Optional rules and permission profiles are examples, not silently installed
  policy.

Use sandboxing, approvals, tests, linters, code review, and deployment policies
for stronger enforcement.
