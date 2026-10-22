# -*- coding: utf-8 -*-
"""SOX 8거래일 이상 연속 하락이 끝난 직후(첫 상승일) — 이후 경로"""
import pandas as pd, numpy as np, load
p = load.panel(); s = p["sox"]; dn = s.diff() < 0
run = dn.groupby((~dn).cumsum()).cumsum()
rows = []
for i in range(1, len(s) - 1):
    if run.iat[i-1] >= 7 and not dn.iat[i]:         # 7일+ 연속하락 후 첫 반등일
        L = s.iloc[:i].iloc[-1]                     # 연속하락 마지막 종가(=저점 후보)
        fut = s.iloc[i+1:i+61]
        rows.append(dict(date=s.index[i].date(), streak=int(run.iat[i-1]), streak_dd=L/s.iat[i-1-int(run.iat[i-1])]-1,
                         low_held=fut.min() >= L if len(fut) == 60 else np.nan,
                         more=min(fut.min()/L-1, 0) if len(fut) else np.nan,
                         f20=s.iat[min(i+20, len(s)-1)]/s.iat[i]-1, f60=s.iat[min(i+60, len(s)-1)]/s.iat[i]-1, n=len(fut)))
R = pd.DataFrame(rows)
print(R.round(3).to_string(index=False))
c = R[R.n == 60]
print(f"\n완결 n={len(c)} | 연속하락 마지막 종가가 60일 내 안 깨짐 {c.low_held.mean():.0%} | 추가하락 중앙 {c.more.median():.1%} 하위25% {c.more.quantile(.25):.1%} | 20일뒤+ {(c.f20>0).mean():.0%} | 60일뒤 중앙 {c.f60.median():.1%}")
big = c[c.streak_dd <= -0.10]
print(f"연속하락 중 -10% 이상 빠진 경우 n={len(big)} | 안 깨짐 {big.low_held.mean():.0%} | 추가하락 중앙 {big.more.median():.1%} | 60일뒤 중앙 {big.f60.median():.1%}")
