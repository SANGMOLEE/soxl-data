# Investing 딸깍 프로젝트 — 메모리 항목과 세션 목록 (2026-11-20 채취)

claude.ai 프로젝트 「Investing 딸깍」(soxl 주가의 저점·고점 맞추기)에서 비트코인 저점 탐지와 관계된 것만 옮겨 적었다. 프로젝트 지침(prompt)은 비어 있었다. 지식 파일 44개 중 `btc/` 5건·`cycle/` 5건은 이 폴더에 원문 그대로 복사했고, 나머지(SOXL·NAIL·TIGER·원자료 CSV)는 비트코인과 무관해 옮기지 않았다.

## 프로젝트 메모리 중 비트코인 관련 (원문)

### BTC Bottom Score (2026-10-26)
요약: 비트코인(BTC) 사이클 저점·고점 스코어 연구 — 주인님이 기준으로 삼은 지표(PlanB S2F), 8월 판단 정정, 기준 문서 위치
- 비트코인 저점 탐지 스코어를 만들 때 중심으로 잡은 것은 PlanB의 stock-to-flow 모형과 그 사이트에 있던 여러 지표였음
- 2026년 8월 중순 코인이 더 하락할 것으로 예상했으나, 그 뒤 크게 상승해 버티고 있어 최저점은 지나온 것 같다고 판단(2026-10-26) — 당시 스코어 판단이 잘못 짚은 것으로 봄
- 재점검 결과 문서: 프로젝트 `btc/비트코인_저점판정_재점검_2026-10-26.md` (8월 BT 세션의 BCPS/BBS 설계가 바탕)

### SOLT BITU STRATEGY (2026-10-31)
요약: SOLT·BITU(솔라나·비트코인 2배 ETF) 사이클 전략 — 주인님의 운용 원칙(상승기만 보유, 하락기 현금)
- SOLT·BITU 전략은 비트코인 상승기에만 보유하는 전략 — 비트코인 하락기에는 하지 않고 현금 보유, 반등 시 다시 매수함 (전 기간 보유로 해석하지 말 것)

### Findings (2026-11-12) 중 비트코인·사이클 관련 줄
- Bitcoin–SOX relationship: BTC functions as a shared-fear indicator at shock lows (gap of 1–9 days across 2018/2020/2025 episodes) but is not a reliable predictive signal
- Halving-driven BTC cycle regularity (1,050–1,068 day variance: 18 days) vs. SOX inventory-cycle irregularity (587-day variance) makes a stable lead-lag structurally impossible
- Hindsight vs. real-time discipline: always distinguish hindsight-identified lows from real-time-available entry points; sample populations must match the actual trading scenario
- Statistical claims must report sample sizes; n<15 cases must be listed individually rather than summarized as medians
- 사례 통계는 중앙값 하나가 아니라 범위(25~75%)로 말할 것. 반등 예측 시 "하위 30% 경로"를 함께 제시
- 매도 목표 숫자는 근거와 함께 한 번 정하고 새 사실이 나올 때만 바꿀 것(며칠 새 6번 넘게 바뀌어 신뢰를 잃음)
- 규칙 매매는 성과가 좋았고 손실은 규칙 밖 매수에서 나옴 — 한 번 맞은 결과로 규칙을 바꾸지 말 것

(SOXL 단타·NAIL·TSS·TIGER 메모리는 비트코인과 무관해 옮기지 않았다.)

## 비트코인 관련 세션(채팅) 목록 — 원문은 Investing 딸깍 프로젝트에 남아 있음
| 날짜 | 세션 제목 | 산출물 소재 |
|---|---|---|
| 2026-11-14 | 비트코인 저점스코어 BBS 산출 | 문서 없음(세션 안에만 있음) |
| 2026-11-11 | 비트코인 사이클 위치 판단 | BCPS v1.1 공식 — 저장소 `research/bcps/BCPS_v1.1_TradingView.pine`로 이미 이관됨(어느 세션 산출물인지는 미확인) |
| 2026-10-31 전후 | (세션 미확인) BBS 차트 아티팩트 | `charts/BTC_BBS_full_history_chart.html`, `charts/SOLT_virtual_BTC_BBS_chart.html` — PC Downloads 10/31 저장본 |
| 2026-11-12 | RSI·200일선 지표 활용 | — |
| 2026-10-28 | 비트코인 저점 탐지 재분석 / 버블 붕괴 시기 분석 | `cycle/강세장_4-5년차_가속론_검증_2026-10-28.md` |
| 2026-10-26 | 비트코인 저점 탐지 스코어 재분석 | `btc/비트코인_저점판정_재점검_2026-10-26.md` |
| 2026-11-01, 10-31 | 전략 검증 및 수정 / 전략 백테스팅 및 최적화 | `btc/SOLT_BITU_*` 4건 |
| 2026-08-03 | (BT 세션) BBS v1.0a/v1.1 설계·실측 | `archive_2026-08/` 2건 |

세션 본문은 옮기지 않았다. 세션에만 있고 문서로 남지 않은 결론이 필요하면 해당 세션을 열어 문서로 뽑아 이 폴더에 추가한다.
