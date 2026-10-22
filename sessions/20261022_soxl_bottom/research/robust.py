# -*- coding: utf-8 -*-
"""강건성: 임계값/속도 조건을 바꿔도 '추가 하락' 분포가 비슷한가 + 사후 2일 조건부"""
import pandas as pd, numpy as np, load
p = load.panel(); s = p["sox"]; H = 60

def events(th, fast, src="sox"):
    x = p[src] if src != "sox" else s
    dd = x / x.rolling(60, min_periods=20).max() - 1
    ds = x.rolling(60, min_periods=20).apply(lambda a: len(a)-1-np.argmax(a), raw=True)
    out, last = [], None
    for i in range(250, len(p) - 1):
        if dd.iat[i] <= th and ds.iat[i] <= fast and (last is None or i - last >= H):
            last = i; out.append(i)
    return out, x

def stats(idx, x, post2=False):
    r = []
    for i in idx:
        if i + H >= len(x): continue
        base = x.iat[i]
        if post2:  # 이후 2거래일 동안 신저가 없고, 반등도 +3% 미만 (현재 상황)
            nx = x.iloc[i+1:i+3]
            if nx.min() < base or nx.iloc[-1] / base - 1 > 0.03: continue
            fut = x.iloc[i+3:i+3+H]; ref = nx.iloc[-1]
        else:
            fut = x.iloc[i+1:i+1+H]; ref = base
        r.append(dict(date=x.index[i].date(), more=min(fut.min()/base - 1, 0),
                      held=fut.min() >= base, d2=fut.values.argmin()+1, f60=fut.iloc[-1]/ref - 1))
    return pd.DataFrame(r)

print("SOX 1x — 임계 x 속도 격자 (H=60)")
for th in (-0.12, -0.15, -0.18):
    for fast in (10, 15, 25):
        idx, x = events(th, fast)
        d = stats(idx, x)
        if len(d):
            print(f"  th={th:.0%} 고점후<={fast:2d}일  n={len(d):2d}  이날이바닥 {d.held.mean():4.0%}  추가하락 중앙 {d.more.median():6.1%}  하위25% {d.more.quantile(.25):6.1%}  바닥까지 중앙 {d.d2.median():3.0f}일")

print("\n[현재와 같은 사후 2일(신저가 없음, 반등 3% 미만) 조건부]")
for th in (-0.12, -0.15):
    for fast in (15, 25):
        idx, x = events(th, fast)
        d = stats(idx, x, post2=True)
        if len(d):
            print(f"  th={th:.0%} <= {fast}일  n={len(d):2d}  첫 급락일 종가가 바닥 {d.held.mean():4.0%}  추가하락 중앙 {d.more.median():6.1%}  하위25% {d.more.quantile(.25):6.1%}")
            print("     ", ", ".join(f"{a}({b:+.0%})" for a, b in zip(d.date, d.more)))

print("\nSOXL 실물 (2010~) — 60일 고점 대비 -38% 이하, 고점 후 15일 이내")
idx, x = events(-0.38, 15, "soxl")
d = stats(idx, x)
print(d.round(3).to_string(index=False))
print(f"  n={len(d)}  이날이바닥 {d.held.mean():.0%}  추가하락 중앙 {d.more.median():.1%}  하위25% {d.more.quantile(.25):.1%}  바닥까지 중앙 {d.d2.median():.0f}일  60일뒤 중앙 {d.f60.median():.1%}")
d2 = stats(idx, x, post2=True)
if len(d2):
    print(f"  사후2일 조건부 n={len(d2)}  바닥확률 {d2.held.mean():.0%}  추가하락 중앙 {d2.more.median():.1%}")
    print(d2.round(3).to_string(index=False))
else:
    print("  사후2일 조건부: 해당 사례 없음")
