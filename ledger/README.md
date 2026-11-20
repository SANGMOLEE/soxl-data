# 예측 원장 (ledger)

Claude가 주인님께 드린 예측·조언을 기록하고, 매일 가격 데이터로 자동 채점하는 곳입니다.

## 파일
| 파일 | 내용 | 누가 고치나 |
|---|---|---|
| `predictions.csv` | 예측 원장 (한 줄 = 예측 1건) | Claude가 `score.py add`로 추가 |
| `manual_prices.csv` | 공식 가격이 아직 없는 날의 추정 가격 | Claude (공식 가격이 들어오면 자동으로 무시됨) |
| `scoreboard.md` | 성적표 (전체·유형별·확률 보정·진행중·최근 판정) | 자동 생성 |
| `status.json` | 성적 요약 숫자 | 자동 생성 |
| `positions.md` | 보유 포지션의 탈출 계획과 변경 이력 | Claude (변경 시 사유 필수) |
| `reports/` | 수기 채점 보고서 | Claude |

## 자동 실행
- `daily-collect` 워크플로가 데이터를 모은 뒤 `python scripts/score.py`를 실행하고, 결과를 함께 커밋합니다.
- 채점이 실패해도 데이터 수집은 멈추지 않습니다.

## 판정 규칙
- `prob`은 "예측 문장이 참일 확률"입니다.
  - 0.5 초과 → 참에 건 것, 0.5 미만 → 거짓에 건 것으로 맞음/틀림을 매깁니다.
  - 정확히 0.5는 동전으로 보고 적중 집계에서 빼며, Brier 점수만 계산합니다.
- Brier = (확률 − 결과)². 낮을수록 좋습니다. 항상 50%라고 말하면 0.25입니다.
- 기간은 `ref_date` 다음 거래일부터 `horizon_td`거래일까지입니다. `end_date`를 쓰면 그날까지입니다.
- 장중 도달(`touch_high` / `touch_low`)은 닿는 순간 확정됩니다. 종가 판정(`close_ge` / `close_le`)은 기간 마지막 날에 확정됩니다.
- `first_up` / `first_dn`은 위쪽은 장중 고가, 아래쪽은 종가로 봅니다. 같은 날 둘 다 일어나면 장중 고가가 먼저 일어난 것으로 봅니다.
- 추정 가격으로 판정된 건은 `est=1`로 표시됩니다. 공식 가격이 들어오면 다음 실행 때 다시 판정됩니다.
- `source=retro` 건은 2026-11-20에 수기로 채점한 과거 기록입니다(점수 1 / 0.5 / 0).

## 유형
A 위험 회피 · B 큰 방향·국면 · C 가격 목표·시점 · D 숏 관련 · E 규칙 판정·연구 · F 이벤트·장중 구조

## 예측 등록 예시
```bash
python scripts/score.py add --ticker SOXL --cat C \
  --statement "본전 53 장중 도달 — 5거래일 안" --check touch_high --level 53 \
  --ref 2026-11-19 --horizon 5 --prob 0.48 --basis "같은 국면 27개월 표본" --room 판단1
python scripts/score.py        # 바로 재채점
```
