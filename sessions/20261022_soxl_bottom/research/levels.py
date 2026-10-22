# -*- coding: utf-8 -*-
"""SOX 목표 구간 → SOXL 환산.  SOXL ≈ 현재가 × (SOX비율)^3 × 변동성감쇠 exp(-3σ²t)"""
import numpy as np, pandas as pd, load
p = load.panel()
s, x = p["sox"], p["soxl"]
r = s.pct_change(); rx = x.pct_change()
sig = r.iloc[-60:].std()
print(f"SOX 60일 일간변동성 {sig:.2%} (연 {sig*252**.5:.0%}),  SOXL {rx.iloc[-60:].std():.2%}")
print(f"최근 60일 SOXL/SOX 일간 베타 {np.polyfit(r.iloc[-60:], rx.iloc[-60:], 1)[0]:.2f}")
S0, L0 = s.iat[-1], x.iat[-1]
for name, lv in [("10/20 SOX 장중저점(78.6% 되돌림)", 11043.24), ("10/16 종가 최저", 11137.29),
                 ("스윙고점 -18%", 13217.82*0.82), ("200일선", s.rolling(200).mean().iat[-1]),
                 ("스윙고점 -20%", 13217.82*0.80), ("7/29 1차 저점", 10447.49),
                 ("2차하락 중앙(10/16 대비 -14.7%)", 11137.29*0.853), ("스윙고점 -30%", 13217.82*0.70)]:
    if True:
        dec = np.exp(-3*sig**2*10)
        if True:
            print(f"  {name:30s} SOX {lv:8,.0f} ({lv/S0-1:+6.1%}) → SOXL ≈ {L0*(lv/S0)**3*dec:6.1f} (10일) / {L0*(lv/S0)**3*np.exp(-3*sig**2*25):6.1f} (25일)")

# 검증: 2021-09 이후 실제 SOXL 과 환산식의 20거래일 오차
xx = x.dropna().loc["2021-09":]; ss = s.reindex(xx.index)
sg = ss.pct_change().rolling(60).std()
pred = xx.shift(20) * (ss/ss.shift(20))**3 * np.exp(-3*sg**2*20)
err = (xx/pred - 1).dropna()
print(f"환산식 20일 오차: 중앙 {err.median():+.1%}, 10~90% {err.quantile(.1):+.1%}~{err.quantile(.9):+.1%}")
