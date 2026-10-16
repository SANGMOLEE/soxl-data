# TIGER 200 IT (139260) 단기저점 스코어 — 세션 폴더 (2026-10-16 시작)

SOXL·NAIL 연구와 같은 구조(단일 점수 + 기준선, **표시점수 = 100 − 조건점수, 0에 가까울수록 저점**)를
국내 상장 TIGER 200 IT ETF의 **단기(수 거래일~수 주) 저점**에 맞춘 연구 공간이다.
사이클 최저점이 목표였던 NAIL R9와 달리, 이번 목표는 **이번 주(2026-10 셋째 주) 하락 추세의 단기 저점**이다.

| 무엇 | 어디 |
|---|---|
| 사전 고정(규칙을 결과보다 먼저 적은 문서) | `PREREGISTRATION.md` |
| 자료 수집 스크립트(GitHub Actions에서 실행) | `collect_kr.py`, 워크플로 `.github/workflows/kr-collect.yml` |
| 점수 엔진 | `engine/tiger_it_short_bottom.py` |
| 최신 판정·보고서 | `output/LATEST.md`, `reports/` |
| 원자료 | `data/` (매번 전 기간 재수집) |

## 자료 받는 법
작업 컨테이너에서는 시세 사이트가 막혀 있다. `RUN_TRIGGER` 내용을 바꿔 이 브랜치에 푸시하면
`kr-collect` 워크플로가 GitHub 서버에서 Yahoo·KRX 자료를 받아 `data/`에 커밋한다.

투자 권유가 아니다.
