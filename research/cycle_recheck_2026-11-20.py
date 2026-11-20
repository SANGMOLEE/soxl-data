# -*- coding: utf-8 -*-
"""2026-11-20 사이클 정밀 재검: 시간창·200주선·전저점 되밟기·데스크로스·탐지기 what-if.
실행: python research/cycle_recheck_2026-11-20.py"""
import os, sys, numpy as np, pandas as pd
R = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, R)
import bottom_detector as bd
b = pd.read_csv(os.path.join(R, "..", "data", "crypto", "BTCUSD.csv"), parse_dates=["date"]).set_index("date").sort_index()
ix = pd.date_range(b.index[0], b.index[-1]); b = b.reindex(ix).ffill(); c = b.close
today = ix[-1]; p = c.iloc[-1]
m50, m200, w200 = c.rolling(50).mean(), c.rolling(200).mean(), c.rolling(1400).mean()
print(f"== 기준일 {today.date()} 종가(진행 중) {p:,.0f}")

print("\n== 1. 시간창 (과거 3사이클)")
H = {"2012-11-28": ("2013-12-04", "2015-01-14"), "2016-07-09": ("2017-12-17", "2018-12-15"), "2020-05-11": ("2021-11-08", "2022-11-21")}
for h, (t, l) in H.items():
    h, t, l = map(pd.Timestamp, (h, t, l)); print(f"  반감기 {h.date()} → 고점 +{(t-h).days}일 → 저점 +{(l-t).days}일 (반감기→저점 {(l-h).days}일)")
h4, t4 = pd.Timestamp("2024-04-20"), pd.Timestamp("2025-10-06")
print(f"  이번: 반감기 {h4.date()} → 고점 {t4.date()} +{(t4-h4).days}일. 오늘은 고점 +{(today-t4).days}일, 반감기 +{(today-h4).days}일")
print(f"  고점→저점 창 363~406일 = {(t4+pd.Timedelta(days=363)).date()} ~ {(t4+pd.Timedelta(days=406)).date()}  ← 11/14 저점(64,128)은 +404일")
print(f"  반감기→저점 창 777~924일 = {(h4+pd.Timedelta(days=777)).date()} ~ {(h4+pd.Timedelta(days=924)).date()}  ← 이미 지남. 6/30 저점은 +{(pd.Timestamp('2026-06-30')-h4).days}일")
for d in ["2026-11-16", "2026-12-12", "2027-01-13"]:
    d = pd.Timestamp(d); print(f"  중간선거 후 저점 후보 {d.date()}: 고점 +{(d-t4).days}일, 반감기 +{(d-h4).days}일")

print("\n== 2. 200주선 아래 머문 기록 (과거 저점)")
for name, lo in [("2015", "2015-01-14"), ("2018", "2018-12-15"), ("2020", "2020-03-12"), ("2022", "2022-11-21")]:
    lo = pd.Timestamp(lo); seg = c[lo - pd.Timedelta(days=200): lo + pd.Timedelta(days=200)]; wseg = w200.reindex(seg.index)
    below = (seg < wseg); 
    if wseg.isna().all(): print(f"  {name}: 200주선 자료 없음(2014-09 이전 포함)"); continue
    runs = below.astype(int).groupby((below != below.shift()).cumsum()).sum(); longest = int(runs[below.groupby((below != below.shift()).cumsum()).first()].max()) if below.any() else 0
    print(f"  {name}: 저점일 200주선 대비 {seg[lo]/wseg[lo]-1:+.0%}, 최저 {(seg/wseg-1).min():+.0%}, 가장 긴 연속 하회 {longest}일")
cur_below = (c < w200); run = cur_below[::-1].cumprod().sum() if cur_below.iloc[-1] else 0
print(f"  지금: 200주선 {w200.iloc[-1]:,.0f}, 대비 {p/w200.iloc[-1]-1:+.1%}, 연속 하회 {int(run)}일. 6/30 저점일 200주선 대비 {c['2026-06-30']/w200['2026-06-30']-1:+.1%}")

print("\n== 3. 약세장 첫 큰 저점 → 최종 저점 (전저점 되밟기)")
for name, a, bb in [("2014-15", "2014-10-05", "2015-01-14"), ("2018", "2018-06-29", "2018-12-15"), ("2022", "2022-06-18", "2022-11-21")]:
    a, bb = pd.Timestamp(a), pd.Timestamp(bb); print(f"  {name}: 첫 저점 {a.date()} {c[a]:,.0f} → 최종 {bb.date()} {c[bb]:,.0f} ({c[bb]/c[a]-1:+.0%}, {(bb-a).days}일 뒤)")
j = pd.Timestamp("2026-06-30"); print(f"  이번: 첫 저점 {j.date()} {c[j]:,.0f} → 오늘 {p:,.0f} ({p/c[j]-1:+.1%}, {(today-j).days}일). -10~-15% 되밟기면 {c[j]*0.9:,.0f}~{c[j]*0.85:,.0f}")

print("\n== 4. 2026년 구조")
y = c["2026"]; print(f"  2026 고점 {y.idxmax().date()} {y.max():,.0f} (ATH 126,200 대비 {y.max()/126200-1:+.0%}) → 9/21 이후 고점 86,603 → 오늘 {p/86603-1:+.0%}")
dc = (m50 < m200); print(f"  50일선 {m50.iloc[-1]:,.0f} vs 200일선 {m200.iloc[-1]:,.0f}: {'데스크로스 상태' if dc.iloc[-1] else '골든 상태'}; 최근 교차일 {dc[dc != dc.shift()].index[-1].date()}")
print(f"  200일선 하회 연속 {int((c<m200)[::-1].cumprod().sum())}일, 200일선 30일 기울기 {m200.iloc[-1]/m200.iloc[-31]-1:+.1%}")

print("\n== 5. 탐지기 what-if (오늘 종가가 이 값이면)")
F = bd.features(); print(f"  오늘 점수 {int(F.score.iloc[-1])} 단계 {int(F.level.iloc[-1])} 켜진 조건 {''.join(k for k in 'ABCDEFGH' if F[k].iloc[-1])}")
for px in [62000, 60500, 58559, 56292, 53475, 50000, 46000]:
    s, l, on = bd.what_if(px); print(f"  {px:>7,}: 점수 {s} 단계 {l} 구간 {on}")
