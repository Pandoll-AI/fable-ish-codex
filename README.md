# fable-ish Codex

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
  deletes, destructive Git cleanup, production deploy commands, infrastructure
  writes, database migrations, and package publishing.
- `PostToolUse` records changed-file signals, verification commands, failures,
  and coarse coverage information in a small JSON ledger under `PLUGIN_DATA`.
- `Stop` asks Codex to continue when normal or deep work has no verification
  evidence, capped to avoid continuation loops.

By design, `git push`, secret-output commands, and permission approval requests
are not blocked by this plugin.

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
configuration. Secret output is intentionally not blocked by the hooks.

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

---

# fable-ish Codex 한국어

`fable-ish-codex`는 떠나가버린 Fable을 그리워하는 사람들을 위한 작은
플러그인입니다.

남기고 싶었던 것은 Fable이라는 이름이나 성격이 아니라, 일하는 습관이었습니다.
목표를 대충 처리하지 않고, 검증 가능한 작업 단위로 바꾸고, 코드가 존재한다는
이유만으로 완료라고 말하지 않는 습관입니다.

이 플러그인은 Fable이라는 모델 자체를 재현한다고 주장하지 않습니다. 대신 Fable이
유용하게 느껴졌던 다음 루프를 Codex에서 더 쉽게 유지하려고 합니다.

1. 사용자 목표를 구체적인 작업 단위나 불변식으로 바꿉니다.
2. 현재 작업에서 무엇이 깨질 수 있는지 정합니다.
3. 멈추기 전에 필요한 관찰 가능한 증거를 고릅니다.
4. 가장 작은 일관된 단위를 구현합니다.
5. 가장 좁지만 충분한 검증을 실행합니다.
6. 실패 가능성이 높은 경로를 다시 확인합니다.
7. 검증된 경계에서만 멈추거나, 남은 blocker를 명확히 적습니다.

짧게 말하면, 이 플러그인의 목적은 동적인 종료 조건, 증거 기반 완료, 위험도에
맞춘 리뷰, 그리고 실제로 관찰한 검증만 보고하는 습관을 Codex 작업에 붙이는
것입니다.

`fable-ish-codex`는 Codex 작업에 검증 중심 워크플로우를 더하는 가벼운
Codex 플러그인입니다. `fable-ish` 스킬과 lifecycle hook을 함께 묶어,
작업 위험도를 분류하고, 도구 실행 증거를 기록하고, 의미 있는 변경에는
최종 보고 전에 검증을 요구합니다.

이 플러그인은 작게 유지됩니다. 서버, 데이터베이스, 외부 API, 백그라운드
워커, LLM 분류기를 추가하지 않습니다.

## 포함 파일

- 플러그인 manifest: `.codex-plugin/plugin.json`
- 스킬: `skills/fable-ish/SKILL.md`
- hook 설정: `hooks/hooks.json`
- hook entrypoint:
  - `hooks/user_prompt_submit.py`
  - `hooks/pre_tool_use.py`
  - `hooks/post_tool_use.py`
  - `hooks/stop_gate.py`
- 표준 라이브러리만 사용하는 Python helper: `scripts/`
- 선택형 command-policy 예시: `rules/`
- 선택형 permission-profile 예시: `examples/`
- contract test: `tests/`

## 동작

- `UserPromptSubmit`은 요청을 `quick`, `normal`, `deep`, `blocked`로 분류하고
  짧은 작업 지침을 주입합니다.
- `PreToolUse`는 파괴적 삭제, 파괴적 Git cleanup, production deploy, infra write,
  database migration, package publish 같은 일부 고위험 로컬 명령을 막습니다.
- `PostToolUse`는 변경 파일, 검증 명령, 실패, 대략적인 검증 커버리지를
  `PLUGIN_DATA` 아래 작은 JSON ledger에 기록합니다.
- `Stop`은 normal/deep 작업에 검증 증거가 없을 때 Codex가 이어서 검증하도록
  요청합니다. 무한 루프를 막기 위해 횟수는 제한됩니다.

의도적으로 `git push`, secret 출력 명령, permission approval request는 막지 않습니다.

## 설치

이 저장소를 Codex 플러그인 설치 방식에 맞게 설치하세요. 설치 또는 업데이트 후
Codex를 재시작하고, hooks UI에서 bundled hook을 검토하고 trust해야 기계적
가드레일이 동작합니다.

Codex는 hook 설정을 아래 경로에서 찾습니다.

```text
hooks/hooks.json
```

hook이 꺼져 있거나 trust되지 않은 경우에도 스킬 지침은 사용할 수 있지만,
기계적 가드레일은 실행되지 않습니다.

## 선택형 rules와 permissions

기본 가드레일은 hook입니다. 더 강한 로컬 command policy가 필요하면
`rules/fable-ish.rules`를 Codex rules layer에 맞게 적용하세요.

secret 파일 접근 정책이 필요하면 `examples/permissions.toml`을 Codex 설정에 맞게
조정하세요. secret 출력은 hook에서 의도적으로 막지 않습니다.

## 검증

저장소 루트에서 아래 검증을 실행합니다.

```bash
python3 -m json.tool .codex-plugin/plugin.json
python3 -m json.tool hooks/hooks.json
python3 -m py_compile hooks/*.py scripts/*.py tests/*.py
python3 -m unittest discover -s tests
```

Codex plugin/skill validator 스크립트가 로컬에 있다면 아래도 실행할 수 있습니다.

```bash
python3 /path/to/plugin-creator/scripts/validate_plugin.py .
python3 /path/to/skill-creator/scripts/quick_validate.py skills/fable-ish
```

## 라이선스와 인용

이 프로젝트는 Apache License 2.0을 사용합니다.

사용, fork, 수정, 수정본 재배포가 가능합니다. 다만 라이선스가 요구하는 license
notice와 attribution notice는 유지해야 합니다. 이 프로젝트를 사용하거나 아이디어를
바탕으로 공개 작업을 한다면 `CITATION.cff`를 기준으로 인용해 주세요.

## 한계

Codex hook은 가드레일이지 완전한 보안 경계가 아닙니다.

- hook은 검토 및 trust 후에만 실행됩니다.
- `PreToolUse`가 모든 실행 경로를 가로채지는 못합니다.
- `PostToolUse`는 이미 완료된 명령의 부작용을 되돌릴 수 없습니다.
- Stop hook은 무한 continuation loop를 막기 위해 횟수가 제한됩니다.
- rules와 permission profile은 예시이며 자동 설치되는 정책이 아닙니다.

더 강한 보장이 필요하면 sandbox, approval, test, lint, code review, deployment policy를
함께 사용하세요.
