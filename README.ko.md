# fable-ish Codex

`fable-ish-codex`는 Codex 작업에 검증 중심 워크플로우를 더하는 가벼운
Codex 플러그인입니다. 영문 설명이 기본 문서이며, 이 파일은 한국어 요약입니다.

## 포함 내용

- `.codex-plugin/plugin.json`
- `skills/fable-ish/SKILL.md`
- `hooks/hooks.json`
- `hooks/`
- `scripts/`
- `rules/`
- `examples/`
- `tests/`

## 주요 동작

- 요청을 `quick`, `normal`, `deep`, `blocked`로 분류합니다.
- 일부 고위험 명령을 실행 전에 막습니다.
- 변경 파일과 검증 명령을 JSON ledger에 기록합니다.
- 검증 증거 없이 deep/normal 작업을 끝내려 할 때 이어서 검증하도록 요청합니다.

`git push`, secret 출력 명령, permission approval request는 막지 않습니다.

## 검증

```bash
python3 -m json.tool .codex-plugin/plugin.json
python3 -m json.tool hooks/hooks.json
python3 -m py_compile hooks/*.py scripts/*.py tests/*.py
python3 -m unittest discover -s tests
```

자세한 내용은 [README.md](README.md)를 보세요.
