# TIGER 200 IT (139260) 단기저점 스코어 — 세션 폴더 (2026-10-16)

SOXL·NAIL 연구와 같은 구조(단일 점수 + 기준선, **표시점수 = 100 − 조건점수, 0에 가까울수록 저점**)를
국내 상장 TIGER 200 IT ETF의 **단기(수 거래일~수 주) 저점**에 맞춘 연구 공간이다.
이번 목표는 **2026-10-06 고점 뒤 급락(−27%)의 단기 저점**이다.

| 무엇 | 어디 |
|---|---|
| **보고서 (먼저 읽을 것)** | `reports/TIGER_IT_short_bottom_2026-10-16.md` |
| 최신 판정 | `output/LATEST.md`, `output/status.json`, 일별 점수 `output/daily.csv` |
| 사전 고정(규칙을 결과보다 먼저 적은 문서) | `PREREGISTRATION.md` |
| 점수 엔진 v1 | `engine/tiger_it_short_bottom.py` |
| 백테스트·표 생성 | `research/backtest.py`, `research/render_tables.py`, 결과 `research/output/` |
| 코드 묶음(txt, 보관용) | `reports/tiger_it_code_bundle_2026-10-16.txt` |
| 자료 수집(GitHub Actions) | `collect_kr.py`, `.github/workflows/kr-collect.yml`, 원자료 `data/` |

## 자료 갱신·판정 다시 하기
1. `RUN_TRIGGER` 내용을 바꿔 이 브랜치에 푸시 → `kr-collect` 워크플로가 GitHub 서버에서 야후·네이버 자료를 받아 `data/`에 커밋한다(약 12분).
2. `git pull` 뒤 `python3 -I engine/tiger_it_short_bottom.py --session <이 폴더> --repo <soxl-data 루트>` → `output/LATEST.md` 갱신.
3. 백테스트: `python3 -I research/backtest.py --session <이 폴더> --repo <루트>` 그리고 `python3 -I research/render_tables.py <이 폴더>`.

## 점수 (v1, 2026-10-16 고정)
P 가격손상 40(20일 낙폭·RSI14·20일선 이격·5일 수익률) · V 거래량수급 20(ETF 거래량·코스피 외국인 5일·삼성+하이닉스 외국인+기관 5일) · S 공포 25(VKOSPI→실현변동성 대체·VIX·공포탐욕·원달러) · G 글로벌반도체 15(SOX 낙폭·RSI).
매수 규칙 v1: 1차 ≤60(20%) · 2차 ≤50 & −5% & 2일(30%) · 3차 ≤40 & −5% & 2일(50%).

투자 권유가 아니다.
