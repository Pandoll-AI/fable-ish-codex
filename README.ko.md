# fable-ish Codex

[![English](https://img.shields.io/badge/lang-English-blue)](README.md)
[![Korean](https://img.shields.io/badge/lang-%ED%95%9C%EA%B5%AD%EC%96%B4-lightgrey)](README.ko.md)
![Version](https://img.shields.io/badge/version-1.0.5-blue)
![License](https://img.shields.io/badge/license-Apache--2.0-green)
![Codex Plugin](https://img.shields.io/badge/Codex-plugin-111111)
![Python](https://img.shields.io/badge/python-3.10%2B-3776AB)

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

영문 설명이 기본 문서이며, 이 파일은 한국어 요약입니다.

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

`git push`, secret 출력 명령, 배포 명령, database push 명령, package publish,
migration deploy, infrastructure apply/up, permission approval request는 막지
않습니다. 안전한 워크플로 명령인 `ship`과 `yeet`, slash-command 형태, `gstack`
래퍼 형태도 막지 않습니다.

## 검증

```bash
python3 -m json.tool .codex-plugin/plugin.json
python3 -m json.tool hooks/hooks.json
python3 -m py_compile hooks/*.py scripts/*.py tests/*.py
python3 -m unittest discover -s tests
```

## 라이선스와 인용

이 프로젝트는 Apache License 2.0을 사용합니다.

사용, fork, 수정, 수정본 재배포가 가능합니다. 다만 라이선스가 요구하는 license
notice와 attribution notice는 유지해야 합니다. 이 프로젝트를 사용하거나 아이디어를
바탕으로 공개 작업을 한다면 `CITATION.cff`를 기준으로 인용해 주세요.

자세한 내용은 [README.md](README.md)를 보세요.
