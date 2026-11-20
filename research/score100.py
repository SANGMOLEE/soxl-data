# -*- coding: utf-8 -*-
"""BTC 저점 점수 v3 — 0~100 연속 점수 + 정밀 트리거 (2026-11-20)
  구간 Z = 4년 백분위 평균: 200일선 이격, 200주선 이격, ATH 낙폭, MVRV, 주간 RSI      (느린 층)
  타이밍 T = 4년 백분위 평균: 일간 RSI14, 30일 낙폭, 90일 낙폭, 볼린저 z, 50일선 이격, 7일 수익  (빠른 층)
  점수 = 0.5 Z + 0.5 T.  띠: ≥90 극저점, 80~90 저점권, 65~80 저평가, <65 중립.
  정밀 트리거(당일 포착용) = 점수 ≥ 85 & 종가 20일 신저가 & 게이트(고점 후 240일·ATH −45%) → 다음날 종가 > 당일 종가면 "확인".
    과거: 2018·2020·2022·2026 사이클 저점 당일 4/4 포착, 사건 16건(그중 가짜 11건), 매수(익일 종가) 뒤 180일 추가낙폭 중앙 −8%·최악 −42%, 1년 +131%·플러스 81%.
    사다리(직전 트리거보다 5% 이상 낮을 때만 추가)의 마지막 매수는 최저점 +2~12%.
  연구: score100_study.py / 보고서 score100_research_2026-11-20.md.  기존 0~8 탐지기(bottom_detector.py)는 그대로 두고 병행한다.
실행: python research/score100.py  → 현재 상태 출력, research/score100_state.json
"""
import os, sys, json, numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from score100_features import load, pct_rank
ZC = ["mayer", "w200", "ddath", "mvrv", "rsi_w"]; TC = ["rsi14", "dd30", "dd90", "bbz", "ma50d", "r7"]
THR, THR_STRONG = 85, 90

def band(x): return "자료없음" if pd.isna(x) else "극저점" if x >= 90 else "저점권" if x >= 80 else "저평가" if x >= 65 else "중립"

def compute():
    F = load(); P = pct_rank(F, ZC + TC)
    F["Z"] = P[ZC].mean(axis=1); F["T"] = P[TC].mean(axis=1); F["score"] = 0.5 * F.Z + 0.5 * F["T"]
    F["gate"] = (F.days_ath >= 240) & (F.ddath <= -0.45)
    F["newlow20"] = F.close == F.close.rolling(20).min()
    F["cand"] = (F.score >= THR) & F.newlow20 & F.gate                      # 후보일(당일 저녁에 알 수 있음)
    F["trigger"] = F.cand.shift(1).fillna(False) & (F.close > F.close.shift(1))   # 확인일(후보 다음날 종가 상승) → 그날 종가 매수
    F["strong"] = F.trigger & (F.score.shift(1) >= THR_STRONG)
    return F, P

if __name__ == "__main__":
    F, P = compute(); x = F.iloc[-1]; d = F.index[-1]
    last_trig = F.index[F.trigger][-1] if F.trigger.any() else None
    print(f"{d.date()} BTC {x.close:,.0f} | 점수 {x.score:.1f} ({band(x.score)}) = 구간 {x.Z:.0f} · 타이밍 {x['T']:.0f} | 게이트 {bool(x.gate)} | 20일 신저가 {bool(x.newlow20)} | 후보일 {bool(x.cand)}")
    print("  구간:", {k: round(P.at[d, k]) for k in ZC}); print("  타이밍:", {k: round(P.at[d, k]) for k in TC})
    print(f"  최근 트리거: {last_trig.date() if last_trig is not None else None} (매수가 {F.close[last_trig]:,.0f}, 후보일 점수 {F.score[last_trig - pd.Timedelta(days=1)]:.0f})" if last_trig is not None else "  트리거 없음")
    print("  최근 30일 점수:", " ".join(str(int(round(v))) for v in F.score.iloc[-30:]))
    st = dict(date=str(d.date()), close=round(float(x.close)), score=round(float(x.score), 1), band=band(x.score), zone=round(float(x.Z)), timing=round(float(x["T"])),
              gate=bool(x.gate), newlow20=bool(x.newlow20), candidate=bool(x.cand), trigger_today=bool(x.trigger),
              last_trigger=str(last_trig.date()) if last_trig is not None else None, last_trigger_price=round(float(F.close[last_trig])) if last_trig is not None else None,
              components={k: round(float(P.at[d, k])) for k in ZC + TC})
    json.dump(st, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "score100_state.json"), "w"), ensure_ascii=False, indent=1)
    F[["close", "Z", "T", "score", "gate", "cand", "trigger"]].to_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), "score100_series.csv"))
