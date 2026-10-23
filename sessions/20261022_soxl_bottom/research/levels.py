# -*- coding: utf-8 -*-
"""SOX 목표 구간 → SOXL 환산 (마지막 종가 기준, 수준은 데이터에서 자동 산출)
SOXL ≈ 현재가 × (SOX비율)^3 × 변동성감쇠 exp(-3σ²t)"""
import numpy as np, pandas as pd, load
p = load.panel(); s, x = p["sox"], p["soxl"]
r = s.pct_change(); rx = x.pct_change()
sig = r.iloc[-60:].std()
S0, L0 = s.iat[-1], x.iat[-1]
hi_t = s.iloc[-60:].idxmax(); HI = s[hi_t]                 # 스윙고점
since = s.loc[hi_t:]; LOW = since.min()                     # 스윙고점 이후 종가 최저
sox_low_intra = pd.read_csv(load.D + "prices/SOX.csv", parse_dates=["date"]).set_index("date")["low"].loc[hi_t:].min()
ath_t = s.idxmax()
T1 = s.loc[ath_t:hi_t].min(); T1_t = s.loc[ath_t:hi_t].idxmin()   # 1차 저점
HI80 = s.iloc[-81:-1].max()
trig = since[since <= HI*0.85]; TRIG = trig.iat[0] if len(trig) else LOW   # 재하락 확인일(=8일 연속하락 마지막) 종가
MA200 = s.rolling(200).mean().iat[-1]
print(f"기준일 {s.index[-1].date()}  SOX {S0:,.2f}  SOXL {L0:.2f}")
print(f"SOX 60일 일간변동성 {sig:.2%} (연 {sig*252**.5:.0%}),  SOXL {rx.iloc[-60:].std():.2%}, 60일 베타 {np.polyfit(r.iloc[-60:], rx.iloc[-60:], 1)[0]:.2f}")
print(f"스윙고점 {HI:,.0f} ({hi_t.date()}), 1차 저점 {T1:,.0f} ({T1_t.date()}), 80일 고점 {HI80:,.0f}, 재하락 확인일 {trig.index[0].date() if len(trig) else '-'} {TRIG:,.0f}")
levels = [
    ("스윙고점 이후 SOX 장중 최저", sox_low_intra),
    ("스윙고점 이후 SOX 종가 최저", LOW),
    ("스윙고점 -18%", HI*0.82),
    ("80일 고점 -25% (과거 저점 중앙 낙폭)", HI80*0.75),
    ("200일선", MA200),
    ("스윙고점 -20%", HI*0.80),
    ("1차 저점", T1),
    ("확인일 종가 -8.4% (연속하락 사례 중앙)", TRIG*(1-0.084)),
    ("확인일 종가 -14.7% (2차하락 구조 중앙)", TRIG*0.853),
    ("현재 -8% (-18% 급락·VIX<25 사례 중앙)", S0*0.92),
    ("현재 -16.3% (-18% 급락 전체 사례 중앙)", S0*(1-0.163)),
    ("SOX 9,850", 9850.0), ("SOX 9,500", 9500.0),
    ("스윙고점 -30%", HI*0.70),
]
for name, lv in sorted(levels, key=lambda z: -z[1]):
    print(f"  {name:34s} SOX {lv:8,.0f} ({lv/S0-1:+6.1%}) → SOXL ≈ {L0*(lv/S0)**3*np.exp(-3*sig**2*10):6.1f} (10일) / {L0*(lv/S0)**3*np.exp(-3*sig**2*25):6.1f} (25일)")
xx = x.dropna().loc["2021-09":]; ss = s.reindex(xx.index)
sg = ss.pct_change().rolling(60).std()
pred = xx.shift(20) * (ss/ss.shift(20))**3 * np.exp(-3*sg**2*20)
err = (xx/pred - 1).dropna()
print(f"환산식 20일 오차: 중앙 {err.median():+.1%}, 10~90% {err.quantile(.1):+.1%}~{err.quantile(.9):+.1%}")
