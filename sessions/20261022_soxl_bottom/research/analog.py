# -*- coding: utf-8 -*-
"""
최근접 유사국면 — 2026-10-20 의 상태 벡터와 가장 닮은 과거 날짜(에피소드당 1일)
특징: SOX 60일고점 낙폭, 고점 후 경과일, ATH 낙폭, 200일선 이격, RSI14,
      SPY 60일 낙폭, VIX, HY 20일 변화
"""
import pandas as pd, numpy as np, load
pd.set_option("display.width", 250)
p = load.panel(); s, y = p["sox"], p["syn3"]
F = ["dd60", "days_since_hi60", "dd_ath", "ma200", "rsi", "spy_dd60", "vix", "hy_chg20"]
X = p[F].dropna()
X = X[X.index < "2026-10-01"]           # 현재 에피소드 제외
now = p[F].iloc[-1]
z = (X - X.mean()) / X.std()
zn = (now - X.mean()) / X.std()
W = pd.Series(1.0, index=F); W["dd60"] = 2; W["days_since_hi60"] = 1.5   # 급락 형태를 중시
dist = (((z - zn) ** 2) * W).sum(axis=1) ** 0.5
picked = []
for t in dist.sort_values().index:
    if all(abs((t - u).days) > 90 for u in picked):
        picked.append(t)
    if len(picked) == 15:
        break
rows = []
for t in picked:
    i = p.index.get_loc(t)
    fut = s.iloc[i+1:i+61]; fy = y.iloc[i+1:i+61]
    rows.append(dict(date=t.date(), dist=dist[t], **{k: p.at[t, k] for k in F},
                     more=min(fut.min()/s.iat[i]-1, 0), d2low=int(fut.values.argmin()+1) if fut.min() < s.iat[i] else 0,
                     more3x=min(fy.min()/y.iat[i]-1, 0),
                     f20=s.iat[min(i+20, len(s)-1)]/s.iat[i]-1, f60=s.iat[min(i+60, len(s)-1)]/s.iat[i]-1,
                     f60_3x=y.iat[min(i+60, len(y)-1)]/y.iat[i]-1))
A = pd.DataFrame(rows)
A.to_csv("../output/analogs.csv", index=False)
print("현재:", now.round(3).to_dict())
print(A.round(3).to_string(index=False))
for k in (10, 15):
    a = A.head(k)
    print(f"\n상위 {k}개: 이날이 바닥(60일 내 더 안 빠짐) {(a.more >= 0).mean():.0%} | 추가하락 3% 이내 {(a.more > -0.03).mean():.0%}"
          f" | 추가하락 중앙 {a.more.median():.1%} (하위25% {a.more.quantile(.25):.1%}) | 합성3배 중앙 {a.more3x.median():.1%}"
          f" | 바닥까지 중앙 {a.d2low.median():.0f}일 | 20일뒤 + 확률 {(a.f20>0).mean():.0%} | 60일뒤 중앙 {a.f60.median():.1%}, 3배 {a.f60_3x.median():.1%}")
