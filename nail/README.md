# NAIL 사이클 저점 매수 연구 (soxl-data 안의 별도 연구 공간)

NAIL(Direxion 3배 주택건설 ETF)의 사이클 최저점 근처 매수 연구. SOXL 연구와 같은 구조(단일 점수 + 기준선)이며, 현행 모형은 **R9**(2026-09-23 동결)다.

| 무엇 | 어디 |
|---|---|
| **인계 문서(모든 이력·규칙·상태값, 가장 먼저 읽을 것)** | `NAIL_HANDOFF.md` |
| 최신 판정 | `output/LATEST.md` |
| 전진 기록(평가일별 1행, 덮어쓰지 않음) | `output/score_log.csv` |
| 엔진 v1.2 · 수기 계산기 | `engine/` |
| 수집·판정 스크립트 | `scripts/fetch_nail_data.py`, `scripts/run_daily.py` |
| 원자료(매 실행 전 기간 재수집) | `data/prices`, `data/macro`, `data/dividends`, `data/fetch_status.json` |
| 연구 코드·사전 고정 문서·결과 | `research/` |
| 보고서 | `reports/` |

## 새 Claude Code 세션 시작 프롬프트

GitHub에서 이 저장소(`SANGMOLEE/soxl-data`)로 새 Claude Code 세션을 열고 첫 메시지로 붙여 넣는다.

```text
이 세션은 NAIL(3배 주택건설 ETF) 사이클 저점 매수 연구를 이어받는 새 세션이다.

1. 저장소의 nail/NAIL_HANDOFF.md를 처음부터 끝까지 읽어라. 길면 나눠 읽되 §0, Part A 전체, Part B의 §1·§4·§6-0은 빠짐없이 읽어라. 그다음 nail/output/LATEST.md와 nail/reports/ 의 가장 최근 보고서를 읽어라.
2. NAIL_HANDOFF.md §0-2의 규칙(호칭, 출력 형식, 판단 원칙)을 이 세션 내내 지켜라.
3. 다 읽었으면 다섯 줄 이내로 보고하라: 현행 모형과 매수 기준, 마지막 판정일과 표시점수, 모형 가상 장부 상태, 다음에 확인할 일정, 미해결 과제 1순위.
4. 그다음 내 지시를 기다려라. 점수를 다시 계산하라고 하면 nail/data/fetch_status.json 날짜를 보고, 최신 종가가 아니면 nail/RUN_TRIGGER 내용을 바꿔 푸시해 nail-research 워크플로를 돌린 뒤 결과를 받아 보고하라.
5. 판정이나 연구 내용이 바뀌는 작업을 마치면 NAIL_HANDOFF.md의 Part A와 Part B §6-0을 고쳐 같은 경로에 덮어쓰고 커밋·푸시하라. 새 인계 파일을 따로 만들지 마라.
```

## 자료 수집·판정 실행

- **자동:** `.github/workflows/nail-research.yml`. main 브랜치에 있으면 평일 22:50 UTC(공용 수집기 22:30 뒤) 실행.
- **수동:** Actions → nail-research → Run workflow(main에 있을 때), 또는 작업 브랜치에서 `nail/RUN_TRIGGER` 내용을 바꿔 푸시.
- 순서: `fetch_nail_data.py`(Yahoo 18종목 전 기간 + FRED 43종) → `run_daily.py`(엔진 원자료 모드) → 같은 브랜치에 커밋.
- 로컬: `pip install pandas numpy exchange_calendars` 후 `python nail/scripts/run_daily.py` (수집은 인터넷이 되는 곳에서만).

## 주의

- 모든 과거 성과는 인샘플이다. R9는 동결 상태이며 이후 사건은 전진 기록으로만 평가한다. 새 규칙은 결과를 보기 전에 `research/`에 문서로 고정한다.
- 조정종가는 새 분배금마다 과거까지 바뀐다. 그래서 `nail/data`는 덧붙이지 않고 매번 전 기간을 다시 받는다. 판정의 기록은 `output/score_log.csv`가 맡는다.
- 투자 권유가 아니다.
