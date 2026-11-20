# 비트코인 사이클 저점 탐지 — 통합 지식 색인 (2026-11-20)

세 곳에 흩어져 있던 비트코인 저점 탐지 지식을 이 저장소 한 곳에 모았다. **원본은 이 저장소(`research/`)이고, claude.ai 프로젝트 「BTC딸깍」은 그 사본을 읽는다.** 결론이 바뀌면 저장소 문서를 먼저 고치고, 프로젝트 사본을 다시 올린다.

| 출처 | 어디서 왔나 | 이 저장소의 위치 |
|---|---|---|
| ① Claude Code 세션 | 저장소 브랜치 `ccr-b178db42-c7x4uo`에서 직접 만든 연구·코드·알람 | `research/` 바로 아래 (아래 A절) |
| ② Investing 딸깍 프로젝트 | claude.ai 프로젝트 지식 `btc/`·`cycle/` 10건 + 프로젝트 메모리 | `research/knowledge/investing_project/` (B절) |
| ③ PC Downloads 보관본 | 8월 BT 세션 BBS 설계·실측 보고서, BBS 차트, 영상 스크립트, 온체인 갭 자료 | `research/knowledge/archive_2026-08/`, `charts/`, `video/`, `data/` (C절) |

읽는 순서: `research/BTC_BOTTOM_MASTER_2026-11-20.md`(종합 연구) → `research/pc_project_pack/00_PROJECT_KNOWLEDGE_btc_cycle.md`(요약 1장) → `research/BOTTOM_DETECTION_PLAN_2026-11-20.md`(계획 원문) → 필요한 것만 아래에서.

---

## A. Claude Code 세션 산출물 (`research/`) — 현재 유효한 기준

### 계획·전략·기록
| 파일 | 내용 | 상태 |
|---|---|---|
| `score100_research_2026-11-20.md` (+`score100.py`, `score100_features.py`, `score100_study.py`) | **100점 연속 점수 v3**와 정밀 트리거 연구. 지표 25개 진단, 결합·창·임계 민감도, 교차 검증. 결론: 점수로는 첫 저점/최종 저점 구분 불가, 당일 포착은 "후보일+익일 확인"으로 4/4(가짜 11/16) | 최신 |
| `BTC_BOTTOM_MASTER_2026-11-20.md` | **종합 연구.** 어디(57~58k 중앙, A/B/C)·언제(12/3~12/16 45%)·얼마(ATH −50~−63%)·신호 체계(알람→투매→반전→상승 확인)·3분할 집행·무효 규칙·과거 저점 서명표·판단 이력 | **읽기 시작점** |
| `BOTTOM_DETECTION_PLAN_2026-11-20.md` | 최종 저점 탐지 계획. 지표 세 층(빠른·가치·시간), 사전 등록 시나리오(A 45% / B 30% / C 25%), 시기 창(12/3~12/16 45%), 3분할 매수, 알람 체계 | **기준 문서** |
| `FINAL_STRATEGY_SOLT_BITU.md` | SOLT·BITU 2배 ETF 사이클 전략서 v2 (상승기만 보유, 하락기 현금) | 기준. 검증 보고서는 B절 |
| `forward_log.md` / `forward_log.csv` | 전방 검증 기록(사전 등록 10/31). 엔진 v2 자동 기록 | 진행 중 |
| `cycle_recheck_2026-11-20.md` (+`.py`) | 11/20 사이클 재검(고점 후 410일, 첫 저점 후 143일, 중간선거 +17일) | 최신 |
| `vix_bottom_study_2026-11-20.md` (+`vix_bottom_study.py`) | VIX가 저점 탐지에 보탬이 되는지 실측. 결론: 점수에 넣지 않음(사이클 저점 VIX 21~22로 평범, 방향 비일관, VIX 급등 단독은 신호 아님). 2단계+VIX≥30은 "충격형" 꼬리표만 | 최신 |
| `video_compare_2026-11-20.md` (+`video_compare_calc.py`) | 자산제곱 「2027년 불장」 영상 주장 대조 — 맞는 것·틀린 것·반영한 것 | 최신 |
| `btc_sol_realdata_findings_2026-10-31.md` | BTC·SOL·BITU·SOLT 실측(추정치 정정, BTC→SOL 시차) | 유효 |
| `btc_bottom_and_sol_timing_2026-10-31.md` | 10/31 저점 재분석 + SOL 시차 | 유효(11/20 재검으로 갱신됨) |
| `btc_halving_cycle_bottom_2026.md` | 10/27 반감기 사이클 저점 연구("7/1 저점 확률 55~60%") | 11/20 계획에서 25%로 하향됨 — 이력용 |
| `monthly_strategy_2026-11_2027-06.md` | 나스닥 기준 월별 시기 판정(종목 추천 없음) | 참고 |
| `sox_cycle_low_2027_check.md` | SOX 저점 창(2027-02~04) 재검증 — 시간 층 4번째 창과 겹침 | 참고 |

### 코드·알람·자료
| 파일 | 역할 |
|---|---|
| `bottom_detector.py` | 빠른 층 저점 탐지 점수 0~8 (A~H), 1·2·3단계, 게이트·저점 구간, `alarm_state.json` 생성 |
| `bcps/bcps_rebuild.py`, `bcps/bcps_series.csv`, `bcps/bcps_v11_embedded.csv` | 가치 층 BCPS(0~100) 재계산. v1.1 공식은 Investing 프로젝트에서 왔고 여기서 오늘까지 재산출 |
| `bcps/BTC_BOTTOM_DETECTOR_v2.pine` | **트레이딩뷰 v2**: 빠른 층 8조건을 차트에서 계산(점수·단계·게이트·저점 구간·반전) + BCPS v1.2 내장 + 조건표 + 경보 7종. v1.2를 대체 |
| `bcps/BTC_SCORE100_v3.pine` | 트레이딩뷰 v3: 100점 점수(Z·T 백분위, MVRV 내장)·게이트·후보일·정밀 트리거·정점 통과·경보 6종 |
| `bcps/BTC_BOTTOM_LEVELS_v1.pine` | 트레이딩뷰 가격선: 사전 등록 가격선 10개 + 200일·200주선 + 실현가 배수선 + 종가 이탈/돌파 경보 |
| `bcps/BCPS_v1.1_TradingView.pine`, `bcps/BCPS_v1.2_TradingView.txt`, `bcps/make_pine.py` | 트레이딩뷰 BCPS 단독 지표(v1.2는 점수 내장판, 그대로 써도 됨) |
| `cycle_engine_v2.py` | 2배 ETF 모의 장부 엔진(기준). `full_cycle_backtest.py`는 폐기된 v1 |
| `cycle_signal_daily.py` | 엔진 v2 일일 상태 → `forward_log.csv` |
| `bottom_signal_study.py` | 저점 직후 반등 신호 7종 연구(가짜 반등 구분) |
| `btc_sol_analysis.py`, `solt_*_search*.py`, `build_solt_chart.py`, `charts/solt_btc_cycle_chart.html` | SOL 시차·SOLT 진입/이탈 탐색·차트 |
| `alarm_state.json` | 알람 상태(11/20: 점수 4, 1단계, BCPS 21.1, MVRV 1.16, 알람 없음·주의 있음) |
| `../.github/workflows/bottom-alarm.yml` | 자료 갱신 → BCPS → 탐지기 → 알람이면 GitHub 이슈. main 병합 뒤 예약 실행 |
| `../.github/workflows/cycle-signal.yml`, `crypto-once.yml`, `daily.yml` | 엔진 일일 기록, 크립토 자료 수집, 주가 자료 수집 |
| `../data/crypto/` | BTCUSD·SOLUSD·BITU·SOLT·IBIT 일봉(Yahoo), `BTC_ONCHAIN.csv`(Coin Metrics MVRV·실현가격 등) |
| `pc_project_pack/` (+zip) | 프로젝트에 올릴 묶음 8건(00 요약 ~ 07 트레이딩뷰) |

---

## B. Investing 딸깍 프로젝트에서 가져온 것 (`knowledge/investing_project/`)

### `btc/` — 비트코인 저점 판정과 SOLT·BITU 검증
| 파일 | 내용 | 현재 계획과의 관계 |
|---|---|---|
| `비트코인_저점판정_재점검_2026-10-26.md` | ① 8월 "추가 하락" 판단이 틀린 이유(모형이 과거 3회 저점 깊이 −77~−84%·시점을 요구, 이번은 −54%·반감기 640일 전) ② 최저점 통과 확률 60~65% ③ S2F·PlanB 지표 ④ 중간선거 뒤 패턴 ⑤ 2028 반감기 전 전망. 2025-10-14 이후 일봉 없이 근사 경로 사용 | 11/20 계획은 "6/30이 이미 바닥" 확률을 25%로 낮춤(근거: 11/14 저점 64,128 이탈, 200일선 9일 하회, 200주선 이탈, ETF 11월 유출). 이 문서는 그 전 판정의 근거로 보존 |
| `SOLT_BITU_전략검증_v1_2026-10-31.md` | 전략서 독립 검증 v1. 전략서 성적(+11,007%, 한 사이클 +2,202%)은 과대 — 실제 체결 조건으로 +499% / 최대낙폭 −62%, 연복리÷낙폭 0.93(현물과 같음). 부풀려진 원인 4가지(문서≠코드, 주말 체결, 상장 전 합성, 비용) | 전략서 v2·엔진 v2가 이를 반영 |
| `SOLT_BITU_검증_최적화연구_v2_2026-10-31.md` | v1 요약 + 수익률 최적화. "상승기를 미리 알 수 있다면 SOLT 보유가 74~105배로 압도적이나 실시간으로는 알 수 없다" | v2.1로 대체됨 |
| `SOLT_BITU_검증_최적화연구_v2.1_2026-10-31.md` | v2의 구현 오류 정정(약세장 판정이 신고가 뒤에도 안 풀리던 것) | 유효 |
| `SOLT_BITU_전략서v2_검증_오류수정_개선안_2026-11-01.md` | 전략서 v2·엔진 v2 독립 재현(`v2check.py`). 수치는 엔진 기준으로 일치하나 "10/31 기준"이 실제론 10/26 기준(거래일 달력 끊김), 코드 버그 2건(2028 최종매도 활성 시점, 약세장 저점 갱신), 문서 오류 목록 | 버그 (1)은 현재 엔진에 반영 확인, (2)는 미확인 — D절 3항 |

### `cycle/` — 사이클 자산 전반(비트코인은 그 일부)
| 파일 | 내용 | 비트코인 관련 부분 |
|---|---|---|
| `cycle_research_master_2026-10-17.md` | 사이클 산업 선별(A등급 7개)·저점 동시성·위상 지도 마스터 | "비트코인은 BTC 세션 판정이 우선" — 이 문서는 BTC 판정을 바꾸지 않음 |
| `trough_sync_study_v1_2026-10-17.md` | SOXL 저점 신호가 켜질 때 다른 사이클 자산도 바닥인가(2016·2018·2020·2025 동시 바닥, 2022-10 예외). 돈은 SOXL이 가장 많이 범 | 저점 동시성 맥락. BTC–SOX는 "충격 저점에서 공포 공유 지표(1~9일 간격), 예측 신호는 아님"(Findings) |
| `cycle_industry_leverage_map_v2_2026-10-17.md` | 사이클 산업 레버리지 지도 v2(선별판) | 암호화폐 레버리지(BITU·SOLT 등) 티커 목록 |
| `산업사이클_레버리지지도_2026-10-17.md` | 60종 간이 선별표 | **폐기 지시된 문서**(주인님 지시, 삭제는 확인 대기) — 이력용 |
| `강세장_4-5년차_가속론_검증_2026-10-28.md` | "1~3년 완만 → 4~5년 가속" 시간표 검증(법칙 아님, 타이밍 도구 신뢰도 낮음) + 버블 지속/종료 시나리오 | `monthly_strategy_2026-11_2027-06.md`의 전제 |

### `project_memory_and_sessions_2026-11-20.md`
프로젝트 메모리(BTC Bottom Score, SOLT BITU STRATEGY, Findings) 원문과 비트코인 관련 세션 목록. 세션 본문은 옮기지 않았다.

---

## C. PC Downloads 보관본 (`knowledge/archive_2026-08/`, `charts/`, `video/`, `data/`)

| 파일 | 내용 | 상태 |
|---|---|---|
| `archive_2026-08/BBS_v1.0a_v1.1_최종_의사결정_보고서_20260803.md` | BBS(비트코인 저점 스코어) v1.0a 합의문·v1.1 설계안 의사결정(8/3). 핵심 명령: 단일 총점 폐지, 두 축 분리, 가격 R² 게이트 폐지, 분위수 창 사전 검증, 원자료 확정 후 재산출 | BCPS v1.1의 전신. 설계 원칙은 유효, 수치는 낡음 |
| `archive_2026-08/BTC_수정형_저점모델_실제가격_실측_현재재검증_20260803.md` | Bitfinex 일봉(2012-02~2025-10-13)으로 수정형 저점모델 실측(8/3, 현물 $63,061). "저점 매력도 중상 / 바닥 확인 혼재" | 8월 판단(추가 하락 예상)의 근거 — 10/26 재점검에서 "틀린 판단"으로 정리됨 |
| `charts/BTC_BBS_full_history_chart.html` | BTCUSD·BBS 스코어 전 기간 차트(자료 내장, 10/31 저장) | 참고 |
| `charts/SOLT_virtual_BTC_BBS_chart.html` | SOLT(가상)·BTCUSD·BBS 차트 | 참고 |
| `video/자산제곱_2027불장_영상스크립트_2026-11-20.txt` | 영상 전문 스크립트(자막). 대조 결과는 `research/video_compare_2026-11-20.md` | 원자료 |
| `data/btc_coinmetrics_gap_2026-05-24_2026-08-05.json` | Coin Metrics 온체인 갭 메우기 자료(74일: MVRV·시총·해시레이트·발행·가격·공급) | `data/crypto/BTC_ONCHAIN.csv`에 이미 반영됨(확인) — 원자료 보관용 |

---

## D. 지식 간 모순·미해결 항목 (확인된 것과 확인되지 않은 것)
1. **"최저점 통과" 확률**: 8/3 실측 "추가 하락" → 10/26 "통과 60~65%" → 10/27 "55~60%" → 11/20 "25%(시나리오 C)". 가장 최신인 11/20 계획이 기준이며, 갱신 규칙(60,500 이탈 → 15%, 200일선 위 마감 → 40%)에 따라 바뀐다.
2. **BCPS와 BBS 이름**: 8월 문서는 BBS, 11월 문서는 BCPS(v1.1·v1.2). 같은 계보(두 축 분리 설계)이나 공식이 같은지는 미확인 — v1.1 공식은 `bcps/BCPS_v1.1_TradingView.pine`가 기준.
3. **엔진 v2 버그 2건**(11/1 검증 보고서): (1) 2028-01-01 최종매도 활성화는 현재 코드에 `TOP_FORCE_FROM = 2028-01-01`로 들어가 있음(확인). (2) 약세장 저점이 신고가 뒤에도 갱신되지 않던 문제는 코드만 봐서는 수정 여부를 판정하지 못함(미확인 — 11/1 보고서의 `v2check.py`로 재현해 볼 것).
4. **온체인 갭 자료(5/24~8/5)**: `data/crypto/BTC_ONCHAIN.csv`에 74일 전부 MVRV·실현가격이 채워져 있음(확인). `knowledge/data/`의 JSON은 원자료 보관용.
5. **VIX**: 점수 본체에 넣지 않기로 결정(`vix_bottom_study_2026-11-20.md`). DVOL(옵션 내재변동성)은 자료가 없어 미시험.
6. **폐기 지시 문서**(`산업사이클_레버리지지도_2026-10-17.md`)는 이력용으로만 두었다.

## E. 갱신 규칙
- 결론이 바뀌면 `research/`의 해당 문서 → `pc_project_pack/00_PROJECT_KNOWLEDGE_btc_cycle.md` → 이 README의 D절 순으로 고친다.
- 프로젝트 「BTC딸깍」 지식은 이 폴더의 사본이다. 저장소를 고친 뒤 바뀐 파일만 프로젝트에 다시 올린다.
- 새 세션 산출물은 출처 폴더(`investing_project/` 또는 `research/`)에 날짜를 붙여 넣고, 이 색인에 한 줄 추가한다.
