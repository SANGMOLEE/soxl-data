# -*- coding: utf-8 -*-
"""
큰 그림: SOX 지그재그(15%)로 '고점 → 1차 저점 → 반등 고점(전고점 미달) → 재하락' 구조를 찾아
재하락이 1차 저점을 깼는지 본다.  현재: 14,635(6/22) → 10,447(7/29) → 13,218(10/6, 전고점의 90%) → 11,137(10/16)
"""
import pandas as pd, numpy as np, load
p = load.panel(); s = p["sox"]

def zigzag(x, th):
    pts, mode = [], None; hi = lo = x.index[0]
    for t, v in x.items():
        if v > x[hi]: hi = t
        if v < x[lo]: lo = t
        if mode != "down" and v <= x[hi]*(1-th): pts.append((hi, "P")); mode, lo = "down", t
        elif mode != "up" and v >= x[lo]*(1+th): pts.append((lo, "T")); mode, hi = "up", t
    return pts

z = zigzag(s, 0.15)
print("SOX 15% 지그재그 전환점 (최근 20개)")
for t, k in z[-20:]:
    print(f"  {t.date()} {k} {s[t]:,.0f}")

rows = []
for a in range(len(z) - 3):
    (p1, k1), (t1, k2), (p2, k3), (t2, k4) = z[a], z[a+1], z[a+2], z[a+3]
    if (k1, k2, k3) != ("P", "T", "P"):
        continue
    first = s[t1]/s[p1]-1; rally = s[p2]/s[t1]-1; lh = s[p2]/s[p1]
    if first > -0.20 or lh >= 1.0:
        continue
    # p2 이후 15% 하락 시점(재하락 확인일)
    after = s[p2:]
    trig = after[after <= s[p2]*0.85]
    if not len(trig):
        continue
    td = trig.index[0]
    nxt_low = s[t2] if k4 == "T" else np.nan
    rows.append(dict(peak=p1.date(), first_low=t1.date(), first_dd=first, rally=rally, lower_high=lh,
                     peak2=p2.date(), trigger=td.date(), next_low=t2.date(), next_low_vs_first=nxt_low/s[t1]-1,
                     next_low_vs_trigger=nxt_low/s[td]-1, broke_first=nxt_low < s[t1]))
R = pd.DataFrame(rows)
pd.set_option("display.width", 250)
print("\n'1차 하락 >=20% → 전고점 미달 반등 → 반등고점 대비 -15%' 사례")
print(R.round(3).to_string(index=False))
print(f"\n1차 저점 하향 이탈 비율: {R.broke_first.mean():.0%} (n={len(R)})")
print(f"재하락 확인일 대비 추가하락 중앙값: {R.next_low_vs_trigger.median():.1%}")
