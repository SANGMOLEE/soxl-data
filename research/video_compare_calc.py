# -*- coding: utf-8 -*-
"""자산제곱 영상(2027년 비트코인 불장, 11월 중순 녹화 추정) 주장 대조 계산. 실행: python research/video_compare_calc.py"""
import os, pandas as pd, numpy as np
R = os.path.dirname(os.path.abspath(__file__))
b = pd.read_csv(os.path.join(R, "..", "data", "crypto", "BTCUSD.csv"), parse_dates=["date"]).set_index("date").sort_index()
ix = pd.date_range(b.index[0], b.index[-1]); b = b.reindex(ix).ffill(); c = b.close; hi = b.high
o = pd.read_csv(os.path.join(R, "..", "data", "crypto", "BTC_ONCHAIN.csv"), parse_dates=["date"]).set_index("date").sort_index()
p = c.iloc[-1]; ath = 126200.0; rp = o.realized_price.iloc[-1]; m200 = c.rolling(200).mean().iloc[-1]; w200 = c.rolling(1400).mean().iloc[-1]
ETF_COST = 81300.0   # 영상이 말한 ETF 평균 매수가
print(f"기준 {ix[-1].date()} 종가 {p:,.0f} | ATH 대비 {p/ath-1:+.1%} | 이번 사이클 최대 낙폭(종가) {c['2025-10-06':].min()/ath-1:+.1%} (영상: -54%)")
print(f"11/4 고가 {hi['2026-11-04']:,.0f} (영상: 81,100) vs ETF 평균 매수가 {ETF_COST:,.0f} → 지금 가격 대비 {ETF_COST/p-1:+.0%} 위")
print(f"영상 기본 시나리오 '연말까지 200일선~ETF 평균가 사이': 200일선 {m200:,.0f} → 지금 {p/m200-1:+.1%} (이탈)")
print(f"영상 대안 '12월 FOMC 전 200주선 근처까지': 200주선 {w200:,.0f} → 지금 {p/w200-1:+.1%} (이미 아래)")
print(f"실현가격 {rp:,.0f} (영상: 54,000) → 지금 대비 {rp/p-1:+.1%}")
print("\n손익비(영상 방식: 하방 = 실현가격, 상방 = 전고점 126,200, 필요 승률 = D/(U+D))")
for name, px in [("영상 녹화 시점(약 75,000)", 75000), ("오늘", p)]:
    for dn_name, dn in [("실현가격", rp), ("MVRV 0.9 (우리 하방)", rp * 0.9)]:
        D = 1 - dn / px; U = ath / px - 1; print(f"  {name} {px:,.0f} | 하방 {dn_name} {dn:,.0f} ({-D:.0%}) 상방 {U:+.0%} → 필요 승률 {D/(U+D):.0%}")
print("\n영상 3분할: ① 지금(≈75k) ② 200주선 ③ 연준 인상 중단 확인 후")
print(f"  ①을 11/10 종가 {c['2026-11-10']:,.0f}로 잡으면 오늘 {p/c['2026-11-10']-1:+.1%}. ② 200주선 {w200:,.0f}은 11/14 이후 통과.")
print("\n중간선거 해 → 다음 해 (영상 주장 검증)")
for y in [2014, 2018, 2022]:
    a = c[f"{y}-01-01":f"{y}-12-31"]; n = c[f"{y+1}-01-01":f"{y+1}-12-31"]
    if len(a) and len(n): print(f"  {y}: {a.iloc[-1]/a.iloc[0]-1:+.0%} → {y+1}: {n.iloc[-1]/n.iloc[0]-1:+.0%}")
    else: print(f"  {y}: 자료 범위 밖(2014-09 시작)")
print("\n사이클 배수(저점→고점): ", end="")
for lo, hi_ in [("2015-01-14", "2017-12-17"), ("2018-12-15", "2021-11-08"), ("2022-11-21", "2025-10-06")]: print(f"{c[hi_]/c[lo]:.0f}x ", end="")
print()
